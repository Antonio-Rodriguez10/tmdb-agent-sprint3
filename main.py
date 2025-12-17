import os
import sys
import requests
from dotenv import load_dotenv


# -----------------------------
# Config / Auth
# -----------------------------
TMDB_API_BASE = "https://api.themoviedb.org/3"


def get_auth():
    """
    Devuelve un dict con:
      - headers (si usa token v4)
      - params_base (si usa api_key v3)
    """
    load_dotenv()

    api_key = os.getenv("TMDB_API_KEY")
    bearer = os.getenv("TMDB_READ_ACCESS_TOKEN")

    if bearer:  # token v4
        return {
            "headers": {"Authorization": f"Bearer {bearer}"},
            "params_base": {},
        }
    if api_key:  # api key v3
        return {
            "headers": {},
            "params_base": {"api_key": api_key},
        }

    print("No se encontró TMDB_API_KEY ni TMDB_READ_ACCESS_TOKEN en tu .env", file=sys.stderr)
    print("Revisa que tu archivo .env exista y tenga una de estas variables.", file=sys.stderr)
    sys.exit(1)


def tmdb_get(path: str, params: dict | None = None):
    auth = get_auth()
    url = f"{TMDB_API_BASE}{path}"

    final_params = dict(auth["params_base"])
    if params:
        final_params.update(params)

    r = requests.get(url, headers=auth["headers"], params=final_params, timeout=20)
    r.raise_for_status()
    return r.json()


# -----------------------------
# TMDB calls
# -----------------------------
def search_movie(query: str):
    return tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": "false",
            "language": "es-ES",
            "page": 1,
        },
    )


def get_movie_details(movie_id: int):
    return tmdb_get(
        f"/movie/{movie_id}",
        {"language": "es-ES"},
    )


def get_movie_recommendations(movie_id: int):
    # Puedes usar /recommendations o /similar. /recommendations suele ir mejor.
    return tmdb_get(
        f"/movie/{movie_id}/recommendations",
        {"language": "es-ES", "page": 1},
    )


def get_genres():
    data = tmdb_get("/genre/movie/list", {"language": "es-ES"})
    return data.get("genres", [])


# -----------------------------
# Helpers
# -----------------------------
def pick_number(prompt: str, min_n: int, max_n: int) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw.isdigit():
            print("Dame un número, por favor.")
            continue
        n = int(raw)
        if n < min_n or n > max_n:
            print(f"Elige un número entre {min_n} y {max_n}.")
            continue
        return n


def normalize(s: str) -> str:
    return s.strip().lower()


def find_genre_id_by_name(genres: list[dict], name: str):
    name = normalize(name)
    for g in genres:
        if normalize(g.get("name", "")) == name:
            return g.get("id")
    return None


def movie_line(m: dict) -> str:
    title = m.get("title") or m.get("name") or "Sin título"
    date = m.get("release_date") or "¿?"
    rating = m.get("vote_average")
    rating_txt = f"{rating:.1f}" if isinstance(rating, (int, float)) else "¿?"
    return f"{title} ({date}) — rating: {rating_txt}"


# -----------------------------
# Main
# -----------------------------
def main():
    print("TMDB mini-agente (buscador + recomendador)\n")

    query = input("Dime una película para buscar (para entender tu estilo): ").strip()
    if not query:
        print("No me has dado nada. Fin.")
        return

    data = search_movie(query)
    results = data.get("results", [])[:7]

    if not results:
        print("No encontré nada con ese título.")
        return

    print("\nResultados:")
    for i, m in enumerate(results, 1):
        print(f"{i}. {movie_line(m)}")

    choice = pick_number("\nElige la peli que querías decir (número): ", 1, len(results))
    picked = results[choice - 1]
    movie_id = picked["id"]

    details = get_movie_details(movie_id)
    base_title = details.get("title", "esa peli")
    base_genres = details.get("genres", [])
    base_genre_names = ", ".join(g["name"] for g in base_genres) if base_genres else "¿?"

    print(f"\nOK. Tomo como referencia: {base_title}")
    print(f"Géneros de esa peli: {base_genre_names}\n")

    # Género (opcional)
    all_genres = get_genres()
    genre_input = input(
        "Si quieres, dime un género para afinar (ej: Ciencia ficción, Acción, Thriller). "
        "Si no, pulsa Enter: "
    ).strip()

    genre_id = None
    if genre_input:
        genre_id = find_genre_id_by_name(all_genres, genre_input)
        if not genre_id:
            print("No pillé ese género tal cual. Sigo sin filtrar por género.\n")
        else:
            print(f"Perfecto. Filtro por género: {genre_input}\n")

    rec = get_movie_recommendations(movie_id)
    recs = rec.get("results", [])

    if not recs:
        print("No tengo recomendaciones para esa película.")
        return

    # Filtrado por género si aplica
    if genre_id:
        recs = [m for m in recs if genre_id in (m.get("genre_ids") or [])]

    # Orden simple por rating y mostramos top 10
    recs_sorted = sorted(
        recs,
        key=lambda x: (x.get("vote_average") or 0),
        reverse=True,
    )[:10]

    if not recs_sorted:
        print("Con ese filtro de género no me queda nada. Prueba otro género o quita el filtro.")
        return

    print("Recomendaciones:")
    for i, m in enumerate(recs_sorted, 1):
        print(f"{i}. {movie_line(m)}")


if __name__ == "__main__":
    main()
