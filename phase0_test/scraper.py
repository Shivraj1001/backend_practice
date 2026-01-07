import requests
from bs4 import BeautifulSoup

def scrape_title(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string if soup.title else None
    return title