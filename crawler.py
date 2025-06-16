import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def allowed_by_robots(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        response = requests.get(robots_url, timeout=5)
        lines = response.text.lower().splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith("user-agent"):
                continue  # Ignoriramo zaenkrat
            if line.startswith("disallow:") and line.split("disallow:")[1].strip() == "/":
                return False
            if line.startswith("allow:") and line.split("allow:")[1].strip() == "/":
                return True
        return True  # Če "/"" ni eksplicitno prepovedan, je dovoljeno
    except:
        return True  # Če robots.txt ni dostopen

def crawl(url, depth=3, visited=None):
    url = url.split("#")[0]  # <--- očistimo fragmente

    if visited is None:
        visited = set()
    if depth == 0 or url in visited or not allowed_by_robots(url):
        return visited

    print(f"Crawling: {url}")
    visited.add(url)

    try:
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href).split("#")[0]  # <--- očistimo tudi tukaj
            parsed = urlparse(full_url)
            if parsed.scheme in ["http", "https"] and parsed.path == "/" and full_url not in visited:
                visited |= crawl(full_url, depth - 1, visited)
    except Exception as e:
        print(f"Napaka pri: {url} → {e}")
    return visited

if __name__ == "__main__":
    url = "https://www.fri.uni-lj.si/"
    enough = allowed_by_robots(url)
    print(f"Dovoljenje za {url}: {enough}")

    all_sites = crawl(url, depth=3)
    print("\nObiskane strani:")
    for site in all_sites:
        print(site)