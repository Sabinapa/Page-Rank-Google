import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import matplotlib
matplotlib.use('Agg')

def allowed_by_robots(url):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    print(f"Preverjam robots.txt na: {robots_url}")
    try:
        response = requests.get(robots_url, timeout=5)
        #print(f"Vsebina robots.txt:\n{response.text[:300]}")
        lines = response.text.splitlines()

        user_agent_block = False
        allow_root = None  # Nič pomeni, da ni še določeno

        for line in lines:
            line = line.strip().lower()
            if not line or line.startswith("#"):
                continue

            if line.startswith("user-agent:"):
                agent = line.split(":")[1].strip()
                user_agent_block = (agent == "*" or "my-crawler" in agent)

            elif user_agent_block:
                if line.startswith("disallow:"):
                    path = line.split(":", 1)[1].strip()
                    if path == "/":
                        allow_root = False
                elif line.startswith("allow:"):
                    path = line.split(":", 1)[1].strip()
                    if path == "/":
                        allow_root = True

        # Če ni bilo pravila, privzemi da je dovoljeno
        return allow_root is not False

    except Exception as e:
        print(f"Napaka pri dostopu do robots.txt: {e}")
        return True

def crawl(url, depth=3, visited=None, graph=None):
    url = url.split("#")[0]  # očistimo fragmente

    if visited is None:
        visited = set()
    if graph is None:
        graph = {}

    if depth == 0 or url in visited or not allowed_by_robots(url):
        return visited, graph

    print(f"Crawling: {url}")
    visited.add(url)
    graph[url] = []

    try:
        html = requests.get(url, timeout=5).text
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href).split("#")[0]
            parsed = urlparse(full_url)
            if parsed.scheme in ["http", "https"] and parsed.path == "/":
                graph[url].append(full_url)
                if full_url not in visited:
                    visited, graph = crawl(full_url, depth - 1, visited, graph)

        graph[url] = list(set(graph[url]))

    except Exception as e:
        print(f"Napaka pri: {url} → {e}")

    return visited, graph

def compute_pagerank(graph, beta=0.85, eps=1e-6, max_iter=100):
    nodes = list(graph.keys())
    N = len(nodes)
    ranks = {node: 1 / N for node in nodes}
    new_ranks = ranks.copy()

    # Pripravi vhodne povezave (kdo kaže na koga)
    incoming_links = {node: [] for node in nodes}
    for from_node, to_nodes in graph.items():
        for to_node in to_nodes:
            if to_node in incoming_links:
                incoming_links[to_node].append(from_node)

    for _ in range(max_iter):
        for node in nodes:
            rank_sum = 0
            for in_node in incoming_links[node]:
                out_links = graph[in_node]
                if out_links:
                    rank_sum += ranks[in_node] / len(out_links)
            new_ranks[node] = (1 - beta) / N + beta * rank_sum

        # Preveri konvergenco
        delta = sum(abs(new_ranks[n] - ranks[n]) for n in nodes)
        if delta < eps:
            break
        ranks = new_ranks.copy()

    return new_ranks

def narisi_graf(graph, pagerank, filename='graf.png'):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()

    # Dodaj povezave
    for node, edges in graph.items():
        for target in edges:
            G.add_edge(node, target)

    # Velikost vozlišč glede na PageRank
    sizes = [pagerank.get(node, 0) * 5000 for node in G.nodes()]  # zmanjšano

    # Nariši graf
    plt.figure(figsize=(10, 6))  # manjša slika
    pos = nx.shell_layout(G)

    nx.draw(
        G, pos, with_labels=True, arrows=True,
        node_color='lightblue', node_size=sizes,
        font_size=6,  # manjša pisava
        edge_color='gray', arrowstyle='-|>', arrowsize=10
    )

    plt.title("Spletni graf (kompaktna postavitev)", fontsize=10)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)


if __name__ == "__main__":
    url = "https://feri.um.si/"
    enough = allowed_by_robots(url)
    print(f"Dovoljenje za {url}: {enough}")

    _, graph = crawl(url, depth=2)
    pagerank = compute_pagerank(graph)

    print("\nPovezave v grafu:")
    for k, v in graph.items():
        print(f"{k} → {v}")

    print("\nRezultati PageRank:")
    for node, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
        print(f"{node} → {score:.4f}")

    narisi_graf(graph, pagerank, filename='graf.png')