import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

# 1 configuración y CSS inyectado
st.set_page_config(page_title="Monitor DataOps", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    
    /* Hacer los números de las métricas principales mucho más grandes */
    [data-testid="stMetricValue"] {font-size: 3.5rem !important; font-weight: bold;}
    [data-testid="stMetricLabel"] {font-size: 1.5rem !important;}
    
    /* Agrandar los subtítulos de Streamlit */
    h2, h3 {font-size: 2rem !important;}
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
    
    # traducciones
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

    # configuración global para letras grandes en Plotly
    plotly_font_config = dict(family="Arial", size=16, color="white")

    # VISTA 1: NEGOCIO Y EDA
    if menu == "Exploración de Datos (EDA)":
        st.title("Análisis Exploratorio de Datos (EDA)")
        
        # Las métricas superiores se mantienen en columnas porque son números cortos
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Volumen Analizado", f"{len(df):,}")
        col2.metric("Edad Promedio", f"{int(df['Edad'].mean())} años")
        col3.metric("Saldo Promedio", f"${df['Saldo Cuenta'].mean():,.0f}")
        tasa = (len(df[df['Depósito Aceptado'] == 'Sí']) / len(df)) * 100 if len(df) > 0 else 0
        col4.metric("Tasa de Conversión", f"{tasa:.1f}%")
            
        st.divider()
        st.subheader("Distribución por Profesión")
        
        # Gráfico 1 - Full Width
        df_jobs = df['Profesión'].value_counts().reset_index()
        df_jobs.columns = ['Profesión', 'Cantidad']
        fig_job = px.bar(df_jobs, x='Cantidad', y='Profesión', orientation='h')
        fig_job.update_layout(yaxis={'categoryorder':'total ascending'}, font=plotly_font_config, height=500)
        st.plotly_chart(fig_job, use_container_width=True)
            
        st.divider()
        st.subheader("Suscripción a Depósito a Plazo")
        
        # Gráfico 2 - Full Width
        df_dep = df['Depósito Aceptado'].value_counts().reset_index()
        df_dep.columns = ['Depósito', 'Cantidad']
        fig_dep = px.pie(df_dep, values='Cantidad', names='Depósito', hole=0.4,
                         color='Depósito', color_discrete_map={'Sí': '#3b82f6', 'No': '#ef4444'})
        fig_dep.update_traces(textinfo='label+percent', textfont_size=20) 
        fig_dep.update_layout(font=plotly_font_config, height=500)
        st.plotly_chart(fig_dep, use_container_width=True)

        st.divider()
        st.subheader("Análisis Bivariado: Edad vs Saldo en Cuenta")
        
        # Gráfico 3 - Full Width
        fig_scatter = px.scatter(df, x="Edad", y="Saldo Cuenta", color="Depósito Aceptado", 
                                 opacity=0.6, color_discrete_map={'Sí': '#3b82f6', 'No': '#ef4444'})
        fig_scatter.update_layout(font=plotly_font_config, height=600)
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()
        st.subheader("Matriz de Correlación Lineal")
        
        # Gráfico 4 - Full Width
        df_num = df.select_dtypes(include=['int64', 'float64'])
        matriz_corr = df_num.corr().round(2)
        fig_corr = px.imshow(matriz_corr, text_auto=True, aspect="auto", color_continuous_scale='Blues')
        fig_corr.update_traces(textfont_size=18) 
        fig_corr.update_layout(font=plotly_font_config, height=700)
        st.plotly_chart(fig_corr, use_container_width=True)

        st.divider()
        
        # explorador interactivo
        st.subheader("Explorador de Datos y Muestreo Dinámico")
        
        col_search, col_slider = st.columns(2)
        busqueda = col_search.text_input("Buscador global de clientes (Ej: married, admin, yes):", "")
        filas_mostrar = col_slider.slider("Tamaño de la muestra a analizar:", min_value=10, max_value=5000, value=100, step=50)
        
        df_mostrar = df.copy()
        if busqueda:
            mask = df_mostrar.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_mostrar = df_mostrar[mask]
            
        df_muestra = df_mostrar.head(filas_mostrar)
        
        st.markdown("**Métricas en tiempo real de la muestra seleccionada:**")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Resultados en pantalla", len(df_muestra))
        mc2.metric("Mayor Saldo", f"${df_muestra['Saldo Cuenta'].max():,.0f}" if not df_muestra.empty else "N/A")
        mc3.metric("Saldo Promedio", f"${df_muestra['Saldo Cuenta'].mean():,.0f}" if not df_muestra.empty else "N/A")
        mc4.metric("Edad Máxima", f"{df_muestra['Edad'].max()} años" if not df_muestra.empty else "N/A")
        
        st.dataframe(df_muestra, use_container_width=True)

    # VISTA 2: IA
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
            
            # tabla de datos
            st.markdown("""
            <style>
            .tabla-final { 
                width: 100%; 
                border-collapse: collapse; 
                color: #e0e0e0; 
                font-size: 18px; 
                font-family: sans-serif;
            }
            .tabla-final th { 
                background-color: #2563eb; 
                color: white;
                padding: 12px 15px; 
                text-align: center; 
                font-weight: 600;
            }
            .tabla-final td { 
                padding: 12px 15px; 
                text-align: center; 
                border-bottom: 1px solid #333; 
            }
            .tabla-final tr:nth-child(even) { background-color: #1a1a1a; }
            .tabla-final tr:hover { background-color: #2d2d2d; }
            </style>
            """, unsafe_allow_html=True)

            tabla_html = "<table class='tabla-final'><tr><th>Modelo</th><th>Exactitud</th><th>Precisión</th><th>Sensibilidad</th><th>F1-Score</th><th>AUC</th><th>Gini</th><th>RAM (MB)</th><th>Latencia (s)</th></tr>"
            for nombre, metrica in metricas.items():
                tabla_html += f"<tr><td><b>{nombre}</b></td><td>{metrica['accuracy']*100:.2f}%</td><td>{metrica['precision']*100:.2f}%</td><td>{metrica['recall']*100:.2f}%</td><td>{metrica['f1']*100:.2f}%</td><td>{metrica['auc']:.2f}</td><td>{metrica['gini']:.2f}</td><td>{metrica['ram_mb']:.2f}</td><td>{metrica['tiempo_s']:.4f}</td></tr>"
            tabla_html += "</table>"
            st.markdown(tabla_html, unsafe_allow_html=True)
            
            st.divider()
            
            # MATRICES DE CONFUSIÓN APILADAS
            st.subheader("Matrices de Confusión (Falsos Positivos/Negativos)")
            modelos_keys = list(metricas.keys())
            
            if 'matriz_confusion' in metricas[modelos_keys[0]]:
                # Matriz Modelo 1
                z1 = metricas[modelos_keys[1]]['matriz_confusion']
                fig_cm1 = px.imshow(z1, text_auto=True, aspect="auto", title=f"Matriz: {modelos_keys[1]}",
                                    labels=dict(x="Predicción de la IA", y="Realidad Histórica"),
                                    x=['No Depósito', 'Sí Depósito'], y=['No Depósito', 'Sí Depósito'],
                                    color_continuous_scale='Blues')
                fig_cm1.update_traces(textfont_size=28) 
                fig_cm1.update_layout(font=plotly_font_config, title_font_size=26, height=550)
                st.plotly_chart(fig_cm1, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Matriz Modelo 2
                z2 = metricas[modelos_keys[0]]['matriz_confusion']
                fig_cm2 = px.imshow(z2, text_auto=True, aspect="auto", title=f"Matriz: {modelos_keys[0]}",
                                    labels=dict(x="Predicción de la IA", y="Realidad Histórica"),
                                    x=['No Depósito', 'Sí Depósito'], y=['No Depósito', 'Sí Depósito'],
                                    color_continuous_scale='Teal')
                fig_cm2.update_traces(textfont_size=28) 
                fig_cm2.update_layout(font=plotly_font_config, title_font_size=26, height=550)
                st.plotly_chart(fig_cm2, use_container_width=True)

            st.divider()
            
            # GRÁFICO DE CURVA ROC
            st.subheader("Curva ROC (Poder de Discriminación)")
            fig_roc = go.Figure()
            colores_roc = ['#008080', '#3b82f6']
            
            for i, m_name in enumerate(modelos_keys):
                if 'roc_fpr' in metricas[m_name] and 'roc_tpr' in metricas[m_name]:
                    fpr = metricas[m_name]['roc_fpr']
                    tpr = metricas[m_name]['roc_tpr']
                    auc_val = metricas[m_name].get('auc', 0)
                    
                    fig_roc.add_trace(go.Scatter(
                        x=fpr, y=tpr, mode='lines', 
                        name=f"{m_name} (AUC={auc_val:.2f})",
                        line=dict(width=4, color=colores_roc[i % len(colores_roc)])
                    ))
            
            # línea base
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode='lines', 
                name="Línea Aleatoria (Sin IA)", 
                line=dict(dash='dash', color='gray', width=2)
            ))
            
            fig_roc.update_layout(
                xaxis_title="Tasa de Falsos Positivos (FPR)",
                yaxis_title="Tasa de Verdaderos Positivos (TPR)",
                font=plotly_font_config,
                title_font_size=24,
                height=700,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(x=0.65, y=0.1, font=dict(size=20)),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig_roc, use_container_width=True)
            
            st.divider()

            # RADARES APILADOS
            st.subheader("Análisis de Trade-Off (Radar)")
            radar_data = []
            for m_name, d in metricas.items():
                radar_data.append({"Modelo": m_name, "Métrica": "Exactitud", "Valor": d.get('accuracy', 0)})
                radar_data.append({"Modelo": m_name, "Métrica": "Precisión", "Valor": d.get('precision', 0)})
                radar_data.append({"Modelo": m_name, "Métrica": "Recall", "Valor": d.get('recall', 0)})
                radar_data.append({"Modelo": m_name, "Métrica": "F1-Score", "Valor": d.get('f1', 0)})
                
            df_radar = pd.DataFrame(radar_data)
            
            polar_layout = dict(
                bgcolor='rgba(0,0,0,0)', 
                radialaxis=dict(visible=True, gridcolor='gray', tickfont=dict(color='white', size=16)),
                angularaxis=dict(tickfont=dict(size=20, color='white'))
            )
            
            # Radar 1
            df_rf = df_radar[df_radar['Modelo'] == modelos_keys[1]]
            fig_r1 = px.line_polar(df_rf, r='Valor', theta='Métrica', line_close=True, title=modelos_keys[1])
            fig_r1.update_traces(fill='toself', line_color='#3b82f6')
            fig_r1.update_layout(polar=polar_layout, paper_bgcolor='rgba(0,0,0,0)', font=plotly_font_config, title_font_size=26, height=600)
            st.plotly_chart(fig_r1, use_container_width=True)
            
            # Radar 2
            df_lr = df_radar[df_radar['Modelo'] == modelos_keys[0]]
            fig_r2 = px.line_polar(df_lr, r='Valor', theta='Métrica', line_close=True, title=modelos_keys[0])
            fig_r2.update_traces(fill='toself', line_color='#008080')
            fig_r2.update_layout(polar=polar_layout, paper_bgcolor='rgba(0,0,0,0)', font=plotly_font_config, title_font_size=26, height=600)
            st.plotly_chart(fig_r2, use_container_width=True)
            
            # Radar Comparativo Global
            fig_r3 = px.line_polar(df_radar, r='Valor', theta='Métrica', color='Modelo', line_close=True, title="Comparativa Global")
            fig_r3.update_traces(fill='toself')
            fig_r3.update_layout(polar=polar_layout, paper_bgcolor='rgba(0,0,0,0)', font=plotly_font_config, title_font_size=26, height=600, legend=dict(font=dict(size=18)))
            st.plotly_chart(fig_r3, use_container_width=True)
            
            st.divider()
            
            #SIMULADOR DE ROI BANCARIO
            st.subheader("Simulador de Impacto Financiero (ROI)")
            st.markdown("Proyección comercial comparando campaña tradicional vs. campaña optimizada por IA (Random Forest).")
            
            #parámetros interactivos para la defensa
            col_roi1, col_roi2, col_roi3 = st.columns(3)
            base_clientes = col_roi1.number_input("Tamaño de la Base de Clientes (Llamadas):", min_value=1000, max_value=100000, value=10000, step=1000)
            costo_llamada = col_roi2.number_input("Costo Operativo por Llamada (CLP):", min_value=500, max_value=5000, value=1500, step=100)
            ganancia_dep = col_roi3.number_input("Ganancia Est. por Depósito (CLP):", min_value=10000, max_value=200000, value=50000, step=5000)
            
            #cálculo del Modelo Tradicional (A ciegas)
            tasa_conversion_historica = 0.12 # 12% de conversión según EDA
            clientes_convertidos_trad = base_clientes * tasa_conversion_historica
            costo_total_trad = base_clientes * costo_llamada
            ingreso_bruto_trad = clientes_convertidos_trad * ganancia_dep
            beneficio_neto_trad = ingreso_bruto_trad - costo_total_trad
            
            #cálculo del Modelo IA (Random Forest)
            precision_rf = metricas.get(modelos_keys[1], {}).get('precision', 0.81)
            recall_rf = metricas.get(modelos_keys[1], {}).get('recall', 0.86)
            
            # IA identifica el 86% de los clientes reales dispuestos a comprar
            clientes_convertidos_ia = clientes_convertidos_trad * recall_rf
            #para lograr esa conversión con 81% de precisión, la IA solo hace esta cantidad de llamadas:
            llamadas_ia = clientes_convertidos_ia / precision_rf if precision_rf > 0 else 0
            
            costo_total_ia = llamadas_ia * costo_llamada
            ingreso_bruto_ia = clientes_convertidos_ia * ganancia_dep
            beneficio_neto_ia = ingreso_bruto_ia - costo_total_ia
            
            #visualización de Resultados Financieros
            mc_roi1, mc_roi2, mc_roi3 = st.columns(3)
            mc_roi1.metric("Llamadas Ahorradas", f"{int(base_clientes - llamadas_ia):,}")
            mc_roi2.metric("Ahorro Operativo (OPEX)", f"${int(costo_total_trad - costo_total_ia):,.0f}")
            mc_roi3.metric("Beneficio Neto Extra (ROI)", f"${int(beneficio_neto_ia - beneficio_neto_trad):,.0f}", delta="Impacto IA")
        else:
            st.warning("Archivo de métricas no encontrado.")

    # VISTA 3: DATAOPS
    elif menu == "Telemetría DataOps":
        st.title("Supervisión del Pipeline ETL y Auditoría")
        
        ruta_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'pipeline.log')
        
        errores_historicos = 0
        errores_ultima_ejecucion = 0
        logs_completos = []
        logs_ultima_ejecucion = []
        
        if os.path.exists(ruta_log):
            with open(ruta_log, 'r', encoding="utf-8", errors="ignore") as f:
                logs_completos = f.readlines()
                
            #Extrae SOLAMENTE la última ejecución para los KPIs
            indice_inicio = 0
            for i in range(len(logs_completos)-1, -1, -1):
                if "INICIANDO EJECUCION INTEGRAL DEL PIPELINE" in logs_completos[i]:
                    indice_inicio = i
                    break
            
            logs_ultima_ejecucion = logs_completos[indice_inicio:]
            
            #contar errores solo en la pasada actual
            for linea in logs_ultima_ejecucion:
                if "ERROR" in linea.upper() or "FALLA" in linea.upper(): 
                    errores_ultima_ejecucion += 1
                        
        #CÁLCULO DE KPIs DINÁMICOS
        filas_cargadas_aws = len(df_base) #alimentado directo de AWS
        salud_pipeline = 100 - (errores_ultima_ejecucion * 5)
        salud_pipeline = max(0, salud_pipeline)
        
        st.subheader("Indicadores Clave de Rendimiento (KPIs)")
        st.markdown("Monitor de salud enfocado en la **última ejecución** del orquestador.")
        
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        
        with col_kpi1:
            st.metric("Completitud de Datos (AWS)", f"{filas_cargadas_aws:,}", delta="Datos Íntegros", delta_color="normal")
            st.markdown("*Volumen persistido en la nube*")
            
        with col_kpi2:
            color_delta = "inverse" if errores_ultima_ejecucion > 0 else "normal"
            estado_contrato = "Vulnerado" if errores_ultima_ejecucion > 0 else "100% Validado"
            st.metric("Fallas de Contrato (Actual)", f"{errores_ultima_ejecucion} Errores", delta=estado_contrato, delta_color=color_delta)
            st.markdown("*Anomalías en la ejecución reciente*")
            
        with col_kpi3:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = salud_pipeline,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Salud del Pipeline", 'font': {'size': 20, 'color': 'white'}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#3b82f6"},
                    'bgcolor': "black",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 60], 'color': "#ef4444"},
                        {'range': [60, 90], 'color': "#f59e0b"},
                        {'range': [90, 100], 'color': "#10b981"}],
                }
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=plotly_font_config, height=300, margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        st.divider()
        
        #buscador de eventos
        st.subheader("Buscador de Eventos (Logs Totales)")
        st.button("Refrescar Logs desde Servidor")
        
        if logs_completos:
            busqueda = st.text_input("Filtro Dinámico (Ej: 'ERROR', 'Fase', 'Pandas'):", "")
            
            #filtro lógico nativo
            if busqueda:
                logs_filtrados = [linea for linea in logs_completos if busqueda.lower() in linea.lower()]
            else:
                logs_filtrados = logs_completos.copy()
                
            logs_filtrados.reverse() # Mostrar recientes arriba
            texto_final = "".join(logs_filtrados) if logs_filtrados else "No se encontraron registros que coincidan con la búsqueda."
            
            st.text_area("Consola de Eventos del Sistema", value=texto_final, height=400, disabled=True)
        else:
            st.warning("No se encontró el archivo de logs. Ejecute el orquestador principal.")
except Exception as e:
    st.error(f"Falla crítica en el sistema: {e}")
