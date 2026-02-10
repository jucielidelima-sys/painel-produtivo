import streamlit as st
import pandas as pd
from pathlib import Path
import time
from datetime import datetime, date
import matplotlib.pyplot as plt
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Painel Performance Montagem", layout="wide")

# Ajuste para o seu ambiente local (Windows) OU para Streamlit Cloud (GitHub)
BASE_DIR = Path(".")  # no repo
ARQ_LIMPO_LOCAL = Path(r"C:\Users\Jucieli\Desktop\automacao_senior\movimentos_estoque_dados.xlsx")
ARQ_LIMPO = BASE_DIR / "movimentos_estoque_dados.xlsx"

LOGO_PATH = BASE_DIR / "logo_empresa.png"

# BASE DE CÁLCULO
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
# CSS (TV / COMPACTO)
# =========================
st.markdown(
    """
    <style>
      html, body, #root, .stApp,
      [data-testid="stAppViewContainer"], section.main, main, .block-container{
        background:#000 !important; color:rgba(255,255,255,.92) !important;
      }
      /* TV sem rolagem */
      html, body { height:100%; overflow:hidden !important; }
      [data-testid="stAppViewContainer"] { height:100vh !important; overflow:hidden !important; }
      section.main { height:100vh !important; overflow:hidden !important; }
      .block-container { height:100vh !important; overflow:hidden !important; padding-top:.4rem; padding-bottom:.2rem; max-width: 1500px; }

      header[data-testid="stHeader"] { height: 0.2rem !important; }
      div[data-testid="stToolbar"] { visibility: hidden !important; height: 0px !important; }

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

      /* ===== TOP BAR ===== */
      .topbar{
        display:flex; align-items:center; justify-content:space-between;
        gap:14px; margin: 2px 0 6px 0;
      }
      .top-left{
        display:flex; align-items:center; gap:12px; min-width: 520px;
      }
      .brand-title{
        font-size:34px; font-weight:950; margin:0; line-height:1.1;
      }
      .right-tools{
        display:flex; align-items:center; gap:10px;
      }
      .upd{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:12px;
        padding:8px 12px;
        min-width:260px;
      }
      .upd .lbl{ color:var(--muted); font-size:12px; font-weight:800; }
      .upd .val{ color:var(--orange); font-weight:950; font-size:14px; margin-top:4px; }

      /* ===== KPI ===== */
      .kpi-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:6px 0 8px;}
      .kpi{ background:var(--panel); border:1px solid var(--stroke); border-radius:14px; padding:10px 12px;}
      .kpi .t{ color:var(--muted); font-size:12px; font-weight:900;}
      .kpi .v{ font-size:30px; font-weight:950; margin-top:6px; line-height:1;}
      .kpi .u{ color:var(--orange); font-weight:950; font-size:12px; margin-top:4px;}

      /* ===== SECTIONS ===== */
      .section-grid{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }
      .panel{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:10px;
      }
      .panel h2{ margin:0 0 8px 0; color:var(--orange); font-size:14px; font-weight:950; letter-spacing:.4px;}

      .table-header{ display:grid; grid-template-columns:70px 70px 70px 70px 1fr; gap:8px; padding:8px 6px;
                     border-bottom:1px solid var(--stroke); color:var(--muted); font-weight:950; font-size:12px;}
      .row{ display:grid; grid-template-columns:70px 70px 70px 70px 1fr; gap:8px; padding:8px 6px;
            border-bottom:1px solid rgba(255,255,255,.08); font-size:12px; align-items:center; }
      .pos{ color:var(--green); font-weight:950;}
      .neg{ color:var(--red); font-weight:950;}

      .barwrap{ background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.10);
                height:10px; border-radius:999px; overflow:hidden;}
      .bar{ height:100%; border-radius:999px;}
      .bar.orange{ background:var(--orange); }
      .bar.green{ background:var(--green); }

      .foot{ margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;}
      .chip{ background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.10);
             border-radius:999px; padding:6px 10px; font-size:12px; color:var(--muted);}
      .chip b{ color:var(--text); }
      .chip .o{ color:var(--orange); font-weight:950;}
      .chip .g{ color:var(--green); font-weight:950;}
      .chip .r{ color:var(--red); font-weight:950;}

      .smallnote{ color:var(--muted); font-size:12px; margin-top:4px;}
      .stButton>button{ border-radius:10px; font-weight:950; padding:.35rem .8rem; }
      div[data-testid="stVerticalBlock"] > div { gap: .25rem; }
    </style>
    """,
    unsafe_allow_html=True
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
    agora = datetime.now().hour
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

def render_panel(title, base_horas: pd.DataFrame, meta_h: int):
    st.markdown(f"<div class='panel'><h2>{title}</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='table-header'><div>Hora</div><div>Qtd</div><div>Meta</div><div>Delta</div><div>Termômetro</div></div>",
        unsafe_allow_html=True
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
        </div></div>
        """,
        unsafe_allow_html=True
    )

# =========================
# DATA SOURCE
# =========================
# (Cloud) lê do repo. (Local) se não existir no repo, tenta do caminho local.
if not ARQ_LIMPO.exists() and ARQ_LIMPO_LOCAL.exists():
    # copia para o diretório atual (ajuda quando rodando local)
    try:
        ARQ_LIMPO.write_bytes(ARQ_LIMPO_LOCAL.read_bytes())
    except Exception:
        pass

if not ARQ_LIMPO.exists():
    st.error("Não encontrei movimentos_estoque_dados.xlsx no repositório. Suba o arquivo no GitHub.")
    st.stop()

mtime = ARQ_LIMPO.stat().st_mtime
ultima_atualizacao = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")

@st.cache_data(show_spinner=False)
def load_noheader(path: str, mtime_cache: float) -> pd.DataFrame:
    return pd.read_excel(path, header=None)

# =========================
# TOP BAR (1 LINHA)
# =========================
col_top = st.columns([8, 2])

with col_top[0]:
    left = st.container()
with col_top[1]:
    right = st.container()

with left:
    # Barra superior manual em HTML
    logo_html = ""
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)
    st.markdown(
        f"""
        <div class="topbar">
          <div class="top-left">
            <div class="brand-title">Painel Performance Montagem</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with right:
    # Botão + última atualização na mesma área (direita)
    cbtn, cupd = st.columns([1.2, 2.0], vertical_alignment="center")
    with cbtn:
        if st.button("🔄 Atualizar painel"):
            st.cache_data.clear()
            st.rerun()
    with cupd:
        st.markdown(
            f"<div class='upd'><div class='lbl'>Última atualização (arquivo)</div><div class='val'>{ultima_atualizacao}</div></div>",
            unsafe_allow_html=True
        )

# =========================
# LOAD + TRANSFORM
# =========================
df0 = load_noheader(str(ARQ_LIMPO), mtime)

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
# GRÁFICO (% realizado x % projeção)
# =========================
meta_turno_total_safe = max(1.0, meta_turno_total)
perc_realizado = max(0.0, min(100.0, (acum_total / meta_turno_total_safe) * 100.0))
perc_projecao = max(0.0, min(200.0, (proj_final_total / meta_turno_total_safe) * 100.0))

st.markdown("<div class='panel'><h2>Progresso do turno (percentual)</h2></div>", unsafe_allow_html=True)

fig = plt.figure(figsize=(9, 1.6), dpi=140)
ax = fig.add_subplot(111)
ax.set_xlim(0, 200)
ax.set_ylim(0, 1)
ax.set_yticks([])
ax.set_xticks([0, 50, 100, 150, 200])
ax.tick_params(axis='x', colors='white', labelsize=8)
ax.set_facecolor("black")
fig.patch.set_facecolor("black")

# barras (sem definir cores via style global do matplotlib; aqui é direto no plot)
ax.barh(0.65, perc_realizado, height=0.22, color="#17c964")
ax.text(min(perc_realizado + 2, 198), 0.65, f"Realizado: {perc_realizado:.0f}%", va="center", color="white", fontsize=9)

ax.barh(0.30, perc_projecao, height=0.22, color="#ff7a18")
ax.text(min(perc_projecao + 2, 198), 0.30, f"Projeção: {perc_projecao:.0f}%", va="center", color="white", fontsize=9)

# linha 100%
ax.axvline(100, color="white", linewidth=1, alpha=0.35)
ax.text(100, 0.98, "100%", ha="center", va="top", color="white", fontsize=8, alpha=0.7)

for spine in ax.spines.values():
    spine.set_visible(False)

st.pyplot(fig, use_container_width=True)

# =========================
# PAINÉIS 60L e 22L
# =========================
colA, colB = st.columns(2)
with colA:
    render_panel("60L — FORNOS DE BANCADA", base_60, META_60L)
with colB:
    render_panel("22L — AIR FRYER (22L)", base_22, META_22L)
