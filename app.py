import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# --- CONFIGURACIÓN DE TMDB ---
API_KEY = 'f14a6ad63fd7df06f327d2e2547cef36'
BASE_URL = 'https://api.themoviedb.org/3'

# --- FUNCIONES DE LÓGICA (Mantenidas de tu main.py) ---

def obtener_generos():
    # ... (Tu función original)
    url = f'{BASE_URL}/genre/movie/list?api_key={API_KEY}&language=es-ES'
    response = requests.get(url)
    data = response.json()
    return {genre['id']: genre['name'] for genre in data['genres']}

def obtener_peliculas_populares(num_peliculas=20): 
    # ... (Tu función original)
    peliculas = []
    unique_titles = set()
    while len(peliculas) < num_peliculas * 2: # Buscar el doble por si hay duplicados
        pagina_aleatoria = random.randint(1, 40) 
        url = f'{BASE_URL}/movie/popular?api_key={API_KEY}&language=es-ES&page={pagina_aleatoria}'
        response = requests.get(url)
        if response.status_code != 200:
            break
        data = response.json()['results']
        for peli in data:
            if peli['title'] not in unique_titles:
                peliculas.append(peli)
                unique_titles.add(peli['title'])
    return peliculas[:num_peliculas]

def obtener_peliculas_por_genero(genero_id, cantidad=3):
    # ... (Tu función original, usada solo para Fallback)
    url = f'{BASE_URL}/discover/movie?api_key={API_KEY}&language=es-ES&with_genres={genero_id}&sort_by=popularity.desc'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results'][:cantidad]
    return []

def calcular_distancia_euclidea(vec1, vec2):
    # ... (Tu función original)
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return float('inf')
    return np.sqrt(np.sum((np.array(vec1) - np.array(vec2))**2))

# --- MANEJO DE ESTADO Y UI (Streamlit) ---

def inicializar_estado(generos_dict):
    if 'peliculas' not in st.session_state:
        st.session_state.peliculas = obtener_peliculas_populares(20)
        st.session_state.indice = 0
        st.session_state.generos_dict = generos_dict
        st.session_state.peliculas_gustadas = []
        # Matriz para el grafo de afinidad (aunque la reco usa k-NN)
        st.session_state.matriz = pd.DataFrame([0]*len(generos_dict), index=generos_dict.values(), columns=['Usuario'])
        st.session_state.genero_ids_list = list(generos_dict.keys())

def me_gusta():
    peli = st.session_state.peliculas[st.session_state.indice]
    
    # 1. ACTUALIZAR MATRIZ PARA EL GRAFO
    for gid in peli.get('genre_ids', []):
        nombre = st.session_state.generos_dict.get(gid)
        if nombre:
            st.session_state.matriz.loc[nombre, 'Usuario'] += 1

    # 2. CREAR EL VECTOR BINARIO PARA K-NN
    vector_genero = [1 if gid in peli.get('genre_ids', []) else 0 
                     for gid in st.session_state.genero_ids_list]
    
    st.session_state.peliculas_gustadas.append({
        'id': peli['id'],
        'titulo': peli['title'],
        'vector': vector_genero
    })
    
    st.session_state.indice += 1

def no_gusta():
    st.session_state.indice += 1

def mostrar_grafo():
    G = nx.DiGraph()
    G.add_node("Usuario", color="#e50914")
    
    # Asegurarse de que la matriz no esté vacía
    if not st.session_state.matriz.empty:
        for genero, peso in st.session_state.matriz['Usuario'].items():
            if peso > 0:
                G.add_node(genero, color="#1DB954")
                G.add_edge("Usuario", genero, weight=peso)
    
    pos = nx.spring_layout(G, seed=42)
    colors = [nx.get_node_attributes(G, 'color').get(n, '#CCCCCC') for n in G.nodes] # Color por defecto si no está en el diccionario
    weights = [G[u][v]['weight'] for u, v in G.edges]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    nx.draw(G, pos, ax=ax, with_labels=True, node_color=colors, edge_color='gray',
            width=[w * 0.5 for w in weights], font_size=10, node_size=1500, font_color='white')
    nx.draw_networkx_edge_labels(G, pos, ax=ax,
            edge_labels={(u, v): G[u][v]['weight'] for u, v in G.edges}, font_color='#e50914')
    
    ax.set_title("🔗 Grafo de Preferencias (Afinidad por Género)", color='white', fontsize=14)
    ax.set_facecolor("#141414")
    fig.patch.set_facecolor("#141414")
    st.pyplot(fig)


def mostrar_recomendaciones():
    # --- Mostrar Afinidad y Grafo ---
    st.header("📊 Preferencias Recolectadas")
    st.dataframe(st.session_state.matriz.sort_values(by='Usuario', ascending=False), 
                 use_container_width=True, hide_index=False)
    mostrar_grafo()
    
    st.markdown("---")
    st.header("🎉 Recomendaciones k-NN")
    
    # --- Lógica de k-NN ---
    K = 5
    generos_ids_list = st.session_state.genero_ids_list
    
    if len(st.session_state.peliculas_gustadas) < 2:
        st.warning("Marca al menos 2 películas como favoritas para generar recomendaciones k-NN.")
        return
        
    candidatas = obtener_peliculas_populares(30) 
    recomendaciones_finales = []
    
    for candidata in candidatas:
        if candidata['id'] in [p['id'] for p in st.session_state.peliculas_gustadas]:
            continue
            
        vector_candidata = [1 if gid in candidata.get('genre_ids', []) else 0 
                            for gid in generos_ids_list]

        distancias = []
        for peli_gustada in st.session_state.peliculas_gustadas:
            dist = calcular_distancia_euclidea(vector_candidata, peli_gustada['vector'])
            distancias.append({'distancia': dist, 'peli': peli_gustada['titulo']})

        distancias.sort(key=lambda x: x['distancia'])
        k_vecinos = distancias[:K]

        # Criterio k-NN: Distancia baja (similaridad alta) a la película gustada más cercana
        if k_vecinos[0]['distancia'] <= 1.5: 
            if candidata not in recomendaciones_finales:
                recomendaciones_finales.append(candidata)
        
        if len(recomendaciones_finales) >= 5: 
            break

    # --- Mostrar Resultados ---
    if not recomendaciones_finales:
        st.info("No se encontraron películas muy similares a tus favoritas (k-NN no clasificó ninguna con alta confianza).")
    else:
        for i, peli in enumerate(recomendaciones_finales, 1):
            generos_reco = [st.session_state.generos_dict.get(gid, '') for gid in peli['genre_ids']]
            anio = peli.get('release_date', '????')[:4]
            st.markdown(f"**{i}. {peli['title']} ({anio})**")
            st.caption(f"🎭 {', '.join(generos_reco)}")

def mostrar_interfaz_principal():
    peli = st.session_state.peliculas[st.session_state.indice]
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Póster")
        poster_path = peli.get('poster_path')
        poster_url = f"https://image.tmdb.org/t/p/w342{poster_path}" if poster_path else None
        
        if poster_url:
            try:
                st.image(poster_url, width=250)
            except:
                st.warning("No se pudo cargar el póster.")
        else:
            st.markdown("*(Póster no disponible)*")

    with col2:
        st.subheader(peli.get('title', 'Sin título'))
        generos = [st.session_state.generos_dict.get(gid, '') for gid in peli.get('genre_ids', [])]
        st.caption(f"**Géneros:** {', '.join(generos)}")
        st.markdown(f"**Resumen:** {peli.get('overview', 'Sin resumen disponible')}")

    st.markdown("---")
    
    st.subheader("Swipe & Decide")
    
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
    
    with btn_col1:
        if st.button("❌ No me gusta", use_container_width=True):
            no_gusta()
            st.rerun()

    with btn_col3:
        if st.button("❤️ Me gusta", use_container_width=True, type="primary"):
            me_gusta()
            st.rerun()
    
    with btn_col2:
        # Espacio central
        st.markdown(f"**Película {st.session_state.indice + 1} / {len(st.session_state.peliculas)}**")
        
    st.markdown("---")
    
# --- FUNCIÓN PRINCIPAL DE STREAMLIT ---

def main():
    
    # Aplicar el estilo del póster (Netflix/Minimalista Oscuro)
    st.set_page_config(
        page_title="Swipe&Watch k-NN Demo",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items=None,
    )
    
    # Custom CSS para el diseño rojo
    st.markdown("""
        <style>
        .st-emotion-cache-1jm77ly { 
            background-color: #141414; /* Fondo principal oscuro */
        }
        .stButton>button {
            color: white !important;
            border-radius: 8px;
            font-weight: bold;
        }
        .stButton>button:first-child {
            background-color: #e50914; /* Rojo Netflix para primary */
            border-color: #e50914;
        }
        .stButton>button:hover {
            opacity: 0.8;
        }
        h1, h2, h3, h4, .stCaption {
            color: white !important;
        }
        
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🎬 Swipe&Watch (k-NN Demo)")
    st.markdown("Aplica 'Me gusta' o 'No me gusta' a las películas para entrenar el modelo.")
    st.markdown("---")

    generos = obtener_generos()
    inicializar_estado(generos)

    if st.session_state.indice < len(st.session_state.peliculas):
        mostrar_interfaz_principal()
    else:
        mostrar_recomendaciones()

if __name__ == "__main__":
    main()