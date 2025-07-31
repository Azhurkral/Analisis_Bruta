import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", delimiter=';')
    df['Fecha'] = pd.to_datetime(df['Fecha'], format="%d/%m/%Y")
    return df

df = load_data()

st.title("Análisis de caída de bruta en baterías")

# Identificar los tipos de datos y sus columnas
tipo_datos = df['Grafico'].unique()
columnas_por_tipo = {
    tipo: df[df['Grafico'] == tipo].drop(columns=['Fecha', 'Grafico']).columns.tolist()
    for tipo in tipo_datos
}

# Crear diccionario para almacenar selecciones del usuario
selecciones = {}

# Mostrar selectores
for tipo in tipo_datos:
    columnas = columnas_por_tipo[tipo]
    seleccion = st.multiselect(f"Selecciona pozos para '{tipo}':", columnas)
    selecciones[tipo] = seleccion

# Selector para eje secundario por tipo de grafico
tipo_secundario = st.multiselect(
    "Selecciona los tipos de datos para mostrar en el eje Y secundario:",
    list(tipo_datos)
)

# Preparar figura con eje Y secundario
fig, ax1 = plt.subplots(figsize=(14, 8))
ax2 = ax1.twinx()

curvas_agregadas = 0
columnas_para_tabla = []
fechas_tabla = set()

for tipo, cols in selecciones.items():
    if not cols:
        continue
    df_tipo = df[df['Grafico'] == tipo]
    for col in cols:
        if col in df_tipo.columns:
            subdf = df_tipo[['Fecha', col]].dropna()
            if tipo in tipo_secundario:
                ax2.plot(subdf['Fecha'], subdf[col], linestyle='-', label=f"{tipo}: {col}")
            else:
                ax1.plot(subdf['Fecha'], subdf[col], marker='o', linestyle='-', label=f"{tipo}: {col}")
            curvas_agregadas += 1
            fechas_tabla.update(subdf['Fecha'].tolist())
            columnas_para_tabla.append((tipo, col))

if curvas_agregadas > 0:
    ax1.set_xlabel("Fecha")
    ax1.set_ylabel("Eje Y primario")
    ax2.set_ylabel("Eje Y secundario")
    ax1.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)

    # Formato de fechas: mostrar texto cada 7 días, pero líneas menores cada 1 día
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax1.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
    fig.autofmt_xdate()

    # Línea vertical azul en el 03-07-2025
    fecha_evento = pd.to_datetime("03/07/2025", format="%d/%m/%Y")
    ax1.axvline(fecha_evento, color='blue', linestyle='--')

    # Combinar leyendas de ambos ejes y colocar fuera del gráfico
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=(1.01, 1))

    ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    st.pyplot(fig)

else:
    st.info("Selecciona al menos una columna para visualizar el gráfico.")

