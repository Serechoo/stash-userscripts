import requests
from bs4 import BeautifulSoup

def get_gif_links(search_term):
    base_url = "https://www.pornhub.com"
    gif_links = []

    # Function to extract gif links from a given page URL
    def extract_gif_links_from_page(page_url):
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the parent container that holds gif links
            gifs_wrapper = soup.find('div', class_='gifsWrapper hideLastItemLarge')

            # Find all li elements with class 'gifVideoBlock' excluding those with class 'sniperModeEngaged alpha'
            gif_blocks = gifs_wrapper.find_all('li', class_=lambda x: x and 'sniperModeEngaged' not in x and 'alpha' not in x)

            for gif_block in gif_blocks:
                # Extract the link to the subsequent page
                link_to_subsequent_page = gif_block.find('a')['href']

                # Visit the subsequent page and extract the gif link
                subsequent_page_url = f"{base_url}{link_to_subsequent_page}"
                gif_link = extract_gif_link_from_subsequent_page(subsequent_page_url)

                if gif_link:
                    gif_links.append(gif_link)

    # Function to extract gif link from a subsequent page
    def extract_gif_link_from_subsequent_page(subsequent_page_url):
        response = requests.get(subsequent_page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the gif link
            gif_link_element = soup.find('input', class_='floatLeft gifvalue')
            if gif_link_element:
                return gif_link_element['value']

    # Start with the search page
    search_url = f"{base_url}/gifs/search?search={search_term}"
    extract_gif_links_from_page(search_url)

    # You may need to adjust the range based on the total number of pages
    for page_number in range(2):  # Adjust the upper limit based on your needs
        # Construct the subsequent page URL
        subsequent_page_url = f"{search_url}&page={page_number}"
        extract_gif_links_from_page(subsequent_page_url)

    return gif_links

def generate_html_gallery(gif_links, search_term):
    # Read the template file
    with open('gallery_template.html', 'r', encoding='utf-8') as template_file:
        template_content = template_file.read()

    # Replace placeholders with actual content
    dynamic_content = "\n".join([f'<li class="gif-list-item" onclick="showGifPreview(\'{gif_link}\')">{gif_link}</li>' for gif_link in gif_links])
    total_gifs = len(gif_links)
    final_html_content = template_content.replace('{SEARCH_TERM}', search_term).replace('{DYNAMIC_CONTENT}', dynamic_content).replace('{TOTAL_GIFS}', str(total_gifs))

    # Save the HTML content to a file
    with open(f'{search_term}_gif_gallery.html', 'w', encoding='utf-8') as file:
        file.write(final_html_content)


# Prompt the user for a search term
search_term = input("Enter a search term: ")

# Get the list of gif links
result = get_gif_links(search_term)

# Generate HTML gallery with the search term as part of the filename
generate_html_gallery(result, search_term)

# Notify the user
print(f"HTML gallery generated. Open {search_term}_gallery.html to view the results.")
