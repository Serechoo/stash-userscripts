import re
import requests
import stashapi.log as log  # Importing progress tracking module

# Function to find studio ID
def find_studio_id(studio_name):
    find_studios_url = "http://localhost:9999/graphql"
    find_studios_payload = {
        "query": f"""
            query FindStudios {{
                findStudios(filter: {{ q: "{studio_name}" }}) {{
                    studios {{
                        id
                    }}
                }}
            }}
        """
    }

    response = requests.post(find_studios_url, json=find_studios_payload)
    result = response.json()

    if "data" in result and "findStudios" in result["data"]:
        studios = result["data"]["findStudios"]["studios"]
        if studios:
            return studios[0]["id"]
        else:
            log.info(f"Studio with name '{studio_name}' not found.")
            return None
    else:
        log.error("Error finding studios:", result.get("errors"))
        return None

# Function to find scenes
def find_scenes(studio_id):
    find_scenes_url = "http://localhost:9999/graphql"
    find_scenes_payload = {
        "query": f"""
            query FindScenes {{
                findScenes(
                    scene_filter: {{ studios: {{ value: "{studio_id}", modifier: EQUALS }} }},
                    filter: {{ per_page: -1 }}
                ) {{
                    scenes {{
                        id
                        title
                    }}
                }}
            }}
        """
    }

    response = requests.post(find_scenes_url, json=find_scenes_payload)
    result = response.json()

    if "data" in result and "findScenes" in result["data"]:
        return result["data"]["findScenes"]["scenes"]
    else:
        log.error("Error finding scenes:", result.get("errors"))
        return None

# Function to find scene details
def find_scene_details(scene_id):
    find_scene_query = f"""
        query FindScene {{
            findScene(id: {scene_id}) {{
                title
                files {{
                    basename
                }}
            }}
        }}
    """

    response = requests.post("http://localhost:9999/graphql", json={"query": find_scene_query})
    result = response.json()

    if "data" in result and "findScene" in result["data"]:
        return result["data"]["findScene"]
    else:
        log.error("Error finding scene details:", result.get("errors"))
        return None

# Function to update title with basename
def update_title_with_basename(scene_id, file_basename):
    # Use regex to remove file extension
    title = re.sub(r'\.[^.]*$', '', file_basename)

    # GraphQL mutation to update scene title
    update_scene_mutation = f"""
        mutation SceneUpdate {{
            sceneUpdate(input: {{ id: {scene_id}, title: "{title}" }}) {{
                title
            }}
        }}
    """

    log.info("\nGraphQL Mutation to Update Scene Title:")
    log.info(update_scene_mutation)

    # Uncomment the following lines to execute the mutation
    response = requests.post("http://localhost:9999/graphql", json={"query": update_scene_mutation})
    result = response.json()
    log.info("Mutation Result:", result)

if __name__ == "__main__":
    studio_name = "Movie"

    log.info(f"Finding scenes for Studio: {studio_name}")

    studio_id = find_studio_id(studio_name)

    if studio_id:
        log.info(f"Found Studio ID for '{studio_name}': {studio_id}")

        scenes = find_scenes(studio_id)

        if scenes:
            log.info(f"\nScenes for Studio '{studio_name}':")
            total_scenes = len(scenes)
            processed_scenes = 0

            log.info("\nChecking and updating titles:")
            for scene in scenes:
                scene_details = find_scene_details(scene['id'])

                if scene_details:
                    title = scene_details["title"]
                    file_basename = scene_details["files"][0]["basename"] if scene_details["files"] else None

                    log.info("\nScene Details:")
                    log.info(f"Scene ID: {scene['id']}")
                    log.info(f"Title: {title}")
                    log.info(f"File Basename: {file_basename}")

                    if not title and file_basename:
                        update_title_with_basename(scene['id'], file_basename)
                        log.info(f"Scene title updated: {title}")  # Log the updated scene title
                    else:
                        log.info("No action needed. Scene already has a title or is missing a file basename.")
                
                # Update progress
                processed_scenes += 1
                progress = processed_scenes / total_scenes
                log.progress(progress)

            log.info("\nProcessing complete.")
        else:
            log.info(f"No scenes found for Studio '{studio_name}'.")
    else:
        log.error(f"Could not proceed without Studio ID for '{studio_name}'.")
