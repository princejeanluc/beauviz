# Guide de choix des graphiques

Ce guide répond à une seule question : **« j'ai ce message à faire passer,
quelle fonction j'appelle ? »** Il est organisé par intention de communication,
pas par type de graphique — vous n'avez pas besoin de connaître le nom d'une
fonction pour trouver la bonne.

Pensé pour être utilisable seul, sans connaître le reste de la librairie :
suivez l'arbre de décision (section 1), trouvez votre cas dans le tableau de
correspondance (section 4) ou les fiches (section 2), et vérifiez le piège le
plus proche de votre situation (section 5).

---

## Sommaire

1. [Arbre de décision](#1-arbre-de-décision)
2. [Fiches par fonction](#2-fiches-par-fonction)
3. [Règles universelles de communication visuelle](#3-règles-universelles-de-communication-visuelle)
4. [Tableau de correspondance type de données → graphique](#4-tableau-de-correspondance-type-de-données--graphique)
5. [Pièges courants](#5-pièges-courants)

---

## 1. Arbre de décision

Posez-vous les questions dans l'ordre. Dès qu'une réponse correspond à votre
cas, suivez la flèche — n'allez pas plus loin.

```
Combien de variables numériques principales avez-vous ?

├─ 1 variable
│   │
│   ├─ Je veux montrer sa DISTRIBUTION (forme, dispersion)
│   │   ├─ Comparer plusieurs groupes, peu de points (<20/groupe) → box_plot()
│   │   ├─ Comparer plusieurs groupes, beaucoup de points (≥20/groupe) → violin()
│   │   └─ Un seul groupe → histogramme()
│   │
│   ├─ Je veux CLASSER des catégories par cette variable
│   │   ├─ 5 à 30 catégories, peu de place → lollipop()
│   │   ├─ Beaucoup de variance, mettre en avant le top → barres_ranked()
│   │   └─ Standard, peu de catégories (<8) → barres()
│   │
│   ├─ Je veux montrer une ÉVOLUTION dans le temps
│   │   ├─ Tendance simple → ligne()
│   │   ├─ Composition qui évolue (parts qui changent) → aire(empile=True)
│   │   └─ Plusieurs entités, valeurs ET variations → barres_connectees()
│   │
│   ├─ Je veux montrer une RÉPARTITION (parties d'un tout)
│   │   ├─ 2 à 5 catégories seulement → camembert()
│   │   ├─ Plus de 5 catégories, ou comparaison de plusieurs ensembles → unit_chart(mode="proportion")
│   │   └─ … ET l'importance relative des catégories elles-mêmes compte
│   │      aussi (poids/taille de chaque catégorie) → mekko()
│   │
│   ├─ Je veux DÉCOMPOSER une variation en contributions → waterfall()
│   │   └─ … avec un seul message à faire ressortir (gris/accent) → cascade()
│   │
│   └─ Je veux comparer plusieurs entités sur PLUSIEURS CRITÈRES qualitatifs
│      à la fois (profil, pas une seule mesure) → radar()
│
├─ 2 variables numériques
│   ├─ Je veux montrer une RELATION/CORRÉLATION → nuage()
│   ├─ Je veux comparer AVANT/APRÈS sur 1 seule catégorie → comparaison_avant_apres()
│   ├─ Je veux comparer AVANT/APRÈS sur plusieurs catégories → slope()
│   │   └─ … avec seulement les plus fortes variations en accent → pente()
│   ├─ Je veux comparer une valeur à un OBJECTIF → bullet_chart()
│   ├─ Je veux montrer un ratio offre/demande → unit_chart(mode="ratio")
│   └─ Deux échelles très différentes à superposer → ligne_double_axe() [à venir]
│
├─ 3 variables numériques (X, Y, + taille OU couleur) → nuage(couleur_var=…) ou nuage(taille_var=…)
│   └─ … avec chaque point étiqueté directement (pas de légende) → nuage_annote()
│
├─ 4 variables numériques (X, Y, taille, couleur ordinale) → bulle_4d()
│
├─ Plus de 4 variables numériques → scatter_matrix() [à venir] ou coordonnees_paralleles() [à venir]
│
├─ Je veux mettre en avant 1 ou 2 éléments dans un ensemble (le reste en
│  contexte gris) → barres_focus() ou ligne_focus()
│
├─ Je veux des écarts positifs/négatifs par rapport à zéro → divergent()
│
├─ Je veux comparer la même mesure entre plusieurs sous-groupes,
│  un graphique par sous-groupe → facet()
│
├─ Je veux comparer la FORME de la distribution (densité) de plusieurs
│  groupes empilés visuellement → ridgeline()
│
├─ Une hiérarchie / structure imbriquée (parts dans des parts) → treemap() [à venir]
│
├─ Une proportion sous forme d'icônes/carrés comptables → waffle() [à venir]
│
├─ Un classement qui évolue dans le temps (qui dépasse qui) → bump()
│
├─ Je veux montrer comment une quantité se répartit et circule à travers
│  plusieurs étapes successives (budget, trafic, parcours) → flux()
│
└─ Une matrice (corrélation, confusion, pivot) → heatmap()
```

> Les fonctions marquées **[à venir]** ne sont pas encore implémentées — elles
> figurent ici pour que l'arbre reste complet ; en attendant, rapprochez-vous
> de l'alternative la plus proche listée dans ce guide.

---

## 2. Fiches par fonction

Chaque fiche suit le même format : une phrase, quand l'utiliser, quand ne pas
l'utiliser, le nombre de variables/catégories visé, les données attendues, un
exemple minimal, les erreurs courantes, et les fonctions proches.

### `ligne()`

- **En une phrase** : montre l'évolution d'une ou plusieurs séries dans le temps ou selon une variable ordonnée.
- **Utiliser quand** : vous avez une suite ordonnée (dates, années, étapes) et voulez en montrer la tendance.
- **Ne pas utiliser quand** : l'axe X n'a pas d'ordre naturel (catégories non ordonnées) — utilisez `barres()`.
- **Nombre de variables** : 1 axe X + 1 à ~5 séries Y.
- **Nombre de catégories recommandé** : pas de limite stricte sur les points, mais >5 séries simultanées devient illisible.
- **Données requises** : `x` (liste), `y_series` (dict `{"nom": [valeurs]}`).
- **Exemple minimal** : `ligne(x=[2020,2021,2022], y_series={"CA":[10,15,18]})`
- **Erreurs courantes** : empiler trop de séries (>5) sans `ligne_focus()` pour hiérarchiser ; axe Y ne démarrant pas à zéro pour des comparaisons d'amplitude.
- **Voir aussi** : `ligne_focus()`, `aire()`, `barres_connectees()`.

### `barres()`

- **En une phrase** : compare des valeurs entre catégories discrètes.
- **Utiliser quand** : vous comparez 2 à ~15 catégories sur une seule mesure.
- **Ne pas utiliser quand** : l'axe X représente le temps de façon continue avec beaucoup de points (préférez `ligne()`), ou pour montrer une distribution (préférez `box_plot()`).
- **Nombre de variables** : 1 catégorie + 1 valeur.
- **Nombre de catégories recommandé** : 2 à 15 (au-delà, passez en horizontal ou utilisez `lollipop()`/`barres_ranked()`).
- **Données requises** : `categories` (liste), `valeurs` (liste).
- **Exemple minimal** : `barres(categories=["A","B"], valeurs=[10,20])`
- **Erreurs courantes** : axe Y ne démarrant pas à zéro (déforme visuellement les écarts) ; tri arbitraire des catégories quand un ordre clair existe.
- **Voir aussi** : `barres_groupees()`, `barres_focus()`, `lollipop()`, `barres_ranked()`.

### `barres_groupees()`

- **En une phrase** : compare plusieurs séries côte à côte pour chaque catégorie.
- **Utiliser quand** : vous comparez 2 à 4 groupes sur chaque catégorie (ex : années, régions).
- **Ne pas utiliser quand** : plus de 4 groupes (les barres deviennent trop fines) — préférez `facet()` ou `barres_connectees()`.
- **Nombre de variables** : 1 catégorie + 2 à 4 séries.
- **Nombre de catégories recommandé** : 2 à 10.
- **Données requises** : `categories` (liste), `groupes` (dict `{"nom": [valeurs]}`).
- **Exemple minimal** : `barres_groupees(categories=["T1","T2"], groupes={"2023":[10,20],"2024":[15,18]})`
- **Erreurs courantes** : trop de groupes simultanés ; oublier que l'œil compare mal des barres non adjacentes.
- **Voir aussi** : `barres()`, `facet()`, `barres_connectees()`.

### `aire()`

- **En une phrase** : montre l'évolution d'une grandeur, seule ou en composition cumulée.
- **Utiliser quand** : vous voulez insister sur le volume sous la courbe, ou montrer comment des parts évoluent dans le temps (`empile=True`).
- **Ne pas utiliser quand** : les séries se croisent beaucoup en mode non empilé (les aires superposées deviennent illisibles) — préférez `ligne()`.
- **Nombre de variables** : 1 axe X + 1 à ~6 séries.
- **Nombre de catégories recommandé** : ≤6 séries empilées.
- **Données requises** : `x` (liste), `y_series` (dict).
- **Exemple minimal** : `aire(x=annees, y_series={"Mobile":[...], "Desktop":[...]}, empile=True)`
- **Erreurs courantes** : empiler des séries dont la somme n'a pas de sens métier ; trop de séries empilées (>6).
- **Voir aussi** : `ligne()`, `waterfall()`.

### `histogramme()`

- **En une phrase** : montre la distribution d'une seule variable numérique.
- **Utiliser quand** : vous avez une seule série de mesures brutes (pas déjà agrégées) et voulez voir sa forme.
- **Ne pas utiliser quand** : vous voulez comparer plusieurs groupes (préférez `box_plot()` ou `violin()`), ou vos données sont déjà des catégories/agrégats.
- **Nombre de variables** : 1.
- **Nombre de catégories recommandé** : non applicable (variable continue).
- **Données requises** : `data` (liste de valeurs brutes).
- **Exemple minimal** : `histogramme(data=salaires, bins=30)`
- **Erreurs courantes** : choisir un nombre de `bins` trop faible (masque la forme) ou trop élevé (bruite la forme).
- **Voir aussi** : `box_plot()`, `violin()`.

### `nuage()`

- **En une phrase** : montre la relation entre deux variables numériques, avec jusqu'à 2 dimensions encodées en plus (couleur, taille).
- **Utiliser quand** : vous explorez ou démontrez une corrélation, ou positionnez des entités sur deux axes continus.
- **Ne pas utiliser quand** : une des deux variables est catégorielle (préférez `barres()`), ou il y a très peu de points (<5, la relation n'est pas visuellement parlante).
- **Nombre de variables** : 2 (+ 1 via `couleur_var`, + 1 via `taille_var`).
- **Nombre de catégories recommandé** : non applicable.
- **Données requises** : `x`, `y` (listes numériques).
- **Exemple minimal** : `nuage(x=budget, y=conversions, ligne_tendance=True)`
- **Erreurs courantes** : ajouter une droite de tendance sur des données clairement non linéaires ; confondre corrélation et causalité dans le titre.
- **Voir aussi** : `bulle_4d()`.

### `camembert()`

- **En une phrase** : montre la répartition d'un tout en quelques parts.
- **Utiliser quand** : vous avez 2 à 5 catégories qui se somment à un total significatif.
- **Ne pas utiliser quand** : plus de 5 catégories (l'œil ne compare pas bien les angles) — préférez `unit_chart(mode="proportion")` ou `barres()`.
- **Nombre de variables** : 1 catégorie + 1 valeur (proportion d'un tout).
- **Nombre de catégories recommandé** : 2 à 5.
- **Données requises** : `labels`, `valeurs`.
- **Exemple minimal** : `camembert(labels=["Mobile","Desktop"], valeurs=[60,40])`
- **Erreurs courantes** : plus de 5 parts ; parts qui ne se somment pas à un tout cohérent.
- **Voir aussi** : `unit_chart()`.

### `heatmap()`

- **En une phrase** : visualise une matrice de valeurs (corrélation, pivot, confusion) par intensité de couleur.
- **Utiliser quand** : vous avez une matrice 2D de valeurs numériques comparables entre elles.
- **Ne pas utiliser quand** : les lignes/colonnes ne sont pas vraiment comparables entre elles (échelles différentes) — normalisez d'abord ou changez de représentation.
- **Nombre de variables** : 1 matrice (lignes × colonnes × valeur).
- **Nombre de catégories recommandé** : jusqu'à ~20×20 reste lisible.
- **Données requises** : `matrice` (array 2D).
- **Exemple minimal** : `heatmap(df.corr().values, labels_lignes=cols, labels_colonnes=cols)`
- **Erreurs courantes** : colormap arc-en-ciel non perceptuellement uniforme ; oublier d'annoter les valeurs sur de petites matrices où l'exactitude compte.
- **Voir aussi** : `nuage()` (pour des relations brutes plutôt qu'agrégées).

### `flux()`

- **En une phrase** : diagramme de Sankey — montre comment une quantité se répartit et circule à travers plusieurs étapes successives.
- **Utiliser quand** : vous décomposez un volume (budget, trafic, effectifs) en flux successifs entre étapes ordonnées (source → canal → résultat).
- **Ne pas utiliser quand** : le graphe contient un cycle (A → B → A, non supporté) ; ou pour comparer des catégories indépendantes sans relation de flux (préférez `barres()`) ; ou pour décomposer une variation dans le temps sur une seule dimension (préférez `waterfall()`/`cascade()`).
- **Nombre de variables** : 1 valeur par lien source→cible, N étapes.
- **Nombre de catégories recommandé** : jusqu'à une dizaine de nœuds par colonne (au-delà, pas de minimisation de croisement — la lisibilité se dégrade).
- **Données requises** : `liens` — liste de tuples `(source, cible, valeur)`. La colonne de chaque nœud est déduite automatiquement.
- **Exemple minimal** : `flux([("Recherche","Site A",120), ("Site A","Achat",90), ("Site A","Abandon",30)])`
- **Erreurs courantes** : créer un cycle involontaire en réutilisant un nom de nœud en aval comme s'il s'agissait d'une nouvelle étape ; trop de nœuds par colonne qui tassent les rubans.
- **Voir aussi** : `waterfall()`/`cascade()` (décomposition sur un seul axe plutôt qu'un flux multi-étapes), `barres_connectees()` (suivi temporel plutôt que répartition).

### `dashboard()`

- **En une phrase** : assemble plusieurs graphiques dans une seule figure en grille.
- **Utiliser quand** : vous présentez plusieurs indicateurs liés ensemble, dans un même export.
- **Ne pas utiliser quand** : un seul message clé doit ressortir (un dashboard dilue l'attention) — préférez un graphique narratif unique.
- **Nombre de variables** : variable selon les sous-graphiques.
- **Nombre de catégories recommandé** : 2 à 6 sous-graphiques.
- **Données requises** : `configs` (liste de dicts `{"type":..., **kwargs}`).
- **Exemple minimal** : `dashboard([{"type":"barres","categories":[...],"valeurs":[...]}])`
- **Erreurs courantes** : mélanger des échelles incomparables sans le signaler ; trop de sous-graphiques (>6) pour une lecture rapide.
- **Voir aussi** : `facet()` (pour répéter le *même* graphique par sous-groupe, plutôt que des graphiques différents).

### `dot_plot_comparatif()`

- **En une phrase** : compare plusieurs dimensions entre deux périodes sur un axe Y commun (point creux → point plein).
- **Utiliser quand** : vous montrez une progression multi-critères normalisée (scores 0–1, indices composites) entre deux dates.
- **Ne pas utiliser quand** : les dimensions n'ont pas une échelle comparable, ou vous comparez plus de deux périodes (préférez `ligne()` multi-séries).
- **Nombre de variables** : N dimensions × 2 périodes.
- **Nombre de catégories recommandé** : 3 à 8 colonnes.
- **Données requises** : `colonnes` (dict `{"nom": (avant, apres)}`).
- **Exemple minimal** : `dot_plot_comparatif({"News": (0.05,0.15), "Patents": (0.20,0.30)})`
- **Erreurs courantes** : mélanger des échelles non comparables (0–1 et 0–100) dans le même graphique.
- **Voir aussi** : `slope()` (équivalent pour des valeurs non normalisées).

### `bulle_4d()`

- **En une phrase** : cartographie des entités sur 4 dimensions (X, Y, taille, couleur ordinale) en une seule figure.
- **Utiliser quand** : vous construisez une matrice d'innovation, de priorisation de portefeuille ou de maturité avec 4 critères.
- **Ne pas utiliser quand** : moins de 3 variables suffisent (simplifiez en `nuage()`), ou les bulles se chevauchent trop (>~15 entités).
- **Nombre de variables** : 4 (X, Y, taille, couleur ordinale).
- **Nombre de catégories recommandé** : 5 à 15 bulles.
- **Données requises** : `x`, `y`, `taille`, `couleur_var` (listes alignées).
- **Exemple minimal** : `bulle_4d(x=[...], y=[...], taille=[...], couleur_var=[...])`
- **Erreurs courantes** : trop de bulles qui se superposent ; échelle de taille non perceptible (`taille_min`/`taille_max` trop proches).
- **Voir aussi** : `nuage()`.

### `nuage_annote()`

- **En une phrase** : nuage de points où chaque entité est étiquetée directement sur le graphique, sans légende.
- **Utiliser quand** : le nombre de points est petit (<30) et chacun a un nom qui doit apparaître à l'écran — positionnement d'entités, mapping stratégique.
- **Ne pas utiliser quand** : trop de points pour que les étiquettes restent lisibles (préférez `nuage()` seul, sans labels) ou 4 dimensions sont nécessaires (préférez `bulle_4d()`).
- **Nombre de variables** : 2 (+ 1 taille optionnelle) + labels.
- **Nombre de catégories recommandé** : 5 à 25 points étiquetés.
- **Données requises** : `x`, `y`, `labels` (listes alignées), `tailles` optionnel.
- **Exemple minimal** : `nuage_annote(x=[22,45], y=[3.2,1.8], labels=["A","B"])`
- **Erreurs courantes** : trop de points étiquetés qui se chevauchent ; `quadrants=True` sans `quadrant_labels` explicites (les cadrans restent muets) ; `zones_colorees=True` sans `quadrants=True` (ignoré silencieusement, aucune zone ne s'affiche).
- **Astuce matrice de priorisation** : `quadrants=True, zones_colorees=True, zone_couleurs=(...)` transforme le nuage en matrice de décision type BCG — 4 zones translucides nommées et colorées selon leur sens métier (ex. rouge = risque, vert = priorité).
- **Voir aussi** : `nuage()`, `bulle_4d()`.

### `unit_chart()`

- **En une phrase** : carrés de proportion (`mode="proportion"`) ou ratios offre/demande imbriqués (`mode="ratio"`) — alternative honnête au camembert.
- **Utiliser quand** : vous comparez de nombreuses catégories en proportion d'un maximum, ou un écart offre/demande (talent, capacité).
- **Ne pas utiliser quand** : vous avez seulement 2-3 catégories simples (un `camembert()` ou `barres()` suffit).
- **Nombre de variables** : 1 (proportion) ou 2 (ratio offre/demande).
- **Nombre de catégories recommandé** : 3 à 10.
- **Données requises** : `categories`, `valeurs` (+ `reference` en mode ratio).
- **Exemple minimal** : `unit_chart(categories=["Python","C++"], valeurs=[37,21], mode="proportion")`
- **Erreurs courantes** : confondre `valeurs` déjà-ratio et `reference`+`valeurs` à diviser en mode `"ratio"`.
- **Voir aussi** : `camembert()`.

### `mekko()`

- **En une phrase** : Marimekko chart — largeur de colonne = poids de la catégorie, hauteur empilée = composition normalisée à 100 %, deux dimensions croisées en une figure.
- **Deux versions** : `beau_graphique.mekko()` — neutre, chaque segment sa couleur (utilisable sans `narratif.py`). `narratif.mekko(..., focus=...)` — un segment en accent, le reste en gris.
- **Utiliser quand** : la composition de chaque catégorie compte (parts d'acteurs, mix produit) ET l'importance relative des catégories elles-mêmes compte aussi (taille de marché, volume) — les deux perdues si on les sépare en deux graphiques.
- **Ne pas utiliser quand** : toutes les catégories ont le même poids (la largeur variable ajoute de la complexité de lecture pour rien — préférez `barres_groupees(empile=True, normalise=True)`).
- **Nombre de variables** : 1 poids par catégorie + N segments empilés par catégorie.
- **Nombre de catégories recommandé** : 3 à 8 colonnes, 2 à 5 segments.
- **Données requises** : `categories`, `poids` (largeur, >0), `segments` (dict `{"nom": [valeurs par catégorie]}`).
- **Exemple minimal** : `mekko(["A","B"], [100,200], {"X":[30,10],"Y":[70,90]})`
- **Erreurs courantes** : colonnes trop nombreuses ou trop étroites qui perdent leurs étiquettes de segment ; oublier `focus` (version `narratif`) alors qu'un seul acteur/segment est le vrai sujet du message.
- **Voir aussi** : `unit_chart()`, `barres_groupees(empile=True)`.

### `barres_connectees()`

- **En une phrase** : pour chaque entité, montre N barres chronologiques reliées par une ligne, avec les variations entre périodes annotées en bulles.
- **Utiliser quand** : vous suivez plusieurs entités sur plusieurs périodes et la valeur absolue ET la variation comptent toutes les deux.
- **Ne pas utiliser quand** : plus de ~5 entités ou ~5 périodes simultanées (devient dense) — préférez `facet()` ou `ligne()`.
- **Nombre de variables** : 1 catégorie × N périodes.
- **Nombre de catégories recommandé** : 2 à 5 entités, 2 à 4 périodes.
- **Données requises** : `categories`, `periodes`, `valeurs` (liste de listes).
- **Exemple minimal** : `barres_connectees(categories=["IA"], periodes=["2022","2023"], valeurs=[[10,20]])`
- **Erreurs courantes** : trop d'entités × trop de périodes en même temps ; deltas illisibles si les valeurs sont très petites.
- **Voir aussi** : `barres_groupees()`, `slope()`.

### `box_plot()`

- **En une phrase** : compare la distribution complète (médiane, quartiles, extrêmes) de plusieurs groupes.
- **Utiliser quand** : vous comparez la dispersion de 2 à ~10 groupes, avec peu de points par groupe (<20) ou quand seuls les quartiles comptent.
- **Ne pas utiliser quand** : une seule série sans groupe de comparaison (préférez `histogramme()`), ou une série temporelle (préférez `ligne()`).
- **Nombre de variables** : 1 mesure × N groupes.
- **Nombre de catégories recommandé** : 2 à 10.
- **Données requises** : `data` (liste de listes), `categories` (optionnel).
- **Exemple minimal** : `box_plot(data=[[12,15,14],[20,25,23]], categories=["A","B"])`
- **Erreurs courantes** : interpréter les moustaches comme des min/max absolus (ce sont des seuils IQR) ; comparer des groupes de tailles d'échantillon très différentes sans le signaler.
- **Voir aussi** : `violin()`, `histogramme()`.

### `violin()`

- **En une phrase** : montre la forme complète de la distribution (densité) par groupe, au-delà des seuls quartiles.
- **Utiliser quand** : vous avez ≥20 points par groupe et la *forme* de la distribution (bimodalité, asymétrie) compte pour le message.
- **Ne pas utiliser quand** : peu de points par groupe (<20) — la densité estimée devient trompeuse, préférez `box_plot()`.
- **Nombre de variables** : 1 mesure × N groupes.
- **Nombre de catégories recommandé** : 2 à 8.
- **Données requises** : `data` (liste de listes), `categories` (optionnel).
- **Exemple minimal** : `violin(data=[serie_a, serie_b], categories=["A","B"])`
- **Erreurs courantes** : utiliser des violons sur de petits échantillons (forme non fiable) ; oublier `afficher_boxplot=True` quand un public non technique a besoin d'un repère médian explicite.
- **Voir aussi** : `box_plot()`.

### `waterfall()`

- **En une phrase** : décompose une variation en contributions positives et négatives successives entre un départ et une arrivée.
- **Utiliser quand** : vous expliquez une variation de CA, d'effectif ou de marge par des facteurs qui s'additionnent dans un ordre logique.
- **Ne pas utiliser quand** : l'ordre des contributions n'a pas de sens métier, ou vous comparez des catégories indépendantes sans relation cumulative (préférez `barres()`).
- **Nombre de variables** : 1 valeur × N contributions ordonnées.
- **Nombre de catégories recommandé** : 3 à 8 contributions.
- **Données requises** : `categories`, `valeurs` (variations signées), `total_debut`/`total_fin` (optionnels).
- **Exemple minimal** : `waterfall(categories=["Churn","Upsell"], valeurs=[-45,30], total_debut=500)`
- **Erreurs courantes** : contributions qui ne se cumulent pas réellement au total affiché ; oublier `total_debut`/`total_fin` et perdre le repère de départ/arrivée.
- **Voir aussi** : `comparaison_avant_apres()`, `divergent()`.

### `cascade()`

- **En une phrase** : version narrative de `waterfall()` — même décomposition en contributions cumulées, mais avec le total en couleur neutre et les contributions clairement vert/rouge selon le signe.
- **Utiliser quand** : le public doit distinguer immédiatement les facteurs qui aident de ceux qui pénalisent, sans lire chaque étiquette.
- **Ne pas utiliser quand** : les valeurs n'ont pas de signe naturel positif/négatif (préférez `waterfall()` avec des couleurs neutres).
- **Nombre de variables** : 1 valeur × N contributions signées.
- **Nombre de catégories recommandé** : 3 à 8 contributions.
- **Données requises** : `categories`, `valeurs` (premier = départ absolu, dernier = `label_total` = arrivée absolue).
- **Exemple minimal** : `cascade(categories=["Départ","Churn","Arrivée"], valeurs=[1200,-180,1450], label_total="Arrivée")`
- **Erreurs courantes** : oublier que l'élément `label_total` doit contenir la valeur absolue d'arrivée, pas un delta.
- **Voir aussi** : `waterfall()`.

### `lollipop()`

- **En une phrase** : tige + point pour classer des catégories, plus aéré qu'une barre pleine.
- **Utiliser quand** : vous classez 5 à ~30 catégories, avec ou sans seuil de référence.
- **Ne pas utiliser quand** : l'ordre des catégories est imposé et ne doit pas être trié (laissez `trier=False`), ou pour des séries temporelles.
- **Nombre de variables** : 1 catégorie + 1 valeur.
- **Nombre de catégories recommandé** : 5 à 30.
- **Données requises** : `categories`, `valeurs`.
- **Exemple minimal** : `lollipop(categories=["Nord","Sud"], valeurs=[82,65], ligne_ref=70)`
- **Erreurs courantes** : oublier de trier alors que le classement est le message ; trop de catégories (>30) qui tassent les étiquettes.
- **Voir aussi** : `barres()`, `barres_ranked()`.

### `slope()`

- **En une phrase** : pentes connectées entre deux colonnes de points — qui progresse, régresse ou stagne, catégorie par catégorie.
- **Utiliser quand** : vous comparez ~3 à 15 catégories entre exactement deux moments, et voulez insister sur la direction du changement plutôt que sur les valeurs seules.
- **Ne pas utiliser quand** : plus de deux périodes (préférez `ligne()`), ou trop de catégories (>15, les étiquettes se chevauchent).
- **Nombre de variables** : 1 catégorie × 2 périodes.
- **Nombre de catégories recommandé** : 3 à 15.
- **Données requises** : `categories`, `valeurs_gauche`, `valeurs_droite`.
- **Exemple minimal** : `slope(categories=["A","B"], valeurs_gauche=[10,20], valeurs_droite=[15,18])`
- **Erreurs courantes** : ne pas utiliser `focus` quand seules 1-2 catégories sont le vrai sujet, laissant toutes les lignes se battre pour l'attention.
- **Voir aussi** : `comparaison_avant_apres()`, `dot_plot_comparatif()`, `barres_connectees()`.

### `pente()`

- **En une phrase** : version narrative de `slope()` — seules les `top_n` entités à plus forte variation absolue reçoivent l'accent, le reste passe en gris.
- **Utiliser quand** : parmi de nombreuses catégories entre deux périodes, seules 1 à 3 méritent vraiment l'attention du lecteur.
- **Ne pas utiliser quand** : toutes les catégories sont d'intérêt égal (préférez `slope()` sans hiérarchisation).
- **Nombre de variables** : 1 catégorie × 2 périodes.
- **Nombre de catégories recommandé** : 3 à 15, avec `top_n` = 1 à 3.
- **Données requises** : `categories`, `valeurs_avant`, `valeurs_apres`.
- **Exemple minimal** : `pente(categories=["A","B","C"], valeurs_avant=[10,20,15], valeurs_apres=[15,18,15], top_n=1)`
- **Erreurs courantes** : `top_n` trop grand (dilue l'effet de hiérarchie, revient à `slope()`).
- **Voir aussi** : `slope()`, `comparaison_avant_apres()`.

### `bump()`

- **En une phrase** : classement (rang) de plusieurs entités qui évolue entre périodes, lignes lissées, rang 1 en haut.
- **Utiliser quand** : le message est « qui dépasse qui » dans un classement suivi dans le temps (parts de marché, ligues, popularité).
- **Ne pas utiliser quand** : la valeur absolue compte autant que le rang (préférez `ligne()` ou `barres_connectees()`).
- **Nombre de variables** : 1 rang entier × N périodes, par entité.
- **Nombre de catégories recommandé** : 3 à 8 entités, 3 à 8 périodes.
- **Données requises** : `periodes`, `series` (dict `{"nom": [rangs...]}`).
- **Exemple minimal** : `bump(periodes=["2022","2023"], series={"A":[1,2],"B":[2,1]})`
- **Erreurs courantes** : mélanger rangs et valeurs brutes dans `series` (les rangs doivent être des entiers 1..N).
- **Voir aussi** : `ligne()`, `barres_connectees()`.

### `radar()`

- **En une phrase** : profil multi-critères d'une ou plusieurs entités sur des axes disposés en étoile.
- **Utiliser quand** : vous comparez 2 à 5 entités sur 3 à 10 critères qualitatifs ou quantitatifs de même échelle (compétences, scores, notation).
- **Ne pas utiliser quand** : plus de 5 entités superposées (les polygones se chevauchent trop) ou les critères n'ont pas la même échelle — préférez `dot_plot_comparatif()` ou `bulle_4d()`.
- **Nombre de variables** : N critères × 1 à 5 entités.
- **Nombre de catégories recommandé** : 3 à 10 critères, 1 à 5 entités.
- **Données requises** : `categories` (critères), `series` (dict `{"nom": [val_par_critère]}`).
- **Exemple minimal** : `radar(categories=["Vitesse","Force"], series={"A":[8,7]})`
- **Erreurs courantes** : critères sur des échelles différentes sans normalisation préalable (fausse l'aire des polygones).
- **Voir aussi** : `dot_plot_comparatif()`.

### `ridgeline()`

- **En une phrase** : distributions de plusieurs groupes superposées et décalées verticalement (Joy Plot), pour comparer leur forme d'un coup d'œil.
- **Utiliser quand** : vous comparez la forme (bimodalité, asymétrie) de 3 à 10 groupes avec suffisamment de points chacun (≥20).
- **Ne pas utiliser quand** : moins de 3 groupes (préférez `violin()` ou `box_plot()`) ou peu de points par groupe (la densité estimée devient trompeuse).
- **Nombre de variables** : 1 mesure × N groupes.
- **Nombre de catégories recommandé** : 3 à 10 groupes.
- **Données requises** : `series` (dict `{"nom": [valeurs brutes...]}`), premier groupe affiché en haut.
- **Exemple minimal** : `ridgeline(series={"A": donnees_a, "B": donnees_b})`
- **Erreurs courantes** : `chevauchement` trop élevé qui masque des groupes derrière d'autres.
- **Voir aussi** : `violin()`, `box_plot()`.

### `facet()`

- **En une phrase** : petits multiples — répète le même graphique pour chaque valeur unique d'une colonne de regroupement.
- **Utiliser quand** : vous comparez une même mesure entre 3 à ~12 sous-groupes (régions, produits, segments) sans surcharger un seul graphique.
- **Ne pas utiliser quand** : plus d'une douzaine de sous-groupes (grille illisible), ou une simple superposition (`ligne()` multi-séries) suffit déjà.
- **Nombre de variables** : variable selon `type_graphique`.
- **Nombre de catégories recommandé** : 3 à 12 sous-groupes.
- **Données requises** : `data` (DataFrame ou dict de dicts), `x`, `y`, `par`.
- **Exemple minimal** : `facet(df, x="Mois", y="Ventes", par="Region", type_graphique="barres")`
- **Erreurs courantes** : `meme_echelle=False` alors qu'une comparaison honnête entre facettes est attendue ; trop de sous-groupes qui rendent chaque facette minuscule.
- **Voir aussi** : `barres_groupees()`, `dashboard()`.

### `barres_focus()`

- **En une phrase** : barres en gris neutre sauf 1 ou 2 éléments mis en accent — le regard va directement où l'analyse l'emmène.
- **Utiliser quand** : un seul élément (ou deux) doit ressortir dans un classement ou une comparaison, le reste servant de contexte.
- **Ne pas utiliser quand** : toutes les catégories sont également importantes pour le message (préférez `barres()` standard).
- **Nombre de variables** : 1 catégorie + 1 valeur + 1 focus.
- **Nombre de catégories recommandé** : 4 à 15.
- **Données requises** : `categories`, `valeurs`, `focus` (index ou liste d'index).
- **Exemple minimal** : `barres_focus(categories=["Jan","Fév","Mar"], valeurs=[42,38,71], focus=2)`
- **Erreurs courantes** : mettre plus de 2 éléments en focus (dilue l'effet) ; titre qui ne nomme pas explicitement l'élément en focus.
- **Voir aussi** : `barres()`, `barres_ranked()`.

### `ligne_focus()`

- **En une phrase** : graphique multi-lignes où une série ressort (couleur + épaisseur), les autres servent de contexte gris.
- **Utiliser quand** : une série raconte l'histoire principale parmi plusieurs (ex : un pays qui dépasse les autres).
- **Ne pas utiliser quand** : toutes les séries sont d'importance égale (préférez `ligne()` standard).
- **Nombre de variables** : 1 axe X + N séries, 1 en focus.
- **Nombre de catégories recommandé** : 3 à 10 séries de contexte.
- **Données requises** : `x`, `series` (dict), `focus_serie` (clé).
- **Exemple minimal** : `ligne_focus(x=annees, series={"FR":[...],"DE":[...]}, focus_serie="FR")`
- **Erreurs courantes** : oublier `annoter_fin=True` alors que le nom des séries de contexte aide à la lecture.
- **Voir aussi** : `ligne()`, `barres_focus()`.

### `comparaison_avant_apres()`

- **En une phrase** : barres doubles avant/après avec delta et flèche directionnelle annotés sur chaque paire.
- **Utiliser quand** : vous montrez l'effet d'un changement (refonte, campagne) sur 2 à ~8 indicateurs, à un seul moment avant et un seul après.
- **Ne pas utiliser quand** : plus de deux périodes (préférez `ligne()`), ou plus de 8 catégories (préférez `slope()`).
- **Nombre de variables** : 1 catégorie × 2 périodes.
- **Nombre de catégories recommandé** : 2 à 8.
- **Données requises** : `categories`, `avant`, `apres`.
- **Exemple minimal** : `comparaison_avant_apres(categories=["Conversion"], avant=[3.2], apres=[4.7])`
- **Erreurs courantes** : pourcentage de variation calculé sur une valeur de départ proche de zéro (delta % explosif et trompeur).
- **Voir aussi** : `slope()`, `divergent()`.

### `barres_ranked()`

- **En une phrase** : classement horizontal trié où le Top N reçoit l'accent, le reste s'efface en gris dégradé.
- **Utiliser quand** : le message est « voici les meilleurs/pires » parmi de nombreuses catégories (10+).
- **Ne pas utiliser quand** : le classement complet (pas seulement le top) a de l'importance pour chaque catégorie (préférez `lollipop()` sans dégradé).
- **Nombre de variables** : 1 catégorie + 1 valeur.
- **Nombre de catégories recommandé** : 8 à 30 (le top_n reste petit, 3 à 5).
- **Données requises** : `categories`, `valeurs`, `top_n`.
- **Exemple minimal** : `barres_ranked(categories=pays, valeurs=scores, top_n=3)`
- **Erreurs courantes** : `top_n` trop grand (perd l'effet de hiérarchie) ; ne pas trier les données en amont si un ordre spécifique est attendu en plus du tri par valeur.
- **Voir aussi** : `lollipop()`, `barres_focus()`.

### `divergent()`

- **En une phrase** : barres centrées sur zéro, colorées selon le signe — parfait pour des deltas ou des soldes.
- **Utiliser quand** : vos valeurs sont naturellement signées (variation, NPS, balance) et le signe est le message.
- **Ne pas utiliser quand** : les valeurs sont toutes positives (préférez `barres()`).
- **Nombre de variables** : 1 catégorie + 1 valeur signée.
- **Nombre de catégories recommandé** : 4 à 20.
- **Données requises** : `categories`, `valeurs` (signées).
- **Exemple minimal** : `divergent(categories=mois, valeurs=[-3.2, 5.1, 8.4])`
- **Erreurs courantes** : couleurs positif/négatif inversées par rapport à l'intuition culturelle du public (rouge = mauvais, vert = bon, sauf contexte financier où le rouge peut signifier différent).
- **Voir aussi** : `waterfall()`, `comparaison_avant_apres()`.

### `bullet_chart()`

- **En une phrase** : représentation compacte d'un KPI face à son objectif et à ses plages de performance (alternative honnête aux jauges).
- **Utiliser quand** : vous suivez 1 à ~8 KPIs contre un objectif et des seuils qualitatifs (mauvais/moyen/bon).
- **Ne pas utiliser quand** : il n'y a pas d'objectif ou de seuil de référence pertinent (préférez `barres()`).
- **Nombre de variables** : 1 valeur + 1 objectif + N seuils, par KPI.
- **Nombre de catégories recommandé** : 1 à 8 KPIs.
- **Données requises** : `kpis` (liste de dicts `{"nom","valeur","objectif","plages"}`).
- **Exemple minimal** : `bullet_chart([{"nom":"Conversion","valeur":4.7,"objectif":5.0,"plages":[2,4,6]}])`
- **Erreurs courantes** : plages de performance non cohérentes avec le sens métier (croissantes alors qu'une valeur basse est bonne).
- **Voir aussi** : `divergent()`.

---

## 3. Règles universelles de communication visuelle

1. Le titre est une affirmation, pas une étiquette : « Les ventes accélèrent au T3 » plutôt que « Ventes par trimestre ».
2. Le sous-titre porte le contexte (période, périmètre, unité) — pas le message, qui est déjà dans le titre.
3. Une couleur d'accent = un seul message. Si tout est en couleur, rien ne ressort.
4. Le gris n'est pas une couleur de remplissage par défaut, c'est un outil : il pousse le contexte à l'arrière-plan pour faire ressortir le signal.
5. L'axe Y des barres commence toujours à zéro — sinon les écarts visuels mentent sur les écarts réels.
6. L'axe Y des lignes peut ne pas commencer à zéro si la tendance (pas l'amplitude absolue) est le message — mais dites-le.
7. Triez les catégories par valeur quand l'ordre alphabétique ou d'arrivée n'a pas de sens pour le message.
8. N'utilisez jamais une palette arc-en-ciel sur une variable continue — elle n'est pas perceptuellement ordonnée. Préférez une colormap séquentielle (`viridis`, `Blues`).
9. Une légende séparée du graphique oblige l'œil à faire des allers-retours. Préférez l'annotation directe (étiqueter la ligne à son point final, comme le fait `ligne()`).
10. Le camembert n'est lisible que jusqu'à 5 parts — au-delà, les angles deviennent indiscernables.
11. Deux axes Y avec des échelles sans rapport (`twinx`) suggèrent une corrélation qui n'existe pas forcément — n'en abusez pas.
12. La 3D n'ajoute jamais de clarté à un graphique 2D — elle déforme les proportions perçues sans ajouter d'information.
13. Une note de source en bas de graphique est obligatoire dès qu'un chiffre peut être contesté.
14. Le format des nombres doit correspondre à l'usage du lecteur (`k€`, `%`, `×`) — pas au format brut de la donnée.
15. Annoter la valeur directement sur le graphique (sur la barre, au bout de la ligne) est presque toujours préférable à forcer le lecteur à lire l'axe.
16. Choisissez le graphique en fonction du message à transmettre, pas en fonction du type de graphique que vous savez déjà faire.
17. Une seule idée par graphique. Si vous avez deux messages, faites deux graphiques (ou un `dashboard()`/`facet()` avec un message d'ensemble clair).
18. Le rouge et le vert ne sont pas universellement « mauvais/bon » — vérifiez le contexte culturel et le daltonisme (voir `themes.palette_safe()`).
19. N'arrondissez pas les pourcentages au point de masquer un écart significatif (« +0 % » sur un delta de +0.4 pt est trompeur s'il est en réalité +40 %).
20. Si un graphique nécessite plus de 30 secondes d'explication orale pour être compris, simplifiez-le ou découpez-le.

---

## 4. Tableau de correspondance type de données → graphique

| Type de données | Question à poser | Graphique recommandé | Alternative | À éviter |
|---|---|---|---|---|
| Série temporelle, 1 mesure | La tendance évolue comment dans le temps ? | `ligne()` | `aire()` | `camembert()` |
| Série temporelle, composition qui change | Comment les parts évoluent-elles ensemble ? | `aire(empile=True)` | `facet()` par catégorie | `ligne()` superposée brute |
| Comparaison de catégories, peu nombreuses | Qui est devant, qui est derrière ? | `barres()` | `lollipop()` | `camembert()` à 6+ parts |
| Comparaison de catégories, nombreuses (10+) | Quel est le classement complet ? | `lollipop()` | `barres_ranked()` | `barres()` vertical serré |
| Mise en avant d'1-2 éléments dans un ensemble | Quel est l'élément qui compte ici ? | `barres_focus()` / `ligne_focus()` | `barres_ranked()` | Tout colorer différemment |
| Distribution d'une variable, 1 groupe | Comment les valeurs se répartissent-elles ? | `histogramme()` | `box_plot()` seul | `barres()` sur des moyennes seules |
| Distribution, plusieurs groupes, peu de points | Quel groupe est plus dispersé / plus haut ? | `box_plot()` | `violin()` si ≥20 pts/groupe | Moyennes seules sans dispersion |
| Distribution, plusieurs groupes, beaucoup de points | Quelle est la forme de chaque distribution ? | `violin()` | `box_plot()` | `histogramme()` superposés |
| Relation entre 2 variables continues | Y dépend-il de X ? | `nuage()` | `nuage(ligne_tendance=True)` | `ligne()` si X n'est pas ordonné |
| 4 dimensions sur des entités | Comment se positionnent les entités sur 4 critères ? | `bulle_4d()` | 2× `nuage()` côte à côte | Tableau de chiffres bruts |
| Répartition d'un tout, peu de parts | Comment le tout se découpe-t-il ? | `camembert()` | `unit_chart(mode="proportion")` | `camembert()` à 6+ parts |
| Répartition d'un tout, nombreuses parts | Quelle proportion pour chaque catégorie ? | `unit_chart(mode="proportion")` | `barres()` horizontal | `camembert()` |
| Composition ET poids des catégories | Comment ça se décompose, et laquelle de ces catégories pèse le plus ? | `mekko()` | `barres_groupees(empile=True)` si poids égaux | Camembert par catégorie (perd le poids relatif) |
| Ratio offre/demande | L'offre couvre-t-elle la demande ? | `unit_chart(mode="ratio")` | `divergent()` sur l'écart | `camembert()` |
| Avant/après, 1 catégorie | Qu'est-ce qui a changé ? | `comparaison_avant_apres()` | `divergent()` sur le delta | `barres_groupees()` à 2 barres |
| Avant/après, plusieurs catégories | Qui a progressé, qui a régressé ? | `slope()` | `comparaison_avant_apres()` | `ligne()` à 2 points |
| Décomposition d'une variation | Quels facteurs expliquent le changement total ? | `waterfall()` | `divergent()` par facteur | `barres()` empilées sans logique cumulative |
| KPI vs objectif | Sommes-nous dans la cible ? | `bullet_chart()` | `divergent()` sur l'écart à l'objectif | Jauge circulaire |
| Valeurs signées (delta, NPS, solde) | Où est-ce positif, où est-ce négatif ? | `divergent()` | `waterfall()` si cumulatif | `barres()` sans repère zéro visible |
| Comparaison entre sous-groupes, même mesure | Ce sous-groupe se comporte-t-il comme les autres ? | `facet()` | `barres_groupees()` si ≤4 groupes | Tout sur un seul graphique surchargé |
| Matrice de valeurs (corrélation, pivot) | Où sont les zones fortes/faibles ? | `heatmap()` | `nuage()` par paire de variables | Tableau de chiffres seul |
| Répartition d'un volume à travers plusieurs étapes | Comment ce volume se divise-t-il et circule-t-il ? | `flux()` | `barres_groupees()` empilées si 2 étapes seulement | Camembert par étape (perd la continuité) |
| Suivi temporel multi-entités avec variations | Qui progresse, de combien, à chaque étape ? | `barres_connectees()` | `slope()` si 2 périodes seulement | `barres_groupees()` dense |
| Classement qui évolue dans le temps | Qui dépasse qui, à quel moment ? | `bump()` | `ligne()` si la valeur absolue compte | `barres_groupees()` par période |
| Profil multi-critères d'entités | Comment ces entités se comparent-elles sur plusieurs axes ? | `radar()` | `dot_plot_comparatif()` | Tableau de scores brut |
| Distribution de plusieurs groupes, comparaison de forme | Quelle est la forme de chaque distribution, les unes à côté des autres ? | `ridgeline()` | `violin()` | `histogramme()` superposés |

---

## 5. Pièges courants

### Piège 1 — Axe Y des barres qui ne démarre pas à zéro

- **Ce qu'on voit souvent** : un graphique en barres dont l'axe Y commence à 80 au lieu de 0, faisant paraître une différence de 2 points comme un écart massif.
- **Pourquoi c'est un problème** : la hauteur des barres est l'information visuelle — la tronquer déforme la perception de l'écart réel.
- **La correction** : laissez `barres()` gérer l'axe Y automatiquement (il part toujours de zéro) ; si l'écart est trop petit pour être visible, c'est que `barres()` n'est pas le bon graphique — utilisez `divergent()` ou `comparaison_avant_apres()` pour montrer le delta directement.

### Piège 2 — Palette arc-en-ciel sur une variable ordonnée

- **Ce qu'on voit souvent** : une heatmap ou un nuage de points coloré avec une colormap `jet`/arc-en-ciel pour représenter une variable continue.
- **Pourquoi c'est un problème** : l'arc-en-ciel n'a pas d'ordre perceptuel — le jaune ne semble ni plus « haut » ni plus « bas » que le vert, donc l'œil ne peut pas lire l'intensité directement.
- **La correction** : utilisez une colormap séquentielle (`viridis`, `Blues`, `RdYlGn` pour du divergent autour d'un centre) — déjà le défaut dans `nuage()` et `heatmap()`.

### Piège 3 — Camembert à plus de 5 catégories

- **Ce qu'on voit souvent** : un camembert à 8-10 tranches, dont plusieurs sont à peine distinguables visuellement.
- **Pourquoi c'est un problème** : l'œil humain compare mal les angles au-delà de 4-5 parts ; les petites parts deviennent illisibles et leurs étiquettes se chevauchent.
- **La correction** : passez à `unit_chart(mode="proportion")` ou `barres()` horizontal trié par valeur décroissante.

### Piège 4 — Double axe Y avec des variables sans rapport

- **Ce qu'on voit souvent** : un graphique avec deux axes Y (`twinx`) superposant, par exemple, un chiffre d'affaires et une température, pour « montrer une corrélation ».
- **Pourquoi c'est un problème** : en choisissant arbitrairement l'échelle des deux axes, on peut faire se superposer presque n'importe quelles deux courbes — la corrélation visuelle suggérée est souvent fabriquée par le choix d'échelle, pas par les données.
- **La correction** : si la relation est réelle, montrez-la avec `nuage()` (X = variable 1, Y = variable 2) plutôt qu'en superposant deux séries temporelles sur deux échelles indépendantes.

### Piège 5 — Titre-étiquette au lieu de titre-affirmation

- **Ce qu'on voit souvent** : un titre du type « Ventes par mois, 2024 » qui décrit le contenu du graphique sans dire ce qu'il faut en retenir.
- **Pourquoi c'est un problème** : le lecteur doit lire tout le graphique pour deviner le message, alors que le titre est l'endroit où 90 % des lecteurs s'arrêtent.
- **La correction** : reformulez en affirmation — « Les ventes accélèrent depuis septembre » — et laissez le sous-titre porter le contexte descriptif (période, périmètre).

### Piège 6 — 3D inutile

- **Ce qu'on voit souvent** : des barres ou un camembert en perspective 3D « pour faire plus pro ».
- **Pourquoi c'est un problème** : la perspective déforme les proportions perçues (les éléments à l'arrière paraissent plus petits qu'ils ne le sont) sans ajouter la moindre information — c'est une 3ᵉ dimension visuelle pour une donnée qui n'en a que 2.
- **La correction** : restez en 2D. Si une vraie 3ᵉ variable existe, encodez-la en couleur ou en taille (`bulle_4d()`, `nuage(couleur_var=...)`) plutôt qu'en perspective.

### Piège 7 — Légende séparée au lieu d'annotation directe

- **Ce qu'on voit souvent** : un graphique en lignes avec une légende dans un coin, obligeant à faire des allers-retours entre les couleurs et les courbes.
- **Pourquoi c'est un problème** : la charge cognitive de mémoriser quelle couleur correspond à quelle série ralentit la lecture, surtout au-delà de 3-4 séries.
- **La correction** : annotez directement chaque série à son point final (c'est le comportement par défaut de `ligne()`) ou utilisez `ligne_focus()` pour ne nommer que ce qui compte.

### Piège 8 — Choisir le graphique avant de connaître le message

- **Ce qu'on voit souvent** : « je vais faire un camembert » décidé avant même de savoir ce qu'on veut démontrer.
- **Pourquoi c'est un problème** : le choix du graphique doit découler du message (comparaison ? tendance ? distribution ? décomposition ?) — pas l'inverse. Un mauvais choix de graphique peut rendre un message clair illisible, ou pire, suggérer un message qui n'est pas dans les données.
- **La correction** : formulez d'abord la phrase-titre (l'affirmation que le graphique doit prouver), puis utilisez la [section 1](#1-arbre-de-décision) ou le [tableau](#4-tableau-de-correspondance-type-de-données--graphique) de ce guide pour trouver la fonction adaptée à *cette* phrase.
