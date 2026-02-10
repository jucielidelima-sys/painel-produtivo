import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Painel Performance Montagem", layout="wide")

BASE_DIR = Path(".")  # repo / Streamlit Cloud
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

      /* TV sem rolagem (se faltar a última linha, reduza um pouco padding e fonte) */
      html, body { height:100%; overflow:hidden !important; }
      [data-testid="stAppViewContainer"] { height:100vh !important; overflow:hidden !important; }
      section.main { height:100vh !important; overflow:hidden !important; }
      .block-container {
        height:100vh !important; overflow:hidden !important;
        padding-top:.30rem; padding-bottom:.15rem;
        max-width: 1520px;
      }

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
        display:flex; align-items:center; gap:12px;
      }
      .brand-title{
        font-size:34px; font-weight:950; margin:0; line-height:1.05;
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
      .upd .lbl{ color:var(--muted); font-size:12px; font-weight:900; }
      .upd .val{ color:var(--orange); font-weight:950; font-size:14px; margin-top:4px; }

      /* ===== KPI ===== */
      .kpi-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:6px 0 8px;}
      .kpi{ background:var(--panel); border:1px solid var(--stroke); border-radius:14px; padding:10px 12px;}
      .kpi .t{ color:var(--muted); font-size:12px; font-weight:900;}
      .kpi .v{ font-size:30px; font-weight:950; margin-top:6px; line-height:1;}
      .kpi .u{ color:var(--orange); font-weight:950; font-size:12px; margin-top:4px;}

      /* ===== MINI PROGRESS (sem matplotlib) ===== */
      .mini{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:10px 12px;
        margin: 6px 0 8px;
      }
      .mini h3{ margin:0 0 6px 0; color:var(--orange); font-size:13px; font-weight:950; }
      .p-row{ display:flex; align-items:center; gap:10px; margin: 6px 0; }
      .p-lbl{ width: 92px; color: var(--muted); font-size:12px; font-weight:900; }
      .p-barwrap{
        flex:1;
        background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.10);
        height:10px; border-radius:999px; overflow:hidden;
      }
      .p-bar{ height:100%; border-radius:999px; }
      .p-green{ background: var(--green); }
      .p-orange{ background: var(--orange); }
      .p-val{ width: 78px; text-align:right; font-size:12px; color: var(--text); font-weight:950; }

      /* ===== SECTIONS ===== */
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
      div[data-testid="stVerticalBlock"] > div { gap: .22rem; }
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

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def render_mini_progress(title: str, realizado_pct: float, proj_pct: float):
    # cap para não estourar
    r = clamp(realizado_pct, 0, 200)
    p = clamp(proj_pct, 0, 200)
    st.markdown(
        f"""
        <div class="mini">
          <h3>{title}</h3>

          <div class="p-row">
            <div class="p-lbl">Realizado</div>
            <div class="p-barwrap">
              <div class="p-bar p-green" style="width:{r/2:.1f}%"></div>
            </div>
            <div class="p-val">{r:.0f}%</div>
          </div>

          <div class="p-row">
            <div class="p-lbl">Projeção</div>
            <div class="p-barwrap">
              <div class="p-bar p-orange" style="width:{p/2:.1f}%"></div>
            </div>
            <div class="p-val">{p:.0f}%</div>
          </div>

          <div class="smallnote">
            Realizado = (Acumulado até agora / Meta proporcional até agora) •
            Projeção = (Proj. final / Meta do turno)
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def calc_progress(base_horas: pd.DataFrame, meta_h: int):
    """
    Retorna:
      acumulado, meta_acum, proj_final, meta_turno,
      realizado_pct (acum/meta_acum), proj_pct (proj/meta_turno)
    """
    hn = horas_ate_agora()
    acumulado = float(base_horas[base_horas["HORA"].isin(hn)]["QTD"].sum())
    meta_acum = float(meta_h * len(hn))

    total_horas = len(base_horas)
    meta_turno = float(meta_h * total_horas)

    ritmo = acumulado / max(1, len(hn))
    proj_final = ritmo * total_horas

    realizado_pct = (acumulado / meta_acum * 100.0) if meta_acum > 0 else 0.0
    proj_pct = (proj_final / meta_turno * 100.0) if meta_turno > 0 else 0.0

    return acumulado, meta_acum, proj_final, meta_turno, realizado_pct, proj_pct

def render_panel(title, base_horas: pd.DataFrame, meta_h: int):
    st.markdown(f"<div class='panel'><h2>{title}</h2>", unsafe_allow_html=True)

    # mini progresso (dentro do painel)
    _, _, _, _, r_pct, p_pct = calc_progress(base_horas, meta_h)
    render_mini_progress("Percentual (linha)", r_pct, p_pct)

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
# Cloud: lê do repo. Local: se não existir no repo, tenta copiar do caminho local.
if not ARQ_LIMPO.exists() and ARQ_LIMPO_LOCAL.exists():
    try:
        ARQ_LIMPO.write_bytes(ARQ_LIMPO_LOCAL.read_bytes())
    except Exception:
        pass

if not ARQ_LIMPO.exists():
    st.error("Não encontrei movimentos_estoque_dados.xlsx no repositório. Suba/atualize o arquivo no GitHub.")
    st.stop()

mtime = ARQ_LIMPO.stat().st_mtime
ultima_atualizacao = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")

@st.cache_data(show_spinner=False)
def load_noheader(path: str, mtime_cache: float) -> pd.DataFrame:
    return pd.read_excel(path, header=None)

# =========================
# TOP BAR (1 LINHA)
# =========================
left, mid, right = st.columns([7, 1.4, 2.6], vertical_alignment="center")

with left:
    c1, c2 = st.columns([1.2, 5.8], vertical_alignment="center")
    with c1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=110)
    with c2:
        st.markdown("<div class='brand-title'>Painel Performance Montagem</div>", unsafe_allow_html=True)

with mid:
    if st.button("🔄 Atualizar painel"):
        st.cache_data.clear()
        st.rerun()

with right:
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
# KPIs (TOTAL)
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
# PROGRESSO TOTAL (compacto)
# =========================
realizado_pct_total = (acum_total / meta_acum_total * 100.0) if meta_acum_total > 0 else 0.0
proj_pct_total = (proj_final_total / meta_turno_total * 100.0) if meta_turno_total > 0 else 0.0
render_mini_progress("Percentual (total)", realizado_pct_total, proj_pct_total)

# =========================
# PAINÉIS 60L e 22L
# =========================
colA, colB = st.columns(2)
with colA:
    render_panel("60L — FORNOS DE BANCADA", base_60, META_60L)
with colB:
    render_panel("22L — AIR FRYER (22L)", base_22, META_22L)
