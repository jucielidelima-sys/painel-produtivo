import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# =========================
# AUTO REFRESH 30 SEGUNDOS
# =========================
st_autorefresh(interval=30 * 1000, key="refresh")

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Painel Performance Montagem",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(".")
ARQ_LIMPO = BASE_DIR / "movimentos_estoque_dados.xlsx"
LOGO_PATH = BASE_DIR / "logo_empresa.png"

TZ_BR = ZoneInfo("America/Sao_Paulo")

# BASE DE CÁLCULO
H_INICIO, H_FIM = 7, 17
H_ALMOCO, H_ALMOCO_DEST = 12, 13
HORAS_TURNO = list(range(H_INICIO, H_FIM + 1))

META_EMBUTIR = 8
META_60L = 50

# colunas por letra do Excel
COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

# =========================
# CSS (MODO TV FIXO)
# =========================
st.markdown(
    """
    <style>

    html, body, [class*="css"] {
        background-color: #000000;
        color: white;
        overflow: hidden;
    }

    .stApp {
        background-color: #000000;
        overflow: hidden;
    }

    header[data-testid="stHeader"] {
        display: none;
    }

    [data-testid="stToolbar"] {
        display: none;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .main .block-container {
        padding-top: 0.4rem;
        padding-bottom: 0.2rem;
        max-width: 100%;
    }

    :root{
        --panel:rgba(255,255,255,.05);
        --panel2:rgba(255,255,255,.03);
        --stroke:rgba(255,255,255,.10);
        --text:rgba(255,255,255,.92);
        --muted:rgba(255,255,255,.65);
        --orange:#ff7a18;
        --green:#17c964;
        --red:#ff4d4f;
    }

    .brand-title{
        font-size:36px;
        font-weight:950;
        color:white;
        margin-top:10px;
    }

    .upd{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:12px;
        padding:8px 12px;
        text-align:center;
    }

    .upd .lbl{
        color:var(--muted);
        font-size:12px;
        font-weight:900;
    }

    .upd .val{
        color:var(--orange);
        font-weight:950;
        font-size:14px;
    }

    .kpi-grid{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:12px;
        margin-top:10px;
        margin-bottom:10px;
    }

    .kpi{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:12px;
        text-align:center;
    }

    .kpi .t{
        color:var(--muted);
        font-size:12px;
        font-weight:900;
    }

    .kpi .v{
        font-size:34px;
        font-weight:950;
        margin-top:5px;
    }

    .kpi .u{
        color:var(--orange);
        font-weight:950;
        font-size:12px;
    }

    .panel{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:10px;
    }

    .panel-title{
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:8px;
    }

    .panel-title h2{
        color:var(--orange);
        font-size:16px;
        margin:0;
    }

    .pchips{
        display:flex;
        gap:6px;
    }

    .pch{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.12);
        border-radius:999px;
        padding:4px 10px;
        font-size:11px;
        color:white;
    }

    .table-header{
        display:grid;
        grid-template-columns:70px 70px 70px 70px 1fr;
        gap:8px;
        padding:6px;
        border-bottom:1px solid var(--stroke);
        font-size:12px;
        font-weight:900;
        color:var(--muted);
    }

    .row{
        display:grid;
        grid-template-columns:70px 70px 70px 70px 1fr;
        gap:8px;
        padding:6px;
        border-bottom:1px solid rgba(255,255,255,.06);
        font-size:12px;
        align-items:center;
    }

    .pos{
        color:var(--green);
        font-weight:950;
    }

    .neg{
        color:var(--red);
        font-weight:950;
    }

    .barwrap{
        background:rgba(255,255,255,.08);
        height:10px;
        border-radius:999px;
        overflow:hidden;
    }

    .bar{
        height:100%;
        border-radius:999px;
    }

    .green{
        background:var(--green);
    }

    .orange{
        background:var(--orange);
    }

    .smallnote{
        font-size:10px;
        color:var(--muted);
    }

    .foot{
        display:flex;
        gap:6px;
        flex-wrap:wrap;
        margin-top:8px;
    }

    .chip{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.10);
        border-radius:999px;
        padding:5px 8px;
        font-size:11px;
        color:white;
    }

    button[kind="secondary"]{
        background:#ff7a18 !important;
        color:white !important;
        border:none !important;
        border-radius:10px !important;
        font-weight:900 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HELPERS
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
    except:
        pass

    s = str(x).strip()

    try:
        return int(s.split(":")[0])
    except:
        return None

def meta_from_desc(desc: str) -> int:
    d = str(desc).upper()

    if "EMBUTIR" in d:
        return META_EMBUTIR

    if "60L" in d:
        return META_60L

    return 0

def horas_ate_agora():
    agora = datetime.now(TZ_BR).hour
    h_max = max(H_INICIO, min(agora, H_FIM))

    horas = [h for h in range(H_INICIO, h_max + 1) if h != H_ALMOCO]

    return horas if horas else [H_INICIO]

def build_hour_table(df_line: pd.DataFrame):
    agg = df_line.groupby("HORA", as_index=False)["QTD"].sum()

    base = pd.DataFrame({
        "HORA": [h for h in HORAS_TURNO if h != H_ALMOCO]
    })

    base = base.merge(agg, on="HORA", how="left").fillna({"QTD": 0})

    base["HORA"] = base["HORA"].astype(int)
    base["QTD"] = base["QTD"].astype(float)

    return base.sort_values("HORA")

def render_panel(title, base_horas: pd.DataFrame, meta_h: int):

    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='panel-title'>
            <h2>{title}</h2>
        </div>

        <div class='table-header'>
            <div>Hora</div>
            <div>Qtd</div>
            <div>Meta</div>
            <div>Δ</div>
            <div>Performance</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for _, r in base_horas.iterrows():

        h = int(r["HORA"])
        qtd = float(r["QTD"])

        meta = meta_h

        delta = qtd - meta

        perc = (qtd / meta) if meta else 0

        w = min(perc, 1.0) * 100

        cor = "green" if perc >= 1 else "orange"

        st.markdown(
            f"""
            <div class='row'>
                <div>{h:02d}:00</div>
                <div><b>{int(qtd)}</b></div>
                <div>{meta}</div>
                <div class='{"pos" if delta >= 0 else "neg"}'>
                    {delta:+.0f}
                </div>

                <div>
                    <div class='barwrap'>
                        <div class='bar {cor}' style='width:{w:.1f}%'></div>
                    </div>

                    <div class='smallnote'>
                        {int(perc * 100)}%
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
if not ARQ_LIMPO.exists():
    st.error("Arquivo Excel não encontrado.")
    st.stop()

mtime = ARQ_LIMPO.stat().st_mtime

ultima_atualizacao = datetime.fromtimestamp(
    mtime,
    tz=TZ_BR
).strftime("%d/%m/%Y %H:%M:%S")

@st.cache_data(ttl=30)
def load_noheader(path: str):
    return pd.read_excel(path, header=None)

df0 = load_noheader(str(ARQ_LIMPO))

s_hora = get_series_by_letter(df0, COL_HORA)
s_qtd  = get_series_by_letter(df0, COL_QTD)
s_desc = get_series_by_letter(df0, COL_DESC)

df = pd.DataFrame({
    "HORA_RAW": s_hora,
    "QTD_RAW": s_qtd,
    "DESC": s_desc
})

df["HORA"] = df["HORA_RAW"].apply(parse_hour)

df["QTD"] = pd.to_numeric(
    df["QTD_RAW"],
    errors="coerce"
).fillna(0)

df["META_H"] = df["DESC"].apply(meta_from_desc)

df = df[df["META_H"].isin([META_EMBUTIR, META_60L])]

df.loc[df["HORA"] == H_ALMOCO, "HORA"] = H_ALMOCO_DEST

df = df[df["HORA"].between(H_INICIO, H_FIM)]

df_60L = df[df["META_H"] == META_60L]
df_EMBUTIR = df[df["META_H"] == META_EMBUTIR]

base_60L = build_hour_table(df_60L)
base_EMBUTIR = build_hour_table(df_EMBUTIR)

# =========================
# TOPO
# =========================
top1, top2 = st.columns([4, 1])

with top1:

    c1, c2 = st.columns([1, 8])

    with c1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=90)

    with c2:
        st.markdown(
            "<div class='brand-title'>Painel Performance Montagem</div>",
            unsafe_allow_html=True,
        )

with top2:

    st.markdown(
        f"""
        <div class='upd'>
            <div class='lbl'>Última atualização</div>
            <div class='val'>{ultima_atualizacao}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# KPIS
# =========================
total_dia = int(base_60L["QTD"].sum() + base_EMBUTIR["QTD"].sum())

st.markdown(
    f"""
    <div class='kpi-grid'>

        <div class='kpi'>
            <div class='t'>TOTAL PRODUZIDO</div>
            <div class='v'>{total_dia}</div>
            <div class='u'>UNIDADES</div>
        </div>

        <div class='kpi'>
            <div class='t'>META 60L</div>
            <div class='v'>{META_60L}</div>
            <div class='u'>POR HORA</div>
        </div>

        <div class='kpi'>
            <div class='t'>META EMBUTIR</div>
            <div class='v'>{META_EMBUTIR}</div>
            <div class='u'>POR HORA</div>
        </div>

        <div class='kpi'>
            <div class='t'>AUTO REFRESH</div>
            <div class='v'>30s</div>
            <div class='u'>ATIVO</div>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# PAINÉIS
# =========================
col1, col2 = st.columns(2)

with col1:
    render_panel(
        "60L — FORNOS DE BANCADA",
        base_60L,
        META_60L
    )

with col2:
    render_panel(
        "EMBUTIR — LINHA EMBUTIR",
        base_EMBUTIR,
        META_EMBUTIR
    )
