import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Painel Performance Montagem",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <meta http-equiv="refresh" content="30">
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(".")
ARQ_LIMPO = BASE_DIR / "movimentos_estoque_dados.xlsx"
LOGO_PATH = BASE_DIR / "logo_empresa.png"

TZ_BR = ZoneInfo("America/Sao_Paulo")

H_INICIO, H_FIM = 7, 17
H_ALMOCO, H_ALMOCO_DEST = 12, 13

# Metas do turno por família
# Distribuição proporcional aos minutos trabalhados por faixa horária.
META_TURNO_EMBUTIR = 50
META_TURNO_BANCADA = 800

# Minutos produtivos por hora:
# 09:00 tem intervalo de café, então considera 50 min.
# 17:00 trabalha somente até 17:15, então considera 15 min.
MINUTOS_POR_HORA = {
    7: 60,
    8: 60,
    9: 50,
    10: 60,
    11: 60,
    13: 60,
    14: 60,
    15: 60,
    16: 60,
    17: 15,
}

HORAS_TURNO = list(MINUTOS_POR_HORA.keys())

FAMILIA_EMBUTIR = "EMBUTIR"
FAMILIA_BANCADA = "BANCADA"

COL_HORA = "X"
COL_QTD = "N"
COL_DESC = "O"

st.markdown(
    """
    <style>
      html, body, #root, .stApp,
      [data-testid="stAppViewContainer"], section.main, main, .block-container{
        background:#000 !important;
        color:rgba(255,255,255,.92) !important;
      }

      header[data-testid="stHeader"],
      [data-testid="stToolbar"],
      [data-testid="stDecoration"]{
        display:none !important;
        height:0 !important;
      }

      iframe {
        display:none !important;
        height:0px !important;
        min-height:0px !important;
      }

      .main .block-container,
      .block-container {
        padding-top:0rem !important;
        margin-top:-4.5rem !important;
        padding-bottom:.15rem !important;
        padding-left:.45rem !important;
        padding-right:.45rem !important;
        max-width:100% !important;
      }

      :root{
        --panel:rgba(255,255,255,.05);
        --panel2:rgba(255,255,255,.03);
        --stroke:rgba(255,255,255,.10);
        --text:rgba(255,255,255,.92);
        --muted:rgba(255,255,255,.65);
        --orange:#ff7a18;
        --green:#17c964;
        --red:#ff3b30;
      }

      .brand-title{
        font-size:28px;
        font-weight:950;
        margin:0;
        line-height:1;
      }

      .upd{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:12px;
        padding:5px 9px;
        min-width:230px;
      }

      .upd .lbl{
        color:var(--muted);
        font-size:10px;
        font-weight:900;
      }

      .upd .val{
        color:var(--orange);
        font-weight:950;
        font-size:12px;
        margin-top:1px;
      }

      .kpi-grid{
        display:grid;
        grid-template-columns:repeat(4,1fr);
        gap:8px;
        margin:3px 0 5px;
      }

      .kpi{
        background:var(--panel);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:6px 8px;
      }

      .kpi .t{
        color:var(--muted);
        font-size:10px;
        font-weight:900;
      }

      .kpi .v{
        font-size:22px;
        font-weight:950;
        margin-top:3px;
        line-height:1;
      }

      .kpi .u{
        color:var(--orange);
        font-weight:950;
        font-size:10px;
        margin-top:2px;
      }

      .panel{
        background:var(--panel2);
        border:1px solid var(--stroke);
        border-radius:14px;
        padding:5px;
        margin-bottom:4px;
      }

      .panel-title{
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:8px;
        margin:0 0 4px 0;
      }

      .panel-title h2{
        margin:0;
        color:var(--orange);
        font-size:12px;
        font-weight:950;
        letter-spacing:.3px;
      }

      .pchips{
        display:flex;
        gap:4px;
        align-items:center;
        flex-wrap:wrap;
      }

      .pch{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.12);
        border-radius:999px;
        padding:3px 6px;
        font-size:10px;
        color:var(--muted);
        white-space:nowrap;
      }

      .pch b{ color:var(--text); }
      .pch .g{ color:var(--green); font-weight:950; }
      .pch .o{ color:var(--orange); font-weight:950; }

      .table-header{
        display:grid;
        grid-template-columns:64px 55px 55px 55px 1fr;
        gap:6px;
        padding:4px 5px;
        border-bottom:1px solid var(--stroke);
        color:var(--muted);
        font-weight:950;
        font-size:10px;
      }

      .row{
        display:grid;
        grid-template-columns:64px 55px 55px 55px 1fr;
        gap:6px;
        padding:3px 5px;
        border-bottom:1px solid rgba(255,255,255,.07);
        font-size:10px;
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
        background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.10);
        height:7px;
        border-radius:999px;
        overflow:hidden;
      }

      .bar{
        height:100%;
        border-radius:999px;
      }

      .bar.green{
        background:var(--green);
      }

      .bar.red{
        background:var(--red);
      }

      .smallnote{
        color:var(--muted);
        font-size:9px;
        margin-top:1px;
      }

      .foot{
        margin-top:3px;
        display:flex;
        gap:4px;
        flex-wrap:wrap;
      }

      .chip{
        background:rgba(255,255,255,.05);
        border:1px solid rgba(255,255,255,.10);
        border-radius:999px;
        padding:3px 6px;
        font-size:10px;
        color:var(--muted);
      }

      .chip b{ color:var(--text); }
      .chip .o{ color:var(--orange); font-weight:950; }
      .chip .g{ color:var(--green); font-weight:950; }
      .chip .r{ color:var(--red); font-weight:950; }

      .stButton>button{
        border-radius:10px;
        font-weight:950;
        padding:.22rem .55rem;
        font-size:11px;
      }

      div[data-testid="stVerticalBlock"] > div {
        gap:.10rem;
      }

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

      @media (max-width:768px) {
        html, body {
          height:auto !important;
          overflow:auto !important;
        }

        [data-testid="stAppViewContainer"],
        section.main,
        .block-container{
          height:auto !important;
          overflow:visible !important;
        }

        .main .block-container,
        .block-container{
          padding-top:.5rem !important;
          margin-top:0rem !important;
          padding-left:.75rem !important;
          padding-right:.75rem !important;
          max-width:100% !important;
        }

        .brand-title{
          font-size:20px;
        }

        .upd{
          min-width:unset;
          width:100%;
        }

        .kpi-grid{
          grid-template-columns:repeat(2,1fr);
          gap:8px;
        }

        .kpi .v{
          font-size:20px;
        }

        .table-header{
          grid-template-columns:56px 44px 44px 50px 1fr;
          font-size:10px;
        }

        .row{
          grid-template-columns:56px 44px 44px 50px 1fr;
          font-size:10px;
        }

        .smallnote{
          font-size:9px;
        }

        .chip{
          font-size:10px;
          padding:4px 7px;
        }

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


def familia_from_desc(desc: str) -> str | None:
    d = str(desc).upper()

    if "EMBUTIR" in d or "E50" in d:
        return FAMILIA_EMBUTIR

    if "TOP 50L" in d or "TOP50L" in d or "TOP 50" in d or "60L" in d:
        return FAMILIA_BANCADA

    return None


def metas_por_hora(meta_turno: int) -> dict[int, int]:
    """Distribui a meta do turno proporcionalmente aos minutos de cada hora.

    Usa arredondamento por maior sobra para garantir que a soma das metas
    horárias seja exatamente igual à meta do turno.
    """
    total_minutos = sum(MINUTOS_POR_HORA.values())

    bruto = {
        h: (meta_turno * minutos / total_minutos)
        for h, minutos in MINUTOS_POR_HORA.items()
    }

    metas = {h: int(v) for h, v in bruto.items()}
    falta = int(meta_turno - sum(metas.values()))

    ordem = sorted(
        bruto,
        key=lambda h: bruto[h] - metas[h],
        reverse=True,
    )

    for h in ordem[:falta]:
        metas[h] += 1

    return metas


META_HORA_EMBUTIR = metas_por_hora(META_TURNO_EMBUTIR)
META_HORA_BANCADA = metas_por_hora(META_TURNO_BANCADA)

def minutos_decorridos_por_hora() -> dict[int, int]:
    """Retorna quantos minutos produtivos já devem contar em cada faixa horária.

    A hora atual entra proporcional ao minuto atual.
    Exemplo: às 10:22 conta 22 minutos da faixa 10:00, não a hora cheia.
    """
    agora = datetime.now(TZ_BR)
    hora_atual = agora.hour
    minuto_atual = agora.minute

    minutos = {}

    for h, minutos_programados in MINUTOS_POR_HORA.items():
        if h < hora_atual:
            minutos[h] = minutos_programados
        elif h == hora_atual:
            minutos[h] = clamp(minuto_atual, 0, minutos_programados)
        else:
            minutos[h] = 0

    return minutos


def horas_ate_agora():
    minutos = minutos_decorridos_por_hora()
    horas = [h for h, m in minutos.items() if m > 0]
    return horas if horas else [H_INICIO]


def meta_acumulada_proporcional(meta_hora: dict[int, int]) -> float:
    minutos = minutos_decorridos_por_hora()
    meta = 0.0

    for h, minutos_realizados in minutos.items():
        minutos_programados = MINUTOS_POR_HORA.get(h, 0)
        if minutos_programados <= 0:
            continue

        meta += meta_hora.get(h, 0) * (minutos_realizados / minutos_programados)

    return meta


def minutos_acumulados_atuais() -> int:
    return int(sum(minutos_decorridos_por_hora().values()))

def build_hour_table(df_line: pd.DataFrame, meta_hora: dict[int, int]):
    agg = df_line.groupby("HORA", as_index=False)["QTD"].sum()

    base = pd.DataFrame({
        "HORA": HORAS_TURNO,
    })

    base = base.merge(agg, on="HORA", how="left").fillna({"QTD": 0})
    base["HORA"] = base["HORA"].astype(int)
    base["QTD"] = base["QTD"].astype(float)
    base["META"] = base["HORA"].map(meta_hora).astype(float)

    return base.sort_values("HORA")

def fmt_delta_html(x: float) -> str:
    if x >= 0:
        return f"<span class='g'>{x:+.0f}</span>"

    return f"<span class='r'>{x:+.0f}</span>"


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def calc_line_kpis(base_horas: pd.DataFrame):
    hn = horas_ate_agora()
    base_acum = base_horas[base_horas["HORA"].isin(hn)]

    acumulado = float(base_acum["QTD"].sum())

    meta_hora = dict(zip(base_horas["HORA"].astype(int), base_horas["META"].astype(float)))
    meta_acum = meta_acumulada_proporcional(meta_hora)

    realizado_pct = (
        acumulado / meta_acum * 100.0
        if meta_acum > 0 else 0.0
    )

    minutos_acum = minutos_acumulados_atuais()
    total_minutos = sum(MINUTOS_POR_HORA.values())

    ritmo_por_minuto = acumulado / max(1, minutos_acum)
    proj_final = ritmo_por_minuto * total_minutos

    meta_turno = float(base_horas["META"].sum())

    proj_pct = (
        proj_final / meta_turno * 100.0
        if meta_turno > 0 else 0.0
    )

    return clamp(realizado_pct, 0, 999), clamp(proj_pct, 0, 999)

def render_panel(title, base_horas: pd.DataFrame):
    realizado_pct, proj_pct = calc_line_kpis(base_horas)

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
        meta = float(r["META"])
        delta = qtd - meta
        perc = (qtd / meta) if meta else 0

        w = max(0, min(perc, 1.0)) * 100
        bar_class = "green" if delta >= 0 else "red"
        delta_class = "pos" if delta >= 0 else "neg"

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
              <div class='{delta_class}'>{delta:+.0f}</div>
              <div>
                <div class='barwrap'>
                  <div class='bar {bar_class}' style='width:{w:.1f}%'></div>
                </div>
                <div class='smallnote'>{termo_txt}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    total = float(base_horas["QTD"].sum())
    meta_turno = float(base_horas["META"].sum())

    hn = horas_ate_agora()

    acumulado = float(
        base_horas[base_horas["HORA"].isin(hn)]["QTD"].sum()
    )

    meta_hora = dict(zip(base_horas["HORA"].astype(int), base_horas["META"].astype(float)))
    meta_acum = meta_acumulada_proporcional(meta_hora)
    delta_acum = acumulado - meta_acum

    minutos_acum = minutos_acumulados_atuais()
    total_minutos = sum(MINUTOS_POR_HORA.values())
    ritmo = acumulado / max(1, minutos_acum)
    proj_final = ritmo * total_minutos
    delta_proj = proj_final - meta_turno

    st.markdown(
        f"""
        <div class='foot'>
          <div class='chip'>Acum.: <b class='o'>{int(acumulado)}</b></div>
          <div class='chip'>Δ acum.: <b>{fmt_delta_html(delta_acum)}</b></div>
          <div class='chip'>Proj.: <b>{int(round(proj_final, 0))}</b></div>
          <div class='chip'>Δ proj.: <b>{fmt_delta_html(delta_proj)}</b></div>
          <div class='chip'>Total: <b class='o'>{int(total)}</b></div>
          <div class='chip'>Meta: <b>{int(meta_turno)}</b></div>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if not ARQ_LIMPO.exists():
    st.error("Não encontrei movimentos_estoque_dados.xlsx no repositório.")
    st.stop()

mtime = ARQ_LIMPO.stat().st_mtime

ultima_atualizacao = datetime.fromtimestamp(
    mtime,
    tz=TZ_BR
).strftime("%d/%m/%Y %H:%M:%S")


def load_noheader(path: str) -> pd.DataFrame:
    return pd.read_excel(path, header=None)


df0 = load_noheader(str(ARQ_LIMPO))

s_hora = get_series_by_letter(df0, COL_HORA)
s_qtd = get_series_by_letter(df0, COL_QTD)
s_desc = get_series_by_letter(df0, COL_DESC)

if s_hora is None or s_qtd is None or s_desc is None:
    st.error("Não consegui localizar as colunas por letra N, O e X no arquivo.")
    st.stop()

df = pd.DataFrame({
    "HORA_RAW": s_hora,
    "QTD_RAW": s_qtd,
    "DESC": s_desc
}).dropna(how="all")

df["HORA"] = df["HORA_RAW"].apply(parse_hour)

df["QTD"] = pd.to_numeric(
    df["QTD_RAW"],
    errors="coerce"
).fillna(0)

df["FAMILIA"] = df["DESC"].apply(familia_from_desc)

df = df[df["FAMILIA"].isin([FAMILIA_EMBUTIR, FAMILIA_BANCADA])].copy()

df.loc[df["HORA"] == H_ALMOCO, "HORA"] = H_ALMOCO_DEST

df = df[df["HORA"].isin(HORAS_TURNO)].copy()

df_EMBUTIR = df[df["FAMILIA"] == FAMILIA_EMBUTIR].copy()
df_60L = df[df["FAMILIA"] == FAMILIA_BANCADA].copy()

base_EMBUTIR = build_hour_table(df_EMBUTIR, META_HORA_EMBUTIR)
base_60L = build_hour_table(df_60L, META_HORA_BANCADA)

c_mode1, c_mode2 = st.columns([1, 2], vertical_alignment="center")

with c_mode1:
    modo_mobile = st.toggle("Modo celular (1 coluna)", value=False)

with c_mode2:
    modo_tv = st.toggle("Modo TV (sem rolagem)", value=True)

if modo_tv:
    st.markdown(
        "<script>document.body.classList.add('tv-mode');</script>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<script>document.body.classList.remove('tv-mode');</script>",
        unsafe_allow_html=True,
    )

top1, top2 = st.columns([1.2, 1], vertical_alignment="center")

with top1:
    c1, c2 = st.columns([1.2, 5.8], vertical_alignment="center")

    with c1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=65)

    with c2:
        st.markdown(
            "<div class='brand-title'>Painel Performance Montagem</div>",
            unsafe_allow_html=True,
        )

with top2:
    a, b = st.columns([1, 1], vertical_alignment="center")

    with a:
        if st.button("🔄 Atualizar"):
            st.cache_data.clear()
            st.rerun()

    with b:
        st.markdown(
            f"""
            <div class='upd'>
              <div class='lbl'>Última atualização</div>
              <div class='val'>{ultima_atualizacao}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

total_dia = float(
    base_EMBUTIR["QTD"].sum()
    + base_60L["QTD"].sum()
)

horas_exibidas = len(HORAS_TURNO)

meta_turno_total = float(
    base_EMBUTIR["META"].sum() + base_60L["META"].sum()
)

hn = horas_ate_agora()

acum_total = float(
    base_EMBUTIR[base_EMBUTIR["HORA"].isin(hn)]["QTD"].sum()
    + base_60L[base_60L["HORA"].isin(hn)]["QTD"].sum()
)

meta_acum_total = float(
    meta_acumulada_proporcional(dict(zip(base_EMBUTIR["HORA"].astype(int), base_EMBUTIR["META"].astype(float))))
    + meta_acumulada_proporcional(dict(zip(base_60L["HORA"].astype(int), base_60L["META"].astype(float))))
)

delta_acum_total = acum_total - meta_acum_total

minutos_acum_total = minutos_acumulados_atuais()
total_minutos_turno = sum(MINUTOS_POR_HORA.values())
ritmo = acum_total / max(1, minutos_acum_total)

proj_final_total = ritmo * total_minutos_turno

delta_proj_total = proj_final_total - meta_turno_total

st.markdown(
    f"""
    <div class="kpi-grid">
      <div class='kpi'>
        <div class='t'>TOTAL DO DIA</div>
        <div class='v'>{int(total_dia)}</div>
        <div class='u'>Unidades</div>
      </div>

      <div class='kpi'>
        <div class='t'>DELTA ACUMULADO</div>
        <div class='v' style='color:{"var(--green)" if delta_acum_total >= 0 else "var(--red)"};'>
          {int(delta_acum_total):+d}
        </div>
        <div class='u'>Meta até agora</div>
      </div>

      <div class='kpi'>
        <div class='t'>PROJEÇÃO FINAL</div>
        <div class='v'>{int(round(proj_final_total, 0))}</div>
        <div class='u'>Ritmo x H</div>
      </div>

      <div class='kpi'>
        <div class='t'>DELTA PROJEÇÃO</div>
        <div class='v' style='color:{"var(--green)" if delta_proj_total >= 0 else "var(--red)"};'>
          {int(round(delta_proj_total, 0)):+d}
        </div>
        <div class='u'>Proj - Meta</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if modo_mobile:
    render_panel(
        "60L + TOP 50L — FORNOS DE BANCADA — META 800",
        base_60L
    )

    render_panel(
        "EMBUTIR + E50 — META 50",
        base_EMBUTIR
    )

else:
    colA, colB = st.columns(2)

    with colA:
        render_panel(
            "60L + TOP 50L — FORNOS DE BANCADA — META 800",
            base_60L
        )

    with colB:
        render_panel(
            "EMBUTIR + E50 — META 50",
            base_EMBUTIR
        )
