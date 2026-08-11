"""
beau_graphique_mckinsey.py
===========================
Graphiques McKinsey — extension de beau_graphique.py (module à plat, pas de
sous-paquet). Importe le socle via `import beau_graphique as bg` pour
accéder à PALETTE/_T à chaud (patchés par themes.appliquer()) — jamais via
`from beau_graphique import ...` qui figerait une copie obsolète.

Usage
-----
    import beau_graphique as bg
    from beau_graphique_mckinsey import dot_plot_comparatif, bulle_4d

Ces fonctions sont ré-exportées par beau_graphique/__init__.py — l'import
depuis `beau_graphique` reste inchangé pour l'utilisateur final.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import numpy as np
import textwrap

import beau_graphique as bg


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
    couleur_apres     : Couleur du cercle plein. ``None`` → ``bg.PALETTE[0]``.
    couleur_connecteur: Couleur de la ligne / flèche. ``None`` → ``bg._T["texte_dim"]``.
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
    c_apres = couleur_apres or couleur or bg.PALETTE[0]
    c_conn  = couleur_connecteur or bg._T["texte_dim"]

    # Fond effectif
    if background is None:
        bg_color    = bg._T["bg"]
        transparent = False
    elif background == "transparent":
        bg_color    = bg._T["bg"]
        transparent = True
    else:
        bg_color    = background
        transparent = False

    # Cercle creux : fond identique au background → effet "anneau"
    c_avant = couleur_avant or (bg_color if not transparent else bg._T["fond_neutre"])

    # ── Figure ──────────────────────────────────────────────────────────────
    x_extra = 1.6 if montrer_plage else 0.0
    fig_w   = max(8, n * 2.8 + x_extra)
    fig, ax = plt.subplots(figsize=bg._resoudre_figsize(figsize, format) or (fig_w, 6.5))

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
    ax.tick_params(axis="y", labelcolor=bg._T["texte_dim"], labelsize=9, length=0)

    # Grille horizontale dashed dans la zone données
    ax.yaxis.grid(True, color=bg._T["grille"], lw=0.5, linestyle="--", zorder=0)
    ax.set_axisbelow(True)

    # Ligne séparatrice données / en-têtes
    ax.axhline(y_sep, color=bg._T["grille"], lw=0.8, zorder=1)

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
            ax.axvline(i - 0.5, color=bg._T["grille"], lw=0.5, zorder=0)

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
                fontsize=10, fontweight="bold", color=bg._T["texte"], clip_on=False)

        # En-tête description (optionnelle, plus petite, gris)
        desc = descriptions.get(nom)
        if desc:
            ax.text(i, y_col_desc, textwrap.fill(desc, 18),
                    ha="center", va="bottom", fontsize=8.5,
                    color=bg._T["texte_dim"], linespacing=1.3, clip_on=False)

    # ── Axe X et bords ──────────────────────────────────────────────────────
    x_right = (n - 0.4 + x_extra) if montrer_plage else (n - 0.4)
    ax.set_xlim(-0.6, x_right)
    ax.xaxis.set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(bg._T["grille"])
    ax.spines["bottom"].set_color(bg._T["grille"])

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
              labelcolor=bg._T["texte"],
              handletextpad=0.4, columnspacing=1.0)

    # ── Indicateur gauche : label_plage / sous_titre ─────────────────────────
    # sous_titre et label_plage peuvent tous deux utiliser {vmin}/{vmax}
    def _rendre(s):
        return s.format(vmin=_fv(vmin_eff), vmax=_fv(vmax_eff)) if s else ""

    texte_gauche = _rendre(label_plage) or _rendre(sous_titre)
    if texte_gauche:
        ax.text(-0.55, y_row_top, texte_gauche, ha="left", va="center",
                fontsize=9.5, fontweight="bold",
                color=bg._T["texte"], clip_on=False)

    # ── Indicateur droit : rectangle plage ───────────────────────────────────
    if montrer_plage:
        xi0   = n - 0.4 + 0.4    # bord gauche du rectangle
        xi1   = n - 0.4 + 1.3    # bord droit du rectangle
        xi_m  = (xi0 + xi1) / 2
        rh    = header_h * 0.15  # hauteur en unités données

        rect = mpatches.Rectangle(
            (xi0, y_row_top - rh / 2), xi1 - xi0, rh,
            facecolor="none", edgecolor=bg._T["texte_dim"],
            linewidth=0.9, zorder=5,
        )
        ax.add_patch(rect)

        ax.text(xi0 - 0.07, y_row_top, _fv(vmin_eff),
                ha="right", va="center", fontsize=8, color=bg._T["texte_dim"])
        ax.text(xi1 + 0.07, y_row_top, _fv(vmax_eff),
                ha="left",  va="center", fontsize=8, color=bg._T["texte_dim"])
        ax.text(xi_m, y_row_top - rh * 0.9, "Range shown",
                ha="center", va="top", fontsize=7, color=bg._T["texte_dim"],
                style="italic")

    # ── Titre et note (figure) ────────────────────────────────────────────────
    if titre:
        fig.text(0.01, 0.97, titre, fontsize=14, fontweight="bold",
                 color=bg._T["texte"])
    if note:
        fig.text(0.01, 0.01, note, fontsize=7.5, color=bg._T["texte_dim"],
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
    figsize = bg._resoudre_figsize(figsize, format)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    taille = np.asarray(taille, dtype=float)
    n = len(x)

    niveaux_couleur = niveaux_couleur or sorted(set(couleur_var))
    ncol = len(niveaux_couleur)
    if palette_bulles is None:
        # Interpole la bg.PALETTE active pour couvrir tous les niveaux
        src = bg.PALETTE * ((ncol // len(bg.PALETTE)) + 1)
        palette_bulles = src[:ncol]
    couleur_par_niveau = dict(zip(niveaux_couleur, palette_bulles))
    point_colors = [couleur_par_niveau.get(v, bg._T["serie_dim"]) for v in couleur_var]

    trange = (taille.max() - taille.min()) or 1.0
    tailles_norm = taille_min + (taille - taille.min()) / trange * (taille_max - taille_min)

    fig, ax = bg._new_fig(figsize or (9, 7), background=background)

    if quadrants:
        ax.axhline(quadrant_y, color=bg._T["grille"], lw=1, ls="--", zorder=1)
        ax.axvline(quadrant_x, color=bg._T["grille"], lw=1, ls="--", zorder=1)

    ax.scatter(x, y, s=tailles_norm, color=point_colors, alpha=0.85,
              edgecolor=bg._T["fond_neutre"], linewidth=1.2, zorder=3)

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
                        fontsize=9, color=bg._T["texte"], va="center")

    xmarge = (x.max() - x.min()) * 0.1 or 0.1
    ymarge = (y.max() - y.min()) * 0.1 or 0.1
    ax.set_xlim(x.min() - xmarge, x.max() + xmarge)
    ax.set_ylim(y.min() - ymarge, y.max() + ymarge)

    ax.set_xlabel((xlabel + "  →") if xlabel else "", color=bg._T["texte_dim"], fontsize=10)
    ax.set_ylabel((ylabel + "  ↑") if ylabel else "", color=bg._T["texte_dim"], fontsize=10)
    ax.grid(axis="both", color=bg._T["grille"], lw=0.6, ls="--", alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=0)

    fig.subplots_adjust(right=0.76)

    handles_couleur = [plt.scatter([], [], s=120, color=couleur_par_niveau[niv],
                                    edgecolor=bg._T["fond_neutre"]) for niv in niveaux_couleur]
    leg1 = ax.legend(handles_couleur, [str(niv) for niv in niveaux_couleur],
                     title=label_couleur, loc="upper left", bbox_to_anchor=(1.02, 1.0),
                     frameon=False, fontsize=8.5, title_fontsize=9)
    ax.add_artist(leg1)

    valeurs_ref = sorted(set(np.round(np.linspace(taille.min(), taille.max(), 4)).astype(int).tolist()))
    handles_taille = [plt.scatter([], [], s=taille_min + (v - taille.min()) / trange * (taille_max - taille_min),
                                   color=bg._T["serie_dim"], alpha=0.5, edgecolor=bg._T["texte_dim"])
                      for v in valeurs_ref]
    ax.legend(handles_taille, [str(v) for v in valeurs_ref],
             title=label_taille, loc="lower left", bbox_to_anchor=(1.02, 0.0),
             frameon=False, fontsize=8.5, title_fontsize=9, labelspacing=1.4)

    if titre:
        ax.set_title(titre, fontsize=14, fontweight="bold", color=bg._T["texte"],
                     pad=14, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 26), textcoords="offset points",
                    fontsize=10, color=bg._T["texte_dim"], annotation_clip=False)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color=bg._T["texte_dim"], style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# ⑪ unit_chart — carrés de proportion / ratio (alternative honnête au camembert)
# ══════════════════════════════════════════════════════════════════════════════

def unit_chart(categories: list, valeurs: list, mode="proportion",
                reference: list = None, valeur_max: float = None, couleur=None,
                fmt="{:.0f}", fmt_ratio="{:.1f}×", taille_carre=1.0,
                titre="", sous_titre="", note="", figsize=None, format=None,
                background=None):
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
    couleur = couleur or bg.PALETTE[0]
    figsize = bg._resoudre_figsize(figsize, format)
    n = len(categories)
    fig, ax = plt.subplots(figsize=figsize or (n * 1.7, 4.5))
    bg._appliquer_background(fig, ax, background)

    espacement = taille_carre * 1.7
    positions = [i * espacement for i in range(n)]
    sommets = []

    if mode == "proportion":
        vmax = valeur_max or max(valeurs)
        for x0, cat, val in zip(positions, categories, valeurs):
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, taille_carre,
                                            edgecolor=bg._T["serie_dim"], facecolor="none", lw=1.5, zorder=2))
            h = (val / vmax) * taille_carre if vmax else 0
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, h,
                                            facecolor=couleur, edgecolor="none",
                                            alpha=0.9, zorder=3))
            couleur_texte = "white" if h > taille_carre * 0.15 else couleur
            ax.text(x0 + taille_carre * 0.08, taille_carre * 0.06, fmt.format(val),
                    fontsize=11, fontweight="bold", color=couleur_texte,
                    ha="left", va="bottom", zorder=4)
            ax.text(x0 + taille_carre / 2, -taille_carre * 0.12, cat,
                    fontsize=9.5, color=bg._T["texte_dim"], ha="center", va="top")
            sommets.append(taille_carre)
    else:  # mode == "ratio"
        if reference is not None:
            ratios = [v / r if r else 0 for v, r in zip(valeurs, reference)]
        else:
            ratios = valeurs
        for x0, cat, ratio in zip(positions, categories, ratios):
            cx, cy = x0 + taille_carre / 2, taille_carre / 2
            ax.add_patch(mpatches.Rectangle((x0, 0), taille_carre, taille_carre,
                                            edgecolor=bg._T["serie_dim"], facecolor="none", lw=1.5, zorder=2))
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
                    fontsize=9.5, color=bg._T["texte_dim"], ha="center", va="top")
            sommets.append(sommet + taille_carre * 0.32)

    ax.set_xlim(-taille_carre * 0.3, positions[-1] + taille_carre * 1.3)
    ax.set_ylim(-taille_carre * 0.4, max(sommets) * 1.1)
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    if titre:
        ax.set_title(titre, fontsize=14, fontweight="bold", color=bg._T["texte"],
                     pad=18, loc="left")
    if sous_titre:
        ax.annotate(sous_titre, xy=(0, 1), xycoords="axes fraction",
                    xytext=(0, 8), textcoords="offset points",
                    fontsize=10, color=bg._T["texte_dim"], annotation_clip=False)
    if note:
        fig.text(0.01, -0.02, note, fontsize=8, color=bg._T["texte_dim"], style="italic")

    return fig, ax


# ══════════════════════════════════════════════════════════════════════════════
# Barres temporelles (style McKinsey — polygone continu + badge cumulatif)
# ══════════════════════════════════════════════════════════════════════════════

def _dessiner_barre_tendance(ax, valeurs, deltas, cumul, couleur, nom=""):
    """Dessine un mini-graphique 'barres temporelles' : polygone continu
    sur N années avec pentes de transition, labels YoY et badge cumulatif."""
    bw   = 0.62   # largeur de barre (en unités x)
    gap  = 0.38   # espace inter-barres (crée la pente diagonale)
    step = bw + gap  # 1.0

    v = [float(x) for x in valeurs]
    n = len(v)
    vmax = max(v) if max(v) > 0 else 1.0

    # ── Polygone principal ──────────────────────────────────────────────────
    # Profil supérieur : [x0, x0+bw, x1, x1+bw, x2, x2+bw, ...]
    # La pente entre bar_i et bar_{i+1} est naturelle (ligne de (xi+bw, vi)
    # à (xi+1, vi+1)).
    xs_top, ys_top = [], []
    for i in range(n):
        x0 = i * step
        xs_top += [x0, x0 + bw]
        ys_top += [v[i], v[i]]

    poly_x = xs_top + [xs_top[-1], xs_top[0]]
    poly_y = ys_top + [0.0, 0.0]
    verts  = list(zip(poly_x, poly_y))

    ax.add_patch(
        mpatches.Polygon(verts, closed=True,
                         facecolor=couleur, edgecolor="none", zorder=2)
    )

    # ── Séparateurs blancs aux transitions bar ↔ pente ─────────────────────
    for i in range(n - 1):
        x_end = i * step + bw
        x_nxt = (i + 1) * step
        ax.plot([x_end, x_end], [0, v[i]],
                color="white", linewidth=1.4, zorder=4, solid_capstyle="butt")
        ax.plot([x_nxt, x_nxt], [0, v[i + 1]],
                color="white", linewidth=1.4, zorder=4, solid_capstyle="butt")

    # ── Labels YoY dans la zone de pente ────────────────────────────────────
    for i, d in enumerate(deltas):
        x_lbl = i * step + bw + gap / 2
        y_lbl = (v[i] + v[i + 1]) / 2
        signe = "+" if float(d) >= 0 else ""
        label_yoy = f"{signe}{d}"
        # Taille réduite pour les grands nombres (ex: +1562)
        fs_yoy = 5.5 if len(label_yoy) >= 5 else 6.8
        ax.text(x_lbl, y_lbl, label_yoy,
                ha="center", va="center",
                fontsize=fs_yoy, fontweight="bold", color="white", zorder=5,
                bbox=dict(boxstyle="round,pad=0.15",
                          facecolor=couleur, edgecolor="none", alpha=0.6))

    # ── Badge cumulatif ─────────────────────────────────────────────────────
    # On utilise ax.transAxes pour que le cercle soit TOUJOURS rond,
    # quelle que soit l'échelle des données (évite l'effet ellipse).
    peak_i  = int(np.argmax(v))
    xmax    = (n - 1) * step + bw
    # Position en fraction d'axe
    x_badge_ax = (peak_i * step + bw / 2) / xmax

    signe = "+" if float(cumul) >= 0 else ""
    label = f"{signe}{cumul}"
    fs = 5.5 if abs(float(cumul)) >= 1000 else (6.0 if abs(float(cumul)) >= 100 else 6.8)

    ax.text(
        x_badge_ax, 0.87, label,
        transform=ax.transAxes,
        ha="center", va="center",
        fontsize=fs, fontweight="bold", color="white",
        bbox=dict(
            boxstyle="circle,pad=0.35",
            facecolor=couleur,
            edgecolor="white",
            linewidth=0.8,
        ),
        zorder=6, clip_on=False,
    )

    # ── Limites et axes ─────────────────────────────────────────────────────
    ax.set_xlim(-0.06, xmax + 0.06)
    ax.set_ylim(0, vmax * 1.48)   # headroom fixe pour le badge (48 %)

    ax.grid(False)   # pas de grille — le polygone suffit comme repère visuel
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=3, integer=True))
    ax.tick_params(axis="y", labelsize=6.2, colors=bg._T["texte_dim"], length=2, pad=2)
    ax.tick_params(axis="x", bottom=False, labelbottom=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_color(bg._T["grille"])
    ax.spines["left"].set_linewidth(0.6)

    ax.axhline(0, color=bg._T["grille"], linewidth=0.6, zorder=1)

    if nom:
        wrapped = "\n".join(textwrap.wrap(nom, width=18))
        ax.set_xlabel(wrapped, fontsize=7.5, color=bg._T["texte"], labelpad=5)


def tendances_grille(
    items,
    ncols=4,
    titre="",
    sous_titre="",
    note="",
    hspace=0.75,
    wspace=0.30,
    figsize=None,
    format=None,
    background=None,
    **_extra,
):
    """
    Grille de mini-graphiques 'barres temporelles' — style rapport McKinsey.

    Chaque item représente une catégorie avec des valeurs sur N années
    (typiquement 3 : 2022, 2023, 2024). Le graphique produit un polygone
    continu : barres plates + pentes de transition + badge cumulatif.

    Parameters
    ----------
    items : liste de dicts. Chaque dict contient :

        - ``"nom"``     : str — libellé affiché sous le graphique
        - ``"valeurs"`` : list[float] — valeurs absolues par année
                          ex: ``[95, 79, 117]``
        - ``"deltas"``  : list[float] — variations YoY en %
                          ex: ``[-17, 48]``  (signe +/- automatique)
        - ``"cumul"``   : float — variation cumulée sur toute la période
                          ex: ``22``
        - ``"couleur"`` : str hex — couleur du graphique (optionnel,
                          bg.PALETTE par défaut)

    ncols      : colonnes dans la grille (défaut 4)
    hspace     : espace vertical entre graphiques, 0–1 (défaut 0.75)
    wspace     : espace horizontal entre graphiques, 0–1 (défaut 0.30)
    titre      : titre global de la figure
    sous_titre : ligne descriptive (unité, période…)
    note       : note de bas de page (source…)

    Returns
    -------
    ``(fig, axes)`` — axes est la liste des axes dans l'ordre des items.

    Exemple
    -------
    >>> items = [
    ...     {"nom": "Intelligence artificielle",
    ...      "valeurs": [95, 79, 117], "deltas": [-17, 48], "cumul": 22,
    ...      "couleur": "#1B2A8A"},
    ...     {"nom": "Cloud et edge computing",
    ...      "valeurs": [26, 41, 61],  "deltas": [58, 50],  "cumul": 138,
    ...      "couleur": "#4CC9F0"},
    ... ]
    >>> fig, axes = tendances_grille(
    ...     items, ncols=2,
    ...     titre="Investissements par tendance technologique",
    ...     sous_titre="Equity, 2022–24, Mds $",
    ... )
    """
    n = len(items)
    if n == 0:
        raise ValueError("tendances_grille : la liste 'items' est vide.")

    nrows    = (n + ncols - 1) // ncols
    fig_size = bg._resoudre_figsize(figsize, format) or (ncols * 3.4, nrows * 3.6)

    fig = plt.figure(figsize=fig_size)
    bg._appliquer_background(fig, None, background)

    top_margin = 0.93 if (titre or sous_titre) else 0.97

    gs = fig.add_gridspec(
        nrows, ncols,
        hspace=hspace, wspace=wspace,
        left=0.06, right=0.97,
        top=top_margin, bottom=0.07,
    )

    axes = []
    for idx, item in enumerate(items):
        row, col = divmod(idx, ncols)
        ax = fig.add_subplot(gs[row, col])
        bg._appliquer_background(fig, ax, background)
        axes.append(ax)

        _dessiner_barre_tendance(
            ax,
            valeurs=item["valeurs"],
            deltas=item.get("deltas", []),
            cumul=item.get("cumul", 0),
            couleur=item.get("couleur", bg.PALETTE[idx % len(bg.PALETTE)]),
            nom=item.get("nom", ""),
        )

    # Masquer les cellules vides
    for idx in range(n, nrows * ncols):
        row, col = divmod(idx, ncols)
        ax_empty = fig.add_subplot(gs[row, col])
        ax_empty.set_visible(False)

    # ── Textes globaux ───────────────────────────────────────────────────────
    if titre:
        fig.text(0.03, 0.98, titre,
                 fontsize=12, fontweight="bold", color=bg._T["texte"],
                 ha="left", va="top")
    if sous_titre:
        fig.text(0.03, 0.955, sous_titre,
                 fontsize=8.5, color=bg._T["texte_dim"],
                 ha="left", va="top")
    if note:
        fig.text(0.03, 0.01, note,
                 fontsize=7, color=bg._T["texte_dim"],
                 ha="left", va="bottom", style="italic")

    return fig, axes


# ══════════════════════════════════════════════════════════════════════════════
# Barres temporelles — style McKinsey vrai (axes partagés, point 2023)
# ══════════════════════════════════════════════════════════════════════════════

def _lum(couleur):
    """Luminance perceptuelle (0=noir, 1=blanc). Accepte hex ou nom CSS."""
    try:
        import matplotlib.colors as mcolors
        r, g, b, _ = mcolors.to_rgba(couleur)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    except Exception:
        return 0.5  # valeur neutre si couleur non parsable


def _dessiner_tendance_cat(ax, x_base, valeurs, deltas, cumul, couleur,
                            cat_w, ymax_ax, nom=""):
    """Dessine UNE catégorie — style McKinsey exact.

    Polygone 5 sommets (pas de plateau horizontal) :
        (xl,0) → (xl,h0) → (xm,h1) → (xr,h2) → (xr,0)
    Cercles ouverts aux 3 angles (2022, 2023, 2024).
    Séparateur blanc vertical à xm, de y=0 à y=h1.
    """
    h0, h1, h2 = float(valeurs[0]), float(valeurs[1]), float(valeurs[2])

    xl = x_base               # 2022 — bord gauche de la catégorie
    xm = x_base + cat_w / 2   # 2023 — centre
    xr = x_base + cat_w       # 2024 — bord droit

    # ── Polygone 5 sommets ──────────────────────────────────────────────────
    # Départ direct depuis la valeur — pas de plateau horizontal
    verts = [(xl, 0), (xl, h0), (xm, h1), (xr, h2), (xr, 0)]
    ax.add_patch(mpatches.Polygon(
        verts, closed=True, facecolor=couleur, edgecolor="none", zorder=2
    ))

    # ── Séparateur blanc vertical au centre (y=0 → y=h1) ───────────────────
    ax.plot([xm, xm], [0, h1],
            color="white", lw=1.5, zorder=4, solid_capstyle="butt")

    # ── Cercles ouverts aux 3 angles ────────────────────────────────────────
    for xi, hi in [(xl, h0), (xm, h1), (xr, h2)]:
        ax.plot(xi, hi, "o",
                markersize=7, markerfacecolor=bg._T["bg"],
                markeredgecolor=couleur, markeredgewidth=1.8,
                zorder=6, clip_on=False)

    # ── Labels YoY — couleur adaptée à la luminosité du fond ────────────────
    txt_c = "white" if _lum(couleur) < 0.40 else "#1a1a2e"
    for xa, ya, d in [
        ((xl + xm) / 2, (h0 + h1) / 2 * 0.72, deltas[0] if len(deltas) > 0 else None),
        ((xm + xr) / 2, (h1 + h2) / 2 * 0.72, deltas[1] if len(deltas) > 1 else None),
    ]:
        if d is None:
            continue
        s   = "+" if float(d) >= 0 else ""
        txt = f"{s}{d}"
        fs  = 8.0 if len(txt) >= 5 else 9.5
        ax.text(xa, ya, txt,
                ha="center", va="center",
                fontsize=fs, fontweight="bold", color=txt_c, zorder=5)

    # ── Badge cumulatif (toujours rond via boxstyle='circle') ───────────────
    s   = "+" if float(cumul) >= 0 else ""
    lab = f"{s}{cumul}"
    fs  = 7.5 if abs(float(cumul)) >= 1000 else (8.5 if abs(float(cumul)) >= 100 else 9.5)
    ax.text(xm, ymax_ax * 0.88, lab,
            ha="center", va="center",
            fontsize=fs, fontweight="bold", color="white",
            bbox=dict(boxstyle="circle,pad=0.38",
                      facecolor=couleur, edgecolor="white", linewidth=1.0),
            zorder=7, clip_on=False)

    # ── Nom catégorie sous l'axe ─────────────────────────────────────────────
    if nom:
        wrapped = "\n".join(textwrap.wrap(nom, width=16))
        ax.text(xm, -ymax_ax * 0.08, wrapped,
                ha="center", va="top",
                fontsize=8.5, color=bg._T["texte"])


def tendances_comparatives(
    items,
    ncols=4,
    titre="",
    sous_titre="",
    note="",
    hspace=0.65,
    figsize=None,
    format=None,
    background=None,
    **_extra,
):
    """Graphiques 'investissements temporels' style McKinsey — axes partagés.

    Différence clé avec ``tendances_grille()`` :

    - Les catégories d'une même rangée **partagent le même axe y** (échelle commune).
    - L'année intermédiaire (ex : 2023) est un **point de convergence** (cercle
      ouvert), pas une barre — les polygones reviennent à zéro aux extrémités.
    - Plusieurs catégories sont dessinées côte à côte sur un seul matplotlib Axes.

    Parameters
    ----------
    items : liste de dicts (même format que ``tendances_grille()``) ::

        {
            "nom"     : "Intelligence artificielle",
            "valeurs" : [95, 79, 117],   # 3 années
            "deltas"  : [-17, 48],        # variations YoY
            "cumul"   : 22,               # variation cumulée
            "couleur" : "#1B2A8A",        # hex, optionnel
        }

    ncols  : catégories par rangée, partagent le même axe y (défaut 4)
    hspace : espace vertical entre rangées, 0–1 (défaut 0.65)

    Returns
    -------
    ``(fig, axes)``
    """
    n = len(items)
    if n == 0:
        raise ValueError("tendances_comparatives : liste 'items' vide.")

    nrows = (n + ncols - 1) // ncols

    cat_w = 3.10   # largeur totale d'une catégorie en unités x
    cat_g = 0.55   # espace entre catégories sur le même axe

    fig_w = max(10.0, ncols * 3.3 + 1.0)
    fig_h = nrows * 3.5
    fig_size = bg._resoudre_figsize(figsize, format) or (fig_w, fig_h)

    fig, axes_2d = plt.subplots(nrows, 1, figsize=fig_size, squeeze=False)
    axes = axes_2d.flatten()
    bg._appliquer_background(fig, None, background)

    for row_idx in range(nrows):
        row_items = items[row_idx * ncols : (row_idx + 1) * ncols]
        if not row_items:
            break

        ax = axes[row_idx]
        bg._appliquer_background(fig, ax, background)

        n_cat   = len(row_items)
        x_total = n_cat * (cat_w + cat_g) - cat_g

        all_vals = [float(v) for item in row_items for v in item["valeurs"]]
        ymax     = max(all_vals) * 1.52

        # Configurer xlim avant de dessiner (requis pour boxstyle='circle')
        ax.set_xlim(-0.22, x_total + 0.22)

        # Ticks y calculés sur [0, ymax], puis ylim étendu pour les labels
        ax.set_ylim(0, ymax)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=4, integer=True))
        yticks = [t for t in ax.get_yticks() if 0 <= t <= ymax * 1.01]

        ax.set_ylim(-ymax * 0.14, ymax)
        ax.set_yticks(yticks)

        for col_idx, item in enumerate(row_items):
            _dessiner_tendance_cat(
                ax,
                x_base=col_idx * (cat_w + cat_g),
                valeurs=item["valeurs"],
                deltas=item.get("deltas", []),
                cumul=item.get("cumul", 0),
                couleur=item.get("couleur", bg.PALETTE[col_idx % len(bg.PALETTE)]),
                cat_w=cat_w, ymax_ax=ymax,
                nom=item.get("nom", ""),
            )

        ax.grid(False)
        ax.axhline(0, color=bg._T["grille"], linewidth=0.8, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_color(bg._T["grille"])
        ax.spines["left"].set_linewidth(0.6)
        ax.tick_params(axis="y", labelsize=8, colors=bg._T["texte_dim"], length=2, pad=2)
        ax.tick_params(axis="x", bottom=False, labelbottom=False)

    # Masquer les axes vides
    for row_idx in range(nrows):
        if not items[row_idx * ncols : (row_idx + 1) * ncols]:
            axes[row_idx].set_visible(False)

    # ── Titre / sous-titre : espacement basé sur la hauteur réelle de la figure
    fig_h_pt = fig.get_figheight() * 72.0   # hauteur en points typographiques
    y_cur    = 0.99
    if titre:
        fig.text(0.03, y_cur, titre,
                 fontsize=12, fontweight="bold", color=bg._T["texte"],
                 ha="left", va="top")
        y_cur -= 15.0 / fig_h_pt   # descend de 15 pt (corps 12 + 3 pt interligne)
    if sous_titre:
        fig.text(0.03, y_cur, sous_titre,
                 fontsize=8.5, color=bg._T["texte_dim"], ha="left", va="top")
        y_cur -= 11.0 / fig_h_pt   # descend encore de 11 pt
    if note:
        fig.text(0.03, 0.01, note,
                 fontsize=7, color=bg._T["texte_dim"],
                 ha="left", va="bottom", style="italic")

    top_margin = (y_cur - 4.0 / fig_h_pt) if (titre or sous_titre) else 0.97
    plt.subplots_adjust(
        hspace=hspace,
        left=0.09, right=0.97,
        top=top_margin, bottom=0.04,
    )

    return fig, axes[:nrows]


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
    couleurs = bg._couleurs_auto(noms, couleur, couleurs_multiples)
    if isinstance(couleurs, str):
        couleurs = [couleurs] * len(noms)

    fig, ax = bg._new_fig(figsize, ax, format, background=background)

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
                   edgecolors=bg._T["fond_neutre"], linewidths=2)

        if montrer_valeurs:
            for xi, yi in zip(x, y):
                ax.text(float(xi), float(yi), str(int(yi)),
                        ha="center", va="center",
                        fontsize=8, color=bg._T["fond_neutre"],
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
    ax.set_xticklabels(periodes, fontsize=10, color=bg._T["texte_dim"])
    ax.set_yticks(range(1, max_rang + 1))
    ax.set_yticklabels(
        [f"#{r}" for r in range(1, max_rang + 1)],
        fontsize=9, color=bg._T["texte_dim"],
    )

    # Grille horizontale par niveau de rang
    ax.yaxis.grid(True, color=bg._T["grille"], lw=0.7, linestyle="--")
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)

    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(bg._T["grille"])
    ax.tick_params(length=0)

    return bg._finalize(ax, titre, sous_titre, note=note, legende=False, fig=fig)


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
    couleurs = bg._couleurs_auto(noms, couleur, couleurs_multiples)
    if isinstance(couleurs, str):
        couleurs = [couleurs] * len(noms)

    fig_size = bg._resoudre_figsize(figsize, format) or (7, 7)
    fig      = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(111, projection="polar")
    bg._appliquer_background(fig, ax, background)

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
    ax.set_xticklabels(categories, fontsize=9.5, color=bg._T["texte"])
    ax.set_ylim(vmin, vmax)
    ax.yaxis.grid(True, color=bg._T["grille"], lw=0.6, linestyle="--")
    ax.xaxis.grid(True, color=bg._T["grille"], lw=0.6)
    ax.spines["polar"].set_color(bg._T["grille"])
    ax.tick_params(axis="y", colors=bg._T["texte_dim"], labelsize=7.5)
    ax.set_rlabel_position(45)

    if len(noms) > 1:
        ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
                  framealpha=0, labelcolor=bg._T["texte"], fontsize=9)

    if titre:
        fig.suptitle(titre, fontsize=14, fontweight="bold",
                     color=bg._T["texte"], y=1.03)
    if sous_titre:
        fig.text(0.5, -0.01, sous_titre, ha="center",
                 fontsize=9, color=bg._T["texte_dim"])
    if note:
        fig.text(0.01, -0.04, note, fontsize=8, color=bg._T["texte_dim"],
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
    couleurs = bg._couleurs_auto(noms, couleur, couleurs_multiples)
    if isinstance(couleurs, str):
        couleurs = [couleurs] * n

    fig_size = bg._resoudre_figsize(figsize, format) or (10, max(4, n * 1.4))
    fig, ax  = plt.subplots(figsize=fig_size)
    bg._appliquer_background(fig, ax, background)

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
        ax.axhline(y_base, color=bg._T["grille"], lw=0.6, zorder=1)

    ax.set_yticks(range(n))
    ax.set_yticklabels(list(reversed(noms)), fontsize=9.5, color=bg._T["texte"])
    ax.set_ylim(-0.15, n - 1 + chevauchement + 0.2)

    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(bg._T["grille"])
    ax.tick_params(axis="x", colors=bg._T["texte_dim"], length=0)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)

    return bg._finalize(ax, titre, sous_titre, note=note, legende=False, fig=fig)
