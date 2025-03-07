import streamlit as st
import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



st.set_page_config(
    layout="wide",
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100px !important; # Set the width to your desired value
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
            padding-left: 2rem;
            padding-right: 2rem;
        }
        h2 {
        text-align: center;  
        }
        
    <style>
        """, unsafe_allow_html=True,

)

st.header("👩 Dones")

def run_query(query):
    df = pd.read_sql(query, con=engine)
    return df

engine = create_engine(f"postgresql://postgres.spdwbcfeoefxnlfdhlgi:chatbot2025@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")

st.header("Descargues de dones per Ámbito")

querry_donas = "SELECT u.nomambito, COUNT(d.id) AS total_descargas_mujer, (COUNT(d.id) * 100.0 / NULLIF(td.total_descargas, 0)) AS porcentaje_descargas_mujer FROM public.descargas d JOIN public.usuarios u ON d.usuario = u.usuario JOIN (SELECT u.nomambito, COUNT(d.id) AS total_descargas FROM public.descargas d JOIN public.usuarios u ON d.usuario = u.usuario GROUP BY u.nomambito) td ON u.nomambito = td.nomambito WHERE u.genero = 'Mujer' GROUP BY u.nomambito, td.total_descargas ORDER BY total_descargas_mujer ASC;"

df_donas = run_query(querry_donas)

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

# Mostrar el gráfico en Streamlit
st.pyplot(fig)

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

# Mostrar el gráfico en Streamlit
st.pyplot(plot_bar_chart())
