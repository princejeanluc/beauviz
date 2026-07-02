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



# ══════════════════════════════════════════════════════════════════════════════
# Initialisation
# ══════════════════════════════════════════════════════════════════════════════

def init():
    """Active le style beau_graphique pour toute la session matplotlib."""
    if os.path.exists(_STYLE_PATH):
        plt.style.use(_STYLE_PATH)
    else:
        # fallback léger si le fichier .mplstyle n'est pas trouvé
        plt.rcParams.update({
            "figure.facecolor": "#F7F8FC",
            "axes.facecolor":   "#F7F8FC",
            "axes.spines.top":  False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.6,
        })
    print("✓ Style beau_graphique activé.")


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
                     color="#1A1C2E", pad=14, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 26), textcoords="offset points",
                    fontsize=10, color="#6B6F85", annotation_clip=False)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    handles, labels = ax.get_legend_handles_labels()
    if legende and handles:
        ax.legend(loc="best")

    if note and fig:
        fig.text(0.01, -0.03, note, fontsize=8.5, color="#9295A8",
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


def _new_fig(figsize=None, ax=None, format=None):
    """Crée une nouvelle figure, ou réutilise l'axe fourni si présent."""
    if ax is not None:
        return ax.figure, ax
    return plt.subplots(figsize=_resoudre_figsize(figsize, format) or (10, 5.6))


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
          note="", markers=True, fill_last=False, figsize=None, ax=None, format=None, **_extra):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
    couleurs_series = _palette_pour(list(y_series.keys()))
    for i, (nom, vals) in enumerate(y_series.items()):
        color = couleurs_series[i]
        mk = "o" if markers else None
        ax.plot(x, vals, label=nom, color=color, marker=mk,
                markerfacecolor="white", markeredgecolor=color,
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

    _formater_axe_dates(ax, x)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ② Barres (verticales ou horizontales)
# ══════════════════════════════════════════════════════════════════════════════

def barres(categories, valeurs, titre="", sous_titre="", xlabel="", ylabel="",
           note="", couleur=None, horizontal=False, valeurs_sur_barres=True,
           couleurs_multiples=False, figsize=None, ax=None, format=None, **_extra):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)

    colors = _couleurs_auto(categories, couleur, couleurs_multiples)

    if horizontal:
        bars = ax.barh(categories, valeurs, color=colors, height=0.55)
        ax.invert_yaxis()
        if valeurs_sur_barres:
            for bar, val in zip(bars, valeurs):
                ax.text(bar.get_width() + max(valeurs) * 0.01, bar.get_y() + bar.get_height() / 2,
                        f"{val:,.0f}", va="center", ha="left", fontsize=9.5, fontweight="bold",
                        color="#2D2F3E")
        ax.set_xlim(0, max(valeurs) * 1.15)
        ax.xaxis.set_visible(False)
        ax.spines["bottom"].set_visible(False)
    else:
        bars = ax.bar(categories, valeurs, color=colors, width=0.55)
        if valeurs_sur_barres:
            for bar, val in zip(bars, valeurs):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(valeurs) * 0.01,
                        f"{val:,.0f}", ha="center", va="bottom", fontsize=9.5,
                        fontweight="bold", color="#2D2F3E")
        ax.set_ylim(0, max(valeurs) * 1.15)
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)
        _formater_axe_dates(ax, categories)

    return _finalize(ax, titre, sous_titre, xlabel, ylabel, note, legende=False, fig=fig,
                     ajuster_layout=ajuster_layout)


# ══════════════════════════════════════════════════════════════════════════════
# ③ Barres groupées
# ══════════════════════════════════════════════════════════════════════════════

def barres_groupees(categories, groupes: dict, titre="", sous_titre="",
                    xlabel="", ylabel="", note="", figsize=None, ax=None, format=None, **_extra):
    """
    Barres groupées multi-séries.

    Parameters
    ----------
    categories : Étiquettes de l'axe X
    groupes    : dict {"Groupe A": [v1, v2, …], "Groupe B": [v1, v2, …]}
    **_extra   : clés ignorées — permet d'appeler barres_groupees(**depuis_df(...))
                 même si le dict contient des clés destinées à d'autres fonctions
                 (x, y_series, valeurs)

    Exemple
    -------
    >>> barres_groupees(
    ...     categories=["T1", "T2", "T3", "T4"],
    ...     groupes={"2023": [30, 45, 40, 60], "2024": [38, 50, 55, 72]},
    ...     titre="Comparaison trimestrielle",
    ...     ylabel="Ventes (k€)"
    ... )
    """
    ajuster_layout = ax is None
    fig, ax = _new_fig(figsize, ax=ax, format=format)
    n_groupes = len(groupes)
    x = np.arange(len(categories))
    width = 0.7 / n_groupes
    couleurs_groupes = _palette_pour(list(groupes.keys()))

    for i, (nom, vals) in enumerate(groupes.items()):
        offset = (i - n_groupes / 2 + 0.5) * width
        bars = ax.bar(x + offset, vals, width * 0.9, label=nom,
                      color=couleurs_groupes[i])
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(max(v) for v in groupes.values()) * 0.01,
                    f"{val}", ha="center", va="bottom", fontsize=8.5, color="#2D2F3E")

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
         note="", empile=False, figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
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
                note="", courbe_densite=False, couleur=None, figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
    color = couleur or PALETTE[0]

    ax.hist(data, bins=bins, color=color, alpha=0.75, edgecolor="white", linewidth=0.5)

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
          ligne_tendance=False, figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)

    scatter_kw = dict(alpha=0.75, edgecolors="white", linewidths=0.6)

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
                        fontsize=8.5, color="#4A4D6A")

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
              donut=True, exploser_max=True, figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize or (7, 7), ax=ax)

    explode = [0] * len(valeurs)
    if exploser_max:
        explode[np.argmax(valeurs)] = 0.06

    wedge_kw = dict(linewidth=2.5, edgecolor="white")
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
                fontsize=12, fontweight="bold", color="#1A1C2E")

    # Légende externe propre
    legend_patches = [mpatches.Patch(color=PALETTE[i], label=f"{lb}  ({v})")
                      for i, (lb, v) in enumerate(zip(labels, valeurs))]
    ax.legend(handles=legend_patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=10)

    ax.set_aspect("equal")

    if titre:
        ax.set_title(titre, fontsize=15, fontweight="bold",
                     color="#1A1C2E", pad=18, loc="center")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0.5, 1.04), xycoords="axes fraction",
                    ha="center", fontsize=10, color="#6B6F85")
    if note and fig:
        fig.text(0.5, -0.04, note, ha="center", fontsize=8.5,
                 color="#9295A8", style="italic")

    if ajuster_layout:
        fig.tight_layout()
    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑧ Heatmap (matrice de corrélation ou autre)
# ══════════════════════════════════════════════════════════════════════════════

def heatmap(matrice, labels_lignes=None, labels_colonnes=None,
            titre="", sous_titre="", note="",
            cmap="RdYlGn", annot=True, fmt=".2f", figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize or (max(6, m * 0.9), max(5, n * 0.75)), ax=ax)

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
                     color="#1A1C2E", pad=14, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1.02), xycoords="axes fraction",
                    fontsize=10, color="#6B6F85")
    if note:
        fig.text(0.01, -0.03, note, fontsize=8.5, color="#9295A8",
                 style="italic", transform=ax.transAxes)

    if ajuster_layout:
        fig.tight_layout()
    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑨ dot_plot_comparatif — comparaison multi-dimensions entre deux périodes
# ══════════════════════════════════════════════════════════════════════════════

def dot_plot_comparatif(colonnes: dict, descriptions: dict = None,
                        label_avant="Avant", label_apres="Après",
                        couleur=None, titre="", sous_titre="", note="",
                        figsize=None, format=None):
    """
    Compare N dimensions (colonnes) entre deux périodes sur un axe Y commun.
    Chaque colonne affiche un point creux (avant) et un point plein (après)
    reliés par une flèche — idéal pour une progression multi-critères.

    Parameters
    ----------
    colonnes     : dict {"Nom colonne": (valeur_avant, valeur_apres), ...}
    descriptions : dict {"Nom colonne": "texte descriptif", ...} — optionnel
    label_avant  : étiquette de légende pour le point creux
    label_apres  : étiquette de légende pour le point plein
    couleur      : couleur des points/flèches (défaut : PALETTE[0])

    Exemple
    -------
    >>> dot_plot_comparatif(
    ...     colonnes={"News": (0.05, 0.15), "Searches": (0.08, 0.19)},
    ...     label_avant="2020", label_apres="2024",
    ...     titre="Score par vecteur (0 = faible ; 1 = élevé)",
    ... )
    """
    couleur = couleur or PALETTE[0]
    figsize = _resoudre_figsize(figsize, format)
    descriptions = descriptions or {}
    noms = list(colonnes.keys())
    n = len(noms)

    fig, ax = plt.subplots(figsize=figsize or (n * 2.2, 6))
    fig.subplots_adjust(top=0.68, bottom=0.1)

    valeurs_toutes = [v for paire in colonnes.values() for v in paire]
    ymin, ymax = min(valeurs_toutes), max(valeurs_toutes)
    marge = (ymax - ymin) * 0.18 or 0.1
    ax.set_ylim(ymin - marge, ymax + marge)

    trans = ax.get_xaxis_transform()  # x en données, y en fraction d'axes

    for i, nom in enumerate(noms):
        avant, apres = colonnes[nom]

        if i > 0:
            ax.axvline(i - 0.5, color="#D8DAE8", lw=0.5, zorder=0)

        if apres != avant:
            ax.annotate("", xy=(i, apres), xytext=(i, avant),
                        arrowprops=dict(arrowstyle="->", color="#A8ABBC", lw=1.3),
                        zorder=2)

        ax.scatter([i], [avant], s=120, facecolor="none", edgecolor=couleur,
                   linewidth=2, zorder=3)
        ax.scatter([i], [apres], s=120, facecolor=couleur, edgecolor=couleur,
                   zorder=4)

        # en-têtes de colonne en 2 niveaux, hors zone graphique
        ax.text(i, 1.32, nom, transform=trans, ha="center", va="bottom",
                fontsize=10, fontweight="bold", color="#1A1C2E", clip_on=False)
        desc = descriptions.get(nom)
        if desc:
            ax.text(i, 1.04, textwrap.fill(desc, 18), transform=trans,
                    ha="center", va="bottom", fontsize=8.5, color="#6B6F85",
                    linespacing=1.3, clip_on=False)

    ax.set_xlim(-0.6, n - 0.4)
    ax.xaxis.set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D8DAE8")
    ax.spines["bottom"].set_color("#D8DAE8")
    ax.tick_params(length=0)

    legende_handles = [
        plt.Line2D([0], [0], marker="o", linestyle="none", markersize=8,
                   markerfacecolor="none", markeredgecolor=couleur, markeredgewidth=2,
                   label=label_avant),
        plt.Line2D([0], [0], marker="o", linestyle="none", markersize=8,
                   markerfacecolor=couleur, markeredgecolor=couleur, label=label_apres),
    ]
    ax.legend(handles=legende_handles, loc="upper right", bbox_to_anchor=(1.0, 1.28),
              frameon=False, fontsize=9, ncol=2)

    if titre:
        fig.text(0.01, 0.96, titre, fontsize=14, fontweight="bold", color="#1A1C2E")
    if sous_titre:
        fig.text(0.01, 0.91, sous_titre, fontsize=10, color="#6B6F85")
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color="#9295A8", style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑩ bulle_4d — nuage de points à 4 variables (X, Y, taille, couleur ordinale)
# ══════════════════════════════════════════════════════════════════════════════

def bulle_4d(x: list, y: list, taille: list, couleur_var: list, labels: list = None,
             xlabel="", ylabel="", label_taille="", label_couleur="",
             niveaux_couleur: list = None, quadrants=False,
             quadrant_x=0.5, quadrant_y=0.5, taille_min=80, taille_max=2000,
             palette_bulles: list = None, titre="", sous_titre="", note="",
             figsize=None, format=None):
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
        cmap = plt.colormaps["Blues"]
        palette_bulles = [cmap(0.3 + 0.6 * i / max(ncol - 1, 1)) for i in range(ncol)]
    couleur_par_niveau = dict(zip(niveaux_couleur, palette_bulles))
    point_colors = [couleur_par_niveau.get(v, "#A8ABBC") for v in couleur_var]

    trange = (taille.max() - taille.min()) or 1.0
    tailles_norm = taille_min + (taille - taille.min()) / trange * (taille_max - taille_min)

    fig, ax = plt.subplots(figsize=figsize or (9, 7))

    if quadrants:
        ax.axhline(quadrant_y, color="#D8DAE8", lw=1, ls="--", zorder=1)
        ax.axvline(quadrant_x, color="#D8DAE8", lw=1, ls="--", zorder=1)

    ax.scatter(x, y, s=tailles_norm, color=point_colors, alpha=0.85,
              edgecolor="white", linewidth=1.2, zorder=3)

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
                        fontsize=9, color="#1A1C2E", va="center")

    xmarge = (x.max() - x.min()) * 0.1 or 0.1
    ymarge = (y.max() - y.min()) * 0.1 or 0.1
    ax.set_xlim(x.min() - xmarge, x.max() + xmarge)
    ax.set_ylim(y.min() - ymarge, y.max() + ymarge)

    ax.set_xlabel((xlabel + "  →") if xlabel else "", color="#6B6F85", fontsize=10)
    ax.set_ylabel((ylabel + "  ↑") if ylabel else "", color="#6B6F85", fontsize=10)
    ax.grid(axis="both", color="#D8DAE8", lw=0.6, ls="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=0)

    fig.subplots_adjust(right=0.76)

    handles_couleur = [plt.scatter([], [], s=120, color=couleur_par_niveau[niv],
                                    edgecolor="white") for niv in niveaux_couleur]
    leg1 = ax.legend(handles_couleur, [str(niv) for niv in niveaux_couleur],
                     title=label_couleur, loc="upper left", bbox_to_anchor=(1.02, 1.0),
                     frameon=False, fontsize=8.5, title_fontsize=9)
    ax.add_artist(leg1)

    valeurs_ref = sorted(set(np.round(np.linspace(taille.min(), taille.max(), 4)).astype(int).tolist()))
    handles_taille = [plt.scatter([], [], s=taille_min + (v - taille.min()) / trange * (taille_max - taille_min),
                                   color="#A8ABBC", alpha=0.5, edgecolor="#6B6F85")
                      for v in valeurs_ref]
    ax.legend(handles_taille, [str(v) for v in valeurs_ref],
             title=label_taille, loc="lower left", bbox_to_anchor=(1.02, 0.0),
             frameon=False, fontsize=8.5, title_fontsize=9, labelspacing=1.4)

    if titre:
        ax.set_title(titre, fontsize=14, fontweight="bold", color="#1A1C2E",
                     pad=14, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 26), textcoords="offset points",
                    fontsize=10, color="#6B6F85", annotation_clip=False)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color="#9295A8", style="italic")

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
                                            edgecolor="#A8ABBC", facecolor="none", lw=1.5, zorder=2))
            h = (val / vmax) * taille_carre if vmax else 0
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, h,
                                            facecolor=couleur, edgecolor="none",
                                            alpha=0.9, zorder=3))
            couleur_texte = "white" if h > taille_carre * 0.15 else couleur
            ax.text(x0 + taille_carre * 0.08, taille_carre * 0.06, fmt.format(val),
                    fontsize=11, fontweight="bold", color=couleur_texte,
                    ha="left", va="bottom", zorder=4)
            ax.text(x0 + taille_carre / 2, -taille_carre * 0.12, cat,
                    fontsize=9.5, color="#6B6F85", ha="center", va="top")
            sommets.append(taille_carre)
    else:  # mode == "ratio"
        if reference is not None:
            ratios = [v / r if r else 0 for v, r in zip(valeurs, reference)]
        else:
            ratios = valeurs
        for x0, cat, ratio in zip(positions, categories, ratios):
            cx, cy = x0 + taille_carre / 2, taille_carre / 2
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, taille_carre,
                                            edgecolor="#A8ABBC", facecolor="none", lw=1.5, zorder=2))
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
                    fontsize=9.5, color="#6B6F85", ha="center", va="top")
            sommets.append(sommet + taille_carre * 0.32)

    ax.set_xlim(-taille_carre * 0.3, positions[-1] + taille_carre * 1.3)
    ax.set_ylim(-taille_carre * 0.4, max(sommets) * 1.1)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    if titre:
        ax.set_title(titre, fontsize=14, fontweight="bold", color="#1A1C2E",
                     pad=18, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 8), textcoords="offset points",
                    fontsize=10, color="#6B6F85", annotation_clip=False)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color="#9295A8", style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑫ box_plot — distribution par catégorie (boîtes à moustaches)
# ══════════════════════════════════════════════════════════════════════════════

def box_plot(data: list, categories: list = None, titre="", sous_titre="",
             xlabel="", ylabel="", note="", horizontal=False, couleur=None,
             afficher_points=False, notch=False, figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
    couleur = couleur or PALETTE[0]
    n = len(data)
    categories = categories or [f"Groupe {i + 1}" for i in range(n)]

    bp = ax.boxplot(
        data, vert=not horizontal, patch_artist=True, notch=notch,
        labels=categories, widths=0.5,
        medianprops=dict(color="#1A1C2E", linewidth=2),
        whiskerprops=dict(color="#A8ABBC", linewidth=1.2),
        capprops=dict(color="#A8ABBC", linewidth=1.2),
        flierprops=dict(marker="o", markerfacecolor="none",
                        markeredgecolor="#A8ABBC", markersize=5),
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
           figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
    n = len(data)
    categories = categories or [f"Groupe {i + 1}" for i in range(n)]
    positions = list(range(1, n + 1))

    vp = ax.violinplot(data, positions=positions, showmedians=True, showextrema=False)
    for i, body in enumerate(vp["bodies"]):
        color = couleur or PALETTE[i % len(PALETTE)]
        body.set_facecolor(color)
        body.set_edgecolor(color)
        body.set_alpha(0.75)
    vp["cmedians"].set_color("#1A1C2E")
    vp["cmedians"].set_linewidth(1.5)

    if afficher_boxplot:
        bp = ax.boxplot(data, positions=positions, widths=0.08, patch_artist=True,
                        showfliers=False, medianprops=dict(color=PALETTE[1], linewidth=2))
        for box in bp["boxes"]:
            box.set_facecolor("white")
            box.set_edgecolor("#6B6F85")

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
              figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
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
                    color="#D8DAE8", linewidth=1, linestyle="--", zorder=1)

    plage = max(b + h for b, h in zip(bottoms, hauteurs)) * 0.02 or 1
    for xi, b, h, tot, val in zip(x, bottoms, hauteurs, est_total, vals_affiche):
        signe = "+" if (val > 0 and not tot) else ""
        ax.text(xi, b + h + plage, f"{signe}{val:,.0f}", ha="center", va="bottom",
                fontsize=9.5, fontweight="bold", color="#2D2F3E")

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
             xlabel="", note="", couleur=None, trier=True, ligne_ref: float = None,
             label_ref="", taille_point=8, figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
    couleur = couleur or PALETTE[0]

    paires = list(zip(categories, valeurs))
    if trier:
        paires.sort(key=lambda p: p[1], reverse=True)
    categories_t, valeurs_t = (list(t) for t in zip(*paires)) if paires else ([], [])
    y_pos = np.arange(len(categories_t))

    ax.hlines(y_pos, 0, valeurs_t, color="#D8DAE8", linewidth=1.6, zorder=2)
    ax.plot(valeurs_t, y_pos, "o", color=couleur, markersize=taille_point, zorder=3)

    marge = (max(valeurs_t) * 0.03) if valeurs_t else 1
    for yi, val in zip(y_pos, valeurs_t):
        ax.text(val + marge, yi, f"{val:,.0f}", va="center", ha="left",
                fontsize=9.5, fontweight="bold", color="#2D2F3E")

    if ligne_ref is not None:
        ax.axvline(ligne_ref, color="#6B6F85", linewidth=1.2, linestyle="--", zorder=1)
        if label_ref:
            ax.text(ligne_ref, -0.6, label_ref, fontsize=9, color="#6B6F85",
                    ha="center", va="top")

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
          afficher_valeurs=True, focus: list = None, figsize=None, ax=None, format=None):
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
    fig, ax = _new_fig(figsize, ax=ax, format=format)
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
                marker="o", markersize=6, markerfacecolor=couleur, markeredgecolor="white")

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
                    color="#1A1C2E")

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

        ax_i.set_title(str(groupe), fontsize=10, fontweight="bold", color="#1A1C2E")
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
        fig.suptitle(titre, fontsize=15, fontweight="bold", color="#1A1C2E", y=1.02)
    if sous_titre:
        fig.text(0.01, 0.965, sous_titre, fontsize=10, color="#6B6F85")
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color="#9295A8", style="italic")

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
                     color="#1A1C2E", y=1.02)
    return fig, np.array(axes[:n])
