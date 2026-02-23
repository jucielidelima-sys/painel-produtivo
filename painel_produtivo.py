import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
ARQ = BASE_DIR / "movimentos_estoque_dados.xlsx"
LOGO = BASE_DIR / "logo_empresa.png"

H_INICIO = 7
H_FIM = 17
H_ALMOCO = 12
H_ALMOCO_DEST = 13

HORAS = [h for h in range(H_INICIO, H_FIM + 1) if h != H_ALMOCO]

# ===== METAS =====
META_60L = 60

COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

st.set_page_config(layout="wide")

# ===== FUNÇÕES =====

def excel_letters(n):
    out = []
    for i in range(n):
        s = ""
        x = i
        while True:
            s = chr(65 + x % 26) + s
            x = x // 26 - 1
            if x < 0:
                break
        out.append(s)
    return out

def col_by_letter(df, letter):
    letters = excel_letters(df.shape[1])
    return df.iloc[:, letters.index(letter)]

def parse_hour(x):
    try:
        ts = pd.to_datetime(x)
        return ts.hour
    except:
        try:
            return int(str(x).split(":")[0])
        except:
            return None

def meta_from_desc(desc):
    d = str(desc).upper()

    if "60L" in d:
        return META_60L

    return 0

def build_table(df):
    agg = df.groupby("HORA", as_index=False)["QTD"].sum()
    base = pd.DataFrame({"HORA": HORAS})
    base = base.merge(agg, how="left").fillna(0)
    return base

# ===== HEADER LIMPO =====

col1, col2 = st.columns([6, 2])

with col1:
    if LOGO.exists():
        st.image(str(LOGO), width=140)

with col2:
    st.markdown(
        f"<div style='text-align:right; font-size:18px; color:#ff7a18;'>"
        f"{datetime.now():%d/%m/%Y %H:%M:%S}</div>",
        unsafe_allow_html=True
    )

st.markdown(
    "<h1 style='margin-top:-70px;'>Painel Performance Montagem</h1>",
    unsafe_allow_html=True
)

# ===== DADOS =====

if not ARQ.exists():
    st.error("Arquivo não encontrado.")
    st.stop()

df0 = pd.read_excel(ARQ, header=None)

hora = col_by_letter(df0, COL_HORA)
qtd = col_by_letter(df0, COL_QTD)
desc = col_by_letter(df0, COL_DESC)

df = pd.DataFrame({
    "HORA_RAW": hora,
    "QTD": pd.to_numeric(qtd, errors="coerce").fillna(0),
    "DESC": desc
})

df["HORA"] = df["HORA_RAW"].apply(parse_hour)

df.loc[df["HORA"] == H_ALMOCO, "HORA"] = H_ALMOCO_DEST

df["META_H"] = df["DESC"].apply(meta_from_desc)

df = df[df["META_H"] > 0]
df = df[df["HORA"].between(H_INICIO, H_FIM)]

# ===== FILTROS =====

df_60 = df[df["META_H"] == META_60L]

base_60 = build_table(df_60)

# ===== KPIs =====

acum = base_60["QTD"].sum()
meta_turno = META_60L * len(base_60)

st.markdown(
    f"""
    <div style='display:flex; gap:20px;'>
      <div>Total Dia<br><b style='font-size:28px'>{int(acum)}</b></div>
      <div>Meta Turno<br><b style='font-size:28px'>{int(meta_turno)}</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ===== TABELA =====

st.markdown("### 60L — EMBUTIR / BANCADA")

for _, r in base_60.iterrows():
    h = int(r["HORA"])
    qtd = float(r["QTD"])
    delta = qtd - META_60L
    perc = qtd / META_60L if META_60L else 0

    st.write(f"{h:02d}:00  |  {int(qtd)}  |  Δ {delta:+.0f}  |  {perc:.0%}")
