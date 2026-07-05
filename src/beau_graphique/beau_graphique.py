"""
beau_graphique.py
=================
Utilitaires pour créer des graphiques matplotlib impactants et centrés
sur l'expérience utilisateur — sans effort de conception répété.

Usage rapide
------------
    from beau_graphique import init, ligne, barres, camembert, aire, histogramme, nuage

    init()   # ← active le style une fois pour toute la session

Chaque fonction retourne (fig, ax) prêt à être affiché ou sauvegardé.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import datetime
import os
import textwrap

# ── Chemin vers le fichier de style (même dossier que ce module) ───────────
_STYLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beau_graphique.mplstyle")

# format= est utilisé comme nom de paramètre dans toutes les fonctions publiques ;
# on sauvegarde ici le built-in pour les rares endroits qui en ont besoin.
_fmt_builtin = format

# Palette par défaut (même ordre que dans le .mplstyle)
PALETTE = ["#4361EE", "#F72585", "#4CC9F0", "#7209B7",
           "#3A0CA3", "#F3722C", "#43AA8B", "#90BE6D"]

# Formats de figure prédéfinis
# Utilisez format="slide" au lieu de figsize=(13.33, 7.5)
FORMATS = {
    "slide":     (13.33, 7.5),    # 16:9 — PowerPoint, Google Slides
    "a4":        (11.69, 5.5),    # A4 paysage demi-hauteur — rapport Word / PDF
    "a4_pleine": (11.69, 8.27),   # A4 paysage pleine page
    "carre":     (7, 7),          # carré — réseaux sociaux, miniatures
    "large":     (14, 5.6),       # très large — dashboards multi-graphiques
}

# Registre de couleurs par entité
# Remplissez une fois en début de session pour assurer la cohérence
# des couleurs entre tous les graphiques d'un même rapport.
COULEURS_ENTITES: dict = {}

# ── Thèmes ──────────────────────────────────────────────────────────────────
# Chaque thème définit 6 rôles sémantiques consultés par toutes les fonctions.
# Passez votre propre dict à init(theme={...}) pour personnaliser entièrement.
THEMES: dict = {
    "light": {
        "bg":          "#F7F8FC",   # fond figure / axes
        "texte":       "#1A1C2E",   # texte principal (titres, annotations grasses)
        "texte_dim":   "#6B6F85",   # texte secondaire (sous-titres, axes, notes)
        "grille":      "#D8DAE8",   # lignes de grille, séparateurs légers
        "fond_neutre": "#FFFFFF",   # blanc neutre (trou donut, boîte violin, bord barre)
        "serie_dim":   "#A8ABBC",   # séries non-focus, éléments en retrait
    },
    "dark": {
        "bg":          "#0D1B2A",
        "texte":       "#E8ECF4",
        "texte_dim":   "#8A8FA8",
        "grille":      "#1E2D40",
        "fond_neutre": "#0D1B2A",
        "serie_dim":   "#3A4A5E",
    },
}

# Thème actif — toutes les fonctions le lisent via _T["clé"]
_T: dict = dict(THEMES["light"])


# ══════════════════════════════════════════════════════════════════════════════
# Initialisation
# ══════════════════════════════════════════════════════════════════════════════

def init(theme="light"):
    """
    Active le style beau_graphique et configure le thème visuel.

    Parameters
    ----------
    theme : str ou dict
        ``"light"`` (défaut) — fond clair, idéal pour rapports imprimés.
        ``"dark"``  — fond sombre, idéal pour slides et présentations dark.
        ``dict``    — thème personnalisé ; les clés manquantes sont héritées
                      du thème ``"light"``. Clés disponibles :
                      ``bg``, ``texte``, ``texte_dim``, ``grille``,
                      ``fond_neutre``, ``serie_dim``.

    Exemple
    -------
    >>> init()                             # thème clair par défaut
    >>> init(theme="dark")                 # thème sombre
    >>> init(theme={"bg": "#1A1A2E",       # thème personnalisé (Marine nuit)
    ...             "texte": "#EAEDF4",
    ...             "texte_dim": "#7B8499",
    ...             "grille": "#1E2440",
    ...             "fond_neutre": "#1A1A2E",
    ...             "serie_dim": "#3C4A66"})
    """
    global _T

    # ── Résoudre le thème ─────────────────────────────────────────────────────
    if isinstance(theme, str):
        if theme not in THEMES:
            valides = ", ".join(f'"{k}"' for k in THEMES)
            raise ValueError(f"Thème inconnu : '{theme}'. Valides : {valides}")
        resolved = dict(THEMES[theme])
    elif isinstance(theme, dict):
        resolved = {**THEMES["light"], **theme}
    else:
        raise TypeError(f"theme doit être str ou dict, reçu {type(theme).__name__}")

    _T = resolved
    nom_theme = theme if isinstance(theme, str) else "personnalisé"

    # ── Charger le style de base puis écraser avec les couleurs du thème ──────
    if os.path.exists(_STYLE_PATH):
        plt.style.use(_STYLE_PATH)

    plt.rcParams.update({
        "figure.facecolor":  _T["bg"],
        "axes.facecolor":    _T["bg"],
        "axes.edgecolor":    _T["grille"],
        "axes.labelcolor":   _T["texte_dim"],
        "text.color":        _T["texte"],
        "xtick.color":       _T["texte_dim"],
        "ytick.color":       _T["texte_dim"],
        "grid.color":        _T["grille"],
        "legend.facecolor":  _T["bg"],
        "legend.edgecolor":  _T["grille"],
        "savefig.facecolor": _T["bg"],
    })

    # ── Synchroniser les constantes de couleur de narratif.py ─────────────────
    try:
        import narratif as _nar
        _nar.BG         = _T["bg"]
        _nar.TEXTE      = _T["texte"]
        _nar.TEXTE_DOUX = _T["texte_dim"]
        _nar.GRIS_FORT  = _T["texte_dim"]
        _nar.GRIS_MOY   = _T["serie_dim"]
        _nar.GRIS_CLAIR = _T["grille"]
    except ImportError:
        pass

    print(f"✓ Style beau_graphique activé (thème : {nom_theme}).")


# ══════════════════════════════════════════════════════════════════════════════
# Helpers internes
# ══════════════════════════════════════════════════════════════════════════════

def _finalize(ax, titre="", sous_titre="", xlabel="", ylabel="",
              note="", legende=True, fig=None, ajuster_layout=True):
    """
    Applique les éléments textuels et visuels finaux communs à tous les graphiques.

    Parameters
    ----------
    ax        : Axes matplotlib
    titre     : Titre principal (gras)
    sous_titre: Ligne grise sous le titre
    xlabel    : Étiquette axe X
    ylabel    : Étiquette axe Y
    note      : Note de bas de figure (source, remarque…)
    legende   : Afficher la légende ou non
    fig       : Figure (nécessaire pour ajouter la note)
    ajuster_layout : Appeler fig.tight_layout() — à désactiver quand l'axe
                     fait partie d'une figure composite (ex: dashboard())
    """
    if titre:
        ax.set_title(titre, fontsize=15, fontweight="bold",
                     color=_T["texte"], pad=14, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 26), textcoords="offset points",
                    fontsize=10, color=_T["texte_dim"], annotation_clip=False)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    handles, labels = ax.get_legend_handles_labels()
    if legende and handles:
        ax.legend(loc="best")

    if note and fig:
        fig.text(0.01, -0.03, note, fontsize=8.5, color=_T["texte_dim"],
                 style="italic", transform=ax.transAxes)

    ax.yaxis.set_tick_params(length=0)
    ax.xaxis.set_tick_params(length=0)

    if fig and ajuster_layout:
        fig.tight_layout()
    return fig, ax


def _palette_pour(noms: list) -> list:
    """Retourne les couleurs pour une liste de noms, en consultant COULEURS_ENTITES
    en priorité et en tombant sur PALETTE en fallback."""
    return [
        COULEURS_ENTITES.get(str(nom), PALETTE[i % len(PALETTE)])
        for i, nom in enumerate(noms)
    ]


def enregistrer_couleurs(mapping: dict, fusionner: bool = True) -> None:
    """
    Associe des couleurs hex à des entités nommées (villes, produits, séries…)
    pour assurer la cohérence visuelle entre tous les graphiques d'un rapport.

    Parameters
    ----------
    mapping  : dict {"NomEntité": "#couleur_hex", ...}
    fusionner: True (défaut) — ajoute/met à jour le registre existant.
               False — remplace l'intégralité du registre.

    Exemple
    -------
    >>> enregistrer_couleurs({
    ...     "Douala":    "#4361EE",
    ...     "Yaoundé":   "#F3722C",
    ...     "Bafoussam": "#2DC653",
    ... })
    >>> barres(["Douala", "Yaoundé"], [79, 61])   # → bleu et orange automatiquement
    >>> ligne(x=mois, y_series={"Douala": [...], "Yaoundé": [...]})  # idem
    """
    global COULEURS_ENTITES
    if fusionner:
        COULEURS_ENTITES.update(mapping)
    else:
        COULEURS_ENTITES = dict(mapping)


def reinitialiser_couleurs() -> None:
    """Vide le registre de couleurs par entité."""
    COULEURS_ENTITES.clear()


def _couleurs_auto(categories, couleur_explicite=None, couleurs_multiples=False):
    """
    Résout la liste de couleurs pour barres().
    — couleur_explicite fourni → toutes les barres dans cette couleur.
    — Sinon, si couleurs_multiples=True OU au moins une catégorie est dans le
      registre → une couleur par catégorie (via _palette_pour).
    — Sinon → PALETTE[0] pour toutes.
    """
    if couleur_explicite is not None:
        return couleur_explicite
    if couleurs_multiples or any(str(c) in COULEURS_ENTITES for c in categories):
        return _palette_pour([str(c) for c in categories])
    return PALETTE[0]


_COULEUR_HAUT   = "#2DC653"   # vert — au-dessus du seuil
_COULEUR_BAS    = "#E63946"   # rouge — en-dessous du seuil
_COULEUR_NEUTRE = "#B0B3C6"   # gris — exactement égal au seuil

# ── Styles de tuiles KPI ────────────────────────────────────────────────────
# Chaque preset définit trois flags booléens. Passez un dict à style_kpi=
# dans layout_rapport() pour surcharger n'importe quelle combinaison.
_STYLE_KPI_PRESETS: dict = {
    "minimal": {"border": False, "accent_bar": False, "bg_fill": False},
    "simple":  {"border": True,  "accent_bar": False, "bg_fill": False},
    "accent":  {"border": False, "accent_bar": True,  "bg_fill": False},
    "filled":  {"border": False, "accent_bar": False, "bg_fill": True},
}


def colorier_si(seuil, couleur_haut=None, couleur_bas=None, couleur_egal=None):
    """
    Retourne une fonction ``fn_couleur(categorie, valeur) -> str`` qui colore
    chaque barre (ou point) selon sa position par rapport à un seuil.

    À passer au paramètre ``fn_couleur=`` de :func:`barres` ou :func:`lollipop`.

    Parameters
    ----------
    seuil        : valeur pivot (objectif, moyenne, cible…)
    couleur_haut : couleur quand valeur > seuil  (défaut : vert  #2DC653)
    couleur_bas  : couleur quand valeur < seuil  (défaut : rouge #E63946)
    couleur_egal : couleur quand valeur == seuil (défaut : gris  #B0B3C6)

    Exemple
    -------
    >>> barres(mois, ventes, fn_couleur=colorier_si(seuil=50_000))
    >>> lollipop(villes, scores, fn_couleur=colorier_si(70, couleur_bas="#F3722C"))
    """
    ch = couleur_haut or _COULEUR_HAUT
    cb = couleur_bas  or _COULEUR_BAS
    ce = couleur_egal or _COULEUR_NEUTRE

    def _fn(_, val):
        if val > seuil:  return ch
        if val < seuil:  return cb
        return ce

    return _fn


def colorier_selon(regles: list):
    """
    Retourne une fonction ``fn_couleur(categorie, valeur) -> str`` depuis une
    liste de règles priorisées.

    Chaque règle est un tuple ``(condition, couleur)`` :

    * ``condition`` : ``True`` (fallback toujours vrai) **ou** un callable
      ``(valeur) -> bool``.
    * ``couleur``   : chaîne hex (``"#2DC653"``) ou nom matplotlib (``"red"``).

    Les règles sont testées dans l'ordre ; la première qui correspond est
    retenue.  Terminez toujours par un fallback ``(True, couleur)``.

    Exemple
    -------
    >>> fn = colorier_selon([
    ...     (lambda v: v >= 80, "#2DC653"),   # vert  — excellent
    ...     (lambda v: v >= 50, "#F3722C"),   # orange — correct
    ...     (True,              "#E63946"),   # rouge  — insuffisant
    ... ])
    >>> barres(villes, scores, fn_couleur=fn)
    """
    def _fn(_, val):
        for condition, couleur in regles:
            if condition is True or condition(val):
                return couleur
        return PALETTE[0]

    return _fn


def _resoudre_figsize(figsize, format=None):
    """Retourne le figsize effectif depuis un preset ou une valeur explicite.
    figsize prend la priorité sur format si les deux sont fournis.
    """
    if figsize is not None:
        return figsize
    if format is not None:
        if format not in FORMATS:
            valides = ", ".join(f'"{k}"' for k in FORMATS)
            raise ValueError(f"format inconnu : '{format}'. Valides : {valides}")
        return FORMATS[format]
    return None


def _appliquer_background(fig, ax, background=None):
    """Applique le fond à figure et axe.
    None → _T["bg"] ; "transparent" → alpha=0 ; hex → couleur."""
    if background == "transparent":
        fig.patch.set_alpha(0)
        if ax is not None:
            ax.patch.set_alpha(0)
    else:
        bg = background if background is not None else _T["bg"]
        fig.patch.set_facecolor(bg)
        if ax is not None:
            ax.set_facecolor(bg)


def _new_fig(figsize=None, ax=None, format=None, background=None):
    """Crée une nouvelle figure, ou réutilise l'axe fourni si présent."""
    if ax is not None:
        return ax.figure, ax
    fig, new_ax = plt.subplots(figsize=_resoudre_figsize(figsize, format) or (10, 5.6))
    _appliquer_background(fig, new_ax, background)
    return fig, new_ax


def _es_date(valeurs) -> bool:
    """
    Vrai si la séquence contient des dates réelles (datetime, date, Timestamp,
    np.datetime64) — et non de simples libellés comme "Jan" ou "T1".
    Conservateur par construction : aucune tentative de parser des chaînes,
    pour ne jamais transformer des catégories textuelles en axe temporel.
    """
    if valeurs is None or len(valeurs) == 0:
        return False
    premier = valeurs[0]
    if isinstance(premier, (datetime.date, datetime.datetime)):
        return True
    if isinstance(premier, np.datetime64):
        return True
    return type(premier).__module__.startswith("pandas") and "Timestamp" in type(premier).__name__


def _formater_axe_dates(ax, valeurs, freq=None):
    """
    Si valeurs contient des dates, applique un format adapté à la fréquence
    réelle des points (jour/mois/trimestre/année) via pipeline._formater_axe_dates,
    et fait pivoter les étiquettes pour éviter le chevauchement.
    """
    if not _es_date(valeurs):
        return
    import pipeline
    pipeline._formater_axe_dates(ax, valeurs, freq=freq)


# ══════════════════════════════════════════════════════════════════════════════
# ① Graphique en lignes
# ══════════════════════════════════════════════════════════════════════════════

def ligne(x, y_series: dict, titre="", sous_titre="", xlabel="", ylabel="",
          note="", markers=True, fill_last=False, vmin=None, vmax=None,
          figsize=None, ax=None, format=None, background=None, **_extra):
    """
    Graphique en lignes multi-séries.

    Parameters
    ----------
    x          : Valeurs de l'axe X (liste ou array)
    y_series   : dict  {"Nom série": [valeurs], ...}
    markers    : Afficher les marqueurs ronds sur chaque point
    fill_last  : Remplir la zone sous la première série (effet aire légère)
    **_extra   : clés ignorées — permet d'appeler ligne(**depuis_df(...)) même
                 si le dict contient des clés destinées à d'autres fonctions
                 (categories, valeurs, groupes)

    Returns
    -------
    (fig, ax)

    Exemple
    -------
    >>> ligne(
    ...     x=[2020, 2021, 2022, 2023],
    ...     y_series={"Ventes A": [10, 18, 15, 25], "Ventes B": [8, 12, 20, 22]},
    ...     titre="Évolution des ventes",
    ...     xlabel="Année", ylabel="Unités (k)"
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    couleurs_series = _palette_pour(list(y_series.keys()))
    for i, (nom, vals) in enumerate(y_series.items()):
        color = couleurs_series[i]
        mk = "o" if markers else None
        ax.plot(x, vals, label=nom, color=color, marker=mk,
                markerfacecolor=_T["fond_neutre"], markeredgecolor=color,
                markeredgewidth=2, zorder=3)
        if fill_last and i == 0:
            ax.fill_between(x, vals, alpha=0.12, color=color)

    # Annotation valeur finale
    for i, (nom, vals) in enumerate(y_series.items()):
        color = couleurs_series[i]
        ax.annotate(f"{vals[-1]}",
                    xy=(x[-1], vals[-1]),
                    xytext=(6, 0), textcoords="offset points",
                    fontsize=9.5, color=color, fontweight="bold", va="center")

    if vmin is not None or vmax is not None:
        ax.set_ylim(vmin, vmax)
    _formater_axe_dates(ax, x)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ② Barres (verticales ou horizontales)
# ══════════════════════════════════════════════════════════════════════════════

def barres(categories, valeurs, titre="", sous_titre="", xlabel="", ylabel="",
           note="", couleur=None, horizontal=False, valeurs_sur_barres=True,
           couleurs_multiples=False, fn_couleur=None, vmin=None, vmax=None,
           figsize=None, ax=None, format=None, background=None, **_extra):
    """
    Graphique en barres simples (verticales ou horizontales).

    Parameters
    ----------
    categories         : Liste des étiquettes
    valeurs            : Liste de nombres
    horizontal         : True → barres horizontales (pratique pour beaucoup de catégories)
    valeurs_sur_barres : Afficher les valeurs directement sur/à côté des barres
    couleurs_multiples : Chaque barre dans une couleur de la palette
    **_extra           : clés ignorées — permet d'appeler barres(**depuis_df(...))
                          même si le dict contient des clés destinées à d'autres
                          fonctions (x, y_series, groupes)

    Exemple
    -------
    >>> barres(
    ...     categories=["Jan", "Fév", "Mar", "Avr"],
    ...     valeurs=[42, 58, 51, 73],
    ...     titre="Revenus mensuels",
    ...     ylabel="k€",
    ...     couleurs_multiples=True
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)

    if fn_couleur is not None:
        colors = [fn_couleur(cat, val) for cat, val in zip(categories, valeurs)]
    else:
        colors = _couleurs_auto(categories, couleur, couleurs_multiples)

    if horizontal:
        bars = ax.barh(categories, valeurs, color=colors, height=0.55)
        ax.invert_yaxis()
        if valeurs_sur_barres:
            for bar, val in zip(bars, valeurs):
                ax.text(bar.get_width() + max(valeurs) * 0.01, bar.get_y() + bar.get_height() / 2,
                        f"{val:,.0f}", va="center", ha="left", fontsize=9.5, fontweight="bold",
                        color=_T["texte"])
        ax.set_xlim(vmin if vmin is not None else 0, vmax if vmax is not None else max(valeurs) * 1.15)
        ax.xaxis.set_visible(False)
        ax.spines["bottom"].set_visible(False)
    else:
        bars = ax.bar(categories, valeurs, color=colors, width=0.55)
        if valeurs_sur_barres:
            for bar, val in zip(bars, valeurs):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(valeurs) * 0.01,
                        f"{val:,.0f}", ha="center", va="bottom", fontsize=9.5,
                        fontweight="bold", color=_T["texte"])
        ax.set_ylim(vmin if vmin is not None else 0, vmax if vmax is not None else max(valeurs) * 1.15)
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)
        _formater_axe_dates(ax, categories)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ③ Barres groupées
# ══════════════════════════════════════════════════════════════════════════════

def barres_groupees(categories, groupes: dict, titre="", sous_titre="",
                    xlabel="", ylabel="", note="", empile=False, normalise=False,
                    figsize=None, ax=None, format=None, background=None, **_extra):
    """
    Barres groupées, empilées ou normalisées (100 %) multi-séries.

    Parameters
    ----------
    categories : Étiquettes de l'axe X
    groupes    : dict {"Groupe A": [v1, v2, …], "Groupe B": [v1, v2, …]}
    empile     : True → barres empilées (valeurs absolues)
    normalise  : True → barres empilées normalisées à 100 % (implique empile=True)
    **_extra   : clés ignorées — permet d'appeler barres_groupees(**depuis_df(...))
                 même si le dict contient des clés destinées à d'autres fonctions

    Exemple
    -------
    >>> barres_groupees(
    ...     categories=["T1", "T2", "T3", "T4"],
    ...     groupes={"2023": [30, 45, 40, 60], "2024": [38, 50, 55, 72]},
    ...     titre="Comparaison trimestrielle",
    ...     ylabel="Ventes (k€)"
    ... )
    >>> barres_groupees(
    ...     categories=["T1", "T2", "T3", "T4"],
    ...     groupes={"Mobile": [40, 50, 55, 60], "Desktop": [60, 50, 45, 40]},
    ...     empile=True, normalise=True,
    ...     titre="Répartition du trafic (%)",
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    n_groupes = len(groupes)
    x = np.arange(len(categories))
    couleurs_groupes = _palette_pour(list(groupes.keys()))

    if empile or normalise:
        series = {nom: np.array(vals, dtype=float) for nom, vals in groupes.items()}
        if normalise:
            totaux = sum(series.values())
            totaux = np.where(totaux == 0, 1, totaux)
            series = {nom: vals / totaux * 100 for nom, vals in series.items()}

        bottom = np.zeros(len(categories))
        for i, (nom, vals) in enumerate(series.items()):
            ax.bar(x, vals, bottom=bottom, width=0.6, label=nom,
                   color=couleurs_groupes[i])
            for xi, (v, b) in enumerate(zip(vals, bottom)):
                if v > (3 if normalise else max(max(s) for s in series.values()) * 0.06):
                    ax.text(xi, b + v / 2, f"{v:.0f}{'%' if normalise else ''}",
                            ha="center", va="center", fontsize=8, color=_T["fond_neutre"],
                            fontweight="bold")
            bottom += vals

        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        if normalise:
            ax.set_ylim(0, 100)
            ax.yaxis.set_visible(False)
        else:
            ax.set_ylim(0, bottom.max() * 1.12)
            ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)
    else:
        width = 0.7 / n_groupes
        for i, (nom, vals) in enumerate(groupes.items()):
            offset = (i - n_groupes / 2 + 0.5) * width
            bars = ax.bar(x + offset, vals, width * 0.9, label=nom,
                          color=couleurs_groupes[i])
            for bar, val in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(max(v) for v in groupes.values()) * 0.01,
                        f"{val}", ha="center", va="bottom", fontsize=8.5, color=_T["texte"])

        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_ylim(0, max(max(v) for v in groupes.values()) * 1.18)
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ④ Graphique en aire
# ══════════════════════════════════════════════════════════════════════════════

def aire(x, y_series: dict, titre="", sous_titre="", xlabel="", ylabel="",
         note="", empile=False, figsize=None, ax=None, format=None, background=None):
    """
    Graphique en aire (simple ou empilée).

    Parameters
    ----------
    empile : True → aires empilées (stacked area chart)

    Exemple
    -------
    >>> aire(
    ...     x=list(range(2018, 2025)),
    ...     y_series={"Mobile": [20, 28, 35, 42, 50, 58, 65],
    ...               "Desktop": [60, 58, 54, 50, 45, 40, 35]},
    ...     titre="Répartition du trafic",
    ...     empile=True
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    noms = list(y_series.keys())
    valeurs = list(y_series.values())

    couleurs_series_aire = _palette_pour(noms)
    if empile:
        ax.stackplot(x, valeurs, labels=noms,
                     colors=[c + "CC" for c in couleurs_series_aire],
                     alpha=0.88)
    else:
        for i, (nom, vals) in enumerate(y_series.items()):
            color = couleurs_series_aire[i]
            ax.fill_between(x, vals, alpha=0.20, color=color)
            ax.plot(x, vals, label=nom, color=color, linewidth=2.4)

    _formater_axe_dates(ax, x)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑤ Histogramme
# ══════════════════════════════════════════════════════════════════════════════

def histogramme(data, bins=20, titre="", sous_titre="", xlabel="", ylabel="Fréquence",
                note="", courbe_densite=False, couleur=None, figsize=None, ax=None,
                format=None, background=None):
    """
    Histogramme avec optionnellement une courbe de densité KDE.

    Exemple
    -------
    >>> import numpy as np
    >>> histogramme(
    ...     np.random.normal(170, 8, 500),
    ...     bins=25,
    ...     titre="Distribution des tailles",
    ...     xlabel="Taille (cm)",
    ...     courbe_densite=True
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    color = couleur or PALETTE[0]

    ax.hist(data, bins=bins, color=color, alpha=0.75, edgecolor=_T["fond_neutre"], linewidth=0.5)

    if courbe_densite:
        from scipy.stats import gaussian_kde
        kde_x = np.linspace(min(data), max(data), 300)
        kde_y = gaussian_kde(data)(kde_x)
        # Mise à l'échelle pour correspondre à l'histogramme
        n, bin_edges = np.histogram(data, bins=bins)
        bin_width = bin_edges[1] - bin_edges[0]
        scale = len(data) * bin_width
        ax2 = ax.twinx()
        ax2.plot(kde_x, kde_y, color=PALETTE[1], linewidth=2.4, label="Densité")
        ax2.set_yticks([])
        ax2.spines["right"].set_visible(False)
        ax2.spines["top"].set_visible(False)

    # Ligne médiane
    mediane = np.median(data)
    ax.axvline(mediane, color=PALETTE[3], linewidth=1.8, linestyle="--", alpha=0.8)
    ax.text(mediane, ax.get_ylim()[1] * 0.97, f" Médiane\n {mediane:.1f}",
            color=PALETTE[3], fontsize=9, va="top")

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑥ Nuage de points
# ══════════════════════════════════════════════════════════════════════════════

def nuage(x, y, couleur_var=None, taille_var=None, labels=None,
          titre="", sous_titre="", xlabel="", ylabel="", note="",
          ligne_tendance=False, figsize=None, ax=None, format=None, background=None):
    """
    Nuage de points avec encodage optionnel couleur/taille.

    Parameters
    ----------
    couleur_var   : Array de valeurs numériques → colormap continue
    taille_var    : Array de valeurs → taille proportionnelle des points
    labels        : Liste de chaînes → étiquettes sur chaque point
    ligne_tendance: Ajouter une droite de régression linéaire

    Exemple
    -------
    >>> nuage(
    ...     x=[1,2,3,4,5], y=[2,4,3,6,5],
    ...     titre="Corrélation X / Y",
    ...     ligne_tendance=True
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)

    scatter_kw = dict(alpha=0.75, edgecolors=_T["fond_neutre"], linewidths=0.6)

    if couleur_var is not None:
        scatter_kw["c"] = couleur_var
        scatter_kw["cmap"] = "viridis"
    else:
        scatter_kw["color"] = PALETTE[0]

    if taille_var is not None:
        s_min, s_max = 40, 400
        arr = np.array(taille_var, dtype=float)
        scatter_kw["s"] = s_min + (arr - arr.min()) / (arr.ptp() or 1) * (s_max - s_min)
    else:
        scatter_kw["s"] = 70

    sc = ax.scatter(x, y, **scatter_kw)

    if couleur_var is not None:
        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        cbar.ax.tick_params(labelsize=9)

    if labels:
        for xi, yi, lb in zip(x, y, labels):
            ax.annotate(lb, (xi, yi), xytext=(5, 5), textcoords="offset points",
                        fontsize=8.5, color=_T["texte_dim"])

    if ligne_tendance:
        es_date_x = _es_date(x)
        x_num = mdates.date2num(x) if es_date_x else np.asarray(x, dtype=float)
        m, b = np.polyfit(x_num, y, 1)
        xfit_num = np.linspace(x_num.min(), x_num.max(), 200)
        xfit = mdates.num2date(xfit_num) if es_date_x else xfit_num
        label_tendance = "Tendance" if es_date_x else f"Tendance (y={m:.2f}x+{b:.2f})"
        ax.plot(xfit, m * xfit_num + b, color=PALETTE[1], linewidth=1.8,
                linestyle="--", alpha=0.8, label=label_tendance)

    _formater_axe_dates(ax, x)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑦ Camembert / Donut
# ══════════════════════════════════════════════════════════════════════════════

def camembert(labels, valeurs, titre="", sous_titre="", note="",
              donut=True, exploser_max=True, figsize=None, ax=None, format=None, background=None):
    """
    Graphique circulaire (camembert ou donut).

    Parameters
    ----------
    donut       : True → trou central (plus moderne)
    exploser_max: Détache légèrement la plus grande part pour la mettre en valeur

    Exemple
    -------
    >>> camembert(
    ...     labels=["Mobile", "Desktop", "Tablette", "Autre"],
    ...     valeurs=[55, 30, 10, 5],
    ...     titre="Répartition des appareils",
    ...     donut=True
    ... )
    """
    ajuster_layout = ax is None
    figsize = _resoudre_figsize(figsize, format)
    fig, ax = _new_fig(figsize or (7, 7), ax=ax, background=background)

    explode = [0] * len(valeurs)
    if exploser_max:
        explode[np.argmax(valeurs)] = 0.06

    wedge_kw = dict(linewidth=2.5, edgecolor=_T["fond_neutre"])
    wedges, texts, autotexts = ax.pie(
        valeurs, labels=None, autopct="%1.1f%%",
        colors=_palette_pour(labels), explode=explode,
        startangle=90, wedgeprops=wedge_kw,
        pctdistance=0.82 if donut else 0.65
    )

    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")

    if donut:
        circle = plt.Circle((0, 0), 0.55, color=fig.get_facecolor())
        ax.add_patch(circle)
        total = sum(valeurs)
        ax.text(0, 0, f"Total\n{total:,.0f}", ha="center", va="center",
                fontsize=12, fontweight="bold", color=_T["texte"])

    # Légende externe propre
    legend_patches = [mpatches.Patch(color=PALETTE[i], label=f"{lb}  ({v})")
                      for i, (lb, v) in enumerate(zip(labels, valeurs))]
    ax.legend(handles=legend_patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=10)

    ax.set_aspect("equal")

    if titre:
        ax.set_title(titre, fontsize=15, fontweight="bold",
                     color=_T["texte"], pad=18, loc="center")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0.5, 1.04), xycoords="axes fraction",
                    ha="center", fontsize=10, color=_T["texte_dim"])
    if note and fig:
        fig.text(0.5, -0.04, note, ha="center", fontsize=8.5,
                 color=_T["texte_dim"], style="italic")

    if ajuster_layout:
        fig.tight_layout()
    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑧ Heatmap (matrice de corrélation ou autre)
# ══════════════════════════════════════════════════════════════════════════════

def heatmap(matrice, labels_lignes=None, labels_colonnes=None,
            titre="", sous_titre="", note="",
            cmap="RdYlGn", annot=True, fmt=".2f", figsize=None, ax=None, format=None,
            background=None):
    """
    Heatmap générique (corrélation, pivot, confusion matrix…).

    Parameters
    ----------
    matrice         : Array 2D numpy ou liste de listes
    labels_lignes   : Étiquettes des lignes
    labels_colonnes : Étiquettes des colonnes
    annot           : Afficher les valeurs dans les cellules
    fmt             : Format des valeurs (ex: ".2f", ".0f", "d")

    Exemple
    -------
    >>> import numpy as np
    >>> mat = np.corrcoef(np.random.randn(5, 50))
    >>> heatmap(mat, titre="Matrice de corrélation")
    """
    matrice = np.array(matrice)
    n, m = matrice.shape
    ajuster_layout = ax is None
    figsize = _resoudre_figsize(figsize, format)
    fig, ax = _new_fig(figsize or (max(6, m * 0.9), max(5, n * 0.75)), ax=ax, background=background)

    im = ax.imshow(matrice, cmap=cmap, aspect="auto",
                   vmin=matrice.min(), vmax=matrice.max())

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=9)

    if labels_lignes is not None:
        ax.set_yticks(range(n))
        ax.set_yticklabels(labels_lignes, fontsize=10)
    if labels_colonnes is not None:
        ax.set_xticks(range(m))
        ax.set_xticklabels(labels_colonnes, rotation=40, ha="right", fontsize=10)

    if annot:
        thresh = (matrice.max() + matrice.min()) / 2
        for i in range(n):
            for j in range(m):
                val = matrice[i, j]
                color = "white" if val < thresh else "#1A1C2E"
                ax.text(j, i, _fmt_builtin(val, fmt), ha="center", va="center",
                        fontsize=9, color=color, fontweight="bold")

    ax.set_frame_on(False)
    ax.tick_params(length=0)

    if titre:
        ax.set_title(titre, fontsize=15, fontweight="bold",
                     color=_T["texte"], pad=14, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1.02), xycoords="axes fraction",
                    fontsize=10, color=_T["texte_dim"])
    if note:
        fig.text(0.01, -0.03, note, fontsize=8.5, color=_T["texte_dim"],
                 style="italic", transform=ax.transAxes)

    if ajuster_layout:
        fig.tight_layout()
    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑨ dot_plot_comparatif — comparaison multi-dimensions entre deux périodes
# ══════════════════════════════════════════════════════════════════════════════

def dot_plot_comparatif(
    colonnes: dict,
    descriptions: dict = None,
    label_avant="Avant",
    label_apres="Après",
    couleur=None,
    couleur_avant=None,
    couleur_apres=None,
    couleur_connecteur=None,
    titre="",
    sous_titre="",
    note="",
    label_plage=None,
    montrer_plage=False,
    vmin=None,
    vmax=None,
    montrer_fleche=True,
    background=None,
    figsize=None,
    format=None,
):
    """
    Compare N dimensions entre deux périodes sur un axe Y commun — style McKinsey.

    Chaque colonne affiche un point creux (avant) et un point plein (après) reliés
    par un connecteur. Les en-têtes de colonnes sont **intégrés dans le cadre** du
    graphique, séparés des données par une ligne horizontale.

    Parameters
    ----------
    colonnes          : ``{"Nom": (valeur_avant, valeur_apres), ...}``
    descriptions      : ``{"Nom": "texte court"}`` — description optionnelle sous chaque nom.
    label_avant       : Étiquette légende du point creux (défaut ``"Avant"``).
    label_apres       : Étiquette légende du point plein (défaut ``"Après"``).
    couleur           : Alias rétrocompatible → couleur_apres si couleur_apres non défini.
    couleur_avant     : Couleur du cercle creux. ``None`` → couleur de fond (aspect «contour seul»).
    couleur_apres     : Couleur du cercle plein. ``None`` → ``PALETTE[0]``.
    couleur_connecteur: Couleur de la ligne / flèche. ``None`` → ``_T["texte_dim"]``.
    titre             : Titre principal (figure, au-dessus du cadre).
    sous_titre        : Texte léger affiché dans le cadre, coin haut-gauche de la zone en-têtes.
                        Supporte les tokens ``{vmin}`` et ``{vmax}`` qui seront remplacés
                        par les bornes réelles de l'axe Y.
                        Exemple : ``"Score ({vmin} = faible ; {vmax} = élevé)"``
    note              : Note de bas de page (source, remarque…).
    label_plage       : Indicateur **gauche** — chaîne format avec tokens ``{vmin}`` / ``{vmax}``.
                        Affiché à gauche dans la ligne supérieure de la zone en-têtes.
                        Exemple : ``"Score ({vmin}–{vmax})"``
    montrer_plage     : Indicateur **droit** — rectangle visuel montrant la plage [vmin, vmax].
                        Affiché à droite dans la ligne supérieure de la zone en-têtes.
    vmin              : Borne inférieure de l'axe Y (défaut : ``min(0, données)``).
    vmax              : Borne supérieure de l'axe Y (défaut : ``max(données)``).
    montrer_fleche    : Afficher la pointe de flèche sur le connecteur (défaut ``True``).
    background        : Fond de la figure.
                        ``None`` → thème actif · ``"transparent"`` → alpha=0
                        (idéal pour incruster dans PowerPoint) · ``"#0D1B2A"`` → couleur hex.
    figsize, format   : Taille de figure (figsize prioritaire sur format).

    Returns
    -------
    ``(fig, ax)``

    Exemple McKinsey
    ----------------
    >>> dot_plot_comparatif(
    ...     colonnes={
    ...         "News":     (0.08, 0.27),
    ...         "Searches": (0.07, 0.09),
    ...         "Research": (0.05, 0.08),
    ...         "Patents":  (0.13, 0.19),
    ...     },
    ...     descriptions={
    ...         "News":     "Mentions presse liées à la tendance",
    ...         "Searches": "Requêtes moteurs de recherche",
    ...         "Research": "Publications scientifiques",
    ...         "Patents":  "Dépôts de brevets liés",
    ...     },
    ...     label_avant="2020", label_apres="2024",
    ...     label_plage="Score ({vmin} = faible ; {vmax} = élevé)",
    ...     montrer_plage=True,
    ...     background="transparent",
    ...     titre="Tendances numériques — Cybersécurité",
    ... )
    """
    import matplotlib.ticker as _mticker

    descriptions = descriptions or {}
    noms         = list(colonnes.keys())
    n            = len(noms)
    has_desc     = any(nom in descriptions for nom in noms)

    # ── Couleurs ────────────────────────────────────────────────────────────
    c_apres = couleur_apres or couleur or PALETTE[0]
    c_conn  = couleur_connecteur or _T["texte_dim"]

    # Fond effectif
    if background is None:
        bg_color    = _T["bg"]
        transparent = False
    elif background == "transparent":
        bg_color    = _T["bg"]
        transparent = True
    else:
        bg_color    = background
        transparent = False

    # Cercle creux : fond identique au background → effet "anneau"
    c_avant = couleur_avant or (bg_color if not transparent else _T["fond_neutre"])

    # ── Figure ──────────────────────────────────────────────────────────────
    x_extra = 1.6 if montrer_plage else 0.0
    fig_w   = max(8, n * 2.8 + x_extra)
    fig, ax = plt.subplots(figsize=_resoudre_figsize(figsize, format) or (fig_w, 6.5))

    if transparent:
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
    else:
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)

    fig.subplots_adjust(left=0.10, right=0.97, top=0.92, bottom=0.08)

    # ── Plage Y ─────────────────────────────────────────────────────────────
    all_vals = [v for paire in colonnes.values() for v in paire]
    ymin_d, ymax_d = min(all_vals), max(all_vals)
    vmin_eff = vmin if vmin is not None else min(0.0, ymin_d)
    vmax_eff = vmax if vmax is not None else ymax_d

    data_span   = vmax_eff - vmin_eff or 1.0
    data_marge  = data_span * 0.05
    # Zone en-têtes : fraction du data_span (plus haute si descriptions présentes)
    header_h    = data_span * (0.46 if has_desc else 0.28)

    y_sep  = vmax_eff + data_marge   # ligne séparatrice
    y_top  = y_sep + header_h        # sommet des axes

    ax.set_ylim(vmin_eff, y_top)

    # Ticks Y uniquement dans la zone données
    locator = _mticker.MaxNLocator(nbins=5, min_n_ticks=3)
    tick_vals = [t for t in locator.tick_values(vmin_eff, vmax_eff)
                 if vmin_eff - 1e-10 <= t <= vmax_eff + 1e-10]
    ax.set_yticks(tick_vals)
    ax.tick_params(axis="y", labelcolor=_T["texte_dim"], labelsize=9, length=0)

    # Grille horizontale dashed dans la zone données
    ax.yaxis.grid(True, color=_T["grille"], lw=0.5, linestyle="--", zorder=0)
    ax.set_axisbelow(True)

    # Ligne séparatrice données / en-têtes
    ax.axhline(y_sep, color=_T["grille"], lw=0.8, zorder=1)

    # ── Y positions (en-têtes) ──────────────────────────────────────────────
    # Ligne supérieure : label_plage + légende + indicateur de plage
    y_row_top  = y_sep + header_h * 0.82
    # Noms de colonnes
    y_col_nom  = y_sep + header_h * (0.50 if has_desc else 0.48)
    # Descriptions
    y_col_desc = y_sep + header_h * 0.04

    # ── Helper format ───────────────────────────────────────────────────────
    def _fv(v):
        return str(int(v)) if v == int(v) else f"{v:g}"

    # ── Colonnes ────────────────────────────────────────────────────────────
    for i, nom in enumerate(noms):
        avant, apres = colonnes[nom]

        # Séparateur vertical (traverse les deux zones)
        if i > 0:
            ax.axvline(i - 0.5, color=_T["grille"], lw=0.5, zorder=0)

        # Connecteur : ligne droite + tête de flèche séparée (évite les disparitions)
        if avant != apres:
            ax.plot([i, i], [avant, apres], color=c_conn, lw=0.9, zorder=2)
            if montrer_fleche:
                d    = 1 if apres > avant else -1
                tiny = data_span * 0.005
                ax.annotate(
                    "",
                    xy=(i, apres + d * tiny),
                    xytext=(i, apres - d * tiny * 1.5),
                    arrowprops=dict(
                        arrowstyle="->, head_width=0.3, head_length=0.4",
                        color=c_conn, lw=0.9, mutation_scale=8,
                    ),
                    zorder=5,
                )

        # Points
        ax.scatter([i], [avant], s=200, facecolor=c_avant,
                   edgecolor=c_apres, linewidth=2.2, zorder=3)
        ax.scatter([i], [apres], s=200, facecolor=c_apres,
                   edgecolor=c_apres, zorder=4)

        # En-tête nom (gras)
        ax.text(i, y_col_nom, nom, ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=_T["texte"], clip_on=False)

        # En-tête description (optionnelle, plus petite, gris)
        desc = descriptions.get(nom)
        if desc:
            ax.text(i, y_col_desc, textwrap.fill(desc, 18),
                    ha="center", va="bottom", fontsize=8.5,
                    color=_T["texte_dim"], linespacing=1.3, clip_on=False)

    # ── Axe X et bords ──────────────────────────────────────────────────────
    x_right = (n - 0.4 + x_extra) if montrer_plage else (n - 0.4)
    ax.set_xlim(-0.6, x_right)
    ax.xaxis.set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(_T["grille"])
    ax.spines["bottom"].set_color(_T["grille"])

    # ── Légende (ligne supérieure, centré) ──────────────────────────────────
    legende_handles = [
        plt.Line2D([0], [0], marker="o", linestyle="none", markersize=8,
                   markerfacecolor=c_avant, markeredgecolor=c_apres,
                   markeredgewidth=2, label=label_avant),
        plt.Line2D([0], [0], marker="o", linestyle="none", markersize=8,
                   markerfacecolor=c_apres, markeredgecolor=c_apres,
                   label=label_apres),
    ]
    # Centre X de la zone colonnes en fraction axes
    y_span   = y_top - vmin_eff
    y_row_af = (y_row_top - vmin_eff) / y_span
    leg_x_af = 0.42 if not label_plage else 0.55  # décale si label_plage présent
    ax.legend(handles=legende_handles, loc="center",
              bbox_to_anchor=(leg_x_af, y_row_af),
              bbox_transform=ax.transAxes,
              frameon=False, fontsize=9, ncol=2,
              labelcolor=_T["texte"],
              handletextpad=0.4, columnspacing=1.0)

    # ── Indicateur gauche : label_plage / sous_titre ─────────────────────────
    # sous_titre et label_plage peuvent tous deux utiliser {vmin}/{vmax}
    def _rendre(s):
        return s.format(vmin=_fv(vmin_eff), vmax=_fv(vmax_eff)) if s else ""

    texte_gauche = _rendre(label_plage) or _rendre(sous_titre)
    if texte_gauche:
        ax.text(-0.55, y_row_top, texte_gauche, ha="left", va="center",
                fontsize=9.5, fontweight="bold",
                color=_T["texte"], clip_on=False)

    # ── Indicateur droit : rectangle plage ───────────────────────────────────
    if montrer_plage:
        xi0   = n - 0.4 + 0.4    # bord gauche du rectangle
        xi1   = n - 0.4 + 1.3    # bord droit du rectangle
        xi_m  = (xi0 + xi1) / 2
        rh    = header_h * 0.15  # hauteur en unités données

        rect = mpatches.Rectangle(
            (xi0, y_row_top - rh / 2), xi1 - xi0, rh,
            facecolor="none", edgecolor=_T["texte_dim"],
            linewidth=0.9, zorder=5,
        )
        ax.add_patch(rect)

        ax.text(xi0 - 0.07, y_row_top, _fv(vmin_eff),
                ha="right", va="center", fontsize=8, color=_T["texte_dim"])
        ax.text(xi1 + 0.07, y_row_top, _fv(vmax_eff),
                ha="left",  va="center", fontsize=8, color=_T["texte_dim"])
        ax.text(xi_m, y_row_top - rh * 0.9, "Range shown",
                ha="center", va="top", fontsize=7, color=_T["texte_dim"],
                style="italic")

    # ── Titre et note (figure) ────────────────────────────────────────────────
    if titre:
        fig.text(0.01, 0.97, titre, fontsize=14, fontweight="bold",
                 color=_T["texte"])
    if note:
        fig.text(0.01, 0.01, note, fontsize=7.5, color=_T["texte_dim"],
                 style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑩ bulle_4d — nuage de points à 4 variables (X, Y, taille, couleur ordinale)
# ══════════════════════════════════════════════════════════════════════════════

def bulle_4d(x: list, y: list, taille: list, couleur_var: list, labels: list = None,
             xlabel="", ylabel="", label_taille="", label_couleur="",
             niveaux_couleur: list = None, quadrants=False,
             quadrant_x=0.5, quadrant_y=0.5, taille_min=80, taille_max=2000,
             palette_bulles: list = None, titre="", sous_titre="", note="",
             figsize=None, format=None, background=None):
    """
    Nuage de points où chaque bulle encode 4 variables : position X, position Y,
    taille (variable continue) et couleur (variable ordinale 1→N). Permet de
    cartographier des entités sur 4 axes d'analyse en une seule figure.

    Parameters
    ----------
    x, y            : positions des bulles
    taille          : variable continue → taille des bulles
    couleur_var     : variable ordinale entière (ex: 1,2,3,4,5)
    niveaux_couleur : valeurs ordinales possibles (défaut : valeurs triées uniques)
    quadrants       : afficher les lignes de quadrant

    Exemple
    -------
    >>> bulle_4d(
    ...     x=[0.9, 0.15, 0.1], y=[0.9, 0.55, 0.4], taille=[200, 10, 30],
    ...     couleur_var=[4, 3, 3], labels=["IA", "Semi-conducteurs", "Connectivité"],
    ...     label_couleur="Niveau d'adoption", quadrants=True,
    ... )
    """
    figsize = _resoudre_figsize(figsize, format)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    taille = np.asarray(taille, dtype=float)
    n = len(x)

    niveaux_couleur = niveaux_couleur or sorted(set(couleur_var))
    ncol = len(niveaux_couleur)
    if palette_bulles is None:
        # Interpole la PALETTE active pour couvrir tous les niveaux
        src = PALETTE * ((ncol // len(PALETTE)) + 1)
        palette_bulles = src[:ncol]
    couleur_par_niveau = dict(zip(niveaux_couleur, palette_bulles))
    point_colors = [couleur_par_niveau.get(v, _T["serie_dim"]) for v in couleur_var]

    trange = (taille.max() - taille.min()) or 1.0
    tailles_norm = taille_min + (taille - taille.min()) / trange * (taille_max - taille_min)

    fig, ax = _new_fig(figsize or (9, 7), background=background)

    if quadrants:
        ax.axhline(quadrant_y, color=_T["grille"], lw=1, ls="--", zorder=1)
        ax.axvline(quadrant_x, color=_T["grille"], lw=1, ls="--", zorder=1)

    ax.scatter(x, y, s=tailles_norm, color=point_colors, alpha=0.85,
              edgecolor=_T["fond_neutre"], linewidth=1.2, zorder=3)

    if labels is not None:
        ordre = np.argsort(y)
        yrange = (y.max() - y.min()) or 1.0
        dernier_y = None
        decalage = 0
        for idx in ordre:
            if dernier_y is not None and abs(y[idx] - dernier_y) < yrange * 0.03:
                decalage += 10
            else:
                decalage = 0
            dernier_y = y[idx]
            rayon = np.sqrt(tailles_norm[idx] / np.pi)
            ax.annotate(labels[idx], xy=(x[idx], y[idx]),
                        xytext=(rayon + 5, decalage), textcoords="offset points",
                        fontsize=9, color=_T["texte"], va="center")

    xmarge = (x.max() - x.min()) * 0.1 or 0.1
    ymarge = (y.max() - y.min()) * 0.1 or 0.1
    ax.set_xlim(x.min() - xmarge, x.max() + xmarge)
    ax.set_ylim(y.min() - ymarge, y.max() + ymarge)

    ax.set_xlabel((xlabel + "  →") if xlabel else "", color=_T["texte_dim"], fontsize=10)
    ax.set_ylabel((ylabel + "  ↑") if ylabel else "", color=_T["texte_dim"], fontsize=10)
    ax.grid(axis="both", color=_T["grille"], lw=0.6, ls="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=0)

    fig.subplots_adjust(right=0.76)

    handles_couleur = [plt.scatter([], [], s=120, color=couleur_par_niveau[niv],
                                    edgecolor=_T["fond_neutre"]) for niv in niveaux_couleur]
    leg1 = ax.legend(handles_couleur, [str(niv) for niv in niveaux_couleur],
                     title=label_couleur, loc="upper left", bbox_to_anchor=(1.02, 1.0),
                     frameon=False, fontsize=8.5, title_fontsize=9)
    ax.add_artist(leg1)

    valeurs_ref = sorted(set(np.round(np.linspace(taille.min(), taille.max(), 4)).astype(int).tolist()))
    handles_taille = [plt.scatter([], [], s=taille_min + (v - taille.min()) / trange * (taille_max - taille_min),
                                   color=_T["serie_dim"], alpha=0.5, edgecolor=_T["texte_dim"])
                      for v in valeurs_ref]
    ax.legend(handles_taille, [str(v) for v in valeurs_ref],
             title=label_taille, loc="lower left", bbox_to_anchor=(1.02, 0.0),
             frameon=False, fontsize=8.5, title_fontsize=9, labelspacing=1.4)

    if titre:
        ax.set_title(titre, fontsize=14, fontweight="bold", color=_T["texte"],
                     pad=14, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 26), textcoords="offset points",
                    fontsize=10, color=_T["texte_dim"], annotation_clip=False)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color=_T["texte_dim"], style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑪ unit_chart — carrés de proportion / ratio (alternative honnête au camembert)
# ══════════════════════════════════════════════════════════════════════════════

def unit_chart(categories: list, valeurs: list, mode="proportion",
                reference: list = None, valeur_max: float = None, couleur=None,
                fmt="{:.0f}", fmt_ratio="{:.1f}×", taille_carre=1.0,
                titre="", sous_titre="", note="", figsize=None, format=None):
    """
    Chaque item est un carré de référence rempli proportionnellement à sa valeur.
    Mode "proportion" : un seul rectangle rempli jusqu'au %. Mode "ratio" : deux
    carrés imbriqués (demande = grand, offre = petit) avec ratio annoté.
    Plus honnête visuellement qu'un camembert pour comparer de nombreuses
    catégories.

    Parameters
    ----------
    valeurs    : proportions (mode "proportion") ou ratios/offre (mode "ratio")
    reference  : valeurs de demande pour calculer le ratio (mode "ratio" seulement,
                 optionnel — si absent, `valeurs` est déjà interprété comme le ratio)
    valeur_max : normalisation du mode "proportion" (défaut : max(valeurs))

    Exemple
    -------
    >>> unit_chart(
    ...     categories=["Python", "C++", "GPU"], valeurs=[37, 21, 30],
    ...     mode="proportion", titre="Talent requis",
    ... )
    >>> unit_chart(
    ...     categories=["Python", "C++"], valeurs=[0.5, 2.7],
    ...     mode="ratio", titre="Disponibilité du talent",
    ... )
    """
    couleur = couleur or PALETTE[0]
    figsize = _resoudre_figsize(figsize, format)
    n = len(categories)
    fig, ax = plt.subplots(figsize=figsize or (n * 1.7, 4.5))

    espacement = taille_carre * 1.7
    positions = [i * espacement for i in range(n)]
    sommets = []

    if mode == "proportion":
        vmax = valeur_max or max(valeurs)
        for x0, cat, val in zip(positions, categories, valeurs):
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, taille_carre,
                                            edgecolor=_T["serie_dim"], facecolor="none", lw=1.5, zorder=2))
            h = (val / vmax) * taille_carre if vmax else 0
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, h,
                                            facecolor=couleur, edgecolor="none",
                                            alpha=0.9, zorder=3))
            couleur_texte = "white" if h > taille_carre * 0.15 else couleur
            ax.text(x0 + taille_carre * 0.08, taille_carre * 0.06, fmt.format(val),
                    fontsize=11, fontweight="bold", color=couleur_texte,
                    ha="left", va="bottom", zorder=4)
            ax.text(x0 + taille_carre / 2, -taille_carre * 0.12, cat,
                    fontsize=9.5, color=_T["texte_dim"], ha="center", va="top")
            sommets.append(taille_carre)
    else:  # mode == "ratio"
        if reference is not None:
            ratios = [v / r if r else 0 for v, r in zip(valeurs, reference)]
        else:
            ratios = valeurs
        for x0, cat, ratio in zip(positions, categories, ratios):
            cx, cy = x0 + taille_carre / 2, taille_carre / 2
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, taille_carre,
                                            edgecolor=_T["serie_dim"], facecolor="none", lw=1.5, zorder=2))
            cote_petit = np.sqrt(max(ratio, 0)) * taille_carre
            px0, py0 = cx - cote_petit / 2, cy - cote_petit / 2
            ax.add_patch(mpatches.Rectangle((px0, py0), cote_petit, cote_petit,
                                            facecolor=couleur, edgecolor=couleur,
                                            alpha=0.85, lw=0, zorder=3))
            sommet = max(taille_carre, py0 + cote_petit)
            ax.text(cx, sommet + taille_carre * 0.1, fmt_ratio.format(ratio),
                    fontsize=11, fontweight="bold", color=couleur,
                    ha="center", va="bottom", zorder=4)
            ax.text(cx, -taille_carre * 0.12, cat,
                    fontsize=9.5, color=_T["texte_dim"], ha="center", va="top")
            sommets.append(sommet + taille_carre * 0.32)

    ax.set_xlim(-taille_carre * 0.3, positions[-1] + taille_carre * 1.3)
    ax.set_ylim(-taille_carre * 0.4, max(sommets) * 1.1)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    if titre:
        ax.set_title(titre, fontsize=14, fontweight="bold", color=_T["texte"],
                     pad=18, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 8), textcoords="offset points",
                    fontsize=10, color=_T["texte_dim"], annotation_clip=False)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color=_T["texte_dim"], style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑫ box_plot — distribution par catégorie (boîtes à moustaches)
# ══════════════════════════════════════════════════════════════════════════════

def box_plot(data: list, categories: list = None, titre="", sous_titre="",
             xlabel="", ylabel="", note="", horizontal=False, couleur=None,
             afficher_points=False, notch=False, figsize=None, ax=None, format=None,
             background=None):
    """
    Boîtes à moustaches : compare la distribution complète (médiane, quartiles,
    valeurs extrêmes) de plusieurs groupes — plus honnête qu'une moyenne seule.

    Quand l'utiliser
    ----------------
    Comparer la dispersion de 2 à ~10 groupes (salaires par département,
    temps de réponse par version, notes par classe…).

    Ne pas utiliser
    ----------------
    Pour une seule série sans groupe de comparaison, ou pour des séries
    temporelles (utilisez ligne() ou aire()).

    Parameters
    ----------
    data            : liste de listes — une liste de valeurs par groupe
    categories      : étiquettes des groupes (défaut : "Groupe 1", "Groupe 2"…)
    horizontal      : True → boîtes horizontales
    afficher_points : superposer les points individuels (jitter)
    notch           : encoche autour de la médiane (intervalle de confiance)

    Exemple
    -------
    >>> box_plot(
    ...     data=[[12, 15, 14, 18, 22], [20, 25, 23, 30, 19]],
    ...     categories=["Équipe A", "Équipe B"],
    ...     titre="Distribution des délais de livraison",
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    couleur = couleur or PALETTE[0]
    n = len(data)
    categories = categories or [f"Groupe {i + 1}" for i in range(n)]

    bp = ax.boxplot(
        data, vert=not horizontal, patch_artist=True, notch=notch,
        labels=categories, widths=0.5,
        medianprops=dict(color=_T["texte"], linewidth=2),
        whiskerprops=dict(color=_T["serie_dim"], linewidth=1.2),
        capprops=dict(color=_T["serie_dim"], linewidth=1.2),
        flierprops=dict(marker="o", markerfacecolor="none",
                        markeredgecolor=_T["serie_dim"], markersize=5),
    )
    for box in bp["boxes"]:
        box.set_facecolor(couleur)
        box.set_alpha(0.6)
        box.set_edgecolor(couleur)

    if afficher_points:
        rng = np.random.default_rng(0)
        for i, vals in enumerate(data, start=1):
            jitter = rng.uniform(-0.15, 0.15, len(vals))
            positions = np.full(len(vals), i, dtype=float) + jitter
            if horizontal:
                ax.scatter(vals, positions, color=couleur, alpha=0.4, s=18, zorder=3)
            else:
                ax.scatter(positions, vals, color=couleur, alpha=0.4, s=18, zorder=3)

    if horizontal:
        ax.xaxis.grid(True, alpha=0.4)
        ax.yaxis.grid(False)
    else:
        ax.yaxis.grid(True, alpha=0.4)
        ax.xaxis.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑬ violin — distribution détaillée par catégorie (forme de densité)
# ══════════════════════════════════════════════════════════════════════════════

def violin(data: list, categories: list = None, titre="", sous_titre="",
           xlabel="", ylabel="", note="", afficher_boxplot=True, couleur=None,
           figsize=None, ax=None, format=None, background=None):
    """
    Violons : montre la forme complète de la distribution (densité) par groupe —
    révèle bimodalité, asymétrie, ce qu'une boîte à moustaches seule ne montre pas.

    Quand l'utiliser
    ----------------
    Avec suffisamment de points par groupe (>~20) pour que la densité soit
    informative, et quand la *forme* de la distribution compte (pas seulement
    sa médiane).

    Ne pas utiliser
    ----------------
    Avec peu de points (<20) — la densité estimée devient trompeuse ; préférez
    alors box_plot() ou un nuage de points brut.

    Parameters
    ----------
    data             : liste de listes — une liste de valeurs par groupe
    categories       : étiquettes des groupes
    afficher_boxplot : superposer une mini-boîte à moustaches au centre

    Exemple
    -------
    >>> violin(
    ...     data=[np.random.normal(170, 8, 200), np.random.normal(178, 10, 200)],
    ...     categories=["Femmes", "Hommes"],
    ...     titre="Distribution des tailles",
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    n = len(data)
    categories = categories or [f"Groupe {i + 1}" for i in range(n)]
    positions = list(range(1, n + 1))

    vp = ax.violinplot(data, positions=positions, showmedians=True, showextrema=False)
    for i, body in enumerate(vp["bodies"]):
        color = couleur or PALETTE[i % len(PALETTE)]
        body.set_facecolor(color)
        body.set_edgecolor(color)
        body.set_alpha(0.75)
    vp["cmedians"].set_color(_T["texte"])
    vp["cmedians"].set_linewidth(1.5)

    if afficher_boxplot:
        bp = ax.boxplot(data, positions=positions, widths=0.08, patch_artist=True,
                        showfliers=False, medianprops=dict(color=PALETTE[1], linewidth=2))
        for box in bp["boxes"]:
            box.set_facecolor(_T["fond_neutre"])
            box.set_edgecolor(_T["texte_dim"])

    ax.set_xticks(positions)
    ax.set_xticklabels(categories)
    ax.yaxis.grid(True, alpha=0.4)
    ax.xaxis.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑭ waterfall — décomposition d'une variation en contributions successives
# ══════════════════════════════════════════════════════════════════════════════

def waterfall(categories: list, valeurs: list, total_debut: float = None,
              total_fin: float = None, label_debut="Début", label_fin="Total",
              titre="", sous_titre="", ylabel="", note="", couleur_pos=None,
              couleur_neg=None, couleur_total=None, connecteurs=True,
              figsize=None, ax=None, format=None, background=None):
    """
    Graphique en cascade : montre comment des contributions positives et
    négatives successives transforment une valeur de départ en valeur finale.

    Quand l'utiliser
    ----------------
    Décomposer une variation de CA, d'effectif ou de marge en facteurs
    explicatifs (ex : CA 2023 → +Nouveaux clients −Churn +Upsell → CA 2024).

    Ne pas utiliser
    ----------------
    Si l'ordre des contributions n'a pas de sens logique, ou pour comparer
    des catégories indépendantes sans relation cumulative (utilisez barres()).

    Parameters
    ----------
    categories   : noms des contributions intermédiaires
    valeurs      : variations signées correspondantes (+/-)
    total_debut  : valeur de départ (affichée comme première barre pleine)
    total_fin    : valeur finale (si None, calculée comme la somme cumulée)
    connecteurs  : afficher des pointillés reliant le sommet d'une barre au
                   départ de la suivante

    Exemple
    -------
    >>> waterfall(
    ...     categories=["Nouveaux clients", "Churn", "Upsell"],
    ...     valeurs=[80, -45, 30],
    ...     total_debut=500, label_debut="CA 2023",
    ...     total_fin=565, label_fin="CA 2024",
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    couleur_pos = couleur_pos or PALETTE[6]
    couleur_neg = couleur_neg or PALETTE[1]
    couleur_total = couleur_total or "#6B6F85"

    labels, hauteurs, bottoms, couleurs_barres, est_total, vals_affiche = [], [], [], [], [], []
    cumul = 0.0

    if total_debut is not None:
        labels.append(label_debut)
        hauteurs.append(total_debut)
        bottoms.append(0)
        couleurs_barres.append(couleur_total)
        est_total.append(True)
        vals_affiche.append(total_debut)
        cumul = total_debut

    for cat, val in zip(categories, valeurs):
        labels.append(cat)
        vals_affiche.append(val)
        est_total.append(False)
        if val >= 0:
            bottoms.append(cumul)
            hauteurs.append(val)
            couleurs_barres.append(couleur_pos)
        else:
            bottoms.append(cumul + val)
            hauteurs.append(-val)
            couleurs_barres.append(couleur_neg)
        cumul += val

    if total_fin is None:
        total_fin = cumul
    labels.append(label_fin)
    hauteurs.append(total_fin)
    bottoms.append(0)
    couleurs_barres.append(couleur_total)
    est_total.append(True)
    vals_affiche.append(total_fin)

    x = np.arange(len(labels))
    ax.bar(x, hauteurs, bottom=bottoms, color=couleurs_barres, width=0.6, zorder=3)

    if connecteurs:
        for i in range(len(labels) - 1):
            y_connect = bottoms[i] + hauteurs[i]
            ax.plot([x[i] + 0.3, x[i + 1] - 0.3], [y_connect, y_connect],
                    color=_T["grille"], linewidth=1, linestyle="--", zorder=1)

    plage = max(b + h for b, h in zip(bottoms, hauteurs)) * 0.02 or 1
    for xi, b, h, tot, val in zip(x, bottoms, hauteurs, est_total, vals_affiche):
        signe = "+" if (val > 0 and not tot) else ""
        ax.text(xi, b + h + plage, f"{signe}{val:,.0f}", ha="center", va="bottom",
                fontsize=9.5, fontweight="bold", color=_T["texte"])

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20 if len(labels) > 5 else 0, ha="right" if len(labels) > 5 else "center")
    ax.yaxis.grid(True, alpha=0.4)
    ax.xaxis.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return _finalize(ax, titre, sous_titre, "", ylabel, note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑮ lollipop — classement de catégories (alternative aérée aux barres)
# ══════════════════════════════════════════════════════════════════════════════

def lollipop(categories: list, valeurs: list, titre="", sous_titre="",
             xlabel="", note="", couleur=None, fn_couleur=None, trier=True,
             ligne_ref: float = None, label_ref="", taille_point=8,
             vmin=None, vmax=None, figsize=None, ax=None, format=None, background=None):
    """
    Tige + point : classement de catégories, plus léger visuellement qu'une
    barre pleine quand on a beaucoup de catégories ou peu de place.

    Quand l'utiliser
    ----------------
    Classer 5 à ~30 catégories par valeur, avec ou sans seuil de référence
    (objectif, moyenne, médiane sectorielle…).

    Ne pas utiliser
    ----------------
    Pour des séries temporelles, ou quand l'ordre des catégories est imposé
    et ne doit pas être trié (utilisez barres() avec trier=False implicite).

    Parameters
    ----------
    trier      : trier les catégories par valeur décroissante (défaut True)
    ligne_ref  : valeur de référence verticale (objectif, moyenne…)
    label_ref  : étiquette affichée près de la ligne de référence

    Exemple
    -------
    >>> lollipop(
    ...     categories=["Nord", "Sud", "Est", "Ouest", "Centre"],
    ...     valeurs=[82, 65, 74, 58, 91],
    ...     ligne_ref=70, label_ref="Objectif",
    ...     titre="Taux de satisfaction par région",
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    couleur = couleur or PALETTE[0]

    paires = list(zip(categories, valeurs))
    if trier:
        paires.sort(key=lambda p: p[1], reverse=True)
    categories_t, valeurs_t = (list(t) for t in zip(*paires)) if paires else ([], [])
    y_pos = np.arange(len(categories_t))

    ax.hlines(y_pos, 0, valeurs_t, color=_T["grille"], linewidth=1.6, zorder=2)
    if fn_couleur is not None:
        pts_couleurs = [fn_couleur(cat, val) for cat, val in zip(categories_t, valeurs_t)]
        ax.scatter(valeurs_t, y_pos, c=pts_couleurs, s=taille_point ** 2, zorder=3)
    else:
        ax.plot(valeurs_t, y_pos, "o", color=couleur, markersize=taille_point, zorder=3)

    marge = (max(valeurs_t) * 0.03) if valeurs_t else 1
    for yi, val in zip(y_pos, valeurs_t):
        ax.text(val + marge, yi, f"{val:,.0f}", va="center", ha="left",
                fontsize=9.5, fontweight="bold", color=_T["texte"])

    if ligne_ref is not None:
        ax.axvline(ligne_ref, color=_T["texte_dim"], linewidth=1.2, linestyle="--", zorder=1)
        if label_ref:
            ax.text(ligne_ref, -0.6, label_ref, fontsize=9, color=_T["texte_dim"],
                    ha="center", va="top")

    if vmin is not None or vmax is not None:
        ax.set_xlim(vmin, vmax)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories_t)
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(length=0)

    return _finalize(ax, titre, sous_titre, xlabel, "", note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑯ slope — comparaison avant/après par catégorie (pentes connectées)
# ══════════════════════════════════════════════════════════════════════════════

def slope(categories: list, valeurs_gauche: list, valeurs_droite: list,
          label_gauche="Avant", label_droite="Après", titre="", sous_titre="",
          note="", couleur_hausse=None, couleur_baisse=None, couleur_stable=None,
          afficher_valeurs=True, focus: list = None, figsize=None, ax=None, format=None,
          background=None):
    """
    Deux colonnes de points reliés par des segments : montre, catégorie par
    catégorie, qui a progressé, régressé ou stagné entre deux périodes.

    Quand l'utiliser
    ----------------
    Comparer ~3 à 15 catégories entre exactement deux points (avant/après,
    deux régions, deux candidats…). Utilisez `focus` pour mettre en avant
    1 ou 2 catégories précises sans perdre le contexte des autres.

    Ne pas utiliser
    ----------------
    Pour plus de deux périodes (utilisez ligne()), ou pour énormément de
    catégories (les étiquettes se chevauchent au-delà de ~15).

    Parameters
    ----------
    valeurs_gauche, valeurs_droite : valeurs aux deux périodes, alignées sur categories
    focus      : liste de catégories à mettre en évidence (les autres grisées)
    afficher_valeurs : afficher la valeur numérique à côté de chaque étiquette

    Exemple
    -------
    >>> slope(
    ...     categories=["Produit A", "Produit B", "Produit C"],
    ...     valeurs_gauche=[120, 80, 95],
    ...     valeurs_droite=[140, 60, 95],
    ...     label_gauche="2023", label_droite="2024",
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format, background=background)
    couleur_hausse = couleur_hausse or PALETTE[6]
    couleur_baisse = couleur_baisse or PALETTE[1]
    couleur_stable = couleur_stable or "#A8ABBC"
    n = len(categories)

    for i in range(n):
        vg, vd = valeurs_gauche[i], valeurs_droite[i]
        if focus is not None:
            if categories[i] in focus:
                couleur, alpha, lw, z = PALETTE[0], 1.0, 2.4, 4
            else:
                couleur, alpha, lw, z = "#A8ABBC", 0.3, 1.4, 2
        else:
            if vd > vg:
                couleur = couleur_hausse
            elif vd < vg:
                couleur = couleur_baisse
            else:
                couleur = couleur_stable
            alpha, lw, z = 0.9, 1.8, 3

        ax.plot([0, 1], [vg, vd], color=couleur, alpha=alpha, linewidth=lw, zorder=z,
                marker="o", markersize=6, markerfacecolor=couleur, markeredgecolor=_T["fond_neutre"])

    toutes_valeurs = list(valeurs_gauche) + list(valeurs_droite)
    plage = (max(toutes_valeurs) - min(toutes_valeurs)) or 1

    def _placer_etiquettes(cote_valeurs, x_pos, ha):
        ordre = sorted(range(n), key=lambda i: cote_valeurs[i])
        decales = list(cote_valeurs)
        for k in range(1, len(ordre)):
            i_prev, i_cur = ordre[k - 1], ordre[k]
            if decales[i_cur] - decales[i_prev] < plage * 0.05:
                decales[i_cur] = decales[i_prev] + plage * 0.05
        for i in range(n):
            texte = str(categories[i])
            if afficher_valeurs:
                val_str = f"{cote_valeurs[i]:,.0f}"
                texte = f"{texte}  ({val_str})" if ha == "left" else f"({val_str})  {texte}"
            ax.text(x_pos, decales[i], texte, ha=ha, va="center", fontsize=9.5,
                    color=_T["texte"])

    _placer_etiquettes(valeurs_gauche, -0.05, "right")
    _placer_etiquettes(valeurs_droite, 1.05, "left")

    ax.set_xlim(-0.7, 1.7)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([label_gauche, label_droite], fontsize=11, fontweight="bold")
    ax.xaxis.set_tick_params(length=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.grid(axis="y", alpha=0.4)
    ax.grid(axis="x", visible=False)

    return _finalize(ax, titre, sous_titre, "", "", note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ⑰ facet — petits multiples (un graphique par sous-groupe)
# ══════════════════════════════════════════════════════════════════════════════

def facet(data, x: str = None, y: str = None, par: str = None,
          type_graphique="ligne", ncols=3, meme_echelle=True, titre="",
          sous_titre="", note="", partager_legende=True, figsize=None, ax=None,
          format=None, **kwargs):
    """
    Petits multiples : répète le même graphique pour chaque valeur unique de
    `par`, sur une grille, pour comparer des sous-groupes côte à côte.

    Quand l'utiliser
    ----------------
    Comparer une même mesure entre plusieurs régions/produits/segments
    (3 à ~12 sous-groupes) sans surcharger un seul graphique de séries.

    Ne pas utiliser
    ----------------
    Pour plus d'une douzaine de sous-groupes (la grille devient illisible),
    ou quand une superposition directe (ligne() multi-séries) suffit.

    Parameters
    ----------
    data            : DataFrame pandas/polars, ou dict {groupe: {"x":…, "y":…}}
    x, y            : noms des colonnes (si DataFrame)
    par             : colonne de regroupement (une facette par valeur unique)
    type_graphique  : "ligne" | "barres" | "histogramme" | "nuage"
    ncols           : nombre de colonnes dans la grille
    meme_echelle    : True → même axe Y pour toutes les facettes (comparaison honnête)
    **kwargs        : transmis à la fonction de graphique sous-jacente

    Returns
    -------
    (fig, axes) — axes est un array numpy d'Axes (un par groupe)

    Exemple
    -------
    >>> facet(df, x="Mois", y="Ventes", par="Region", type_graphique="barres")
    """
    figsize = _resoudre_figsize(figsize, format)
    _fn_map = {"ligne": ligne, "barres": barres, "histogramme": histogramme, "nuage": nuage}
    fn = _fn_map.get(type_graphique)
    if fn is None:
        raise ValueError(
            f"type_graphique inconnu : '{type_graphique}'. "
            f"Choix possibles : {list(_fn_map)}"
        )

    est_df = hasattr(data, "columns")
    if est_df:
        df = data.to_pandas() if hasattr(data, "to_pandas") else data
        groupes = list(dict.fromkeys(df[par]))
    else:
        df = None
        groupes = list(data.keys())

    n = len(groupes)
    nrows = int(np.ceil(n / ncols))
    fig = plt.figure(figsize=figsize or (ncols * 4.5, nrows * 3.6))
    gs = fig.add_gridspec(nrows, ncols, hspace=0.55, wspace=0.3)

    axes = []
    for idx in range(nrows * ncols):
        row, col = divmod(idx, ncols)
        ax_i = fig.add_subplot(gs[row, col])
        axes.append(ax_i)
        if idx >= n:
            ax_i.set_visible(False)
            continue

        groupe = groupes[idx]
        if est_df:
            sous_df = df[df[par] == groupe]
            x_vals = list(sous_df[x])
            y_vals = list(sous_df[y])
        else:
            sous = data[groupe]
            x_vals = sous.get(x or "x")
            y_vals = sous.get(y or "valeurs", sous.get("y"))

        if type_graphique == "ligne":
            fn(x=x_vals, y_series={str(y or "valeur"): y_vals}, ax=ax_i, **kwargs)
        elif type_graphique == "barres":
            fn(categories=x_vals, valeurs=y_vals, ax=ax_i, **kwargs)
        elif type_graphique == "nuage":
            fn(x=x_vals, y=y_vals, ax=ax_i, **kwargs)
        elif type_graphique == "histogramme":
            fn(data=y_vals, ax=ax_i, **kwargs)

        ax_i.set_title(str(groupe), fontsize=10, fontweight="bold", color=_T["texte"])
        if col != 0:
            ax_i.set_ylabel("")
        if not partager_legende:
            leg = ax_i.get_legend()
            if leg:
                leg.remove()

    if meme_echelle and n:
        ymins = [a.get_ylim()[0] for a in axes[:n]]
        ymaxs = [a.get_ylim()[1] for a in axes[:n]]
        for a in axes[:n]:
            a.set_ylim(min(ymins), max(ymaxs))

    if titre:
        fig.suptitle(titre, fontsize=15, fontweight="bold", color=_T["texte"], y=1.02)
    if sous_titre:
        fig.text(0.01, 0.965, sous_titre, fontsize=10, color=_T["texte_dim"])
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color=_T["texte_dim"], style="italic")

    fig.tight_layout()
    return fig, np.array(axes[:n])


# ══════════════════════════════════════════════════════════════════════════════
# ⑱ Dashboard multi-graphiques
# ══════════════════════════════════════════════════════════════════════════════

def dashboard(configs: list, titre_global="", ncols=2, figsize=None, format=None):
    """
    Génère une grille de graphiques dans une seule figure.

    Parameters
    ----------
    configs : liste de dicts, chacun avec :
              - "type" : "ligne" | "barres" | "aire" | "nuage" | "histogramme"
              - les mêmes kwargs que la fonction correspondante
              (sauf figsize, géré ici)
    ncols   : nombre de colonnes dans la grille

    Exemple
    -------
    >>> dashboard([
    ...     {"type": "barres",
    ...      "categories": ["Jan","Fév","Mar"],
    ...      "valeurs": [30, 45, 38],
    ...      "titre": "Ventes"},
    ...     {"type": "ligne",
    ...      "x": [1,2,3],
    ...      "y_series": {"KPI": [10,15,12]},
    ...      "titre": "KPI"},
    ... ], titre_global="Tableau de bord Q1")
    """
    figsize = _resoudre_figsize(figsize, format)
    n = len(configs)
    nrows = (n + ncols - 1) // ncols
    fig = plt.figure(figsize=figsize or (ncols * 6, nrows * 4.2))
    gs = fig.add_gridspec(nrows, ncols, hspace=0.5, wspace=0.3)

    _fn_map = {
        "ligne": ligne,
        "barres": barres,
        "aire": aire,
        "nuage": nuage,
        "histogramme": histogramme,
        "barres_groupees": barres_groupees,
        "camembert": camembert,
        "heatmap": heatmap,
    }

    axes = []
    for idx in range(nrows * ncols):
        row, col = divmod(idx, ncols)
        ax = fig.add_subplot(gs[row, col])
        axes.append(ax)
        if idx >= n:
            ax.set_visible(False)
            continue
        cfg = dict(configs[idx])  # copie pour ne pas muter l'input
        fn = _fn_map.get(cfg.pop("type"))
        if fn is None:
            ax.set_visible(False)
            continue
        cfg.pop("figsize", None)  # géré par dashboard()
        fn(ax=ax, **cfg)

    if titre_global:
        fig.suptitle(titre_global, fontsize=18, fontweight="bold",
                     color=_T["texte"], y=1.02)
    return fig, np.array(axes[:n])


# ══════════════════════════════════════════════════════════════════════════════
# Layout rapport / slide
# ══════════════════════════════════════════════════════════════════════════════

def _resoudre_style_kpi(style_kpi) -> dict:
    """Convertit style_kpi= (preset str ou dict brut) en dict de flags booléens."""
    if style_kpi is None:
        return dict(_STYLE_KPI_PRESETS["accent"])
    if isinstance(style_kpi, str):
        if style_kpi not in _STYLE_KPI_PRESETS:
            raise ValueError(
                f"style_kpi inconnu : {style_kpi!r}. "
                f"Valides : {list(_STYLE_KPI_PRESETS)} — ou passez un dict."
            )
        return dict(_STYLE_KPI_PRESETS[style_kpi])
    if isinstance(style_kpi, dict):
        result = dict(_STYLE_KPI_PRESETS["accent"])
        result.update(style_kpi)
        return result
    return dict(_STYLE_KPI_PRESETS["accent"])


def _dessiner_kpi(ax, kpi: dict, style: dict) -> None:
    """
    Dessine une tuile KPI dans l'axe fourni.

    Clés reconnues dans *kpi*
    -------------------------
    label   : libellé de la métrique (affiché en majuscules)
    valeur  : valeur principale déjà formatée (ex: ``"1,24 M"`` ou ``"23 %"``)
    delta   : variation (ex: ``"+12 %"``, ``"−2 pts"``) — optionnel
    positif : ``True`` → delta vert, ``False`` → delta rouge  (défaut ``True``)
    icone   : caractère ou emoji placé avant la valeur (optionnel)
    couleur : couleur d'accent hex — barre ou teinte de fond (défaut PALETTE[0])

    Clés reconnues dans *style*
    ---------------------------
    border     : bool — bordure fine autour de la tuile
    accent_bar : bool — barre colorée verticale sur le bord gauche
    bg_fill    : bool — fond légèrement teinté avec la couleur d'accent
    """
    couleur_accent = kpi.get("couleur", PALETTE[0])
    positif        = kpi.get("positif", True)
    couleur_delta  = "#2DC653" if positif else "#E63946"

    # ── Fond ──────────────────────────────────────────────────────────────
    if style.get("bg_fill"):
        h = couleur_accent.lstrip("#")
        r = int(h[0:2], 16) / 255
        g = int(h[2:4], 16) / 255
        b = int(h[4:6], 16) / 255
        ax.set_facecolor((r, g, b, 0.10))
    else:
        ax.set_facecolor(_T["bg"])

    # ── Bordure ────────────────────────────────────────────────────────────
    for sp in ax.spines.values():
        sp.set_visible(bool(style.get("border")))
        if style.get("border"):
            sp.set_linewidth(0.8)
            sp.set_edgecolor(_T["grille"])

    ax.set_xticks([])
    ax.set_yticks([])

    # ── Barre d'accent verticale (côté gauche) ─────────────────────────────
    x_text = 0.5
    if style.get("accent_bar"):
        bar = mpatches.Rectangle(
            (0.035, 0.10), 0.055, 0.80,
            transform=ax.transAxes, clip_on=False,
            facecolor=couleur_accent, edgecolor="none", zorder=5,
        )
        ax.add_patch(bar)
        x_text = 0.56   # centre de l'espace restant (0.09 → 1.0)

    # ── Textes ─────────────────────────────────────────────────────────────
    label      = str(kpi.get("label",  ""))
    valeur     = str(kpi.get("valeur", "—"))
    delta      = str(kpi.get("delta",  ""))
    icone      = str(kpi.get("icone",  ""))
    txt_valeur = f"{icone} {valeur}".strip() if icone else valeur

    if label:
        ax.text(x_text, 0.82, label.upper(), transform=ax.transAxes,
                fontsize=8, color=_T["texte_dim"], ha="center", va="center",
                fontweight="bold")

    ax.text(x_text, 0.50, txt_valeur, transform=ax.transAxes,
            fontsize=22, color=_T["texte"], ha="center", va="center",
            fontweight="bold")

    if delta:
        signe = "▲" if positif else "▼"
        ax.text(x_text, 0.16, f"{signe} {delta}", transform=ax.transAxes,
                fontsize=9.5, color=couleur_delta, ha="center", va="center",
                fontweight="bold")


def layout_rapport(titre="", sous_titre="", note="", kpis=None,
                   n_graphiques=1, figsize=None, format="slide",
                   style_kpi="accent"):
    """
    Gabarit slide/rapport prêt à l'emploi : titre, tuiles KPI et zone(s) graphique.

    Le layout est organisé en deux rangées sur une grille de 12 colonnes :

    * **Rangée 0** (≈ 25 % de hauteur) — titre à gauche + tuiles KPI à droite.
    * **Rangée 1** (≈ 75 % de hauteur) — un ou plusieurs axes graphiques.

    Parameters
    ----------
    titre        : Titre principal de la page.
    sous_titre   : Ligne descriptive sous le titre.
    note         : Note de bas de page (source, date…).
    kpis         : Liste de dicts décrivant les tuiles métriques.
                   Chaque dict peut contenir :
                   ``label``, ``valeur``, ``delta``, ``positif``, ``icone``.
    n_graphiques : Nombre de zones graphique (1, 2 ou 3).
    figsize      : Taille de figure explicite — prioritaire sur *format*.
    format       : Preset de taille (``"slide"``, ``"a4"``, ``"large"``…).
    style_kpi    : Style des tuiles KPI. Preset str ou dict de flags bruts.

                   Presets disponibles :

                   * ``"accent"``  (défaut) — barre colorée à gauche, fond neutre
                   * ``"filled"``  — fond légèrement teinté avec la couleur d'accent
                   * ``"simple"``  — bordure fine, pas de décoration
                   * ``"minimal"`` — texte seul, aucune décoration

                   Dict brut (toutes les clés sont optionnelles) ::

                       style_kpi={"border": True, "accent_bar": False, "bg_fill": True}

                   La couleur d'accent provient de ``kpi["couleur"]`` (par défaut PALETTE[0]).

    Returns
    -------
    ``(fig, zones)`` où *zones* est un dict :

    * ``zones["graphiques"]`` — liste d'axes prêts à recevoir vos graphiques
      via le paramètre ``ax=``.
    * ``zones["kpis"]`` — liste des axes tuile (pour surcharge éventuelle).

    Exemple
    -------
    >>> fig, zones = layout_rapport(
    ...     titre="Performance commerciale Q4 2024",
    ...     sous_titre="Résultats consolidés — 4 villes",
    ...     kpis=[
    ...         {"label": "Ventes",   "valeur": "1,24 M", "delta": "+12 %", "positif": True},
    ...         {"label": "Clients",  "valeur": "4 832",  "delta": "+5 %",  "positif": True},
    ...         {"label": "Marge",    "valeur": "23 %",   "delta": "−2 pts","positif": False},
    ...     ],
    ...     n_graphiques=2,
    ...     format="slide",
    ... )
    >>> barres(mois, ventes, titre="Ventes par mois", ax=zones["graphiques"][0])
    >>> ligne(mois, {"Douala": v1, "Yaoundé": v2}, ax=zones["graphiques"][1])
    >>> plt.show()
    """
    if kpis is None:
        kpis = []

    style_kpi_resolu = _resoudre_style_kpi(style_kpi)
    n_kpis = len(kpis)
    n_graphiques = max(1, min(int(n_graphiques), 3))

    NCOLS = 12
    # 2 colonnes par tuile KPI (max 8 colonnes pour les KPIs)
    kpi_cols  = min(n_kpis * 2, 8)
    title_cols = NCOLS - kpi_cols  # colonnes restantes pour le titre

    fig_size = _resoudre_figsize(figsize, format) or FORMATS["slide"]
    fig = plt.figure(figsize=fig_size)
    fig.patch.set_facecolor(_T["bg"])

    has_header = bool(titre or sous_titre or n_kpis > 0)

    if has_header:
        gs = fig.add_gridspec(
            2, NCOLS,
            height_ratios=[1.2, 4.2],
            hspace=0.08, wspace=0.06,
            left=0.03, right=0.97,
            top=0.97, bottom=0.05,
        )
        chart_row = 1
    else:
        gs = fig.add_gridspec(
            1, NCOLS,
            hspace=0.0, wspace=0.06,
            left=0.03, right=0.97,
            top=0.97, bottom=0.05,
        )
        chart_row = 0

    # ── Zone titre ────────────────────────────────────────────────────────
    axes_kpis = []
    if has_header:
        ax_h = fig.add_subplot(gs[0, :title_cols])
        ax_h.set_facecolor(_T["bg"])
        ax_h.set_axis_off()

        if titre:
            ax_h.text(0.0, 0.88, titre, transform=ax_h.transAxes,
                      fontsize=17, fontweight="bold", color=_T["texte"],
                      va="top", ha="left")
        if sous_titre:
            ax_h.text(0.0, 0.28, sous_titre, transform=ax_h.transAxes,
                      fontsize=10, color=_T["texte_dim"],
                      va="center", ha="left")

        # ── Tuiles KPI ────────────────────────────────────────────────────
        if n_kpis > 0:
            largeur = kpi_cols // n_kpis
            for i, kpi in enumerate(kpis):
                c0 = title_cols + i * largeur
                c1 = title_cols + (i + 1) * largeur if i < n_kpis - 1 else NCOLS
                ax_k = fig.add_subplot(gs[0, c0:c1])
                _dessiner_kpi(ax_k, kpi, style_kpi_resolu)
                axes_kpis.append(ax_k)

    # ── Axes graphiques ───────────────────────────────────────────────────
    chart_largeur = NCOLS // n_graphiques
    axes_charts = []
    for j in range(n_graphiques):
        c0 = j * chart_largeur
        c1 = (j + 1) * chart_largeur if j < n_graphiques - 1 else NCOLS
        ax_c = fig.add_subplot(gs[chart_row, c0:c1])
        ax_c.set_facecolor(_T["bg"])
        axes_charts.append(ax_c)

    # ── Note de bas de page ───────────────────────────────────────────────
    if note:
        fig.text(0.03, 0.01, note, fontsize=8, color=_T["texte_dim"],
                 style="italic", transform=fig.transFigure)

    return fig, {"graphiques": axes_charts, "kpis": axes_kpis}


# ══════════════════════════════════════════════════════════════════════════════
# Graphiques de classement et de distribution
# ══════════════════════════════════════════════════════════════════════════════

def bump(periodes, series: dict, titre="", sous_titre="", note="",
         figsize=None, format=None, ax=None,
         couleur=None, couleurs_multiples=None,
         montrer_valeurs=True, background=None):
    """
    Graphique de classement (bump chart) — évolution des positions dans le temps.

    Les lignes montrent comment chaque entité progresse ou recule en termes
    de rang d'une période à l'autre. Le rang 1 est affiché en haut.

    Parameters
    ----------
    periodes          : Liste des périodes (axe X) — ex: ``["Q1", "Q2", "Q3", "Q4"]``.
    series            : Dict ``{nom: [rang_t0, rang_t1, ...]}`` — rang de chaque
                        entité à chaque période (entier, 1 = premier).
    titre, sous_titre : Textes du graphique.
    note              : Note de bas de page.
    figsize, format   : Taille de figure.
    ax                : Axe matplotlib externe (optionnel).
    couleur           : Couleur uniforme pour toutes les séries.
    couleurs_multiples: Liste de couleurs hex, une par série.
    montrer_valeurs   : Afficher le rang dans chaque marqueur (défaut ``True``).

    Returns
    -------
    ``(fig, ax)``

    Exemple
    -------
    >>> bump(
    ...     periodes=["2021", "2022", "2023", "2024"],
    ...     series={
    ...         "Orange":  [1, 2, 1, 1],
    ...         "MTN":     [2, 1, 2, 3],
    ...         "Camtel":  [3, 3, 3, 2],
    ...     },
    ...     titre="Classement des opérateurs",
    ... )
    """
    noms     = list(series.keys())
    couleurs = _couleurs_auto(noms, couleur, couleurs_multiples)
    if isinstance(couleurs, str):
        couleurs = [couleurs] * len(noms)

    fig, ax = _new_fig(figsize, ax, format, background=background)

    x        = np.arange(len(periodes), dtype=float)
    max_rang = max(max(rangs) for rangs in series.values())

    for i, (nom, rangs) in enumerate(series.items()):
        y = np.array(rangs, dtype=float)
        c = couleurs[i % len(couleurs)] if isinstance(couleurs, list) else couleurs

        # Courbe lissée (scipy si disponible, sinon linéaire)
        if len(x) >= 4:
            try:
                from scipy.interpolate import make_interp_spline
                x_fine = np.linspace(x[0], x[-1], 400)
                spl    = make_interp_spline(x, y, k=3)
                ax.plot(x_fine, spl(x_fine), color=c, lw=2.5, alpha=0.9, zorder=2)
            except ImportError:
                ax.plot(x, y, color=c, lw=2.5, alpha=0.9, zorder=2)
        else:
            ax.plot(x, y, color=c, lw=2.5, alpha=0.9, zorder=2)

        # Marqueurs circulaires
        ax.scatter(x, y, s=260, color=c, zorder=4,
                   edgecolors=_T["fond_neutre"], linewidths=2)

        if montrer_valeurs:
            for xi, yi in zip(x, y):
                ax.text(float(xi), float(yi), str(int(yi)),
                        ha="center", va="center",
                        fontsize=8, color=_T["fond_neutre"],
                        fontweight="bold", zorder=5)

        # Étiquettes gauche et droite
        ax.text(x[0] - 0.45, y[0], nom, ha="right", va="center",
                fontsize=9, color=c, fontweight="bold")
        ax.text(x[-1] + 0.45, y[-1], nom, ha="left", va="center",
                fontsize=9, color=c, fontweight="bold")

    # Axe Y : rang 1 en haut
    ax.set_ylim(max_rang + 0.7, 0.3)
    ax.set_xlim(x[0] - 1.5, x[-1] + 1.5)
    ax.set_xticks(x)
    ax.set_xticklabels(periodes, fontsize=10, color=_T["texte_dim"])
    ax.set_yticks(range(1, max_rang + 1))
    ax.set_yticklabels(
        [f"#{r}" for r in range(1, max_rang + 1)],
        fontsize=9, color=_T["texte_dim"],
    )

    # Grille horizontale par niveau de rang
    ax.yaxis.grid(True, color=_T["grille"], lw=0.7, linestyle="--")
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)

    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(_T["grille"])
    ax.tick_params(length=0)

    return _finalize(ax, titre, sous_titre, note=note, legende=False, fig=fig)


def radar(categories, series: dict, titre="", sous_titre="", note="",
          figsize=None, format=None,
          vmin=0, vmax=None,
          couleur=None, couleurs_multiples=None,
          remplir=True, alpha_remplissage=0.15, background=None):
    """
    Graphique radar (spider / toile d'araignée) — profil multi-dimensionnel.

    Idéal pour comparer plusieurs entités selon un ensemble de critères
    qualitatifs ou quantitatifs sur la même échelle.

    Parameters
    ----------
    categories        : Liste des dimensions évaluées.
    series            : Dict ``{nom: [val_cat1, val_cat2, ...]}`` — une valeur
                        par catégorie, dans le même ordre.
    titre, sous_titre : Textes du graphique.
    note              : Note de bas de page.
    figsize, format   : Taille de figure.
    vmin, vmax        : Limites radiales (défaut : 0, max des valeurs × 1.05).
    couleur           : Couleur uniforme pour toutes les séries.
    couleurs_multiples: Couleurs hex explicites, une par série.
    remplir           : Remplir les polygones avec transparence.
    alpha_remplissage : Transparence du remplissage (0–1, défaut 0.15).

    Returns
    -------
    ``(fig, ax)``  — *ax* est un axe polaire.

    Exemple
    -------
    >>> radar(
    ...     categories=["Vitesse", "Force", "Endurance", "Précision", "Agilité"],
    ...     series={
    ...         "Joueur A": [8, 7, 9, 6, 9],
    ...         "Joueur B": [6, 9, 7, 8, 7],
    ...     },
    ...     titre="Comparaison des profils athlétiques",
    ... )
    """
    n      = len(categories)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    angles_closed = np.append(angles, angles[0])

    noms     = list(series.keys())
    couleurs = _couleurs_auto(noms, couleur, couleurs_multiples)
    if isinstance(couleurs, str):
        couleurs = [couleurs] * len(noms)

    fig_size = _resoudre_figsize(figsize, format) or (7, 7)
    fig      = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(111, projection="polar")
    _appliquer_background(fig, ax, background)

    all_vals = [v for vals in series.values() for v in vals]
    if vmax is None:
        vmax = max(all_vals) * 1.05 if all_vals else 10

    for i, (nom, valeurs) in enumerate(series.items()):
        c = couleurs[i % len(couleurs)] if isinstance(couleurs, list) else couleurs
        vals_closed = np.append(np.array(valeurs, dtype=float), valeurs[0])
        ax.plot(angles_closed, vals_closed, color=c, lw=2, label=nom, zorder=3)
        if remplir:
            ax.fill(angles_closed, vals_closed, color=c, alpha=alpha_remplissage, zorder=2)

    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontsize=9.5, color=_T["texte"])
    ax.set_ylim(vmin, vmax)
    ax.yaxis.grid(True, color=_T["grille"], lw=0.6, linestyle="--")
    ax.xaxis.grid(True, color=_T["grille"], lw=0.6)
    ax.spines["polar"].set_color(_T["grille"])
    ax.tick_params(axis="y", colors=_T["texte_dim"], labelsize=7.5)
    ax.set_rlabel_position(45)

    if len(noms) > 1:
        ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
                  framealpha=0, labelcolor=_T["texte"], fontsize=9)

    if titre:
        fig.suptitle(titre, fontsize=14, fontweight="bold",
                     color=_T["texte"], y=1.03)
    if sous_titre:
        fig.text(0.5, -0.01, sous_titre, ha="center",
                 fontsize=9, color=_T["texte_dim"])
    if note:
        fig.text(0.01, -0.04, note, fontsize=8, color=_T["texte_dim"],
                 style="italic")
    fig.tight_layout()
    return fig, ax


def ridgeline(series: dict, titre="", sous_titre="", note="",
              figsize=None, format=None,
              couleur=None, couleurs_multiples=None,
              alpha=0.75, chevauchement=0.7, background=None):
    """
    Graphique ridgeline (Joy Plot) — distributions superposées décalées.

    Visualise et compare la forme de la distribution de plusieurs groupes
    en les décalant verticalement. Chaque courbe est une estimation de
    densité (KDE) ou un histogramme lissé.

    Parameters
    ----------
    series            : Dict ``{nom: [valeurs...]}`` — données brutes par groupe,
                        dans l'ordre d'affichage (premier = haut).
    titre, sous_titre : Textes du graphique.
    note              : Note de bas de page.
    figsize, format   : Taille de figure.
    couleur           : Couleur uniforme pour tous les groupes.
    couleurs_multiples: Couleurs hex explicites, une par groupe.
    alpha             : Transparence du remplissage (0–1, défaut 0.75).
    chevauchement     : Hauteur maximale relative de chaque courbe —
                        0.5 = pas de chevauchement, > 1 = fort chevauchement
                        (défaut 0.7).

    Returns
    -------
    ``(fig, ax)``

    Notes
    -----
    Utilise ``scipy.stats.gaussian_kde`` si scipy est installé.
    Sinon, recourt à un histogramme numpy lissé par interpolation.

    Exemple
    -------
    >>> import numpy as np
    >>> ridgeline(
    ...     series={
    ...         "Groupe A": np.random.normal(5, 1, 300).tolist(),
    ...         "Groupe B": np.random.normal(7, 1.5, 300).tolist(),
    ...         "Groupe C": np.random.normal(4, 2, 300).tolist(),
    ...     },
    ...     titre="Distribution des scores par groupe",
    ... )
    """
    noms     = list(series.keys())
    n        = len(noms)
    couleurs = _couleurs_auto(noms, couleur, couleurs_multiples)
    if isinstance(couleurs, str):
        couleurs = [couleurs] * n

    fig_size = _resoudre_figsize(figsize, format) or (10, max(4, n * 1.4))
    fig, ax  = plt.subplots(figsize=fig_size)
    _appliquer_background(fig, ax, background)

    all_vals = np.concatenate([np.asarray(v, dtype=float) for v in series.values()])
    xmin, xmax = all_vals.min(), all_vals.max()
    xpad    = (xmax - xmin) * 0.12
    x_range = np.linspace(xmin - xpad, xmax + xpad, 500)

    for i, nom in enumerate(reversed(noms)):
        idx  = n - 1 - i
        vals = np.asarray(series[nom], dtype=float)
        c    = couleurs[idx % len(couleurs)] if isinstance(couleurs, list) else couleurs

        try:
            from scipy.stats import gaussian_kde
            density = gaussian_kde(vals, bw_method="scott")(x_range)
        except ImportError:
            counts, bins = np.histogram(vals, bins=40, density=True)
            density = np.interp(x_range, (bins[:-1] + bins[1:]) / 2, counts)

        if density.max() > 0:
            density = density / density.max() * chevauchement

        y_base = float(i)
        ax.fill_between(x_range, y_base, y_base + density,
                         color=c, alpha=alpha, lw=0, zorder=n - i)
        ax.plot(x_range, y_base + density, color=c, lw=1.5, zorder=n - i + 1)
        ax.axhline(y_base, color=_T["grille"], lw=0.6, zorder=1)

    ax.set_yticks(range(n))
    ax.set_yticklabels(list(reversed(noms)), fontsize=9.5, color=_T["texte"])
    ax.set_ylim(-0.15, n - 1 + chevauchement + 0.2)

    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(_T["grille"])
    ax.tick_params(axis="x", colors=_T["texte_dim"], length=0)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    return _finalize(ax, titre, sous_titre, note=note, legende=False, fig=fig)
