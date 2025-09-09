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

# Configuración de Streamlit
st.set_page_config(page_title="Consulta interactiva ENIGH 2024 por NSE", layout="wide")
st.title("📊🏘️ ENIGH 2024 - Equipamiento de los hogares, ingreso y gasto por principales rubros según NSE")

st.markdown("""
Esta aplicación permite consultar de forma interactiva los datos de la **ENIGH 2024**, 
enfocándose en **ingresos, gastos y equipamiento de los hogares mexicanos**, clasificados por **nivel socioeconómico (NSE)**.

💡 Puedes preguntar por promedios, distribuciones o proporciones relacionadas con variables contenidas en la base de datos.  
🔒 No puede responder preguntas fuera del contenido de la base, como el detalle metodológico completo del INEGI.  
📊 Todos los cálculos se ajustan automáticamente utilizando el **factor de expansión** para asegurar representatividad estadística.
🏘️ Todos los resultados se muestran a nivel hogar.
""")


# Conectar a la base SQLite
DB_PATH = "DB_ENIGH.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
db = SQLDatabase(engine=engine)

# Crear modelo y agente
llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_API_KEY)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

# Inicializar historial
if "historial" not in st.session_state:
    st.session_state.historial = []

# Nombre de la columna de ponderación
ponderador_col = "Factor_expasion"

def reformular_pregunta(pregunta):
    pregunta = pregunta.lower()
    original = pregunta

    # Periodicidad para ingreso o gasto
    if "ingreso anual" in pregunta or "ingreso promedio anual" in pregunta or "gasto anual" in pregunta or "gasto promedio anual" in pregunta:
        return (
            f"{pregunta}. Recuerda calcular el ingreso o gasto anual a partir del valor mensual promedio, "
            f"multiplicando el promedio ponderado mensual por 12. Es decir: "
            f"SUM(variable * {ponderador_col}) / SUM({ponderador_col}) * 12."
        )
    elif "ingreso quincenal" in pregunta or "ingreso promedio quincenal" in pregunta or "gasto quincenal" in pregunta or "gasto promedio quincenal" in pregunta:
        return (
            f"{pregunta}. Recuerda calcular el ingreso o gasto quincenal a partir del valor mensual promedio, "
            f"dividiendo el promedio ponderado mensual entre 2. Es decir: "
            f"SUM(variable * {ponderador_col}) / SUM({ponderador_col}) / 2."
        )
    elif "ingreso trimestral" in pregunta or "ingreso promedio trimestral" in pregunta or "gasto trimestral" in pregunta or "gasto promedio trimestral" in pregunta:
        return (
            f"{pregunta}. Recuerda calcular el ingreso o gasto trimestral a partir del valor mensual promedio, "
            f"multiplicando el promedio ponderado mensual por 3. Es decir: "
            f"SUM(variable * {ponderador_col}) / SUM({ponderador_col}) * 3."
        )
    elif "ingreso semanal" in pregunta or "ingreso promedio semanal" in pregunta or "gasto semanal" in pregunta or "gasto promedio semanal" in pregunta:
        return (
            f"{pregunta}. Recuerda calcular el ingreso o gasto semanal a partir del valor mensual promedio, "
            f"dividiendo el promedio ponderado mensual entre 4.345. Es decir: "
            f"SUM(variable * {ponderador_col}) / SUM({ponderador_col}) / 4.345."
        )
    elif "ingreso diario" in pregunta or "ingreso promedio diario" in pregunta or "gasto diario" in pregunta or "gasto promedio diario" in pregunta:
        return (
            f"{pregunta}. Recuerda calcular el ingreso o gasto diario a partir del valor mensual promedio, "
            f"dividiendo el promedio ponderado mensual entre 30.4. Es decir: "
            f"SUM(variable * {ponderador_col}) / SUM({ponderador_col}) / 30.4."
        )

    # Lógica para otros tipos de preguntas
    claves_promedio = ["media de", "promedio de", "ingreso promedio", "gasto promedio", "valor medio", "media", "promedio"]
    claves_porcentaje = ["porcentaje", "proporción", "representa", "representación", "cuánto representa", "qué proporción"]
    claves_distribucion = ["distribución", "cómo se distribuye", "reparto", "segmentación"]

    if any(clave in pregunta for clave in claves_promedio):
        return (
            f"{pregunta}. Recuerda calcular el promedio ponderado como "
            f"SUM(variable * {ponderador_col}) / SUM({ponderador_col})."
        )

    elif any(clave in pregunta for clave in claves_porcentaje + claves_distribucion):
        return (
            f"{pregunta}. Recuerda ponderar por la columna '{ponderador_col}' para que la estimación sea representativa."
        )

    # Bloque final: ponderar por defecto cualquier otra consulta
    return (
        f"{pregunta}. Recuerda que cualquier cálculo o comparación debe ponderarse usando la columna '{ponderador_col}' "
        f"para asegurar representatividad estadística."
    )


# Entrada de pregunta
pregunta = st.text_area("Escribe tu consulta:", value="")
if st.button("Responder"):
    with st.spinner("Consultando la base..."):
        pregunta_reformulada = reformular_pregunta(pregunta)
        
        # Modificación opcional: intentar eliminar LIMIT si el usuario quiere todo
        if "todas" in pregunta.lower() or "todas las entidades" in pregunta.lower():
            pregunta_reformulada = pregunta_reformulada.replace("LIMIT 10", "")

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

# Sección de metodología
st.divider()
st.subheader("📘 Metodología")
with st.expander("Ver detalles de la metodología utilizada"):
    st.markdown(f"""
    Esta herramienta se basa en la base de datos **ENIGH 2024**, publicada por el INEGI, 
    que recopila información sobre ingresos, gastos y características de los hogares mexicanos.

    **Fuente:**
    - Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH), 2024. INEGI.
    - La clasificación por nivel socioeconómico (NSE) fue generada a partir de cálculos realizados por el equipo de Planning Quant.
    - La aplicación utiliza inteligencia artificial basada en un agente conversacional desarrollado con LangChain y el modelo GPT-4o de OpenAI.
    """)
