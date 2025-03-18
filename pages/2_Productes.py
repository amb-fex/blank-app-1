import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px

st.set_page_config(
    layout="wide",
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100px !important; 
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

        
        /* Modificar el tamaño de los checkboxes en el multiselect */
        div[data-baseweb="checkbox"] {
            transform: scale(0.5);  /* Ajusta el tamaño */
        }
    
        h2 {
            text-align: center;  
        }
    </style>
    """, unsafe_allow_html=True,
)



st.header("📊 Productes")

def run_query(query):
    df = pd.read_sql(query, con=engine)
    return df

engine = create_engine(f"postgresql://postgres.spdwbcfeoefxnlfdhlgi:chatbot2025@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")


# Consulta SQL para obtener la lista de productos
query_productos = "SELECT DISTINCT nomproducte FROM public.descargas;"
df_productos = run_query(query_productos)
productos = df_productos["nomproducte"].tolist()

# Crear dos columnas
col1, col2 = st.columns([3, 1])  # La primera columna es más ancha que la segunda

# Controles en la segunda columna
with col2:
    st.markdown("")
    st.markdown("")
    st.markdown("Controles: Mapa de calor de descàrregues un producte")
    
    # Selector de productos
    producto_seleccionado = st.selectbox(
        "Selecciona un producte",
        options=productos,
        index=25  # Valor por defecto
    )
    
    # Obtener los años únicos de la base de datos
    query_anys = "SELECT DISTINCT EXTRACT(YEAR FROM fechadescarga) AS anyo FROM public.descargas ORDER BY anyo;"
    df_anys = run_query(query_anys)
    anys = df_anys["anyo"].astype(int).tolist()
    
    # Selector de año
    anys_seleccionados = st.multiselect(
        "Selecciona les anys",
        options=anys,
        default=anys
    )
    
    # Convertir lista de años seleccionados en formato SQL
    anys_str = ",".join(map(str, anys_seleccionados))
    
    # Control para seleccionar el esquema de colores
    esquema_colores = st.selectbox(
        "Selecciona l'esquema de colors",
        options=["Reds", "Oranges", "Blues", "PuBu", "Greens"],
        index=0  
    )

# Consulta SQL para obtener los datos del producto seleccionado
query = f"""
SELECT 
    DATE_TRUNC('month', fechadescarga) AS mes, 
    COUNT(*) AS total_descargas 
FROM public.descargas 
WHERE nomproducte = '{producto_seleccionado}'
AND EXTRACT(YEAR FROM fechadescarga) IN ({anys_str})
GROUP BY mes 
ORDER BY mes;
"""
df_un_producto = run_query(query)

if not df_un_producto.empty:
    # Convertir la columna 'mes' a formato de fecha
    df_un_producto["mes"] = pd.to_datetime(df_un_producto["mes"])

    # Extraer el año y el mes de la columna 'mes'
    df_un_producto["any"] = df_un_producto["mes"].dt.year
    df_un_producto["mes_num"] = df_un_producto["mes"].dt.month

    # Crear un diccionario para mapear los números de mes a nombres completos
    mesos = {
        1: "Gener", 2: "Febrer", 3: "Març", 4: "Abril", 5: "Maig", 6: "Juny",
        7: "Juliol", 8: "Agost", 9: "Setembre", 10: "Octubre", 11: "Novembre", 12: "Desembre"
    }
    df_un_producto["mes_nom"] = df_un_producto["mes_num"].map(mesos)

    # Establecer 'mes_nom' como categoría ordenada
    df_un_producto["mes_nom"] = pd.Categorical(df_un_producto["mes_nom"], categories=[mesos[i] for i in range(1, 13)], ordered=True)

    # Crear un DataFrame con todos los meses para asegurar que no falte ninguno
    meses_ordenados = pd.DataFrame({
        "mes_num": range(1, 13),
        "mes_nom": [mesos[i] for i in range(1, 13)]
    })

    # Unir con el DataFrame original para incluir todos los meses aunque no tengan datos
    df_un_producto = meses_ordenados.merge(df_un_producto, on=["mes_num", "mes_nom"], how="left").fillna(0)

    # Ordenar los datos por número de mes antes de pivotar
    df_un_producto = df_un_producto.sort_values("mes_num")

    if anys_seleccionados:
        # Crear el mapa de calor con Plotly
        fig = px.imshow(
            df_un_producto.pivot(index="mes_nom", columns="any", values="total_descargas"),
            labels=dict(y="Mes", color="Descàrregues"),
            title=f"Descàrregues de {producto_seleccionado}",
            color_continuous_scale=esquema_colores,
            width=800,
            height=600
        )
        # Forzar el orden de los meses en el eje Y
        fig.update_yaxes(categoryorder="array", categoryarray=[mesos[i] for i in range(1, 13)])

        # Mostrar el gráfico en la primera columna
        with col1:
            st.plotly_chart(fig)
    
else:
    with col1:
        st.warning(f"No hi ha dades disponibles per mostrar el mapa de calor per al producte {producto_seleccionado}.")

# Crear dos columnas nuevas columnas
col3, col4 = st.columns([3, 1])  # La primera columna es más ancha que la segunda

# Ahora hago el gráfico que me deja seleccionar más de un producto para la comparación
with col3:
  #  st.markdown('Mapa de calor de descàrregues per a més de un producte')

    query_productos_mes_a_mes = "SELECT DATE_TRUNC('month', fechadescarga) AS mes, nomproducte, COUNT(*) AS total_descargas FROM public.descargas GROUP BY mes, nomproducte ORDER BY mes, nomproducte;"

    df_descargas = run_query(query_productos_mes_a_mes)

    with st.container():  # Full-width container
            productos_seleccionados = st.multiselect(
            "Selecciona els productes",
            options=productos,
            default=productos[54:60]  
         )

if not df_descargas.empty:
    # Convertir la columna 'mes' a formato de fecha
    df_descargas["mes"] = pd.to_datetime(df_descargas["mes"])

    # Obtener la lista única de productos y meses
    productos = df_descargas["nomproducte"].unique()
    meses = df_descargas["mes"].dt.strftime('%Y-%m').unique()  # Convertir fechas a cadenas de texto
    
    
    
    # Controles para seleccionar productos y meses
    with col4:
        st.markdown("Controles per comparar més de un producte")
        
        meses_seleccionados = st.multiselect(
            "Selecciona els mesos",
            options=meses,
            default=meses[-12:]  # Meses seleccionados por defecto
        )

        # Control para seleccionar el esquema de colores
        esquema_colores2 = st.selectbox(
            "Selecciona l'esquema de colors",
            options=["Reds", "Oranges", "Blues", "PuBu", "Greens"],
            index=1  
        )

    if productos_seleccionados and meses_seleccionados:  # Verificar que se hayan seleccionado opciones
        # Convertir las cadenas de texto de meses seleccionados de nuevo a fechas
        meses_seleccionados_dt = pd.to_datetime(meses_seleccionados)
    
        # Filtrar el DataFrame
        df_filtrado = df_descargas[
            df_descargas["nomproducte"].isin(productos_seleccionados) & 
            df_descargas["mes"].isin(meses_seleccionados_dt)  # Usar fechas convertidas
        ]
    
        # Crear el mapa de calor con Plotly
        fig = px.imshow(
            df_filtrado.pivot(index="nomproducte", columns="mes", values="total_descargas"),
            labels=dict(x="", y="", color=""),
            title=f"Descàrregues de {productos_seleccionados}",
            
            color_continuous_scale=esquema_colores2,
            width=800,
            height=600
        )
        
        # Mostrar el gráfico en la primera columna
        with col3:
            st.plotly_chart(fig, use_container_width=True)
        
    else:
        with col3:
            st.warning("Selecciona almenys un producte i un mes per mostrar el mapa de calor.")
else:
    with col3:
        st.warning("No hi ha dades disponibles per mostrar el mapa de calor.")


# Configuración de la aplicación Streamlit
st.header("Comparativa de Descàrregues per producte")

# Consulta SQL para obtener la lista de productos
query_productos = "SELECT DISTINCT nomproducte FROM public.descargas;"
df_productos = run_query(query_productos)
productos = df_productos["nomproducte"].tolist()

query_top5 = """
 SELECT 
        DATE_TRUNC('month', fechadescarga) AS fecha, 
        nomproducte, 
        COUNT(*) AS total_descargas 
    FROM public.descargas 
    GROUP BY fecha, nomproducte 
    ORDER BY fecha;
"""
df_top5 = run_query(query_top5)
col5,col6 = st.columns([3,1])

if not df_top5.empty:
    # Convertir la columna 'mes' a formato de fecha
    # Extraer el año y el mes de la columna 'mes'
    df_top5["fecha"] = pd.to_datetime(df_top5["fecha"], errors="coerce")
    df_top5["any"] = df_top5["fecha"].dt.year
    df_top5["mes_num"] = df_top5["fecha"].dt.month

    # Crear un diccionario para mapear los números de mes a nombres completos
    mesos = {
            1: "Gener", 2: "Febrer", 3: "Març", 4: "Abril", 5: "Maig", 6: "Juny",
            7: "Juliol", 8: "Agost", 9: "Setembre", 10: "Octubre", 11: "Novembre", 12: "Desembre"
        }
    df_top5["mes_nom"] = df_top5["mes_num"].map(mesos)

    with col6:
        # Selector de años
        años_disponibles = df_top5["any"].unique()
        años_seleccionados = st.multiselect(
        "Selecciona els anys a mostrar",
        options=años_disponibles,
        default=años_disponibles  # Todos los años por defecto
        )

# Selector de productos
        productos_disponibles = df_top5["nomproducte"].unique()
        productos_seleccionados = st.multiselect(
        "Selecciona els productes a mostrar",
        options=productos_disponibles,
        default= productos[:5],  
        # Todos los años por defecto
        )
    # Filtrar el DataFrame por años y meses seleccionados
    df_filtrado = df_top5[
        (df_top5["any"].isin(años_seleccionados)) & 
        (df_top5["nomproducte"].isin(productos_seleccionados))
    ]
    with col5:
        # Crear el gráfico de líneas con Plotly
        fig = px.line(
            df_filtrado,
            x="fecha",
            y="total_descargas",
            color="nomproducte",
            labels={"mes": "mes_nom", "total_descargas": "Descàrregues", "nomproducte": "Producte"},
            markers=True,
            line_dash="nomproducte",  # Estilo de línea diferente para cada producto
            color_discrete_sequence=px.colors.qualitative.Plotly  # Paleta de colores personalizada
            )

        # Personalizar el gráfico
        fig.update_layout(
            xaxis_title="Mes",
            yaxis_title="Descàrregues",
            legend_title="Producte",
            width=1000,
            height=600,
            plot_bgcolor="rgba(240, 240, 240, 0.9)",  # Fondo del gráfico más claro
            paper_bgcolor="rgba(255, 255, 255, 0.9)",  # Fondo del área exterior más claro
            font=dict(family="Arial", size=12, color="black"),  # Fuente más profesional
            xaxis=dict(
                showgrid=True,  # Mostrar cuadrícula en el eje X
                gridcolor="rgba(200, 200, 200, 0.5)",  # Color de la cuadrícula
                tickformat="%b %Y"  # Formato de fecha: Mes Año
            ),
            yaxis=dict(
            showgrid=True,  # Mostrar cuadrícula en el eje Y
            gridcolor="rgba(200, 200, 200, 0.5)"  # Color de la cuadrícula
            ),
            legend=dict(
            x=1.02,  # Mover la leyenda fuera del gráfico
            y=1,  # Posición vertical de la leyenda
            bordercolor="black",  # Borde de la leyenda
            borderwidth=1  # Grosor del borde
            )
            )

            # Personalizar las líneas y marcadores
        for trace in fig.data:
            trace.update(
            mode="lines",  # Mostrar líneas y marcadores
            marker=dict(size=8, line=dict(width=1, color="black")),  # Marcadores más grandes con borde
            line=dict(width=2)  # Líneas más gruesas
            )

        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig)
