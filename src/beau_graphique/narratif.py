"""
narratif.py
===========
Extension de beau_graphique.py pour les graphiques d'analyse et de présentation
de résultats — basée sur les principes de communication visuelle :

    • Hiérarchie visuelle    → ce qui compte ressort immédiatement
    • Contraste & opacité    → gris pour le contexte, couleur pour le signal
    • Gammes de gris         → neutraliser le bruit, focaliser l'attention
    • Couleur d'accent       → une seule couleur forte = un seul message
    • Typographie narrative  → titre = affirmation, pas étiquette
    • Annotations dirigées   → flèches, zones, seuils qui "parlent"

Usage
-----
    from narratif import (
        barres_focus, ligne_focus, comparaison_avant_apres,
        barres_ranked, bullet_chart, divergent,
        annoter_zone, annoter_seuil, annoter_delta,
        palette_focus
    )

Chaque fonction accepte les mêmes kwargs de base (titre, sous_titre, note, figsize)
et ajoute des paramètres narratifs spécifiques.

Toutes les fonctions respectent le thème actif (bg.init(theme=...)) et acceptent
background= pour un fond transparent ou personnalisé.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np
import os

# Accents disponibles — à choisir selon le message
ACCENTS = {
    "bleu"    : "#4361EE",
    "rouge"   : "#E63946",
    "vert"    : "#2DC653",
    "orange"  : "#F3722C",
    "violet"  : "#7209B7",
    "rose"    : "#F72585",
    "cyan"    : "#4CC9F0",
    "or"      : "#F4A261",
}

ACCENT_DEFAUT = ACCENTS["bleu"]

_STYLE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "beau_graphique.mplstyle")


# ══════════════════════════════════════════════════════════════════════════════
# Utilitaires internes
# ══════════════════════════════════════════════════════════════════════════════

def _t():
    """Retourne le thème actif de beau_graphique (lecture dynamique)."""
    import beau_graphique as _bg
    return _bg._T


def _init_ax(figsize, background=None, ax=None):
    """Crée ou réutilise une figure/axe stylée en lisant le thème actif.

    Si ``ax`` est fourni (ex: depuis slide()), on dessine dans cet axe
    existant sans créer de nouvelle figure.
    """
    import beau_graphique as _bg
    if ax is not None:
        fig = ax.get_figure()
    else:
        fig, ax = plt.subplots(figsize=figsize or (11, 5.5))
        _bg._appliquer_background(fig, ax, background)
    T = _t()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(T["grille"])
    ax.spines["bottom"].set_color(T["grille"])
    ax.tick_params(colors=T["texte_dim"], length=0)
    ax.grid(axis="y", color=T["grille"], linewidth=0.7, linestyle="--", alpha=0.8)
    return fig, ax


def _header(fig, ax, titre, sous_titre, note):
    """Titre affirmatif + sous-titre descriptif + note de source."""
    T = _t()
    if titre:
        ax.set_title(titre, fontsize=14, fontweight="bold", color=T["texte"],
                     pad=12, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 28), textcoords="offset points",
                    fontsize=10, color=T["texte_dim"], annotation_clip=False)
    if note:
        fig.text(0.01, 0.01, note, fontsize=8, color=T["serie_dim"],
                 style="italic", transform=fig.transFigure)


def _finalize(fig, skip_layout=False):
    if not skip_layout:
        fig.tight_layout()
    return fig


def palette_focus(n_total, indices_focus, accent=ACCENT_DEFAUT):
    """
    Génère une liste de couleurs où seules les barres/séries `indices_focus`
    reçoivent la couleur accent — les autres tombent en gris.

    Parameters
    ----------
    n_total       : nombre total d'éléments
    indices_focus : int ou liste d'ints — positions à mettre en accent
    accent        : couleur hex de l'accent

    Exemple
    -------
    >>> colors = palette_focus(6, [2, 4], accent=ACCENTS["rouge"])
    # → [GRIS, GRIS, ROUGE, GRIS, ROUGE, GRIS]
    """
    if isinstance(indices_focus, int):
        indices_focus = [indices_focus]
    gris = _t()["serie_dim"]
    return [accent if i in indices_focus else gris for i in range(n_total)]


# ══════════════════════════════════════════════════════════════════════════════
# ① barres_focus — "une barre ressort, les autres s'effacent"
# ══════════════════════════════════════════════════════════════════════════════

def barres_focus(categories, valeurs, focus,
                 titre="", sous_titre="", note="",
                 accent=ACCENT_DEFAUT, horizontal=False,
                 fmt="{:.0f}", figsize=None, format=None, background=None):
    """
    Barres en gris neutre sauf les éléments en `focus` qui reçoivent la couleur
    d'accent. Le regard va directement là où l'analyse veut l'emmener.

    Parameters
    ----------
    categories : liste de str
    valeurs    : liste de float
    focus      : int ou liste d'ints — index des barres à mettre en valeur
    accent     : couleur d'accent (défaut bleu)
    horizontal : True → barres horizontales
    fmt        : format des étiquettes de valeur (ex: "{:.1f}%", "{:,.0f}")

    Exemple
    -------
    >>> barres_focus(
    ...     categories=["Jan","Fév","Mar","Avr","Mai","Jun"],
    ...     valeurs=[42, 38, 71, 55, 49, 63],
    ...     focus=2,   # ← Mars est notre point d'analyse
    ...     titre="Mars affiche le pic de trimestre (+87 % vs Fév)",
    ...     sous_titre="Ventes mensuelles · Produit A · S1 2024",
    ...     accent=ACCENTS["rouge"]
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    fig, ax = _init_ax(figsize, background)
    colors = palette_focus(len(categories), focus, accent)
    alphas = [1.0 if c == accent else 0.45 for c in colors]

    if isinstance(focus, int):
        focus = [focus]

    if horizontal:
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_color(T["grille"])
        ax.grid(axis="x", color=T["grille"], lw=0.7, ls="--", alpha=0.8)
        ax.grid(axis="y", visible=False)
        for i, (cat, val, col, alpha) in enumerate(zip(categories, valeurs, colors, alphas)):
            ax.barh(cat, val, color=col, alpha=alpha, height=0.55)
            weight = "bold" if i in focus else "normal"
            size = 10.5 if i in focus else 9
            fc = T["texte"] if i in focus else T["texte_dim"]
            ax.text(val + max(valeurs) * 0.01, i,
                    fmt.format(val), va="center", ha="left",
                    fontsize=size, fontweight=weight, color=fc)
        ax.set_xlim(0, max(valeurs) * 1.18)
        ax.xaxis.set_visible(False)
        ax.invert_yaxis()
        for i, lbl in enumerate(ax.yaxis.get_ticklabels()):
            if i in focus:
                lbl.set_fontweight("bold")
                lbl.set_color(T["texte"])
            else:
                lbl.set_color(T["texte_dim"])
    else:
        for i, (cat, val, col, alpha) in enumerate(zip(categories, valeurs, colors, alphas)):
            ax.bar(i, val, color=col, alpha=alpha, width=0.55)
            weight = "bold" if i in focus else "normal"
            size = 10.5 if i in focus else 9
            fc = T["texte"] if i in focus else T["texte_dim"]
            ax.text(i, val + max(valeurs) * 0.012,
                    fmt.format(val), ha="center", va="bottom",
                    fontsize=size, fontweight=weight, color=fc)
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories)
        for i, lbl in enumerate(ax.xaxis.get_ticklabels()):
            if i in focus:
                lbl.set_fontweight("bold")
                lbl.set_color(T["texte"])
            else:
                lbl.set_color(T["texte_dim"])
        ax.set_ylim(0, max(valeurs) * 1.2)
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig), ax


# ══════════════════════════════════════════════════════════════════════════════
# ② ligne_focus — "une courbe ressort, les autres sont le contexte"
# ══════════════════════════════════════════════════════════════════════════════

def ligne_focus(x, series: dict, focus_serie,
                titre="", sous_titre="", note="",
                accent=ACCENT_DEFAUT, markers=True,
                annoter_fin=True, figsize=None, format=None, background=None):
    """
    Graphique multi-lignes où une série est mise en avant (couleur + épaisseur),
    les autres passent en gris semi-transparent — elles donnent le contexte
    sans voler l'attention.

    Parameters
    ----------
    series      : dict {"Nom": [valeurs], ...}
    focus_serie : str — clé de la série à mettre en accent
    annoter_fin : annoter la valeur finale de chaque série

    Exemple
    -------
    >>> ligne_focus(
    ...     x=annees,
    ...     series={"France": [...], "Allemagne": [...], "Cameroun": [...]},
    ...     focus_serie="Cameroun",
    ...     titre="Le Cameroun dépasse l'Allemagne en 2023",
    ...     accent=ACCENTS["vert"]
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    fig, ax = _init_ax(figsize, background)
    ax.grid(axis="y", color=T["grille"], lw=0.6, ls="--", alpha=0.7)

    x_arr = list(range(len(x))) if not isinstance(x[0], (int, float)) else x
    x_labels = x if not isinstance(x[0], (int, float)) else None

    for nom, vals in series.items():
        if nom == focus_serie:
            continue
        ax.plot(x_arr, vals, color=T["serie_dim"], lw=1.4, alpha=0.55,
                marker=("o" if markers else None),
                mfc=T["bg"], mec=T["serie_dim"], mew=1.2, ms=4, zorder=2)
        if annoter_fin:
            ax.annotate(nom, xy=(x_arr[-1], vals[-1]),
                        xytext=(5, 0), textcoords="offset points",
                        fontsize=8.5, color=T["texte_dim"], va="center")

    vals_focus = series[focus_serie]
    ax.plot(x_arr, vals_focus, color=accent, lw=3.0, zorder=4,
            marker=("o" if markers else None),
            mfc=T["bg"], mec=accent, mew=2.2, ms=7)
    if annoter_fin:
        ax.annotate(focus_serie, xy=(x_arr[-1], vals_focus[-1]),
                    xytext=(7, 0), textcoords="offset points",
                    fontsize=10.5, color=accent, fontweight="bold", va="center")

    if x_labels:
        ax.set_xticks(x_arr)
        ax.set_xticklabels(x_labels, color=T["texte_dim"])

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig), ax


# ══════════════════════════════════════════════════════════════════════════════
# ③ comparaison_avant_apres — contraste temporel clair
# ══════════════════════════════════════════════════════════════════════════════

def comparaison_avant_apres(categories, avant, apres,
                            label_avant="Avant", label_apres="Après",
                            titre="", sous_titre="", note="",
                            accent=ACCENT_DEFAUT, figsize=None, format=None,
                            background=None):
    """
    Barres doubles "Avant / Après" avec :
    - L'avant en gris neutre
    - L'après en accent
    - Delta (+/−) annoté sur chaque paire
    - Code couleur rouge/vert selon la direction du changement

    Exemple
    -------
    >>> comparaison_avant_apres(
    ...     categories=["Conversion", "Panier moyen", "Rétention"],
    ...     avant=[3.2, 42, 68],
    ...     apres=[4.7, 55, 81],
    ...     titre="La refonte UI améliore les 3 KPIs clés",
    ...     label_avant="Avant refonte", label_apres="Après refonte"
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    fig, ax = _init_ax(figsize, background)
    n = len(categories)
    x = np.arange(n)
    w = 0.32

    ax.bar(x - w/2, avant, width=w, color=T["serie_dim"], alpha=0.6, label=label_avant)
    ax.bar(x + w/2, apres, width=w, color=accent, alpha=0.9, label=label_apres)

    ymax = max(max(avant), max(apres))

    for i, (a, b) in enumerate(zip(avant, apres)):
        ax.text(i - w/2, a + ymax*0.01, f"{a}", ha="center", va="bottom",
                fontsize=9, color=T["texte_dim"])
        ax.text(i + w/2, b + ymax*0.01, f"{b}", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=T["texte"])
        delta = b - a
        pct   = (delta / a * 100) if a != 0 else 0
        sign  = "+" if delta >= 0 else ""
        color_delta = ACCENTS["vert"] if delta >= 0 else ACCENTS["rouge"]
        ax.text(i, max(a, b) + ymax*0.085,
                f"{sign}{pct:.0f}%", ha="center", va="bottom",
                fontsize=10, fontweight="bold", color=color_delta)
        arrow = "▲" if delta >= 0 else "▼"
        ax.text(i, max(a, b) + ymax*0.055, arrow,
                ha="center", va="bottom", fontsize=9, color=color_delta)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, color=T["texte_dim"], fontsize=10)
    ax.set_ylim(0, ymax * 1.28)
    ax.yaxis.set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, fontsize=9.5, loc="upper left",
              labelcolor=T["texte_dim"])

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig), ax


# ══════════════════════════════════════════════════════════════════════════════
# ④ barres_ranked — classement avec hiérarchie visuelle par rang
# ══════════════════════════════════════════════════════════════════════════════

def barres_ranked(categories, valeurs,
                  titre="", sous_titre="", note="",
                  accent=ACCENT_DEFAUT, top_n=3,
                  fmt="{:.0f}", figsize=None, format=None, background=None):
    """
    Classement horizontal trié — le Top N reçoit l'accent, le reste s'efface
    progressivement via l'opacité (hiérarchie par rang).

    Parameters
    ----------
    top_n : combien d'éléments reçoivent la couleur accent (les autres = gris dégradé)

    Exemple
    -------
    >>> barres_ranked(
    ...     categories=pays, valeurs=scores,
    ...     titre="Top 3 des marchés les plus performants",
    ...     top_n=3, accent=ACCENTS["or"]
    ... )
    """
    order = np.argsort(valeurs)[::-1]
    cats_s  = [categories[i] for i in order]
    vals_s  = [valeurs[i]    for i in order]
    n       = len(vals_s)
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    fig, ax = _init_ax(figsize or (10, max(4, n * 0.55)), background)
    ax.grid(axis="x", color=T["grille"], lw=0.7, ls="--", alpha=0.8)
    ax.grid(axis="y", visible=False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(T["grille"])
    ax.xaxis.set_visible(False)

    for i, (cat, val) in enumerate(zip(cats_s, vals_s)):
        if i < top_n:
            color = accent
            alpha = 1.0 - i * 0.12
            fw    = "bold"
            fsize = 10.5
            fc    = T["texte"]
        else:
            fade  = min(0.65, 0.25 + (i - top_n) * 0.08)
            color = T["serie_dim"]
            alpha = fade
            fw    = "normal"
            fsize = 9
            fc    = T["texte_dim"]

        ax.barh(n - i - 1, val, color=color, alpha=alpha, height=0.62)
        ax.text(val + max(vals_s) * 0.01, n - i - 1,
                fmt.format(val), va="center", ha="left",
                fontsize=fsize, fontweight=fw, color=fc)
        prefix = {0: "① ", 1: "② ", 2: "③ "}.get(i, "   ")
        ax.text(-max(vals_s) * 0.01, n - i - 1,
                prefix + cat, va="center", ha="right",
                fontsize=fsize, fontweight=fw, color=fc)

    ax.set_xlim(-max(vals_s) * 0.22, max(vals_s) * 1.18)
    ax.set_ylim(-0.6, n - 0.4)
    ax.yaxis.set_visible(False)

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig), ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑤ divergent — graphique de divergence (positif / négatif)
# ══════════════════════════════════════════════════════════════════════════════

def divergent(categories, valeurs,
              titre="", sous_titre="", note="",
              accent_pos=ACCENTS["vert"], accent_neg=ACCENTS["rouge"],
              fmt="{:+.1f}", figsize=None, format=None, background=None):
    """
    Barres divergentes centrées sur zéro — parfait pour les deltas,
    NPS, balance commerciale, évolutions positives/négatives.

    Exemple
    -------
    >>> divergent(
    ...     categories=mois,
    ...     valeurs=[-3.2, +5.1, +8.4, -1.0, +12.3, -0.5],
    ...     titre="Variation mensuelle du NPS",
    ...     fmt="{:+.1f} pts"
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    fig, ax = _init_ax(figsize, background)
    ax.grid(axis="x", color=T["grille"], lw=0.7, ls="--", alpha=0.8)
    ax.grid(axis="y", visible=False)

    y_pos = np.arange(len(categories))
    for i, (cat, val) in enumerate(zip(categories, valeurs)):
        color = accent_pos if val >= 0 else accent_neg
        ax.barh(i, val, color=color, alpha=0.85, height=0.55)
        offset = max(abs(v) for v in valeurs) * 0.02
        ha = "left" if val >= 0 else "right"
        x_pos = val + (offset if val >= 0 else -offset)
        ax.text(x_pos, i, fmt.format(val),
                va="center", ha=ha, fontsize=9.5,
                fontweight="bold", color=T["texte"])

    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, color=T["texte_dim"], fontsize=10)
    ax.axvline(0, color=T["texte_dim"], lw=1.0, zorder=5)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(T["grille"])
    ax.xaxis.set_visible(False)

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig), ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑥ bullet_chart — KPI vs objectif (remplace les jauges)
# ══════════════════════════════════════════════════════════════════════════════

def bullet_chart(kpis: list,
                 titre="", sous_titre="", note="",
                 accent=ACCENT_DEFAUT, figsize=None, format=None, background=None):
    """
    Bullet charts (Stephen Few) — représentation compacte et honnête
    d'un KPI face à son objectif et à ses plages de performance.

    Parameters
    ----------
    kpis : liste de dicts ::
        {
            "nom"      : "Taux de conversion",
            "valeur"   : 4.7,          # valeur actuelle
            "objectif" : 5.0,          # ligne de cible
            "plages"   : [3, 4, 6],    # seuils Mauvais / Moyen / Bon
            "fmt"      : "{:.1f}%"     # format d'affichage (optionnel)
        }

    Exemple
    -------
    >>> bullet_chart([
    ...     {"nom": "Conversion", "valeur": 4.7, "objectif": 5.0,
    ...      "plages": [2, 4, 6], "fmt": "{:.1f}%"},
    ...     {"nom": "Panier moyen", "valeur": 68, "objectif": 75,
    ...      "plages": [40, 60, 90], "fmt": "{:.0f}€"},
    ... ], titre="Performance commerciale vs objectifs Q4")
    """
    n = len(kpis)
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    fig, axes = plt.subplots(n, 1, figsize=figsize or (10, n * 1.4 + 0.8))
    _bg._appliquer_background(fig, None, background)
    if n == 1:
        axes = [axes]

    plage_colors = [T["grille"], T["serie_dim"], T["fond_neutre"]]
    label_zone = 0.32   # fraction de xmax réservée à gauche pour le nom du KPI

    for ax, kpi in zip(axes, kpis):
        _bg._appliquer_background(fig, ax, background)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        plages = sorted(kpi["plages"])
        val    = kpi["valeur"]
        obj    = kpi["objectif"]
        fmt    = kpi.get("fmt", "{:.1f}")
        xmax   = plages[-1] * 1.05
        x_orig = -xmax * label_zone          # origine gauche : zone label

        limites = [0] + plages
        for j in range(len(limites) - 1):
            ax.barh(0, limites[j+1] - limites[j], left=limites[j],
                    height=0.7, color=plage_colors[j % len(plage_colors)])

        ax.barh(0, val, height=0.36, color=accent, alpha=0.92, zorder=3)
        ax.plot([obj, obj], [-0.28, 0.28], color=T["texte"], lw=3.5, zorder=4)

        # Nom du KPI en coordonnées données — plus de transform, tight_layout comprend
        ax.text(-xmax * 0.02, 0, kpi["nom"],
                ha="right", va="center", fontsize=10,
                fontweight="bold", color=T["texte"])

        ax.text(val, 0.42, fmt.format(val),
                ha="center", va="bottom", fontsize=9.5,
                fontweight="bold", color=accent)

        ax.text(obj, -0.44, f"Obj: {fmt.format(obj)}",
                ha="center", va="top", fontsize=8.5, color=T["texte_dim"])

        ax.set_xlim(x_orig, xmax * 1.05)    # zone négative pour le label
        ax.set_ylim(-0.6, 0.7)

    if titre:
        axes[0].set_title(titre, fontsize=13, fontweight="bold",
                          color=T["texte"], pad=14, loc="left")
    if sous_titre:
        axes[0].annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                         xytext=(0, 28), textcoords="offset points",
                         fontsize=9.5, color=T["texte_dim"], annotation_clip=False)
    if note:
        fig.text(0.01, 0.01, note, fontsize=8, color=T["serie_dim"],
                 style="italic", transform=fig.transFigure)

    fig.tight_layout(h_pad=0.4)
    return fig, axes


# ══════════════════════════════════════════════════════════════════════════════
# ⑦ Annotations narratives — à superposer sur n'importe quel graphique
# ══════════════════════════════════════════════════════════════════════════════

def annoter_zone(ax, x_debut, x_fin, label="",
                 couleur=ACCENT_DEFAUT, alpha=0.10, y_label=0.95):
    """
    Zone colorée en surbrillance (rectangle vertical) avec étiquette.
    À appeler APRÈS la création du graphique sur l'ax retourné.

    Exemple
    -------
    >>> fig, ax = ligne_focus(...)
    >>> annoter_zone(ax, x_debut="Mar", x_fin="Mai", label="Période COVID",
    ...              couleur=ACCENTS["rouge"])
    """
    T = _t()
    ax.axvspan(x_debut, x_fin, alpha=alpha, color=couleur, zorder=1)
    ymin, ymax = ax.get_ylim()
    y = ymin + (ymax - ymin) * y_label
    x_mid = (x_debut + x_fin) / 2 if isinstance(x_debut, (int, float)) else x_debut
    if label:
        ax.text(x_mid, y, label, ha="center", va="top",
                fontsize=9, color=couleur, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc=T["bg"], ec=couleur, alpha=0.85))


def annoter_seuil(ax, y, label="", couleur=ACCENTS["rouge"],
                  cote="droite", style="--"):
    """
    Ligne horizontale de seuil / objectif / référence avec étiquette.

    Exemple
    -------
    >>> annoter_seuil(ax, y=100, label="Objectif 100k", couleur=ACCENTS["vert"])
    """
    T = _t()
    ax.axhline(y, color=couleur, lw=1.6, linestyle=style, alpha=0.85, zorder=3)
    xmin, xmax = ax.get_xlim()
    x_pos = xmax if cote == "droite" else xmin
    ha    = "right" if cote == "droite" else "left"
    if label:
        ax.text(x_pos, y, f"  {label}  ", ha=ha, va="bottom",
                fontsize=9, color=couleur, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc=T["bg"], ec=couleur, alpha=0.9))


def annoter_delta(ax, x, y_debut, y_fin, label="",
                  couleur=None, fmt="{:+.0f}"):
    """
    Accolade verticale entre deux points avec la variation annotée.
    Utile pour montrer une hausse/baisse sur un graphique en lignes.

    Exemple
    -------
    >>> annoter_delta(ax, x=5, y_debut=42, y_fin=71, label="×1.7", couleur=ACCENTS["vert"])
    """
    T = _t()
    delta  = y_fin - y_debut
    if couleur is None:
        couleur = ACCENTS["vert"] if delta >= 0 else ACCENTS["rouge"]

    ax.annotate("", xy=(x, y_fin), xytext=(x, y_debut),
                arrowprops=dict(arrowstyle="<->", color=couleur, lw=1.8))
    mid = (y_debut + y_fin) / 2
    txt = label if label else fmt.format(delta)
    ax.text(x, mid, f" {txt}", va="center", ha="left",
            fontsize=9.5, color=couleur, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", fc=T["bg"], ec=couleur, alpha=0.85))


def annoter_point(ax, x, y, label, couleur=ACCENT_DEFAUT,
                  direction="haut", offset=14):
    """
    Annotation pointée sur un point de données (flèche + bulle texte).

    Parameters
    ----------
    direction : "haut" | "bas" | "gauche" | "droite"

    Exemple
    -------
    >>> annoter_point(ax, x=8, y=95, label="Pic historique", couleur=ACCENTS["rouge"])
    """
    T = _t()
    dirs = {
        "haut"   : (0,  offset),
        "bas"    : (0, -offset),
        "gauche" : (-offset*2, 0),
        "droite" : ( offset*2, 0),
    }
    dx, dy = dirs.get(direction, (0, offset))
    ax.annotate(
        label, xy=(x, y), xytext=(dx, dy),
        textcoords="offset points",
        fontsize=9.5, color=couleur, fontweight="bold",
        ha="center", va="bottom" if dy > 0 else "top",
        arrowprops=dict(arrowstyle="-|>", color=couleur,
                        lw=1.5, connectionstyle="arc3,rad=0.15"),
        bbox=dict(boxstyle="round,pad=0.35", fc=T["bg"], ec=couleur,
                  alpha=0.92, linewidth=1.4)
    )
    ax.scatter([x], [y], color=couleur, s=55, zorder=5, edgecolors=T["bg"], linewidths=1.5)


# ══════════════════════════════════════════════════════════════════════════════
# ⑧ barres_connectees — tendance temporelle par entité avec deltas en bulles
# ══════════════════════════════════════════════════════════════════════════════

def barres_connectees(categories: list, periodes: list, valeurs: list,
                      couleurs: list = None, groupes: dict = None,
                      afficher_delta=True, fmt_delta="{:+.0f}", fmt_valeur="{:.0f}",
                      accent_pos=None, accent_neg=None,
                      titre="", sous_titre="", note="", figsize=None, format=None,
                      background=None):
    """
    Pour chaque entité, affiche N barres chronologiques (une par période)
    reliées par une ligne suivant le sommet des barres. Les variations entre
    périodes sont annotées dans des bulles colorées (delta). Montre à la fois
    les valeurs absolues et leur évolution.

    Parameters
    ----------
    categories : noms des entités (ex: ["IA", "Cloud", ...])
    periodes   : noms des périodes (ex: ["2022", "2023", "2024"])
    valeurs    : liste de listes — valeurs[i][j] = entité i, période j
    couleurs   : une couleur par entité (défaut : PALETTE de beau_graphique)
    groupes    : {"Groupe A": ["IA", "Cloud"], ...} pour une légende groupée

    Exemple
    -------
    >>> barres_connectees(
    ...     categories=["IA", "Cloud & Edge"],
    ...     periodes=["2022", "2023", "2024"],
    ...     valeurs=[[295, 245, 290], [40, 63, 95]],
    ...     titre="Investissements par tendance, 2022–2024 (Mds$)",
    ... )
    """
    import beau_graphique as bg
    if couleurs is None:
        couleurs = bg._palette_pour(categories)
    accent_pos = accent_pos or ACCENTS["vert"]
    accent_neg = accent_neg or ACCENTS["rouge"]

    T = _t()
    n_cat = len(categories)
    n_per = len(periodes)
    largeur = 0.55
    pas_barre = largeur + 0.15
    largeur_groupe = n_per * pas_barre
    pas_groupe = largeur_groupe + 1.0

    positions = {(i, j): i * pas_groupe + j * pas_barre
                 for i in range(n_cat) for j in range(n_per)}
    ymax_global = max(max(row) for row in valeurs)
    figsize = bg._resoudre_figsize(figsize, format)
    fig, ax = _init_ax(figsize or (max(10, n_cat * n_per * 0.9), 6), background)

    for i, cat in enumerate(categories):
        couleur = couleurs[i % len(couleurs)]
        xs = [positions[(i, j)] for j in range(n_per)]
        sommets = list(valeurs[i])

        for x, val in zip(xs, sommets):
            ax.bar(x, val, width=largeur, color=couleur, alpha=0.88, zorder=3)
            ax.text(x, val + ymax_global * 0.02, fmt_valeur.format(val),
                    ha="center", va="bottom", fontsize=8.5, color=T["texte"])

        ax.plot(xs, sommets, color=couleur, lw=1.2, alpha=0.7, zorder=2)

        if afficher_delta:
            for j in range(n_per - 1):
                x_mid = (xs[j] + xs[j + 1]) / 2
                y_mid = (sommets[j] + sommets[j + 1]) / 2
                delta = sommets[j + 1] - sommets[j]
                couleur_bulle = accent_pos if delta >= 0 else accent_neg
                ax.scatter([x_mid], [y_mid], s=600, color=couleur_bulle, zorder=5)
                ax.text(x_mid, y_mid, fmt_delta.format(delta),
                        ha="center", va="center", fontsize=8.5,
                        fontweight="bold", color="white", zorder=6)

        centre = sum(xs) / len(xs)
        ax.text(centre, -ymax_global * 0.08, cat, ha="center", va="top",
                fontsize=9.5, color=T["texte_dim"], fontweight="bold")

    all_x = [positions[(i, j)] for i in range(n_cat) for j in range(n_per)]
    all_labels = [periodes[j] for i in range(n_cat) for j in range(n_per)]
    ax.set_xticks(all_x)
    ax.set_xticklabels(all_labels, fontsize=8, color=T["texte_dim"])

    ax.set_xlim(-0.6, max(positions.values()) + largeur + 0.6)
    ax.set_ylim(-ymax_global * 0.22, ymax_global * 1.25)
    ax.yaxis.set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(T["grille"])
    ax.grid(visible=False)

    if groupes:
        handles = []
        for nom_groupe, membres in groupes.items():
            idx = categories.index(membres[0])
            handles.append(mpatches.Patch(color=couleurs[idx % len(couleurs)], label=nom_groupe))
    else:
        handles = [mpatches.Patch(color=couleurs[i % len(couleurs)], label=cat)
                  for i, cat in enumerate(categories)]
    ax.legend(handles=handles, loc="upper left", frameon=False,
             fontsize=9, ncol=min(len(handles), 4))

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig), ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑨ cascade — graphique en cascade / waterfall (bridge chart)
# ══════════════════════════════════════════════════════════════════════════════

def cascade(categories, valeurs,
            label_total="Total",
            titre="", sous_titre="", note="",
            accent_pos=None, accent_neg=None, couleur_total=None,
            fmt="{:+.0f}", fmt_total="{:.0f}",
            figsize=None, format=None, background=None, ax=None):
    """Graphique en cascade (waterfall/bridge) — contributions pos/neg cumulées.

    Idéal pour : décomposition P&L, budget variance, évolution de KPI.

    Le premier élément = valeur de départ (absolu).
    Les éléments intermédiaires = deltas (positif ou négatif).
    L'élément portant ``label_total`` = valeur finale (absolu, depuis 0).

    Exemple
    -------
    >>> cascade(
    ...     categories=["Départ", "Nouveaux", "Churn", "Upsell", "Arrivée"],
    ...     valeurs=[1200, 340, -180, 90, 1450],
    ...     label_total="Arrivée",
    ...     titre="MRR : +250 k€ sur le trimestre",
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    accent_pos    = accent_pos    or ACCENTS["vert"]
    accent_neg    = accent_neg    or ACCENTS["rouge"]
    couleur_total = couleur_total or T["texte_dim"]

    n = len(categories)
    external_ax = ax is not None
    fig, ax = _init_ax(figsize or (max(9, n * 1.3), 5.5), background, ax=ax)

    cumuls, hauteurs, couleurs_b = [], [], []
    running = 0.0

    for i, (cat, val) in enumerate(zip(categories, valeurs)):
        is_total = (cat == label_total)
        is_start = (i == 0)
        fval = float(val)
        if is_start or is_total:
            cumuls.append(0)
            hauteurs.append(fval)
            couleurs_b.append(couleur_total)
            if is_start:
                running = fval
        else:
            bottom = running if fval >= 0 else running + fval
            cumuls.append(bottom)
            hauteurs.append(abs(fval))
            couleurs_b.append(accent_pos if fval >= 0 else accent_neg)
            running += fval

    ymax = max(c + h for c, h in zip(cumuls, hauteurs))
    ymin = min(cumuls)

    for i, (cat, h, b, col) in enumerate(zip(categories, hauteurs, cumuls, couleurs_b)):
        ax.bar(i, h, bottom=b, color=col, width=0.55, alpha=0.88, zorder=3)

        is_total = (cat == label_total)
        is_start = (i == 0)
        label_txt = (fmt_total.format(b + h) if (is_total or is_start)
                     else fmt.format(float(valeurs[i])))
        ax.text(i, b + h / 2, label_txt,
                ha="center", va="center", fontsize=9.5, fontweight="bold",
                color="white" if h > (ymax - ymin) * 0.06 else T["texte"])

        if i < n - 1 and not (cat == label_total):
            ax.plot([i + 0.28, i + 0.72], [b + h, b + h],
                    color=T["grille"], lw=0.9, ls="--", zorder=2)

    ax.set_xticks(range(n))
    ax.set_xticklabels(categories, color=T["texte_dim"], fontsize=9.5)
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(min(0, ymin) - (ymax - ymin) * 0.05, ymax * 1.18)
    ax.axhline(0, color=T["grille"], lw=0.8, zorder=1)
    ax.yaxis.set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(T["grille"])
    ax.grid(visible=False)

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig, skip_layout=external_ax), ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑩ pente — slope chart (comparaison 2 périodes, N entités)
# ══════════════════════════════════════════════════════════════════════════════

def pente(categories, valeurs_avant, valeurs_apres,
          label_avant="Période A", label_apres="Période B",
          titre="", sous_titre="", note="",
          accent=ACCENT_DEFAUT, top_n=3,
          fmt="{:.0f}", figsize=None, format=None, background=None, ax=None):
    """Slope chart — compare N entités entre deux périodes.

    Les entités à variation absolue la plus forte reçoivent l'accent.
    Idéal pour : classements avant/après, évolutions comparées.

    Exemple
    -------
    >>> pente(
    ...     categories=["France", "Allemagne", "Espagne", "Italie"],
    ...     valeurs_avant=[72, 68, 61, 55],
    ...     valeurs_apres=[78, 65, 70, 52],
    ...     label_avant="2022", label_apres="2024",
    ...     titre="L'Espagne gagne 9 pts — plus forte progression",
    ...     top_n=1, accent=ACCENTS["orange"]
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    n = len(categories)

    deltas  = [abs(b - a) for a, b in zip(valeurs_avant, valeurs_apres)]
    top_idx = set(np.argsort(deltas)[-top_n:])

    external_ax = ax is not None
    fig, ax = _init_ax(figsize or (7, max(5, n * 0.85)), background, ax=ax)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(visible=False)
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)

    x0, x1 = 0.28, 0.72
    all_vals = list(valeurs_avant) + list(valeurs_apres)
    vmin, vmax_ = min(all_vals), max(all_vals)
    span = vmax_ - vmin or 1

    def yn(v):
        return (v - vmin) / span * 0.80 + 0.08

    for i, (cat, va, vb) in enumerate(zip(categories, valeurs_avant, valeurs_apres)):
        is_f = i in top_idx
        col  = accent if is_f else T["serie_dim"]
        alph = 1.0 if is_f else 0.40
        ya, yb = yn(va), yn(vb)
        ax.plot([x0, x1], [ya, yb], color=col, lw=2.5 if is_f else 1.0,
                alpha=alph, zorder=3, transform=ax.transAxes)
        ax.scatter([x0, x1], [ya, yb], color=col, s=45 if is_f else 22,
                   alpha=alph, zorder=4, edgecolors=T["bg"], linewidths=1.0,
                   transform=ax.transAxes)
        ax.text(x0 - 0.03, ya, f"{fmt.format(va)}  {cat}",
                ha="right", va="center",
                fontsize=9.5 if is_f else 8.5,
                fontweight="bold" if is_f else "normal",
                color=col if is_f else T["texte_dim"],
                transform=ax.transAxes)
        arrow = "▲" if vb > va else ("▼" if vb < va else "–")
        col_arr = (ACCENTS["vert"] if vb > va else
                   ACCENTS["rouge"] if vb < va else T["texte_dim"])
        ax.text(x1 + 0.03, yb, f"{arrow} {fmt.format(vb)}",
                ha="left", va="center",
                fontsize=9.5 if is_f else 8.5,
                fontweight="bold" if is_f else "normal",
                color=col_arr if is_f else T["texte_dim"],
                transform=ax.transAxes)

    for xv, lbl in [(x0, label_avant), (x1, label_apres)]:
        ax.text(xv, 0.965, lbl, ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=T["texte"],
                transform=ax.transAxes)
        ax.axvline(xv, color=T["grille"], lw=0.7, ymin=0.04, ymax=0.93)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig, skip_layout=external_ax), ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑪ nuage_annote — scatter annoté avec bulles et quadrants
# ══════════════════════════════════════════════════════════════════════════════

def nuage_annote(x, y, labels,
                 tailles=None, couleurs=None, focus=None,
                 titre="", sous_titre="", note="",
                 label_x="", label_y="",
                 accent=ACCENT_DEFAUT,
                 quadrants=False, quadrant_labels=("", "", "", ""),
                 zones_colorees=False, zone_couleurs=None,
                 figsize=None, format=None, background=None, ax=None):
    """Scatter annoté — chaque point labellisé, les points en focus = accent.

    Bulles optionnelles (tailles) et quadrants de positionnement.

    Parameters
    ----------
    tailles : liste de float — rayon visuel des bulles (optionnel)
    focus   : int ou liste d'ints — indices des points à mettre en valeur
    quadrants : True → lignes médianes + libellés de quadrant
    quadrant_labels : (haut-gauche, haut-droite, bas-gauche, bas-droite)
    zones_colorees : True → remplit chacun des 4 quadrants d'un rectangle
                    translucide (nécessite ``quadrants=True`` — ignoré
                    silencieusement sinon). Utile pour des matrices de
                    priorisation métier (risque/opportunité, type BCG) où
                    chaque quadrant a un sens propre à faire ressortir
                    visuellement, pas seulement suggéré par des lignes.
    zone_couleurs : tuple de 4 couleurs hex, même ordre que
                    ``quadrant_labels``. ``None`` (défaut) → 4 couleurs de
                    la palette active, sans sens métier présupposé —
                    personnalisez pour un vrai code couleur (ex. rouge pour
                    une zone à risque, vert pour une opportunité).

    Exemple
    -------
    >>> nuage_annote(
    ...     x=[22, 45, 78, 31, 60],
    ...     y=[3.2, 1.8, 4.5, 2.1, 3.8],
    ...     labels=["A", "B", "C", "D", "E"],
    ...     tailles=[100, 200, 500, 80, 320],
    ...     focus=2,
    ...     quadrants=True,
    ...     quadrant_labels=("Faible/Fort", "Fort/Fort",
    ...                       "Faible/Faible", "Fort/Faible"),
    ...     zones_colorees=True,
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()
    external_ax = ax is not None
    fig, ax = _init_ax(figsize or (10, 6.5), background, ax=ax)

    if focus is None:
        focus = []
    elif isinstance(focus, int):
        focus = [focus]

    n = len(x)
    if tailles is None:
        s_norm = [120] * n
    else:
        s_min, s_max = min(tailles), max(tailles)
        span = s_max - s_min or 1
        s_norm = [80 + (s - s_min) / span * 500 for s in tailles]

    if couleurs is None:
        couleurs = [accent if i in focus else T["serie_dim"] for i in range(n)]

    for i, (xi, yi, lab, sz, col) in enumerate(
            zip(x, y, labels, s_norm, couleurs)):
        is_f = i in focus
        ax.scatter(xi, yi, s=sz, color=col, alpha=0.88 if is_f else 0.40,
                   edgecolors=T["bg"], linewidths=1.2, zorder=4)
        ax.annotate(lab, xy=(xi, yi), xytext=(6, 6),
                    textcoords="offset points",
                    fontsize=10 if is_f else 8.5,
                    fontweight="bold" if is_f else "normal",
                    color=T["texte"] if is_f else T["texte_dim"],
                    zorder=5)

    if quadrants:
        xm, ym = np.median(x), np.median(y)
        ax.axvline(xm, color=T["grille"], lw=0.9, ls="--", alpha=0.7, zorder=1)
        ax.axhline(ym, color=T["grille"], lw=0.9, ls="--", alpha=0.7, zorder=1)
        x0_, x1_ = ax.get_xlim()
        y0_, y1_ = ax.get_ylim()

        if zones_colorees:
            zc = zone_couleurs or _bg._palette_pour(["q0", "q1", "q2", "q3"])
            for (zx0, zx1, zy0, zy1), couleur in zip(
                [(x0_, xm, ym, y1_), (xm, x1_, ym, y1_),
                 (x0_, xm, y0_, ym), (xm, x1_, y0_, ym)],
                zc,
            ):
                ax.add_patch(mpatches.Rectangle(
                    (zx0, zy0), zx1 - zx0, zy1 - zy0,
                    facecolor=couleur, edgecolor="none",
                    alpha=0.10, zorder=0.5,
                ))

        ql = quadrant_labels
        for txt, qx, qy in [
            (ql[0], (x0_ + xm)/2, ym + (y1_-ym)*0.85),
            (ql[1], (xm + x1_)/2, ym + (y1_-ym)*0.85),
            (ql[2], (x0_ + xm)/2, y0_ + (ym-y0_)*0.15),
            (ql[3], (xm + x1_)/2, y0_ + (ym-y0_)*0.15),
        ]:
            if txt:
                ax.text(qx, qy, txt, ha="center", va="center",
                        fontsize=9, color=T["texte_dim"],
                        fontstyle="italic", alpha=0.75)

    ax.set_xlabel(label_x, fontsize=10, color=T["texte_dim"], labelpad=8)
    ax.set_ylabel(label_y, fontsize=10, color=T["texte_dim"], labelpad=8)

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig, skip_layout=external_ax), ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑫ mekko — Marimekko chart (composition empilée × poids de colonne)
# ══════════════════════════════════════════════════════════════════════════════

def mekko(categories, poids, segments, focus=None,
          titre="", sous_titre="", note="",
          accent=ACCENT_DEFAUT, fmt_poids="{:.0f}", fmt_segment="{:.0f}%",
          figsize=None, format=None, background=None, ax=None):
    """Marimekko chart — composition empilée (hauteur) × poids de colonne (largeur).

    Chaque colonne représente une catégorie dont la largeur est proportionnelle
    à son poids (ex : taille de marché) ; à l'intérieur, les segments empilés
    montrent une composition normalisée à 100 % (ex : part de chaque acteur).
    Permet de lire simultanément deux dimensions : combien pèse la catégorie,
    et comment elle se décompose.

    Quand l'utiliser
    -----------------
    Comparer la composition de plusieurs catégories ET leur importance
    relative en une seule figure (parts de marché par région où chaque région
    a une taille différente, mix produit par segment de clientèle...).

    Ne pas utiliser
    ----------------
    Si toutes les catégories ont le même poids — un simple
    ``barres_groupees(empile=True, normalise=True)`` suffit et évite la
    complexité de lecture d'une largeur variable.

    Parameters
    ----------
    categories  : noms des colonnes.
    poids       : poids de chaque colonne (largeur) — valeurs strictement
                  positives, ex: taille de marché.
    segments    : dict ``{"nom_segment": [val_cat1, val_cat2, ...]}`` — une
                  valeur par catégorie, empilée verticalement et normalisée
                  automatiquement à 100 % par colonne (c'est la définition
                  même d'un Mekko — sans normalisation, les colonnes ne
                  seraient plus comparables entre elles).
    focus       : nom de segment (ou liste) mis en accent — les autres
                  passent en gris. ``None`` (défaut) → chaque segment reçoit
                  une couleur distincte de la palette.
    accent      : couleur d'accent quand ``focus`` est utilisé.
    fmt_poids   : format du poids affiché sous chaque colonne.
    fmt_segment : format du pourcentage affiché dans chaque segment (affiché
                  seulement si le segment est assez grand pour rester lisible).

    Returns
    -------
    (fig, ax)

    Exemple
    -------
    >>> mekko(
    ...     categories=["Littoral", "Centre", "Ouest"],
    ...     poids=[420, 260, 180],
    ...     segments={
    ...         "Orange": [45, 38, 30],
    ...         "MTN":    [40, 42, 48],
    ...         "Camtel": [15, 20, 22],
    ...     },
    ...     focus="Orange",
    ...     titre="Orange domine le Littoral mais recule à l'Ouest",
    ... )
    """
    import beau_graphique as _bg
    figsize = _bg._resoudre_figsize(figsize, format)
    T = _t()

    n = len(categories)
    if len(poids) != n:
        raise ValueError(
            f"mekko() : 'categories' ({n}) et 'poids' ({len(poids)}) doivent "
            f"avoir la même longueur."
        )
    if any(p <= 0 for p in poids):
        raise ValueError("mekko() : tous les poids doivent être strictement positifs.")
    if not segments:
        raise ValueError("mekko() : 'segments' est vide.")
    for nom, vals in segments.items():
        if len(vals) != n:
            raise ValueError(
                f"mekko() : le segment '{nom}' a {len(vals)} valeurs, "
                f"attendu {n} (autant que 'categories')."
            )
        if any(v < 0 for v in vals):
            raise ValueError(f"mekko() : le segment '{nom}' contient une valeur négative.")

    totaux_col = [sum(segments[s][i] for s in segments) for i in range(n)]
    for i, t in enumerate(totaux_col):
        if t <= 0:
            raise ValueError(
                f"mekko() : la catégorie '{categories[i]}' a une somme de "
                f"segments nulle — impossible à normaliser."
            )

    noms_segments = list(segments.keys())
    focus_liste = []
    if focus is not None:
        focus_liste = [focus] if isinstance(focus, str) else list(focus)
        manquants = [f for f in focus_liste if f not in noms_segments]
        if manquants:
            raise ValueError(
                f"mekko() : focus {manquants} absent(s) de 'segments' "
                f"({noms_segments})."
            )
        indices_focus = [noms_segments.index(f) for f in focus_liste]
        couleurs = palette_focus(len(noms_segments), indices_focus, accent)
        alphas = [1.0 if c == accent else 0.55 for c in couleurs]
    else:
        couleurs = _bg._palette_pour(noms_segments)
        alphas = [1.0] * len(noms_segments)

    external_ax = ax is not None
    fig, ax = _init_ax(figsize or (11, 6), background, ax=ax)

    gap = sum(poids) * 0.02
    x_gauche = []
    cursor = 0.0
    for p in poids:
        x_gauche.append(cursor)
        cursor += p + gap
    largeur_totale = cursor - gap

    for i in range(n):
        bottom = 0.0
        for s_idx, nom in enumerate(noms_segments):
            hauteur = segments[nom][i] / totaux_col[i] * 100
            en_focus = nom in focus_liste
            ax.bar(x_gauche[i], hauteur, width=poids[i], bottom=bottom,
                   align="edge", color=couleurs[s_idx], alpha=alphas[s_idx],
                   edgecolor=T["bg"], linewidth=1.5, zorder=3)
            if hauteur > 6 and poids[i] > largeur_totale * 0.04:
                txt_color = T["fond_neutre"] if (focus is None or en_focus) else T["texte_dim"]
                pct_txt = fmt_segment.format(segments[nom][i] / totaux_col[i] * 100)
                # Nom du segment affiché uniquement sur la 1re colonne (ou sur
                # la colonne en focus) — identifie chaque segment une seule
                # fois sans répéter son nom dans chaque cellule.
                texte = f"{nom}\n{pct_txt}" if (i == 0 or en_focus) and hauteur > 10 else pct_txt
                ax.text(x_gauche[i] + poids[i] / 2, bottom + hauteur / 2,
                        texte,
                        ha="center", va="center", fontsize=8.5,
                        fontweight="bold" if en_focus else "normal",
                        color=txt_color, zorder=4, linespacing=1.3)
            bottom += hauteur

        label_cat = f"{categories[i]}\n{fmt_poids.format(poids[i])}"
        ax.text(x_gauche[i] + poids[i] / 2, -3, label_cat,
                ha="center", va="top", fontsize=9, color=T["texte_dim"])

    ax.set_xlim(0, largeur_totale)
    ax.set_ylim(-16, 103)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.grid(visible=False)

    _header(fig, ax, titre, sous_titre, note)
    return _finalize(fig, skip_layout=external_ax), ax

