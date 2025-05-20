import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Análisis de Ventas", layout="wide")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("data.csv", parse_dates=["Date"])

df = cargar_datos()

# Preprocesamiento
df['Año'] = df['Date'].dt.year
df['Mes'] = df['Date'].dt.month_name()
df['Hora'] = pd.to_datetime(df['Time'], format='%H:%M').dt.hour

# Sidebar con filtros
st.sidebar.header("Filtros")
selected_branch = st.sidebar.selectbox("Sucursal", options=df['Branch'].unique())
selected_city = st.sidebar.selectbox("Ciudad", options=df['City'].unique())

min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input(
    "Rango de fechas",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Convertir fechas a datetime64
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1]) if len(date_range) > 1 else start_date

# Validar rango de fechas
if start_date > end_date:
    st.sidebar.error("Error: La fecha inicial no puede ser mayor a la final")
    start_date, end_date = end_date, start_date

# Aplicar filtros
df_filtered = df[(df['Branch'] == selected_branch) &
                (df['City'] == selected_city) &
                (df['Date'].between(start_date, end_date))]

# Validar datos filtrados
if df_filtered.empty:
    st.warning("⚠️ No se encontraron datos con los filtros seleccionados")
    st.info("Sugerencias:")
    st.markdown("- Amplía el rango de fechas")
    st.markdown("- Prueba con otra combinación de sucursal/ciudad")
    st.stop()

# Título principal
st.title("Análisis de Ventas - Tienda de Conveniencia")
st.markdown("---")

# Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["Resumen General", "Análisis Temporal", "Comportamiento Clientes", "Relaciones"])

with tab1:
    st.header("Métricas Clave")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ventas Totales", f"${df_filtered['Total'].sum():,.2f}")
    with col2:
        st.metric("Transacciones Promedio", f"${df_filtered['Total'].mean():.2f}")
    with col3:
        st.metric("Clientes Únicos", df_filtered['Invoice ID'].nunique())

    st.subheader("Distribución de Ventas por Línea de Producto")
    fig = px.pie(df_filtered, names='Product line', values='Total',
                 hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Análisis Temporal")

    # Evolución mensual de ventas
    st.subheader("Evolución Mensual de Ventas")
    ventas_mensuales = df_filtered.groupby(['Año', 'Mes'])['Total'].sum().reset_index()
    fig = px.line(ventas_mensuales, x='Mes', y='Total', color='Año',
                  markers=True, title="Tendencia de Ventas Mensuales")
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap de ventas por hora
    st.subheader("Distribución Horaria de Ventas")
    heatmap_data = df_filtered.pivot_table(index='Hora', columns='Product line',
                                         values='Total', aggfunc='sum').fillna(0)
    plt.figure(figsize=(12,6))
    sns.heatmap(heatmap_data, cmap="YlGnBu", annot=True, fmt=".0f")
    st.pyplot(plt)

with tab3:
    st.header("Comportamiento del Cliente")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución de Calificaciones")
        fig = px.histogram(df_filtered, x='Rating', nbins=10,
                         color_discrete_sequence=['#2a9d8f'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Métodos de Pago")
        pagos = df_filtered['Payment'].value_counts()
        fig = px.bar(pagos, color=pagos.index,
                   color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Relaciones Clave")

    st.subheader("Correlación entre Variables")
    corr_matrix = df_filtered[['Unit price', 'Quantity', 'Tax 5%', 'Total', 'Rating']].corr()
    plt.figure(figsize=(10,6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    st.pyplot(plt)

    st.subheader("Relación Costo vs Ganancia")
    fig = px.scatter(df_filtered, x='cogs', y='gross income',
                   color='Product line', trendline="ols")
    st.plotly_chart(fig, use_container_width=True)

# Notas finales
st.markdown("---")
st.markdown("""
**Notas:**
- Los datos se actualizan dinámicamente según los filtros seleccionados
- Puede interactuar con las gráficas (zoom, selección, etc.)
- Los datos monetarios están en dólares
""")
