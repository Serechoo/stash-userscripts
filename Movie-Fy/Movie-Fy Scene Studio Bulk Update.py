import requests

def get_all_movies():
    query = """
    query AllMovies {
        allMovies {
            id
            name
            studio {
                id
                name
            }
            scenes {
                id
                studio {
                    id
                    name
                }
            }
        }
    }
    """
    response = requests.post("http://localhost:9999/graphql", json={"query": query})
    data = response.json()
    return data.get("data", {}).get("allMovies", [])

def update_scene_studio(scene_id, studio_id):
    mutation = """
    mutation SceneUpdate($scene_id: ID!, $studio_id: ID!) {
        sceneUpdate(input: { id: $scene_id, studio_id: $studio_id }) {
            id
        }
    }
    """
    variables = {
        "scene_id": scene_id,
        "studio_id": studio_id
    }
    response = requests.post("http://localhost:9999/graphql", json={"query": mutation, "variables": variables})
    return response.json()

def main():
    print("Starting update process...")
    movies = get_all_movies()
    for movie in movies:
        movie_id = movie.get("id")
        movie_name = movie.get("name")
        movie_studio_id = movie.get("studio", {}).get("id")
        scenes = movie.get("scenes", [])
        print(f"Updating scenes for movie: {movie_name}")
        for scene in scenes:
            scene_id = scene.get("id")
            scene_studio_id = scene.get("studio", {}).get("id")
            if scene_studio_id != movie_studio_id:
                print(f"Updating scene {scene_id} with studio ID {movie_studio_id}")
                update_scene_studio(scene_id, movie_studio_id)
        print(f"All scenes updated for movie: {movie_name}")
    print("Update process completed.")

if __name__ == "__main__":
    main()
