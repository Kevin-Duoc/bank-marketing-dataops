# DataOps Pipeline & Dashboard: Bank Marketing Analysis

Este proyecto implementa un pipeline robusto de DataOps para la ingesta, limpieza, validación y carga de datos masivos de campañas de marketing bancario en AWS EC2 (Instancia Linux con servidor MySQL), junto con un dashboard interactivo para la visualización de métricas clave.

## 1. Arquitectura del Proyecto
El sistema está dividido en dos componentes independientes y desacoplados:
* **Pipeline (ETL):** Ejecuta la ingesta del dataset original, realiza transformaciones avanzadas de datos con Pandas, valida la integridad de los datos mediante esquemas con Pandera y carga la información optimizada en la base de datos MySQL alojada en AWS EC2.
* **Dashboard (Frontend):** Interfaz interactiva desarrollada en Streamlit que consume directamente los datos alojados en AWS para la toma de decisiones estratégicas.

## 2. Tecnologías Utilizadas
* **Lenguaje:** Python 3.12
* **Procesamiento y Validación:** Pandas, Pandera, NumPy
* **Infraestructura y Nube:** AWS EC2 (Instancia Linux con servidor MySQL)
* **Base de Datos y ORM:** SQLAlchemy, PyMySQL
* **Visualización:** Streamlit
* **Contenedores y Despliegue:** Docker, Docker Hub

## 3. Seguridad y Buenas Prácticas
* **Aislamiento de Entorno:** El proyecto se encuentra completamente dockerizado, garantizando que corra idéntico en cualquier máquina.
* **Gestión de Credenciales:** Las llaves privadas (`.pem`) y credenciales de AWS (`.env`) están estrictamente excluidas del control de versiones mediante reglas avanzadas en `.gitignore` y `.dockerignore`. Se adjunta un archivo `env.example` con la estructura requerida.

## 4. Instrucciones de Ejecución (Modo Docker)

Para desplegar la aplicación completa sin necesidad de instalar dependencias locales, asegúrese de tener Docker instalado y siga estos pasos:

### Paso 1: Configurar Variables de Entorno
Cree un archivo `.env` en la raíz del proyecto basándose en `env.example` e inyecte sus credenciales de AWS.

### Paso 2: Descargar y Ejecutar el Contenedor
Ejecute el siguiente comando para descargar la imagen desde Docker Hub y levantar el Dashboard de Streamlit:
```bash
docker run --env-file .env -p 8501:8501 --name bank-dataops-app kevinfuenzalida/bank-dataops:latest
