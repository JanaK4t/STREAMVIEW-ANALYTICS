import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración inicial del dashboard ancho
st.set_page_config(
    page_title="Dashboard Analítico - Gerencia de Contenidos", layout="wide"
)

st.title("Dashboard Analítico (Gerencia de Contenidos y Adquisición)")
st.markdown(
    "Exploración profunda de datos y correlaciones estadísticas."
)


# Carga de datos optimizada con caché
@st.cache_data
def load_data():
  # Carga ambos datasets
  df_movies = pd.read_csv("data/movies_limpio.csv")
  df_tv = pd.read_csv("data/tv_limpio.csv")

  # Asegurar que tengan una columna que los distinga si no la traen
  df_movies["type"] = "Movie"
  df_tv["type"] = "TV Show"

  # Unir verticalmente ambos datasets en uno solo
  df_combinado = pd.concat([df_movies, df_tv], ignore_index=True)

  return df_combinado

df_combinado = load_data()

st.sidebar.header("Filtros Avanzados y Umbrales")


# 1. Ajustar el slider para que su valor máximo sea realista (por ejemplo, 1000)
min_votos = st.sidebar.slider(
    "Umbral mínimo de votos para análisis",
    min_value=0,
    max_value=1000,  # Ajustado al máximo real de los datos (~975)
    value=100,
    step=25,
    help="Filtra títulos con pocos votos para evitar distorsiones estadísticas.",
)


# Aplicar el filtro al dataframe
df_filtrado = df_combinado[df_combinado["vote_count"] >= min_votos]

# 3. Mostrar la métrica contando explícitamente a df_filtrado
st.sidebar.metric("Títulos analizados", len(df_filtrado))



# Limpiar nulos en las columnas clave antes del gráfico
# Limpiar nulos asegurando que conservemos ambos tipos de contenido
df_filtrado = df_combinado.dropna(
    subset=["popularity", "vote_average", "vote_count", "type"]
)

st.subheader("Correlación: Popularidad vs. Calificación")

# Gráfico de dispersión con Plotly Express usando las columnas correctas del esquema
fig_scatter = px.scatter(
    df_filtrado,
    x="popularity",
    y="vote_average",  # Usamos la calificación numérica real del esquema
    color="type",  # Esto separará automáticamente 'Movie' y 'TV Show' en la leyenda
    size="vote_count",
    hover_name="title",
    labels={
        "popularity": "Índice de Popularidad",
        "vote_average": "Calificación Promedio (Vote Average)",
    },
    template="plotly_dark",
)

st.plotly_chart(fig_scatter, use_container_width=True)


# 1. Separar el DataFrame en dos subconjuntos independientes
df_peliculas = df_filtrado[df_filtrado["type"] == "Movie"]
df_series = df_filtrado[df_filtrado["type"] == "TV Show"]

st.subheader(
    "Análisis por Género: Películas vs. Series de TV (Popularidad y Calificación)"
)

# Creamos dos columnas visuales para separar ambos mundos
col_gen1, col_gen2 = st.columns(2)

# --- ANÁLISIS DE GÉNEROS: PELÍCULAS ---
with col_gen1:
  st.markdown("Géneros en Películas")
  if "genres" in df_peliculas.columns:
    # Separar géneros múltiples por comas y expandirlos en filas individuales
    df_m_gen = df_peliculas.assign(
        genres=df_peliculas["genres"].astype(str).str.split(",")
    ).explode("genres")
    df_m_gen["genres"] = df_m_gen["genres"].str.strip()

    # Agrupar por género calculando los promedios
    df_agg_m = (
        df_m_gen.groupby("genres")[["popularity", "vote_average"]]
        .mean()
        .reset_index()
    )
    df_agg_m = df_agg_m.sort_values(by="popularity", ascending=False).head(10)

    # Gráfico de barras agrupadas para películas
    fig_gen_movies = px.bar(
        df_agg_m,
        x="genres",
        y=["popularity", "vote_average"],
        barmode="group",
        labels={
            "value": "Métrica Promedio",
            "genres": "Género",
            "variable": "Indicador",
        },
        template="plotly_dark",
    )
    st.plotly_chart(fig_gen_movies, use_container_width=True)

with col_gen2:
  st.markdown("Géneros en Series de TV")
  if "genres" in df_series.columns:
    # Separar géneros múltiples por comas y expandirlos en filas individuales
    df_s_gen = df_series.assign(
        genres=df_series["genres"].astype(str).str.split(",")
    ).explode("genres")
    df_s_gen["genres"] = df_s_gen["genres"].str.strip()

    # Agrupar por género calculando los promedios
    df_agg_s = (
        df_s_gen.groupby("genres")[["popularity", "vote_average"]]
        .mean()
        .reset_index()
    )
    df_agg_s = df_agg_s.sort_values(by="popularity", ascending=False).head(10)

    # Gráfico de barras agrupadas para series
    fig_gen_series = px.bar(
        df_agg_s,
        x="genres",
        y=["popularity", "vote_average"],
        barmode="group",
        labels={
            "value": "Métrica Promedio",
            "genres": "Género",
            "variable": "Indicador",
        },
        template="plotly_dark",
    )
    st.plotly_chart(fig_gen_series, use_container_width=True)

st.subheader("Treemap: Volumen de Contenido por Género")

# Unimos de nuevo los dataframes limpios o usamos el combinado filtrado
# Asegurándonos de separar y expandir los géneros si vienen juntos por comas
df_treemap = df_filtrado.assign(
    genres=df_filtrado["genres"].astype(str).str.split(",")
).explode("genres")
df_treemap["genres"] = df_treemap["genres"].str.strip()

# Agrupar para contar el volumen de títulos por Tipo y Género
df_grouped_tree = (
    df_treemap.groupby(["type", "genres"])
    .size()
    .reset_index(name="volumen_titulos")
)

# Crear el gráfico de Treemap con Plotly Express
fig_treemap = px.treemap(
    df_grouped_tree,
    path=[
        "type",
        "genres",
    ],  # Jerarquía: primero divide por Tipo (Movie/TV Show) y luego por Género
    values="volumen_titulos",  # El tamaño del bloque depende de la cantidad de títulos
    color="volumen_titulos",  # El color varía según el volumen
    color_continuous_scale="Viridis",
    template="plotly_dark",
    title="Distribución de Volumen de Títulos por Tipo y Género",
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.subheader("Top 10 Títulos Mejor Evaluados (Con Umbral de Votos)")

# Creamos dos columnas visuales para separar películas y series mejor evaluadas
col_top1, col_top2 = st.columns(2)

# --- TOP PELÍCULAS MEJOR EVALUADAS ---
with col_top1:
  st.markdown("Películas Mejor Evaluadas")
  df_top_movies_rated = df_filtrado[df_filtrado["type"] == "Movie"].sort_values(by="vote_average", ascending=False).head(10)

  fig_top_m = px.bar(
      df_top_movies_rated,
      x="vote_average",
      y="title",
      orientation="h",
      text="vote_average",
      labels={
          "vote_average": "Calificación Promedio",
          "title": "Película",
      },
      template="plotly_dark",
  )
  fig_top_m.update_traces(texttemplate="%{text:.2f}", textposition="outside")
  fig_top_m.update_layout(yaxis={"categoryorder": "total ascending"})
  st.plotly_chart(fig_top_m, use_container_width=True)

# --- TOP SERIES DE TV MEJOR EVALUADAS ---
with col_top2:
  st.markdown("Series de TV Mejor Evaluadas")
  df_top_series_rated = df_filtrado[df_filtrado["type"] == "TV Show"].sort_values(
      by="vote_average", ascending=False
  ).head(10)

  fig_top_s = px.bar(
      df_top_series_rated,
      x="vote_average",
      y="title",
      orientation="h",
      text="vote_average",
      labels={
          "vote_average": "Calificación Promedio",
          "title": "Serie",
      },
      template="plotly_dark",
  )
  fig_top_s.update_traces(texttemplate="%{text:.2f}", textposition="outside")
  fig_top_s.update_layout(yaxis={"categoryorder": "total ascending"})
  st.plotly_chart(fig_top_s, use_container_width=True)

st.subheader("Top Directores y Actores por Volumen de Contenido")

col_da1, col_da2 = st.columns(2)

# --- TOP ACTORES / ELENCO (cast) ---
with col_da1:
  st.markdown("Top Actores con Más Títulos")
  if "cast" in df_filtrado.columns:
    # Separar actores múltiples por comas y expandir
    df_cast = df_filtrado.assign(
        cast=df_filtrado["cast"].astype(str).str.split(",")
    ).explode("cast")
    df_cast["cast"] = df_cast["cast"].str.strip()

    # Contar la cantidad de títulos por actor (excluyendo valores vacíos o nulos)
    df_top_cast = (
        df_cast[df_cast["cast"] != "Unknown"]
        .groupby("cast")
        .size()
        .reset_index(name="total_titulos")
    )
    df_top_cast = df_top_cast.sort_values(by="total_titulos", ascending=False).head(10)

    fig_cast = px.bar(
        df_top_cast,
        x="total_titulos",
        y="cast",
        orientation="h",
        labels={"total_titulos": "Cantidad de Títulos", "cast": "Actor / Elenco"},
        template="plotly_dark",
    )
    fig_cast.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_cast, use_container_width=True)

# --- TOP DIRECTORES (si tus datos tienen columna de director) ---
with col_da2:
  st.markdown("Top Directores con Más Títulos")
  # Verificamos si existe la columna 'director' en los datos
  col_dir = "director" if "director" in df_filtrado.columns else "creators"

  if col_dir in df_filtrado.columns:
    df_dir = df_filtrado.assign(
        col_dir=df_filtrado[col_dir].astype(str).str.split(",")
    ).explode("col_dir")
    df_dir["col_dir"] = df_dir["col_dir"].str.strip()

    df_top_dir = (
        df_dir[df_dir["col_dir"] != "Unknown"]
        .groupby("col_dir")
        .size()
        .reset_index(name="total_titulos")
    )
    df_top_dir = df_top_dir.sort_values(
        by="total_titulos", ascending=False
    ).head(10)

    fig_dir = px.bar(
        df_top_dir,
        x="total_titulos",
        y="col_dir",
        orientation="h",
        labels={"total_titulos": "Cantidad de Títulos", "col_dir": "Director"},
        template="plotly_dark",
    )
    fig_dir.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_dir, use_container_width=True)
  else:
    st.info(
        "La columna de director no está disponible en este esquema de datos."
    )

st.subheader("Mapa Coroplético: Popularidad y Calificación Promedio por País")

df_paises = df_filtrado.assign(country=df_filtrado["country"].astype(str).str.split(",")).explode("country")
df_paises["country"] = df_paises["country"].str.strip()

  # 2. Control deslizante para el umbral mínimo de títulos por país
min_titulos_pais = st.sidebar.slider(
      "Mínimo de títulos por país para el mapa",
      min_value=1,
      max_value=100,
      value=5,
      step=1,
      help=(
          "Filtra países con pocos títulos para asegurar promedios confiables."
      ),
  )

  # 3. Agrupar por país calculando el promedio y el conteo de títulos
df_agg_pais = (
      df_paises[df_paises["country"] != ""]
      .groupby("country")
      .agg(
          popularity_promedio=("popularity", "mean"),
          vote_average_promedio=("vote_average", "mean"),
          total_titulos=("title", "count"),
      )
      .reset_index()
  )

  # 4. Aplicar el umbral mínimo de títulos por país
df_paises_filtrado = df_agg_pais[
      df_agg_pais["total_titulos"] >= min_titulos_pais
  ]

  # 5. Selector para que la gerencia elija qué métrica ver en el mapa
metrica_mapa = st.selectbox(
      "Selecciona la métrica a visualizar en el mapa:",
      options=["popularity_promedio", "vote_average_promedio"],
      format_func=lambda x: (
          "Popularidad Promedio"
          if x == "popularity_promedio"
          else "Calificación Promedio"
      ),
  )

  # 6. Crear el mapa coroplético con Plotly Express
fig_mapa = px.choropleth(
      df_paises_filtrado,
      locations="country",
      locationmode="country names",  # Reconoce nombres de países en inglés/español estándar
      color=metrica_mapa,
      hover_name="country",
      hover_data=["total_titulos", "popularity_promedio", "vote_average_promedio"],
      color_continuous_scale="Viridis",
      template="plotly_dark",
      labels={
          "popularity_promedio": "Popularidad Promedio",
          "vote_average_promedio": "Calificación Promedio",
          "total_titulos": "Total de Títulos",
      },
      title=(
          "Distribución Geográfica de"
          f" {'Popularidad' if metrica_mapa == 'popularity_promedio' else 'Calificación'}"
      ),
  )

st.plotly_chart(fig_mapa, use_container_width=True)
st.sidebar.metric("Paises analizados", len(df_paises_filtrado))
