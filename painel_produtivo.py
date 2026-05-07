import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# ======================================================
# CONFIG
# ======================================================
st.set_page_config(
    page_title="Painel Performance Montagem",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ======================================================
# AUTO REFRESH 30 SEGUNDOS
# ======================================================
components.html(
    """
    <script>
        setTimeout(function(){
            window.parent.location.reload();
        }, 30000);
    </script>
    """,
    height=0,
)

# ======================================================
# PATHS
# ======================================================
BASE_DIR = Path(".")
ARQ_LIMPO = BASE_DIR / "movimentos_estoque_dados.xlsx"
LOGO_PATH = BASE_DIR / "logo_empresa.png"

TZ_BR = ZoneInfo("America/Sao_Paulo")

# ======================================================
# HORÁRIOS
# ======================================================
H_INICIO = 7
H_FIM = 17

H_ALMOCO = 12
H_ALMOCO_DEST = 13

HORAS_TURNO = list(range(H_INICIO, H_FIM + 1))

# ======================================================
# METAS
# ======================================================
META_EMBUTIR = 8
META_60L = 50

# ======================================================
# COLUNAS EXCEL
# ======================================================
COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

# ======================================================
# CSS OTIMIZADO TV 50"
# ======================================================
st.markdown(
    """
    <style>

    html, body, #root, .stApp,
    [data-testid="stAppViewContainer"],
    section.main,
    main,
    .block-container{
        background:#000 !important;
        color:white !important;
    }

    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"]{
        display:none !important;
        height:0 !important;
    }

    .main .block-container{
        padding-top:0rem !important;
        padding-bottom:.2rem !important;
        padding-left:.6rem !important;
        padding-right:.6rem !important;
        max-width:100% !important;
    }

    :root{
        --panel:rgba(255,255,255,.05);
        --panel2:rgba(255,255,255,.03);
        --stroke:rgba(255,255,255,.10);

        --text:#ffffff;
        --muted:rgba(255,255,255,.65);

        --orange:#ff6b00;
        --green:#39d239;
        --red:#ff3b30;
    }

    /* ======================================================
       TOPO
    ====================================================== */

    .brand-title{
        font-size:42px;
        font-weight:1000;
        margin:0;
        line-height:1;
        letter-spacing:-1px;
    }

    .upd{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:18px;
        padding:16px 18px;
        height:100%;
    }

    .upd .lbl{
        color:var(--muted);
        font-size:15px;
        font-weight:900;
    }

    .upd .val{
        color:var(--orange);
        font-weight:1000;
        font-size:24px;
        margin-top:6px;
    }

    /* ======================================================
       KPI GRID
    ====================================================== */

    .kpi-grid{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:14px;
        margin-top:10px;
        margin-bottom:12px;
    }

    .kpi{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:20px;
        padding:18px;
        min-height:145px;
    }

    .kpi .t{
        color:var(--muted);
        font-size:18px;
        font-weight:900;
    }

    .kpi .v{
        font-size:62px;
        font-weight:1000;
        margin-top:12px;
        line-height:1;
    }

    .kpi .u{
        color:var(--orange);
        font-weight:1000;
        font-size:18px;
        margin-top:8px;
    }

    /* ======================================================
       PAINÉIS
    ====================================================== */

    .panel{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:20px;
        padding:14px;
    }

    .panel-title{
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom:12px;
    }

    .panel-title h2{
        margin:0;
        color:var(--orange);
        font-size:30px;
        font-weight:1000;
    }

    .pchips{
        display:flex;
        gap:8px;
    }

    .pch{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.12);
        border-radius:999px;
        padding:8px 16px;
        font-size:15px;
        color:white;
        font-weight:900;
    }

    .g{
        color:var(--green);
    }

    .o{
        color:var(--orange);
    }

    .r{
        color:var(--red);
    }

    /* ======================================================
       TABELA
    ====================================================== */

    .table-header{
        display:grid;
        grid-template-columns:90px 80px 80px 80px 1fr;
        gap:10px;
        padding:10px;
        border-bottom:1px solid var(--stroke);

        font-size:16px;
        font-weight:1000;
        color:var(--muted);
    }

    .row{
        display:grid;
        grid-template-columns:90px 80px 80px 80px 1fr;
        gap:10px;
        padding:10px;
        border-bottom:1px solid rgba(255,255,255,.06);

        font-size:17px;
        align-items:center;
    }

    .pos{
        color:var(--green);
        font-weight:1000;
    }

    .neg{
        color:var(--red);
        font-weight:1000;
    }

    /* ======================================================
       BARRAS
    ====================================================== */

    .barwrap{
        background:rgba(255,255,255,.08);
        border:1px solid rgba(255,255,255,.10);

        height:18px;
        border-radius:999px;
        overflow:hidden;
    }

    .bar{
        height:100%;
        border-radius:999px;
    }

    .bar.orange{
        background:var(--orange);
    }

    .bar.green{
        background:var(--green);
    }

    .smallnote{
        color:var(--muted);
        font-size:15px;
        margin-top:4px;
    }

    /* ======================================================
       FOOTER
    ====================================================== */

    .foot{
        margin-top:10px;
        display:flex;
        gap:8px;
        flex-wrap:wrap;
    }

    .chip{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.10);
        border-radius:999px;

        padding:8px 14px;

        font-size:15px;
        color:white;
        font-weight:900;
    }

    /* ======================================================
       BOTÕES
    ====================================================== */

    .stButton > button{
        border-radius:12px !important;
        font-weight:1000 !important;
        padding:.55rem 1rem !important;

        background:#111 !important;
        color:white !important;

        border:1px solid rgba(255,255,255,.12) !important;
    }

    .stButton > button:hover{
        border:1px solid #ff6b00 !important;
        color:#ff6b00 !important;
    }

    /* ======================================================
       TV MODE
    ====================================================== */

    body.tv-mode,
    body.tv-mode html{
        overflow:hidden !important;
    }

    body.tv-mode [data-testid="stAppViewContainer"],
    body.tv-mode section.main,
    body.tv-mode .block-container{
        height:100vh !important;
        overflow:hidden !important;
    }

    /* ======================================================
       CELULAR
    ====================================================== */

    @media (max-width:768px){

        html, body{
            overflow:auto !important;
        }

        .brand-title{
            font-size:22px;
        }

        .kpi-grid{
            grid-template-columns:repeat(2,1fr);
        }

        .kpi{
            min-height:auto;
            padding:12px;
        }

        .kpi .v{
            font-size:34px;
        }

        .table-header{
            grid-template-columns:60px 50px 50px 60px 1fr;
            font-size:11px;
        }

        .row{
            grid-template-columns:60px 50px 50px 60px 1fr;
            font-size:11px;
        }

        .smallnote{
            font-size:10px;
        }

        .panel-title h2{
            font-size:18px;
        }

        .pch{
            font-size:11px;
            padding:5px 10px;
        }

        .chip{
            font-size:11px;
            padding:5px 10px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ======================================================
# FUNÇÕES
# ======================================================
def excel_letters(n_cols):

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


def get_series_by_letter(df_noheader, letter):

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

    if not s:
        return None

    try:
        return int(s.split(":")[0])

    except:
        return None


def meta_from_desc(desc):

    d = str(desc).upper()

    if "EMBUTIR" in d:
        return META_EMBUTIR

    if "60L" in d:
        return META_60L

    return 0


def build_hour_table(df_line):

    agg = df_line.groupby(
        "HORA",
        as_index=False
    )["QTD"].sum()

    base = pd.DataFrame({
        "HORA":[
            h for h in HORAS_TURNO
            if h != H_ALMOCO
        ]
    })

    base = base.merge(
        agg,
        on="HORA",
        how="left"
    ).fillna({"QTD":0})

    return base.sort_values("HORA")


def render_panel(title, base_horas, meta_h):

    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='panel-title'>
            <h2>{title}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='table-header'>
            <div>Hora</div>
            <div>Qtd</div>
            <div>Meta</div>
            <div>Delta</div>
            <div>Termômetro</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for _, r in base_horas.iterrows():

        h = int(r["HORA"])
        qtd = float(r["QTD"])

        meta = float(meta_h)

        delta = qtd - meta

        perc = qtd / meta if meta else 0

        w = max(0, min(perc, 1.0)) * 100

        bar_class = "green" if perc >= 1 else "orange"

        termo_txt = (
            f"{int(qtd)}/{int(meta)} "
            f"({int(round(perc * 100, 0))}%)"
        )

        st.markdown(
            f"""
            <div class='row'>

                <div>{h:02d}:00</div>

                <div><b>{int(qtd)}</b></div>

                <div>{int(meta)}</div>

                <div class='{"pos" if delta >= 0 else "neg"}'>
                    {delta:+.0f}
                </div>

                <div>

                    <div class='barwrap'>
                        <div class='bar {bar_class}'
                             style='width:{w:.1f}%'>
                        </div>
                    </div>

                    <div class='smallnote'>
                        {termo_txt}
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# LOAD EXCEL
# ======================================================
if not ARQ_LIMPO.exists():

    st.error(
        "Não encontrei movimentos_estoque_dados.xlsx"
    )

    st.stop()

mtime = ARQ_LIMPO.stat().st_mtime

ultima_atualizacao = datetime.fromtimestamp(
    mtime,
    tz=TZ_BR
).strftime("%d/%m/%Y %H:%M:%S")

df0 = pd.read_excel(
    ARQ_LIMPO,
    header=None
)

s_hora = get_series_by_letter(df0, COL_HORA)
s_qtd = get_series_by_letter(df0, COL_QTD)
s_desc = get_series_by_letter(df0, COL_DESC)

df = pd.DataFrame({
    "HORA_RAW":s_hora,
    "QTD_RAW":s_qtd,
    "DESC":s_desc
}).dropna(how="all")

df["HORA"] = df["HORA_RAW"].apply(parse_hour)

df["QTD"] = pd.to_numeric(
    df["QTD_RAW"],
    errors="coerce"
).fillna(0)

df["META_H"] = df["DESC"].apply(meta_from_desc)

df = df[
    df["META_H"].isin(
        [META_EMBUTIR, META_60L]
    )
]

df.loc[
    df["HORA"] == H_ALMOCO,
    "HORA"
] = H_ALMOCO_DEST

df = df[
    df["HORA"].between(H_INICIO, H_FIM)
]

df_EMBUTIR = df[
    df["META_H"] == META_EMBUTIR
]

df_60L = df[
    df["META_H"] == META_60L
]

base_EMBUTIR = build_hour_table(df_EMBUTIR)
base_60L = build_hour_table(df_60L)

# ======================================================
# MODOS
# ======================================================
c1, c2 = st.columns([1,1])

with c1:
    modo_mobile = st.toggle(
        "📱 MODO CELULAR",
        value=False
    )

with c2:
    modo_tv = st.toggle(
        "📺 MODO TV",
        value=True
    )

if modo_tv and not modo_mobile:

    st.markdown(
        """
        <script>
            document.body.classList.add('tv-mode');
        </script>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <script>
            document.body.classList.remove('tv-mode');
        </script>
        """,
        unsafe_allow_html=True,
    )

# ======================================================
# TOPO
# ======================================================
top1, top2 = st.columns(
    [1.6, 1],
    vertical_alignment="center"
)

with top1:

    c1, c2 = st.columns(
        [1,6],
        vertical_alignment="center"
    )

    with c1:

        if LOGO_PATH.exists():

            st.image(
                str(LOGO_PATH),
                width=120
            )

    with c2:

        st.markdown(
            "<div class='brand-title'>Painel Performance Montagem</div>",
            unsafe_allow_html=True,
        )

with top2:

    st.markdown(
        f"""
        <div class='upd'>

            <div class='lbl'>
                Última atualização
            </div>

            <div class='val'>
                {ultima_atualizacao}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

# ======================================================
# KPI
# ======================================================
total_dia = float(
    base_EMBUTIR["QTD"].sum()
    +
    base_60L["QTD"].sum()
)

st.markdown(
    f"""
    <div class='kpi-grid'>

        <div class='kpi'>
            <div class='t'>TOTAL DO DIA</div>
            <div class='v'>{int(total_dia)}</div>
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
    unsafe_allow_html=True
)

# ======================================================
# PAINÉIS
# ======================================================
if modo_mobile:

    render_panel(
        "60L — FORNOS DE BANCADA",
        base_60L,
        META_60L
    )

    render_panel(
        "EMBUTIR — EMBUTIR",
        base_EMBUTIR,
        META_EMBUTIR
    )

else:

    col1, col2 = st.columns(2)

    with col1:

        render_panel(
            "60L — FORNOS DE BANCADA",
            base_60L,
            META_60L
        )

    with col2:

        render_panel(
            "EMBUTIR — EMBUTIR",
            base_EMBUTIR,
            META_EMBUTIR
        )
