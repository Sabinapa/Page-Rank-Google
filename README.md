# 🌐 PageRank analiza spletnih strani z uporabo spletnega pajka

## 📌 Namen projekta

V okviru te naloge sem implementirala **spletni pajek (web crawler)**, ki se zažene na določeni spletni strani in sledi vrhnjim povezavam (tistim s potjo `/`) do določene **globine**. Pajek preverja **dovoljenja iz robots.txt** in spoštuje pravila za indeksiranje. Nato sem iz zbranih povezav zgradila **usmerjeni graf** in na njem izvedla **PageRank analizo**.

## ✅ Kaj projekt vključuje
- Rekurzivno iskanje povezav do nastavljene globine
- Izgradnja usmerjenega grafa hiperpovezav
- Ročna implementacija algoritma PageRank
- Vizualizacija grafa z različnimi velikostmi vozlišč glede na PageRank
- Obarvanje top 5 vozlišč z najvišjo PageRank vrednostjo

---

## 📂 Struktura kode

### 1. `allowed_by_robots(url)`
Preveri, ali spletni pajek sme obiskati dano stran, glede na datoteko `robots.txt`. Uporablja `RobotFileParser`.

### 2. `crawl(url, depth)`
Glavna rekurzivna funkcija za pajkanje. Zbira povezave do nastavljenega nivoja globine. Dodaja samo vrhnje poti (`/`).

### 3. `compute_pagerank(graph, beta, eps)`
Ročna implementacija PageRank algoritma:
- `beta = 0.85` predstavlja verjetnost nadaljevanja klikanja
- Metoda iterira do konvergence, z dovolj majhno razliko med vrednostmi

### 4. `draw(graph, pagerank, filename)`
Ustvari vizualizacijo spletnega grafa:
- Velikost vozlišč je sorazmerna PageRank vrednosti
- Najvišjih 5 je obarvanih rdeče
- Vozlišča so prikazana brez "https://"

---

## Kaj izpiše koda
- obiskovane strani
- povezave med njimi,
- izračun PageRank,
- ustvarila sliko graf.png z grafom povezav.

## 📈 Vizualni rezultat grafa
- Velika vozlišča → višji PageRank
- Barva rdeča → najbolj povezane / pomembne strani

Za analizo sta bila uporabljena primera globine 3:
- [FERI.UM.SI](https://feri.um.si/)
- [COBISS.SI](https://www.cobiss.si/)

![image](https://github.com/user-attachments/assets/5312c299-ae33-4f5a-82c9-3ceadccc0937)




