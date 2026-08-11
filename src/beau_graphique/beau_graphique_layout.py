"""
beau_graphique_layout.py
==========================
Mise en page narrative — extension de beau_graphique.py (module à plat, pas
de sous-paquet). Importe le socle via `import beau_graphique as bg` pour
accéder à PALETTE/_T à chaud (patchés par themes.appliquer()) — jamais via
`from beau_graphique import ...` qui figerait une copie obsolète.

Usage
-----
    import beau_graphique as bg
    from beau_graphique_layout import slide, layout_rapport

Ces fonctions sont ré-exportées par beau_graphique/__init__.py — l'import
depuis `beau_graphique` reste inchangé pour l'utilisateur final.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import beau_graphique as bg


# ══════════════════════════════════════════════════════════════════════════════
# slide() — mise en page texte/graphique libre (remplace dashboard)
# ══════════════════════════════════════════════════════════════════════════════

def slide(elements: list, nrows=3, ncols=4,
          hspace=0.35, wspace=0.30,
          figsize=None, format=None, background=None):
    """
    Mise en page libre d'un slide ou rapport : texte, graphiques, KPI et
    callouts s'arrangent dans une grille à la façon d'un éditeur de slides.

    Philosophie
    -----------
    On part du **texte** et de la **structure narrative**, pas des métriques.
    Chaque région peut contenir du texte libre, un graphique, un chiffre clé
    ou un bloc callout. L'ordre des éléments donne la hiérarchie visuelle.

    Parameters
    ----------
    elements : liste de dicts. Chaque dict décrit une région ::

        {
            # Position dans la grille (obligatoire)
            "pos"     : (row, col),             # cellule unique
            # ou
            "pos"     : (row, col, rspan, cspan), # fusion de cellules

            # Type de contenu (obligatoire)
            "type"    : "titre"      # Texte grand format
                      | "sous_titre" # Texte secondaire
                      | "texte"      # Paragraphe libre
                      | "callout"    # Bloc mis en valeur (fond teinté + barre)
                      | "graphique"  # n'importe quelle fonction beau_graphique
                      | "kpi"        # Valeur + delta centrés
                      | "vide"       # Cellule intentionnellement vide,

            # Contenu selon le type
            "texte"   : str,          # pour titre / sous_titre / texte / callout
            "fn"      : callable,     # pour graphique — la fonction à appeler
            "kwargs"  : dict,         # kwargs passés à fn() (sauf figsize, ax)
            "valeur"  : str,          # pour kpi — ex: "23 %", "1,2 M"
            "label"   : str,          # pour kpi — libellé sous la valeur
            "delta"   : str,          # pour kpi — ex: "+3 pts" (optionnel)
            "positif" : bool,         # pour kpi — couleur du delta (défaut True)

            # Style optionnel (tous types)
            "taille"  : float,        # fontsize
            "couleur" : str,          # couleur d'accent hex
            "gras"    : bool,         # fontweight bold
            "align"   : "left"|"center"|"right",
        }

    nrows, ncols : dimensions de la grille (défaut 3×4)
    hspace, wspace : espacement entre cellules

    Returns
    -------
    ``(fig, axes_dict)`` — axes_dict est un dict ``{(row, col): ax}``.

    Exemple
    -------
    >>> fig, axes = slide([
    ...     # Ligne 0 : titre sur toute la largeur
    ...     {"pos": (0, 0, 1, 4), "type": "titre",
    ...      "texte": "Le marché EMEA accélère au T3"},
    ...
    ...     # Ligne 1 : texte d'accroche + 2 graphiques
    ...     {"pos": (1, 0, 1, 1), "type": "texte",
    ...      "texte": "La croissance organique dépasse nos projections "
    ...               "sur trois marchés clés simultanément."},
    ...     {"pos": (1, 1, 1, 2), "type": "graphique",
    ...      "fn": barres, "kwargs": {"categories": [...], "valeurs": [...]}},
    ...     {"pos": (1, 3, 1, 1), "type": "kpi",
    ...      "valeur": "+18 %", "label": "Croissance T3",
    ...      "delta": "vs +11 % attendu", "positif": True},
    ...
    ...     # Ligne 2 : callout + graphique
    ...     {"pos": (2, 0, 1, 1), "type": "callout",
    ...      "texte": "L'Allemagne franchit 100 M€ pour la première fois."},
    ...     {"pos": (2, 1, 1, 3), "type": "graphique",
    ...      "fn": ligne, "kwargs": {"x": [...], "y_series": {...}}},
    ... ], nrows=3, ncols=4)
    """
    figsize = bg._resoudre_figsize(figsize, format)
    fig = plt.figure(figsize=figsize or (ncols * 3.8, nrows * 3.0))
    bg._appliquer_background(fig, None, background)

    gs = fig.add_gridspec(nrows, ncols, hspace=hspace, wspace=wspace,
                          left=0.03, right=0.97, top=0.97, bottom=0.03)

    axes_dict = {}

    for elem in elements:
        pos = elem.get("pos", (0, 0))
        if len(pos) == 2:
            row, col = pos
            rspan, cspan = 1, 1
        else:
            row, col, rspan, cspan = pos

        ax = fig.add_subplot(gs[row:row+rspan, col:col+cspan])
        bg._appliquer_background(fig, ax, background)
        axes_dict[(row, col)] = ax

        typ     = elem.get("type", "vide")
        couleur = elem.get("couleur", bg.PALETTE[0])
        align   = elem.get("align", "left")
        ha_map  = {"left": 0.05, "center": 0.5, "right": 0.95}
        ha_txt  = ha_map.get(align, 0.05)

        # ── Désactiver la frame de l'axe pour tous les types textuels ──────
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])

        if typ == "vide":
            ax.set_facecolor(bg._T["bg"])

        elif typ == "titre":
            ax.set_facecolor(bg._T["bg"])
            texte = elem.get("texte", "")
            taille = elem.get("taille", 18)
            ax.text(ha_txt, 0.5, texte, transform=ax.transAxes,
                    ha=align, va="center",
                    fontsize=taille, fontweight="bold", color=bg._T["texte"],
                    wrap=True)

        elif typ == "sous_titre":
            ax.set_facecolor(bg._T["bg"])
            texte = elem.get("texte", "")
            taille = elem.get("taille", 12)
            ax.text(ha_txt, 0.5, texte, transform=ax.transAxes,
                    ha=align, va="center",
                    fontsize=taille, color=bg._T["texte_dim"],
                    wrap=True)

        elif typ == "texte":
            ax.set_facecolor(bg._T["bg"])
            texte = elem.get("texte", "")
            taille = elem.get("taille", 10.5)
            gras   = elem.get("gras", False)
            ax.text(ha_txt, 0.5, texte, transform=ax.transAxes,
                    ha=align, va="center",
                    fontsize=taille,
                    fontweight="bold" if gras else "normal",
                    color=bg._T["texte"],
                    wrap=True)

        elif typ == "callout":
            # Fond teinté + barre verticale gauche
            import matplotlib.colors as _mcolors
            r_c, g_c, b_c, _ = _mcolors.to_rgba(couleur)
            ax.set_facecolor((r_c, g_c, b_c, 0.10))
            ax.add_patch(mpatches.Rectangle(
                (0, 0), 0.04, 1.0,
                transform=ax.transAxes, clip_on=False,
                facecolor=couleur, edgecolor="none",
            ))
            texte  = elem.get("texte", "")
            taille = elem.get("taille", 10.5)
            ax.text(0.10, 0.5, texte, transform=ax.transAxes,
                    ha="left", va="center",
                    fontsize=taille, color=bg._T["texte"],
                    fontstyle="italic", wrap=True)

        elif typ == "kpi":
            ax.set_facecolor(bg._T["bg"])
            valeur  = str(elem.get("valeur", "—"))
            label   = elem.get("label", "")
            delta   = elem.get("delta", "")
            positif = elem.get("positif", True)
            taille  = elem.get("taille", 26)
            col_delta = bg._COULEUR_HAUT if positif else bg._COULEUR_BAS

            ax.text(0.5, 0.62, valeur, transform=ax.transAxes,
                    ha="center", va="center",
                    fontsize=taille, fontweight="bold", color=couleur)
            if label:
                ax.text(0.5, 0.30, label.upper(), transform=ax.transAxes,
                        ha="center", va="center",
                        fontsize=8.5, color=bg._T["texte_dim"],
                        fontweight="bold")
            if delta:
                ax.text(0.5, 0.10, delta, transform=ax.transAxes,
                        ha="center", va="center",
                        fontsize=9.5, color=col_delta, fontweight="bold")

        elif typ == "graphique":
            fn     = elem.get("fn")
            kwargs = dict(elem.get("kwargs", {}))
            if fn is not None:
                kwargs.pop("figsize", None)
                kwargs.pop("format", None)
                try:
                    fn(ax=ax, **kwargs)
                except TypeError:
                    # la fonction ne supporte pas ax= : on la laisse créer sa figure
                    ax.set_visible(False)

    return fig, axes_dict


# ══════════════════════════════════════════════════════════════════════════════
# Layout rapport / slide
# ══════════════════════════════════════════════════════════════════════════════

def _resoudre_style_kpi(style_kpi) -> dict:
    """Convertit style_kpi= (preset str ou dict brut) en dict de flags booléens."""
    if style_kpi is None:
        return dict(bg._STYLE_KPI_PRESETS["accent"])
    if isinstance(style_kpi, str):
        if style_kpi not in bg._STYLE_KPI_PRESETS:
            raise ValueError(
                f"style_kpi inconnu : {style_kpi!r}. "
                f"Valides : {list(bg._STYLE_KPI_PRESETS)} — ou passez un dict."
            )
        return dict(bg._STYLE_KPI_PRESETS[style_kpi])
    if isinstance(style_kpi, dict):
        result = dict(bg._STYLE_KPI_PRESETS["accent"])
        result.update(style_kpi)
        return result
    return dict(bg._STYLE_KPI_PRESETS["accent"])


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
    couleur : couleur d'accent hex — barre ou teinte de fond (défaut bg.PALETTE[0])

    Clés reconnues dans *style*
    ---------------------------
    border     : bool — bordure fine autour de la tuile
    accent_bar : bool — barre colorée verticale sur le bord gauche
    bg_fill    : bool — fond légèrement teinté avec la couleur d'accent
    """
    couleur_accent = kpi.get("couleur", bg.PALETTE[0])
    positif        = kpi.get("positif", True)
    couleur_delta  = bg._COULEUR_HAUT if positif else bg._COULEUR_BAS

    # ── Fond ──────────────────────────────────────────────────────────────
    if style.get("bg_fill"):
        h = couleur_accent.lstrip("#")
        r = int(h[0:2], 16) / 255
        g = int(h[2:4], 16) / 255
        b = int(h[4:6], 16) / 255
        ax.set_facecolor((r, g, b, 0.10))
    else:
        ax.set_facecolor(bg._T["bg"])

    # ── Bordure ────────────────────────────────────────────────────────────
    for sp in ax.spines.values():
        sp.set_visible(bool(style.get("border")))
        if style.get("border"):
            sp.set_linewidth(0.8)
            sp.set_edgecolor(bg._T["grille"])

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
                fontsize=8, color=bg._T["texte_dim"], ha="center", va="center",
                fontweight="bold")

    ax.text(x_text, 0.50, txt_valeur, transform=ax.transAxes,
            fontsize=22, color=bg._T["texte"], ha="center", va="center",
            fontweight="bold")

    if delta:
        signe = "▲" if positif else "▼"
        ax.text(x_text, 0.16, f"{signe} {delta}", transform=ax.transAxes,
                fontsize=9.5, color=couleur_delta, ha="center", va="center",
                fontweight="bold")


def layout_rapport(titre="", sous_titre="", note="", kpis=None,
                   n_graphiques=1, figsize=None, format="slide",
                   style_kpi="accent", background=None):
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

                   La couleur d'accent provient de ``kpi["couleur"]`` (par défaut bg.PALETTE[0]).

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

    fig_size = bg._resoudre_figsize(figsize, format) or bg.FORMATS["slide"]
    fig = plt.figure(figsize=fig_size)
    bg._appliquer_background(fig, None, background)

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
        bg._appliquer_background(fig, ax_h, background)
        ax_h.set_axis_off()

        if titre:
            ax_h.text(0.0, 0.88, titre, transform=ax_h.transAxes,
                      fontsize=17, fontweight="bold", color=bg._T["texte"],
                      va="top", ha="left")
        if sous_titre:
            ax_h.text(0.0, 0.28, sous_titre, transform=ax_h.transAxes,
                      fontsize=10, color=bg._T["texte_dim"],
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
        bg._appliquer_background(fig, ax_c, background)
        axes_charts.append(ax_c)

    # ── Note de bas de page ───────────────────────────────────────────────
    if note:
        fig.text(0.03, 0.01, note, fontsize=8, color=bg._T["texte_dim"],
                 style="italic", transform=fig.transFigure)

    return fig, {"graphiques": axes_charts, "kpis": axes_kpis}


