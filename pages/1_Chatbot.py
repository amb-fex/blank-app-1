import streamlit as st
#import os
#import subprocess
#import sys
import time
import streamlit as st
#import vanna
#from vanna.base import VannaBase
#import pandas as pd
from Chatbot.vanna_calls import (
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached
)

st.set_page_config(
    layout="wide",
)
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
            #         padding-left: 0rem;
            #         padding-right: 0rem;
                 }
        
        </style>
        """, unsafe_allow_html=True,
)
avatar_url = "https://www.amb.cat/o/amb-generic-theme/images/favicon.ico"
#"https://imgur.com/a/AMxVhby"


st.sidebar.title("Configuració de sortida")
st.sidebar.checkbox("Mostra SQL", value=True, key="show_sql")
st.sidebar.checkbox("Mostra taula", value=True, key="show_table")
st.sidebar.checkbox("Mostra codi Plotly", value=False, key="show_plotly_code")
st.sidebar.checkbox("Mostra gràfic", value=True, key="show_chart")
st.sidebar.checkbox("Mostra resum", value=False, key="show_summary")
st.sidebar.checkbox("Mostra preguntes de seguiment", value=True, key="show_followup")
st.sidebar.button("Restableix", on_click=lambda: set_question(None), use_container_width=True)
st.title("🤖 Chatbot")
st.write("Analítiques del geoportal cartografia AMB")



def set_question(question):
    st.session_state["my_question"] = question
    st.rerun()  # Recarga la interfaz cuando se selecciona una pregunta

# Permitir siempre la entrada de una nueva pregunta
user_input = st.chat_input("Fes-me una pregunta sobre les teves dades")
if user_input:
    set_question(user_input)

my_question = st.session_state.get("my_question", default=None)

assistant_message_suggested = st.chat_message(
    "assistant", avatar=avatar_url
)
if assistant_message_suggested.button("Fes clic per veure preguntes suggerides"):
    st.session_state["my_question"] = None
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        button = st.button(
            question,
            on_click=set_question,
            args=(question,),
            key=f"question_{i}"  # Se agrega una clave única para cada botón
        )
       

       
#my_question = st.session_state.get("my_question", default=None)

#if my_question is None:
   # my_question = st.chat_input(
        #"Fes-me una pregunta sobre les teves dades",
   # )

if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)

    if sql:
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message(
                    "assistant", avatar=avatar_url
                )
                assistant_message_sql.code(sql, language="sql", line_numbers=True)
        else:
            assistant_message = st.chat_message(
                "assistant", avatar=avatar_url
            )
            assistant_message.write(sql)
            st.stop()

        df = run_sql_cached(sql=sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                assistant_message_table.dataframe(df)
                #if len(df) > 10:
                   # assistant_message_table.text("Primeres 10 files de dades")
                   # assistant_message_table.dataframe(df.head(10))
                #else:
                    #assistant_message_table.dataframe(df)

            if should_generate_chart_cached(question=my_question, sql=sql, df=df):

                code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message(
                        "assistant",
                        avatar=avatar_url,
                    )
                    assistant_message_plotly_code.code(
                        code, language="python", line_numbers=True
                    )

                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message(
                            "assistant",
                            avatar=avatar_url,
                        )
                        fig = generate_plot_cached(code=code, df=df)
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                        else:
                            assistant_message_chart.error("No he pogut generar un gràfic")

            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                summary = generate_summary_cached(question=my_question, df=df)
                if summary is not None:
                    assistant_message_summary.text(summary)

            if st.session_state.get("show_followup", True):
                assistant_message_followup = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                followup_questions = generate_followup_cached(
                    question=my_question, sql=sql, df=df
                )
                st.session_state["df"] = None

                if len(followup_questions) > 0:
                    assistant_message_followup.text(
                        "Aquí tens algunes possibles preguntes de seguiment"
                    )
                    # Imprimeix les primeres 5 preguntes de seguiment
                    for question in followup_questions[:5]:
                        assistant_message_followup.button(question, on_click=set_question, args=(question,))

    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar=avatar_url
        )
        assistant_message_error.error("No he pogut generar SQL per a aquesta pregunta")