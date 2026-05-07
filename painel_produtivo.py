import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Painel Performance Montagem",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

BASE_DIR = Path(".")
ARQ_LIMPO = BASE_DIR / "movimentos_estoque_dados.xlsx"
LOGO_PATH = BASE_DIR / "logo_empresa.png"

TZ_BR = ZoneInfo("America/Sao_Paulo")

H_INICIO = 7
H_FIM = 17
H_ALMOCO = 12
H_ALMOCO_DEST = 13

HORAS_TURNO = list(range(H_INICIO, H_FIM + 1))

META_EMBUTIR = 8
META_60L = 50

COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

st.markdown(
    """
    <style>
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        display:none !important;
        height:0 !important;
    }

    .stApp {
        background:#000000 !important;
        color:white !important;
    }

    .block-container {
        padding-top:0rem !important;
        padding-left:0.6rem !important;
        padding-right:0.6rem !important;
        padding-bottom:0.2rem !important;
        max-width:100% !important;
    }

    div[data-testid="stMetric"] {
        background:rgba(255,255,255,0.05);
        border:1px solid rgba(255,255,255,0.12);
        border-radius:18px;
        padding:18px;
        min-height:130px;
    }

    div[data-testid="stMetricLabel"] {
        font-size:18px !important;
        font-weight:900 !important;
        color:rgba(255,255,255,0.70) !important;
    }

    div[data-testid="stMetricValue"] {
        font-size:58px !important;
        font-weight:1000 !important;
        color:white !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size:18px !important;
        font-weight:900 !important;
    }

    .titulo-painel {
        font-size:42px;
        font-weight:1000;
        color:white;
        line-height:1;
    }

    .sub-info {
        font-size:16px;
        font-weight:900;
        color:#ff6b00;
    }

    .titulo-linha {
        font-size:28px;
        font-weight:1000;
        color:#ff6b00;
        margin-top:6px;
        margin-bottom:4px;
    }

    .stDataFrame {
        border:1px solid rgba(255,255,255,0.12);
        border-radius:18px;
        overflow:hidden;
    }

    button[kind="secondary"] {
        background:#111 !important;
        color:white !important;
        border:1px solid rgba(255,255,255,0.20) !important;
        border-radius:12px !important;
        font-weight:900 !important;
    }

    @media (max-width:768px) {
        .titulo-painel {
            font-size:24px;
        }

        div[data-testid="stMetricValue"] {
            font-size:32px !important;
        }

        div[data-testid="stMetric"] {
            min-height:auto;
            padding:12px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
    except Exception:
        pass

    s = str(x).strip()

    if not s:
        return None

    try:
        return int(s.split(":")[0])
    except Exception:
        return None


def meta_from_desc(desc):
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


def build_hour_table(df_line, meta_h):
    agg = df_line.groupby("HORA", as_index=False)["QTD"].sum()

    base = pd.DataFrame({
        "Hora": [h for h in HORAS_TURNO if h != H_ALMOCO]
    })

    base = base.merge(
        agg.rename(columns={"HORA": "Hora", "QTD": "Qtd"}),
        on="Hora",
        how="left"
    ).fillna({"Qtd": 0})

    base["Hora"] = base["Hora"].astype(int)
    base["Qtd"] = base["Qtd"].astype(float)
    base["Meta"] = meta_h
    base["Delta"] = base["Qtd"] - base["Meta"]
    base["Performance"] = base["Qtd"] / base["Meta"]

    base["Hora"] = base["Hora"].apply(lambda h: f"{h:02d}:00")
    base["Qtd"] = base["Qtd"].astype(int)
    base["Meta"] = base["Meta"].astype(int)
    base["Delta"] = base["Delta"].astype(int)

    return base


def calc_kpis_linha(base, meta_h):
    hn = [f"{h:02d}:00" for h in horas_ate_agora()]

    acumulado = base[base["Hora"].isin(hn)]["Qtd"].sum()
    meta_acum = meta_h * len(hn)
    delta_acum = acumulado - meta_acum

    ritmo = acumulado / max(1, len(hn))
    proj = ritmo * len(base)

    meta_turno = meta_h * len(base)
    delta_proj = proj - meta_turno

    realizado_pct = acumulado / meta_acum if meta_acum else 0
    proj_pct = proj / meta_turno if meta_turno else 0

    return acumulado, delta_acum, proj, delta_proj, realizado_pct, proj_pct


def render_linha(titulo, base, meta_h):
    acumulado, delta_acum, proj, delta_proj, realizado_pct, proj_pct = calc_kpis_linha(base, meta_h)

    st.markdown(
        f"<div class='titulo-linha'>{titulo}</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Realizado", f"{realizado_pct:.0%}")
    c2.metric("Projeção", f"{proj_pct:.0%}")
    c3.metric("Acum.", f"{int(acumulado)}", f"{int(delta_acum):+d}")
    c4.metric("Proj.", f"{int(round(proj, 0))}", f"{int(round(delta_proj, 0)):+d}")

    st.dataframe(
        base,
        hide_index=True,
        use_container_width=True,
        height=390,
        column_config={
            "Hora": st.column_config.TextColumn("Hora", width="small"),
            "Qtd": st.column_config.NumberColumn("Qtd", width="small"),
            "Meta": st.column_config.NumberColumn("Meta", width="small"),
            "Delta": st.column_config.NumberColumn("Delta", width="small"),
            "Performance": st.column_config.ProgressColumn(
                "Termômetro",
                min_value=0,
                max_value=1,
                format="%.0f%%",
                width="large",
            ),
        },
    )


if not ARQ_LIMPO.exists():
    st.error("Não encontrei o arquivo movimentos_estoque_dados.xlsx no repositório.")
    st.stop()

mtime = ARQ_LIMPO.stat().st_mtime

ultima_atualizacao = datetime.fromtimestamp(
    mtime,
    tz=TZ_BR
).strftime("%d/%m/%Y %H:%M:%S")

df0 = pd.read_excel(ARQ_LIMPO, header=None)

s_hora = get_series_by_letter(df0, COL_HORA)
s_qtd = get_series_by_letter(df0, COL_QTD)
s_desc = get_series_by_letter(df0, COL_DESC)

if s_hora is None or s_qtd is None or s_desc is None:
    st.error("Não consegui localizar as colunas N, O e X no arquivo Excel.")
    st.stop()

df = pd.DataFrame({
    "HORA_RAW": s_hora,
    "QTD_RAW": s_qtd,
    "DESC": s_desc,
}).dropna(how="all")

df["HORA"] = df["HORA_RAW"].apply(parse_hour)
df["QTD"] = pd.to_numeric(df["QTD_RAW"], errors="coerce").fillna(0)
df["META_H"] = df["DESC"].apply(meta_from_desc)

df = df[df["META_H"].isin([META_EMBUTIR, META_60L])].copy()
df.loc[df["HORA"] == H_ALMOCO, "HORA"] = H_ALMOCO_DEST
df = df[df["HORA"].between(H_INICIO, H_FIM)].copy()

df_60L = df[df["META_H"] == META_60L].copy()
df_EMBUTIR = df[df["META_H"] == META_EMBUTIR].copy()

base_60L = build_hour_table(df_60L, META_60L)
base_EMBUTIR = build_hour_table(df_EMBUTIR, META_EMBUTIR)

modo_mobile = st.toggle("📱 MODO CELULAR", value=False)
modo_tv = st.toggle("📺 MODO TV", value=True)

if modo_tv and not modo_mobile:
    st.markdown(
        """
        <style>
        html, body, .stApp, [data-testid="stAppViewContainer"], .block-container {
            overflow:hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

top1, top2 = st.columns([2.4, 1], vertical_alignment="center")

with top1:
    l1, l2 = st.columns([0.35, 3], vertical_alignment="center")

    with l1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=95)

    with l2:
        st.markdown(
            "<div class='titulo-painel'>Painel Performance Montagem</div>",
            unsafe_allow_html=True,
        )

with top2:
    st.metric("Última atualização", ultima_atualizacao)

total_dia = int(base_60L["Qtd"].sum() + base_EMBUTIR["Qtd"].sum())

horas_exibidas = len([h for h in HORAS_TURNO if h != H_ALMOCO])
meta_turno_total = int((META_60L + META_EMBUTIR) * horas_exibidas)

hn_texto = [f"{h:02d}:00" for h in horas_ate_agora()]

acum_total = int(
    base_60L[base_60L["Hora"].isin(hn_texto)]["Qtd"].sum()
    + base_EMBUTIR[base_EMBUTIR["Hora"].isin(hn_texto)]["Qtd"].sum()
)

meta_acum_total = int((META_60L + META_EMBUTIR) * len(hn_texto))
delta_acum_total = int(acum_total - meta_acum_total)

ritmo_total = acum_total / max(1, len(hn_texto))
proj_final_total = int(round(ritmo_total * horas_exibidas, 0))
delta_proj_total = int(proj_final_total - meta_turno_total)

k1, k2, k3, k4 = st.columns(4)

k1.metric("TOTAL DO DIA", f"{total_dia}", "Unidades")
k2.metric("DELTA ACUMULADO", f"{delta_acum_total:+d}", "Meta até agora")
k3.metric("PROJEÇÃO FINAL", f"{proj_final_total}", "Ritmo x horas")
k4.metric("DELTA PROJEÇÃO", f"{delta_proj_total:+d}", "Proj - Meta")

if modo_mobile:
    render_linha("60L — FORNOS DE BANCADA", base_60L, META_60L)
    render_linha("EMBUTIR — EMBUTIR", base_EMBUTIR, META_EMBUTIR)
else:
    col1, col2 = st.columns(2)

    with col1:
        render_linha("60L — FORNOS DE BANCADA", base_60L, META_60L)

    with col2:
        render_linha("EMBUTIR — EMBUTIR", base_EMBUTIR, META_EMBUTIR)
