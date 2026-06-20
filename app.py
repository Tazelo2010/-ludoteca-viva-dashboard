
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

SPREADSHEET_ID = "19onyfrqnhTH4UeuMvDxgOnlemNa-SHdkz_wVlyEXyac"
SHEET_GID = "1910202614"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
BGG_URL = "https://boardgamegeek.com/boardgame/"
CATALOG_FILE = "bgg_catalog.json"
PLACEHOLDER_IMG = "https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f3b2.png"
# Usa siempre el BGG ID real de cada edición.
BGG_METADATA_ALIASES = {}
MANUAL_IMAGE_OVERRIDES = {
    "417197": "https://www.variantes.com/57017-large_default/rebirth.jpg",
    "246912": "https://www.amigo.games/wp-content/uploads/2024/08/18415_box.jpg",
}

st.set_page_config(page_title="Ludoteca Viva", page_icon="🎲", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 0%, rgba(233,247,236,.75), transparent 26%), radial-gradient(circle at 95% 5%, rgba(255,238,222,.9), transparent 28%), #fbf7ef; color:#173b36; }
.block-container { padding-top: .35rem; padding-bottom: 2rem; max-width: 1600px; }
header[data-testid="stHeader"] { height:0; min-height:0; background:transparent; }
div[data-testid="stToolbar"] { top:.35rem; right:.5rem; }
#MainMenu { visibility:hidden; }
section[data-testid="stSidebar"] { background:#fffaf1; border-right:1px solid #eadfcd; }
div[data-testid="stSidebarHeader"] { display:none; }
.sidebar-title { display:flex; align-items:center; gap:10px; margin:6px 0 18px 0; }
.sidebar-icon { width:32px;height:32px;border-radius:10px;background:#e6f5e8;color:#0d7a54; display:flex;align-items:center;justify-content:center;font-size:18px; }
.sidebar-title-text { color:#073f3a;font-weight:850;font-size:18px;letter-spacing:.2px; }
.filter-title { color:#123f39; font-weight:800; font-size:15px; margin:14px 0 5px 0; line-height:1.2; }
section[data-testid="stSidebar"] label { color:#173b36!important; font-weight:500!important; font-size:14px!important; }
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] div[data-baseweb="select"] { background:#fffdf9!important; border:1px solid #e6dbca!important; border-radius:11px!important; color:#173b36!important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] * { color:#173b36!important; }
.header { display:flex; align-items:center; justify-content:space-between; gap:18px; margin-bottom:18px; }
.brand { display:flex;align-items:center;gap:14px; }
.logo { width:52px;height:52px;border-radius:14px; background:linear-gradient(135deg,#e7f6e7,#fff1dc); border:1px solid #e7ddcc; display:flex;align-items:center;justify-content:center; font-size:28px; box-shadow:0 8px 22px rgba(35,63,52,.06); }
.title { font-size:28px;line-height:1.05;font-weight:900;color:#083e3b;letter-spacing:-.5px; }
.subtitle { color:#6c7c73;font-size:13px;margin-top:4px;font-weight:500; }
.metric-card { background:#fffdf9; border:1px solid #e8ddcd; border-radius:16px; padding:16px 18px; min-height:94px; display:flex; align-items:center; gap:14px; box-shadow:0 10px 26px rgba(35,63,52,.055); }
.metric-icon { width:48px;height:48px;border-radius:50%; display:flex;align-items:center;justify-content:center; font-size:25px;flex:0 0 auto; }
.metric-icon.green { background:#e4f5e7;color:#10845d; } .metric-icon.blue { background:#e6f4ff;color:#2878aa; } .metric-icon.gold { background:#fff0ce;color:#d29413; } .metric-icon.purple { background:#f1e9ff;color:#8051c4; } .metric-icon.peach { background:#ffe9dd;color:#de7044; } .metric-icon.rose { background:#ffe7ed;color:#cd4e70; }
.metric-value { font-size:27px;line-height:1;font-weight:900;color:#0b3f3b; }
.metric-label { color:#50645c;font-size:12px;font-weight:650;margin-top:6px; }
.table-title { color:#0b3f3b;font-size:20px;font-weight:850;margin-top:26px;margin-bottom:8px; }
div[data-testid="stDataFrame"] { border:1px solid #eadfcd; border-radius:16px; overflow:hidden; box-shadow:0 10px 28px rgba(35,63,52,.055); }
.card { background:#fffdf9; border:1px solid #e8ddcd; border-radius:18px; padding:17px 18px 15px 18px; min-height:180px; box-shadow:0 10px 26px rgba(35,63,52,.045); }
.card.green { background:linear-gradient(135deg,#f4fbf4,#fffdf9); } .card.blue { background:linear-gradient(135deg,#f4f9ff,#fffdf9); } .card.gold { background:linear-gradient(135deg,#fff8e8,#fffdf9); }
.card-title { font-weight:850; color:#0b3f3b; margin-bottom:8px; font-size:15px; }
.card ul { margin:0; padding-left:18px; color:#1c4942; font-size:13px; line-height:1.65; }
div[data-testid="stVerticalBlockBorderWrapper"] { background:#fffdf9; border-color:#e8ddcd!important; border-radius:18px!important; box-shadow:0 10px 26px rgba(35,63,52,.045); }
h3 { color:#0b3f3b!important; font-size:18px!important; }
.stButton > button { background:#eef8ef; color:#0d7357; border:1px solid #dcebdd; border-radius:10px; font-weight:750; }
.stButton > button:hover { background:#e3f3e6; color:#0b614b; border:1px solid #cfe4d2; }
</style>
""", unsafe_allow_html=True)

def normalize_bgg_id(value):
    if pd.isna(value): return ""
    text = str(value).strip()
    if text.endswith('.0'): text = text[:-2]
    return text

@st.cache_data(ttl=300)
def load_catalog():
    try:
        with open(CATALOG_FILE, 'r', encoding='utf-8') as f: raw = json.load(f)
        games = raw.get('games', raw if isinstance(raw, list) else [])
        by_id, by_name = {}, {}
        for g in games:
            bgg_id = normalize_bgg_id(g.get('bggId', ''))
            info = {'thumb': g.get('urlThumb', '') or g.get('urlImage', ''), 'image': g.get('urlImage', '') or g.get('urlThumb', ''), 'minPlayers': g.get('minPlayers'), 'maxPlayers': g.get('maxPlayers'), 'minPlayTime': g.get('minPlayTime'), 'maxPlayTime': g.get('maxPlayTime'), 'average': g.get('average'), 'averageweight': g.get('averageweight'), 'name': g.get('name', '')}
            if bgg_id: by_id[bgg_id] = info
            if g.get('name'): by_name[g['name'].strip().lower()] = info
        return by_id, by_name
    except Exception:
        return {}, {}

@st.cache_data(ttl=86400, show_spinner=False)
def load_bgg_live(ids):
    """Completa imágenes y el número de jugadores mejor valorado por la comunidad BGG."""
    clean_ids = []
    reverse_alias = {}
    for original in ids:
        original = normalize_bgg_id(original)
        if not original:
            continue
        source = BGG_METADATA_ALIASES.get(original, original)
        reverse_alias[source] = original
        if source not in clean_ids:
            clean_ids.append(source)

    result = {}
    for start in range(0, len(clean_ids), 20):
        batch = clean_ids[start:start + 20]
        try:
            response = None
            for attempt in range(5):
                response = requests.get(
                    "https://boardgamegeek.com/xmlapi2/thing",
                    params={"id": ",".join(batch), "stats": 1},
                    timeout=30,
                    headers={"User-Agent": "LudotecaViva-Tazelo2010/1.1"},
                )
                # BGG suele responder 202 mientras prepara el lote.
                if response.status_code == 202:
                    time.sleep(2.5 + attempt * 1.5)
                    continue
                response.raise_for_status()
                if response.content.strip():
                    break
                time.sleep(1.5)
            if response is None or response.status_code != 200 or not response.content.strip():
                raise RuntimeError("BGG no devolvió datos")
            root = ET.fromstring(response.content)
            for item in root.findall("item"):
                source_id = item.attrib.get("id", "")
                original_id = reverse_alias.get(source_id, source_id)
                image = (item.findtext("thumbnail") or item.findtext("image") or "").strip()
                best_scores = []
                poll = item.find("poll[@name='suggested_numplayers']")
                if poll is not None:
                    for results in poll.findall("results"):
                        label = results.attrib.get("numplayers", "")
                        best = 0
                        for vote in results.findall("result"):
                            if vote.attrib.get("value") == "Best":
                                try:
                                    best = int(vote.attrib.get("numvotes", "0"))
                                except ValueError:
                                    best = 0
                        if label and best > 0:
                            best_scores.append((label, best))
                best_at = ""
                if best_scores:
                    top = max(score for _, score in best_scores)
                    # Conserva opciones casi empatadas para no dar una falsa precisión.
                    labels = [label for label, score in best_scores if score >= top * 0.90]
                    best_at = ", ".join(labels)
                result[original_id] = {"thumb": image, "best_at": best_at}
        except Exception:
            pass
        if start + 20 < len(clean_ids):
            time.sleep(1.0)
    return result

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == 'object': df[col] = df[col].fillna('').astype(str).str.strip()
    by_id, by_name = load_catalog()
    bgg_col = 'Id BGG' if 'Id BGG' in df.columns else ('BGG ID' if 'BGG ID' in df.columns else None)
    df['BGG_ID'] = df[bgg_col].apply(normalize_bgg_id) if bgg_col else ''
    live_bgg = load_bgg_live(tuple(df['BGG_ID'].dropna().astype(str).tolist()))
    def catalog_info(row):
        bid = row.get('BGG_ID', '')
        nm = str(row.get('Nombre', '')).strip().lower()
        return by_id.get(bid) or by_name.get(nm) or {}
    df['_catalog'] = df.apply(catalog_info, axis=1)
    df['Thumb'] = df.apply(lambda row: (MANUAL_IMAGE_OVERRIDES.get(row['BGG_ID']) or live_bgg.get(row['BGG_ID'], {}).get('thumb') or row['_catalog'].get('thumb') or PLACEHOLDER_IMG), axis=1)
    df['Mejor a'] = df['BGG_ID'].apply(lambda bid: live_bgg.get(bid, {}).get('best_at') or 'Sin dato BGG')
    if 'Puntuación BGG' in df.columns:
        df['Rating_num'] = pd.to_numeric(df['Puntuación BGG'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    else:
        df['Rating_num'] = df['_catalog'].apply(lambda x: x.get('average')).astype(float)
    if 'Peso BGG' in df.columns:
        df['Peso_num'] = pd.to_numeric(df['Peso BGG'].astype(str).str.replace(',', '.', regex=False), errors='coerce')
    else:
        df['Peso_num'] = df['_catalog'].apply(lambda x: x.get('averageweight')).astype(float)
    df['Partidas_num'] = pd.to_numeric(df.get('Partidas', 0), errors='coerce').fillna(0).astype(int)
    df['Ultima_dt'] = pd.to_datetime(df['Última partida'], errors='coerce', dayfirst=True) if 'Última partida' in df.columns else pd.NaT
    if 'Jugadores' not in df.columns:
        def players(row):
            c = row['_catalog']
            if c.get('minPlayers') and c.get('maxPlayers'): return f"{c.get('minPlayers')}–{c.get('maxPlayers')}"
            return ''
        df['Jugadores'] = df.apply(players, axis=1)
    for col in ['Tipo', 'Fricción para mesa', 'Motivo de fricción', 'Notas']:
        if col not in df.columns: df[col] = ''
    if 'Duración' in df.columns:
        df['Tiempo'] = df['Duración'].astype(str)
    else:
        def time_text(row):
            c = row['_catalog']; mn, mx = c.get('minPlayTime'), c.get('maxPlayTime')
            if mn is None or mx is None: return ''
            try: return f"{int(mn)}–{int(mx)}"
            except Exception: return ''
        df['Tiempo'] = df.apply(time_text, axis=1)
    today = pd.Timestamp.today().normalize()
    if 'Tiempo desde última partida' not in df.columns:
        def elapsed(dt):
            if pd.isna(dt): return 'Nunca'
            days = (today - dt.normalize()).days
            if days < 7: return f'{days} días'
            if days < 31: return f'{days//7} sem'
            if days < 365: return f'{days//30} meses'
            return f'{days//365} año'
        df['Tiempo desde última partida'] = df['Ultima_dt'].apply(elapsed)
    df['BGG'] = df['BGG_ID'].apply(lambda x: f'{BGG_URL}{x}' if x else '')
    return df.drop(columns=['_catalog'])

def parse_players(text):
    nums = [int(x) for x in re.findall(r'\d+', str(text))]
    if not nums: return None, None
    return nums[0], nums[-1]

def player_match(text, selected):
    if selected == 'Todos': return True
    mn, mx = parse_players(text)
    if mn is None: return False
    n = int(selected)
    return mn <= n <= mx

def contains_any_type(value, selected_types):
    if not selected_types:
        return False
    text = str(value).lower()
    return any(selected.lower() in text for selected in selected_types)

def parse_time_max(text):
    nums = [int(x) for x in re.findall(r'\d+', str(text))]
    if not nums: return None
    return max(nums)

def friction_simple(value):
    val = str(value); low = val.lower()
    if 'alta' in low: return 'Alta'
    if 'media' in low: return 'Media'
    if 'baja' in low: return 'Baja'
    return val

def parse_time_range(text):
    nums = [int(x) for x in re.findall(r'\d+', str(text))]
    if not nums:
        return None, None
    return nums[0], nums[-1]

def estimate_total_time(row, selected_players):
    """Estimación práctica: juego + preparación + explicación inicial."""
    play_min, play_max = parse_time_range(row.get('Tiempo', ''))
    if play_min is None:
        return ''

    min_p, max_p = parse_players(row.get('Jugadores', ''))
    if selected_players != 'Todos' and min_p is not None and max_p is not None:
        n = int(selected_players)
        if max_p > min_p:
            ratio = max(0, min(1, (n - min_p) / (max_p - min_p)))
            central = play_min + (play_max - play_min) * ratio
        else:
            central = play_max
        play_low = central * 0.90
        play_high = central * 1.10
    else:
        play_low, play_high = play_min, play_max

    weight = row.get('Peso_num', 2.5)
    try:
        weight = float(weight) if pd.notna(weight) else 2.5
    except Exception:
        weight = 2.5
    friction = friction_simple(row.get('Fricción para mesa', 'Media'))
    friction_setup = {'Baja': 0, 'Media': 4, 'Alta': 9}.get(friction, 4)
    friction_teach = {'Baja': 0, 'Media': 6, 'Alta': 14}.get(friction, 6)
    setup = 3 + weight * 2.2 + friction_setup
    teach = 5 + weight * 5.0 + friction_teach
    extra_low = setup + teach
    extra_high = extra_low * 1.25

    total_low = int(round((play_low + extra_low) / 5.0) * 5)
    total_high = int(round((play_high + extra_high) / 5.0) * 5)
    if total_high <= total_low + 5:
        return f'≈ {total_low} min'
    return f'≈ {total_low}–{total_high} min'

def small_list(items):
    if not items: return '<small>Sin juegos con este filtro.</small>'
    return '<ul>' + ''.join([f'<li>{x}</li>' for x in items[:5]]) + '</ul>'

def apply_chart_layout(fig, height=260):
    fig.update_layout(height=height, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(size=12, color='#65706d'), showlegend=False)
    fig.update_xaxes(showgrid=False, zeroline=False, title=None)
    fig.update_yaxes(title=None)
    return fig

df = load_data()
# La app muestra solo las tres categorías operativas elegidas.
df = df[~df['Tipo'].str.contains('Party', case=False, na=False)].copy()

st.sidebar.markdown('<div class="sidebar-title"><div class="sidebar-icon">⌘</div><div class="sidebar-title-text">FILTROS</div></div>', unsafe_allow_html=True)

def sidebar_title(text):
    st.sidebar.markdown(f'<div class="filter-title">{text}</div>', unsafe_allow_html=True)

sidebar_title('Buscar')
search = st.sidebar.text_input('Buscar', placeholder='Escribí para buscar...', label_visibility='collapsed')

sidebar_title('Jugadores')
players_filter = st.sidebar.selectbox('Jugadores', ['Todos', '1', '2', '3', '4', '5', '6', '7', '8'], label_visibility='collapsed')

sidebar_title('Tipo')
type_competitivo = st.sidebar.checkbox('Competitivo', value=True, key='tipo_competitivo')
type_cooperativo = st.sidebar.checkbox('Cooperativo', value=True, key='tipo_cooperativo')
type_campana = st.sidebar.checkbox('Campaña', value=True, key='tipo_campana')
type_selected = [label for label, active in [('Competitivo', type_competitivo), ('Cooperativo', type_cooperativo), ('Campaña', type_campana)] if active]

sidebar_title('Fricción')
friction_baja = st.sidebar.checkbox('Baja', value=True, key='friccion_baja')
friction_media = st.sidebar.checkbox('Media', value=True, key='friccion_media')
friction_alta = st.sidebar.checkbox('Alta', value=True, key='friccion_alta')
friction_selected = [label for label, active in [('Baja', friction_baja), ('Media', friction_media), ('Alta', friction_alta)] if active]

sidebar_title('Estreno')
new_filter = st.sidebar.selectbox('Estreno', ['Todos', 'Sin estrenar', 'Estrenados'], label_visibility='collapsed')
sidebar_title('Rotación')
rotation_filter = st.sidebar.selectbox('Rotación', ['Todos', '< 1 mes', '1–6 meses', '6+ meses', 'Nunca'], label_visibility='collapsed')
sidebar_title('Peso BGG')
weight_filter = st.sidebar.selectbox('Peso BGG', ['Todos', 'Ligero', 'Medio', 'Pesado'], label_visibility='collapsed')
sidebar_title('Partidas')
games_filter = st.sidebar.selectbox('Partidas', ['Todos', '0', '1–5', '6–10', '10+'], label_visibility='collapsed')

f = df.copy()
if search: f = f[f['Nombre'].str.contains(search, case=False, na=False)]
f = f[f['Tipo'].apply(lambda x: contains_any_type(x, type_selected))]
f = f[f['Jugadores'].apply(lambda x: player_match(x, players_filter))]
if friction_selected:
    friction_values = f['Fricción para mesa'].apply(friction_simple)
    f = f[friction_values.isin(friction_selected)]
else:
    f = f.iloc[0:0]
if new_filter == 'Sin estrenar': f = f[f['Partidas_num'] == 0]
elif new_filter == 'Estrenados': f = f[f['Partidas_num'] > 0]
today = pd.Timestamp.today()
if rotation_filter == '< 1 mes': f = f[f['Ultima_dt'].notna() & (f['Ultima_dt'] >= today - pd.DateOffset(months=1))]
elif rotation_filter == '1–6 meses': f = f[f['Ultima_dt'].notna() & (f['Ultima_dt'] < today - pd.DateOffset(months=1)) & (f['Ultima_dt'] >= today - pd.DateOffset(months=6))]
elif rotation_filter == '6+ meses': f = f[f['Ultima_dt'].notna() & (f['Ultima_dt'] < today - pd.DateOffset(months=6))]
elif rotation_filter == 'Nunca': f = f[f['Partidas_num'] == 0]
if weight_filter == 'Ligero': f = f[f['Peso_num'] <= 2.0]
elif weight_filter == 'Medio': f = f[(f['Peso_num'] > 2.0) & (f['Peso_num'] <= 3.2)]
elif weight_filter == 'Pesado': f = f[f['Peso_num'] > 3.2]
if games_filter == '0': f = f[f['Partidas_num'] == 0]
elif games_filter == '1–5': f = f[(f['Partidas_num'] >= 1) & (f['Partidas_num'] <= 5)]
elif games_filter == '6–10': f = f[(f['Partidas_num'] >= 6) & (f['Partidas_num'] <= 10)]
elif games_filter == '10+': f = f[f['Partidas_num'] > 10]

st.markdown(f'<div class="header"><div class="brand"><div class="logo">🎲</div><div><div class="title">Ludoteca Viva</div><div class="subtitle">Tazelo2010 · actualizada {datetime.now().strftime("%d/%m/%Y %H:%M")}</div></div></div></div>', unsafe_allow_html=True)

total = len(df); filtered = len(f); unplayed = int((f['Partidas_num'] == 0).sum()); low_friction = int(f['Fricción para mesa'].str.contains('Baja', case=False, na=False).sum()); old_6 = int((f['Ultima_dt'].notna() & (f['Ultima_dt'] < today - pd.DateOffset(months=6))).sum()); notes_count = int(f['Notas'].astype(str).str.strip().ne('').sum())
c1,c2,c3,c4,c5,c6 = st.columns(6)
metrics=[(c1,'green','▣',total,'Juegos en ludoteca'),(c2,'blue','▽',filtered,'Juegos filtrados'),(c3,'gold','★',unplayed,'Sin estrenar'),(c4,'purple','ϟ',low_friction,'Baja fricción'),(c5,'peach','◷',old_6,'Hace +6 meses'),(c6,'rose','📝',notes_count,'Con notas')]
for col,color,icon,value,label in metrics:
    with col: st.markdown(f'<div class="metric-card"><div class="metric-icon {color}">{icon}</div><div><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div></div>', unsafe_allow_html=True)

st.markdown('<div class="table-title">Colección actual filtrada</div>', unsafe_allow_html=True)
table = f.copy()
table['Juego'] = table['Nombre']; table['BGG ID'] = table['BGG_ID']; table['Rating BGG'] = table['Rating_num'].round(2); table['Peso'] = table['Peso_num'].round(2); table['Partidas'] = table['Partidas_num']; table['Última partida'] = table['Ultima_dt'].dt.strftime('%Y-%m-%d').fillna(''); table['Hace cuánto'] = table['Tiempo desde última partida']; table['Fricción'] = table['Fricción para mesa'].apply(friction_simple); table['Notas personales'] = table['Notas'].astype(str)
table['Tiempo total est.'] = table.apply(lambda row: estimate_total_time(row, players_filter), axis=1)
cols=['Thumb','Juego','BGG','Tipo','Jugadores','Mejor a','Tiempo','Tiempo total est.','Peso','Rating BGG','Partidas','Última partida','Hace cuánto','Fricción','Notas personales']
cols=[c for c in cols if c in table.columns]
grid_df = table[cols].copy()

# Grilla tipo Excel: portada y juego fijos; el resto se recorre horizontalmente.
gb = GridOptionsBuilder.from_dataframe(grid_df)
gb.configure_default_column(
    resizable=True,
    sortable=True,
    filter=False,
    wrapText=False,
    autoHeight=False,
    suppressSizeToFit=True,
)
gb.configure_grid_options(
    rowHeight=48,
    headerHeight=40,
    suppressRowClickSelection=True,
    alwaysShowHorizontalScroll=True,
    suppressHorizontalScroll=False,
    ensureDomOrder=True,
)
gb.configure_column('Thumb', header_name='', pinned='left', lockPinned=True, width=70, minWidth=70, maxWidth=70, sortable=False,
                    cellRenderer=JsCode("""
                    class ImgRenderer {
                      init(params) {
                        this.eGui = document.createElement('div');
                        this.eGui.style.display = 'flex';
                        this.eGui.style.alignItems = 'center';
                        this.eGui.style.justifyContent = 'center';
                        this.eGui.style.height = '100%';
                        const img = document.createElement('img');
                        img.src = params.value || '';
                        img.style.width = '38px';
                        img.style.height = '38px';
                        img.style.objectFit = 'cover';
                        img.style.borderRadius = '4px';
                        this.eGui.appendChild(img);
                      }
                      getGui() { return this.eGui; }
                    }
                    """))
gb.configure_column('Juego', pinned='left', lockPinned=True, width=270, minWidth=220, maxWidth=340, tooltipField='Juego', cellRenderer=JsCode("""
class GameLinkRenderer {
  init(params) {
    this.eGui = document.createElement('a');
    this.eGui.textContent = params.value || '';
    const url = params.data && params.data.BGG ? params.data.BGG : '';
    if (url) {
      this.eGui.href = url;
      this.eGui.target = '_blank';
      this.eGui.rel = 'noopener noreferrer';
    }
    this.eGui.style.color = 'inherit';
    this.eGui.style.textDecoration = 'none';
    this.eGui.style.fontWeight = '600';
    this.eGui.style.display = 'block';
    this.eGui.style.overflow = 'hidden';
    this.eGui.style.textOverflow = 'ellipsis';
    this.eGui.style.whiteSpace = 'nowrap';
  }
  getGui() { return this.eGui; }
}
"""))
gb.configure_column('BGG', hide=True)
gb.configure_column('Tipo', width=120, minWidth=105, maxWidth=145, tooltipField='Tipo')
gb.configure_column('Jugadores', width=95, minWidth=88, maxWidth=110)
gb.configure_column('Mejor a', width=92, minWidth=84, maxWidth=120, tooltipField='Mejor a')
gb.configure_column('Tiempo', width=96, minWidth=88, maxWidth=110)
gb.configure_column('Tiempo total est.', width=142, minWidth=132, maxWidth=170, tooltipField='Tiempo total est.')
gb.configure_column('Peso', width=72, minWidth=68, maxWidth=82)
gb.configure_column('Rating BGG', width=100, minWidth=92, maxWidth=115)
gb.configure_column('Partidas', width=82, minWidth=76, maxWidth=92)
gb.configure_column('Última partida', width=118, minWidth=110, maxWidth=130)
gb.configure_column('Hace cuánto', width=112, minWidth=104, maxWidth=125)
gb.configure_column('Fricción', width=88, minWidth=82, maxWidth=100)
gb.configure_column('Notas personales', width=250, minWidth=190, maxWidth=360, tooltipField='Notas personales')
AgGrid(
    grid_df,
    gridOptions=gb.build(),
    height=560,
    fit_columns_on_grid_load=False,
    allow_unsafe_jscode=True,
    theme='streamlit',
    update_on=[],
    key='coleccion_filtrada_grid_v9',
)
st.caption('Tiempo total estimado = preparación + explicación inicial + partida. Es una guía práctica; se ajusta al número de jugadores elegido, al peso BGG y a la fricción registrada.')

notes_df = table[table['Notas personales'].astype(str).str.strip() != '']
if len(notes_df):
    with st.expander(f'📝 Notas personales visibles ({len(notes_df)})', expanded=False):
        st.dataframe(notes_df[['Juego','Notas personales']].copy(), use_container_width=True, hide_index=True, height=240)

p1,p2,p3,p4 = st.columns(4)
sin_estrenar = f[f['Partidas_num'] == 0].sort_values(['Peso_num','Rating_num'], ascending=[True,False], na_position='last')['Nombre'].head(5).tolist()
menos_jugados = f.sort_values(['Partidas_num','Ultima_dt'], ascending=[True,True], na_position='first')['Nombre'].head(5).tolist()
mas_6 = f[f['Ultima_dt'].notna() & (f['Ultima_dt'] < today - pd.DateOffset(months=6))].sort_values('Ultima_dt')['Nombre'].head(5).tolist()
recientes = f[f['Ultima_dt'].notna()].sort_values('Ultima_dt', ascending=False)['Nombre'].head(5).tolist()
with p1: st.markdown(f'<div class="card green"><div class="card-title">Sin estrenar ({len(f[f["Partidas_num"] == 0])})</div>{small_list(sin_estrenar)}</div>', unsafe_allow_html=True)
with p2: st.markdown(f'<div class="card blue"><div class="card-title">Menos jugados</div>{small_list(menos_jugados)}</div>', unsafe_allow_html=True)
with p3: st.markdown(f'<div class="card gold"><div class="card-title">Hace más de 6 meses ({len(f[f["Ultima_dt"].notna() & (f["Ultima_dt"] < today - pd.DateOffset(months=6))])})</div>{small_list(mas_6)}</div>', unsafe_allow_html=True)
with p4: st.markdown(f'<div class="card green"><div class="card-title">Jugados recientemente</div>{small_list(recientes)}</div>', unsafe_allow_html=True)

st.markdown('<div class="table-title">Estadísticas del filtro</div>', unsafe_allow_html=True)
g1,g2,g3 = st.columns(3)
with g1:
    with st.container(border=True):
        st.markdown('### Fricción')
        fr=f['Fricción para mesa'].replace('', 'Sin dato').value_counts().reset_index(); fr.columns=['Fricción','Cantidad']
        if len(fr):
            fig=px.pie(fr, names='Fricción', values='Cantidad', hole=.55, color='Fricción', color_discrete_map={'Baja':'#69c184','Media':'#f0a440','Alta':'#ef6b5f','Sin dato':'#d8d2c8'})
            fig.update_layout(height=260, margin=dict(l=5,r=5,t=5,b=5), paper_bgcolor='rgba(0,0,0,0)', font=dict(size=12,color='#65706d'), legend=dict(orientation='h', y=-0.05))
            st.plotly_chart(fig, use_container_width=True)
        st.caption(f'Total: {len(f)} juegos')
with g2:
    with st.container(border=True):
        st.markdown('### Tipo')
        rows=[{'Tipo':t,'Cantidad':int(f['Tipo'].str.contains(t, case=False, na=False).sum())} for t in ['Competitivo','Cooperativo','Campaña']]
        fig=px.bar(pd.DataFrame(rows), y='Tipo', x='Cantidad', orientation='h', color='Tipo', color_discrete_map={'Competitivo':'#6ec28a','Cooperativo':'#7fb8e8','Campaña':'#b99be7'})
        st.plotly_chart(apply_chart_layout(fig,260), use_container_width=True)
with g3:
    with st.container(border=True):
        st.markdown('### Jugadores')
        rows=[{'Jugadores': f'{n} jugador' if n==1 else f'{n} jugadores', 'Cantidad': int(f['Jugadores'].apply(lambda x: player_match(x, str(n))).sum())} for n in [1,2,3,4,5]]
        fig=px.bar(pd.DataFrame(rows), y='Jugadores', x='Cantidad', orientation='h', color_discrete_sequence=['#87c7ee'])
        st.plotly_chart(apply_chart_layout(fig,260), use_container_width=True)

g4,g5 = st.columns(2)
with g4:
    with st.container(border=True):
        st.markdown('### Tiempo de juego')
        bins={'0–30 min':0,'30–60 min':0,'60–120 min':0,'120+ min':0}
        for x in f['Tiempo']:
            mx=parse_time_max(x)
            if mx is None: continue
            if mx <= 30: bins['0–30 min'] += 1
            elif mx <= 60: bins['30–60 min'] += 1
            elif mx <= 120: bins['60–120 min'] += 1
            else: bins['120+ min'] += 1
        fig=px.bar(pd.DataFrame({'Tiempo':list(bins.keys()), 'Cantidad':list(bins.values())}), y='Tiempo', x='Cantidad', orientation='h', color_discrete_sequence=['#c6a0e9'])
        st.plotly_chart(apply_chart_layout(fig,260), use_container_width=True)
with g5:
    with st.container(border=True):
        st.markdown('### Peso BGG')
        bins={'Ligero (1–2)':int((f['Peso_num'] <= 2).sum()), 'Medio (2–3)':int(((f['Peso_num'] > 2) & (f['Peso_num'] <= 3.2)).sum()), 'Pesado (3+)':int((f['Peso_num'] > 3.2).sum())}
        fig=px.bar(pd.DataFrame({'Peso':list(bins.keys()), 'Cantidad':list(bins.values())}), y='Peso', x='Cantidad', orientation='h', color_discrete_sequence=['#f0a440'])
        st.plotly_chart(apply_chart_layout(fig,260), use_container_width=True)
