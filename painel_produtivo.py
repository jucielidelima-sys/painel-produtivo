import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Painel Performance Montagem",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(".")  # repo / Streamlit Cloud
ARQ_LIMPO = BASE_DIR / "movimentos_estoque_dados.xlsx"
LOGO_PATH = BASE_DIR / "logo_empresa.png"

TZ_BR = ZoneInfo("America/Sao_Paulo")

# BASE DE CÁLCULO
H_INICIO, H_FIM = 7, 17
H_ALMOCO, H_ALMOCO_DEST = 12, 13
HORAS_TURNO = list(range(H_INICIO, H_FIM + 1))

META_EMBUTIR = 15
META_40L = 50

# colunas por letra do Excel
COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

# =========================
# CSS (RESPONSIVO: TV + CELULAR)
# =========================
st.markdown(
    """
    <style>
      /* fundo preto geral */
      html, body, #root, .stApp,
      [data-testid="stAppViewContainer"], section.main, main, .block-container{
        background:#000 !important; color:rgba(255,255,255,.92) !important;
      }

      /* remove header do streamlit (tarja) */
      header[data-testid="stHeader"] { display:none !important; height:0 !important; }
      [data-testid="stToolbar"] { display:none !important; height:0 !important; }
      [data-testid="stDecoration"] { display:none !important; height:0 !important; }

      /* container padrão */
      .main .block-container { padding-top: .4rem !important; padding-bottom: .6rem !important; max-width: 1520px; }

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

      /* TOP BAR */
      .brand-title{ font-size:30px; font-weight:950; margin:0; line-height:1.05; }
      .upd{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:12px;
        padding:6px 10px;
        min-width:250px;
      }
      .upd .lbl{ color:var(--muted); font-size:11px; font-weight:900; }
      .upd .val{ color:var(--orange); font-weight:950; font-size:13px; margin-top:2px; }

      /* KPI GRID (usar HTML) */
      .kpi-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:6px 0 8px;}
      .kpi{ background:var(--panel); border:1px solid var(--stroke); border-radius:14px; padding:8px 10px;}
      .kpi .t{ color:var(--muted); font-size:11px; font-weight:900;}
      .kpi .v{ font-size:26px; font-weight:950; margin-top:5px; line-height:1;}
      .kpi .u{ color:var(--orange); font-weight:950; font-size:11px; margin-top:3px;}

      /* PANELS */
      .panel{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:8px;
        margin-bottom: 10px;
      }

      .panel-title{
        display:flex; align-items:center; justify-content:space-between;
        gap:10px; margin:0 0 6px 0;
      }
      .panel-title h2{
        margin:0; color:var(--orange); font-size:13px; font-weight:950; letter-spacing:.4px;
      }
      .pchips{ display:flex; gap:6px; align-items:center; flex-wrap:wrap; }
      .pch{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.12);
        border-radius:999px;
        padding:4px 8px;
        font-size:11px;
        color:var(--muted);
        white-space:nowrap;
      }
      .pch b{ color:var(--text); }
      .pch .g{ color:var(--green); font-weight:950; }
      .pch .o{ color:var(--orange); font-weight:950; }

      .table-header{
        display:grid; grid-template-columns:64px 60px 60px 60px 1fr;
        gap:8px; padding:6px 6px;
        border-bottom:1px solid var(--stroke);
        color:var(--muted); font-weight:950; font-size:11px;
      }
      .row{
        display:grid; grid-template-columns:64px 60px 60px 60px 1fr;
        gap:8px; padding:6px 6px;
        border-bottom:1px solid rgba(255,255,255,.07);
        font-size:11px; align-items:center;
      }
      .pos{ color:var(--green); font-weight:950;}
      .neg{ color:var(--red); font-weight:950;}

      .barwrap{
        background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.10);
        height:9px; border-radius:999px; overflow:hidden;
      }
      .bar{ height:100%; border-radius:999px;}
      .bar.orange{ background:var(--orange); }
      .bar.green{ background:var(--green); }

      .smallnote{ color:var(--muted); font-size:10px; margin-top:2px;}

      /* FOOTER CHIPS */
      .foot{ margin-top:6px; display:flex; gap:6px; flex-wrap:wrap;}
      .chip{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.10);
        border-radius:999px;
        padding:5px 8px;
        font-size:11px;
        color:var(--muted);
      }
      .chip b{ color:var(--text); }
      .chip .o{ color:var(--orange); font-weight:950;}
      .chip .g{ color:var(--green); font-weight:950;}
      .chip .r{ color:var(--red); font-weight:950;}

      .stButton>button{ border-radius:10px; font-weight:950; padding:.30rem .7rem; }
      div[data-testid="stVerticalBlock"] > div { gap: .18rem; }

      /* ====== MODO TV (sem rolagem) ======
         ATENÇÃO: aplicamos via classe no body usando um "hack" de CSS (default: ligado)
      */
      body.tv-mode, body.tv-mode html {
        overflow:hidden !important;
      }
      body.tv-mode [data-testid="stAppViewContainer"],
      body.tv-mode section.main,
      body.tv-mode .block-container{
        height:100vh !important;
        overflow:hidden !important;
      }

      /* =========================
         MOBILE AJUSTES
         ========================= */
      @media (max-width: 768px) {
        /* no celular precisa rolar */
        html, body { height:auto !important; overflow:auto !important; }
        [data-testid="stAppViewContainer"], section.main, .block-container{
          height:auto !important; overflow:visible !important;
        }

        .main .block-container{
          padding-left: .75rem !important;
          padding-right: .75rem !important;
          max-width: 100% !important;
        }

        .brand-title{ font-size:20px; }
        .upd{ min-width: unset; width: 100%; }

        /* KPIs: 4 -> 2 colunas */
        .kpi-grid{ grid-template-columns:repeat(2,1fr); gap:8px; }
        .kpi .v{ font-size:20px; }

        /* tabela compacta */
        .table-header{ grid-template-columns:56px 44px 44px 50px 1fr; font-size:10px; }
        .row{ grid-template-columns:56px 44px 44px 50px 1fr; font-size:10px; }

        .smallnote{ font-size:9px; }
        .chip{ font-size:10px; padding:4px 7px; }

        /* desliga modo TV no celular */
        body.tv-mode [data-testid="stAppViewContainer"],
        body.tv-mode section.main,
        body.tv-mode .block-container{
          height:auto !important;
          overflow:visible !important;
        }
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
    if "EMBUTIR" in d:
        return META_EMBUTIR
    if "40L" in d:
        return META_40L
    return 0

def horas_ate_agora():
    agora = datetime.now(TZ_BR).hour
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

def calc_line_kpis(base_horas: pd.DataFrame, meta_h: int):
    hn = horas_ate_agora()
    acumulado = float(base_horas[base_horas["HORA"].isin(hn)]["QTD"].sum())
    meta_acum = float(meta_h * len(hn))
    realizado_pct = (acumulado / meta_acum * 100.0) if meta_acum > 0 else 0.0

    ritmo = acumulado / max(1, len(hn))
    proj_final = ritmo * len(base_horas)
    meta_turno = float(meta_h * len(base_horas))
    proj_pct = (proj_final / meta_turno * 100.0) if meta_turno > 0 else 0.0

    return clamp(realizado_pct, 0, 999), clamp(proj_pct, 0, 999)

def render_panel(title, base_horas: pd.DataFrame, meta_h: int):
    realizado_pct, proj_pct = calc_line_kpis(base_horas, meta_h)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='panel-title'>
          <h2>{title}</h2>
          <div class='pchips'>
            <div class='pch'>Realizado: <b class='g'>{realizado_pct:.0f}%</b></div>
            <div class='pch'>Projeção: <b class='o'>{proj_pct:.0f}%</b></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
              <div>{h:02d}:00</div><div><b>{int(qtd)}</b></div><div>{int(meta)}</div>
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
          <div class='chip'>Acum.: <b class='o'>{int(acumulado)}</b></div>
          <div class='chip'>Δ acum.: <b>{fmt_delta_html(delta_acum)}</b></div>
          <div class='chip'>Proj.: <b>{int(round(proj_final,0))}</b></div>
          <div class='chip'>Δ proj.: <b>{fmt_delta_html(delta_proj)}</b></div>
          <div class='chip'>Total: <b class='o'>{int(total)}</b></div>
          <div class='chip'>Meta: <b>{int(meta_turno)}</b></div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# LOAD DATA
# =========================
if not ARQ_LIMPO.exists():
    st.error("Não encontrei movimentos_estoque_dados.xlsx no repositório.")
    st.stop()

mtime = ARQ_LIMPO.stat().st_mtime
ultima_atualizacao = datetime.fromtimestamp(mtime, tz=TZ_BR).strftime("%d/%m/%Y %H:%M:%S")

@st.cache_data(ttl=60, show_spinner=False)
def load_noheader(path: str, mtime_cache: float) -> pd.DataFrame:
    return pd.read_excel(path, header=None)

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

df = df[df["META_H"].isin([META_EMBUTIR, META_40L])].copy()
df.loc[df["HORA"] == H_ALMOCO, "HORA"] = H_ALMOCO_DEST
df = df[df["HORA"].between(H_INICIO, H_FIM)].copy()

df_EMBUTIR = df[df["META_H"] == META_EMBUTIR].copy()
df_40 = df[df["META_H"] == META_40L].copy()

base_EMBUTIR = build_hour_table(df_EMBUTIR)
base_40 = build_hour_table(df_40)

# =========================
# CONTROLES (modo)
# =========================
c_mode1, c_mode2 = st.columns([1, 2], vertical_alignment="center")
with c_mode1:
    modo_mobile = st.toggle("Modo celular (1 coluna)", value=True)
with c_mode2:
    modo_tv = st.toggle("Modo TV (sem rolagem)", value=False)

# aplica "classe" tv-mode (hack CSS via markdown)
# (quando modo_tv=True, tentamos travar rolagem em telas grandes; no mobile o @media já libera)
if modo_tv:
    st.markdown("<script>document.body.classList.add('tv-mode');</script>", unsafe_allow_html=True)
else:
    st.markdown("<script>document.body.classList.remove('tv-mode');</script>", unsafe_allow_html=True)

# =========================
# TOPO (logo + título + botão + hora) RESPONSIVO
# =========================
top1, top2 = st.columns([1.2, 1], vertical_alignment="center")

with top1:
    c1, c2 = st.columns([1.2, 5.8], vertical_alignment="center")
    with c1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=70)
    with c2:
        st.markdown("<div class='brand-title'>Painel Performance Montagem</div>", unsafe_allow_html=True)

with top2:
    a, b = st.columns([1, 1], vertical_alignment="center")
    with a:
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()
    with b:
        st.markdown(
            f"<div class='upd'><div class='lbl'>Última atualização</div><div class='val'>{ultima_atualizacao}</div></div>",
            unsafe_allow_html=True,
        )

# =========================
# KPIs (TOTAL) - HTML GRID RESPONSIVO
# =========================
total_dia = float(base_EMBUTIR["QTD"].sum() + base_40["QTD"].sum())
horas_exibidas = len([h for h in HORAS_TURNO if h != H_ALMOCO])
meta_turno_total = float((META_EMBUTIR + META_40L) * horas_exibidas)

hn = horas_ate_agora()
acum_total = float(
    base_EMBUTIR[base_EMBUTIR["HORA"].isin(hn)]["QTD"].sum()
    + base_40[base_40["HORA"].isin(hn)]["QTD"].sum()
)
meta_acum_total = float((META_EMBUTIR + META_40L) * len(hn))
delta_acum_total = acum_total - meta_acum_total

ritmo = acum_total / max(1, len(hn))
proj_final_total = ritmo * horas_exibidas
delta_proj_total = proj_final_total - meta_turno_total

st.markdown(
    f"""
    <div class="kpi-grid">
      <div class='kpi'><div class='t'>TOTAL DO DIA</div><div class='v'>{int(total_dia)}</div><div class='u'>Unidades</div></div>

      <div class='kpi'><div class='t'>DELTA ACUMULADO</div>
        <div class='v' style='color:{"var(--green)" if delta_acum_total >= 0 else "var(--red)"};'>
          {int(delta_acum_total):+d}
        </div>
        <div class='u'>Meta até agora</div>
      </div>

      <div class='kpi'><div class='t'>PROJEÇÃO FINAL</div><div class='v'>{int(round(proj_final_total,0))}</div><div class='u'>Ritmo x H</div></div>

      <div class='kpi'><div class='t'>DELTA PROJEÇÃO</div>
        <div class='v' style='color:{"var(--green)" if delta_proj_total >= 0 else "var(--red)"};'>
          {int(round(delta_proj_total,0)):+d}
        </div>
        <div class='u'>Proj - Meta</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# PAINÉIS (RESPONSIVO)
# =========================
if modo_mobile:
    render_panel("40L — FORNOS DE BANCADA", base_40, META_40L)
    render_panel("EMBUTIR — EMBUTIR (EMBUTIR)", base_EMBUTIR, META_EMBUTIR)
else:
    colA, colB = st.columns(2)
    with colA:
        render_panel("40L — FORNOS DE BANCADA", base_40, META_40L)
    with colB:
        render_panel("EMBUTIR — EMBUTIR (EMBUTIR)", base_EMBUTIR, META_EMBUTIR)




