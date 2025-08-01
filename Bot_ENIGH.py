# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 17:37:03 2025

@author: Gerardo Nájera
"""

import streamlit as st
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
import pandas as pd

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración Streamlit
st.set_page_config(page_title="NIVELES SOCIECONÓMICOS 2024", layout="wide")
st.title("📊 Consulta lo que deseas sobre los NSE 2024")

# Conectar a la base SQLite creada previamente
DB_PATH = "DB_ENIGH.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
db = SQLDatabase(engine=engine)

# Crear modelo y agente
llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_API_KEY)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

# Inicializar historial
if "historial" not in st.session_state:
    st.session_state.historial = []

# Nombre de columna de ponderación
ponderador_col = "Factor_expasion"

def reformular_pregunta(pregunta):
    pregunta = pregunta.lower()

    # Lista de palabras clave para identificar diferentes tipos de preguntas
    claves_promedio = ["media de", "promedio de", "ingreso promedio", "valor medio", "media", "promedio"]
    claves_porcentaje = ["porcentaje", "proporción", "representa", "representación", "cuánto representa", "qué proporción"]
    claves_distribucion = ["distribución", "cómo se distribuye", "reparto", "segmentación"]

    if any(clave in pregunta for clave in claves_promedio):
        return (
            f"{pregunta}. Recuerda calcular el promedio ponderado como "
            f"SUM(variable * {ponderador_col}) / SUM({ponderador_col}), en lugar de usar AVG()."
        )

    elif any(clave in pregunta for clave in claves_porcentaje + claves_distribucion):
        return (
            f"{pregunta}. Recuerda ponderar por la columna '{ponderador_col}' para que la estimación sea representativa."
        )

    return pregunta


# Mostrar advertencia al usuario
st.info(f"""
ℹ️ Las consultas como promedios o distribuciones serán reformuladas automáticamente para usar el factor de expansión: **'{ponderador_col}'**.
No necesitas escribirlo manualmente.
""")

# Entrada de pregunta
pregunta = st.text_area("Escribe tu consulta:", value="¿Cuál es el ingreso promedio mensual por nivel socioeconómico?")
if st.button("Responder"):
    with st.spinner("Consultando la base..."):
        pregunta_reformulada = reformular_pregunta(pregunta)
        respuesta = agent_executor.invoke({"input": pregunta_reformulada})
        st.session_state.historial.append({
            "Pregunta original": pregunta,
            "Reformulada": pregunta_reformulada,
            "Respuesta": respuesta["output"]
        })
        st.success("Respuesta:")
        st.write(respuesta["output"])

# Mostrar historial
st.divider()
st.subheader("🕓 Historial de consultas")
if st.session_state.historial:
    df_hist = pd.DataFrame(st.session_state.historial)
    st.dataframe(df_hist)
else:
    st.info("Aún no hay consultas registradas.")
