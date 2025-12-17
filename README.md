 TMDB Mini-Agente: Buscador y Recomendador de Películas con IA
 
Repositorio:
https://github.com/Antonio-Rodriguez10/tmdb-agent-sprint3

Descripción general del agente:

Este proyecto consiste en el desarrollo de un primer agente inteligente sencillo, cuyo objetivo es interactuar con el usuario para buscar películas y generar recomendaciones personalizadas a partir de sus preferencias.
El agente se apoya en la API pública de The Movie Database (TMDB) para obtener información real sobre películas (títulos, géneros, valoraciones, etc.) y utiliza el modelo de lenguaje Groq (LLM) para enriquecer la interacción con el usuario, interpretando mejor sus gustos y aportando explicaciones más naturales en las recomendaciones.
El foco del proyecto no es la complejidad técnica, sino entender cómo se estructura un agente inteligente básico, cómo fluye la información desde la entrada del usuario hasta la respuesta final, y cómo herramientas asistidas por IA pueden acelerar su creación.

Propósito del agente:

Permitir al usuario buscar una película o introducir un concepto general (por ejemplo, un actor, un estilo o un género).
 Ayudarle a seleccionar la película que realmente tiene en mente cuando hay varios resultados posibles.
 Detectar los géneros principales de esa película.
 Generar recomendaciones de películas similares, filtradas por género si el usuario lo desea.
 Aportar una explicación sencilla y natural sobre las recomendaciones realizadas, usando un modelo de lenguaje.
Este agente simula el comportamiento de un asistente inteligente básico de recomendación de contenidos audiovisuales.

Herramientas y tecnologías utilizadas:

Para la creación del agente se han utilizado las siguientes herramientas:
GitHub
 Se ha creado un repositorio público para versionar el proyecto, documentarlo y facilitar su revisión.
Python
 Lenguaje utilizado para implementar la lógica del agente, por su sencillez y legibilidad.
API de The Movie Database (TMDB)
 Se utiliza como fuente de datos reales sobre películas, géneros y recomendaciones.
Modelo de lenguaje Groq (LLM) vía API
 Se integra un LLM para aportar una capa de razonamiento y generación de texto más natural, mejorando la interacción con el usuario.
Chatgpt
El código se ha refinado mediante una herramienta asistida por IA (ChatGPT), siguiendo un enfoque de programación guiada.

Flujo lógico de la interacción del agente:

El funcionamiento del agente sigue un flujo sencillo y claro:
Primero, el agente solicita al usuario un texto inicial, que puede ser el nombre de una película o una referencia general (por ejemplo, un actor o estilo).
Con esa información, el agente consulta la API de TMDB y muestra una lista de posibles películas relacionadas.
El usuario selecciona la película que realmente tenía en mente.
A partir de esa película, el agente obtiene información adicional como géneros y valoraciones.
De forma opcional, el usuario puede indicar un género concreto para afinar las recomendaciones.
El agente recupera una lista de películas recomendadas y las ordena según su valoración.
Finalmente, el agente utiliza el modelo de lenguaje para presentar las recomendaciones de forma más natural, explicando el porqué de las sugerencias.
Este flujo reproduce el ciclo básico de percepción (entrada del usuario), procesamiento (consultas, filtros y razonamiento) y acción (respuesta final).

Fundamentos de programación presentes en el ejemplo:

Aunque el código es sencillo, en este proyecto se aplican varios conceptos fundamentales de programación:
Variables
 Se utilizan para almacenar datos como el texto introducido por el usuario, las películas obtenidas desde la API, los géneros o las recomendaciones finales.
Estructuras de control
 El agente toma decisiones en función de distintas condiciones, por ejemplo:
 – si el usuario no introduce texto, se termina la ejecución
 – si no hay resultados de búsqueda, se muestra un mensaje adecuado
 – si el usuario decide filtrar por género, se aplica ese filtro
 Estas decisiones se implementan mediante estructuras condicionales.
Funciones
 La lógica del agente se divide en funciones con responsabilidades claras, como buscar películas, obtener detalles, recuperar recomendaciones o formatear resultados. Esto permite reutilizar código y hacer el flujo más comprensible.
Entrada y salida
 El agente interactúa continuamente con el usuario a través de preguntas y respuestas por consola, simulando una conversación básica.

Resultado de la interacción:

El resultado final es un agente funcional que permite mantener una interacción sencilla con el usuario, ofreciendo resultados reales y recomendaciones personalizadas.
El agente responde a preguntas básicas, interpreta elecciones del usuario y genera salidas comprensibles, mostrando cómo un LLM puede potenciar un agente tradicional basado únicamente en reglas y consultas a una API.

<img width="1919" height="1133" alt="image (38)" src="https://github.com/user-attachments/assets/5ad7b36f-6d2b-4715-941e-432813bbb3ca" />


Código utilizado: 

import os
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

TMDB_API_BASE = "https://api.themoviedb.org/3"


def get_auth():
    load_dotenv()
    api_key = os.getenv("TMDB_API_KEY")
    bearer = os.getenv("TMDB_READ_ACCESS_TOKEN")

    if bearer:
        return {"headers": {"Authorization": f"Bearer {bearer}"}, "params_base": {}}
    if api_key:
        return {"headers": {}, "params_base": {"api_key": api_key}}

    print("No se encontró TMDB_API_KEY ni TMDB_READ_ACCESS_TOKEN", file=sys.stderr)
    sys.exit(1)


def tmdb_get(path, params=None):
    auth = get_auth()
    url = f"{TMDB_API_BASE}{path}"
    final_params = dict(auth["params_base"])
    if params:
        final_params.update(params)
    r = requests.get(url, headers=auth["headers"], params=final_params, timeout=20)
    r.raise_for_status()
    return r.json()


def search_movie(query):
    return tmdb_get(
        "/search/movie",
        {"query": query, "include_adult": "false", "language": "es-ES", "page": 1},
    )


def get_movie_details(movie_id):
    return tmdb_get(f"/movie/{movie_id}", {"language": "es-ES"})


def get_movie_recommendations(movie_id):
    return tmdb_get(
        f"/movie/{movie_id}/recommendations",
        {"language": "es-ES", "page": 1},
    )


def get_genres():
    return tmdb_get("/genre/movie/list", {"language": "es-ES"}).get("genres", [])


def pick_number(prompt, min_n, max_n):
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            n = int(raw)
            if min_n <= n <= max_n:
                return n
        print(f"Elige un número entre {min_n} y {max_n}.")


def normalize(s):
    return s.strip().lower()


def find_genre_id_by_name(genres, name):
    name = normalize(name)
    for g in genres:
        if normalize(g.get("name", "")) == name:
            return g.get("id")
    return None


def movie_line(m):
    title = m.get("title") or "Sin título"
    date = m.get("release_date") or "¿?"
    rating = m.get("vote_average")
    rating_txt = f"{rating:.1f}" if isinstance(rating, (int, float)) else "¿?"
    return f"{title} ({date}) — rating: {rating_txt}"


def llm_commentary(base_title, base_genres, recs):
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return "(No hay GROQ_API_KEY configurada)"

    client = OpenAI(
        api_key=groq_key,
        base_url="https://api.groq.com/openai/v1",
    )

    candidates = [
        {
            "title": m.get("title"),
            "release_date": m.get("release_date"),
            "vote_average": m.get("vote_average"),
        }
        for m in recs[:10]
    ]

    system = (
        "Eres un recomendador de cine. Responde en español, tono directo. "
        "Elige 3 películas y explica por qué encajan con la película base."
    )

    user = f"""
Película base: {base_title}
Géneros: {base_genres}

Candidatas:
{candidates}

Devuelve 3 recomendaciones numeradas con una breve justificación.
"""

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
    )

    return resp.choices[0].message.content.strip()


def main():
    print("TMDB mini-agente (buscador + recomendador)\n")

    query = input("Dime una película para buscar: ").strip()
    if not query:
        return

    results = search_movie(query).get("results", [])[:7]
    if not results:
        print("No encontré resultados.")
        return

    print("\nResultados:")
    for i, m in enumerate(results, 1):
        print(f"{i}. {movie_line(m)}")

    choice = pick_number("\nElige una (número): ", 1, len(results))
    picked = results[choice - 1]

    details = get_movie_details(picked["id"])
    base_title = details.get("title", "esa peli")
    base_genres = details.get("genres", [])
    base_genre_names = ", ".join(g["name"] for g in base_genres) if base_genres else "¿?"

    print(f"\nReferencia: {base_title}")
    print(f"Géneros: {base_genre_names}\n")

    all_genres = get_genres()
    genre_input = input("¿Filtrar por género? (Enter para saltar): ").strip()

    genre_id = None
    if genre_input:
        genre_id = find_genre_id_by_name(all_genres, genre_input)

    recs = get_movie_recommendations(picked["id"]).get("results", [])
    if genre_id:
        recs = [m for m in recs if genre_id in (m.get("genre_ids") or [])]

    recs_sorted = sorted(
        recs, key=lambda x: x.get("vote_average") or 0, reverse=True
    )[:10]

    print("Recomendaciones (TMDB):")
    for i, m in enumerate(recs_sorted, 1):
        print(f"{i}. {movie_line(m)}")

    print("\nComentario del LLM:")
    print(llm_commentary(base_title, base_genre_names, recs_sorted))


if __name__ == "__main__":
    main()




