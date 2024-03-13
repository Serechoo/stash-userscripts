import json
import requests
from thefuzz import process

# Function to find studio ID
def find_studio_id():
    find_studios_url = "http://localhost:9999/graphql"
    find_studios_payload = {
        "query": """
            query FindStudios {
                findStudios(studio_filter: { name: { value: "Movie", modifier: EQUALS } }) {
                    studios {
                        id
                    }
                }
            }
        """
    }
    response = requests.post(find_studios_url, json=find_studios_payload)
    result = response.json()
    if "data" in result and "findStudios" in result["data"] and result["data"]["findStudios"]["studios"]:
        return result["data"]["findStudios"]["studios"][0]["id"]
    else:
        print("Error finding studios:", result.get("errors", "Unknown Error"))
        return None

# Function to find scenes
def find_scenes(studio_id):
    find_scenes_url = "http://localhost:9999/graphql"
    query_string = f"""
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
    find_scenes_payload = {"query": query_string}

    try:
        response = requests.post(find_scenes_url, json=find_scenes_payload)
        response.raise_for_status()
        result = response.json()
        if "data" in result and "findScenes" in result["data"]:
            return result["data"]["findScenes"]["scenes"]
        else:
            print("Error finding scenes:", result.get("errors", "Unknown Error"))
            return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to server: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return None

# Function to find movie information with fuzzy matching
def find_movie_info(movie_name, movie_data):
    matches = []
    for entry in movie_data:
        match_ratio = process.extractOne(movie_name.lower(), [entry.get('Name', '').lower()])
        if match_ratio[1] >= 90:  # Adjust threshold as needed
            matches.append(entry)
    return matches

# Function to create a new movie with title and URL
def create_movie(movie_name, mutation_name, movie_url):
    movie_create_url = "http://localhost:9999/graphql"

    # Constructing the mutation string using title and URL
    mutation_string = f"""
        mutation MovieCreate {{
            movieCreate(
                input: {{
                    name: "{movie_name}"
                    url: "{movie_url}"
                }}
            ) {{
                id
            }}
        }}
    """

    movie_create_payload = {"query": mutation_string}

    try:
        response = requests.post(movie_create_url, json=movie_create_payload)
        response.raise_for_status()  # Raise an exception for bad status codes

        result = response.json()

        if "data" in result and "movieCreate" in result["data"]:
            movie_data = result["data"]["movieCreate"]
            if movie_data and "id" in movie_data:
                movie_id = movie_data["id"]
                print(f"Movie created successfully with ID: {movie_id}.")
                return movie_id, True
            else:
                print("Error: Unable to retrieve movie ID.")
        else:
            print("Error creating movie:", result.get("errors", "Unknown Error"))
    except requests.exceptions.RequestException as e:
        print(f"Error creating movie: {e}")
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")

    return None, False

# Function to find movie ID by name
def find_movie_id(movie_name):
    find_movie_url = "http://localhost:9999/graphql"
    find_movie_payload = {
        "query": """
            query FindMovieID($name: String!) {
                findMovies(movie_filter: { name: { value: $name, modifier: EQUALS } }) {
                    movies {
                        id
                    }
                }
            }
        """,
        "variables": {
            "name": movie_name
        }
    }
    response = requests.post(find_movie_url, json=find_movie_payload)
    result = response.json()
    if "data" in result and "findMovies" in result["data"] and result["data"]["findMovies"]["movies"]:
        return result["data"]["findMovies"]["movies"][0]["id"]
    else:
        print("Movie not found:", result.get("errors", "Unknown Error"))
        return None

# Function to update scenes with the movie
def update_scenes_with_movie(scene_id, movie_id):
    scene_update_url = "http://localhost:9999/graphql"
    scene_update_payload = {
        "query": """
            mutation SceneUpdate($id: ID!, $movies: [SceneMovieInput!]) {
                sceneUpdate(input: { id: $id, movies: $movies }) {
                    id
                }
            }
        """,
        "variables": {
            "id": scene_id,
            "movies": [{"movie_id": movie_id}]
        }
    }
    response = requests.post(scene_update_url, json=scene_update_payload)
    result = response.json()
    if "data" in result and "sceneUpdate" in result["data"]:
        return result["data"]["sceneUpdate"]["id"], True
    else:
        print("Error updating scene with movie:", result.get("errors", "Unknown Error"))
        return None, False


import re

# Function to parse movie titles
def parse_movie_titles(search_term):
    modified_search_term = re.sub(r'\bscene\b.*', '', search_term, flags=re.IGNORECASE)
    modified_search_term = re.sub(r'\s-.*', '', modified_search_term)
    return modified_search_term.strip()

# Main function
def main():
    print("Starting process...")
    # Find studio ID
    studio_id = find_studio_id()
    if studio_id:
        print(f"Found studio ID: {studio_id}")
        # Find scenes for the studio
        scenes = find_scenes(studio_id)
        if scenes:
            print(f"Found {len(scenes)} scenes.")
            # Load movie data from file
            try:
                with open('Movie-Fy URLs.json', 'r', encoding='utf-8') as json_file:
                    movie_data = json.load(json_file)
            except Exception as e:
                print(f"Error reading JSON file: {e}")
                return

            # Query all existing movies
            all_movies = []
            all_movies_query = """
                query AllMovies {
                    allMovies {
                        id
                        name
                    }
                }
            """
            all_movies_response = requests.post("http://localhost:9999/graphql", json={"query": all_movies_query})
            all_movies_result = all_movies_response.json()
            if "data" in all_movies_result and "allMovies" in all_movies_result["data"]:
                all_movies = all_movies_result["data"]["allMovies"]

            # Process each scene
            previous_movie_id = None
            previous_custom_search_term = None
            for scene in scenes:
                print(f"Processing scene: {scene['title']}")
                # Parse movie details from the scene title
                parsed_title = parse_movie_titles(scene['title'])
                # Check if movie with same title exists
                movie_name = parsed_title
                existing_movie_id = None
                for movie in all_movies:
                    if movie['name'] == movie_name:
                        existing_movie_id = movie['id']
                        break
                if existing_movie_id:
                    print(f"Movie '{movie_name}' already exists with ID {existing_movie_id}. Skipping scene.")
                    continue  # Skip processing for this scene

                # Find movie info from parsed title
                movie_matches = find_movie_info(movie_name, movie_data)
                
                # Display fuzzy matched movies for the user to choose from
                if movie_matches:
                    print(f"Fuzzy matched movies for '{scene['title']}':")
                    for i, match in enumerate(movie_matches, start=1):
                        print(f"{i}. {match['Name']} ({match['Source']})")
                    choice = input("Enter the number of the correct match, 'c' to perform a custom search, or 's' to skip: ")
                    if choice.lower() == 'c':
                        if previous_custom_search_term:
                            use_previous = input(f"Do you want to use the previous custom search term '{previous_custom_search_term}'? (y/n): ")
                            if use_previous.lower() == 'y':
                                custom_search_term = previous_custom_search_term
                            else:
                                custom_search_term = input("Enter a new custom search term: ")
                        else:
                            custom_search_term = input("Enter a custom search term: ")
                            
                        custom_movie_matches = find_movie_info(custom_search_term, movie_data)
                        if custom_movie_matches:
                            print(f"Custom search term '{custom_search_term}' matches:")
                            for i, match in enumerate(custom_movie_matches, start=1):
                                print(f"{i}. {match['Name']} ({match['Source']})")
                            choice = input("Enter the number of the correct match, or 's' to skip: ")
                            if choice.lower() == 's':
                                previous_custom_search_term = custom_search_term
                                continue  # Skip processing for this scene
                            try:
                                choice_index = int(choice) - 1
                                if 0 <= choice_index < len(custom_movie_matches):
                                    movie_info = custom_movie_matches[choice_index]
                                else:
                                    print("Invalid choice.")
                                    continue
                            except ValueError:
                                print("Invalid choice.")
                                continue
                        else:
                            print(f"No matching movies found for the custom search term '{custom_search_term}'.")
                            previous_custom_search_term = custom_search_term
                            continue  # Skip processing for this scene
                    elif choice.lower() == 's':
                        print("Skipping scene.")
                        continue  # Skip processing for this scene
                    try:
                        choice_index = int(choice) - 1
                        if 0 <= choice_index < len(movie_matches):
                            movie_info = movie_matches[choice_index]
                        else:
                            print("Invalid choice.")
                            continue
                    except ValueError:
                        print("Invalid choice.")
                        continue

                    # Check if movie with same title exists
                    existing_movie_id = find_movie_id(movie_info['Name'])
                    if existing_movie_id:
                        # Prompt user to confirm the match
                        confirm_match = input(f"Scene '{scene['title']}' matches with existing movie '{movie_info['Name']}'. Do you want to proceed with this match? (y/n): ")
                        if confirm_match.lower() != 'y':
                            continue  # Skip this scene
                        if existing_movie_id == previous_movie_id:
                            add_scene = input("This scene appears to belong to the previously created movie. Do you want to add it as a scene to the previously created movie? (y/n): ")
                            if add_scene.lower() == 'y':
                                if update_scenes_with_movie(scene['id'], existing_movie_id):
                                    print(f"Scene {scene['id']} successfully added to movie {existing_movie_id}.")
                                else:
                                    print(f"Failed to add scene {scene['id']} to movie {existing_movie_id}.")
                            else:
                                print("Skipping scene.")
                        else:
                            # Update scene with existing movie ID
                            print(f"Movie '{movie_info['Name']}' exists with ID {existing_movie_id}. Updating scene {scene['id']} to this movie.")
                            if update_scenes_with_movie(scene['id'], existing_movie_id):
                                print(f"Scene {scene['id']} successfully updated to movie {existing_movie_id}.")
                            else:
                                print(f"Failed to update scene {scene['id']} to movie {existing_movie_id}.")
                    else:
                        # Create new movie with scraped data
                        print(f"Creating new movie for '{movie_info['Name']}' based on URL: {movie_info['Source']}")
                        new_movie_id, created = create_movie(movie_info['Name'], movie_info['Name'], movie_info['Source'])
                        if created:
                            # Update scene with new movie ID
                            print(f"Movie '{movie_info['Name']}' created with ID {new_movie_id}. Updating scene {scene['id']} to this new movie.")
                            if update_scenes_with_movie(scene['id'], new_movie_id):
                                print(f"Scene {scene['id']} successfully updated to new movie {new_movie_id}.")
                            else:
                                print(f"Failed to update scene {scene['id']} to new movie {new_movie_id}.")
                        else:
                            print(f"Failed to create movie '{movie_info['Name']}'.")
                else:
                    print(f"No matching movie found for '{scene['title']}'.")

                    # Prompt user to skip or perform a custom search
                    choice = input("Enter 'c' to perform a custom search or 's' to skip: ")
                    if choice.lower() == 'c':
                        custom_search_term = input("Enter a custom search term: ")
                        custom_movie_matches = find_movie_info(custom_search_term, movie_data)
                        if custom_movie_matches:
                            print(f"Custom search term '{custom_search_term}' matches:")
                            for i, match in enumerate(custom_movie_matches, start=1):
                                print(f"{i}. {match['Name']} ({match['Source']})")
                            choice = input("Enter the number of the correct match or 's' to skip: ")
                            if choice.lower() == 's':
                                continue  # Skip processing for this scene
                            try:
                                choice_index = int(choice) - 1
                                if 0 <= choice_index < len(custom_movie_matches):
                                    movie_info = custom_movie_matches[choice_index]
                                else:
                                    print("Invalid choice.")
                                    continue
                            except ValueError:
                                print("Invalid choice.")
                                continue
                        else:
                            print(f"No matching movies found for the custom search term '{custom_search_term}'.")
                            continue  # Skip processing for this scene
                    elif choice.lower() == 's':
                        print("Skipping scene.")
                        continue  # Skip processing for this scene
                    else:
                        print("Invalid choice. Skipping scene.")
                        continue

                # Store the current movie ID for comparison in the next iteration
                if existing_movie_id:
                    previous_movie_id = existing_movie_id
        else:
            print("No scenes found for the specified studio.")
    else:
        print("Studio 'Movie' not found.")

# Entry point
if __name__ == "__main__":
    main()
