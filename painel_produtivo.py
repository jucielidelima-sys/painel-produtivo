import streamlit as st
import pandas as pd
import time
import requests
from datetime import datetime, date
from zoneinfo import ZoneInfo
from io import BytesIO

# =========================
# TIMEZONE BRASIL
# =========================
TZ = ZoneInfo("America/Sao_Paulo")
def agora_br():
    return datetime.now(TZ)

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(page_title="Painel de Controle Produtivo", layout="wide")

# =========================
# GITHUB RAW
# =========================
RAW_XLSX_URL = "https://raw.githubusercontent.com/jucielidelima-sys/painel-produtivo/main/movimentos_estoque_dados.xlsx"

# =========================
# REGRAS DE NEGÓCIO
# =========================
H_INICIO, H_FIM = 7, 17
H_ALMOCO, H_ALMOCO_DEST = 12, 13
HORAS_TURNO = list(range(H_INICIO, H_FIM + 1))

META_22L = 15
META_60L = 60

# colunas por letra do Excel
COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

# =========================
# CSS - MODO TV (SEM ROLAGEM)
# =========================
st.markdown(
    """
    <style>
      html, body{
        margin:0 !important; padding:0 !important;
        height:100vh !important; overflow:hidden !important;
        background:#000 !important;
      }
      [data-testid="stAppViewContainer"]{
        height:100vh !important; overflow:hidden !important;
        background:#000 !important;
      }
      header[data-testid="stHeader"],
      div[data-testid="stToolbar"],
      div[data-testid="stDecoration"],
      footer{
        display:none !important; height:0 !important;
      }
      section.main{
        height:100vh !important; overflow:hidden !important;
        padding-top:0 !important;
      }
      .main .block-container{
        height:100vh !important;
        overflow:hidden !important;
        padding-top:.25rem !important;
        padding-bottom:.15rem !important;
        padding-left:.85rem !important;
        padding-right:.85rem !important;
        max-width: 1920px !important;
      }

      :root{
        --panel:rgba(255,255,255,.05);
        --panel2:rgba(255,255,255,.03);
        --stroke:rgba(255,255,255,.10);
        --text:rgba(255,255,255,.92);
        --muted:rgba(255,255,255,.62);
        --orange:#ff7a18;
        --green:#17c964;
        --red:#ff4d4f;
      }
      *{ color: var(--text); }

      .brand h1{ margin:0; font-size:24px; font-weight:950; line-height:1.05; }
      .brand .sub{ color:var(--muted); font-size:12px; margin-top:2px; }

      .upd{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:10px 14px;
        min-width:260px;
      }
      .upd .lbl{ color:var(--muted); font-size:12px; }
      .upd .val{ color:var(--orange); font-weight:950; font-size:13px; margin-top:6px; }

      /* KPIs (4) */
      .kpi-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:8px 0 8px; }
      .kpi{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:10px 12px;
        min-height:72px;
      }
      .kpi .t{ color:var(--muted); font-size:12px; font-weight:900; }
      .kpi .v{ font-size:30px; font-weight:950; margin-top:6px; line-height:1; }
      .kpi .u{ color:var(--orange); font-weight:950; font-size:12px; margin-top:4px; }

      /* Dois painéis lado a lado */
      .section-grid{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }

      .panel{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:16px;
        padding:10px 10px 8px 10px;
      }
      .panel h2{
        margin:0 0 6px 0;
        color:var(--orange);
        font-size:14px;
        font-weight:950;
        letter-spacing:.3px;
      }

      /* Cabeçalho tabela */
      .table-header{
        display:grid;
        grid-template-columns:60px 60px 70px 70px 1fr;
        gap:8px;
        padding:6px 4px;
        border-bottom:1px solid var(--stroke);
        color:var(--muted);
        font-weight:950;
        font-size:12px;
      }

      /* Linhas tabela (compactas) */
      .row{
        display:grid;
        grid-template-columns:60px 60px 70px 70px 1fr;
        gap:8px;
        padding:6px 4px;
        border-bottom:1px solid rgba(255,255,255,.08);
        font-size:12px;
        align-items:center;
      }

      .pos{ color:var(--green); font-weight:950;}
      .neg{ color:var(--red); font-weight:950;}

      .barwrap{
        background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.10);
        height:10px;
        border-radius:999px;
        overflow:hidden;
      }
      .bar{ height:100%; border-radius:999px; }
      .bar.orange{ background:var(--orange); }
      .bar.green{ background:var(--green); }
      .smallnote{ color:var(--muted); font-size:11px; margin-top:2px; }

      /* Rodapé do painel - SEM SUMIR */
      .foot{
        margin-top:8px;
        display:flex;
        gap:8px;
        flex-wrap:wrap;
      }
      .chip{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.12);
        border-radius:999px;
        padding:7px 12px;
        font-size:13px;
        line-height:1.2;
        white-space:nowrap;
      }
      .chip b{ color:var(--text); }
      .chip .o{ color:var(--orange); font-weight:950;}
      .chip .g{ color:var(--green); font-weight:950;}
      .chip .r{ color:var(--red); font-weight:950;}

      .smallline{ color:var(--muted); font-size:12px; margin-top:2px; }
      div[data-testid="stVerticalBlock"] > div { gap: .25rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# FUNÇÕES
# =========================
def excel_letters(n_cols: int):
    letters = []
    for i in range(n_cols):
        x = i
        s = ""
        while True:
            s = chr(ord("A") + (x % 26)) + s
            x = x // 26 - 1
            if x < 0:
                break
        letters.append(s)
    return letters

def get_series_by_letter(df_noheader: pd.DataFrame, letter: str):
    letters = excel_letters(df_noheader.shape[1])
    if letter not in letters:
        return None
    return df_noheader.iloc[:, letters.index(letter)]

def parse_hour(x):
    if pd.isna(x):
        return None
    try:
        ts = pd.to_datetime(x, errors="coerce", dayfirst=True)
        if pd.notna(ts):
            return int(ts.hour)
    except Exception:
        pass
    s = str(x).strip()
    if not s:
        return None
    try:
        return int(s.split(":")[0])
    except Exception:
        return None

def meta_from_desc(desc: str) -> int:
    d = str(desc).upper()
    if "22L" in d:
        return META_22L
    if "60L" in d:
        return META_60L
    return 0

def horas_ate_agora():
    agora = agora_br().hour
    h_max = max(H_INICIO, min(agora, H_FIM))
    horas = [h for h in range(H_INICIO, h_max + 1) if h != H_ALMOCO]
    return horas if horas else [H_INICIO]

def build_hour_table(df_line: pd.DataFrame):
    agg = df_line.groupby("HORA", as_index=False)["QTD"].sum()
    base = pd.DataFrame({"HORA": [h for h in HORAS_TURNO if h != H_ALMOCO]})
    base = base.merge(agg, on="HORA", how="left").fillna({"QTD": 0})
    base["HORA"] = base["HORA"].astype(int)
    base["QTD"] = base["QTD"].astype(float)
    return base.sort_values("HORA")

def fmt_delta_html(x: float) -> str:
    return f"<span class='g'>{x:+.0f}</span>" if x >= 0 else f"<span class='r'>{x:+.0f}</span>"

@st.cache_data(show_spinner=False, ttl=55)
def baixar_excel_bytes(url: str):
    r = requests.get(url, timeout=25)
    r.raise_for_status()
    meta = {
        "len": len(r.content),
        "etag": r.headers.get("ETag"),
        "last_modified": r.headers.get("Last-Modified"),
    }
    return r.content, meta

@st.cache_data(show_spinner=False)
def ler_excel_sem_header(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_excel(BytesIO(file_bytes), header=None)

# =========================
# RENDER DO PAINEL (COM RODAPÉ)
# =========================
def render_panel(title, base_horas: pd.DataFrame, meta_h: int):
    st.markdown(f"<div class='panel'><h2>{title}</h2>", unsafe_allow_html=True)
    st.markdown("<div class='table-header'><div>Hora</div><div>Qtd</div><div>Meta/h</div><div>Delta</div><div>Termômetro</div></div>", unsafe_allow_html=True)

    for _, r in base_horas.iterrows():
        h = int(r["HORA"])
        qtd = float(r["QTD"])
        meta = float(meta_h)
        delta = qtd - meta
        perc = (qtd / meta) if meta else 0
        w = max(0, min(perc, 1.0)) * 100
        bar_class = "green" if perc >= 1 else "orange"
        delta_class = "pos" if delta >= 0 else "neg"
        termo_txt = f"{int(qtd)}/{int(meta)} ({int(round(perc*100,0))}%)"

        st.markdown(
            f"""
            <div class='row'>
              <div>{h:02d}:00</div><div><b>{int(qtd)}</b></div><div>{int(meta)}</div>
              <div class='{delta_class}'>{delta:+.0f}</div>
              <div>
                <div class='barwrap'><div class='bar {bar_class}' style='width:{w:.1f}%'></div></div>
                <div class='smallnote'>{termo_txt}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Rodapé com acumulados/projeções
    total = float(base_horas["QTD"].sum())
    meta_turno = float(meta_h * len(base_horas))

    hn = horas_ate_agora()
    acumulado = float(base_horas[base_horas["HORA"].isin(hn)]["QTD"].sum())
    meta_acum = float(meta_h * len(hn))
    delta_acum = acumulado - meta_acum

    ritmo = acumulado / max(1, len(hn))
    proj_final = ritmo * len(base_horas)
    delta_proj = proj_final - meta_turno

    st.markdown(
        f"""
        <div class='foot'>
          <div class='chip'>Acumulado: <b class='o'>{int(acumulado)}</b></div>
          <div class='chip'>Delta acum.: <b>{fmt_delta_html(delta_acum)}</b></div>
          <div class='chip'>Proj. final: <b>{int(round(proj_final,0))}</b></div>
          <div class='chip'>Delta proj.: <b>{fmt_delta_html(delta_proj)}</b></div>
          <div class='chip'>Total: <b class='o'>{int(total)}</b></div>
          <div class='chip'>Meta turno: <b>{int(meta_turno)}</b></div>
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# TOPO
# =========================
colL, colR = st.columns([3.2, 1])
with colL:
    st.markdown(
        f"<div class='brand'><h1>Painel de Controle Produtivo</h1><div class='sub'>Modo TV — {date.today():%d/%m/%Y}</div></div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='smallline'>Fonte: <b>GitHub (automático)</b></div>", unsafe_allow_html=True)

with colR:
    st.markdown(
        f"<div class='upd'><div class='lbl'>Atualização</div><div class='val'>{agora_br():%d/%m/%Y %H:%M:%S}</div></div>",
        unsafe_allow_html=True
    )

# =========================
# CONTROLES
# =========================
c1, c2, c3 = st.columns([2.0, 1.3, 3.7])
with c2:
    if st.button("🔄 Atualizar painel"):
        st.cache_data.clear()
        st.rerun()

with c3:
    auto = st.checkbox("Auto atualizar (a cada 60s)", value=True)

if auto:
    time.sleep(60)
    st.rerun()

# =========================
# LER DADOS
# =========================
try:
    file_bytes, meta = baixar_excel_bytes(RAW_XLSX_URL)
except Exception as e:
    st.error("Não consegui baixar o Excel do GitHub (RAW).")
    st.write("URL configurada:", RAW_XLSX_URL)
    st.code(str(e))
    st.stop()

st.markdown(
    f"<div class='smallline'>Arquivo: <b>movimentos_estoque_dados.xlsx</b> | Tamanho: <b>{meta.get('len',0)} bytes</b> | "
    f"ETag: <b>{meta.get('etag','-')}</b></div>",
    unsafe_allow_html=True
)

df0 = ler_excel_sem_header(file_bytes)

s_hora = get_series_by_letter(df0, COL_HORA)
s_qtd  = get_series_by_letter(df0, COL_QTD)
s_desc = get_series_by_letter(df0, COL_DESC)

if s_hora is None or s_qtd is None or s_desc is None:
    st.error("Não consegui localizar as colunas por letra (N/O/X) no Excel.")
    st.write("Qtd colunas:", df0.shape[1])
    st.write("Letras disponíveis:", excel_letters(df0.shape[1]))
    st.stop()

df = pd.DataFrame({"HORA_RAW": s_hora, "QTD_RAW": s_qtd, "DESC": s_desc}).dropna(how="all")
df["HORA"] = df["HORA_RAW"].apply(parse_hour)
df["QTD"] = pd.to_numeric(df["QTD_RAW"], errors="coerce").fillna(0)
df["META_H"] = df["DESC"].apply(meta_from_desc)

df = df[df["META_H"].isin([META_22L, META_60L])].copy()
df.loc[df["HORA"] == H_ALMOCO, "HORA"] = H_ALMOCO_DEST
df = df[df["HORA"].between(H_INICIO, H_FIM)].copy()

df_22 = df[df["META_H"] == META_22L].copy()
df_60 = df[df["META_H"] == META_60L].copy()

base_22 = build_hour_table(df_22)
base_60 = build_hour_table(df_60)

# =========================
# KPIs (4 cards)
# =========================
total_dia = float(base_22["QTD"].sum() + base_60["QTD"].sum())
horas_exibidas = len([h for h in HORAS_TURNO if h != H_ALMOCO])
meta_turno_total = float((META_22L + META_60L) * horas_exibidas)

hn = horas_ate_agora()
acum_total = float(
    base_22[base_22["HORA"].isin(hn)]["QTD"].sum() +
    base_60[base_60["HORA"].isin(hn)]["QTD"].sum()
)
meta_acum_total = float((META_22L + META_60L) * len(hn))
delta_acum_total = acum_total - meta_acum_total

ritmo = acum_total / max(1, len(hn))
proj_final_total = ritmo * horas_exibidas
delta_proj_total = proj_final_total - meta_turno_total

st.markdown("<div class='kpi-grid'>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"<div class='kpi'><div class='t'>TOTAL DO DIA</div><div class='v'>{int(total_dia)}</div><div class='u'>Unidades</div></div>", unsafe_allow_html=True)
with k2:
    cor = "var(--green)" if delta_acum_total >= 0 else "var(--red)"
    st.markdown(f"<div class='kpi'><div class='t'>DELTA ACUMULADO</div><div class='v' style='color:{cor};'>{int(delta_acum_total):+d}</div><div class='u'>Meta proporcional até agora</div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='kpi'><div class='t'>PROJEÇÃO FINAL</div><div class='v'>{int(round(proj_final_total,0))}</div><div class='u'>Ritmo x H</div></div>", unsafe_allow_html=True)
with k4:
    cor = "var(--green)" if delta_proj_total >= 0 else "var(--red)"
    st.markdown(f"<div class='kpi'><div class='t'>DELTA PROJEÇÃO</div><div class='v' style='color:{cor};'>{int(round(delta_proj_total,0)):+d}</div><div class='u'>Projeção - Meta turno</div></div>", unsafe_allow_html=True)

# =========================
# PAINÉIS
# =========================
colA, colB = st.columns(2)
with colA:
    render_panel("60L — FORNOS DE BANCADA", base_60, META_60L)
with colB:
    render_panel("22L — AIR FRYER (22L)", base_22, META_22L)
