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
import matplotlib.path as mpath
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import datetime
import os
import textwrap
import sys


def _print_safe(msg):
    """Affiche *msg* ; replie sur une version sans caractères non supportés
    si le terminal ne gère pas l'UTF-8 (ex: console Windows en cp1252 par
    défaut — sinon UnicodeEncodeError sur les symboles ✓/⚠/┌─┐ etc.)."""
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(msg.encode(enc, errors="replace").decode(enc))


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

    _print_safe(f"✓ Style beau_graphique activé (thème : {nom_theme}).")


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
        ax2.plot(kde_x, kde_y, color=PALETTE[1 % len(PALETTE)], linewidth=2.4, label="Densité")
        ax2.set_yticks([])
        ax2.spines["right"].set_visible(False)
        ax2.spines["top"].set_visible(False)

    # Ligne médiane
    mediane = np.median(data)
    ax.axvline(mediane, color=PALETTE[3 % len(PALETTE)], linewidth=1.8, linestyle="--", alpha=0.8)
    ax.text(mediane, ax.get_ylim()[1] * 0.97, f" Médiane\n {mediane:.1f}",
            color=PALETTE[3 % len(PALETTE)], fontsize=9, va="top")

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
        ax.plot(xfit, m * xfit_num + b, color=PALETTE[1 % len(PALETTE)], linewidth=1.8,
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
                color = _T["bg"] if val < thresh else _T["texte"]
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
                        showfliers=False, medianprops=dict(color=PALETTE[1 % len(PALETTE)], linewidth=2))
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
    couleur_pos = couleur_pos or _COULEUR_HAUT
    couleur_neg = couleur_neg or _COULEUR_BAS
    couleur_total = couleur_total or _T["texte_dim"]

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
    couleur_hausse = couleur_hausse or _COULEUR_HAUT
    couleur_baisse = couleur_baisse or _COULEUR_BAS
    couleur_stable = couleur_stable or _T["serie_dim"]
    n = len(categories)

    for i in range(n):
        vg, vd = valeurs_gauche[i], valeurs_droite[i]
        if focus is not None:
            if categories[i] in focus:
                couleur, alpha, lw, z = PALETTE[0], 1.0, 2.4, 4
            else:
                couleur, alpha, lw, z = _T["serie_dim"], 0.3, 1.4, 2
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
          format=None, background=None, **kwargs):
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
    _appliquer_background(fig, None, background)
    gs = fig.add_gridspec(nrows, ncols, hspace=0.55, wspace=0.3)

    axes = []
    for idx in range(nrows * ncols):
        row, col = divmod(idx, ncols)
        ax_i = fig.add_subplot(gs[row, col])
        _appliquer_background(fig, ax_i, background)
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

def dashboard(configs: list, titre_global="", ncols=2,
              hspace=0.5, wspace=0.3,
              figsize=None, format=None, background=None):
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
    _appliquer_background(fig, None, background)
    gs = fig.add_gridspec(nrows, ncols, hspace=hspace, wspace=wspace)

    _fn_map = {
        "ligne": ligne,
        "barres": barres,
        "aire": aire,
        "nuage": nuage,
        "histogramme": histogramme,
        "barres_groupees": barres_groupees,
        "camembert": camembert,
        "heatmap": heatmap,
        "flux": flux,
    }

    axes = []
    for idx in range(nrows * ncols):
        row, col = divmod(idx, ncols)
        ax = fig.add_subplot(gs[row, col])
        _appliquer_background(fig, ax, background)
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
# Flux — diagramme de Sankey (rubans de Bézier, style maison)
# ══════════════════════════════════════════════════════════════════════════════

def _stade_noeuds(liens):
    """Attribue à chaque nœud une colonne = plus long chemin depuis une
    source (aucune configuration manuelle requise). Lève ValueError si le
    graphe formé par *liens* contient un cycle (flux() exige un DAG)."""
    predecesseurs = {}
    for s, c, _ in liens:
        predecesseurs.setdefault(s, [])
        predecesseurs.setdefault(c, []).append(s)

    cache, en_cours = {}, set()

    def _profondeur(nom):
        if nom in cache:
            return cache[nom]
        if nom in en_cours:
            raise ValueError(
                f"flux() : cycle détecté impliquant '{nom}' — seuls les "
                f"graphes acycliques (DAG) sont supportés."
            )
        en_cours.add(nom)
        preds = predecesseurs.get(nom, [])
        profondeur = 0 if not preds else 1 + max(_profondeur(p) for p in preds)
        en_cours.discard(nom)
        cache[nom] = profondeur
        return profondeur

    return {nom: _profondeur(nom) for nom in predecesseurs}


def flux(liens, noeuds=None,
         titre="", sous_titre="", note="",
         couleur_ruban="source", couleurs_noeuds=None,
         alpha_ruban=0.55, fmt="{:.0f}",
         figsize=None, format=None, background=None, ax=None):
    """
    Diagramme de flux (Sankey) — rubans de Bézier entre nœuds répartis en
    colonnes, largeur proportionnelle à la valeur du flux.

    Quand l'utiliser
    ----------------
    Montrer comment une quantité se répartit et circule à travers plusieurs
    étapes successives (budget, trafic, parcours client, migration de parts
    de marché).

    Ne pas utiliser
    ----------------
    Si le graphe des flux contient un cycle (A → B → A) — non supporté, voir
    plus bas. Au-delà d'une dizaine de nœuds par colonne, le diagramme
    devient difficile à lire (aucune minimisation de croisement globale
    n'est appliquée, seulement un tri local par colonne cible).

    Parameters
    ----------
    liens          : liste de tuples ``(source, cible, valeur)``. La colonne
                     de chaque nœud est déduite automatiquement (plus long
                     chemin depuis une source) — aucun paramètre de layout
                     manuel n'est nécessaire.
    noeuds         : ordre vertical explicite (liste de noms) — optionnel,
                     sinon ordre de première apparition dans *liens*.
    couleur_ruban  : ``"source"`` (défaut) ou ``"cible"`` — le nœud dont la
                     couleur détermine celle du ruban — ou une couleur hex
                     fixe appliquée à tous les rubans.
    couleurs_noeuds: dict ``{nom: couleur}`` — sinon couleurs de ``PALETTE``
                     cyclées par ordre d'apparition (via ``_palette_pour``).
    alpha_ruban    : transparence des rubans (0-1, défaut 0.55).
    fmt            : format des valeurs affichées sous chaque nœud.

    Returns
    -------
    (fig, ax)

    Exemple
    -------
    >>> flux([
    ...     ("Recherche", "Site A", 120), ("Pub", "Site A", 60),
    ...     ("Site A", "Achat", 90), ("Site A", "Abandon", 90),
    ... ], titre="Parcours d'acquisition")
    """
    if not liens:
        raise ValueError("flux() : 'liens' est vide.")

    liens = [(str(s), str(c), float(v)) for s, c, v in liens]
    for s, c, v in liens:
        if v <= 0:
            raise ValueError(
                f"flux() : la valeur du lien ('{s}', '{c}', {v}) doit être "
                f"strictement positive."
            )

    stades = _stade_noeuds(liens)
    noms_liens = list(dict.fromkeys([n for s, c, _ in liens for n in (s, c)]))

    if noeuds is not None:
        manquants = set(noms_liens) - set(noeuds)
        if manquants:
            raise ValueError(
                f"flux() : {sorted(manquants)} référencé(s) dans 'liens' "
                f"mais absent(s) de 'noeuds'."
            )
        noms = [n for n in noeuds if n in stades]
    else:
        noms = noms_liens

    total_in  = {n: 0.0 for n in noms}
    total_out = {n: 0.0 for n in noms}
    for s, c, v in liens:
        total_out[s] += v
        total_in[c]  += v
    valeur_noeud = {n: max(total_in[n], total_out[n]) for n in noms}

    n_colonnes = max(stades.values()) + 1
    colonnes = [[n for n in noms if stades[n] == i] for i in range(n_colonnes)]

    max_total_col = max(sum(valeur_noeud[n] for n in col) for col in colonnes)
    gap = max_total_col * 0.025

    # ── Positions verticales (chaque colonne centrée sur la même échelle) ──
    y_haut = {}
    for col in colonnes:
        hauteur_col = sum(valeur_noeud[n] for n in col) + gap * max(0, len(col) - 1)
        y = (max_total_col - hauteur_col) / 2 + hauteur_col
        for n in col:
            y_haut[n] = y
            y -= valeur_noeud[n] + gap

    couleurs = dict(couleurs_noeuds or {})
    a_colorier = [n for n in noms if n not in couleurs]
    for n, c in zip(a_colorier, _palette_pour(a_colorier)):
        couleurs[n] = c

    fig, ax = _new_fig(figsize or (11, 6.5), ax=ax, format=format, background=background)

    largeur_noeud = 0.16
    espace_col = 1.0
    x_col = {i: i * (largeur_noeud + espace_col) for i in range(n_colonnes)}

    # ── Curseurs d'attache : répartissent les liens sur le bord d'un nœud,
    # triés par colonne source puis position verticale de la cible (limite
    # les croisements sans viser une minimisation globale) ─────────────────
    curseur_sortie = {n: y_haut[n] for n in noms}
    curseur_entree = {n: y_haut[n] for n in noms}
    liens_tries = sorted(liens, key=lambda l: (stades[l[0]], -y_haut[l[1]]))

    for s, c, v in liens_tries:
        y0_haut = curseur_sortie[s]
        y0_bas  = y0_haut - v
        curseur_sortie[s] = y0_bas

        y1_haut = curseur_entree[c]
        y1_bas  = y1_haut - v
        curseur_entree[c] = y1_bas

        x0 = x_col[stades[s]] + largeur_noeud
        x1 = x_col[stades[c]]
        xm = (x0 + x1) / 2

        verts = [
            (x0, y0_haut), (xm, y0_haut), (xm, y1_haut), (x1, y1_haut),
            (x1, y1_bas), (xm, y1_bas), (xm, y0_bas), (x0, y0_bas),
            (x0, y0_haut),
        ]
        codes = [
            mpath.Path.MOVETO,
            mpath.Path.CURVE4, mpath.Path.CURVE4, mpath.Path.CURVE4,
            mpath.Path.LINETO,
            mpath.Path.CURVE4, mpath.Path.CURVE4, mpath.Path.CURVE4,
            mpath.Path.CLOSEPOLY,
        ]
        if couleur_ruban == "source":
            couleur = couleurs[s]
        elif couleur_ruban == "cible":
            couleur = couleurs[c]
        else:
            couleur = couleur_ruban
        ax.add_patch(mpatches.PathPatch(
            mpath.Path(verts, codes), facecolor=couleur,
            edgecolor="none", alpha=alpha_ruban, zorder=2,
        ))

    # ── Nœuds ────────────────────────────────────────────────────────────
    for n in noms:
        x0 = x_col[stades[n]]
        ax.add_patch(mpatches.Rectangle(
            (x0, y_haut[n] - valeur_noeud[n]), largeur_noeud, valeur_noeud[n],
            facecolor=couleurs[n], edgecolor="none", zorder=3,
        ))
        label = f"{n}\n{fmt.format(valeur_noeud[n])}"
        derniere_colonne = stades[n] == n_colonnes - 1
        x_texte = (x0 - 0.04) if derniere_colonne else (x0 + largeur_noeud + 0.04)
        ax.text(x_texte, y_haut[n] - valeur_noeud[n] / 2, label,
                ha=("right" if derniere_colonne else "left"), va="center",
                fontsize=9, color=_T["texte"], linespacing=1.3, zorder=4)

    ax.set_xlim(-0.3, x_col[n_colonnes - 1] + largeur_noeud + 0.3)
    ax.set_ylim(0, max_total_col)
    ax.axis("off")

    if titre:
        fig.text(0.02, 0.97, titre, fontsize=14, fontweight="bold", color=_T["texte"])
    if sous_titre:
        fig.text(0.02, 0.92, sous_titre, fontsize=9.5, color=_T["texte_dim"])
    if note:
        fig.text(0.02, 0.01, note, fontsize=7.5, color=_T["texte_dim"], style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# Ré-exports — fonctions vivant dans des modules à plat séparés
# ══════════════════════════════════════════════════════════════════════════════
# beau_graphique_mckinsey.py et beau_graphique_layout.py font `import
# beau_graphique as bg` pour accéder au socle (PALETTE, _T, _new_fig, ...) à
# chaud. Les importer ici, en bas de fichier, permet à `from beau_graphique
# import dot_plot_comparatif` (et à `bg.dot_plot_comparatif`) de continuer à
# fonctionner sans changement pour l'utilisateur final — l'import circulaire
# est sûr car ces modules ne lisent `bg.xxx` que depuis l'intérieur de leurs
# fonctions, jamais au niveau module.
from beau_graphique_mckinsey import (
    dot_plot_comparatif, bulle_4d, unit_chart,
    tendances_grille, tendances_comparatives,
    bump, radar, ridgeline,
)
from beau_graphique_layout import slide, layout_rapport


