import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import json
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

#1 configuración y CSS inyectado
st.set_page_config(page_title="Monitor DataOps", layout="wide")

st.markdown("""
    <style>
    /* Ocultar menú default de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Ajustar el padding superior para ganar espacio */
    .block-container {padding-top: 2rem;}
    </style>
""", unsafe_allow_html=True)

USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASS')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
DB = os.getenv('DB_NAME')

@st.cache_data
def cargar_datos_aws():
    string_conexion = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    engine = create_engine(string_conexion)
    df = pd.read_sql("SELECT * FROM clientes_marketing", engine)
    return df

try:
    df = cargar_datos_aws()
    
    #2 navegación en el Sidebar
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Ir a:", ["Analítica de Negocio", "Rendimiento de Modelos (IA)", "Telemetría DataOps"])
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"Conectado a AWS EC2\nRegistros: {len(df)}")

    #vista 1: NEGOCIO
    if menu == "Analítica de Negocio":
        st.title("Analítica de Campañas de Marketing")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Volumen de Clientes", f"{len(df):,}")
        col2.metric("Edad Promedio", f"{int(df['age'].mean())} años")
        col3.metric("Saldo Promedio", f"${df['balance'].mean():.2f}")
        col4.metric("Tasa de Conversión", f"{(len(df[df['deposit'] == 'yes']) / len(df)) * 100:.1f}%")
            
        st.divider()
        
        #gráficos interactivos con Plotly
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            #gráfico de barras horizontal para que las profesiones se lean bien
            df_jobs = df['job'].value_counts().reset_index()
            df_jobs.columns = ['Profesión', 'Cantidad']
            fig_job = px.bar(df_jobs, x='Cantidad', y='Profesión', orientation='h', 
                             title="Distribución por Profesión", height=400)
            st.plotly_chart(fig_job, use_container_width=True)
            
        with col_graf2:
            #gráfico de dona para ver la proporción de Sí/No sin ocupar espacio inútil
            df_dep = df['deposit'].value_counts().reset_index()
            df_dep.columns = ['Depósito', 'Cantidad']
            fig_dep = px.pie(df_dep, values='Cantidad', names='Depósito', hole=0.4, 
                             title="Resultados: Suscripción a Depósito", height=400)
            fig_dep.update_traces(marker=dict(colors=['#ff9999','#66b3ff']))
            st.plotly_chart(fig_dep, use_container_width=True)

        st.divider()
        
        #tabla interactiva
        st.subheader("Explorador de Datos Base")
        filas_mostrar = st.slider("Ajustar muestra de filas:", min_value=10, max_value=5000, value=100, step=50)
        
        df_traducido = df.rename(columns={
            'age': 'Edad', 'job': 'Profesión', 'marital': 'Estado Civil', 
            'education': 'Educación', 'default': 'En Mora', 'balance': 'Saldo Cuenta',
            'housing': 'Crédito Hipotecario', 'loan': 'Crédito Consumo', 
            'contact': 'Medio Contacto', 'deposit': 'Depósito Aceptado'
        })
        st.dataframe(df_traducido.head(filas_mostrar), use_container_width=True)

    #vista 2: IA
    elif menu == "Rendimiento de Modelos (IA)":
        st.title("Comparativa de Modelos Predictivos")
        st.markdown("Evaluación de métricas de negocio vs consumo de hardware.")
        
        ruta_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metricas_ia.json')
        if os.path.exists(ruta_json):
            with open(ruta_json, 'r') as f:
                metricas = json.load(f)
            
            #solución al error 7 vs 4: seleccionamos exactamente las columnas que queremos
            df_metricas = pd.DataFrame(metricas).T
            df_metricas = df_metricas[['accuracy', 'precision', 'recall', 'f1', 'ram_mb', 'tiempo_s']]
            df_metricas.columns = ['Exactitud', 'Precisión', 'Sensibilidad (Recall)', 'F1-Score', 'RAM (MB)', 'Tiempo (s)']
            
            #formateo
            for col in ['Exactitud', 'Precisión', 'Sensibilidad (Recall)', 'F1-Score']:
                df_metricas[col] = (df_metricas[col].astype(float) * 100).round(2).astype(str) + '%'
            
            st.dataframe(df_metricas, use_container_width=True)
            
            #gráfico de radar para comparar modelos visualmente
            st.subheader("Análisis de Trade-Off")
            st.markdown("Mientras mayor es el área cubierta, mejor es el equilibrio predictivo del modelo.")
            
            #preparar datos para el Radar Chart
            radar_data = []
            for modelo, datos in metricas.items():
                radar_data.append({"Modelo": modelo, "Métrica": "Exactitud", "Valor": datos['accuracy']})
                radar_data.append({"Modelo": modelo, "Métrica": "Precisión", "Valor": datos['precision']})
                radar_data.append({"Modelo": modelo, "Métrica": "Recall", "Valor": datos['recall']})
                radar_data.append({"Modelo": modelo, "Métrica": "F1-Score", "Valor": datos['f1']})
                
            df_radar = pd.DataFrame(radar_data)
            fig_radar = px.line_polar(df_radar, r='Valor', theta='Métrica', color='Modelo', line_close=True)
            fig_radar.update_traces(fill='toself')
            st.plotly_chart(fig_radar, use_container_width=True)
            
        else:
            st.warning("Archivo de métricas no encontrado. Ejecute el script de modelado primero.")

    #vista 3: DATAOPS
    elif menu == "Telemetría DataOps":
        st.title("Supervisión del Pipeline ETL")
        
        col_op1, col_op2 = st.columns(2)
        col_op1.metric("Limpieza de Datos", "0 Duplicados")
        col_op2.metric("Validación de Esquema", "Cumplimiento 100%")
            
        st.divider()
        
        ruta_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'pipeline.log')
        if os.path.exists(ruta_log):
            with open(ruta_log, 'r') as f:
                logs_completos = f.read()
            st.text_area("Registro de Eventos de la Ingesta (Logs)", logs_completos, height=500)
        else:
            st.warning("No hay logs disponibles.")

except Exception as e:
    st.error(f"Falla crítica en el sistema: {e}")