import requests
from bs4 import BeautifulSoup
import logging
import os
import time  # Import the time module

# Specify the log file path
log_file_path = 'C:\\mass_tag_updater_logs\\mass_tag_updater.log'

# Ensure the directory exists
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Configure logging with the specified log file path
logging.basicConfig(filename=log_file_path, level=logging.DEBUG)

# Set to store all fetched URLs
all_fetched_urls = set()

def get_single_gif_link(search_term, fetch_size=1):
    base_url = "https://www.pornhub.com"
    search_url = f"{base_url}/gifs/search?search={search_term}"

    gif_links = []

    for _ in range(fetch_size):
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        gifs_wrapper = soup.find('div', class_='gifsWrapper hideLastItemLarge')

        if gifs_wrapper:
            for gif_block in gifs_wrapper.find_all('li', class_=lambda x: x and 'sniperModeEngaged' not in x and 'alpha' not in x):
                link_to_subsequent_page = gif_block.find('a')
                if link_to_subsequent_page:
                    subsequent_page_url = f"{base_url}{link_to_subsequent_page['href']}"
                    response_subsequent = requests.get(subsequent_page_url)
                    soup_subsequent = BeautifulSoup(response_subsequent.text, 'html.parser')
                    gif_link_element = soup_subsequent.find('input', class_='floatLeft gifvalue')
                    if gif_link_element:
                        gif_link = gif_link_element['value']
                        if gif_link not in all_fetched_urls:
                            all_fetched_urls.add(gif_link)
                            gif_links.append(gif_link)
                            if len(gif_links) >= fetch_size:
                                break

    return gif_links

def fetch_all_tags(graphql_endpoint):
    # GraphQL query to fetch all tags with image_path
    graphql_query = """
        query AllTags {
            allTags {
                id
                name
                image_path
            }
        }
    """

    # Send the GraphQL query to the GraphQL endpoint without authentication headers
    response = requests.post(graphql_endpoint, json={'query': graphql_query})

    # Check the response
    if response.status_code == 200:
        result_data = response.json()
        return result_data.get('data', {}).get('allTags', [])
    else:
        print(f"Error fetching all tags. Status Code: {response.status_code}")
        print("Response Text:", response.text)
        return []

def get_tag_id(tags, tag_name):
    for tag in tags:
        if tag['name'] == tag_name:
            return tag['id']
    return None

def update_tag_with_image(tag_name, image_url, graphql_endpoint, tag_id):
    # Construct the GraphQL mutation string with the provided image URL
    graphql_mutation = f"""
        mutation TagUpdate {{
            tagUpdate(
                input: {{
                    image: "{image_url}"
                    name: "{tag_name}"
                    id: "{tag_id}"
                }}
            ) {{
                image_path
            }}
        }}
    """

    # Send the GraphQL mutation to the GraphQL endpoint without authentication headers
    response = requests.post(graphql_endpoint, json={'query': graphql_mutation})

    # Check the response
    if response.status_code == 200:
        result_data = response.json()
        print(f"GraphQL Mutation Result for tag '{tag_name}':")
        print(result_data)
    else:
        print(f"Error sending GraphQL mutation for tag '{tag_name}'. Status Code: {response.status_code}")
        print("Response Text:", response.text)

def run_script():
    # GraphQL endpoint URL
    graphql_endpoint = "http://localhost:9999/graphql"  # Adjust as needed

    # Log the start of the script
    logging.info("Mass Tag Updater script started.")

    # Fetch all tags with image_path
    all_tags = fetch_all_tags(graphql_endpoint)

    for tag in all_tags:
        tag_name = tag['name']
        image_path = tag['image_path']

        # Check if the image_path contains '&default=true'
        if '&default=true' in image_path:
            # Attempt to fetch unique gif links for each tag
            for fetch_size_attempt in range(1, 6):  # Maximum 5 attempts to find a unique URL
                gif_links = get_single_gif_link(tag_name, fetch_size_attempt)

                # Log the fetched gif links
                logging.info(f"Fetched gif links for tag '{tag_name}' (Attempt {fetch_size_attempt}): {gif_links}")

                if gif_links:
                    # Get tag ID
                    tag_id = tag['id']

                    for gif_link in gif_links:
                        # Log the attempt to update the tag with the image
                        logging.info(f"Attempting to update tag '{tag_name}' with image: {gif_link}")

                        # Update the tag with the image
                        update_tag_with_image(tag_name, gif_link, graphql_endpoint, tag_id)

                        # Add a delay of 2 seconds between successful mutations
                        time.sleep(2)

                    break  # Exit the loop if a unique URL is found
                else:
                    # Log if no gif links were found for the tag in the current attempt
                    logging.info(f"No gif links found for tag '{tag_name}' in Attempt {fetch_size_attempt}")
        else:
            # Log if the tag doesn't need an updated image
            logging.info(f"Tag '{tag_name}' already has a custom image and doesn't need an update.")

if __name__ == "__main__":
    # Run the script
    run_script()
