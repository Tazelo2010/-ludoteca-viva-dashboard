import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

SPREADSHEET_ID = "19onyfrqnhTH4UeuMvDxgOnlemNa-SHdkz_wVlyEXyac"
SHEET_GID = "1910202614"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"

st.set_page_config(
    page_title="Ludoteca viva – Tazelo2010",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root {
    --bg: #f7f5ef;
    --card: #fffdf8;
    --green: #073f2f;
    --green2: #0b5a42;
    --softgreen: #eaf3e7;
    --gold: #f3b51b;
    --orange: #f27b2a;
    --red: #ef4b3f;
    --blue: #1e73be;
    --purple: #9b62d9;
    --text: #12342a;
    --muted: #6b756f;
    --border: #e5ddcc;
}
.stApp {
    background: var(--bg);
    color: var(--text);
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #073f2f 0%, #0b5a42 100%);
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] input {
    color: #12342a !important;
}
.main-title {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 8px 0 2px 0;
}
.dice {
    font-size: 44px;
    line-height: 1;
}
.title-text {
    font-size: 34px;
    font-weight: 900;
    color: var(--green);
    letter-spacing: -0.5px;
    margin-bottom: -4px;
}
.subtitle {
    color: var(--green2);
    font-size: 17px;
    font-style: italic;
    margin-top: 0px;
}
.updated {
    text-align: right;
    color: var(--green);
    font-weight: 700;
    font-size: 13px;
}
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px 18px;
    min-height: 120px;
    box-shadow: 0 4px 14px rgba(25, 44, 35, 0.08);
    display: flex;
    align-items: center;
    gap: 15px;
}
.metric-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: var(--softgreen);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    flex: 0 0 auto;
}
.metric-label {
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--green2);
}
.metric-value {
    font-size: 34px;
    font-weight: 900;
    color: var(--green);
    line-height: 1.05;
}
.metric-note {
    font-size: 12px;
    color: var(--muted);
    margin-top: 3px;
}
.panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 4px 14px rgba(25, 44, 35, 0.08);
    overflow: hidden;
    margin-bottom: 16px;
}
.panel-header {
    background: linear-gradient(90deg, var(--green) 0%, var(--green2) 100%);
    color: #fff;
    padding: 10px 14px;
    font-weight: 900;
    font-size: 16px;
}
.recommend-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 14px rgba(25, 44, 35, 0.08);
    text-align: center;
}
.recommend-title {
    font-size: 14px;
    font-weight: 900;
    color: var(--green2);
    margin-bottom: 10px;
}
.recommend-game {
    font-size: 26px;
    font-weight: 900;
    color: var(--green);
    margin: 16px 0 6px 0;
}
.pill {
    display: inline-block;
    background: #eaf3e7;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 12px;
    color: var(--green);
    font-weight: 700;
    margin: 3px;
}
.tip {
    background: #fff7df;
    border: 1px solid #f0dfad;
    border-radius: 14px;
    padding: 14px 18px;
    color: #143d2e;
    font-weight: 650;
    margin-top: 12px;
}
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [c.strip() for c in df.columns]

    for col in ["Nombre", "Tipo", "Jugadores", "Fricción para mesa", "Motivo de fricción"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    if "Partidas" in df.columns:
        df["Partidas_num"] = pd.to_numeric(df["Partidas"], errors="coerce").fillna(0).astype(int)
    else:
        df["Partidas_num"] = 0

    if "Peso BGG" in df.columns:
        df["Peso_num"] = pd.to_numeric(
            df["Peso BGG"].astype(str).str.replace(",", ".", regex=False),
            errors="coerce",
        )
    else:
        df["Peso_num"] = None

    if "Última partida" in df.columns:
        df["Ultima_dt"] = pd.to_datetime(df["Última partida"], errors="coerce")
    else:
        df["Ultima_dt"] = pd.NaT

    return df


def parse_players(text):
    nums = [int(x) for x in re.findall(r"\d+", str(text))]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    return nums[0], nums[-1]


def player_match(jugadores, selected):
    if selected == "Todos":
        return True
    mn, mx = parse_players(jugadores)
    if mn is None:
        return False
    n = int(selected)
    return mn <= n <= mx


def contains_type(tipo, selected):
    if selected == "Todos":
        return True
    return selected.lower() in str(tipo).lower()


def friction_rank(value):
    order = {"Baja": 1, "Media": 2, "Alta": 3, "Muy alta": 4}
    return order.get(str(value), 9)


def metric_card(icon, label, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel(title):
    st.markdown(f'<div class="panel"><div class="panel-header">{title}</div></div>', unsafe_allow_html=True)


def show_table(df, cols, height=250):
    show = df[[c for c in cols if c in df.columns]].copy()
    st.dataframe(show, use_container_width=True, hide_index=True, height=height)


df = load_data()

st.sidebar.markdown("## 🎛️ Filtros rápidos")
tipo_opt = st.sidebar.selectbox("Tipo", ["Todos", "Competitivo", "Cooperativo", "Campaña", "Party"])
jug_opt = st.sidebar.selectbox("Jugadores", ["Todos", "1", "2", "3", "4", "5", "6"])
fric_opt = st.sidebar.selectbox("Fricción", ["Todos", "Baja", "Media", "Alta", "Muy alta"])
estreno_opt = st.sidebar.selectbox("Estreno", ["Todos", "Sin estrenar", "Ya jugados"])
st.sidebar.markdown("---")
energia_opt = st.sidebar.radio("Energía de hoy", ["Baja fricción", "Rotar olvidados", "Estrenar algo", "Algo épico"], index=0)
st.sidebar.caption("La app se actualiza leyendo la Google Sheet.")

f = df.copy()
if "Tipo" in f.columns:
    f = f[f["Tipo"].apply(lambda x: contains_type(x, tipo_opt))]
if "Jugadores" in f.columns:
    f = f[f["Jugadores"].apply(lambda x: player_match(x, jug_opt))]
if fric_opt != "Todos" and "Fricción para mesa" in f.columns:
    f = f[f["Fricción para mesa"] == fric_opt]
if estreno_opt == "Sin estrenar":
    f = f[f["Partidas_num"] == 0]
elif estreno_opt == "Ya jugados":
    f = f[f["Partidas_num"] > 0]

col_title, col_update = st.columns([4, 1])
with col_title:
    st.markdown(
        """
        <div class="main-title">
            <div class="dice">🎲</div>
            <div>
                <div class="title-text">LUDOTECA VIVA – TAZELO2010</div>
                <div class="subtitle">Dashboard de tu colección</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_update:
    st.markdown(
        f"<div class='updated'>Actualizado:<br>{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>",
        unsafe_allow_html=True,
    )

total = len(df)
competitivos = df["Tipo"].str.contains("Competitivo", case=False, na=False).sum()
cooperativos = df["Tipo"].str.contains("Cooperativo", case=False, na=False).sum()
campanias = df["Tipo"].str.contains("Campaña", case=False, na=False).sum()
party = df["Tipo"].str.contains("Party", case=False, na=False).sum()
sin_estrenar_count = (df["Partidas_num"] == 0).sum()
alta_fric = df["Fricción para mesa"].isin(["Alta", "Muy alta"]).sum()
baja_fric = (df["Fricción para mesa"] == "Baja").sum()
old = df[df["Ultima_dt"].notna() & (df["Ultima_dt"] < (pd.Timestamp.today() - pd.DateOffset(months=6)))]

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    metric_card("▦", "Total juegos", total, "En tu colección")
with m2:
    metric_card("⚔️", "Competitivos", competitivos, f"{competitivos/total:.1%} del total" if total else "")
with m3:
    metric_card("🤝", "Cooperativos", cooperativos, f"{cooperativos/total:.1%} del total" if total else "")
with m4:
    metric_card("🚩", "Campañas", campanias, f"{campanias/total:.1%} del total" if total else "")
with m5:
    metric_card("🎉", "Party", party, f"{party/total:.1%} del total" if total else "")

m6, m7, m8, m9, m10 = st.columns(5)
with m6:
    metric_card("📅", "Sin estrenar", sin_estrenar_count, f"{sin_estrenar_count/total:.1%} del total" if total else "")
with m7:
    metric_card("↻", "Hace +6 meses", len(old), "Sin jugar")
with m8:
    metric_card("🔥", "Alta fricción", alta_fric, f"{alta_fric/total:.1%} del total" if total else "")
with m9:
    metric_card("⚡", "Baja fricción", baja_fric, f"{baja_fric/total:.1%} del total" if total else "")
with m10:
    metric_card("⭐", "Favoritos", 0, "Pendiente de valorar")

left, main = st.columns([1.05, 4.25])

with left:
    st.markdown('<div class="recommend-card">', unsafe_allow_html=True)
    st.markdown('<div class="recommend-title">✨ ¿QUÉ JUEGO SACO HOY?</div>', unsafe_allow_html=True)

    rec_pool = f.copy()
    if energia_opt == "Baja fricción":
        rec_pool = rec_pool[rec_pool["Fricción para mesa"].isin(["Baja", "Media"])]
        rec_pool["fr_rank"] = rec_pool["Fricción para mesa"].apply(friction_rank)
        rec_pool = rec_pool.sort_values(["fr_rank", "Ultima_dt"], na_position="first")
    elif energia_opt == "Rotar olvidados":
        rec_pool = rec_pool.sort_values(["Ultima_dt", "Partidas_num"], na_position="first")
    elif energia_opt == "Estrenar algo":
        rec_pool = rec_pool[rec_pool["Partidas_num"] == 0]
        rec_pool["fr_rank"] = rec_pool["Fricción para mesa"].apply(friction_rank)
        rec_pool = rec_pool.sort_values(["fr_rank", "Nombre"])
    elif energia_opt == "Algo épico":
        rec_pool = rec_pool[rec_pool["Fricción para mesa"].isin(["Media", "Alta", "Muy alta"])]
        rec_pool = rec_pool.sort_values(["Peso_num", "Ultima_dt"], ascending=[False, True], na_position="last")

    if len(rec_pool):
        rec = rec_pool.iloc[0]
        st.markdown(f'<div class="recommend-game">{rec.get("Nombre", "")}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <span class="pill">{rec.get("Tipo", "")}</span>
            <span class="pill">{rec.get("Jugadores", "")} jugadores</span>
            <span class="pill">Fricción: {rec.get("Fricción para mesa", "")}</span>
            """,
            unsafe_allow_html=True,
        )
        motivo = rec.get("Motivo de fricción", "")
        if isinstance(motivo, str) and motivo:
            st.caption(motivo)
    else:
        st.markdown('<div class="recommend-game">No hay candidatos</div>', unsafe_allow_html=True)
        st.caption("Probá aflojar algún filtro.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="tip">💡 Tip: registrá tus partidas para que las recomendaciones sean cada vez mejores.</div>', unsafe_allow_html=True)

with main:
    c1, c2, c3 = st.columns(3)

    with c1:
        panel("🆕 SIN ESTRENAR")
        sin_estrenar = df[df["Partidas_num"] == 0].copy()
        sin_estrenar["rank_fric"] = sin_estrenar["Fricción para mesa"].apply(friction_rank)
        sin_estrenar = sin_estrenar.sort_values(["rank_fric", "Nombre"]).head(6)
        show_table(sin_estrenar, ["Nombre", "Tipo", "Jugadores", "Fricción para mesa"])

    with c2:
        panel("🔥 COMPETITIVOS MENOS ROTADOS")
        menos = df[df["Tipo"].str.contains("Competitivo", case=False, na=False)].copy()
        menos = menos.sort_values(["Ultima_dt", "Partidas_num"], na_position="first").head(6)
        show_table(menos, ["Nombre", "Última partida", "Tiempo desde última partida"])

    with c3:
        panel("✅ JUGADOS RECIENTEMENTE")
        recientes = df[df["Ultima_dt"].notna()].sort_values("Ultima_dt", ascending=False).head(6)
        show_table(recientes, ["Nombre", "Última partida", "Fricción para mesa"])

    g1, g2, g3 = st.columns(3)

    with g1:
        panel("📦 DISTRIBUCIÓN POR FRICCIÓN")
        fr = df["Fricción para mesa"].value_counts().reset_index()
        fr.columns = ["Fricción", "Cantidad"]
        fig = px.pie(
            fr,
            names="Fricción",
            values="Cantidad",
            hole=0.55,
            color="Fricción",
            color_discrete_map={
                "Baja": "#6bb24a",
                "Media": "#f3b51b",
                "Alta": "#f27b2a",
                "Muy alta": "#ef4b3f",
            },
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=270, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        panel("🎲 POR TIPO")
        tipo_df = pd.DataFrame([
            {"Tipo": "Competitivo", "Cantidad": competitivos},
            {"Tipo": "Cooperativo", "Cantidad": cooperativos},
            {"Tipo": "Campaña", "Cantidad": campanias},
            {"Tipo": "Party", "Cantidad": party},
        ])
        fig = px.pie(
            tipo_df,
            names="Tipo",
            values="Cantidad",
            hole=0.55,
            color="Tipo",
            color_discrete_map={
                "Competitivo": "#1e73be",
                "Cooperativo": "#9b62d9",
                "Campaña": "#f27b2a",
                "Party": "#f3b51b",
            },
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=270, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with g3:
        panel("⚠️ ALTA FRICCIÓN / OBSERVAR")
        alta = df[df["Fricción para mesa"].isin(["Alta", "Muy alta"])].sort_values(["Ultima_dt"], na_position="first").head(6)
        show_table(alta, ["Nombre", "Tipo", "Última partida", "Fricción para mesa"])

st.markdown("""
<div class="tip">
⭐ Ideas rápidas: <b>¿Jugás con Javi?</b> filtrá 2 jugadores · <b>¿Tenés poca energía?</b> elegí baja fricción ·
<b>¿Querés movimiento?</b> estrená uno pendiente · <b>¿Querés algo épico?</b> revisá si la fricción vale el deseo real.
</div>
""", unsafe_allow_html=True)
