
import json
import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# CONFIG
# =========================

SPREADSHEET_ID = "19onyfrqnhTH4UeuMvDxgOnlemNa-SHdkz_wVlyEXyac"
SHEET_GID = "1910202614"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"

BGG_URL = "https://boardgamegeek.com/boardgame/"
CATALOG_FILE = "bgg_catalog.json"

st.set_page_config(
    page_title="Ludoteca Viva",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================
# STYLE
# =========================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 20% 0%, rgba(233, 247, 236, 0.75), transparent 26%),
        radial-gradient(circle at 95% 5%, rgba(255, 238, 222, 0.90), transparent 28%),
        #fbf7ef;
    color: #173b36;
}

.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1580px;
}

section[data-testid="stSidebar"] {
    background: #fffaf1;
    border-right: 1px solid #eadfcd;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.25rem;
}

div[data-testid="stSidebarHeader"] {
    display: none;
}

.sidebar-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 6px 0 18px 0;
}

.sidebar-icon {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: #e6f5e8;
    color: #0d7a54;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}

.sidebar-title-text {
    color: #073f3a;
    font-weight: 850;
    font-size: 18px;
    letter-spacing: .2px;
}

section[data-testid="stSidebar"] label {
    color: #173b36 !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}

section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background: #fffdf9 !important;
    border: 1px solid #e6dbca !important;
    border-radius: 11px !important;
    color: #173b36 !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #173b36 !important;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 18px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(135deg, #e7f6e7, #fff1dc);
    border: 1px solid #e7ddcc;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    box-shadow: 0 8px 22px rgba(35, 63, 52, .06);
}

.title {
    font-size: 28px;
    line-height: 1.05;
    font-weight: 900;
    color: #083e3b;
    letter-spacing: -0.5px;
}

.subtitle {
    color: #6c7c73;
    font-size: 13px;
    margin-top: 4px;
    font-weight: 500;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}

.soft-button {
    background: #fffdf9;
    border: 1px solid #e8ddcd;
    border-radius: 12px;
    padding: 11px 14px;
    color: #173b36;
    font-weight: 700;
    font-size: 14px;
    box-shadow: 0 6px 18px rgba(35, 63, 52, .045);
}

.updated {
    color: #809088;
    font-size: 12px;
    text-align: right;
    margin-top: 4px;
}

.search-card {
    background: #fffdf9;
    border: 1px solid #e8ddcd;
    border-radius: 14px;
    padding: 6px 14px;
    min-width: 330px;
    box-shadow: 0 8px 22px rgba(35, 63, 52, .05);
}

.metric-card {
    background: #fffdf9;
    border: 1px solid #e8ddcd;
    border-radius: 16px;
    padding: 16px 18px;
    min-height: 94px;
    display: flex;
    align-items: center;
    gap: 14px;
    box-shadow: 0 10px 26px rgba(35, 63, 52, .055);
}

.metric-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size: 25px;
    flex: 0 0 auto;
}

.metric-icon.green { background:#e4f5e7; color:#10845d; }
.metric-icon.blue { background:#e6f4ff; color:#2878aa; }
.metric-icon.gold { background:#fff0ce; color:#d29413; }
.metric-icon.purple { background:#f1e9ff; color:#8051c4; }
.metric-icon.peach { background:#ffe9dd; color:#de7044; }
.metric-icon.rose { background:#ffe7ed; color:#cd4e70; }

.metric-value {
    font-size: 27px;
    line-height: 1;
    font-weight: 900;
    color: #0b3f3b;
}

.metric-label {
    color: #50645c;
    font-size: 12px;
    font-weight: 650;
    margin-top: 6px;
}

.table-toolbar {
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-top: 24px;
    margin-bottom: 8px;
}

.table-title {
    color: #0b3f3b;
    font-size: 18px;
    font-weight: 850;
}

.toolbar-actions {
    display:flex;
    gap:10px;
    color:#425a52;
    font-size:13px;
    font-weight:700;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #eadfcd;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 10px 28px rgba(35, 63, 52, .055);
}

div[data-testid="stDataFrame"] [data-testid="stTable"] {
    background: #fffdf9;
}

.panel {
    background: #fffdf9;
    border: 1px solid #e8ddcd;
    border-radius: 16px;
    padding: 17px 18px 15px 18px;
    min-height: 190px;
    box-shadow: 0 10px 26px rgba(35, 63, 52, .045);
}

.panel.green { background: linear-gradient(135deg, #f4fbf4, #fffdf9); }
.panel.blue { background: linear-gradient(135deg, #f4f9ff, #fffdf9); }
.panel.gold { background: linear-gradient(135deg, #fff8e8, #fffdf9); }
.panel.red { background: linear-gradient(135deg, #fff2f2, #fffdf9); }

.panel-title {
    font-weight: 850;
    color: #0b3f3b;
    margin-bottom: 8px;
    font-size: 15px;
}

.panel ul {
    margin: 0;
    padding-left: 17px;
    color: #1c4942;
    font-size: 13px;
    line-height: 1.8;
}

.panel small {
    color: #718179;
}

.link-button {
    display:inline-block;
    margin-top: 12px;
    border: 1px solid #dce9dd;
    background: #fffdf9;
    border-radius: 10px;
    padding: 8px 11px;
    color: #0d7357;
    font-weight: 750;
    font-size: 13px;
}

.stButton > button {
    background: #eef8ef;
    color: #0d7357;
    border: 1px solid #dcebdd;
    border-radius: 10px;
    font-weight: 750;
}

.stButton > button:hover {
    background: #e3f3e6;
    color: #0b614b;
    border: 1px solid #cfe4d2;
}

hr {
    border: none;
    border-top: 1px solid #eadfcd;
}

.badge {
    display:inline-block;
    border-radius: 999px;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 750;
}

.badge-baja { background:#e4f5e7; color:#177151; border:1px solid #ccebd4; }
.badge-media { background:#fff2d5; color:#9c6500; border:1px solid #ffe2a3; }
.badge-alta { background:#ffe4e4; color:#b93030; border:1px solid #ffcaca; }
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# HELPERS
# =========================

def normalize_bgg_id(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


@st.cache_data(ttl=300)
def load_catalog():
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        games = raw.get("games", raw if isinstance(raw, list) else [])
        by_id = {}
        for g in games:
            bgg_id = normalize_bgg_id(g.get("bggId", ""))
            if bgg_id:
                by_id[bgg_id] = {
                    "thumb": g.get("urlThumb", ""),
                    "image": g.get("urlImage", ""),
                    "minPlayers": g.get("minPlayers"),
                    "maxPlayers": g.get("maxPlayers"),
                    "minPlayTime": g.get("minPlayTime"),
                    "maxPlayTime": g.get("maxPlayTime"),
                    "average": g.get("average"),
                    "averageweight": g.get("averageweight"),
                    "year": g.get("yearPublished"),
                }
        return by_id
    except Exception:
        return {}


@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [c.strip() for c in df.columns]

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("").astype(str).str.strip()

    # Column aliases from the Google Sheet
    name_col = "Nombre"
    bgg_col = "Id BGG" if "Id BGG" in df.columns else ("BGG ID" if "BGG ID" in df.columns else None)

    if bgg_col:
        df["BGG_ID"] = df[bgg_col].apply(normalize_bgg_id)
    else:
        df["BGG_ID"] = ""

    catalog = load_catalog()

    # BGG metadata fallback
    df["Thumb"] = df["BGG_ID"].map(lambda x: catalog.get(x, {}).get("thumb", ""))

    if "Puntuación BGG" in df.columns:
        df["Rating_num"] = pd.to_numeric(df["Puntuación BGG"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    else:
        df["Rating_num"] = df["BGG_ID"].map(lambda x: catalog.get(x, {}).get("average")).astype(float)

    if "Peso BGG" in df.columns:
        df["Peso_num"] = pd.to_numeric(df["Peso BGG"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    else:
        df["Peso_num"] = df["BGG_ID"].map(lambda x: catalog.get(x, {}).get("averageweight")).astype(float)

    df["Partidas_num"] = pd.to_numeric(df.get("Partidas", 0), errors="coerce").fillna(0).astype(int)

    if "Última partida" in df.columns:
        df["Ultima_dt"] = pd.to_datetime(df["Última partida"], errors="coerce", dayfirst=True)
    else:
        df["Ultima_dt"] = pd.NaT

    if "Jugadores" not in df.columns:
        df["Jugadores"] = df["BGG_ID"].map(
            lambda x: (
                f"{catalog.get(x, {}).get('minPlayers')}–{catalog.get(x, {}).get('maxPlayers')}"
                if catalog.get(x, {}).get("minPlayers") and catalog.get(x, {}).get("maxPlayers")
                else ""
            )
        )

    if "Tipo" not in df.columns:
        df["Tipo"] = ""

    if "Fricción para mesa" not in df.columns:
        df["Fricción para mesa"] = ""

    if "Motivo de fricción" not in df.columns:
        df["Motivo de fricción"] = ""

    if "Notas" not in df.columns:
        df["Notas"] = ""

    # Time
    if "Duración" in df.columns:
        df["Tiempo"] = df["Duración"].astype(str)
        df["Tiempo_min_max"] = df["Duración"].astype(str)
    else:
        df["Tiempo"] = df["BGG_ID"].map(
            lambda x: (
                f"{int(catalog.get(x, {}).get('minPlayTime'))}–{int(catalog.get(x, {}).get('maxPlayTime'))}"
                if catalog.get(x, {}).get("minPlayTime") is not None and catalog.get(x, {}).get("maxPlayTime") is not None
                else ""
            )
        )

    if "Tiempo desde última partida" not in df.columns:
        today = pd.Timestamp.today().normalize()
        def elapsed(dt):
            if pd.isna(dt):
                return "Nunca"
            days = (today - dt.normalize()).days
            if days < 7:
                return f"{days} días"
            if days < 31:
                return f"{days//7} sem"
            if days < 365:
                return f"{days//30} meses"
            return f"{days//365} año"
        df["Tiempo desde última partida"] = df["Ultima_dt"].apply(elapsed)

    df["BGG"] = df["BGG_ID"].apply(lambda x: f"{BGG_URL}{x}" if x else "")

    return df


def parse_players(text):
    nums = [int(x) for x in re.findall(r"\d+", str(text))]
    if not nums:
        return None, None
    return nums[0], nums[-1]


def player_match(text, selected):
    if selected == "Todos":
        return True
    mn, mx = parse_players(text)
    if mn is None:
        return False
    n = int(selected)
    return mn <= n <= mx


def contains_type(value, selected):
    if selected == "Todos":
        return True
    return selected.lower() in str(value).lower()


def parse_time_max(text):
    nums = [int(x) for x in re.findall(r"\d+", str(text))]
    if not nums:
        return None
    return max(nums)


def friction_class(value):
    v = str(value).lower()
    if "baja" in v:
        return "Baja"
    if "media" in v:
        return "Media"
    if "alta" in v:
        return "Alta"
    return value


def filter_chip(value):
    val = friction_class(value)
    if val == "Baja":
        return "🟢 Baja"
    if val == "Media":
        return "🟠 Media"
    if val == "Alta" or val == "Muy alta":
        return "🔴 Alta"
    return val


def small_list(items):
    if not items:
        return "<small>Sin juegos con este filtro.</small>"
    lis = "".join([f"<li>{x}</li>" for x in items[:5]])
    return f"<ul>{lis}</ul>"


# =========================
# LOAD
# =========================

df = load_data()


# =========================
# SIDEBAR
# =========================

st.sidebar.markdown(
    """
<div class="sidebar-title">
    <div class="sidebar-icon">⌘</div>
    <div class="sidebar-title-text">FILTROS</div>
</div>
""",
    unsafe_allow_html=True,
)

search = st.sidebar.text_input("Buscar", placeholder="Escribí para buscar...")

type_filter = st.sidebar.selectbox("Tipo", ["Todos", "Competitivo", "Cooperativo", "Campaña", "Party"])
players_filter = st.sidebar.selectbox("Jugadores", ["Todos", "1", "2", "3", "4", "5", "6", "7", "8"])
friction_filter = st.sidebar.selectbox("Fricción", ["Todas", "Baja", "Media", "Alta", "Muy alta"])
new_filter = st.sidebar.selectbox("Estreno", ["Todos", "Sin estrenar", "Estrenados"])
rotation_filter = st.sidebar.selectbox("Rotación (última partida)", ["Todos", "< 1 mes", "1–6 meses", "6+ meses", "Nunca"])
weight_filter = st.sidebar.selectbox("Peso BGG", ["Todos", "Ligero", "Medio", "Pesado"])
games_filter = st.sidebar.selectbox("Partidas", ["Todos", "0", "1–5", "6–10", "10+"])


# =========================
# FILTERS
# =========================

f = df.copy()

if search:
    f = f[f["Nombre"].str.contains(search, case=False, na=False)]

f = f[f["Tipo"].apply(lambda x: contains_type(x, type_filter))]
f = f[f["Jugadores"].apply(lambda x: player_match(x, players_filter))]

if friction_filter != "Todas":
    f = f[f["Fricción para mesa"].str.contains(friction_filter, case=False, na=False)]

if new_filter == "Sin estrenar":
    f = f[f["Partidas_num"] == 0]
elif new_filter == "Estrenados":
    f = f[f["Partidas_num"] > 0]

today = pd.Timestamp.today()
if rotation_filter == "< 1 mes":
    f = f[f["Ultima_dt"].notna() & (f["Ultima_dt"] >= today - pd.DateOffset(months=1))]
elif rotation_filter == "1–6 meses":
    f = f[f["Ultima_dt"].notna() & (f["Ultima_dt"] < today - pd.DateOffset(months=1)) & (f["Ultima_dt"] >= today - pd.DateOffset(months=6))]
elif rotation_filter == "6+ meses":
    f = f[f["Ultima_dt"].notna() & (f["Ultima_dt"] < today - pd.DateOffset(months=6))]
elif rotation_filter == "Nunca":
    f = f[f["Partidas_num"] == 0]

if weight_filter == "Ligero":
    f = f[f["Peso_num"] <= 2.0]
elif weight_filter == "Medio":
    f = f[(f["Peso_num"] > 2.0) & (f["Peso_num"] <= 3.2)]
elif weight_filter == "Pesado":
    f = f[f["Peso_num"] > 3.2]

if games_filter == "0":
    f = f[f["Partidas_num"] == 0]
elif games_filter == "1–5":
    f = f[(f["Partidas_num"] >= 1) & (f["Partidas_num"] <= 5)]
elif games_filter == "6–10":
    f = f[(f["Partidas_num"] >= 6) & (f["Partidas_num"] <= 10)]
elif games_filter == "10+":
    f = f[f["Partidas_num"] > 10]


# =========================
# HEADER
# =========================

st.markdown(
    f"""
<div class="header">
    <div class="brand">
        <div class="logo">🎲</div>
        <div>
            <div class="title">Ludoteca Viva</div>
            <div class="subtitle">Tazelo2010 · actualizada {datetime.now().strftime("%d/%m/%Y %H:%M")}</div>
        </div>
    </div>
    <div class="header-actions">
        <div class="soft-button">📖 Guía rápida</div>
        <div class="soft-button">♡ Favoritos</div>
        <div class="soft-button">⚙</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================
# METRICS
# =========================

total = len(df)
filtered = len(f)
unplayed = int((f["Partidas_num"] == 0).sum())
low_friction = int(f["Fricción para mesa"].str.contains("Baja", case=False, na=False).sum())
old_6 = int((f["Ultima_dt"].notna() & (f["Ultima_dt"] < today - pd.DateOffset(months=6))).sum())
favorites = int(f["Notas"].str.contains("favorit|favorito|favorita|me encanta", case=False, na=False).sum()) if "Notas" in f.columns else 0

c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-icon green">▣</div><div><div class="metric-value">{total}</div><div class="metric-label">Juegos en ludoteca</div></div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><div class="metric-icon blue">▽</div><div><div class="metric-value">{filtered}</div><div class="metric-label">Juegos filtrados</div></div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><div class="metric-icon gold">★</div><div><div class="metric-value">{unplayed}</div><div class="metric-label">Sin estrenar</div></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><div class="metric-icon purple">ϟ</div><div><div class="metric-value">{low_friction}</div><div class="metric-label">Baja fricción</div></div></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="metric-card"><div class="metric-icon peach">◷</div><div><div class="metric-value">{old_6}</div><div class="metric-label">Hace +6 meses</div></div></div>', unsafe_allow_html=True)
with c6:
    st.markdown(f'<div class="metric-card"><div class="metric-icon rose">♡</div><div><div class="metric-value">{favorites}</div><div class="metric-label">Favoritos</div></div></div>', unsafe_allow_html=True)


# =========================
# TABLE
# =========================

st.markdown(
    """
<div class="table-toolbar">
    <div class="table-title">Colección actual filtrada</div>
    <div class="toolbar-actions">
        <span>▦ Columnas</span>
        <span>↧ Exportar</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

table = f.copy()

# Visible columns
table["Juego"] = table["Nombre"]
table["BGG ID"] = table["BGG_ID"]
table["Rating BGG"] = table["Rating_num"].round(2)
table["Peso"] = table["Peso_num"].round(2)
table["Partidas"] = table["Partidas_num"]
table["Última partida"] = table["Ultima_dt"].dt.strftime("%Y-%m-%d").fillna("")
table["Hace cuánto"] = table["Tiempo desde última partida"]
table["Fricción"] = table["Fricción para mesa"].apply(filter_chip)
table["Notas"] = table["Notas"].apply(lambda x: "📝" if str(x).strip() else "")
table["BGG"] = table["BGG"]

cols = ["Thumb", "Juego", "BGG ID", "BGG", "Tipo", "Jugadores", "Tiempo", "Peso", "Rating BGG", "Partidas", "Última partida", "Hace cuánto", "Fricción", "Notas"]
cols = [c for c in cols if c in table.columns]

st.dataframe(
    table[cols],
    use_container_width=True,
    hide_index=True,
    height=520,
    column_config={
        "Thumb": st.column_config.ImageColumn(""),
        "BGG": st.column_config.LinkColumn("BGG", display_text="↗"),
        "Juego": st.column_config.TextColumn("Juego", width="medium"),
        "Notas": st.column_config.TextColumn("Notas", width="small"),
        "Fricción": st.column_config.TextColumn("Fricción", width="small"),
    },
)


# =========================
# LOWER PANELS
# =========================

p1, p2, p3, p4, p5 = st.columns([1, 1, 1, 1, 1.15])

sin_estrenar = f[f["Partidas_num"] == 0].sort_values(["Peso_num", "Rating_num"], ascending=[True, False], na_position="last")["Nombre"].head(5).tolist()
menos_jugados = f.sort_values(["Partidas_num", "Ultima_dt"], ascending=[True, True], na_position="first")["Nombre"].head(5).tolist()
mas_6 = f[f["Ultima_dt"].notna() & (f["Ultima_dt"] < today - pd.DateOffset(months=6))].sort_values("Ultima_dt")["Nombre"].head(5).tolist()
recientes = f[f["Ultima_dt"].notna()].sort_values("Ultima_dt", ascending=False)["Nombre"].head(5).tolist()

with p1:
    st.markdown(f'<div class="panel green"><div class="panel-title">Sin estrenar ({len(f[f["Partidas_num"] == 0])})</div>{small_list(sin_estrenar)}<div class="link-button">Ver todos</div></div>', unsafe_allow_html=True)

with p2:
    st.markdown(f'<div class="panel blue"><div class="panel-title">Menos jugados</div>{small_list(menos_jugados)}<div class="link-button">Ver todos</div></div>', unsafe_allow_html=True)

with p3:
    st.markdown(f'<div class="panel gold"><div class="panel-title">Hace más de 6 meses ({len(f[f["Ultima_dt"].notna() & (f["Ultima_dt"] < today - pd.DateOffset(months=6))])})</div>{small_list(mas_6)}<div class="link-button">Ver todos</div></div>', unsafe_allow_html=True)

with p4:
    st.markdown(f'<div class="panel green"><div class="panel-title">Jugados recientemente</div>{small_list(recientes)}<div class="link-button">Ver todos</div></div>', unsafe_allow_html=True)

with p5:
    st.markdown('<div class="panel red"><div class="panel-title">Distribución por fricción</div>', unsafe_allow_html=True)
    fr = f["Fricción para mesa"].replace("", "Sin dato").value_counts().reset_index()
    fr.columns = ["Fricción", "Cantidad"]
    if len(fr):
        fig = px.pie(
            fr,
            names="Fricción",
            values="Cantidad",
            hole=0.55,
            color="Fricción",
            color_discrete_map={
                "Baja": "#69c184",
                "Media": "#f0a440",
                "Alta": "#ef6b5f",
                "Muy alta": "#d85c5c",
                "Sin dato": "#d8d2c8",
            },
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=155, showlegend=True, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"<small>Total: {len(f)} juegos</small></div>", unsafe_allow_html=True)


# =========================
# EXTRA CHARTS
# =========================

g1, g2, g3, g4 = st.columns(4)

with g1:
    st.markdown('<div class="panel"><div class="panel-title">Por tipo</div>', unsafe_allow_html=True)
    if len(f):
        type_counts = []
        for t in ["Competitivo", "Cooperativo", "Campaña", "Party"]:
            type_counts.append({"Tipo": t, "Cantidad": int(f["Tipo"].str.contains(t, case=False, na=False).sum())})
        chart = pd.DataFrame(type_counts)
        fig = px.bar(chart, y="Tipo", x="Cantidad", orientation="h", color="Tipo",
                     color_discrete_map={"Competitivo":"#6ec28a","Cooperativo":"#7fb8e8","Campaña":"#b99be7","Party":"#f3c55d"})
        fig.update_layout(height=160, showlegend=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g2:
    st.markdown('<div class="panel"><div class="panel-title">Por jugadores</div>', unsafe_allow_html=True)
    if len(f):
        rows = []
        for n in [1,2,3,4,5]:
            rows.append({"Jugadores": f"{n} jugador" if n == 1 else f"{n} jugadores", "Cantidad": int(f["Jugadores"].apply(lambda x: player_match(x, str(n))).sum())})
        chart = pd.DataFrame(rows)
        fig = px.bar(chart, y="Jugadores", x="Cantidad", orientation="h", color_discrete_sequence=["#87c7ee"])
        fig.update_layout(height=160, showlegend=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g3:
    st.markdown('<div class="panel"><div class="panel-title">Por tiempo de juego</div>', unsafe_allow_html=True)
    if len(f):
        bins = {"0–30 min":0, "30–60 min":0, "60–120 min":0, "120+ min":0}
        for x in f["Tiempo"]:
            mx = parse_time_max(x)
            if mx is None:
                continue
            if mx <= 30: bins["0–30 min"] += 1
            elif mx <= 60: bins["30–60 min"] += 1
            elif mx <= 120: bins["60–120 min"] += 1
            else: bins["120+ min"] += 1
        chart = pd.DataFrame({"Tiempo": list(bins.keys()), "Cantidad": list(bins.values())})
        fig = px.bar(chart, y="Tiempo", x="Cantidad", orientation="h", color_discrete_sequence=["#c6a0e9"])
        fig.update_layout(height=160, showlegend=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with g4:
    st.markdown('<div class="panel"><div class="panel-title">Por peso BGG</div>', unsafe_allow_html=True)
    if len(f):
        bins = {
            "Ligero (1–2)": int((f["Peso_num"] <= 2).sum()),
            "Medio (2–3)": int(((f["Peso_num"] > 2) & (f["Peso_num"] <= 3.2)).sum()),
            "Pesado (3+)": int((f["Peso_num"] > 3.2).sum()),
        }
        chart = pd.DataFrame({"Peso": list(bins.keys()), "Cantidad": list(bins.values())})
        fig = px.bar(chart, y="Peso", x="Cantidad", orientation="h", color_discrete_sequence=["#f0a440"])
        fig.update_layout(height=160, showlegend=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
