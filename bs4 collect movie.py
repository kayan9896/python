import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html = BeautifulSoup(response.text, 'lxml')
        print(html)
        return html
    except Exception as e:
        print(e)

def collect_movie_links(html):
    movies = html.find('ul', class_='scripts-list').find_all('a', href=True)
    movies_links = [link['href'] for link in movies]
    return movies_links

def collect_single_movie_data(movie_link):
    root_url = "https://subslikescript.com/"
    single_movie_html = fetch_html(url=root_url+movie_link)

    try:
        movie_title = single_movie_html.find('h1').text.strip()
    except:
        movie_title = np.nan

    try:
        movie_plot = single_movie_html.find('p', class_='plot').text.strip()
    except:
        movie_plot = np.nan

    try:
        movie_script = single_movie_html.find('div', class_="full-script").get_text(strip=True, separator='\n')
    except:
        movie_script = np.nan

    return [movie_title, movie_plot, movie_script]

def fetch_data(start_char, page_num=1):
    start_char = start_char.upper()

    # URL templates for scraping movie data by letter and page number
    letter_with_page_url = "https://subslikescript.com/movies_letter-{}?page={}"

    # URL template for scraping movie data by page number only
    all_movies_with_page_url = "https://subslikescript.com/movies?page={}"

    movies_data = []
    soup = fetch_html(letter_with_page_url.format(start_char, 1))
    total_pages = int(soup.find('ul', class_='pagination').find_all('li')[-2].text.strip())

    for page_no in tqdm(range(1, total_pages), desc='Process'):
        soup = fetch_html(letter_with_page_url.format(start_char, page_no))
        movie_links = collect_movie_links(soup)
        for movie_link in movie_links:
            movies_data.append(collect_single_movie_data(movie_link))
            # Adding a delay of 1 second between requests to avoid overwhelming the server
            time.sleep(1)

    df = pd.DataFrame(columns=['Title', 'Plot', 'Script'], data=movies_data)
    df.to_csv('movies_scripts.csv', index=False)

# Get starting character from user
start_char = input("Enter starting character for movie titles: ").upper()

fetch_data(start_char)

