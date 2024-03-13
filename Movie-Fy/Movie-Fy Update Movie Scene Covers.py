import requests

# Define the GraphQL queries
all_movies_query = """
    query AllMovies {
        allMovies {
            id
            name
            front_image_path
            scenes {
                id
            }
        }
    }
"""

scene_update_mutation = """
    mutation SceneUpdate($movie_scene_id: ID!, $movie_front_image_path: String!) {
        sceneUpdate(input: { id: $movie_scene_id, cover_image: $movie_front_image_path }) {
            id
        }
    }
"""

# GraphQL endpoint
graphql_endpoint = "http://localhost:9999/graphql"

def update_scene_cover_images():
    # Send the GraphQL query to fetch all movies and their scenes
    response = requests.post(graphql_endpoint, json={"query": all_movies_query})
    data = response.json()
    
    if "data" in data and "allMovies" in data["data"]:
        all_movies = data["data"]["allMovies"]
        
        for movie in all_movies:
            movie_id = movie["id"]
            front_image_path = movie["front_image_path"]
            scenes = movie["scenes"]
            
            # Update each scene with the movie's front image path
            for scene in scenes:
                scene_id = scene["id"]
                variables = {
                    "movie_scene_id": scene_id,
                    "movie_front_image_path": front_image_path
                }
                
                # Send the mutation to update the scene cover image
                mutation_response = requests.post(graphql_endpoint, json={"query": scene_update_mutation, "variables": variables})
                mutation_data = mutation_response.json()
                
                if "data" in mutation_data and "sceneUpdate" in mutation_data["data"]:
                    print(f"Updated scene {scene_id} cover image with movie front image for movie {movie_id}")
                else:
                    print(f"Failed to update scene {scene_id} cover image for movie {movie_id}")

if __name__ == "__main__":
    update_scene_cover_images()
