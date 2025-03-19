import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración de la página
st.set_page_config(layout="wide")

# Estilos CSS personalizados
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
    
        h2 {
            text-align: center;  
        }

        h3 {
            text-align: center;  
        }
        h5 {
            text-align: center;  
        }
    </style>
        """, unsafe_allow_html=True,
)

# Función para ejecutar consultas SQL
def run_query(query):
    df = pd.read_sql(query, con=engine)
    return df

# Conexión a la base de datos
engine = create_engine(f"postgresql://postgres.spdwbcfeoefxnlfdhlgi:chatbot2025@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")

# Título de la aplicación
st.title("📈 Tendències i Patrons")


# Consulta SQL para obtener los datos
query = """
WITH productos_top AS (
    SELECT u.nomambito, d.nomproducte, COUNT(*) AS total_descargas,
           RANK() OVER (PARTITION BY u.nomambito ORDER BY COUNT(*) DESC) AS ranking
    FROM public.descargas d
    JOIN public.usuarios u ON d.usuario = u.usuario
    GROUP BY u.nomambito, d.nomproducte
)
SELECT p.nomambito, p.nomproducte AS top_producte, p.total_descargas
FROM productos_top p
WHERE p.ranking <= 3
ORDER BY p.nomambito, p.ranking;
"""
df = run_query(query)

# Verificar si hay datos
if not df.empty:
    # Primera gráfica: Seleccionar producto y mostrar ámbitos
    st.subheader("Distribución de descargas por ámbito para un producto seleccionado")
    
    # Selector de producto
    productos = df['top_producte'].unique()
    producto_seleccionado = st.selectbox("Selecciona un producto", productos)

    # Filtrar datos para el producto seleccionado
    df_filtrado = df[df['top_producte'] == producto_seleccionado]

    # Ordenar los valores de mayor a menor
    df_filtrado = df_filtrado.sort_values(by='total_descargas', ascending=False)

    # Calcular el porcentaje de cada ámbito
    total_descargas = df_filtrado['total_descargas'].sum()
    df_filtrado['porcentaje'] = (df_filtrado['total_descargas'] / total_descargas) * 100

    # Agrupar valores menores al 3% en "Otros"
    df_filtrado['categoria'] = df_filtrado['nomambito']
    df_filtrado.loc[df_filtrado['porcentaje'] < 3, 'categoria'] = 'Otros'

    # Agrupar los datos
    df_agrupado = df_filtrado.groupby('categoria', as_index=False).agg({
        'total_descargas': 'sum',
        'porcentaje': 'sum'
    })

    # Seleccionar paleta de colores
    paleta_colores = st.sidebar.selectbox(
        "Selecciona una paleta de colores",
        options=["viridis", "dark", "magma", "pastel", "icefire", "rocket"]
    )
    colores = sns.color_palette(paleta_colores, len(df_agrupado))

    # Selector de tipo de fuente
    font_type = st.sidebar.selectbox(
        "Selecciona el tipo de fuente",
        options=["serif", "sans-serif", "monospace"]
    )

    # Selector de color de los porcentajes
    porcentaje_color = st.sidebar.color_picker("Selecciona el color de los porcentajes", "#000000")

    # Crear el gráfico de dona
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        df_agrupado['total_descargas'],
        labels=df_agrupado['categoria'],
        autopct=lambda p: f'{p:.1f}%' if p >= 3 else '',  # Mostrar porcentaje solo si es >= 3%
        startangle=90,
        colors=colores,
        pctdistance=0.85,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}  # Borde blanco entre categorías
    )

    # Añadir un círculo blanco en el centro para convertir el gráfico en una dona
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig.gca().add_artist(centre_circle)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Personalizar las etiquetas (labels)
    for text in texts:
        text.set_fontfamily(font_type)
        text.set_color("black")  # Las etiquetas siempre son negras

    # Personalizar los porcentajes (autotexts)
    for autotext in autotexts:
        autotext.set_fontfamily(font_type)
        autotext.set_color(porcentaje_color)  # Color personalizado para los porcentajes

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Segunda gráfica: Seleccionar ámbito y mostrar productos descargados
    st.subheader("Distribución de descargas de productos para un ámbito seleccionado")
    
    # Selector de ámbito profesional
    ambitos = df['nomambito'].unique()
    ambito_seleccionado = st.selectbox("Selecciona un ámbito profesional", ambitos)

    # Filtrar datos para el ámbito seleccionado
    df_filtrado_ambito = df[df['nomambito'] == ambito_seleccionado]

    # Ordenar los valores de mayor a menor
    df_filtrado_ambito = df_filtrado_ambito.sort_values(by='total_descargas', ascending=False)

    # Calcular el porcentaje de cada producto
    total_descargas_ambito = df_filtrado_ambito['total_descargas'].sum()
    df_filtrado_ambito['porcentaje'] = (df_filtrado_ambito['total_descargas'] / total_descargas_ambito) * 100

    # Agrupar valores menores al 3% en "Otros"
    df_filtrado_ambito['categoria'] = df_filtrado_ambito['top_producte']
    df_filtrado_ambito.loc[df_filtrado_ambito['porcentaje'] < 3, 'categoria'] = 'Otros'

    # Agrupar los datos
    df_agrupado_ambito = df_filtrado_ambito.groupby('categoria', as_index=False).agg({
        'total_descargas': 'sum',
        'porcentaje': 'sum'
    })

    # Crear el gráfico de dona para el ámbito seleccionado
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    wedges2, texts2, autotexts2 = ax2.pie(
        df_agrupado_ambito['total_descargas'],
        labels=df_agrupado_ambito['categoria'],
        autopct=lambda p: f'{p:.1f}%' if p >= 3 else '',  # Mostrar porcentaje solo si es >= 3%
        startangle=90,
        colors=colores,
        pctdistance=0.85,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}  # Borde blanco entre categorías
    )

    # Añadir un círculo blanco en el centro para convertir el gráfico en una dona
    centre_circle2 = plt.Circle((0, 0), 0.70, fc='white')
    fig2.gca().add_artist(centre_circle2)
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Personalizar las etiquetas (labels)
    for text in texts2:
        text.set_fontfamily(font_type)
        text.set_color("black")  # Las etiquetas siempre son negras

    # Personalizar los porcentajes (autotexts)
    for autotext in autotexts2:
        autotext.set_fontfamily(font_type)
        autotext.set_color(porcentaje_color)  # Color personalizado para los porcentajes

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig2)
else:
    st.warning("No hi ha dades disponibles per mostrar el gràfic.")

query_idioma = """
SELECT d.idproducto, d.nomproducte, u.ididioma, f.geometria
FROM descargas d
JOIN usuarios u ON d.usuario = u.usuario
JOIN fulls f ON d.fulls = f.idfull
"""
df_idioma= run_querry(query_idioma)

# Selección de idioma
idiomas_disponibles = df_idioma["ididioma"].unique()
idioma_seleccionado = st.selectbox("Selecciona un idioma:", idiomas_disponibles)

# Filtrar datos por idioma seleccionado
df_filtrado = df_idioma[df_idioma["ididioma"] == idioma_seleccionado]

# Crear mapa
st.subheader(f"🗺️ Mapa de descargas para el idioma: {idioma_seleccionado}")
m = folium.Map(location=[41.3879, 2.16992], zoom_start=10)  # Centrado en Barcelona

# Agregar puntos de descargas al mapa
for _, row in df_filtrado.iterrows():
    folium.Marker(
        location=[row["geometria"].centroid.y, row["geometria"].centroid.x],
        popup=f"{row['nomproducte']}",
        icon=folium.Icon(color="blue", icon="cloud")
    ).add_to(m)

# Mostrar mapa en Streamlit
folium_static(m)

# Mostrar tabla de datos
st.subheader("📊 Datos de descargas")
st.dataframe(df_filtrado)












with st.sidebar:
    st.image("Imagenes/Portal.png")  
