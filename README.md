# Pipeline de Datos - Realidad Virtual (VR)

Este proyecto implementa un pipeline de datos automatizado para la ingesta, limpieza y validación de un dataset sobre experiencias en Realidad Virtual.

## Estructura del Proyecto
* `/data/raw/`: Contiene el dataset original descargado desde la API de Kaggle.
* `/data/processed/`: Contiene el dataset limpio y transformado (`vr_clean.csv`) y el validado (`vr_validated.csv`).
* `/data/reports/`: Almacena los reportes automáticos de registros con errores.
* `/src/ingesta.py`: Script que se conecta a Kaggle, autentica el token y descarga los datos automáticamente.
* `/src/limpieza.py`: Script que procesa los datos crudos aplicando transformaciones.
* `/src/validacion.py`: Script que aplica contratos de datos (Pandera) para validación estructural y semántica.
* `/logs/`: Almacena el registro de ejecución del pipeline (`pipeline.log`).

## Transformaciones Aplicadas (Limpieza)
1. **Eliminación de duplicados:** Se verificó y eliminó la existencia de registros idénticos.
2. **Estandarización de texto:** Se limpiaron los espacios en blanco y se aplicó formato capitalizado a las columnas `Gender` y `VRHeadset`.
3. **Tratamiento de Nulos:** Se rellenaron los valores nulos de `Age` utilizando la mediana de la columna.
4. **Estandarización numérica:** Se redondeó la columna `Duration` a 2 decimales para facilitar su lectura y análisis.
5. **Columna Derivada:** Se creó la nueva columna `Riesgo_Mareo` clasificando a los usuarios en "Alto Riesgo" o "Bajo Riesgo" según su nivel de `MotionSickness`.

## Validación Estructural y Semántica
Se implementó un script de validación utilizando la librería **Pandera** (`src/validacion.py`) que aplica el siguiente esquema de calidad:
- **Validaciones Estructurales:** Se verificó la unicidad de la clave primaria (`UserID`), se exigió que la duración (`Duration`) no sea nula, y se controló que la edad sea un número positivo mayor a 0.
- **Validaciones Semánticas:** Se filtraron registros con edades fuera del rango lógico (10 a 100 años) y se verificó que la columna `Riesgo_Mareo` solo contenga los valores permitidos ('Alto Riesgo', 'Bajo Riesgo').
- **Manejo de Errores:** Los datos que superan el contrato se guardan en `vr_validated.csv`. Los registros que no cumplen las reglas son capturados y guardados en un reporte automático en `/data/reports/errores_pandera.csv`.