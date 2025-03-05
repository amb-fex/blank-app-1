import streamlit as st

# Inyectar CSS personalizado para reducir el margen superior y centrar el título

st.markdown(
    """
        <style>
                .stAppHeader {
                    font-size: 10px;  /* Tamaño del título */
                    background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
                    visibility: visible;  /* Ensure the header is visible */
                }

               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
                }
        h2 {
        text-align: center;  
        }
        </style>
        """, unsafe_allow_html=True,
)

st.logo("Imagenes/amb.png")
# Título centrado
st.header("Anàlisi de Dades del Geoportal de Cartografia")
st.write("")  # Esto agrega un espacio vacío
# Mostrar la imagen
st.image("Imagenes/Portal.png", width=600)