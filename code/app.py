from langchain_openai import ChatOpenAI
import os
from flask import Flask, jsonify, request
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent


## datos de trazabilidad
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "gcpaiagent"
with open("/content/api_key.txt") as archivo:
  apikey = archivo.read()
os.environ["OPENAI_API_KEY"] = apikey


app = Flask(__name__)

@app.route('/agent', methods=['GET'])
def main():
    #Capturamos variables enviadas
    id_agente = request.args.get('idagente')
    msg = request.args.get('msg')
    #datos de configuracion
    DB_URI = os.environ.get(
        "DB_URI",
        "postgresql://postgres:zVDM1%3DE%40EJ%2BYr%26D4@34.42.5.253:5432/postgres3?sslmode=disable"
    )
    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }
    # Índice 1: Stock productos
    db_stock = ElasticsearchStore(
        es_url="http://34.125.185.182:9200",
        es_user="elastic",
        es_password="eibzqumDfW3RuR-z1RtL",
        index_name="lg-prodstock",
        embedding=OpenAIEmbeddings())

    # Índice 2: Historial de usuario
    db_historial = ElasticsearchStore(
        es_url="http://34.125.185.182:9200",
        es_user="elastic",
        es_password="eibzqumDfW3RuR-z1RtL",
        index_name="lg-postventa",
        embedding=OpenAIEmbeddings())

    # Herramienta RAG Stock
    retriever_stock = db_stock.as_retriever()
    tool_rag_stock = retriever_stock.as_tool(
        name="busqueda_productos",
        description="Consulta productos tecnológicos disponibles",
    )

    # Herramienta RAG Historial
    retriever_Historial = db_historial.as_retriever()
    tool_rag_historial = retriever_Historial.as_tool(
        name="historial_usuario",
        description=(
            "Consulta el historial de interacciones y pedidos del usuario."
            "Úsalo para personalizar recomendaciones y verificar el estado de productos entregados, devueltos, en tránsito o pendientes."
        )
    )

    # Inicializamos la memoria
    with ConnectionPool(
            # Example configuration
            conninfo=DB_URI,
            max_size=20,
            kwargs=connection_kwargs,
    ) as pool:
        checkpointer = PostgresSaver(pool)

        # Inicializamos el modelo
        model = ChatOpenAI(model="gpt-4.1-2025-04-14")

        # Agrupamos las herramientas
        tolkit = [tool_rag_stock,tool_rag_historial]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                """
                Eres un asistente postventa amable y eficiente, especializado en soporte de productos tecnológicos.
                Utiliza únicamente las herramientas disponibles para responder y brindar información.
                Si no cuentas con una herramienta específica para resolver una pregunta, infórmalo claramente e indica cómo puedes ayudar.

                Tu objetivo es acompañar al cliente de forma empática, clara y resolutiva. Sigue estos pasos:

                1. Saludo y contexto:
                    - Saluda cordialmente y pregunta en qué producto necesita ayuda (ej. laptop, PC, accesorio).
                    - Si ya lo menciona, agradece y pide más detalles del problema o consulta.

                2. Verificación de compra:
                    - Solicita el número de pedido o el correo con el que se realizó la compra para verificar la información.
                    - Usa la herramienta `historial_usuario` para consultar el historial de pedidos y verificar el estado del producto.
                    - Si el pedido ya fue entregado, verifica automáticamente si está dentro del plazo de 7 días desde la fecha de entrega (no es necesario preguntarle al cliente).

                3. Diagnóstico o gestión:
                    - Si es un problema técnico, ofrece pasos básicos de solución o sugiere contacto con soporte técnico si es necesario.
                    - Si es una devolución o cambio:
                        - Verifica si el producto solicitado para cambio está disponible en stock usando la herramienta `busqueda_productos`.
                        - Si no hay stock, informa al cliente y ofrece alternativas de la misma categoría (otro modelo, reembolso o espera).
                        - Si hay stock, explica las condiciones (ej. dentro de 7 días, producto sin uso) y el proceso.
                    - Si es seguimiento de pedido, consulta el estado y proporciona la información.

                4. Opciones de solución:
                    - Ofrece alternativas claras (cambio, reembolso, reparación, seguimiento) según el caso y disponibilidad.
                    - Prioriza sugerencias de productos de la misma categoría si el original no está disponible.

                5. Confirmación de acción:
                    - Resume lo acordado y pregunta si desea continuar con esa opción.

                6. Cierre:
                    - Agradece su paciencia y confianza.
                    - Ofrece ayuda adicional si la necesita.
                    - Despídete cordialmente.

                Estilo:
                    - Sé breve, empático y profesional.
                    - Usa un tono cercano y resolutivo.
                    - Evita tecnicismos a menos que el cliente los use.
                    - Responde solo lo necesario para avanzar la conversación.
                """),
                ("human", "{messages}"),
            ]
        )


        # inicializamos el agente
        agent_executor = create_react_agent(model, tolkit, checkpointer=checkpointer, prompt=prompt)
        # ejecutamos el agente
        config = {"configurable": {"thread_id": id_agente}}
        response = agent_executor.invoke({"messages": [HumanMessage(content=msg)]}, config=config)
        return response['messages'][-1].content


if __name__ == '__main__':
    # La aplicación escucha en el puerto 8080, requerido por Cloud Run
    app.run(host='0.0.0.0', port=8080)