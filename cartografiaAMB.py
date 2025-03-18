import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import pydeck as pdk
import time
from dateutil.relativedelta import relativedelta

st.set_page_config(
    layout="wide",
)
#Dimensiones de pagina y contenedores, tipo de letra, margenes
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100px 
            background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
        }
    
        .stAppHeader {
            font-size: 10px;  /* Tamaño del título */
            background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
            visibility: visible;  /* Ensure the header is visible */
        }

         .block-container {
             margin:1rem;
             padding-top: 0rem;
             padding-bottom: 0rem;
        #     padding-left: 5rem;
        #     padding-right: 5rem;
        # }

        
        /* Modificar el tamaño de los checkboxes en el multiselect */
        div[data-baseweb="checkbox"] {
            transform: scale(0.5);  /* Ajusta el tamaño */
        }
    
        h1 {
            text-align: center;  
        }
         h4 {
            text-align: center;  
        }
         h5 {
            text-align: center;  
        }
    </style>
    """, unsafe_allow_html=True,
)
# Defición de funcion que accede a la base de datos y corre una consulta
def run_query(query):
    df = pd.read_sql(query, con=engine)
    return df

# coneccion a la base de datos
engine = create_engine(f"postgresql://postgres.spdwbcfeoefxnlfdhlgi:chatbot2025@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")

# consulta para contador de descargas y usuarios
query_descargas = """
WITH descargas_mes_actual AS (
    SELECT 
        COUNT(*) AS total_descargas,
        DATE_TRUNC('month', fechadescarga) AS mes
    FROM descargas
    WHERE fechadescarga >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
      AND fechadescarga < DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY mes
),
descargas_mes_anterior AS (
    SELECT 
        COUNT(*) AS total_descargas,
        DATE_TRUNC('month', fechadescarga) AS mes
    FROM descargas
    WHERE fechadescarga >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '2 months'
      AND fechadescarga < DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
    GROUP BY mes
),
usuarios_nuevos_mes_actual AS (
    SELECT 
        COUNT(*) AS nuevos_usuarios,
        DATE_TRUNC('month', fechaalta) AS mes
    FROM usuarios
    WHERE fechaalta >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
      AND fechaalta < DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY mes
),
total_usuarios AS (
    SELECT 
        COUNT(*) AS total_usuarios
    FROM usuarios
),
total_descargas_historico AS (
    SELECT 
        COUNT(*) AS total_descargas_historicas
    FROM descargas
)
SELECT 
    dm.total_descargas AS descargas_actuales,
    COALESCE(da.total_descargas, 0) AS descargas_pasadas,
    um.nuevos_usuarios,
    tu.total_usuarios,
    td.total_descargas_historicas
FROM descargas_mes_actual dm
LEFT JOIN descargas_mes_anterior da ON dm.mes = da.mes + INTERVAL '1 month'
LEFT JOIN usuarios_nuevos_mes_actual um ON dm.mes = um.mes
CROSS JOIN total_usuarios tu
CROSS JOIN total_descargas_historico td;

"""
df_descargas = run_query(query_descargas)

# Extraer valores
descargas_actuales = df_descargas['descargas_actuales'][0]
descargas_pasadas = df_descargas['descargas_pasadas'][0]
nuevos_usuarios = df_descargas['nuevos_usuarios'][0]
usuarios_totales = df_descargas['total_usuarios'][0]
descargas_totales= df_descargas['total_descargas_historicas'][0]

# Calcular delta de descargas
delta_descargas = descargas_actuales - descargas_pasadas

# Función para obtener datos de clicks desde PostgreSQL
click_data= """SELECT lat, lon FROM public.click WHERE lat IS NOT NULL AND lon IS NOT NULL AND fecha >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month' AND fecha < DATE_TRUNC('month', CURRENT_DATE);"""
    
# Obtener datos
df_clicks = run_query(click_data)



st.logo("Imagenes/amb.png")
st.title("Anàlisi de Dades Geoportal Cartografia AMB")
#col4, col5 = st.columns ([5,3])
#col4.title("Anàlisi de Dades Geoportal Cartografia AMB")
# Mostrar la imagen
#col5.image("Imagenes/Portal.png")
cola, colb = st.columns([1, 4])  # Ajusta los tamaños relativos de las columnas

#with colc:
   # st.image("Imagenes/Portal.png", width=500)  # Fija el ancho de la imagen

with st.sidebar:
    st.image("Imagenes/Portal.png", width=250)  # Ancho fijo para evitar cambios bruscos

with cola:
    #st.image("Imagenes/Portal.png", width=500)  # Fija el ancho de la imagen
    st.metric("Descàrregues aquest mes", f"{descargas_actuales}", f"{delta_descargas} que el mes passat ")
    st.write("")
    st.metric("Descàrregues totals", f"{descargas_totales}")
    st.write("")
    st.metric("Usuaris", f"{usuarios_totales} totals", f"{nuevos_usuarios} nous aquest mes")

with colb:
    st.map(df_clicks)  # Tamaño fijo del mapa
    st.markdown("Clicks aquest mes")


#st.subheader("Descarrègues de tots els productes")
#Metricas de contador de descaras y de usuarios
#col1, col2, col3= st.columns(3)
# Métrica principal
#col1.metric("Descàrregues aquest mes", f"{descargas_actuales}", f"{delta_descargas} que el mes passat ")
#col2.metric("Descàrregues totals", f"{descargas_totales}")
#col3.metric("Usuaris", f"{usuarios_totales}totales", f"{nuevos_usuarios} nous aquest mes")
st.write("")
st.write("")
st.write("")  # Esto agrega un espacio vacío
st.subheader("Descarrègues de Mapa topogràfic metropolitá 1:1000")

# Obtener lista de meses disponibles, para el desplegable de opciones
query_meses = """
SELECT DISTINCT DATE_TRUNC('month', fechadescarga) AS mes
FROM descargas
ORDER BY mes DESC;
"""
df_meses = run_query(query_meses)
meses_disponibles = df_meses['mes'].dt.strftime('%Y-%m').tolist()

#Crea un desplegable para seleccionar el mes a visualizar
selected_month = st.selectbox(
    "Seleccionar mes", meses_disponibles, index=0,
    key="selected_month")


query_mapa = f"""
SELECT 
    COUNT(d.idfull) AS num_descargas,
    ST_X(ST_Transform(ST_Centroid(i.geom), 4326)) AS lon,
    ST_Y(ST_Transform(ST_Centroid(i.geom), 4326)) AS lat
FROM 
    descargas d
JOIN 
    fulls i ON d.idfull = i.idfull
WHERE 
    fechadescarga >= ('{selected_month}-01 00:00:00'::DATE - INTERVAL '1 month')  
    AND fechadescarga < '{selected_month}-01 00:00:00'  
    AND d.nomproducte = 'MTM 1000'
GROUP BY 
    i.geom;
"""

def map(df):
    if df.empty:
        st.warning("No hay datos disponibles para este mes.")
        return

    # Normalizar datos para altura de barras
    df['elevation'] = df['num_descargas'] / df['num_descargas'].max() * 1000

    # Definir el polígono del AMB
    #amb_polygon = [[
        #[2.0087, 41.5500], [2.1500, 41.6200], [2.4000, 41.5000],
        #[2.4500, 41.3500], [2.3500, 41.2500], [2.1000, 41.2000],
        #[2.0000, 41.2500], [1.9500, 41.4000], [2.0087, 41.5500]
    #s]]

    #df_polygon = pd.DataFrame({"geometry": [amb_polygon]})

   # polygon_layer = pdk.Layer(
        #"PolygonLayer",
        #df_polygon,
        #get_polygon="geometry",
        #get_fill_color=[255, 0, 0, 50],
        #get_line_color=[255, 0, 0, 255],
        #line_width_min_pixels=2,
        #pickable=True
   # )

    layer_MTM = pdk.Layer(
        "GridLayer",
        df,
        get_position=["lon", "lat"],
        extruded=True,
        pickable=True,
        cell_size=700,
        elevation_scale=4,
        color_range=[[0, 0, 255, 100]]
    )

    view_state = pdk.ViewState(
        latitude=41.3874, longitude=2.1686, zoom=10, pitch=60
    )

    deck = pdk.Deck(
        layers=[layer_MTM],#, spolygon_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/light-v9"
    )

    st.pydeck_chart(deck)

# Obtener datos y mostrar mapa
df = run_query(query_mapa)
map(df)

