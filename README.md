# Pipeline de Datos - Optimización de Campañas de Marketing Bancario 🚀

Este proyecto implementa un pipeline de datos automatizado (ETL) bajo prácticas **DataOps** para la ingesta, limpieza, validación semántica y carga centralizada de un dataset sobre depósitos a plazo fijo e historiales financieros del banco.

## Estructura del Proyecto

* `/data/raw/`: Contiene el dataset original del banco (`02_bank.csv`).
* `/data/processed/`: Contiene los archivos intermedios: el dataset limpio (`bank_clean.csv`) y el dataset validado bajo contrato de datos (`bank_validated.csv`).
* `/data/reports/`: Almacena el reporte automático de anomalías (`errores_pandera.csv`).
* `/src/ingesta.py`: Script de ingesta automatizada de la fuente de datos.
* `/src/limpieza.py`: Script que procesa los datos brutos con Pandas, estandariza campos y genera variables analíticas.
* `/src/validacion.py`: Script que aplica contratos de datos estrictos (Pandera) a nivel estructural y semántico.
* `/src/carga.py`: Script de carga masiva y segura hacia el servidor de base de datos relacional.
* `/logs/`: Almacena el registro de auditoría y métricas de observabilidad (`pipeline.log`).

## Transformaciones y Reglas de Limpieza (Pandas)

1. **Eliminación de Duplicados:** Detección y remoción de registros idénticos para evitar sesgos analíticos.
2. **Estandarización de Texto:** Limpieza de espacios en blanco en columnas categóricas (`job`, `marital`, `education`).
3. **Tratamiento de Valores Nulos:** Imputación inteligente de registros vacíos y conversión de valores incompatibles.
4. **Estandarización Numérica:** Redondeo óptimo de métricas financieras de la campaña (`balance`, `duration`).
5. **Generación de Columna Derivada (Feature Engineering):** Creación de la columna `perfil_cliente`, clasificando automáticamenete a los usuarios en categorías financieras (*'Deudor'*, *'Regular'*, *'Premium'*, *'No Identificado'*) según su comportamiento de saldo anual (`balance`).

## Validación Estructural y Semántica (Contrato de Datos con Pandera)

Para garantizar la máxima calidad de los datos antes de la carga, el script `src/validacion.py` ejecuta una validación perezosa (*lazy validation*) mediante la librería **Pandera**:
* **Validaciones Estructurales:** Exigencia de no-nulidad en balances financieros y control de tipos de datos estrictos.
* **Validaciones Semánticas:** Filtrado estricto de anomalías de negocio (ej. asegurar que el rango de edad (`age`) se encuentre exclusivamente entre 18 y 120 años, y que la duración de llamadas (`duration`) sea un número positivo).
* **Aislamiento de Anomalías:** Las filas que cumplen el contrato avanzan a la fase de carga. Los registros corruptos o fuera de norma son extraídos y guardados automáticamente en un reporte analítico en `/data/reports/errores_pandera.csv` para su posterior auditoría.

## Carga de Datos y Arquitectura Cloud (MySQL en AWS EC2)

El módulo de carga (`src/carga.py`) centraliza la información procesada directamente en la infraestructura en la nube del proyecto:
* **Infraestructura Cloud:** Conexión remota optimizada a un servidor MySQL Server alojado en una instancia de computación **AWS EC2 (Ubuntu)** de alta disponibilidad.
* **Gobierno de Datos y Seguridad:** El script implementa un control robusto de excepciones. Si el puente de red hacia la nube falla, el sistema intercepta el código nativo `2003` y genera una alerta limpia en consola: `Error al conectarse con la instancia EC2. El error técnico es: [Detalle]`.
* **Inserción Eficiente (DML):** Recreación automatizada de la tabla estructurada `bank_marketing` (escapando palabras reservadas del motor como `` `default` ``) y ejecución de inserciones masivas seguras usando `executemany` combinado con control transaccional (`commit`).

## Monitoreo y KPIs de Observabilidad (DataOps)

El pipeline registra de forma automatizada y obligatoria tres Indicadores Clave de Rendimiento (KPIs) en el archivo centralizado `/logs/pipeline.log` al finalizar cada ejecución:

1. **Latencia de Ejecución de Carga (Time-to-Data):** Mide en segundos el tiempo exacto que le toma al pipeline inyectar el lote de datos a AWS a través de internet, permitiendo detectar degradaciones de red.
2. **Tasa de Completitud de Datos (Data Completeness):** Cuantifica el porcentaje de registros inyectados con éxito en la nube frente al volumen procesado, asegurando que las transformaciones no destruyan registros de valor.
3. **Tasa de Fallas en Contratos de Datos (Data Quality Error Rate):** Registra el porcentaje exacto de anomalías semánticas detectadas por Pandera, funcionando como un sistema de alerta temprana ante cambios imprevistos en los formatos del banco.
