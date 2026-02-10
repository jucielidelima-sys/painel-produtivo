import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO
from pathlib import Path

# =========================
# CONFIG / TIMEZONE
# =========================
TZ = ZoneInfo("America/Sao_Paulo")

def agora_br():
    return datetime.now(TZ)

st.set_page_config(page_title="Painel Performance Montagem", layout="wide")

# =========================
# ARQUIVO (GitHub RAW)
# =========================
RAW_XLSX_URL = "https://raw.githubusercontent.com/jucielidelima-sys/painel-produtivo/main/movimentos_estoque_dados.xlsx"

# =========================
# LOGO + TÍTULO
# =========================
LOGO_PATH = Path("logo_empresa.png")

# =========================
# REGRAS DE CÁLCULO
# =========================
H_INICIO, H_FIM = 7, 17
H_ALMOCO, H_ALMOCO_DEST = 12, 13
HORAS_TURNO = list(range(H_INICIO, H_FIM + 1))

META_22L = 15
META_60L = 60

# colunas por letra do Excel
COL_HORA = "X"  # horário
COL_QTD = "N"   # quantidade
COL_DESC = "O"  # descrição

# =========================
# CSS – MODO TV (sem rolagem)
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
      footer{ display:none !important; height:0 !important; }

      section.main{
        height:100vh !important; overflow:hidden !important;
        padding-top:0 !important;
      }
      .main .block-container{
        height:100vh !important;
        overflow:hidden !important;
        padding-top:.20rem !important;
        padding-bottom:.10rem !important;
        padding-left:.80rem !important;
        padding-right:.80rem !important;
        max-width: 1920px !important;
      }

      div[data-testid="stVerticalBlock"] > div { gap: .20rem !important; }
      .stMarkdown { margin-bottom:0 !important; }

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

      /* ===== CABEÇALHO LIMPO ===== */
      .header-clean{
        display:flex;
        align-items:center;
        gap:16px;
        margin: 0 0 6px 0;
      }
      .header-clean h1{
        margin:0;
        font-size:28px;
        font-weight:950;
        color:#ffffff;
        letter-spacing:0.5px;
        line-height:1.0;
      }

      /* ===== KPI ===== */
      .kpi-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin:6px 0 8px; }
      .kpi{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:12px;
        padding:8px 10px;
        min-height:56px;
      }
      .kpi .t{ color:var(--muted); font-size:11px; font-weight:900; }
      .kpi .v{ font-size:24px; font-weight:950; margin-top:4px; line-height:1; }
      .kpi .u{ color:var(--orange); font-weight:950; font-size:11px; margin-top:2px; }

      /* ===== PAINÉIS ===== */
      .panel{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:8px 10px 8px 10px;
      }
      .panel h2{
        margin:0 0 4px 0;
        color:var(--orange);
        font-size:13px;
        font-weight:950;
      }

      .table-header{
        display:grid;
        grid-template-columns:58px 56px 60px 60px 1fr;
        gap:8px;
        padding:5px 3px;
        border-bottom:1px solid var(--stroke);
        color:var(--muted);
        font-weight:950;
        font-size:11px;
      }

      .row{
        display:grid;
        grid-template-columns:58px 56px 60px 60px 1fr;
        gap:8px;
        padding:5px 3px;
        border-bottom:1px solid rgba(255,255,255,.08);
        font-size:11px;
        align-items:center;
      }
      .pos{ color:var(--green); font-weight:950;}
      .neg{ color:var(--red); font-weight:950;}

      .barwrap{
        background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.10);
        height:9px;
        border-radius:999px;
        overflow:hidden;
      }
      .bar{ height:100%; border-radius:999px; }
      .bar.orange{ background:var(--orange); }
      .bar.green{ background:var(--green); }
      .smallnote{ color:var(--muted); font-size:10.5px; margin-top:1px; }

      .foot{
        margin-top:6px;
        display:flex;
        gap:6px;
        flex-wrap:wrap;
      }
      .chip{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.12);
        border-radius:999px;
        padding:6px 10px;
        font-size:12px;
        line-height:1.15;
        white-space:nowrap;
      }
      .chip b{ color:var(--text); }
      .chip .o{ color:var(--orange); font-weight:950;}
      .chip .g{ color:var(--green); font-weight:950;}
      .chip .r{ color:var(--red); font-weight:950;}

      .stButton>button{ border-radius:10px; font-weight:950; padding:.30rem .70rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# FUNÇÕES AUXILIARES
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
    return r.content

@st.cache_data(show_spinner=False)
def ler_excel_sem_header(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_excel(BytesIO(file_bytes), header=None)

def render_panel(title, base_horas: pd.DataFrame, meta_h: int):
    st.markdown(f"<div class='panel'><h2>{title}</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='table-header'><div>Hora</div><div>Qtd</div><div>Meta</div><div>Delta</div><div>Termômetro</div></div>",
        unsafe_allow_html=True,
    )

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
              <div>{h:02d}:00</div>
              <div><b>{int(qtd)}</b></div>
              <div>{int(meta)}</div>
              <div class='{delta_class}'>{delta:+.0f}</div>
              <div>
                <div class='barwrap'><div class='bar {bar_class}' style='width:{w:.1f}%'></div></div>
                <div class='smallnote'>{termo_txt}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
        unsafe_allow_html=True,
    )

# =========================
# CABEÇALHO (APENAS LOGO + TÍTULO)
# =========================
st.markdown("<div class='header-clean'>", unsafe_allow_html=True)

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=110)

st.markdown("<h1>Painel Performance Montagem</h1>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# BOTÃO ATUALIZAR
# =========================
c1, c2, c3 = st.columns([2.2, 1.0, 4.0])
with c2:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()

# =========================
# LER DADOS (GitHub)
# =========================
try:
    file_bytes = baixar_excel_bytes(RAW_XLSX_URL)
except Exception as e:
    st.error("Não consegui baixar o Excel do GitHub (RAW).")
    st.code(str(e))
    st.stop()

df0 = ler_excel_sem_header(file_bytes)

s_hora = get_series_by_letter(df0, COL_HORA)
s_qtd  = get_series_by_letter(df0, COL_QTD)
s_desc = get_series_by_letter(df0, COL_DESC)

if s_hora is None or s_qtd is None or s_desc is None:
    st.error("Não consegui localizar as colunas por letra (N/O/X) no arquivo.")
    st.stop()

df = pd.DataFrame({"HORA_RAW": s_hora, "QTD_RAW": s_qtd, "DESC": s_desc}).dropna(how="all")
df["HORA"] = df["HORA_RAW"].apply(parse_hour)
df["QTD"] = pd.to_numeric(df["QTD_RAW"], errors="coerce").fillna(0)
df["META_H"] = df["DESC"].apply(meta_from_desc)

# aplica regra do almoço: 12h vira 13h
df = df[df["META_H"].isin([META_22L, META_60L])].copy()
df.loc[df["HORA"] == H_ALMOCO, "HORA"] = H_ALMOCO_DEST
df = df[df["HORA"].between(H_INICIO, H_FIM)].copy()

df_22 = df[df["META_H"] == META_22L].copy()
df_60 = df[df["META_H"] == META_60L].copy()

base_22 = build_hour_table(df_22)
base_60 = build_hour_table(df_60)

# =========================
# KPIs
# =========================
total_dia = float(base_22["QTD"].sum() + base_60["QTD"].sum())
horas_exibidas = len([h for h in HORAS_TURNO if h != H_ALMOCO])
meta_turno_total = float((META_22L + META_60L) * horas_exibidas)

hn = horas_ate_agora()
acum_total = float(
    base_22[base_22["HORA"].isin(hn)]["QTD"].sum()
    + base_60[base_60["HORA"].isin(hn)]["QTD"].sum()
)
meta_acum_total = float((META_22L + META_60L) * len(hn))
delta_acum_total = acum_total - meta_acum_total

ritmo = acum_total / max(1, len(hn))
proj_final_total = ritmo * horas_exibidas
delta_proj_total = proj_final_total - meta_turno_total

st.markdown("<div class='kpi-grid'>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"<div class='kpi'><div class='t'>TOTAL DO DIA</div><div class='v'>{int(total_dia)}</div><div class='u'>Unidades</div></div>",
        unsafe_allow_html=True,
    )

with k2:
    cor = "var(--green)" if delta_acum_total >= 0 else "var(--red)"
    st.markdown(
        f"<div class='kpi'><div class='t'>DELTA ACUMULADO</div><div class='v' style='color:{cor};'>{int(delta_acum_total):+d}</div><div class='u'>Meta proporcional até agora</div></div>",
        unsafe_allow_html=True,
    )

with k3:
    st.markdown(
        f"<div class='kpi'><div class='t'>PROJEÇÃO FINAL</div><div class='v'>{int(round(proj_final_total,0))}</div><div class='u'>Ritmo x H</div></div>",
        unsafe_allow_html=True,
    )

with k4:
    cor = "var(--green)" if delta_proj_total >= 0 else "var(--red)"
    st.markdown(
        f"<div class='kpi'><div class='t'>DELTA PROJEÇÃO</div><div class='v' style='color:{cor};'>{int(round(delta_proj_total,0)):+d}</div><div class='u'>Projeção - Meta turno</div></div>",
        unsafe_allow_html=True,
    )

# =========================
# PAINÉIS
# =========================
colA, colB = st.columns(2)
with colA:
    render_panel("60L — FORNOS DE BANCADA", base_60, META_60L)
with colB:
    render_panel("22L — AIR FRYER (22L)", base_22, META_22L)
