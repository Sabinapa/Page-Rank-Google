import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import matplotlib
matplotlib.use('Agg')

def allowed_by_robots(url, user_agent="*"):
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        print(f"Napaka pri branju robots.txt za {robots_url}: {e}")
        return True

def crawl(url, depth=3, visited=None, graph=None):
    url = url.split("#")[0]

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
    nodes = set(graph.keys())
    for targets in graph.values():
        nodes.update(targets)
    nodes = list(nodes)
    N = len(nodes)
    ranks = {node: 1 / N for node in nodes}
    new_ranks = ranks.copy()

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

        delta = sum(abs(new_ranks[n] - ranks[n]) for n in nodes)
        if delta < eps:
            break
        ranks = new_ranks.copy()

    return new_ranks

def draw(graph, pagerank, filename='graf.png'):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = nx.DiGraph()

    for node, edges in graph.items():
        for target in edges:
            G.add_edge(node, target)

    # Pripravi oznake brez 'https://'
    labels = {
        node: node.replace("https://", "").replace("http://", "") for node in G.nodes()
    }

    # Velikost vozlišč
    sizes = [pagerank.get(node, 0) * 200000 for node in G.nodes()]

    # Top 5 strani po PageRank
    top5_nodes = set([node for node, _ in sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:5]])

    # Barve vozlišč
    colors = ['lightcoral' if node in top5_nodes else 'lightblue' for node in G.nodes()]

    # Postavitev
    #pos = nx.shell_layout(G)
    pos = nx.circular_layout(G)

    plt.figure(figsize=(14, 10))
    nx.draw(
        G, pos, labels=labels, with_labels=True, arrows=True,
        node_color=colors, node_size=sizes,
        font_size=9,
        edge_color='gray', arrowstyle='-|>', arrowsize=14
    )

    plt.title("Spletni graf", fontsize=14)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()

if __name__ == "__main__":
    url = "https://www.cobiss.si/"
    enough = allowed_by_robots(url)
    print(f"Dovoljenje za {url}: {'DA' if enough else 'NE'}")

    visited, graph = crawl(url, depth=3)
    pagerank = compute_pagerank(graph)
    print(f"\nŠtevilo obiskanih strani: {len(visited)}")

    print("\nPovezave v grafu:")
    for k, v in graph.items():
        print(f"{k} → {v}")

    print("\nRezultati PageRank:")
    for node, score in sorted(pagerank.items(), key=lambda x: x[1], reverse=True):
        print(f"{node} → {score:.4f}")

    draw(graph, pagerank, filename='graf.png')