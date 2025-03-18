import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import seaborn as sns

# Configuración de la página
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100px !important;
            background-color: rgba(255, 255, 255, 0.0);
        }
        .block-container {
            margin:1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        h2 {
            text-align: center;  
        }
    </style>
    """, unsafe_allow_html=True,
)

st.header(":man-woman-girl-boy: Usuaris")

# Conexión a la base de datos
engine = create_engine("postgresql://postgres.spdwbcfeoefxnlfdhlgi:chatbot2025@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")

def run_query(query):
    return pd.read_sql(query, con=engine)

# Selección de año para filtrar
selected_year = st.selectbox("Selecciona un año", ["Todos"] + list(range(2014, 2026)))

# Query para el acumulado de usuarios incluyendo años anteriores
query_usuarios_mes = f"""
    WITH registros_mensuales AS (
        SELECT
            DATE_TRUNC('month', fechaalta) AS fecha,
            COUNT(*) AS total_registros
        FROM public.usuarios
        WHERE EXTRACT(YEAR FROM fechaalta) <= {selected_year if selected_year != 'Todos' else '9999'}
        GROUP BY fecha
    ),
    acumulado_anterior AS (
        SELECT
            SUM(total_registros) AS usuarios_acumulados
        FROM registros_mensuales
        WHERE EXTRACT(YEAR FROM fecha) < {selected_year if selected_year != 'Todos' else '9999'}
    )
    SELECT
        fecha,
        SUM(total_registros) OVER (ORDER BY fecha) + COALESCE((SELECT usuarios_acumulados FROM acumulado_anterior), 0) AS acumulado_registros
    FROM registros_mensuales
    ORDER BY fecha;
"""
df_mes = run_query(query_usuarios_mes)

# Gráfico del acumulado de usuarios registrados con eje temporal
fig1 = px.line(df_mes, x='fecha', y='acumulado_registros', markers=True, title="Acumulado de Usuarios Nuevos a lo Largo del Tiempo")
fig1.update_traces(fill='tozeroy', mode='lines+markers', marker=dict(symbol='diamond', size=10))
st.plotly_chart(fig1, use_container_width=True)

# Selección de paleta de colores para los gráficos de torta
palettes = list(sns.color_palette().as_hex())
selected_palette = st.selectbox("Selecciona una paleta de colores", ["viridis", "dark", "magma", "pastel", "icefire", "rocket"])
colors = sns.color_palette(selected_palette).as_hex()

# Query para usuarios por ámbito
query_ambito = """
    WITH total AS (
        SELECT COUNT(*) AS total_usuarios FROM public.usuarios
    )
    SELECT
        u.nomambito,
        COUNT(*) AS total_usuarios,
        ROUND((COUNT(*) * 100.0 / t.total_usuarios), 2) AS porcentaje
    FROM public.usuarios u, total t
    GROUP BY u.nomambito, t.total_usuarios
    ORDER BY total_usuarios DESC;
"""
df_ambito = run_query(query_ambito)
fig2 = px.pie(df_ambito, names='nomambito', values='total_usuarios', title="Distribución de Usuarios por Ámbito Profesional", color_discrete_sequence=colors)
fig2.update_traces(textfont_color='white')
fig2.update_layout(legend=dict(x=1, y=0.5, xanchor="left", yanchor="middle"))

# Query para usuarios por perfil profesional
query_perfil = """
    SELECT
        nomperfil,
        COUNT(*) AS total_usuarios
    FROM public.usuarios
    GROUP BY nomperfil
    ORDER BY total_usuarios DESC;
"""
df_perfil = run_query(query_perfil)
fig3 = px.pie(df_perfil, names='nomperfil', values='total_usuarios', title="Distribución de Usuarios por Perfil Profesional", color_discrete_sequence=colors)
fig3.update_traces(textfont_color='white')


col1, col2 = st.columns([5, 3])
with col1:
    st.plotly_chart(fig2, use_container_width=True)
with col2:
    st.plotly_chart(fig3, use_container_width=True)

    query_perfil = """
    WITH registros_mensuales AS (
        SELECT
            DATE_TRUNC('month', fechaalta) AS fecha,
            nomperfil,
            COUNT(*) AS nuevos_registros
        FROM public.usuarios
        GROUP BY fecha, nomperfil
    )
    SELECT
        fecha,
        nomperfil,
        SUM(nuevos_registros) OVER (PARTITION BY nomperfil ORDER BY fecha) AS acumulado_registros
    FROM registros_mensuales
    ORDER BY fecha;
"""
df_perfil = run_query(query_perfil)
# Interfaz en Streamlit
st.title("📊 Evolución de registros por perfil profesional")



# Gráfico de evolución acumulada de usuarios agrupado por perfil profesional
fig4 = px.area(
    df_perfil, x="fecha", y="acumulado_registros",
    color="nomperfil",
    title="Histórico Acumulado de Usuarios Registrados por Perfil Profesional",
    labels={"acumulado_registros": "Número acumulado de registros", "fecha": "Fecha"},
    line_group="nomperfil"
)


# Mostrar la gráfica
st.plotly_chart(fig4, use_container_width=True)

