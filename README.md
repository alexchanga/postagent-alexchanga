# POSTAGENT – IA ESPECIALIZADA EN POSTVENTA

**Construye un asistente conversacional** que combina:

- **LangChain** para orquestar la lógica de IA  
- **RAG** (Retrieve‑Augment‑Generate) sobre **Elasticsearch 8.x**  
- **Memoria de corto plazo** con **Cloud SQL (PostgreSQL)** y checkpoints  
- **Trazabilidad** completa vía **LangSmith**  
- Despliegue **Docker → Cloud Run (GCP)** y **UI React / Next.js en Vercel**

> Video Presentación: https://youtu.be/8zSyy7y40Do?si=28l5-ueja8qw881h

---

## ⬇️ Contenido del repositorio

| Ruta | Descripción |
|------|-------------|
| `POSTAGENT_DATA_SAMPLE.ipynb` | Notebook Colab con todo el paso a paso para construir el agente. |
| `POSTAGENT_DATA_CARGA.ipynb` | Carga datos de prueba en base de datos vectorial Elasticsearch. |
| `datos_postventa.csv` | Datos de prueba para la base de datos vectorial - Datos de Pedidos. |
| `stock_productos.csv` | Datos de prueba para la base de datos vectorial - Datos de Stock. |
| `POSTVENTA-IA AGENTE.pptx` | Presentación de la solución. |
| `docs/` | Carpeta de arquitectura  |
| &nbsp;&nbsp;└ `POSTAGENT_ARQUITECTURA.PNG` | Arquitectura de la solucion. |
| `CloudRun/` | Carpeta con el microservicio listo para Docker ➜ Cloud Run |
| &nbsp;&nbsp;└ `app.py` | Código Python del agente (API `/agent`). |
| &nbsp;&nbsp;└ `Dockerfile` | Imagen multistage ligera. |
| &nbsp;&nbsp;└ `requirements.txt` | Dependencias congeladas. |

Plantillas FrontEnd (repos externos):

- Login con Google → <https://github.com/alexchanga/agentui-withlogin>  

---

## 🗺️ Arquitectura

![Arquitectura](docs/POSTAGENT_ARQUITECTURA.PNG)
