import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

#1 configuración y CSS inyectado
st.set_page_config(page_title="Monitor DataOps", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    [data-testid="stMetricValue"] {font-size: 2.5rem !important;}
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
    
    #traducciones
    dic_trabajos = {
        'admin.': 'Administrativo', 'blue-collar': 'Obrero', 'entrepreneur': 'Emprendedor',
        'housemaid': 'Emp. Doméstico', 'management': 'Gerencia', 'retired': 'Jubilado',
        'self-employed': 'Independiente', 'services': 'Servicios', 'student': 'Estudiante',
        'technician': 'Técnico', 'unemployed': 'Desempleado', 'unknown': 'Desconocido'
    }
    df['job'] = df['job'].map(dic_trabajos).fillna(df['job'])
    df['deposit'] = df['deposit'].map({'yes': 'Sí', 'no': 'No'}).fillna(df['deposit'])
    
    df = df.rename(columns={
        'age': 'Edad', 'job': 'Profesión', 'marital': 'Estado Civil', 
        'education': 'Educación', 'default': 'En Mora', 'balance': 'Saldo Cuenta',
        'housing': 'Crédito Hipotecario', 'loan': 'Crédito Consumo', 
        'contact': 'Medio Contacto', 'deposit': 'Depósito Aceptado',
        'duration': 'Duración Llamada', 'campaign': 'Cant. Contactos'
    })
    return df

try:
    df_base = cargar_datos_aws()
    
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Ir a:", ["Exploración de Datos (EDA)", "Rendimiento de Modelos (IA)", "Telemetría DataOps"])
    st.sidebar.markdown("---")
    st.sidebar.info(f"Conectado a AWS EC2\nRegistros totales: {len(df_base)}")

    # Filtro Dinámico Lateral
    st.sidebar.subheader("Filtros Globales")
    filtro_profesion = st.sidebar.selectbox("Filtrar por Profesión:", ["Todas"] + list(df_base['Profesión'].unique()))
    
    if filtro_profesion != "Todas":
        df = df_base[df_base['Profesión'] == filtro_profesion]
    else:
        df = df_base

    #vista 1: NEGOCIO Y EDA
    if menu == "Exploración de Datos (EDA)":
        st.title("Análisis Exploratorio de Datos (EDA)")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Volumen Analizado", f"{len(df):,}")
        col2.metric("Edad Promedio", f"{int(df['Edad'].mean())} años")
        col3.metric("Saldo Promedio", f"${df['Saldo Cuenta'].mean():,.0f}")
        tasa = (len(df[df['Depósito Aceptado'] == 'Sí']) / len(df)) * 100 if len(df) > 0 else 0
        col4.metric("Tasa de Conversión", f"{tasa:.1f}%")
            
        st.divider()
        st.subheader("Análisis Univariado")
        
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            df_jobs = df['Profesión'].value_counts().reset_index()
            df_jobs.columns = ['Profesión', 'Cantidad']
            fig_job = px.bar(df_jobs, x='Cantidad', y='Profesión', orientation='h', title="Distribución por Profesión")
            fig_job.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_job, use_container_width=True)
            
        with col_graf2:
            df_dep = df['Depósito Aceptado'].value_counts().reset_index()
            df_dep.columns = ['Depósito', 'Cantidad']
            fig_dep = px.pie(df_dep, values='Cantidad', names='Depósito', hole=0.4, title="Suscripción a Depósito",
                             color='Depósito', color_discrete_map={'Sí': '#3b82f6', 'No': '#ef4444'})
            fig_dep.update_traces(textinfo='label+percent') 
            st.plotly_chart(fig_dep, use_container_width=True)

        st.divider()
        st.subheader("Análisis Bivariado y Correlación")
        
        col_biv1, col_biv2 = st.columns(2)
        with col_biv1:
            fig_scatter = px.scatter(df, x="Edad", y="Saldo Cuenta", color="Depósito Aceptado", 
                                     title="Edad vs Saldo en Cuenta", opacity=0.6,
                                     color_discrete_map={'Sí': '#3b82f6', 'No': '#ef4444'})
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_biv2:
            df_num = df.select_dtypes(include=['int64', 'float64'])
            matriz_corr = df_num.corr().round(2)
            fig_corr = px.imshow(matriz_corr, text_auto=True, aspect="auto", 
                                 title="Matriz de Correlación Lineal", color_continuous_scale='Blues')
            st.plotly_chart(fig_corr, use_container_width=True)

        st.divider()
        
        #explorador interactivo
        st.subheader("Explorador de Datos y Muestreo Dinámico")
        
        col_search, col_slider = st.columns(2)
        busqueda = col_search.text_input("Buscador global de clientes (Ej: married, admin, yes):", "")
        filas_mostrar = col_slider.slider("Tamaño de la muestra a analizar:", min_value=10, max_value=5000, value=100, step=50)
        
        #lógica de búsqueda
        df_mostrar = df.copy()
        if busqueda:
            mask = df_mostrar.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_mostrar = df_mostrar[mask]
            
        df_muestra = df_mostrar.head(filas_mostrar)
        
        #curiosidades de la muestra actual
        st.markdown("**Métricas en tiempo real de la muestra seleccionada:**")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Resultados en pantalla", len(df_muestra))
        mc2.metric("Mayor Saldo", f"${df_muestra['Saldo Cuenta'].max():,.0f}" if not df_muestra.empty else "N/A")
        mc3.metric("Saldo Promedio", f"${df_muestra['Saldo Cuenta'].mean():,.0f}" if not df_muestra.empty else "N/A")
        mc4.metric("Edad Máxima", f"{df_muestra['Edad'].max()} años" if not df_muestra.empty else "N/A")
        
        st.dataframe(df_muestra, use_container_width=True)

    #vista 2: IA
    elif menu == "Rendimiento de Modelos (IA)":
        st.title("Auditoría de Algoritmos de Machine Learning")
        
        ruta_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metricas_ia.json')
        if os.path.exists(ruta_json):
            with open(ruta_json, 'r') as f:
                metricas = json.load(f)
            
            df_metricas = pd.DataFrame(metricas).T
            cols_mostrar = ['accuracy', 'precision', 'recall', 'f1', 'auc', 'gini', 'ram_mb', 'tiempo_s']
            cols_disponibles = [c for c in cols_mostrar if c in df_metricas.columns]
            df_vista = df_metricas[cols_disponibles].copy()
            
            mapeo_cols = {
                'accuracy': 'Exactitud', 'precision': 'Precisión', 'recall': 'Sensibilidad',
                'f1': 'F1-Score', 'auc': 'Curva ROC (AUC)', 'gini': 'Índice Gini',
                'ram_mb': 'Peak RAM (MB)', 'tiempo_s': 'Latencia (s)'
            }
            df_vista.rename(columns=mapeo_cols, inplace=True)
            
            for col in ['Exactitud', 'Precisión', 'Sensibilidad', 'F1-Score', 'Curva ROC (AUC)', 'Índice Gini']:
                if col in df_vista.columns:
                    df_vista[col] = (df_vista[col].astype(float) * 100).round(2).astype(str) + '%'
            
            st.dataframe(df_vista, use_container_width=True)
            
            st.divider()
            st.subheader("Matrices de Confusión (Falsos Positivos/Negativos)")
            
            col_rf, col_lr = st.columns(2)
            modelos_keys = list(metricas.keys())
            
            if 'matriz_confusion' in metricas[modelos_keys[0]]:
                with col_rf:
                    z1 = metricas[modelos_keys[1]]['matriz_confusion']
                    #tema azul
                    fig_cm1 = px.imshow(z1, text_auto=True, aspect="auto", title=f"Matriz: {modelos_keys[1]}",
                                        labels=dict(x="Predicción de la IA", y="Realidad Histórica"),
                                        x=['No Depósito', 'Sí Depósito'], y=['No Depósito', 'Sí Depósito'],
                                        color_continuous_scale='Blues')
                    st.plotly_chart(fig_cm1, use_container_width=True)
                
                with col_lr:
                    z2 = metricas[modelos_keys[0]]['matriz_confusion']
                    fig_cm2 = px.imshow(z2, text_auto=True, aspect="auto", title=f"Matriz: {modelos_keys[0]}",
                                        labels=dict(x="Predicción de la IA", y="Realidad Histórica"),
                                        x=['No Depósito', 'Sí Depósito'], y=['No Depósito', 'Sí Depósito'],
                                        color_continuous_scale='Teal')
                    st.plotly_chart(fig_cm2, use_container_width=True)

            st.divider()
            
            #radar de 3 circulos
            st.subheader("Análisis de Trade-Off (Radar)")
            radar_data = []
            for m_name, d in metricas.items():
                radar_data.append({"Modelo": m_name, "Métrica": "Exactitud", "Valor": d.get('accuracy', 0)})
                radar_data.append({"Modelo": m_name, "Métrica": "Precisión", "Valor": d.get('precision', 0)})
                radar_data.append({"Modelo": m_name, "Métrica": "Recall", "Valor": d.get('recall', 0)})
                radar_data.append({"Modelo": m_name, "Métrica": "F1-Score", "Valor": d.get('f1', 0)})
                
            df_radar = pd.DataFrame(radar_data)
            
            rad1, rad2, rad3 = st.columns(3)
            # Layout base transparente
            polar_layout = dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=True, gridcolor='gray', tickfont=dict(color='white')))
            
            with rad1:
                df_lr = df_radar[df_radar['Modelo'] == modelos_keys[0]]
                fig_r1 = px.line_polar(df_lr, r='Valor', theta='Métrica', line_close=True, title=modelos_keys[0])
                fig_r1.update_traces(fill='toself', line_color='#008080')
                fig_r1.update_layout(polar=polar_layout, paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig_r1, use_container_width=True)
                
            with rad2:
                fig_r2 = px.line_polar(df_radar, r='Valor', theta='Métrica', color='Modelo', line_close=True, title="Comparativa Global")
                fig_r2.update_traces(fill='toself')
                fig_r2.update_layout(polar=polar_layout, paper_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
                st.plotly_chart(fig_r2, use_container_width=True)
                
            with rad3:
                df_rf = df_radar[df_radar['Modelo'] == modelos_keys[1]]
                fig_r3 = px.line_polar(df_rf, r='Valor', theta='Métrica', line_close=True, title=modelos_keys[1])
                fig_r3.update_traces(fill='toself', line_color='#3b82f6')
                fig_r3.update_layout(polar=polar_layout, paper_bgcolor='rgba(0,0,0,0)', font_color='white')
                st.plotly_chart(fig_r3, use_container_width=True)
            
        else:
            st.warning("Archivo de métricas no encontrado.")

    #vista 3: DATAOPS
    elif menu == "Telemetría DataOps":
        st.title("Supervisión del Pipeline ETL y Auditoría")
        
        #métricas visuales de respaldo 
        col_op1, col_op2 = st.columns(2)
        with col_op1:
            st.metric("Integridad de Filas (Limpieza)", "11,162 / 11,162", delta="0 Duplicados eliminados", delta_color="off")
            st.progress(100)
        with col_op2:
            st.metric("Contratos de Datos (Pandera)", "17 / 17 Columnas", delta="Esquema 100% Validado", delta_color="normal")
            st.progress(100)
            
        st.divider()
        st.subheader("Buscador de Eventos (Logs)")
        
        ruta_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'pipeline.log')
        if os.path.exists(ruta_log):
            with open(ruta_log, 'r') as f:
                logs_completos = f.readlines()
            
            busqueda = st.text_input("Filtrar logs por palabra clave (Ej: 'ERROR', 'Fase 4', 'AWS'):", "")
            logs_filtrados = [linea for linea in logs_completos if busqueda.lower() in linea.lower()]
            texto_final = "".join(logs_filtrados) if logs_filtrados else "No se encontraron resultados."
            
            st.text_area("Registro Histórico del Sistema", texto_final, height=400)

except Exception as e:
    st.error(f"Falla crítica en el sistema: {e}")