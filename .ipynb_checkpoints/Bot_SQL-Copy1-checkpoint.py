{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "409e6194-aaf4-4a2b-8b93-630e69d9d01e",
   "metadata": {},
   "outputs": [],
   "source": [
    "!pip install --quiet sqlalchemy langchain langchain_openai langchain-community pandas python-dotenv"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "71f46777-5491-4605-8a31-b4a5148e6367",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "\n",
    "#Cargamos el archivo\n",
    "\n",
    "df=pd.read_excel(\"BD_ENIGH_22.xlsx\")\n",
    "df.head(5)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "516bf286-fe0b-4418-85e3-78a63af09da3",
   "metadata": {},
   "outputs": [],
   "source": [
    "import sqlite3\n",
    "from sqlalchemy import create_engine\n",
    "\n",
    "#Creamos un motor de base de datos SQLite con sqlalchemy\n",
    "engine= create_engine(\"sqlite:///DB_ENIGH.db\")\n",
    "\n",
    "df.to_sql(\"ENIGH\", engine,if_exists=\"replace\", index=False)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "95f56016-314f-46dc-8b62-d44e3950bfe4",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Importar dotenv para cargar las variables de entorno\n",
    "from dotenv import load_dotenv\n",
    "import os\n",
    "\n",
    "from langchain_community.utilities import SQLDatabase\n",
    "from langchain_community.agent_toolkits import create_sql_agent\n",
    "from langchain_openai import ChatOpenAI\n",
    "\n",
    "#cargar variables de entorno desde archivo env\n",
    "load_dotenv()\n",
    "\n",
    "#conectar el agente LangChain con la base de datos SQL\n",
    "db= SQLDatabase(engine=engine)\n",
    "\n",
    "#Intanciamos el LLM\n",
    "llm= ChatOpenAI(model=\"gpt-4o\",temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'))\n",
    "\n",
    "#Creamos el agente\n",
    "agent_executor = create_sql_agent (llm, db=db, agent_type=\"openai-tools\", verbose=False)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0de91403-7206-4c7f-9cab-37e4e771cd91",
   "metadata": {},
   "outputs": [],
   "source": [
    "response = agent_executor.invoke ({\"input\": \"¿Cuantos registros hay en la base?\"})\n",
    "print (response[\"output\"])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7d6ff83d-0c8e-45f3-8154-4332901befda",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Hagamos una verificación\n",
    "len(df)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0a20635a-a3f3-43c3-8f09-c3b916dd95e5",
   "metadata": {},
   "outputs": [],
   "source": [
    "response = agent_executor.invoke ({\"input\": \"¿Cual es la distribución de los hogares por nivel socieconomico?\"})\n",
    "print (response[\"output\"])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "44327843-115e-4997-be2d-62a769a7dd1a",
   "metadata": {},
   "outputs": [],
   "source": [
    "response = agent_executor.invoke ({\"input\": \"¿Cual es la distribución en porcentaje de los hogares por nivel socieconomico?\"})\n",
    "print (response[\"output\"])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "acf10e65-9422-4982-931c-08d8cd505100",
   "metadata": {},
   "outputs": [],
   "source": [
    "response = agent_executor.invoke ({\"input\": \"¿Cual es la distribución en porcentaje de los hogares por nivel socieconomico? Pondera por la variable factor_expasión\"})\n",
    "print (response[\"output\"])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "608c08e9-e4e0-4f36-b695-a1bf8b635d80",
   "metadata": {},
   "outputs": [],
   "source": [
    "response = agent_executor.invoke ({\"input\": \"¿Cual es el ingreso promedio mensual por nivel socioeconomico ? Pondera por la variable factor_expasión\"})\n",
    "print (response[\"output\"])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5324bf2f-3a8d-4cb6-9676-07fc6d960bab",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2be3b915-fea4-4128-86d5-aa4f87c67caa",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b058c502-8e61-4382-a042-26c897d00733",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
