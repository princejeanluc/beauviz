# beau_graphique

Librairie matplotlib orientée **communication visuelle** — graphiques impactants, centrés expérience utilisateur, prêts à l'emploi en quelques lignes.

```
beau_viz/
├── pyproject.toml
├── src/beau_graphique/
│   ├── beau_graphique.py           # socle : graphiques de base (ligne, barres, aire, ...)
│   ├── beau_graphique_mckinsey.py  # graphiques McKinsey (dot_plot_comparatif, bulle_4d, ...)
│   ├── beau_graphique_layout.py    # mise en page (slide, layout_rapport)
│   ├── beau_graphique.mplstyle     # style global matplotlib
│   ├── narratif.py                 # hiérarchie visuelle & annotations
│   ├── pipeline.py                 # intégration DataFrame (optionnel)
│   ├── themes.py                   # thèmes, palettes, daltonisme-safe
│   └── export.py                   # sauvegarde PNG/PDF, export batch
└── tests/
```

Tous les modules sont des fichiers **à plat**, sans imports relatifs entre
eux (`import beau_graphique as bg`, jamais `from .beau_graphique import
...`). `beau_graphique_mckinsey.py` et `beau_graphique_layout.py` importent
le socle via `import beau_graphique as bg` et sont ré-importés à la fin de
`beau_graphique.py` — `from beau_graphique import dot_plot_comparatif`
fonctionne exactement comme si tout vivait dans un seul fichier. Ça permet
d'utiliser indifféremment l'un des deux modes d'installation ci-dessous — le
code applicatif (`from beau_graphique import ligne`) est identique dans les
deux cas.

---

## Installation

Deux modes, au choix selon le contexte :

### Mode 1 — copie de fichiers (zéro dépendance d'outillage)

Copiez les fichiers de `src/beau_graphique/` (les 4 `.py` + le `.mplstyle`)
directement dans votre dossier de travail. Aucune installation, aucun
`pip install` requis — pratique en notebook isolé ou environnement contraint.

### Mode 2 — package installable (`pip install`)

Depuis la racine du dépôt :

```bash
pip install -e .          # installation éditable (développement)
# ou
pip install .             # installation figée
```

Le package s'appelle `beau-graphique`, mais une fois installé les imports
restent identiques au mode copie : `import beau_graphique`, `from narratif
import barres_focus`, etc. — utilisable depuis n'importe quel dossier, sans
copier de fichiers.

> Le fichier `beau_graphique.mplstyle` n'est pas embarqué par le mode package ;
> `init()` retombe automatiquement sur des `rcParams` de repli équivalents,
> donc le style reste appliqué dans les deux modes.

**Dépendances** :

| Package | Requis | Usage |
|---|---|---|
| `matplotlib` | ✅ | rendu graphique |
| `numpy` | ✅ | calculs |
| `pandas` | optionnel | pipeline DataFrame |
| `polars` | optionnel | pipeline DataFrame |
| `scipy` | optionnel | courbe de densité dans `histogramme()` |

---

## Démarrage rapide

```python
from beau_graphique import init, ligne, barres, camembert

init()  # active le style — à appeler une fois en début de session

barres(
    categories=["Jan", "Fév", "Mar", "Avr"],
    valeurs=[42, 58, 51, 73],
    titre="Revenus mensuels",
)
```

---

## Module 1 — `beau_graphique.py`

Graphiques classiques avec style UX appliqué automatiquement.

### `init()`

Active le style global pour toute la session matplotlib.  
À appeler une fois, en début de notebook ou de script.

```python
from beau_graphique import init
init()
```

---

### `ligne(x, y_series, ...)`

Graphique en lignes multi-séries. Annote automatiquement la valeur finale de chaque série.

> **Dates automatiques** — si `x` contient des vraies dates (`datetime.date`,
> `datetime.datetime`, `pandas.Timestamp`, `np.datetime64`), l'axe est formaté
> automatiquement avec un format adapté à la fréquence réelle des points :
> `"%d %b"` pour des données journalières, `"%b %Y"` pour des données
> mensuelles, `"T<n> %Y"` pour des données trimestrielles, `"%Y"` pour des
> données annuelles — la fréquence est détectée à partir de l'écart moyen
> entre points consécutifs, ou imposée via `pipeline._formater_axe_dates(ax,
> x, freq="M")`. Les étiquettes pivotent automatiquement au-delà de 6 points.
> Les libellés textuels comme `"Jan"` ou `"T1"` restent traités comme des
> catégories — aucun parsing de chaîne n'est tenté. Même comportement dans
> `barres()` (mode vertical), `aire()` et `nuage()`.

```python
ligne(
    x=["Jan", "Fév", "Mar", "Avr", "Mai"],
    y_series={
        "Produit A": [42, 48, 55, 51, 63],
        "Produit B": [30, 35, 38, 42, 45],
    },
    titre="Évolution des ventes",
    sous_titre="S1 2024 · Toutes régions",
    xlabel="Mois", ylabel="k€",
    note="Source : ERP interne",
    markers=True,      # marqueurs ronds sur chaque point
    fill_last=False,   # aire légère sous la première série
)
```

---

### `barres(categories, valeurs, ...)`

Barres verticales ou horizontales. Affiche les valeurs sur les barres.

```python
barres(
    categories=["Marketing", "R&D", "Ventes", "Support"],
    valeurs=[85, 120, 95, 60],
    titre="Budget par département (k€)",
    horizontal=False,         # True → barres horizontales
    couleurs_multiples=True,  # chaque barre dans une couleur de la palette
    valeurs_sur_barres=True,
)
```

---

### `barres_groupees(categories, groupes, ...)`

Barres côte à côte pour comparer plusieurs séries.

```python
barres_groupees(
    categories=["T1", "T2", "T3", "T4"],
    groupes={
        "2023": [30, 45, 40, 60],
        "2024": [38, 50, 55, 72],
    },
    titre="Comparaison trimestrielle",
    ylabel="Ventes (k€)",
)
```

`empile=True` empile les barres (valeurs absolues) au lieu de les mettre
côte à côte ; `normalise=True` empile ET normalise chaque catégorie à 100 %
(implique `empile=True`) — utile pour comparer une composition (mix produit,
répartition d'appareils) plutôt que des valeurs absolues.

```python
barres_groupees(
    categories=["T1", "T2", "T3", "T4"],
    groupes={"Mobile": [40, 50, 55, 60], "Desktop": [60, 50, 45, 40]},
    empile=True, normalise=True,
    titre="Répartition du trafic (%)",
)
```

---

### `aire(x, y_series, ...)`

Graphique en aire simple ou empilée.

```python
aire(
    x=list(range(2018, 2025)),
    y_series={
        "Mobile":  [20, 28, 35, 42, 50, 58, 65],
        "Desktop": [60, 58, 54, 50, 45, 40, 35],
    },
    titre="Répartition du trafic",
    empile=True,   # False → aires superposées transparentes
)
```

---

### `histogramme(data, ...)`

Distribution avec ligne de médiane automatique. Optionnellement une courbe de densité KDE (nécessite `scipy`).

```python
histogramme(
    data=salaires,       # liste ou array numpy
    bins=30,
    titre="Distribution des salaires",
    xlabel="Salaire (FCFA)",
    courbe_densite=False,
)
```

---

### `nuage(x, y, ...)`

Nuage de points avec encodage optionnel couleur/taille et droite de tendance.

```python
nuage(
    x=budget_pub,
    y=conversions,
    couleur_var=conversions,   # colormap continue
    taille_var=None,           # taille proportionnelle
    labels=None,               # étiquettes sur les points
    ligne_tendance=True,       # régression linéaire
)
```

---

### `camembert(labels, valeurs, ...)`

Graphique circulaire ou donut moderne. La plus grande part est détachée automatiquement.

```python
camembert(
    labels=["Mobile", "Desktop", "Tablette", "Autre"],
    valeurs=[55, 30, 10, 5],
    titre="Répartition des appareils",
    donut=True,          # False → camembert plein
    exploser_max=True,   # détache la plus grande part
)
```

---

### `heatmap(matrice, ...)`

Matrice de corrélation, pivot, confusion matrix.

```python
heatmap(
    matrice=df.corr().values,
    labels_lignes=colonnes,
    labels_colonnes=colonnes,
    titre="Matrice de corrélation",
    cmap="RdYlGn",
    annot=True,
    fmt=".2f",
)
```

---

### `dashboard(configs, ...)`

Grille de graphiques dans une seule figure. Construit les axes directement
via `GridSpec` puis appelle chaque fonction avec `ax=` — pas de figure
intermédiaire.

```python
dashboard([
    {"type": "barres", "categories": mois, "valeurs": ventes, "titre": "CA"},
    {"type": "ligne",  "x": mois, "y_series": {"KPI": kpi}, "titre": "KPI"},
    {"type": "camembert", "labels": labels, "valeurs": parts, "titre": "Répartition"},
    {"type": "heatmap", "matrice": df.corr().values, "titre": "Corrélation"},
], titre_global="Tableau de bord Q1", ncols=2)
```

Types supportés : `ligne`, `barres`, `barres_groupees`, `aire`, `histogramme`,
`nuage`, `camembert`, `heatmap`, `flux`.

---

### `flux(liens, noeuds=None, couleur_ruban="source", ...)`

Diagramme de flux (Sankey) — rubans en courbes de Bézier entre nœuds
répartis automatiquement en colonnes (plus long chemin depuis une source),
largeur proportionnelle à la valeur. Aucune configuration de layout manuelle
requise. `liens` est une liste de tuples `(source, cible, valeur)`.

```python
from beau_graphique import flux

flux([
    ("Recherche", "Site A", 120), ("Pub", "Site A", 60),
    ("Site A", "Achat", 90), ("Site A", "Abandon", 90),
], titre="Parcours d'acquisition", sous_titre="Sessions, dernier trimestre")
```

`couleur_ruban="source"` (défaut) colore chaque ruban selon son nœud de
départ — `"cible"` ou une couleur hex fixe sont aussi acceptés.
`couleurs_noeuds={nom: couleur}` permet de fixer des couleurs explicites,
sinon `PALETTE` est cyclée par ordre d'apparition.

> **Limite connue** — `flux()` exige un graphe acyclique (DAG) : un lien qui
> reviendrait vers un nœud déjà visité (`A → B → A`) lève une erreur claire
> plutôt que de produire un rendu incohérent. Au-delà d'une dizaine de nœuds
> par colonne, la lisibilité se dégrade (pas de minimisation de croisement
> globale — seulement un tri local qui limite les croisements évidents).

---

### Tracer dans un axe existant — `ax=...`

Toutes les fonctions de `beau_graphique.py` et `narratif.py` acceptent un
paramètre optionnel `ax`. Si fourni, le graphique est tracé dans cet axe au
lieu d'en créer un nouveau — utile pour composer plusieurs graphiques dans
une figure matplotlib que vous contrôlez vous-même (sous-figures,
`plt.subplots()`, grilles personnalisées).

```python
import matplotlib.pyplot as plt
from beau_graphique import barres, ligne

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
barres(["A", "B", "C"], [10, 20, 15], ax=axes[0], titre="Barres")
ligne([1, 2, 3], {"Série": [5, 8, 6]}, ax=axes[1], titre="Ligne")
```

### Fond transparent — `background=...`

Toutes les fonctions publiques de `beau_graphique.py` et `narratif.py`
acceptent `background`. Valeurs possibles : `None` (fond du thème actif,
défaut), `"transparent"` (fond et axes transparents — pratique pour coller
la figure sur un slide PowerPoint déjà stylé), ou une couleur hex explicite.

```python
barres(["A", "B"], [10, 20], background="transparent")
```

### Bornes de l'axe Y — `vmin=`, `vmax=`

`ligne()`, `barres()` et `lollipop()` acceptent `vmin`/`vmax` pour forcer les
limites de l'axe Y au lieu de l'échelle automatique (utile pour synchroniser
plusieurs graphiques sur la même échelle, ou zoomer sur une plage précise).

```python
ligne(x, y_series={"KPI": valeurs}, vmin=0, vmax=100)
```

---

## Graphiques McKinsey

Quatre graphiques inspirés du style éditorial McKinsey — pour des présentations
à fort impact visuel. Trois vivent dans `beau_graphique.py`, un dans `narratif.py`
(il s'appuie sur les conventions narratives : `ACCENT_DEFAUT`, `GRIS_*`).

### `dot_plot_comparatif(colonnes, descriptions=None, label_avant="Avant", label_apres="Après", couleur=None, titre="", sous_titre="", note="", figsize=None)`

Compare N dimensions entre deux périodes sur un axe Y commun : un point creux
(avant) et un point plein (après), reliés par une flèche. Idéal pour montrer
une progression multi-critères (scores, KPIs, indicateurs composites).

```python
from beau_graphique import dot_plot_comparatif

dot_plot_comparatif(
    colonnes={"News": (0.05, 0.15), "Searches": (0.08, 0.19), "Patents": (0.20, 0.30)},
    label_avant="2020", label_apres="2024",
    titre="Score par vecteur (0 = faible ; 1 = élevé)",
)
```

### `bulle_4d(x, y, taille, couleur_var, labels=None, ..., quadrants=False, titre="", figsize=None)`

Nuage de bulles à 4 dimensions : position X/Y, taille (variable continue) et
couleur (variable ordinale 1→N). Permet de cartographier des entités sur 4 axes
d'analyse en une seule figure — usage recommandé pour des matrices d'innovation,
de maturité ou de priorisation de portefeuille.

```python
from beau_graphique import bulle_4d

bulle_4d(
    x=[0.9, 0.15, 0.1], y=[0.9, 0.55, 0.4],
    taille=[200, 10, 30], couleur_var=[4, 3, 3],
    labels=["IA", "Semi-conducteurs", "Connectivité"],
    label_couleur="Niveau d'adoption", quadrants=True,
)
```

### `unit_chart(categories, valeurs, mode="proportion", reference=None, ..., titre="", figsize=None)`

Carrés de proportion (mode `"proportion"`) ou de ratio offre/demande imbriqué
(mode `"ratio"`) — une alternative plus honnête au camembert pour comparer de
nombreuses catégories. Usage recommandé : comparaisons de parts/pénétration
(`"proportion"`) ou d'écarts offre/demande de talents, capacités, ressources
(`"ratio"`).

```python
from beau_graphique import unit_chart

unit_chart(
    categories=["Python", "C++", "GPU"], valeurs=[37, 21, 30],
    mode="proportion", titre="Talent requis",
)
```

### `barres_connectees(categories, periodes, valeurs, couleurs=None, groupes=None, ..., titre="", figsize=None)`

Pour chaque entité, N barres chronologiques reliées par une ligne suivant leur
sommet, avec les variations entre périodes annotées dans des bulles colorées.
Usage recommandé : suivi temporel multi-entités où la valeur absolue ET la
variation comptent (investissements, effectifs, parts de marché par période).

```python
from narratif import barres_connectees

barres_connectees(
    categories=["IA", "Cloud & Edge"],
    periodes=["2022", "2023", "2024"],
    valeurs=[[295, 245, 290], [40, 63, 95]],
    titre="Investissements par tendance, 2022–2024 (Mds$)",
)
```

### `tendances_grille(items, ncols=4, ...)`

Grille de mini-graphiques "barres temporelles" style rapport McKinsey — un
polygone continu (barres + pentes de transition + badge cumulatif) par
catégorie, chacune sur son propre axe Y.

```python
from beau_graphique import tendances_grille

tendances_grille([
    {"nom": "Intelligence artificielle", "valeurs": [95, 79, 117],
     "deltas": [-17, 48], "cumul": 22, "couleur": "#1B2A8A"},
    {"nom": "Cloud et edge computing", "valeurs": [26, 41, 61],
     "deltas": [58, 50], "cumul": 138, "couleur": "#4CC9F0"},
], ncols=2, titre="Investissements par tendance technologique")
```

### `tendances_comparatives(items, ncols=4, ...)`

Variante de `tendances_grille()` où les catégories d'une même rangée
**partagent le même axe Y** — pour comparer directement l'échelle absolue
entre catégories plutôt que leur seule forme. L'année intermédiaire devient
un point de convergence entre deux polygones distincts.

```python
from beau_graphique import tendances_comparatives

tendances_comparatives(items, ncols=2, titre="Comparaison à échelle commune")
```

### `bump(periodes, series, ...)`

Bump chart — évolution du classement (rang) de plusieurs entités entre
périodes, lignes lissées, rang 1 en haut.

```python
from beau_graphique import bump

bump(
    periodes=["2021", "2022", "2023", "2024"],
    series={"Orange": [1, 2, 1, 1], "MTN": [2, 1, 2, 3], "Camtel": [3, 3, 3, 2]},
    titre="Classement des opérateurs",
)
```

### `radar(categories, series, ...)`

Graphique radar (spider chart) — profil multi-dimensionnel d'une ou
plusieurs entités sur un même jeu de critères.

```python
from beau_graphique import radar

radar(
    categories=["Vitesse", "Force", "Endurance", "Précision", "Agilité"],
    series={"Joueur A": [8, 7, 9, 6, 9], "Joueur B": [6, 9, 7, 8, 7]},
    titre="Comparaison des profils athlétiques",
)
```

### `ridgeline(series, ...)`

Ridgeline plot (Joy Plot) — distributions superposées et décalées
verticalement, pour comparer la forme (KDE) de plusieurs groupes.

```python
from beau_graphique import ridgeline

ridgeline(series={
    "Groupe A": donnees_a, "Groupe B": donnees_b, "Groupe C": donnees_c,
}, titre="Comparaison des distributions")
```

### `slide(elements, nrows=3, ncols=4, ...)`

Mise en page libre façon éditeur de slides : chaque cellule d'une grille
reçoit du texte, un graphique (`fn=`/`kwargs=`), un KPI ou un callout.
Philosophie texte-first — on construit la narration avant les métriques.

```python
from beau_graphique import slide, barres

slide([
    {"pos": (0, 0, 1, 4), "type": "titre", "texte": "Le marché EMEA accélère au T3"},
    {"pos": (1, 0, 1, 1), "type": "texte", "texte": "Croissance organique au-delà des projections."},
    {"pos": (1, 1, 1, 2), "type": "graphique", "fn": barres,
     "kwargs": {"categories": mois, "valeurs": ventes}},
    {"pos": (1, 3, 1, 1), "type": "kpi", "valeur": "+18 %", "label": "Croissance T3", "positif": True},
], nrows=2, ncols=4)
```

### `layout_rapport(titre="", kpis=None, n_graphiques=1, ...)`

Gabarit rapport/slide prêt à l'emploi : bande titre + tuiles KPI en haut,
zone(s) graphique en bas (à remplir via `ax=` sur n'importe quelle fonction
de la librairie). Le style des tuiles KPI est configurable via `style_kpi`
(`"accent"`, `"filled"`, `"simple"`, `"minimal"`, ou un dict de flags bruts).

```python
from beau_graphique import layout_rapport, barres, ligne

fig, zones = layout_rapport(
    titre="Performance commerciale Q4 2024",
    kpis=[
        {"label": "Ventes", "valeur": "1,24 M", "delta": "+12 %", "positif": True},
        {"label": "Marge", "valeur": "23 %", "delta": "−2 pts", "positif": False},
    ],
    n_graphiques=2,
)
barres(mois, ventes, titre="Ventes par mois", ax=zones["graphiques"][0])
ligne(mois, {"Douala": v1, "Yaoundé": v2}, ax=zones["graphiques"][1])
```

---

## Distributions, contributions et comparaisons

Six fonctions de `beau_graphique.py` pour des cas d'usage qui ne sont ni des
séries temporelles ni des comparaisons catégorielles simples. Voir
[`GUIDE_CHOIX.md`](GUIDE_CHOIX.md) pour savoir laquelle choisir selon votre message.

### `box_plot(data, categories=None, ..., horizontal=False, afficher_points=False, titre="", figsize=None)`

Boîtes à moustaches : compare la distribution complète (médiane, quartiles,
valeurs extrêmes) de 2 à ~10 groupes.

```python
from beau_graphique import box_plot

box_plot(
    data=[[12, 15, 14, 18, 22], [20, 25, 23, 30, 19]],
    categories=["Équipe A", "Équipe B"],
    titre="Distribution des délais de livraison",
    afficher_points=True,
)
```

### `violin(data, categories=None, ..., afficher_boxplot=True, titre="", figsize=None)`

Violons : montre la forme complète de la distribution (densité), utile à
partir d'une vingtaine de points par groupe.

```python
from beau_graphique import violin

violin(
    data=[tailles_femmes, tailles_hommes],
    categories=["Femmes", "Hommes"],
    titre="Distribution des tailles",
)
```

### `waterfall(categories, valeurs, total_debut=None, total_fin=None, ..., titre="", figsize=None)`

Graphique en cascade : décompose une variation en contributions positives et
négatives successives entre une valeur de départ et une valeur d'arrivée.

```python
from beau_graphique import waterfall

waterfall(
    categories=["Nouveaux clients", "Churn", "Upsell"],
    valeurs=[80, -45, 30],
    total_debut=500, label_debut="CA 2023",
    total_fin=565, label_fin="CA 2024",
)
```

### `lollipop(categories, valeurs, ..., trier=True, ligne_ref=None, titre="", figsize=None)`

Tige + point : classement de catégories, alternative aérée aux barres pour
5 à ~30 catégories, avec ligne de référence optionnelle.

```python
from beau_graphique import lollipop

lollipop(
    categories=["Nord", "Sud", "Est", "Ouest", "Centre"],
    valeurs=[82, 65, 74, 58, 91],
    ligne_ref=70, label_ref="Objectif",
    titre="Taux de satisfaction par région",
)
```

### `slope(categories, valeurs_gauche, valeurs_droite, ..., focus=None, titre="", figsize=None)`

Pentes connectées : comparaison avant/après catégorie par catégorie entre
exactement deux périodes, avec mise en évidence optionnelle via `focus`.

```python
from beau_graphique import slope

slope(
    categories=["Produit A", "Produit B", "Produit C"],
    valeurs_gauche=[120, 80, 95],
    valeurs_droite=[140, 60, 95],
    label_gauche="2023", label_droite="2024",
)
```

### `facet(data, x=None, y=None, par=None, type_graphique="ligne", ncols=3, meme_echelle=True, titre="", figsize=None, **kwargs)`

Petits multiples : répète le même graphique (`"ligne"`, `"barres"`,
`"histogramme"` ou `"nuage"`) pour chaque valeur unique de `par`, sur une
grille — pour comparer 3 à ~12 sous-groupes côte à côte. Retourne
`(fig, axes)` où `axes` est un array d'Axes.

```python
from beau_graphique import facet

facet(df, x="Mois", y="Ventes", par="Region", type_graphique="barres")
```

---

## Module 2 — `narratif.py`

Graphiques orientés **communication de résultats** : hiérarchie visuelle, contraste, opacité, annotations dirigées.

> Principe : le gris porte le contexte, la couleur accent porte le message.

### Constantes utiles

```python
from narratif import ACCENTS, ACCENT_DEFAUT

ACCENTS = {
    "bleu": "#4361EE",   "rouge": "#E63946",
    "vert": "#2DC653",   "orange": "#F3722C",
    "violet": "#7209B7", "rose": "#F72585",
    "cyan": "#4CC9F0",   "or": "#F4A261",
}
```

---

### `barres_focus(categories, valeurs, focus, ...)`

Toutes les barres en gris sauf les indices `focus` qui reçoivent la couleur accent. Le label et la valeur de la barre ciblée passent automatiquement en gras.

```python
from narratif import barres_focus, ACCENTS

barres_focus(
    categories=["Jan", "Fév", "Mar", "Avr", "Mai", "Jun"],
    valeurs=[42, 38, 71, 55, 49, 63],
    focus=2,                    # index ou liste d'index
    titre="Mars affiche le pic du semestre",
    sous_titre="Ventes mensuelles · Produit A · S1 2024",
    accent=ACCENTS["rouge"],
    horizontal=False,
    fmt="{:.0f}",
)
```

---

### `ligne_focus(x, series, focus_serie, ...)`

Passe 1 : toutes les séries en gris fin (contexte).  
Passe 2 : la série ciblée en couleur accent + épaisseur doublée.

```python
ligne_focus(
    x=annees,
    series={
        "France":    [68, 71, 69, 65, 72, 75, 78],
        "Allemagne": [74, 76, 73, 70, 71, 73, 76],
        "Cameroun":  [41, 48, 55, 58, 65, 74, 79],
    },
    focus_serie="Cameroun",
    titre="Le Cameroun dépasse la France en 2024",
    accent=ACCENTS["vert"],
    annoter_fin=True,
)
```

---

### `comparaison_avant_apres(categories, avant, apres, ...)`

Barres grises (avant) vs accent (après) avec delta coloré ▲/▼ automatique.

```python
comparaison_avant_apres(
    categories=["Conversion (%)", "Panier moyen (€)", "Rétention (%)"],
    avant=[3.2, 42, 68],
    apres=[4.7, 55, 81],
    titre="La refonte UI améliore les 3 KPIs clés",
    label_avant="Avant refonte",
    label_apres="Après refonte",
    accent=ACCENTS["bleu"],
)
```

---

### `barres_ranked(categories, valeurs, top_n, ...)`

Classement horizontal trié. Le Top N reçoit l'accent avec opacité décroissante par rang (①②③). Le reste s'efface progressivement en gris.

```python
barres_ranked(
    categories=pays,
    valeurs=scores,
    titre="Top 3 des marchés les plus performants",
    top_n=3,
    accent=ACCENTS["or"],
    fmt="{:.0f}",
)
```

---

### `divergent(categories, valeurs, ...)`

Barres horizontales centrées sur zéro. Vert pour les valeurs positives, rouge pour les négatives.

```python
divergent(
    categories=mois,
    valeurs=[-3.2, +5.1, +8.4, -1.0, +12.3, -0.5],
    titre="Variation mensuelle du NPS",
    fmt="{:+.1f} pts",
)
```

---

### `bullet_chart(kpis, ...)`

Bullet charts (Stephen Few) — remplace les jauges. Plages de performance en gris, valeur actuelle en accent, objectif en trait noir.

```python
bullet_chart([
    {
        "nom":      "Taux de conversion",
        "valeur":   4.7,
        "objectif": 5.0,
        "plages":   [2, 4, 6],   # Mauvais / Moyen / Bon
        "fmt":      "{:.1f}%",
    },
    {
        "nom":      "Panier moyen",
        "valeur":   68,
        "objectif": 75,
        "plages":   [40, 60, 90],
        "fmt":      "{:.0f}€",
    },
], titre="Performance commerciale vs objectifs Q4")
```

---

### Annotations — à superposer sur n'importe quel graphique

Ces fonctions s'appellent **après** la création du graphique, sur l'axe retourné.

#### `annoter_zone(ax, x_debut, x_fin, label, ...)`

Rectangle coloré semi-transparent avec étiquette — pour signaler une période ou un événement.

```python
fig, ax = ligne_focus(...)
annoter_zone(ax, x_debut=8, x_fin=13, label="Crise Q2", couleur=ACCENTS["rouge"])
```

#### `annoter_seuil(ax, y, label, ...)`

Ligne horizontale de référence — objectif, seuil réglementaire, moyenne de marché.

```python
annoter_seuil(ax, y=100, label="Objectif 100k", couleur=ACCENTS["vert"])
```

#### `annoter_delta(ax, x, y_debut, y_fin, label, ...)`

Accolade verticale avec variation annotée — pour montrer une hausse ou une baisse.

```python
annoter_delta(ax, x=5, y_debut=42, y_fin=71, label="×1.7")
```

#### `annoter_point(ax, x, y, label, direction, ...)`

Flèche pointée sur un point de données avec bulle texte.

```python
annoter_point(ax, x=8, y=95, label="Pic historique",
              couleur=ACCENTS["rouge"], direction="haut")
```

---

### `cascade(categories, valeurs, label_total="Total", ...)`

Waterfall/bridge chart narratif : décompose une variation en contributions
positives (vert) et négatives (rouge) cumulées entre un départ et une
arrivée, avec pointillés de liaison entre les barres.

```python
from narratif import cascade

cascade(
    categories=["Départ", "Nouveaux", "Churn", "Upsell", "Arrivée"],
    valeurs=[1200, 340, -180, 90, 1450],
    label_total="Arrivée",
    titre="MRR : +250 k€ sur le trimestre",
)
```

### `pente(categories, valeurs_avant, valeurs_apres, top_n=3, ...)`

Slope chart narratif : compare N entités entre deux périodes, seules les
`top_n` entités à plus forte variation absolue reçoivent l'accent — les
autres passent en gris.

```python
from narratif import pente

pente(
    categories=["France", "Allemagne", "Espagne", "Italie"],
    valeurs_avant=[72, 68, 61, 55],
    valeurs_apres=[78, 65, 70, 52],
    label_avant="2022", label_apres="2024",
    titre="L'Espagne gagne 9 pts — plus forte progression",
    top_n=1,
)
```

### `nuage_annote(x, y, labels, tailles=None, focus=None, quadrants=False, ...)`

Scatter annoté : chaque point est étiqueté directement (pas de légende),
taille optionnelle en bulle, mise en accent d'un sous-ensemble via `focus`,
et quadrants de positionnement optionnels avec libellés.

```python
from narratif import nuage_annote

nuage_annote(
    x=[22, 45, 78, 31, 60], y=[3.2, 1.8, 4.5, 2.1, 3.8],
    labels=["A", "B", "C", "D", "E"],
    tailles=[100, 200, 500, 80, 320],
    focus=2, quadrants=True,
    quadrant_labels=("Faible/Fort", "Fort/Fort", "Faible/Faible", "Fort/Faible"),
)
```

### `palette_focus(n_total, indices_focus, accent)`

Génère une liste de couleurs — accent pour les indices ciblés, gris pour le reste.  
Utile pour colorer manuellement des éléments matplotlib.

```python
from narratif import palette_focus, ACCENTS

colors = palette_focus(6, indices_focus=[1, 3], accent=ACCENTS["rouge"])
# → [GRIS, ROUGE, GRIS, ROUGE, GRIS, GRIS]
```

---

## Module 3 — `pipeline.py`

Couche de résolution optionnelle entre vos données et les fonctions graphiques.  
**Rien n'est obligatoire** — si vous passez des listes, tout fonctionne comme avant.

### `inspecter(df)`

Rapport terminal avant de tracer : types, NaN par colonne, outliers IQR, doublons.  
Donne des conseils automatiques sur les nettoyages à effectuer.

```python
from pipeline import inspecter
inspecter(df)

# ┌──────────────────────────────────────────────────────────┐
# │  DataFrame — 500 lignes × 6 colonnes                    │
# ├──────────────────────────────────────────────────────────┤
# │  Colonne        Type         NaN    Unique  Plage        │
# │  Mois           object         —        12  Jan, Fév…   │
# │  Ventes         float64    4 (3%)      496  12.0 → 180k │
# │  ...                                                     │
# └──────────────────────────────────────────────────────────┘
# → NaN dans : ['Ventes', 'Marge'] — nettoyer(df, dropna=True)
# → ⚡ 'Ventes' : 2 outlier(s) IQR — nettoyer(df, clip_outliers=True)
```

---

### `nettoyer(df, ...)`

Pipeline de préparation avec paramètres à la carte. Tout est verbeux.

```python
from pipeline import nettoyer

df_propre = nettoyer(
    df,
    dropna="fill",        # True → supprime | "fill" → médiane/Inconnu | False → rien
    dedup=True,           # supprimer les doublons exacts
    clip_outliers=True,   # écrêter à ±3×IQR (moins agressif que 1.5)
    renommer={"rev": "Revenus", "qty": "Quantité"},
    trier_par="Mois",
    verbose=True,
)
# ✓ nettoyer() — 114 lignes × 6 colonnes
#   · lignes NaN supprimées : 6
#   · outliers 'Ventes' écrêtés ×2 [8.5 – 127.3]
#   · trié par 'Mois'
```

---

### `depuis_df(df, x, y, groupe, ...)`

Transforme un DataFrame en dict prêt à passer à `ligne()`, `barres()`, `barres_groupees()`.

```python
from pipeline import depuis_df

# Série simple
ligne(**depuis_df(df, x="Mois", y="Ventes"))

# Multi-colonnes Y
ligne(**depuis_df(df, x="Date", y=["Produit A", "Produit B", "Produit C"]))

# Groupé par catégorie (pivot automatique)
barres_groupees(**depuis_df(df, x="Trimestre", y="CA", groupe="Region"))
```

---

### `_formater_axe_dates(ax, x_list, freq=None)`

Formate l'axe X d'un graphique existant selon la fréquence réelle des dates
(`"D"` jour, `"M"` mois, `"Q"` trimestre, `"Y"` année — auto-détectée si
`freq` n'est pas fourni). Utilisé automatiquement par `ligne()`, `barres()`
(mode vertical) et `aire()` de `beau_graphique.py` ; appelable directement
pour forcer une fréquence ou formater un axe construit à la main.

```python
from pipeline import _formater_axe_dates

fig, ax = plt.subplots()
ax.plot(dates, valeurs)
_formater_axe_dates(ax, dates, freq="Q")  # force un format trimestriel
```

---

### `resoudre(x, y, df, ...)`

Résout x et y depuis n'importe quelle source. Utilisé en interne, mais accessible si besoin.

```python
from pipeline import resoudre

# Depuis des listes
x, y = resoudre(x=[1, 2, 3], y=[10, 20, 30])

# Depuis un DataFrame
x, y = resoudre(df=df, col_x="Mois", col_y="Ventes")

# Depuis un dict
x, y = resoudre(x={"Jan": 10, "Fév": 20, "Mar": 30})
```

---

### Wrappers directs `_df`

Sucre syntaxique — évitent le `**depuis_df()` intermédiaire.

```python
from pipeline import barres_df, ligne_df, nuage_df, histogramme_df

barres_df(df, x="Mois", y="Ventes", titre="CA mensuel")
barres_df(df, x="Région", y="CA", groupe="Produit")   # → barres_groupees
ligne_df(df, x="Date", y="Revenus")
ligne_df(df, x="Date", y=["A", "B", "C"])             # multi-colonnes
nuage_df(df, x="Budget", y="Conversions", ligne_tendance=True)
histogramme_df(df, col="Salaire", bins=30)
```

---

## Module 4 — `themes.py`

Système de thèmes global — met à jour matplotlib et la `PALETTE` de tous les modules simultanément.

### Thèmes disponibles

| Clé | Description |
|---|---|
| `defaut` | Palette bleue-rose vive, fond clair chaleureux |
| `finance` | Bleu marine + vert, sobre et professionnel |
| `sante` | Bleu, vert et rouge doux — tonalités médicales |
| `academique` | 8 couleurs distinguables en noir & blanc — publications |
| `tech` | Palette néon sur fond sombre — présentations |
| `minimal` | Gris + 1 accent — rapports Word/PDF épurés |
| `chaud` | Ambre et corail — slides percutants |
| `sombre` | Fond noir profond, palette vive |
| `daltonisme_safe` | Palette Wong (2011) — universelle tous types de daltonisme |
| `deuteranopie` | IBM palette — optimisée rouge-vert (8 % des hommes) |
| `sequentielle_bleu` | Dégradé clair→foncé pour une variable ordonnée |
| `divergente` | Rouge → blanc → bleu — données centrées sur 0 |

---

### `appliquer(nom_theme)`

Active un thème globalement.

```python
from themes import appliquer

appliquer("finance")
appliquer("daltonisme_safe")   # publications
appliquer("sombre")            # mode sombre
appliquer("tech")              # présentations
```

---

### `lister()`

Aperçu terminal de tous les thèmes disponibles.

```python
from themes import lister
lister()
```

---

### `apercu(palette_ou_theme)`

Rendu visuel d'une palette ou d'un thème — idéal en notebook.

```python
from themes import apercu

apercu()                              # thème actif
apercu("finance")                     # thème nommé
apercu(["#E63946", "#457B9D"])        # palette custom
```

---

### `depuis_couleur(couleur_base, n, methode)`

Génère une palette harmonieuse depuis une couleur de marque.

```python
from themes import depuis_couleur, appliquer_palette

# Méthodes disponibles : analogique · complementaire · triadique · monochrome · split
palette = depuis_couleur("#003566", n=6, methode="analogique")
appliquer_palette(palette)
```

---

### `palette_safe(n, type_daltonisme)`

Retourne les n premières couleurs d'une palette daltonisme-safe.

```python
from themes import palette_safe
from beau_graphique import barres

colors = palette_safe(4)                        # Wong universelle
colors = palette_safe(4, "deuteranopie")        # IBM rouge-vert
barres(cats, vals, couleur=colors[0])
```

---

### `appliquer_palette(palette)` / `reinitialiser()`

```python
from themes import appliquer_palette, reinitialiser

appliquer_palette(["#E63946", "#457B9D", "#1D3557"])
reinitialiser()   # revient au thème défaut
```

---

## Flux de travail complet

```python
# ── 0. Setup ─────────────────────────────────────────────────
from beau_graphique import init
from narratif import barres_focus, annoter_seuil, ACCENTS
from pipeline import inspecter, nettoyer, barres_df
from themes import appliquer

init()
appliquer("finance")

# ── 1. Données ───────────────────────────────────────────────
import pandas as pd
df = pd.read_csv("ventes.csv")

inspecter(df)
df = nettoyer(df, dropna="fill", dedup=True, trier_par="Mois")

# ── 2. Graphique de base ─────────────────────────────────────
barres_df(df, x="Mois", y="Ventes", titre="CA mensuel")

# ── 3. Graphique narratif ─────────────────────────────────────
fig, ax = barres_focus(
    categories=df["Mois"].tolist(),
    valeurs=df["Ventes"].tolist(),
    focus=df["Ventes"].idxmax(),
    titre="Septembre affiche le meilleur mois de l'année",
    accent=ACCENTS["rouge"],
)
annoter_seuil(ax, y=df["Ventes"].mean(), label="Moyenne annuelle")
```

---

## Prochains axes d'enrichissement

- **Nouveaux types** — `ligne_double_axe`, `scatter_matrix`, `coordonnees_paralleles`,
  `treemap`, `waffle`, `beeswarm` (voir [`GUIDE_CHOIX.md`](GUIDE_CHOIX.md))
- **Annotations avancées** — timeline, zones d'incertitude, intervalles de confiance
- **Export** — HTML interactif (Plotly) ; `export.py` couvre déjà PNG haute résolution,
  PDF vectoriel/multi-pages et export batch
