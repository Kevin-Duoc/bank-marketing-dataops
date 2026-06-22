# DataOps Pipeline, IA & Dashboard: Bank Marketing Analysis

Este proyecto implementa una arquitectura robusta de DataOps para la ingesta, limpieza, validación y carga de datos masivos de campañas de marketing bancario en AWS EC2, sumado al entrenamiento de modelos de Machine Learning con telemetría de hardware y un dashboard corporativo interactivo para la toma de decisiones.

## 1. Arquitectura del Proyecto
El sistema está dividido en tres componentes independientes y desacoplados:
* **Pipeline ETL (DataOps):** Ejecuta la ingesta del dataset original por lotes, realiza limpieza defensiva en RAM con Pandas, valida la integridad estricta mediante contratos de datos con Pandera y carga la información en una base de datos MySQL alojada en AWS EC2.
* **Inteligencia Artificial y Telemetría:** Entrena y evalúa modelos predictivos (Regresión Logística y Random Forest) para identificar clientes propensos a suscribir depósitos. Incluye un monitor de recursos (`tracemalloc` y `gc`) para medir el trade-off exacto entre métricas de negocio (AUC, Gini, F1-Score) y consumo de hardware (Peak RAM y Latencia).
* **Dashboard Corporativo (Frontend):** Interfaz interactiva desarrollada en Streamlit y Plotly que consume los datos de AWS y los JSON de métricas. Permite realizar Análisis Exploratorio (EDA) dinámico, visualizar matrices de confusión y auditar la salud del pipeline en tiempo real.

## 2. Tecnologías Utilizadas
* **Lenguaje:** Python 3.12
* **Procesamiento y Validación:** Pandas, Pandera, NumPy
* **Machine Learning:** Scikit-Learn
* **Telemetría de Hardware:** tracemalloc, gc, time, psutil
* **Infraestructura y Nube:** AWS EC2 (Instancia Linux con servidor MySQL)
* **Base de Datos y ORM:** SQLAlchemy, PyMySQL
* **Visualización:** Streamlit, Plotly (Gráficos interactivos y Radares)
* **Contenedores y Despliegue:** Docker, Docker Hub

## 3. Seguridad, Auditoría y Buenas Prácticas
* **Aislamiento de Entorno:** El proyecto se encuentra dockerizado, garantizando que corra de forma idéntica en cualquier máquina.
* **Gestión de Credenciales:** Las llaves privadas (`.pem`) y credenciales de AWS (`.env`) están estrictamente excluidas del control de versiones mediante reglas avanzadas en `.gitignore`. Se adjunta un archivo `env.example` con la estructura requerida.
* **Privacidad de Datos:** En alineación con la normativa de protección de datos, el Dashboard opera sobre vistas agregadas y métricas anonimizadas, asegurando que información sensible de los clientes (como sus saldos exactos) sea procesada de forma segura bajo roles de acceso.

## 4. Instrucciones de Ejecución (Modo Docker)

Para desplegar la aplicación completa con persistencia de datos en tiempo real, asegúrese de tener Docker instalado y siga esta secuencia de comandos en su terminal:

### Paso 1: Configurar Variables de Entorno
Cree un archivo `.env` en la raíz del proyecto basándose en `env.example` e inyecte sus credenciales de base de datos AWS.

### Paso 2: Levantar la Infraestructura Base
Ejecute el contenedor en modo *detached* (`-d`), mapeando el volumen actual (`-v`) para que los logs y métricas se sincronicen en vivo con el Dashboard de Streamlit:
```bash
docker run -d -v ${PWD}:/app --env-file .env -p 8501:8501 --name bank-dataops-app kevinfuenzalida/bank-dataops:latest