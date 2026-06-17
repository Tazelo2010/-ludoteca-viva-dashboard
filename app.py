
import re, random
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

SPREADSHEET_ID="19onyfrqnhTH4UeuMvDxgOnlemNa-SHdkz_wVlyEXyac"
SHEET_GID="1910202614"
CSV_URL=f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
BGG_URL="https://boardgamegeek.com/boardgame/"

st.set_page_config(page_title="Ludoteca Viva – Tazelo2010", page_icon="🎲", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp{background:#f7f5ef;color:#12342a}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#073f2f 0%,#0b5a42 100%)}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3,section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p,section[data-testid="stSidebar"] span{color:white!important}
section[data-testid="stSidebar"] div[data-baseweb="select"]{background:white!important;color:#12342a!important;border-radius:10px}
section[data-testid="stSidebar"] div[data-baseweb="select"] *{color:#12342a!important}
section[data-testid="stSidebar"] input{color:#12342a!important}
.title{font-size:36px;font-weight:950;color:#073f2f;letter-spacing:-.7px}
.subtitle{color:#0b5a42;font-size:17px;font-style:italic}
.updated{text-align:right;color:#073f2f;font-weight:750;font-size:13px}
.metric-card{background:#fffdf8;border:1px solid #e5ddcc;border-radius:17px;padding:15px;min-height:104px;box-shadow:0 4px 14px rgba(25,44,35,.08);display:flex;align-items:center;gap:13px}
.metric-icon{width:50px;height:50px;border-radius:50%;background:#eaf3e7;display:flex;align-items:center;justify-content:center;font-size:26px}
.metric-label{font-size:12px;font-weight:850;text-transform:uppercase;color:#0b5a42}
.metric-value{font-size:30px;font-weight:950;color:#073f2f;line-height:1.05}
.metric-note{font-size:12px;color:#6b756f;margin-top:3px}
.panel-header,.big-table-title{background:linear-gradient(90deg,#073f2f 0%,#0b5a42 100%);color:white;padding:11px 15px;font-weight:900;font-size:16px;border-radius:16px 16px 0 0;margin-top:12px}
.big-table-title{font-size:18px;margin-top:18px}
.recommend-card,.game-detail{background:#fffdf8;border:1px solid #e5ddcc;border-radius:17px;padding:16px;box-shadow:0 4px 14px rgba(25,44,35,.08)}
.recommend-card{text-align:center;margin-top:10px}
.recommend-title{font-size:13px;font-weight:900;color:#0b5a42;margin-bottom:8px;text-transform:uppercase}
.recommend-game{font-size:24px;font-weight:950;color:#073f2f;margin:12px 0 6px}
.pill{display:inline-block;background:#eaf3e7;border-radius:999px;padding:5px 10px;font-size:12px;color:#073f2f;font-weight:750;margin:3px}
.tip{background:#fff7df;border:1px solid #f0dfad;border-radius:14px;padding:12px 16px;color:#143d2e;font-weight:650;margin-top:10px}
div[data-testid="stDataFrame"]{border-radius:0 0 16px 16px;overflow:hidden;border:1px solid #e5ddcc}
.stButton>button{background:#073f2f;color:white;border:0;border-radius:12px;padding:.55rem .9rem;font-weight:800}
.stButton>button:hover{background:#0b5a42;color:white;border:0}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data():
    df=pd.read_csv(CSV_URL)
    df.columns=[c.strip() for c in df.columns]
    for col in ["Id BGG","Nombre","Tipo","Jugadores","Fricción para mesa","Motivo de fricción","Tiempo desde última partida","Notas","Puntuación BGG","Peso BGG"]:
        if col in df.columns:
            df[col]=df[col].fillna("").astype(str).str.strip()
    df["Partidas_num"]=pd.to_numeric(df.get("Partidas",0),errors="coerce").fillna(0).astype(int)
    df["Peso_num"]=pd.to_numeric(df.get("Peso BGG","").astype(str).str.replace(",",".",regex=False),errors="coerce") if "Peso BGG" in df.columns else pd.NA
    df["Rating_num"]=pd.to_numeric(df.get("Puntuación BGG","").astype(str).str.replace(",",".",regex=False),errors="coerce") if "Puntuación BGG" in df.columns else pd.NA
    df["Ultima_dt"]=pd.to_datetime(df.get("Última partida",""),errors="coerce") if "Última partida" in df.columns else pd.NaT
    df["BGG"]=df["Id BGG"].apply(lambda x:f"{BGG_URL}{x}" if str(x).strip() else "")
    return df

def parse_players(t):
    nums=[int(x) for x in re.findall(r"\d+",str(t))]
    return (None,None) if not nums else (nums[0],nums[-1])

def player_match(j,sel):
    if sel=="Todos": return True
    mn,mx=parse_players(j)
    return mn is not None and mn<=int(sel)<=mx

def contains_type(t,sel):
    return True if sel=="Todos" else sel.lower() in str(t).lower()

def friction_rank(v):
    return {"Baja":1,"Media":2,"Alta":3,"Muy alta":4}.get(str(v),9)

def metric_card(icon,label,value,note=""):
    st.markdown(f'<div class="metric-card"><div class="metric-icon">{icon}</div><div><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div></div>',unsafe_allow_html=True)

def panel(title):
    st.markdown(f'<div class="panel-header">{title}</div>',unsafe_allow_html=True)

def show_table(data,cols,height=250):
    cols=[c for c in cols if c in data.columns]
    st.dataframe(data[cols].copy(),use_container_width=True,hide_index=True,height=height)

def explain(row):
    parts=[]
    if row.get("Jugadores",""): parts.append(f"se juega a {row['Jugadores']}")
    if row.get("Fricción para mesa",""): parts.append(f"fricción {row['Fricción para mesa'].lower()}")
    if row.get("Tiempo desde última partida",""): parts.append(f"hace {row['Tiempo desde última partida']} que no sale")
    if row.get("Partidas_num",1)==0: parts.append("está sin estrenar")
    try:
        if not pd.isna(row.get("Rating_num")): parts.append(f"rating BGG {row['Rating_num']:.2f}")
    except Exception: pass
    return " · ".join(parts)

df=load_data()

st.sidebar.markdown("## 🎛️ Filtros")
busqueda=st.sidebar.text_input("Buscar juego","")
tipo_opt=st.sidebar.selectbox("Tipo",["Todos","Competitivo","Cooperativo","Campaña","Party"])
jug_opt=st.sidebar.selectbox("Jugadores",["Todos","1","2","3","4","5","6","7","8"])
fric_opt=st.sidebar.selectbox("Fricción",["Todos","Baja","Media","Alta","Muy alta"])
estreno_opt=st.sidebar.selectbox("Estreno",["Todos","Sin estrenar","Ya jugados"])
rotacion_opt=st.sidebar.selectbox("Rotación",["Todos","Jugados recientemente","Hace +6 meses","Hace +1 año","Nunca jugados"])
peso_opt=st.sidebar.selectbox("Peso BGG",["Todos","Liviano ≤2.0","Medio 2.1–3.0","Pesado 3.1–4.0","Muy pesado >4.0"])
st.sidebar.markdown("---")
modo=st.sidebar.radio("Modo recomendación",["Baja energía","Con Javi","Estrenar algo","Rotar olvidado","Algo épico","Azar puro"],index=0)

f=df.copy()
if busqueda: f=f[f["Nombre"].str.contains(busqueda,case=False,na=False)]
f=f[f["Tipo"].apply(lambda x:contains_type(x,tipo_opt))]
f=f[f["Jugadores"].apply(lambda x:player_match(x,jug_opt))]
if fric_opt!="Todos": f=f[f["Fricción para mesa"]==fric_opt]
if estreno_opt=="Sin estrenar": f=f[f["Partidas_num"]==0]
elif estreno_opt=="Ya jugados": f=f[f["Partidas_num"]>0]
if rotacion_opt=="Jugados recientemente": f=f[f["Ultima_dt"].notna()].sort_values("Ultima_dt",ascending=False).head(25)
elif rotacion_opt=="Hace +6 meses": f=f[f["Ultima_dt"].notna()&(f["Ultima_dt"]<(pd.Timestamp.today()-pd.DateOffset(months=6)))]
elif rotacion_opt=="Hace +1 año": f=f[f["Ultima_dt"].notna()&(f["Ultima_dt"]<(pd.Timestamp.today()-pd.DateOffset(years=1)))]
elif rotacion_opt=="Nunca jugados": f=f[f["Partidas_num"]==0]
if peso_opt=="Liviano ≤2.0": f=f[f["Peso_num"]<=2.0]
elif peso_opt=="Medio 2.1–3.0": f=f[(f["Peso_num"]>2.0)&(f["Peso_num"]<=3.0)]
elif peso_opt=="Pesado 3.1–4.0": f=f[(f["Peso_num"]>3.0)&(f["Peso_num"]<=4.0)]
elif peso_opt=="Muy pesado >4.0": f=f[f["Peso_num"]>4.0]

ct,cu=st.columns([4,1])
with ct:
    st.markdown('<div style="display:flex;align-items:center;gap:16px;padding:8px 0 2px"><div style="font-size:46px">🎲</div><div><div class="title">LUDOTECA VIVA – TAZELO2010</div><div class="subtitle">Tu planilla, pero con una interfaz linda para decidir qué jugar</div></div></div>',unsafe_allow_html=True)
with cu:
    st.markdown(f"<div class='updated'>Actualizado:<br>{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>",unsafe_allow_html=True)

base_total=len(df); total=len(f)
competitivos=f["Tipo"].str.contains("Competitivo",case=False,na=False).sum()
cooperativos=f["Tipo"].str.contains("Cooperativo",case=False,na=False).sum()
campanias=f["Tipo"].str.contains("Campaña",case=False,na=False).sum()
party=f["Tipo"].str.contains("Party",case=False,na=False).sum()
sin_estrenar=(f["Partidas_num"]==0).sum()
alta=f["Fricción para mesa"].isin(["Alta","Muy alta"]).sum()
baja=(f["Fricción para mesa"]=="Baja").sum()
old_6=f[f["Ultima_dt"].notna()&(f["Ultima_dt"]<(pd.Timestamp.today()-pd.DateOffset(months=6)))]

m1,m2,m3,m4,m5=st.columns(5)
with m1: metric_card("▦","Juegos filtrados",total,f"de {base_total} en colección")
with m2: metric_card("⚔️","Competitivos",competitivos,f"{competitivos/total:.1%} del filtro" if total else "")
with m3: metric_card("🤝","Cooperativos",cooperativos,f"{cooperativos/total:.1%} del filtro" if total else "")
with m4: metric_card("🚩","Campañas",campanias,f"{campanias/total:.1%} del filtro" if total else "")
with m5: metric_card("🎉","Party",party,f"{party/total:.1%} del filtro" if total else "")
m6,m7,m8,m9,m10=st.columns(5)
with m6: metric_card("🆕","Sin estrenar",sin_estrenar,f"{sin_estrenar/total:.1%} del filtro" if total else "")
with m7: metric_card("↻","Hace +6 meses",len(old_6),"Sin salir a mesa")
with m8: metric_card("🔥","Alta fricción",alta,f"{alta/total:.1%} del filtro" if total else "")
with m9: metric_card("⚡","Baja fricción",baja,f"{baja/total:.1%} del filtro" if total else "")
with m10: metric_card("⭐","Rating prom.",f"{f['Rating_num'].mean():.2f}" if total and f["Rating_num"].notna().any() else "–","BGG")

def candidate_pool(current,selected_mode):
    pool=current.copy()
    if selected_mode=="Baja energía":
        pool=pool[pool["Fricción para mesa"].isin(["Baja","Media"])].copy()
        pool["fr_rank"]=pool["Fricción para mesa"].apply(friction_rank)
        pool=pool.sort_values(["fr_rank","Ultima_dt","Partidas_num"],na_position="first")
    elif selected_mode=="Con Javi":
        pool=pool[pool["Jugadores"].apply(lambda x:player_match(x,"2"))].copy()
        pool=pool[pool["Fricción para mesa"].isin(["Baja","Media"])].copy()
        pool["fr_rank"]=pool["Fricción para mesa"].apply(friction_rank)
        pool=pool.sort_values(["fr_rank","Ultima_dt","Rating_num"],ascending=[True,True,False],na_position="first")
    elif selected_mode=="Estrenar algo":
        pool=pool[pool["Partidas_num"]==0].copy()
        pool["fr_rank"]=pool["Fricción para mesa"].apply(friction_rank)
        pool=pool.sort_values(["fr_rank","Rating_num"],ascending=[True,False],na_position="last")
    elif selected_mode=="Rotar olvidado":
        pool=pool.sort_values(["Ultima_dt","Partidas_num"],ascending=[True,True],na_position="first")
    elif selected_mode=="Algo épico":
        pool=pool[pool["Fricción para mesa"].isin(["Media","Alta","Muy alta"])].copy()
        pool=pool.sort_values(["Rating_num","Peso_num"],ascending=[False,False],na_position="last")
    elif selected_mode=="Azar puro" and len(pool):
        pool=pool.sample(frac=1,random_state=random.randint(1,1000000))
    return pool

left,right=st.columns([1.1,3.9])
with left:
    st.markdown('<div class="recommend-card"><div class="recommend-title">✨ Recomendación del filtro</div>',unsafe_allow_html=True)
    rec_pool=candidate_pool(f,modo)
    if len(rec_pool):
        rec=rec_pool.iloc[0]
        st.markdown(f'<div class="recommend-game">{rec.get("Nombre","")}</div>',unsafe_allow_html=True)
        st.markdown(f'<span class="pill">{rec.get("Tipo","")}</span><span class="pill">{rec.get("Jugadores","")}</span><span class="pill">Fricción: {rec.get("Fricción para mesa","")}</span>',unsafe_allow_html=True)
        st.caption(explain(rec))
        if rec.get("BGG"): st.link_button("Abrir en BGG",rec["BGG"])
    else:
        st.markdown('<div class="recommend-game">No hay candidato</div>',unsafe_allow_html=True)
        st.caption("Aflojá algún filtro.")
    st.markdown("</div>",unsafe_allow_html=True)
with right:
    st.markdown('<div class="tip">Usá los filtros de la izquierda como una planilla viva. La tabla principal muestra todos los juegos filtrados.</div>',unsafe_allow_html=True)
    b1,b2,b3,b4,b5,b6=st.columns(6)
    for col,label,mode in [(b1,"🎲 Azar","Azar puro"),(b2,"👥 Con Javi","Con Javi"),(b3,"⚡ Baja energía","Baja energía"),(b4,"🆕 Estrenar","Estrenar algo"),(b5,"🔥 Olvidado","Rotar olvidado"),(b6,"🏰 Épico","Algo épico")]:
        with col:
            if st.button(label):
                tmp=candidate_pool(f,mode)
                if len(tmp): st.toast(tmp.iloc[0]["Nombre"])

st.markdown(f'<div class="big-table-title">🎲 TODOS LOS JUEGOS FILTRADOS ({len(f)})</div>',unsafe_allow_html=True)
main_cols=["Nombre","Id BGG","BGG","Tipo","Jugadores","Puntuación BGG","Peso BGG","Partidas","Última partida","Tiempo desde última partida","Fricción para mesa","Motivo de fricción","Notas"]
main_df=f[[c for c in main_cols if c in f.columns]].copy()
if "Fricción para mesa" in main_df.columns:
    main_df["Orden fricción"]=main_df["Fricción para mesa"].apply(friction_rank)
    main_df=main_df.sort_values(["Orden fricción","Nombre"]).drop(columns=["Orden fricción"])
st.dataframe(main_df,use_container_width=True,hide_index=True,height=460,column_config={"BGG":st.column_config.LinkColumn("BGG",display_text="Abrir"),"Notas":st.column_config.TextColumn("Notas",width="large"),"Motivo de fricción":st.column_config.TextColumn("Motivo",width="large")})

st.markdown('<div class="big-table-title">🧩 FICHA RÁPIDA DEL JUEGO</div>',unsafe_allow_html=True)
if len(f):
    selected_name=st.selectbox("Elegí un juego del filtro actual",f["Nombre"].tolist())
    selected=f[f["Nombre"]==selected_name].iloc[0]
    d1,d2,d3=st.columns([1.2,1.2,2.6])
    with d1:
        st.markdown('<div class="game-detail">',unsafe_allow_html=True)
        st.subheader(selected.get("Nombre",""))
        st.write(f"**BGG ID:** {selected.get('Id BGG','')}")
        st.write(f"**Tipo:** {selected.get('Tipo','')}")
        st.write(f"**Jugadores:** {selected.get('Jugadores','')}")
        st.write(f"**Fricción:** {selected.get('Fricción para mesa','')}")
        if selected.get("BGG"): st.link_button("Abrir en BoardGameGeek",selected["BGG"])
        st.markdown("</div>",unsafe_allow_html=True)
    with d2:
        st.markdown('<div class="game-detail">',unsafe_allow_html=True)
        st.write(f"**Rating BGG:** {selected.get('Puntuación BGG','')}")
        st.write(f"**Peso BGG:** {selected.get('Peso BGG','')}")
        st.write(f"**Partidas:** {selected.get('Partidas','')}")
        st.write(f"**Última partida:** {selected.get('Última partida','')}")
        st.write(f"**Hace:** {selected.get('Tiempo desde última partida','')}")
        st.markdown("</div>",unsafe_allow_html=True)
    with d3:
        st.markdown('<div class="game-detail">',unsafe_allow_html=True)
        st.write("**Motivo de fricción**")
        st.write(selected.get("Motivo de fricción","") or "Sin motivo registrado.")
        st.write("**Notas**")
        st.write(selected.get("Notas","") or "Sin notas registradas.")
        st.write("**Por qué podría salir hoy**")
        st.write(explain(selected) or "No hay suficiente información.")
        st.markdown("</div>",unsafe_allow_html=True)

c1,c2,c3=st.columns(3)
with c1:
    panel("🆕 Sin estrenar en filtro")
    x=f[f["Partidas_num"]==0].copy()
    if len(x):
        x["rank_fric"]=x["Fricción para mesa"].apply(friction_rank)
        show_table(x.sort_values(["rank_fric","Nombre"]).head(8),["Nombre","Tipo","Jugadores","Fricción para mesa"],270)
    else: st.info("No hay juegos sin estrenar.")
with c2:
    panel("🔥 Menos rotados")
    show_table(f.sort_values(["Ultima_dt","Partidas_num"],na_position="first").head(8),["Nombre","Última partida","Tiempo desde última partida","Fricción para mesa"],270)
with c3:
    panel("✅ Jugados recientemente")
    show_table(f[f["Ultima_dt"].notna()].sort_values("Ultima_dt",ascending=False).head(8),["Nombre","Última partida","Fricción para mesa"],270)

g1,g2,g3=st.columns(3)
with g1:
    panel("📦 Fricción")
    if len(f):
        fr=f["Fricción para mesa"].value_counts().reset_index(); fr.columns=["Fricción","Cantidad"]
        fig=px.pie(fr,names="Fricción",values="Cantidad",hole=.55,color="Fricción",color_discrete_map={"Baja":"#6bb24a","Media":"#f3b51b","Alta":"#f27b2a","Muy alta":"#ef4b3f"})
        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),height=270,showlegend=True)
        st.plotly_chart(fig,use_container_width=True)
with g2:
    panel("🎲 Tipo")
    if len(f):
        tipo_df=pd.DataFrame([{"Tipo":"Competitivo","Cantidad":competitivos},{"Tipo":"Cooperativo","Cantidad":cooperativos},{"Tipo":"Campaña","Cantidad":campanias},{"Tipo":"Party","Cantidad":party}])
        tipo_df=tipo_df[tipo_df["Cantidad"]>0]
        if len(tipo_df):
            fig=px.pie(tipo_df,names="Tipo",values="Cantidad",hole=.55,color="Tipo",color_discrete_map={"Competitivo":"#1e73be","Cooperativo":"#9b62d9","Campaña":"#f27b2a","Party":"#f3b51b"})
            fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),height=270,showlegend=True)
            st.plotly_chart(fig,use_container_width=True)
with g3:
    panel("⚠️ Alta fricción")
    show_table(f[f["Fricción para mesa"].isin(["Alta","Muy alta"])].sort_values(["Ultima_dt"],na_position="first").head(8),["Nombre","Tipo","Última partida","Fricción para mesa"],270)

st.markdown('<div class="tip">La Google Sheet sigue siendo la fuente de verdad. Si cambiás datos en la planilla, la app los toma al refrescar o en pocos minutos.</div>',unsafe_allow_html=True)
