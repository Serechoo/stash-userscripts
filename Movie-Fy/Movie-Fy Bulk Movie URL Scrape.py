import requests

# GraphQL queries
all_movies_query = """
query AllMovies {
    allMovies {
        id
        name
        url
    }
}
"""

scrape_movie_query = """
query ScrapeMovieURL($url: String!) {
    scrapeMovieURL(url: $url) {
        name
        date
        synopsis
        front_image
        back_image
    }
}
"""

movie_update_mutation = """
mutation MovieUpdate($id: ID!, $name: String!, $date: String!, $synopsis: String!, $front_image: String!, $back_image: String!) {
    movieUpdate(input: {
        id: $id
        name: $name
        date: $date
        synopsis: $synopsis
        front_image: $front_image
        back_image: $back_image
    }) {
        id
    }
}
"""

# GraphQL endpoint
graphql_endpoint = "http://localhost:9999/graphql"

# Function to send GraphQL queries
def send_query(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(graphql_endpoint, json=payload)
    return response.json()

# Step 1: Fetch all movies and their URLs
response = send_query(all_movies_query)
movies = response["data"]["allMovies"]

# Step 2-5: Iterate through movies, scrape metadata, and update records
for movie in movies:
    movie_id = movie["id"]
    movie_name = movie["name"]
    movie_url = movie["url"]
    
    # Step 3: Send GraphQL query to scrape metadata
    scrape_variables = {"url": movie_url}
    scrape_response = send_query(scrape_movie_query, variables=scrape_variables)
    scraped_data = scrape_response["data"]["scrapeMovieURL"]
    
    # Step 4: Extract scraped metadata
    name = scraped_data.get("name", "")
    date = scraped_data.get("date", "")
    synopsis = scraped_data.get("synopsis", "")
    front_image = scraped_data.get("front_image", "")
    back_image = scraped_data.get("back_image", "")

    
    # Step 5: Send GraphQL mutation to update movie record
    update_variables = {
        "id": movie_id,
        "name": name,
        "date": date,
        "synopsis": synopsis,
        "front_image": front_image,
        "back_image": back_image
    }
    update_response = send_query(movie_update_mutation, variables=update_variables)
    if "errors" in update_response:
        print(f"Failed to update movie {movie_name}: {update_response['errors']}")
    else:
        print(f"Movie {movie_name} updated successfully.")
