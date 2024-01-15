import requests
from bs4 import BeautifulSoup
import subprocess
import webbrowser

def open_web_browser(html_filename):
    # Open the generated HTML gallery in the default web browser
    webbrowser.open(html_filename, new=2)  # new=2 opens in a new tab, you can adjust it as needed

def get_gif_links(search_term, max_results=10):
    base_url = "https://www.pornhub.com"
    gif_links = []

    def extract_gif_links_from_page(page_url):
        response = requests.get(page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            gifs_wrapper = soup.find('div', class_='gifsWrapper hideLastItemLarge')
            gif_blocks = gifs_wrapper.find_all('li', class_=lambda x: x and 'sniperModeEngaged' not in x and 'alpha' not in x)

            for gif_block in gif_blocks:
                link_to_subsequent_page = gif_block.find('a')['href']
                subsequent_page_url = f"{base_url}{link_to_subsequent_page}"
                gif_link = extract_gif_link_from_subsequent_page(subsequent_page_url)

                if gif_link:
                    gif_links.append(gif_link)

                    # Limit the results to max_results
                    if len(gif_links) >= max_results:
                        return

    def extract_gif_link_from_subsequent_page(subsequent_page_url):
        response = requests.get(subsequent_page_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            gif_link_element = soup.find('input', class_='floatLeft gifvalue')

            if gif_link_element:
                return gif_link_element['value']

    search_url = f"{base_url}/gifs/search?search={search_term}"
    extract_gif_links_from_page(search_url)

    for page_number in range(2):  # Adjust the upper limit based on your needs
        subsequent_page_url = f"{search_url}&page={page_number}"
        extract_gif_links_from_page(subsequent_page_url)

        # Break if max_results is reached
        if len(gif_links) >= max_results:
            break

    return gif_links

def generate_html_gallery(gif_links, search_term):
    with open('gallery_template.html', 'r', encoding='utf-8') as template_file:
        template_content = template_file.read()

    dynamic_content = "\n".join([f'<li class="gif-list-item" onclick="showGifPreview(\'{gif_link}\')">{gif_link}</li>' for gif_link in gif_links])
    total_gifs = len(gif_links)
    final_html_content = template_content.replace('{SEARCH_TERM}', search_term).replace('{DYNAMIC_CONTENT}', dynamic_content).replace('{TOTAL_GIFS}', str(total_gifs))

    with open(f'{search_term}_gif_gallery.html', 'w', encoding='utf-8') as file:
        file.write(final_html_content)

while True:
    # Get the list of gif links
    search_term = input("Enter a search term: ")
    result = get_gif_links(search_term)

    # Generate HTML gallery with the search term as part of the filename
    generate_html_gallery(result, search_term)

    # Open the web browser
    html_filename = f'{search_term}_gif_gallery.html'
    open_web_browser(html_filename)

    # Call the tag_ql.py script
    try:
        subprocess.run(['python', 'tag_ql.py'], check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing tag_ql.py script: {e}")

    # Ask the user if they want to find another Tag GIF
    another_search = input("Find another Tag GIF? (yes/no): ").lower()
    if another_search != 'yes':
        break
