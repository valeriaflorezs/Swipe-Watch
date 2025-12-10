# 🎬 Swipe & Watch: Sistema de Recomendación Basado en k-NN y Grafos

Un proyecto innovador que combina la usabilidad moderna (patrón "Swipe") con algoritmos de Machine Learning (`k-NN`) y modelado de datos mediante la **Teoría de Grafos** para generar recomendaciones de películas personalizadas.

🔗 Ver Demo (streamlit)[https://swipe-and-watch.streamlit.app/]

## 🎯 Objetivo del Proyecto

El objetivo principal de *Swipe & Watch* es demostrar la implementación práctica de algoritmos de recomendación en un entorno interactivo y moderno.

  * Utilizamos el patrón de "swipe" (similar a Tinder) para **recoger datos de afinidad del usuario en tiempo real** .
  * Posteriormente, aplicamos el algoritmo **k-Nearest Neighbors (k-NN)** para clasificar y recomendar nuevas películas.

Este proyecto fue desarrollado como parte de una evaluación en **Matemáticas Discretas**, enfocándose en la **Teoría de Grafos** y su aplicación en la modelización de relaciones complejas, lo que resulta en un modelo de recomendación híbrido y explicable.

## ⚙️ Tecnologías y Algoritmos

| Componente | Tecnología/Algoritmo | Propósito |
| :--- | :--- | :--- |
| **Frontend/Web App** | Streamlit, Python | Interfaz de usuario interactiva y despliegue rápido. |
| **Recomendación** | **k-Nearest Neighbors (k-NN)** | Clasifica películas candidatas basándose en la similaridad de género con las películas que el usuario ha gustado. |
| **Métrica de Similitud** | **Distancia Euclídea** | Mide la similitud entre los vectores de género de las películas. |
| **Modelado de Datos** | **Grafo Bipartito Ponderado** | Representa la relación Usuario-Género mediante una matriz de adyacencia (Afinidad). |
| **API de Datos** | The Movie Database (TMDB) | Obtención de datos de películas (títulos, pósters, géneros). |
| **Visualización** | NetworkX, Matplotlib, Pandas | Creación y visualización del grafo de afinidad, y manejo de datos. |

## 💡 El Modelo Híbrido Explicado

El sistema opera en dos fases clave, utilizando los conceptos de **Grafos** para el modelado de afinidad y **k-NN** para la predicción de preferencias.

### Fase 1: Modelado de Afinidad con Grafos (Entrenamiento)

Esta fase establece el perfil de gusto del usuario mediante la Teoría de Grafos:

1.  **Mecanismo de Entrada:** El usuario clasifica películas populares con "Me gusta" o "No me gusta".
2.  **Grafo Bipartito:** Se construye una relación entre el **Nodo Usuario** y los **Nodos Género** .
3.  **Peso de la Arista:** La arista entre el Usuario y un Género se **pondera** (incrementa en 1) cada vez que el usuario aprueba una película con ese género.
4.  **Resultado:** Se genera una **Matriz de Afinidad** y un Grafo, donde el grosor de las aristas (su peso) indica las preferencias más fuertes del usuario.

### Fase 2: Recomendación con k-NN (Clasificación de Ítems)

Utilizamos el perfil de afinidad generado en la Fase 1 como base para la predicción:

1.  **Set de Entrenamiento:** Son las películas que el usuario marcó con "Me gusta", representadas como vectores binarios de género.

2.  **Set de Prueba:** Películas candidatas (no vistas) que buscamos clasificar.

3.  **Cálculo de Distancia:** Se calcula la Distancia Euclídea entre el vector de género de la película candidata y el vector de cada película gustada.

    $$\text{Distancia Euclídea} = \sqrt{\sum_{i=1}^{N} (A_i - B_i)^2}$$

4.  **Clasificación:** El sistema identifica las $K$ películas más cercanas ($K=5$). Si la distancia al vecino más cercano es baja (alta similaridad de género), la película candidata es clasificada como una recomendación.

## 🚀 Instalación y Despliegue

### Requisitos

Asegúrate de tener Python 3.8+ instalado. Instala las dependencias necesarias:

```bash
pip install streamlit pandas requests numpy matplotlib networkx
```

### Ejecución Local

1.  Guarda el código actualizado como `app.py`.

2.  Ejecuta la aplicación desde tu terminal:

    ```bash
    streamlit run app.py
    ```

3.  Accede a la aplicación en `http://localhost:8501`.

### Despliegue en Streamlit Cloud

Para desplegar tu aplicación en Streamlit Cloud:

1.  Sube `app.py` y un archivo `requirements.txt` con las dependencias a tu repositorio de GitHub.
2.  Conecta tu repositorio a Streamlit Cloud. ¡Estará online en minutos\!

## 👥 Desarrolladores

| Nombre | Rol |
| :--- | :--- |
| **Valeria Florez Sarmiento** | Desarrolladora Principal |

Este proyecto es una muestra de la aplicación de la **Teoría de Grafos** y la **Ciencia de Datos** en sistemas de recomendación modernos y explicables.
