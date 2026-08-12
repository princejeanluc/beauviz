# CONTEXT — beau_graphique

Document de transfert de contexte pour **Claude Code**.  
À lire en entier avant toute modification du projet.

---

## 1. Origine et intention du projet

Ce projet est né d'un constat simple : les graphiques matplotlib par défaut sont fonctionnels mais ne communiquent pas. Quand on présente des résultats ou qu'on mène une analyse, un graphique doit **guider le regard** et **porter un message** — pas juste afficher des données.

Le projet construit une **librairie matplotlib maison** en français, orientée expérience utilisateur et communication visuelle. Elle est conçue pour être utilisée dans des notebooks Jupyter ou des scripts Python, sans dépendance à Plotly, Seaborn ou autre — matplotlib pur, mais avec une couche de design et de narration au-dessus.

L'utilisateur est francophone, travaille souvent avec des données africaines (exemples récurrents : Cameroun, FCFA, marchés africains), et veut pouvoir produire des graphiques impactants **vite**, sans passer du temps sur la conception à chaque fois.

---

## 2. Architecture du projet

```
beau_viz/
├── pyproject.toml            # packaging (mode pip install)
├── README.md                 # documentation complète
├── CONTEXT.md                # ce fichier
├── GUIDE_CHOIX.md            # guide autonome : quel graphique pour quel message
├── galerie.ipynb             # démo exécutable de tous les modules
├── demo_mckinsey.py          # génère une figure par fonction McKinsey
├── src/beau_graphique/
│   ├── beau_graphique.py           # socle — graphiques de base (ligne, barres, aire, ...)
│   ├── beau_graphique_mckinsey.py  # graphiques McKinsey (dot_plot_comparatif, bulle_4d, ...)
│   ├── beau_graphique_layout.py    # mise en page (slide, layout_rapport)
│   ├── beau_graphique.mplstyle
│   ├── narratif.py           # graphiques narratifs — hiérarchie visuelle
│   ├── pipeline.py           # intégration DataFrame optionnelle + formatage dates
│   ├── themes.py             # thèmes, palettes, daltonisme-safe
│   └── export.py             # PNG/PDF, export batch
└── tests/
    ├── test_mckinsey.py
    └── test_phase2.py
```

**Règle d'architecture fondamentale** : les modules sont indépendants et optionnels. On peut utiliser `beau_graphique.py` seul, ou l'enrichir avec les autres. Aucun module ne force un import obligatoire d'un autre — les imports croisés se font en `try/except` ou en import local dans la fonction.

**Double mode d'installation (restructuration)** : les fichiers vivent dans `src/beau_graphique/` mais restent des modules **à plat**, sans aucun import relatif entre eux (`import beau_graphique as bg`, jamais `from . import beau_graphique`). `pyproject.toml` déclare `py-modules = [...]` (7 modules, voir le fichier) avec `package-dir = {"" = "src/beau_graphique"}` — ça installe des modules top-level (pas un sous-paquet `beau_graphique.narratif`). Conséquence : les mêmes fichiers, copiés tels quels dans un dossier de travail (mode 1, zéro outillage) ou installés via `pip install -e .` (mode 2), s'utilisent avec exactement les mêmes imports (`from narratif import barres_focus`). Aucun bootstrap, aucun `sys.path.insert`, aucune branche `try/except ImportError` n'a été nécessaire pour ça — c'est la convention d'imports déjà en place (cross-imports en `import X as x` plats) qui rend les deux modes gratuits. Le seul compromis : `beau_graphique.mplstyle` n'est pas embarqué par le mode package (pas de `package_data` possible sans vrai sous-paquet) — `init()` retombe sur son fallback `rcParams` existant, qui couvrait déjà ce cas.

**Split de `beau_graphique.py` (2026-08-07)** : le fichier avait grossi à 3239 lignes / 43 fonctions, seuil jugé ingérable. Les fonctions McKinsey (`dot_plot_comparatif`, `bulle_4d`, `unit_chart`, `tendances_grille`, `tendances_comparatives`, `bump`, `radar`, `ridgeline`) sont parties dans `beau_graphique_mckinsey.py`, et la mise en page (`slide`, `layout_rapport`) dans `beau_graphique_layout.py`. Les deux nouveaux fichiers font `import beau_graphique as bg` pour lire `PALETTE`/`_T` à chaud (jamais `from beau_graphique import PALETTE`, qui figerait une copie obsolète après un `themes.appliquer()`). `beau_graphique.py` les réimporte à sa toute fin (après ses propres définitions, pour que l'import circulaire reste sûr) — `from beau_graphique import dot_plot_comparatif` continue de fonctionner à l'identique. Les fonctions listées ci-dessous restent groupées par thème (socle / McKinsey / layout) dans ce document même si leur fichier a changé — voir le nom de fichier entre parenthèses dans chaque en-tête de sous-section.

---

## 3. État actuel — ce qui existe

### `beau_graphique.py` — socle

Fonctions publiques :
- `init()` — active le style `.mplstyle` pour toute la session
- `ligne(x, y_series, ...)` — lignes multi-séries, annote la valeur finale
- `barres(categories, valeurs, ...)` — vertical ou horizontal, valeurs sur barres
- `barres_groupees(categories, groupes, ...)` — barres côte à côte
- `aire(x, y_series, ...)` — aire simple ou empilée
- `histogramme(data, ...)` — distribution avec médiane auto, KDE optionnel
- `nuage(x, y, ...)` — scatter avec colormap, taille, droite de tendance
- `camembert(labels, valeurs, ...)` — donut ou camembert plein
- `heatmap(matrice, ...)` — matrice avec annotations et colormap
- `mekko(categories, poids, segments, ...)` — Marimekko chart (2026-08-12) : composition empilée à 100 % (hauteur) × poids de colonne (largeur), version neutre multi-couleur. Duplique volontairement la géométrie de `narratif.mekko()` (même précédent que `waterfall`/`cascade`, `slope`/`pente` : neutre dans le socle, narratif séparé) — sans ça, un utilisateur de `beau_graphique.py` seul (voir §2, modules indépendants) n'aurait aucun accès au Mekko.
- `dashboard(configs, ...)` — grille de graphiques, construite via `GridSpec` (voir §6)
- `flux(liens, noeuds=None, ...)` — diagramme de Sankey (2026-08-10) : rubans de Bézier entre nœuds, colonnes déduites automatiquement (plus long chemin depuis une source, DAG requis), largeur proportionnelle à la valeur. Aucun module dédié — l'API `matplotlib.sankey.Sankey` standard rend des angles droits, incompatible avec l'esthétique du reste de la lib.
- `dot_plot_comparatif(colonnes, descriptions=None, ...)` — McKinsey : comparaison multi-dimensions entre deux périodes (points creux/pleins + flèche)
- `bulle_4d(x, y, taille, couleur_var, ...)` — McKinsey : scatter à 4 variables (position, taille, couleur ordinale), quadrants optionnels
- `unit_chart(categories, valeurs, mode="proportion"|"ratio", ...)` — McKinsey : carrés de proportion ou de ratio offre/demande imbriqué
- `box_plot(data, categories=None, ...)` — distribution par groupe (quartiles), points individuels optionnels
- `violin(data, categories=None, ...)` — distribution par groupe (densité complète), mini-boxplot optionnel
- `waterfall(categories, valeurs, total_debut=None, total_fin=None, ...)` — décomposition d'une variation en contributions cumulées
- `lollipop(categories, valeurs, ...)` — classement tige + point, tri et ligne de référence optionnels
- `slope(categories, valeurs_gauche, valeurs_droite, ...)` — pentes avant/après par catégorie, focus ou coloration par direction
- `facet(data, x=None, y=None, par=None, type_graphique="ligne", ...)` — petits multiples (grille), `meme_echelle` pour synchroniser les axes Y

Voir [`GUIDE_CHOIX.md`](GUIDE_CHOIX.md) pour savoir quelle fonction utiliser selon le message à transmettre — c'est le document de référence pour choisir entre toutes ces fonctions (et celles de `narratif.py`).

Constante globale `PALETTE` — liste de 8 couleurs hex. Elle est **patchée à chaud** par `themes.py` lors de `appliquer()`.

**Convention de retour** : toutes les fonctions retournent `(fig, ax)`. Sans exception.

**Convention de style** : toutes les fonctions acceptent `titre`, `sous_titre`, `xlabel`, `ylabel`, `note`, `figsize`. Le `_finalize()` interne applique ces éléments de façon cohérente.

### `beau_graphique.mplstyle`

Fichier de style matplotlib. Attention : dans cet environnement, les couleurs doivent être en **tuples RGB (0-1)** et non en hex — les hex dans les fichiers `.mplstyle` causent des erreurs silencieuses selon la version de matplotlib. Le cycler de couleurs utilise des hex courts sans `#` (comportement vérifié).

### `narratif.py` — couche de communication visuelle

Principe central : **gris = contexte, couleur = signal**. Une seule couleur accent par graphique = un seul message.

Fonctions publiques :
- `barres_focus(categories, valeurs, focus, ...)` — toutes les barres grises sauf les indices `focus`
- `ligne_focus(x, series, focus_serie, ...)` — séries grises + 1 série en accent
- `comparaison_avant_apres(categories, avant, apres, ...)` — gris vs accent + delta ▲▼
- `barres_ranked(categories, valeurs, top_n, ...)` — classement avec opacité décroissante par rang
- `divergent(categories, valeurs, ...)` — centré zéro, vert/rouge
- `bullet_chart(kpis, ...)` — KPI vs objectif vs plages de performance
- `barres_connectees(categories, periodes, valeurs, ...)` — McKinsey : barres chronologiques par entité reliées par une ligne, deltas annotés en bulles colorées
- `cascade(categories, valeurs, label_total="Total", ...)` — version narrative de `waterfall()` (accent vert/rouge selon le signe)
- `pente(categories, valeurs_avant, valeurs_apres, top_n=3, ...)` — version narrative de `slope()` (seules les `top_n` variations les plus fortes en accent)
- `nuage_annote(x, y, labels, tailles=None, focus=None, quadrants=False, zones_colorees=False, zone_couleurs=None, ...)` — scatter annoté directement (sans légende), bulles et quadrants optionnels. `zones_colorees` (2026-08-12) remplit les 4 quadrants de rectangles translucides nommés — matrice de priorisation métier type BCG (risque/opportunité) ; ignoré silencieusement si `quadrants=False`
- `mekko(categories, poids, segments, focus=None, ...)` — Marimekko chart (2026-08-12) : composition empilée à 100 % (hauteur) × poids de colonne (largeur), `focus` sur un nom de segment applique gris=contexte/accent=signal via `palette_focus()`
- `palette_focus(n_total, indices_focus, accent)` — liste de couleurs utilitaire

Fonctions d'annotation (superposables sur n'importe quel `ax`) :
- `annoter_zone(ax, x_debut, x_fin, label, ...)` — rectangle coloré + étiquette
- `annoter_seuil(ax, y, label, ...)` — ligne horizontale de référence
- `annoter_delta(ax, x, y_debut, y_fin, label, ...)` — accolade verticale avec variation
- `annoter_point(ax, x, y, label, direction, ...)` — flèche + bulle sur un point

Constantes importantes :
```python
BG         = "#F7F8FC"
GRIS_FORT  = "#6B6F85"
GRIS_MOY   = "#A8ABBC"   # couleur des séries "contexte"
GRIS_CLAIR = "#D8DAE8"
TEXTE      = "#1A1C2E"
ACCENTS    = {"bleu": "#4361EE", "rouge": "#E63946", "vert": "#2DC653",
              "orange": "#F3722C", "violet": "#7209B7", "rose": "#F72585",
              "cyan": "#4CC9F0", "or": "#F4A261"}
```

Ces constantes sont **patchées à chaud** par `themes.appliquer()`. Ne pas les rendre locales aux fonctions.

### `pipeline.py` — couche DataFrame optionnelle

Philosophie : zéro friction. Si tu as des listes, ça marche comme avant. Si tu as un DataFrame, une ligne suffit.

Fonctions publiques :
- `resoudre(x, y, df, col_x, col_y, ...)` — résout x/y depuis n'importe quelle source (liste, array, dict, Series, DataFrame)
- `depuis_df(df, x, y, groupe, agg, ...)` — retourne un dict avec clés `x`, `y_series`, `categories`, `valeurs`, `groupes` — compatible avec toutes les fonctions de `beau_graphique`
- `inspecter(df)` — rapport terminal : types, NaN, outliers IQR, doublons + conseils automatiques
- `nettoyer(df, dropna, dedup, clip_outliers, renommer, trier_par, ...)` — pipeline de préparation verbeux
- `barres_df(df, x, y, groupe, ...)` — wrapper direct
- `ligne_df(df, x, y, groupe, ...)` — wrapper direct
- `nuage_df(df, x, y, ...)` — wrapper direct
- `histogramme_df(df, col, ...)` — wrapper direct
- `_formater_axe_dates(ax, x_list, freq=None)` — formate l'axe X d'un `ax` matplotlib selon la fréquence réelle des dates (D/M/Q/Y, auto-détectée ou imposée via `freq`). Appelée par `beau_graphique._formater_axe_dates()` (import local) — voir §6.

Compatibilité : pandas et polars. Les imports sont en `try/except` — si ni l'un ni l'autre n'est installé, les fonctions qui en ont besoin lèvent une `TypeError` claire.

### `themes.py` — système de thèmes

Fonctions publiques :
- `appliquer(nom_theme)` — active un thème : met à jour `plt.rcParams`, patche `beau_graphique.PALETTE`, `narratif.BG/TEXTE/GRIS_CLAIR/PALETTE`
- `appliquer_palette(palette)` — applique une liste de couleurs sans changer le reste
- `reinitialiser()` — revient au thème défaut
- `lister()` — aperçu terminal de tous les thèmes
- `apercu(palette_ou_theme)` — rendu visuel matplotlib d'une palette
- `depuis_couleur(couleur_base, n, methode)` — génère une palette depuis une couleur de marque (5 méthodes : analogique, complémentaire, triadique, monochrome, split)
- `palette_safe(n, type_daltonisme)` — palette daltonisme-safe

Thèmes disponibles (clés du dict `THEMES`) :
`defaut`, `finance`, `sante`, `academique`, `tech`, `minimal`, `chaud`, `sombre`, `daltonisme_safe`, `deuteranopie`, `sequentielle_bleu`, `divergente`

Chaque thème contient : `fond`, `texte`, `grille`, `palette` (liste de 8 hex), optionnellement `mode` ("sombre") et `linestyles` (pour académique).

---

## 4. Principes de design à respecter absolument

Ces principes ont guidé toutes les décisions. Toute nouvelle fonction doit les respecter.

**Principe 1 — Optionnalité totale**  
Aucun paramètre ne doit être obligatoire sauf les données elles-mêmes. `titre`, `sous_titre`, `note`, `xlabel`, `ylabel` sont toujours optionnels et défaut à `""`. Jamais de `None` requis explicitement.

**Principe 2 — Retour systématique (fig, ax)**  
Toutes les fonctions de graphique retournent `(fig, ax)` — sans exception. Cela permet de superposer des annotations après coup. `bullet_chart` retourne `(fig, axes)` (liste) car multi-axes.

**Principe 3 — Verbosité utile**  
Les fonctions qui modifient des données (`nettoyer`, `appliquer`, `inspecter`) impriment un résumé de ce qu'elles ont fait. Paramètre `verbose=True` par défaut, `False` pour silencer.

**Principe 4 — Gris pour le contexte**  
Dans `narratif.py`, les éléments non-focus ne disparaissent pas — ils passent en `GRIS_MOY` avec opacité réduite. L'œil voit le contexte sans y être attiré. Ne jamais `set_visible(False)` sur un élément de contexte.

**Principe 5 — Un seul accent par graphique**  
Les fonctions narratives acceptent un `accent` unique. Même `barres_focus` avec plusieurs indices focus utilise la même couleur accent — la multiplicité des cibles est gérée par l'opacité, pas par des couleurs différentes.

**Principe 6 — Compatibilité descendante stricte**  
Les nouvelles fonctions s'ajoutent, les existantes ne changent pas de signature. Si une signature doit évoluer, on ajoute des paramètres avec des valeurs par défaut qui reproduisent l'ancien comportement.

**Principe 7 — Français partout**  
Noms de fonctions, paramètres, messages, commentaires : tout en français. Seules exceptions : les noms de variables internes très courts (`fig`, `ax`, `lw`, etc.) et les valeurs de paramètres matplotlib qui sont des chaînes anglaises imposées par l'API.

---

## 5. Conventions de code

```python
# Structure type d'une fonction dans beau_graphique.py
def ma_fonction(param_requis, param_opt="", figsize=None):
    """
    Une ligne de description.

    Parameters
    ----------
    param_requis : type — description
    param_opt    : str  — description (défaut : "")
    figsize      : tuple ou None — taille figure (défaut : (10, 5.6))

    Returns
    -------
    (fig, ax)

    Exemple
    -------
    >>> ma_fonction([1,2,3], param_opt="test")
    """
    fig, ax = _new_fig(figsize)
    # ... logique ...
    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, fig=fig)

# Structure type d'une fonction dans narratif.py
def ma_fonction_narrative(params, accent=ACCENT_DEFAUT, figsize=None):
    fig, ax = _init_ax(figsize)
    # ... logique avec GRIS_MOY pour contexte, accent pour signal ...
    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig), ax
```

Helpers internes (préfixés `_`) :
- `_new_fig(figsize)` dans `beau_graphique.py` — crée une figure avec style appliqué
- `_init_ax(figsize)` dans `narratif.py` — crée une figure avec le style narratif (fond, spines, grille)
- `_finalize(ax, ...)` dans `beau_graphique.py` — applique titre/sous_titre/xlabel/ylabel/note/légende
- `_header(fig, ax, ...)` dans `narratif.py` — applique titre/sous_titre/note sur le style narratif
- `_is_df(obj)` dans `pipeline.py` — détecte pandas/polars sans import obligatoire

---

## 6. Problèmes connus et limitations actuelles

**`depuis_df()` cassait systématiquement `ligne()`, `barres()`, `barres_groupees()` — RÉSOLU**  
Bug critique découvert en construisant `galerie.ipynb` (exécution réelle, pas juste lecture du code) : `depuis_df()` retourne toujours les 5 clés `x`, `categories`, `y_series`, `valeurs`, `groupes` quel que soit le mode, mais chaque fonction cible n'en accepte qu'un sous-ensemble. Résultat : **les patterns documentés dans le README (`ligne(**depuis_df(...))`, `barres_groupees(**depuis_df(..., groupe=...))`) levaient systématiquement un `TypeError`**, et les wrappers `barres_df()`/`ligne_df()` (qui passent par le même mécanisme dans `_wrap_beau`) étaient cassés aussi. Autrement dit, la promesse centrale de `pipeline.py` ("zéro friction... une ligne suffit") ne fonctionnait jamais en pratique.  
Fix : `ligne()`, `barres()`, `barres_groupees()` acceptent désormais `**_extra` (clés ignorées) dans `beau_graphique.py`. C'est un correctif volontairement permissif uniquement sur ces 3 fonctions — les 5 autres (`aire`, `histogramme`, `nuage`, `camembert`, `heatmap`) restent strictes car non documentées comme cibles de `depuis_df()`.

**`dashboard()` dans `beau_graphique.py` — RÉSOLU**  
Toutes les fonctions de `beau_graphique.py` (`ligne`, `barres`, `barres_groupees`, `aire`, `histogramme`, `nuage`, `camembert`, `heatmap`) acceptent désormais un paramètre optionnel `ax=None`. Si fourni, la fonction trace dans cet axe au lieu d'en créer un nouveau, et `fig.tight_layout()` n'est pas appelé (pour ne pas perturber une figure composite). `dashboard()` a été réécrit pour créer les axes directement via `fig.add_gridspec()` et appeler chaque fonction avec `ax=` — plus de copie d'artistes entre figures. Ce changement débloque aussi l'intégration de n'importe quelle fonction dans un layout matplotlib existant (`plt.subplots()`, sous-figures, etc.), pas seulement `dashboard()`.

**Couleurs hex dans `.mplstyle`**  
Les couleurs hex avec `#` dans les fichiers `.mplstyle` causent des warnings ou erreurs selon la version de matplotlib. Le fichier utilise des tuples RGB `(r, g, b)` où chaque valeur est entre 0 et 1. Le cycler utilise des hex sans `#` (comportement spécifique vérifié sur matplotlib 3.10).

**`appliquer()` dans `themes.py` et les couleurs**  
Quand `appliquer()` patche `narratif.BG`, `narratif.TEXTE` etc., les figures déjà créées avant l'appel ne sont pas mises à jour — seules les nouvelles figures bénéficient du thème. C'est le comportement attendu et voulu.

**`appliquer()` ne patchait pas `bg._T` — RÉSOLU (2026-08-10)**  
Bug découvert en vérifiant visuellement `flux()` sous `themes.appliquer("sombre")` (exécution réelle, comme pour le bug `depuis_df()` ci-dessus — une lecture du code seule ne l'aurait pas montré). `appliquer()` mettait à jour `plt.rcParams`, `bg.PALETTE` et les constantes de `narratif.py`, mais jamais `bg._T` (le dict `bg`/`texte`/`texte_dim`/`grille`/`fond_neutre`/`serie_dim` introduit avec le système de thème `light`/`dark` de `init()`). Conséquence : après un `appliquer("sombre")`, les couleurs de données changeaient bien, mais le texte/fond de **toute fonction lisant `_T`** — c'est-à-dire `dot_plot_comparatif`, `bulle_4d`, `unit_chart`, `tendances_grille`, `tendances_comparatives`, `bump`, `radar`, `ridgeline`, `slide`, `layout_rapport`, `box_plot`, `violin`, `waterfall`, `lollipop`, `slope`, `facet`, `dashboard`, `flux`, et tout `narratif.py` (qui lit `_bg._T` via `_t()`) — restait sur les valeurs du dernier `bg.init(theme=...)`. Cas concret observé : titre rendu en `#1A1C2E` (texte du thème clair) sur un fond de thème sombre, donc invisible.  
Fix : `appliquer()` calcule maintenant `texte_dim`/`serie_dim` par interpolation entre `texte` et `fond` (`_teinte_intermediaire()`, nouveau helper dans `themes.py`) et réassigne `bg._T` en entier. Les thèmes de `themes.py` ne définissent pas nativement `texte_dim`/`serie_dim`/`fond_neutre` (contrairement aux thèmes `light`/`dark` de `beau_graphique.THEMES`) — d'où l'interpolation plutôt qu'une valeur exacte.

**`tight_layout()` avec des sous-figures**  
`fig.tight_layout(hspace=..., wspace=...)` n'est pas supporté sur toutes les versions de matplotlib. Utiliser `fig.subplots_adjust()` ou `GridSpec` avec `hspace`/`wspace` à la création.

---

## 7. Axes d'enrichissement planifiés (par ordre de priorité)

### Priorité 1 — Nouveaux types de graphiques (`beau_graphique.py`)

**Waterfall, slope, lollipop, box_plot, violin, facet — FAIT (Phase 2)**  
Ces 6 fonctions sont implémentées, testées (`tests/test_phase2.py`) et documentées dans `README.md` et `GUIDE_CHOIX.md`. Voir §3 pour le détail des signatures.

**Beeswarm / Strip plot**  
Distribution de points individuels sans superposition — alternative à l'histogramme quand on a peu de points (<200) et qu'on veut voir chaque observation. Paramètres : `data`, `categories` (optionnel pour grouper), `jitter`.

**Scatter matrix / coordonnées parallèles**  
Pour visualiser plus de 4 variables numériques simultanément (au-delà de ce que `bulle_4d()` peut encoder). `scatter_matrix(df, colonnes, ...)` — grille de nuages de points par paire de variables. `coordonnees_paralleles(df, colonnes, groupe, ...)` — une ligne par observation, un axe vertical par variable.

**Treemap, waffle, bump chart**  
`treemap(labels, valeurs, parents=None, ...)` — hiérarchie imbriquée par aire. `waffle(categories, valeurs, ...)` — proportion en grille de carrés/icônes, alternative comptable au camembert. `bump_chart(categories, periodes, rangs, ...)` — classement qui évolue dans le temps (qui dépasse qui).

**Ligne double axe**  
`ligne_double_axe(x, y_gauche, y_droite, ...)` — deux échelles Y sur la même figure, avec avertissement explicite dans la docstring sur le risque de corrélation visuelle fabriquée (voir `GUIDE_CHOIX.md`, piège 4).

Voir [`GUIDE_CHOIX.md`](GUIDE_CHOIX.md) section 1 (arbre de décision) pour la place de chacune de ces fonctions futures parmi celles déjà disponibles.

### Priorité 2 — Mise en page narrative

Un système de layout complet pour les figures "rapport" ou "slide" :
- Bande supérieure avec 3-4 KPI cards (valeur + delta coloré + label)
- Titre posé comme une affirmation (pas une étiquette)
- Zone graphique principale
- Note de source standardisée en bas à gauche

Implémentation suggérée : une fonction `layout_rapport(kpis, fig_principale, titre, note)` qui crée une figure `GridSpec` composite.

### Priorité 3 — Annotations avancées (`narratif.py`)

**Timeline**  
Ligne horizontale avec jalons annotés (événements, versions, étapes). Paramètres : `dates`, `labels`, `descriptions`.

**Zone d'incertitude**  
Bande autour d'une courbe représentant un intervalle de confiance ou une projection. `annoter_incertitude(ax, x, y_bas, y_haut, label)`.

### Priorité 4 — Export (`export.py` — nouveau module)

- `sauvegarder(fig, nom, format)` — PNG haute résolution, PDF vectoriel
- `rapport_pdf(figs, nom)` — PDF multi-pages avec `fpdf2`
- `html_interactif(fig, nom)` — conversion vers Plotly pour zoom/hover
- `batch_export(figs_dict, dossier)` — exporte un dict `{nom: fig}` en une fois

---

## 8. Ce à quoi l'utilisateur n'a pas encore pensé

Ces points méritent d'être anticipés dans les prochains développements.

**Formats de date sur l'axe X — RÉSOLU (Phase 2, sensible à la fréquence)**  
Le formatage des dates a été refondu pour être sensible à la **fréquence réelle des points**, et non plus un format générique unique. `pipeline.py` porte désormais la logique : `_est_date(v)` (isinstance sur `datetime.date`/`datetime.datetime`/`pandas.Timestamp`), `_liste_est_dates(lst)` (heuristique majoritaire sur les 10 premières valeurs non-`None`), et `_formater_axe_dates(ax, x_list, freq=None)` qui détecte la fréquence à partir de l'écart moyen entre points consécutifs (`<32j`→"D", `<100j`→"M", `<400j`→"Q", sinon→"Y") et applique le format adapté (`"%d %b"` / `"%b %Y"` / `"T<n> %Y"` / `"%Y"`), avec rotation 35° des étiquettes au-delà de 6 points. `freq` peut être imposé explicitement. `beau_graphique._formater_axe_dates(ax, valeurs, freq=None)` reste le point d'entrée côté `beau_graphique.py` : il fait un pré-check rapide avec l'ancien `_es_date()` (premier élément seulement) puis délègue à `pipeline._formater_axe_dates()` via un import local. Branché dans `ligne()`, `aire()`, `nuage()` et désormais aussi **`barres()` en mode vertical** (gap comblé en Phase 2 — `barres()` n'avait aucun support de dates avant). `nuage(..., ligne_tendance=True)` reste corrigé pour fitter sur `mdates.date2num(x)`.  
**Reste à faire** : le même traitement n'a toujours pas été porté sur `narratif.py` (`ligne_focus` notamment). À faire si besoin, en réutilisant `beau_graphique._formater_axe_dates` (import local, comme la convention l'impose entre modules).

**Troncature des étiquettes longues**  
Avec des noms de catégories longs (>15 caractères), les labels se chevauchent sur l'axe X. Ajouter une détection automatique et un wrapping avec `textwrap.wrap()` ou une rotation automatique des labels selon leur longueur.

**Valeurs formatées selon le contexte**  
Actuellement les valeurs sur les barres s'affichent avec le format brut ou `{:,.0f}`. Il faudrait un paramètre `fmt_auto=True` qui détecte l'ordre de grandeur (milliers → "k", millions → "M", FCFA, %) et formate en conséquence.

**Reproductibilité des figures**  
Aucune graine aléatoire n'est fixée pour les fonctions qui utilisent `np.random` (beeswarm futur, jitter). Ajouter un paramètre `seed=None` optionnel.

**Gestion des très petits et très grands datasets**  
- Moins de 3 points : `ligne()` devrait avertir et utiliser des barres
- Plus de 1000 points sur un `nuage()` : ajouter automatiquement `alpha` réduit + un hint vers `hexbin`
- Plus de 20 catégories sur `barres()` : suggérer `horizontal=True`

**Tests automatisés — partiellement RÉSOLU**  
`tests/test_mckinsey.py` couvre les 4 fonctions McKinsey (`dot_plot_comparatif`, `bulle_4d`, `unit_chart`, `barres_connectees`) : retour `(fig, ax)`, paramètres vides, compatibilité `themes.appliquer()`, cas limites (taille de bulle constante, mode ratio avec/sans `reference`).  
`tests/test_phase2.py` couvre le formatage des dates (`ligne()` avec dates Python/pandas, entiers non traités comme dates), le retour `(fig, ax)` de `box_plot`/`violin`/`waterfall`/`lollipop`/`slope`, `facet()` avec un DataFrame, le paramètre `ax=` externe, et la compatibilité thème des nouvelles fonctions. `test_ligne_dates_pandas` utilise `freq="ME"` (alias pandas ≥2.2) — un `pytest.mark.skipif` (2026-08-07) le passe automatiquement en skip sur un environnement pandas <2.2 au lieu de rester rouge en permanence.  
`tests/test_geometrie.py` (2026-08-07) comble un angle mort : la quasi-totalité des tests précédents ne vérifiait que `(fig, ax)` / absence de crash, pas la géométrie réelle — un bug comme l'ancien "plateau plat" de `_dessiner_tendance_cat` (voir plus bas) serait resté invisible pour la suite. Il inspecte les coordonnées réelles des artistes matplotlib : `Polygon.get_xy()` a exactement 5 sommets distincts pour `tendances_comparatives()` (avec les bonnes valeurs Y, pas un plateau), la géométrie plate-mais-voulue de `tendances_grille()` (barres à sommet plat + pentes, différente et correcte), la continuité cumulative des `Rectangle` de `waterfall()`, les positions Y avant/après de `dot_plot_comparatif()`, et l'ordre (non trié) des tailles de bulles de `bulle_4d()`.  
Suite complète : 104/104 (environnement courant : pandas 2.2.3).  
**Reste à faire** : `tests/test_basique.py` (smoke tests des 8 fonctions de base de `beau_graphique.py` + `narratif.py` historique) et `tests/test_pipeline.py` (wrappers `_df`, `depuis_df()`) n'existent pas encore.

**Documentation interactive — RÉSOLU**  
`galerie.ipynb` existe désormais : démo exécutable de tous les modules (`beau_graphique`, `narratif`, `pipeline`, `themes`) sur un jeu de données réaliste (ventes Douala/Yaoundé, FCFA). Exécuté de bout en bout sans erreur (validé via `jupyter nbconvert --execute`) — c'est cette exécution réelle qui a révélé le bug `depuis_df()` ci-dessus, qu'une simple lecture du code n'aurait pas montré.

**Internationalisation partielle**  
Les messages d'erreur et de `inspecter()` sont en français. Si le projet est partagé avec des collaborateurs anglophones, prévoir un paramètre `lang="fr"` / `"en"` sur `inspecter()` et `nettoyer()`.

---

## 9. Flux de travail recommandé pour Claude Code

1. Lire `README.md` pour l'API publique complète
2. Lire ce fichier pour le contexte et les décisions de design
3. Lire le module ciblé avant toute modification
4. Vérifier que les fonctions existantes retournent toujours `(fig, ax)`
5. Ajouter des fonctions, ne pas modifier les signatures existantes
6. Tester avec un DataFrame minimal pandas avant de livrer
7. Mettre à jour `README.md` à chaque ajout de fonction publique

### Workflow git — à respecter à chaque session

Il n'y a pas de CI : rien n'empêche `main` local et `origin/main` de diverger
silencieusement si cette routine n'est pas suivie. C'est exactement ce qui
s'est produit le 2026-08-07 — une branche mergée via PR sur GitHub pendant
que 12 commits s'accumulaient en local, découvert seulement au moment du
`git push`.

1. **En début de session** : `git fetch origin` puis vérifier `git log
   HEAD..origin/main --oneline` — si non vide, `git merge origin/main` avant
   de commencer à travailler.
2. **Avant chaque commit** : lancer `python -m pytest tests/ -q` — décision
   assumée de ne pas mettre en place de CI pour l'instant, donc rien
   n'exécute les tests à votre place.
3. **En fin de session** : `git push origin main` — ne pas laisser de
   commits locaux non poussés d'une session à l'autre.

---

## 10. Structure cible du projet à terme

```
beau_viz/
├── pyproject.toml            # packaging pip install -e . — fait
├── src/beau_graphique/
│   ├── beau_graphique.py           # socle — stable
│   ├── beau_graphique_mckinsey.py  # McKinsey — stable
│   ├── beau_graphique_layout.py    # mise en page — stable
│   ├── beau_graphique.mplstyle
│   ├── narratif.py           # hiérarchie visuelle + barres_connectees — stable
│   ├── pipeline.py           # DataFrame — stable
│   ├── themes.py             # thèmes — stable
│   └── export.py             # PNG/PDF/batch — fait
├── tests/
│   ├── test_mckinsey.py      # fait
│   ├── test_phase2.py        # dates, box_plot/violin/waterfall/lollipop/slope/facet — fait
│   ├── test_export.py, test_layout.py, test_nouveaux_charts.py,
│   │   test_barres_empilees_et_narratif.py  # fait
│   ├── test_geometrie.py     # assertions sur coordonnées réelles (Polygon,
│   │   Rectangle, scatter) — pas seulement (fig, ax) — fait
│   ├── test_basique.py       # smoke tests des fonctions de base — à créer
│   └── test_pipeline.py      # tests DataFrame — à créer
├── galerie.ipynb              # démo visuelle complète — fait
├── demo_mckinsey.py            # démo des 4 fonctions McKinsey — fait
├── GUIDE_CHOIX.md              # guide de choix autonome — fait
└── README.md                  # documentation — à maintenir
```
