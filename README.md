# Pipeline de Datos - Realidad Virtual (VR)

Este proyecto implementa un pipeline de datos automatizado para la ingesta y limpieza de un dataset sobre experiencias en Realidad Virtual.

## Estructura del Proyecto
* `/data/raw/`: Contiene el dataset original descargado desde la API de Kaggle.
* `/data/processed/`: Contiene el dataset limpio y transformado (`vr_clean.csv`).
* `/src/ingesta.py`: Script que se conecta a Kaggle, autentica el token y descarga los datos automáticamente.
* `/src/limpieza.py`: Script que procesa los datos crudos aplicando transformaciones.
* `/logs/`: Almacena el registro de ejecución del pipeline (`pipeline.log`).

## Transformaciones Aplicadas (Limpieza)
1. **Eliminación de duplicados:** Se verificó y eliminó la existencia de registros idénticos.
2. **Estandarización de texto:** Se limpiaron los espacios en blanco y se aplicó formato capitalizado a las columnas `Gender` y `VRHeadset`.
3. **Tratamiento de Nulos:** Se rellenaron los valores nulos de `Age` utilizando la mediana de la columna.
4. **Estandarización numérica:** Se redondeó la columna `Duration` a 2 decimales para facilitar su lectura y análisis.
5. **Columna Derivada:** Se creó la nueva columna `Riesgo_Mareo` clasificando a los usuarios en "Alto Riesgo" o "Bajo Riesgo" según su nivel de `MotionSickness`.