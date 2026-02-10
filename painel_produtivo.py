import streamlit as st
import pandas as pd
import time
import requests
from datetime import datetime, date
from zoneinfo import ZoneInfo
from io import BytesIO

# ======================================================
# TIMEZONE BRASIL
# ======================================================
TZ = ZoneInfo("America/Sao_Paulo")

def agora_br():
    return datetime.now(TZ)

# ======================================================
# CONFIG STREAMLIT
# ======================================================
st.set_page_config(
    page_title="Painel de Controle Produtivo",
    layout="wide"
)

# ======================================================
# CONFIG GITHUB (RAW)
# ======================================================
RAW_XLSX_URL = (
    "https://raw.githubusercontent.com/"
    "jucielidelima-sys/painel-produtivo/main/"
    "movimentos_estoque_dados.xlsx"
)

# ======================================================
# REGRAS DE NEGÓCIO
# ======================================================
H_INICIO, H_FIM = 7, 17
H_ALMOCO, H_ALMOCO_DEST = 12, 13
HORAS_TURNO = list(range(H_INICIO, H_FIM + 1))

META_22L = 15
META_60L = 60

COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

# ======================================================
# CSS – MODO TV
# ======================================================
st.markdown("""
<style>
html, body {
  background:#000 !important;
  height:100vh !important;
  overflow:hidden !important;
}
[data-testid="stAppViewContainer"],
section.main {
  height:100vh !important;
  overflow:hidden !important;
  background:#000 !important;
}
header, footer, div[data-testid="stToolbar"] {
  display:none !important;
}
.main .block-container {
  padding:0.5rem 1rem !important;
  max-width:1920px !important;
}

:root{
  --panel:rgba(255,255,255,.05);
  --panel2:rgba(255,255,255,.03);
  --stroke:rgba(255,255,255,.12);
  --text:rgba(255,255,255,.95);
  --muted:rgba(255,255,255,.65);
  --orange:#ff7a18;
  --green:#17c964;
  --red:#ff4d4f;
}

*{ color:var(--text); }

.brand h1{ margin:0; font-size:22px; font-weight:900; }
.brand .sub{ font-size:12px; color:var(--muted); }

.upd{
  background:var(--panel);
  border:1px solid var(--stroke);
  border-radius:14px;
  padding:10px 14px;
}
.upd .lbl{ font-size:12px; color:var(--muted); }
.upd .val{ font-size:14px; color:var(--orange); font-weight:900; }

.kpi{
  background:var(--panel);
  border:1px solid var(--stroke);
  border-radius:14px;
  padding:10px 14px;
}
.kpi .t{ font-size:12px; color:var(--muted); }
.kpi .v{ font-size:30px; font-weight:900; }
.kpi .u{ font-size:12px; color:var(--orange); }

.panel{
  background:var(--panel2);
  border:1px solid var(--stroke);
  border-radius:16px;
  padding:12px;
}
.panel h2{
  margin:0 0 8px 0;
  color:var(--orange);
  font-size:14px;
  font-weight:900;
}

.table-header, .row{
  display:grid;
  grid-template-columns:70px 70px 70px 70px 1fr;
  gap:8px;
}
.table-header{
  font-size:12px;
  color:var(--muted);
  border-bottom:1px solid var(--stroke);
  padding-bottom:6px;
}
.row{
  font-size:12px;
  padding:6px 0;
  border-bottom:1px solid rgba(255,255,255,.08);
  align-items:center;
}

.pos{ color:var(--green); font-weight:900; }
.neg{ color:var(--red); font-weight:900; }

.barwrap{
  background:rgba(255,255,255,.08);
  height:10px;
  border-radius:999px;
  overflow:hidden;
}
.bar.green{ background:var(--green); height:100%; }
.bar.orange{ background:var(--orange); height:100%; }

.smallnote{ font-size:11px; color:var(--muted); }

/* RODAPÉ (ÚLTIMA LINHA) – MAIOR */
.foot{
  margin-top:10px;
  display:flex;
  gap:10px;
  flex-wrap:wrap;
}
.chip{
  background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.15);
  border-radius:999px;
  padding:8px 14px;
  font-size:14px;
  line-height:1.3;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# FUNÇÕES AUXILIARES
# ======================================================
def excel_letters(n):
    r=[]
    for i in range(n):
        s=""
        x=i
        while True:
            s=chr(ord("A")+x%26)+s
            x=x//26-1
            if x<0: break
        r.append(s)
    return r

def col(df, letra):
    letras=excel_letters(df.shape[1])
    return df.iloc[:, letras.index(letra)]

def parse_h(x):
    try:
        return int(pd.to_datetime(x).hour)
    except:
        try:
            return int(str(x).split(":")[0])
        except:
            return None

def meta(desc):
    d=str(desc).upper()
    if "60L" in d: return META_60L
    if "22L" in d: return META_22L
    return 0

def horas_ate_agora():
    h=agora_br().hour
    h=max(H_INICIO,min(h,H_FIM))
    return [x for x in range(H_INICIO,h+1) if x!=H_ALMOCO]

def base_horas(df):
    b=pd.DataFrame({"HORA":[h for h in HORAS_TURNO if h!=H_ALMOCO]})
    g=df.groupby("HORA")["QTD"].sum().reset_index()
    b=b.merge(g,on="HORA",how="left").fillna(0)
    return b

# ======================================================
# BAIXAR EXCEL DO GITHUB
# ======================================================
@st.cache_data(ttl=60)
def carregar_excel():
    r=requests.get(RAW_XLSX_URL,timeout=20)
    r.raise_for_status()
    return pd.read_excel(BytesIO(r.content),header=None), len(r.content)

# ======================================================
# TOPO
# ======================================================
l,r=st.columns([3,1])
with l:
    st.markdown(
        f"<div class='brand'><h1>Painel de Controle Produtivo</h1>"
        f"<div class='sub'>Modo TV — {date.today():%d/%m/%Y}</div></div>",
        unsafe_allow_html=True
    )
with r:
    st.markdown(
        f"<div class='upd'><div class='lbl'>Atualização</div>"
        f"<div class='val'>{agora_br():%d/%m/%Y %H:%M:%S}</div></div>",
        unsafe_allow_html=True
    )

# ======================================================
# CONTROLES
# ======================================================
c1,c2,c3=st.columns([2,1,3])
with c1:
    st.markdown("<div class='smallnote'>Fonte: GitHub (automático)</div>",unsafe_allow_html=True)
with c2:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()
with c3:
    auto=st.checkbox("Auto atualizar (a cada 60s)",True)

if auto:
    time.sleep(60)
    st.rerun()

# ======================================================
# DADOS
# ======================================================
try:
    df0,tam=carregar_excel()
except Exception as e:
    st.error("Erro ao carregar Excel do GitHub")
    st.code(e)
    st.stop()

s_h=col(df0,COL_HORA)
s_q=col(df0,COL_QTD)
s_d=col(df0,COL_DESC)

df=pd.DataFrame({
    "HORA":s_h.apply(parse_h),
    "QTD":pd.to_numeric(s_q,errors="coerce").fillna(0),
    "META":s_d.apply(meta)
})

df=df[df["META"].isin([META_22L,META_60L])]
df.loc[df["HORA"]==H_ALMOCO,"HORA"]=H_ALMOCO_DEST
df=df[df["HORA"].between(H_INICIO,H_FIM)]

df22=df[df["META"]==META_22L]
df60=df[df["META"]==META_60L]

b22=base_horas(df22)
b60=base_horas(df60)

# ======================================================
# KPIs
# ======================================================
hn=horas_ate_agora()
total=b22["QTD"].sum()+b60["QTD"].sum()
acum=b22[b22["HORA"].isin(hn)]["QTD"].sum()+b60[b60["HORA"].isin(hn)]["QTD"].sum()
meta_acum=(META_22L+META_60L)*len(hn)
delta_acum=acum-meta_acum

k1,k2,k3,k4=st.columns(4)
k1.markdown(f"<div class='kpi'><div class='t'>TOTAL DO DIA</div><div class='v'>{int(total)}</div><div class='u'>Unidades</div></div>",unsafe_allow_html=True)
k2.markdown(f"<div class='kpi'><div class='t'>DELTA ACUMULADO</div><div class='v'>{int(delta_acum):+d}</div></div>",unsafe_allow_html=True)

# ======================================================
# PAINÉIS
# ======================================================
def painel(titulo,base,meta_h):
    st.markdown(f"<div class='panel'><h2>{titulo}</h2>",unsafe_allow_html=True)
    st.markdown("<div class='table-header'><div>Hora</div><div>Qtd</div><div>Meta</div><div>Delta</div><div>Termômetro</div></div>",unsafe_allow_html=True)
    for _,r in base.iterrows():
        q=r["QTD"]; d=q-meta_h; p=q/meta_h if meta_h else 0
        cor="green" if p>=1 else "orange"
        st.markdown(
            f"<div class='row'><div>{int(r['HORA']):02d}:00</div>"
            f"<div>{int(q)}</div><div>{meta_h}</div>"
            f"<div class={'pos' if d>=0 else 'neg'}>{int(d):+d}</div>"
            f"<div><div class='barwrap'><div class='bar {cor}' style='width:{min(p,1)*100:.0f}%'></div></div></div></div>",
            unsafe_allow_html=True
        )
    st.markdown("</div>",unsafe_allow_html=True)

cA,cB=st.columns(2)
with cA: painel("60L — FORNOS DE BANCADA",b60,META_60L)
with cB: painel("22L — AIR FRYER (22L)",b22,META_22L)
