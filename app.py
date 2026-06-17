import re
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

SPREADSHEET_ID="19onyfrqnhTH4UeuMvDxgOnlemNa-SHdkz_wVlyEXyac"
SHEET_GID="1910202614"
CSV_URL=f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"

st.set_page_config(page_title="Ludoteca viva – Tazelo2010", page_icon="🎲", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp{background:#f7f5ef;color:#12342a}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#073f2f 0%,#0b5a42 100%)}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p{color:white!important}
section[data-testid="stSidebar"] div[data-baseweb="select"]{background:white!important;color:#12342a!important;border-radius:10px}
section[data-testid="stSidebar"] div[data-baseweb="select"] *{color:#12342a!important}
.title{font-size:34px;font-weight:900;color:#073f2f;letter-spacing:-.5px}
.subtitle{color:#0b5a42;font-size:17px;font-style:italic}
.updated{text-align:right;color:#073f2f;font-weight:700;font-size:13px}
.metric-card{background:#fffdf8;border:1px solid #e5ddcc;border-radius:16px;padding:16px;min-height:108px;box-shadow:0 4px 14px rgba(25,44,35,.08);display:flex;align-items:center;gap:14px}
.metric-icon{width:54px;height:54px;border-radius:50%;background:#eaf3e7;display:flex;align-items:center;justify-content:center;font-size:28px}
.metric-label{font-size:12px;font-weight:800;text-transform:uppercase;color:#0b5a42}
.metric-value{font-size:32px;font-weight:900;color:#073f2f;line-height:1.05}
.metric-note{font-size:12px;color:#6b756f;margin-top:3px}
.panel-header{background:linear-gradient(90deg,#073f2f 0%,#0b5a42 100%);color:white;padding:10px 14px;font-weight:900;font-size:16px;border-radius:16px 16px 0 0;margin-top:10px}
.recommend-card{background:#fffdf8;border:1px solid #e5ddcc;border-radius:16px;padding:18px;box-shadow:0 4px 14px rgba(25,44,35,.08);text-align:center;margin-top:10px}
.recommend-title{font-size:14px;font-weight:900;color:#0b5a42;margin-bottom:10px}
.recommend-game{font-size:26px;font-weight:900;color:#073f2f;margin:16px 0 6px 0}
.pill{display:inline-block;background:#eaf3e7;border-radius:999px;padding:5px 10px;font-size:12px;color:#073f2f;font-weight:700;margin:3px}
.tip{background:#fff7df;border:1px solid #f0dfad;border-radius:14px;padding:14px 18px;color:#143d2e;font-weight:650;margin-top:12px}
div[data-testid="stDataFrame"]{border-radius:0 0 16px 16px;overflow:hidden;border:1px solid #e5ddcc}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    df=pd.read_csv(CSV_URL)
    df.columns=[c.strip() for c in df.columns]
    for col in ["Nombre","Tipo","Jugadores","Fricción para mesa","Motivo de fricción"]:
        if col in df.columns: df[col]=df[col].fillna("").astype(str).str.strip()
    df["Partidas_num"]=pd.to_numeric(df.get("Partidas",0), errors="coerce").fillna(0).astype(int)
    df["Peso_num"]=pd.to_numeric(df.get("Peso BGG","").astype(str).str.replace(",",".",regex=False), errors="coerce") if "Peso BGG" in df.columns else None
    df["Ultima_dt"]=pd.to_datetime(df.get("Última partida",""), errors="coerce") if "Última partida" in df.columns else pd.NaT
    return df

def parse_players(t):
    nums=[int(x) for x in re.findall(r"\d+", str(t))]
    if not nums: return None,None
    return (nums[0], nums[-1])

def player_match(j, selected):
    if selected=="Todos": return True
    mn,mx=parse_players(j)
    return mn is not None and mn<=int(selected)<=mx

def contains_type(t, selected):
    return True if selected=="Todos" else selected.lower() in str(t).lower()

def friction_rank(v):
    return {"Baja":1,"Media":2,"Alta":3,"Muy alta":4}.get(str(v),9)

def metric_card(icon,label,value,note=""):
    st.markdown(f"""<div class="metric-card"><div class="metric-icon">{icon}</div><div><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div></div>""", unsafe_allow_html=True)

def panel(t): st.markdown(f'<div class="panel-header">{t}</div>', unsafe_allow_html=True)

def show_table(data, cols, height=250):
    show=data[[c for c in cols if c in data.columns]].copy()
    st.dataframe(show, use_container_width=True, hide_index=True, height=height)

df=load_data()

st.sidebar.markdown("## 🎛️ Filtros rápidos")
tipo_opt=st.sidebar.selectbox("Tipo",["Todos","Competitivo","Cooperativo","Campaña","Party"])
jug_opt=st.sidebar.selectbox("Jugadores",["Todos","1","2","3","4","5","6"])
fric_opt=st.sidebar.selectbox("Fricción",["Todos","Baja","Media","Alta","Muy alta"])
estreno_opt=st.sidebar.selectbox("Estreno",["Todos","Sin estrenar","Ya jugados"])
st.sidebar.markdown("---")
energia_opt=st.sidebar.radio("Energía de hoy",["Baja fricción","Rotar olvidados","Estrenar algo","Algo épico"],index=0)
st.sidebar.caption("Todos los paneles se actualizan con estos filtros.")

f=df.copy()
f=f[f["Tipo"].apply(lambda x: contains_type(x,tipo_opt))]
f=f[f["Jugadores"].apply(lambda x: player_match(x,jug_opt))]
if fric_opt!="Todos": f=f[f["Fricción para mesa"]==fric_opt]
if estreno_opt=="Sin estrenar": f=f[f["Partidas_num"]==0]
elif estreno_opt=="Ya jugados": f=f[f["Partidas_num"]>0]

ct,cu=st.columns([4,1])
with ct:
    st.markdown('<div style="display:flex;align-items:center;gap:16px;padding:8px 0 2px 0"><div style="font-size:44px">🎲</div><div><div class="title">LUDOTECA VIVA – TAZELO2010</div><div class="subtitle">Dashboard de tu colección</div></div></div>', unsafe_allow_html=True)
with cu:
    st.markdown(f"<div class='updated'>Actualizado:<br>{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>", unsafe_allow_html=True)

base_total=len(df); total=len(f)
competitivos=f["Tipo"].str.contains("Competitivo",case=False,na=False).sum()
cooperativos=f["Tipo"].str.contains("Cooperativo",case=False,na=False).sum()
campanias=f["Tipo"].str.contains("Campaña",case=False,na=False).sum()
party=f["Tipo"].str.contains("Party",case=False,na=False).sum()
sin_estrenar=(f["Partidas_num"]==0).sum()
alta=f["Fricción para mesa"].isin(["Alta","Muy alta"]).sum()
baja=(f["Fricción para mesa"]=="Baja").sum()
old=f[f["Ultima_dt"].notna() & (f["Ultima_dt"] < (pd.Timestamp.today()-pd.DateOffset(months=6)))]

m1,m2,m3,m4,m5=st.columns(5)
with m1: metric_card("▦","Juegos filtrados",total,f"de {base_total} en colección")
with m2: metric_card("⚔️","Competitivos",competitivos,f"{competitivos/total:.1%} del filtro" if total else "")
with m3: metric_card("🤝","Cooperativos",cooperativos,f"{cooperativos/total:.1%} del filtro" if total else "")
with m4: metric_card("🚩","Campañas",campanias,f"{campanias/total:.1%} del filtro" if total else "")
with m5: metric_card("🎉","Party",party,f"{party/total:.1%} del filtro" if total else "")

m6,m7,m8,m9,m10=st.columns(5)
with m6: metric_card("📅","Sin estrenar",sin_estrenar,f"{sin_estrenar/total:.1%} del filtro" if total else "")
with m7: metric_card("↻","Hace +6 meses",len(old),"Sin jugar en filtro")
with m8: metric_card("🔥","Alta fricción",alta,f"{alta/total:.1%} del filtro" if total else "")
with m9: metric_card("⚡","Baja fricción",baja,f"{baja/total:.1%} del filtro" if total else "")
with m10: metric_card("⭐","Favoritos",0,"Pendiente de valorar")

left,main=st.columns([1.05,4.25])
with left:
    st.markdown('<div class="recommend-card"><div class="recommend-title">✨ ¿QUÉ JUEGO SACO HOY?</div>', unsafe_allow_html=True)
    rec_pool=f.copy()
    if energia_opt=="Baja fricción":
        rec_pool=rec_pool[rec_pool["Fricción para mesa"].isin(["Baja","Media"])].copy()
        rec_pool["fr_rank"]=rec_pool["Fricción para mesa"].apply(friction_rank)
        rec_pool=rec_pool.sort_values(["fr_rank","Ultima_dt"],na_position="first")
    elif energia_opt=="Rotar olvidados":
        rec_pool=rec_pool.sort_values(["Ultima_dt","Partidas_num"],na_position="first")
    elif energia_opt=="Estrenar algo":
        rec_pool=rec_pool[rec_pool["Partidas_num"]==0].copy()
        rec_pool["fr_rank"]=rec_pool["Fricción para mesa"].apply(friction_rank)
        rec_pool=rec_pool.sort_values(["fr_rank","Nombre"])
    else:
        rec_pool=rec_pool[rec_pool["Fricción para mesa"].isin(["Media","Alta","Muy alta"])].sort_values(["Peso_num","Ultima_dt"],ascending=[False,True],na_position="last")
    if len(rec_pool):
        rec=rec_pool.iloc[0]
        st.markdown(f'<div class="recommend-game">{rec.get("Nombre","")}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="pill">{rec.get("Tipo","")}</span><span class="pill">{rec.get("Jugadores","")} jugadores</span><span class="pill">Fricción: {rec.get("Fricción para mesa","")}</span>', unsafe_allow_html=True)
        if rec.get("Motivo de fricción",""): st.caption(rec.get("Motivo de fricción",""))
    else:
        st.markdown('<div class="recommend-game">No hay candidatos</div>', unsafe_allow_html=True)
        st.caption("Probá aflojar algún filtro.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="tip">💡 Si el filtro deja pocos juegos, aflojá fricción o jugadores.</div>', unsafe_allow_html=True)

with main:
    c1,c2,c3=st.columns(3)
    with c1:
        panel("🆕 SIN ESTRENAR")
        x=f[f["Partidas_num"]==0].copy(); x["rank_fric"]=x["Fricción para mesa"].apply(friction_rank)
        show_table(x.sort_values(["rank_fric","Nombre"]).head(6),["Nombre","Tipo","Jugadores","Fricción para mesa"])
    with c2:
        panel("🔥 MENOS ROTADOS")
        show_table(f.sort_values(["Ultima_dt","Partidas_num"],na_position="first").head(6),["Nombre","Última partida","Tiempo desde última partida"])
    with c3:
        panel("✅ JUGADOS RECIENTEMENTE")
        show_table(f[f["Ultima_dt"].notna()].sort_values("Ultima_dt",ascending=False).head(6),["Nombre","Última partida","Fricción para mesa"])
    g1,g2,g3=st.columns(3)
    with g1:
        panel("📦 FRICCIÓN EN FILTRO")
        if len(f):
            fr=f["Fricción para mesa"].value_counts().reset_index(); fr.columns=["Fricción","Cantidad"]
            fig=px.pie(fr,names="Fricción",values="Cantidad",hole=.55,color="Fricción",color_discrete_map={"Baja":"#6bb24a","Media":"#f3b51b","Alta":"#f27b2a","Muy alta":"#ef4b3f"})
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),height=270,showlegend=True)
            st.plotly_chart(fig,use_container_width=True)
    with g2:
        panel("🎲 TIPO EN FILTRO")
        tipo_df=pd.DataFrame([{"Tipo":"Competitivo","Cantidad":competitivos},{"Tipo":"Cooperativo","Cantidad":cooperativos},{"Tipo":"Campaña","Cantidad":campanias},{"Tipo":"Party","Cantidad":party}])
        tipo_df=tipo_df[tipo_df["Cantidad"]>0]
        if len(tipo_df):
            fig=px.pie(tipo_df,names="Tipo",values="Cantidad",hole=.55,color="Tipo",color_discrete_map={"Competitivo":"#1e73be","Cooperativo":"#9b62d9","Campaña":"#f27b2a","Party":"#f3b51b"})
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),height=270,showlegend=True)
            st.plotly_chart(fig,use_container_width=True)
    with g3:
        panel("⚠️ ALTA FRICCIÓN / OBSERVAR")
        show_table(f[f["Fricción para mesa"].isin(["Alta","Muy alta"])].sort_values(["Ultima_dt"],na_position="first").head(6),["Nombre","Tipo","Última partida","Fricción para mesa"])

st.markdown('<div class="tip">⭐ Los filtros ahora afectan métricas, recomendación, tablas y gráficos.</div>', unsafe_allow_html=True)
