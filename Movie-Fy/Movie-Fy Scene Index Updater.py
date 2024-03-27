import requests
import re
import stashapi.log as log  # Importing progress tracking module

# GraphQL query to fetch all scenes
all_scenes_query = """
query AllScenes {
    allScenes {
        id
        title
        movies {
            movie {
                id
            }
        }
    }
}
"""

# GraphQL mutation to update scene with scene_index
update_scene_mutation = """
mutation UpdateScene($sceneId: ID!, $movieId: ID!, $sceneIndex: Int!) {
  sceneUpdate(input: {id: $sceneId, movies: {movie_id: $movieId, scene_index: $sceneIndex}}) {
    id
  }
}
"""

def fetch_all_scenes():
    url = "http://localhost:9999/graphql"
    payload = {"query": all_scenes_query}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("data", {}).get("allScenes", [])
    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching scenes: {e}")
        return []

def update_scene(scene_id, movie_id, scene_index):
    url = "http://localhost:9999/graphql"
    payload = {
        "query": update_scene_mutation,
        "variables": {
            "sceneId": scene_id,
            "movieId": movie_id,
            "sceneIndex": scene_index
        }
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json().get("data", {}).get("sceneUpdate", {})
        if result:
            log.info(f"Scene {scene_id} updated successfully.")
        else:
            log.warning(f"Failed to update scene {scene_id}.")
    except requests.exceptions.RequestException as e:
        log.error(f"Error updating scene {scene_id}: {e}")

def parse_scene_index(title, scenes):
    # Check if title contains 'bonus' or '-bonus-'
    if 'bonus' in title.lower() or '-bonus-' in title.lower():
        return 50
    
    # Use regular expression to extract scene index from title
    match = re.search(r'(?:scene|Scene)[\s_-]*([\d]+)', title)
    if match:
        title_scene_index = int(match.group(1))  # Extracted scene index from title
    else:
        title_scene_index = None

    # Get the last assigned scene index
    last_assigned_index = max(scene.get('sceneIndex', 0) for scene in scenes)

    # Compare title_scene_index and last_assigned_index, prioritize title_scene_index if it exists and is greater
    if title_scene_index is not None:
        return max(title_scene_index, last_assigned_index + 1)

    # Start scene index from 1 if no number in title
    return last_assigned_index + 1 if last_assigned_index > 0 else 1  

def main():
    scenes = fetch_all_scenes()
    if not scenes:
        log.warning("No scenes found.")
        return

    for scene in scenes:
        scene_id = scene['id']
        
        # Check if scene has associated movies
        movies = scene.get('movies', [])
        if not movies:
            log.warning(f"Scene {scene_id} does not have any associated movies. Skipping.")
            continue
        
        movie_id = movies[0]['movie'].get('id')  # Get the movie id if available
        title = scene['title']
        
        # Check if scene already has a scene index assigned
        if 'sceneIndex' in scene:
            log.info(f"Scene {scene_id} already has a scene index assigned. Skipping.")
            continue
        
        scene_index = parse_scene_index(title, scenes)
        update_scene(scene_id, movie_id, scene_index)
        log.info(f"Updated scene_index for scene {scene_id}.")

    log.info("Script completed successfully.")

if __name__ == "__main__":
    main()
