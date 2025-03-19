import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



st.set_page_config(
    layout="wide",
)

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
             padding-left: 5rem;
             padding-right: 5rem;
         }

        
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

st.header("👩 Dones")

def run_query(query):
    df = pd.read_sql(query, con=engine)
    return df

engine = create_engine(f"postgresql://postgres.spdwbcfeoefxnlfdhlgi:chatbot2025@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")

query_usuarios= """
WITH total AS (
        SELECT COUNT(*) AS total_usuarios FROM public.usuarios
    )
    SELECT
        u.genero AS genere,
        COUNT(*) AS total_usuaris,
        ROUND((COUNT(*) * 100.0 / t.total_usuarios), 2) AS percentatge
    FROM public.usuarios u, total t
    GROUP BY u.genero, t.total_usuarios
    ORDER BY percentatge DESC
"""
query_descargas= """
    SELECT 
            u.genero,
            COUNT(d.id) AS total_descargas
        FROM public.descargas d
        JOIN public.usuarios u ON d.usuario = u.usuario
        WHERE u.genero IN ('Hombre', 'Mujer', 'Otros')
        GROUP BY u.genero
        ORDER BY total_descargas DESC;
"""

df_usuarios= run_query(query_usuarios)
df_descargas= run_query(query_descargas)

# Agrupar 'No se recoge' y 'No respondido' en 'No especificado'
df_usuarios['genere'] = df_usuarios['genere'].replace({'No se recoge': 'No especificado', 'No respondido': 'No especificado'})

# Sumar valores por categoría
df_grouped = df_usuarios.groupby('genere', as_index=False).sum()

# Calcular el porcentaje de usuarios mujeres sobre quienes reportaron género
usuarios_reportaron_genere= df_grouped[df_grouped['genere'].isin(['Hombre', 'Mujer', 'Otros'])]['total_usuaris'].sum()
porcentaje_mujeres = (df_grouped[df_grouped['genere'] == 'Mujer']['total_usuaris'].values[0] / usuarios_reportaron_genere) * 100

# Crear nueva columna con el porcentaje sobre quienes reportaron género
total_reportaron_genero = df_grouped[df_grouped['genere'].isin(['Hombre', 'Mujer', 'Otros'])]['total_usuaris'].sum()
df_grouped['percentatge_reportado'] = df_grouped['total_usuaris'] / total_reportaron_genero * 100
df_grouped_reportado= df_grouped.drop(df_grouped[df_grouped['genere']== 'No especificado'].index)
#calculos para el % de descagas de mujeres
total_descargas = df_descargas['total_descargas'].sum()
descargas_mujeres = df_descargas[df_descargas['genero'] == 'Mujer']['total_descargas'].values[0]
proporcion_mujeres = (descargas_mujeres / total_descargas)*100

#st.subheader("Porcentatge d´usuaris per sexe")
st.subheader( f"Les donas representen el {porcentaje_mujeres:.1f}% dels usuaris que van reportar gènere y realizan el {proporcion_mujeres:.1f}% de las descargas")

col1,col2= st.columns(2)
# Crear gráfico de pastel
with col1:
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(df_grouped_reportado['percentatge_reportado'], labels=df_grouped_reportado['genere'], autopct='%1.1f%%', startangle=90, colors =sns.color_palette(palette='Pastel1'))
    ax.set_title("Usuarios por género excluyendo no reportados")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(df_grouped['percentatge'], labels=df_grouped['genere'], autopct='%1.1f%%', startangle=90)
    ax.set_title("Porcentaje de usuarios por género reportado")
    st.pyplot(fig)

st.subheader("Descargues de dones per Ámbito")

query_donas = """
SELECT 
    u.nomambito, 
    COUNT(d.id) AS total_descargas_mujer, 
    (COUNT(d.id) * 100.0 / NULLIF(td.total_descargas, 0)) AS porcentaje_descargas_mujer 
FROM 
    public.descargas d 
JOIN 
    public.usuarios u 
    ON d.usuario = u.usuario 
JOIN 
    (
        SELECT 
            u.nomambito, 
            COUNT(d.id) AS total_descargas 
        FROM 
            public.descargas d 
        JOIN 
            public.usuarios u 
            ON d.usuario = u.usuario 
        WHERE 
            u.genero NOT IN ('No respondido', 'No se recoge') 
        GROUP BY 
            u.nomambito
    ) td 
    ON u.nomambito = td.nomambito 
WHERE 
    u.genero = 'Mujer' 
GROUP BY 
    u.nomambito, 
    td.total_descargas 
ORDER BY 
    total_descargas_mujer ASC;
"""
df_donas = run_query(query_donas)

# Ordenar los datos de menor a mayor porcentaje
df_donas = df_donas.sort_values(by="porcentaje_descargas_mujer", ascending=True)

# Configurar la figura del gráfico
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={'projection': 'polar'})

# Configurar la orientación del gráfico
ax.set_theta_zero_location('N')  # El punto cero está en la parte superior
ax.set_theta_direction(1)  # Dirección de las barras en sentido horario
ax.set_rlabel_position(0)
ax.set_thetagrids([], labels=[])  # Oculta las líneas de referencia de ángulo
ax.set_rgrids(range(len(df_donas)), labels=df_donas["nomambito"])  # Etiquetas de categorías en el eje radial

# Asignar colores a las categorías
colors = plt.cm.viridis(np.linspace(0, 1, len(df_donas)))

# Graficar las barras circulares
for i, (descarga, ambito, color) in enumerate(zip(df_donas["porcentaje_descargas_mujer"], df_donas["nomambito"], colors)):
    ax.barh(i, descarga * 2 * np.pi / 100, label=ambito, color=color)

# Agregar leyenda
plt.legend(bbox_to_anchor=(1, 1), loc=2)



st.header("")
st.header("")

# Calcular porcentajes de hombres (asumimos que el resto de descargas no son de mujeres)
df_donas["porcentaje_descargas_otros"] = 100 - df_donas["porcentaje_descargas_mujer"]

def plot_bar_chart():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Crear las barras apiladas
    ax.bar(df_donas["nomambito"], df_donas["porcentaje_descargas_mujer"], color="red", label="Descargas por mujeres")
    ax.bar(df_donas["nomambito"], df_donas["porcentaje_descargas_otros"], color="gray", alpha=0.6, label="", bottom=df_donas["porcentaje_descargas_mujer"])
    
    # Etiquetas y título
    ax.set_ylabel("Porcentaje (%)")
    ax.set_xticklabels(df_donas["nomambito"], rotation=90)
    ax.set_title("Porcentaje de Descargas por Ámbito")
    
    # Ajustar el eje Y para que vaya de 0 a 100%
    ax.set_ylim(0, 100)
    
    # Agregar leyenda
    ax.legend()
    
    return fig

col3, col4 =st.columns(2)
with col3:
    st.pyplot(fig)
with col4:
    st.pyplot(plot_bar_chart())
