import pandera as pa
import logging
import os

##ya no es necesario debido a la ruta /src/etc
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# LOG_DIR = os.path.join(BASE_DIR, 'logs')
# os.makedirs(LOG_DIR, exist_ok=True)
# LOG_FILE = os.path.join(LOG_DIR, 'pipeline.log')

# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

def validar_datos(df):
    try:
        logging.info("Fase 3: Iniciando validacion de Contratos de Datos (Pandera)...")
        
        #contrato estricto
        schema = pa.DataFrameSchema({
            "age": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(18)),
            "job": pa.Column(str),
            "marital": pa.Column(str, checks=pa.Check.isin(["married", "divorced", "single", "unknown"])),
            "education": pa.Column(str, checks=pa.Check.isin(["primary", "secondary", "tertiary", "unknown"])),
            "default": pa.Column(str, checks=pa.Check.isin(["yes", "no"])),
            "balance": pa.Column(int), #permite negativos
            "housing": pa.Column(str, checks=pa.Check.isin(["yes", "no"])),
            "loan": pa.Column(str, checks=pa.Check.isin(["yes", "no"])),
            "contact": pa.Column(str, checks=pa.Check.isin(["cellular", "telephone", "unknown"])),
            "day": pa.Column(int, checks=pa.Check.in_range(1, 31)),
            "month": pa.Column(str, checks=pa.Check.isin(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])),
            "duration": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(0)),
            "campaign": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(1)),
            "pdays": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(-1)), # -1 significa no contactado previamente
            "previous": pa.Column(int, checks=pa.Check.greater_than_or_equal_to(0)),
            "poutcome": pa.Column(str, checks=pa.Check.isin(["unknown", "other", "failure", "success"])),
            "deposit": pa.Column(str, checks=pa.Check.isin(["yes", "no"]))
        }, coerce=True)

        df_validado = schema.validate(df)
        
        logging.info("Validacion exitosa: Todos los registros cumplen con el contrato de calidad.")
        
        return df_validado

    except pa.errors.SchemaError as e:
        logging.error(f"Falla Critica: Contrato de datos roto. Detalles: {e}")
        raise e
    except Exception as e:
        logging.error(f"Error inesperado en Fase de Validacion: {e}")
        raise e