"""
themes.py
=========
Système de thèmes pour beau_graphique — palettes, modes, secteurs.

Fonctionnalités
---------------
  • Thèmes prédéfinis par secteur : finance, santé, académique, tech, neutre
  • Palettes daltonisme-safe (deutéranopie, protanopie, tritanopie)
  • Mode sombre natif
  • Génération de palette depuis une couleur de marque
  • Thème courant global (persiste dans la session, remplace PALETTE)

Usage
-----
    from themes import appliquer, THEMES, palette_safe, depuis_couleur

    appliquer("finance")           # active le thème globalement
    appliquer("sombre")            # mode sombre
    appliquer("daltonisme_safe")   # palette universelle

    # Depuis une couleur de marque
    palette = depuis_couleur("#E63946", n=6)
    appliquer_palette(palette)

    # Accéder à la palette active
    from themes import PALETTE_ACTIVE
"""

import colorsys
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import numpy as np
import os
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


# ── Référence vers beau_graphique pour patcher PALETTE ───────────────────────
_BG_MODULE = None


def _get_bg():
    global _BG_MODULE
    if _BG_MODULE is None:
        try:
            import beau_graphique as bg
            _BG_MODULE = bg
        except ImportError:
            pass
    return _BG_MODULE


def _teinte_intermediaire(c1: str, c2: str, t: float) -> str:
    """Mélange deux couleurs hex (t=0 -> c1, t=1 -> c2)."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


# ══════════════════════════════════════════════════════════════════════════════
# Catalogue des thèmes
# ══════════════════════════════════════════════════════════════════════════════

THEMES = {

    # ── Par défaut ────────────────────────────────────────────────────────────
    "defaut": {
        "nom":        "Défaut",
        "description": "Palette bleue-rose vive, fond clair chaleureux",
        "fond":       "#F7F8FC",
        "texte":      "#1A1C2E",
        "grille":     "#E2E4EE",
        "palette": [
            "#4361EE", "#F72585", "#4CC9F0",
            "#7209B7", "#3A0CA3", "#F3722C",
            "#43AA8B", "#90BE6D",
        ],
    },

    # ── Finance ───────────────────────────────────────────────────────────────
    "finance": {
        "nom":        "Finance",
        "description": "Palette sobre et professionnelle, bleu marine + vert",
        "fond":       "#F5F6FA",
        "texte":      "#0D1B2A",
        "grille":     "#DDE1EC",
        "palette": [
            "#003566", "#0077B6", "#00B4D8",
            "#2DC653", "#E9C46A", "#F4A261",
            "#E76F51", "#8D99AE",
        ],
    },

    # ── Santé ─────────────────────────────────────────────────────────────────
    "sante": {
        "nom":        "Santé",
        "description": "Teintes médicales claires — bleu, vert, rouge doux",
        "fond":       "#F0F7F4",
        "texte":      "#1B3A4B",
        "grille":     "#D6EAE2",
        "palette": [
            "#1B7F79", "#2EC4B6", "#CBF3F0",
            "#E63946", "#FFBF69", "#FF9F1C",
            "#52B788", "#40916C",
        ],
    },

    # ── Académique ────────────────────────────────────────────────────────────
    "academique": {
        "nom":        "Académique",
        "description": "Sobre pour publications — 8 couleurs distinguables en N&B",
        "fond":       "#FAFAF8",
        "texte":      "#1A1A1A",
        "grille":     "#E0E0DC",
        "palette": [
            "#E66101", "#5E3C99", "#B2ABD2",
            "#FDB863", "#1B7837", "#762A83",
            "#D9F0D3", "#4D4D4D",
        ],
        "linestyles": ["-", "--", "-.", ":", "-", "--", "-.", ":"],
    },

    # ── Tech / Startup ────────────────────────────────────────────────────────
    "tech": {
        "nom":        "Tech",
        "description": "Néon contrôlé sur fond sombre — pour présentations",
        "fond":       "#0F1117",
        "texte":      "#E8EAF6",
        "grille":     "#1E2130",
        "mode":       "sombre",
        "palette": [
            "#7C3AED", "#06B6D4", "#10B981",
            "#F59E0B", "#EF4444", "#EC4899",
            "#8B5CF6", "#3B82F6",
        ],
    },

    # ── Minimal / Rapport ────────────────────────────────────────────────────
    "minimal": {
        "nom":        "Minimal",
        "description": "Gris + 1 accent — pour rapports Word/PDF épurés",
        "fond":       "#FFFFFF",
        "texte":      "#111111",
        "grille":     "#EEEEEE",
        "palette": [
            "#222222", "#555555", "#888888",
            "#AAAAAA", "#CCCCCC",
            "#1A56DB", "#E02424", "#057A55",
        ],
    },

    # ── Chaud / Présentation ─────────────────────────────────────────────────
    "chaud": {
        "nom":        "Chaud",
        "description": "Tonalités ambre et corail — slides percutants",
        "fond":       "#FFF8F0",
        "texte":      "#1C0A00",
        "grille":     "#F5E6D3",
        "palette": [
            "#E63946", "#F4A261", "#E9C46A",
            "#2A9D8F", "#264653", "#F77F00",
            "#D62828", "#023E8A",
        ],
    },

    # ── Mode sombre générique ────────────────────────────────────────────────
    "sombre": {
        "nom":        "Sombre",
        "description": "Fond noir profond, palette vive sur fond dark",
        "fond":       "#1A1B2E",
        "texte":      "#E8EAF6",
        "grille":     "#2D2F45",
        "mode":       "sombre",
        "palette": [
            "#4CC9F0", "#F72585", "#7209B7",
            "#4361EE", "#43AA8B", "#F3722C",
            "#90BE6D", "#277DA1",
        ],
    },

    # ── Daltonisme-safe — universel ───────────────────────────────────────────
    "daltonisme_safe": {
        "nom":        "Daltonisme-safe",
        "description": "Palette Wong (2011) — distinguable par tous les types de daltonisme",
        "fond":       "#F7F8FC",
        "texte":      "#1A1C2E",
        "grille":     "#E2E4EE",
        "palette": [
            "#000000",  # Noir
            "#E69F00",  # Orange
            "#56B4E9",  # Bleu ciel
            "#009E73",  # Vert
            "#F0E442",  # Jaune
            "#0072B2",  # Bleu foncé
            "#D55E00",  # Vermillon
            "#CC79A7",  # Rose mauve
        ],
        "note": "Palette Wong (2011) — distinguable pour deutéranopie, protanopie et tritanopie",
    },

    # ── Deutéranopie (rouge-vert, le + fréquent) ─────────────────────────────
    "deuteranopie": {
        "nom":        "Deutéranopie",
        "description": "Optimisée rouge-vert (8 % des hommes)",
        "fond":       "#F7F8FC",
        "texte":      "#1A1C2E",
        "grille":     "#E2E4EE",
        "palette": [
            "#1A85FF", "#D41159",
            "#FFC20A", "#0C7BDC",
            "#994F00", "#006CD1",
            "#E1BE6A", "#40B0A6",
        ],
        "note": "IBM colorblind-safe palette — deutéranopie",
    },

    # ── Séquentielle (une variable continue) ─────────────────────────────────
    "sequentielle_bleu": {
        "nom":        "Séquentielle bleue",
        "description": "Dégradé clair→foncé pour une variable ordonnée",
        "fond":       "#F7F8FC",
        "texte":      "#1A1C2E",
        "grille":     "#E2E4EE",
        "palette": [
            "#D0E8FF", "#9AC5F4", "#5B9FE4",
            "#2A7CD4", "#0057B8", "#003A8C",
            "#002060", "#000F3D",
        ],
    },

    # ── Divergente (deux extrêmes + centre neutre) ────────────────────────────
    "divergente": {
        "nom":        "Divergente",
        "description": "Rouge → blanc → bleu — pour des données centrées sur 0",
        "fond":       "#F7F8FC",
        "texte":      "#1A1C2E",
        "grille":     "#E2E4EE",
        "palette": [
            "#B2182B", "#D6604D", "#F4A582",
            "#F7F7F7",
            "#92C5DE", "#4393C3", "#2166AC",
            "#053061",
        ],
    },
}

# ── État courant ──────────────────────────────────────────────────────────────
PALETTE_ACTIVE = list(THEMES["defaut"]["palette"])
_THEME_ACTIF   = "defaut"


# ══════════════════════════════════════════════════════════════════════════════
# appliquer — active un thème globalement
# ══════════════════════════════════════════════════════════════════════════════

def appliquer(nom_theme: str, verbose: bool = True) -> dict:
    """
    Active un thème globalement — met à jour matplotlib et PALETTE dans
    beau_graphique.py et narratif.py si disponibles.

    Parameters
    ----------
    nom_theme : clé du thème dans THEMES, ou nom partiel (recherche floue)
    verbose   : afficher la confirmation

    Returns
    -------
    dict du thème appliqué

    Exemples
    --------
    >>> appliquer("finance")
    >>> appliquer("daltonisme_safe")
    >>> appliquer("sombre")
    >>> appliquer("tech")
    """
    global PALETTE_ACTIVE, _THEME_ACTIF

    # Recherche floue si nom partiel
    theme = _trouver_theme(nom_theme)

    palette = theme["palette"]
    fond    = theme.get("fond",   "#F7F8FC")
    texte   = theme.get("texte",  "#1A1C2E")
    grille  = theme.get("grille", "#E2E4EE")
    mode    = theme.get("mode",   "clair")

    # ── Mise à jour matplotlib ────────────────────────────────────────────────
    plt.rcParams.update({
        "figure.facecolor":   fond,
        "axes.facecolor":     fond,
        "axes.edgecolor":     grille,
        "axes.labelcolor":    texte,
        "text.color":         texte,
        "xtick.color":        texte,
        "ytick.color":        texte,
        "grid.color":         grille,
        "grid.alpha":         0.75,
        "grid.linewidth":     0.7,
        "grid.linestyle":     "--",
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.grid":          True,
        "legend.facecolor":   fond,
        "legend.edgecolor":   grille,
        "savefig.facecolor":  fond,
    })

    # Cycler de couleurs
    from matplotlib.rcsetup import cycler
    plt.rcParams["axes.prop_cycle"] = cycler(color=palette)

    # Linestyles académiques (pour distinguabilité N&B)
    if "linestyles" in theme:
        plt.rcParams["axes.prop_cycle"] = cycler(
            color=palette, linestyle=theme["linestyles"]
        )

    # ── Mise à jour PALETTE + _T dans beau_graphique ──────────────────────────
    # _T pilote fond/texte/grille pour dot_plot_comparatif, bump, radar, slide,
    # layout_rapport, waterfall, box_plot, facet, dashboard, flux, et tout
    # narratif.py (qui le lit dynamiquement via _t()/_bg._T) — sans ce patch,
    # appliquer() changeait les couleurs de données (PALETTE) mais laissait le
    # texte/fond de ces fonctions sur l'état du dernier bg.init(theme=...),
    # avec un vrai risque de texte illisible (ex: texte sombre sur fond sombre).
    PALETTE_ACTIVE = list(palette)
    bg = _get_bg()
    if bg is not None:
        bg.PALETTE = list(palette)
        bg._T = {
            "bg":          fond,
            "texte":       texte,
            "texte_dim":   _teinte_intermediaire(texte, fond, 0.35),
            "grille":      grille,
            "fond_neutre": fond if mode == "sombre" else "#FFFFFF",
            "serie_dim":   _teinte_intermediaire(texte, fond, 0.55),
        }

    # ── Mise à jour couleurs dans narratif si disponible ─────────────────────
    try:
        import narratif as narr
        narr.PALETTE   = list(palette)
        narr.BG        = fond
        narr.TEXTE     = texte
        narr.GRIS_CLAIR = grille
    except ImportError:
        pass

    _THEME_ACTIF = nom_theme

    if verbose:
        mode_icon = "🌙" if mode == "sombre" else "☀"
        _print_safe(f"✓ Thème '{theme['nom']}' activé {mode_icon}")
        if "note" in theme:
            _print_safe(f"  ℹ {theme['note']}")

    return theme


def appliquer_palette(palette: list, verbose: bool = True) -> None:
    """
    Applique directement une liste de couleurs hex sans changer le reste du thème.

    Exemple
    -------
    >>> appliquer_palette(["#E63946", "#457B9D", "#1D3557", "#A8DADC"])
    """
    global PALETTE_ACTIVE
    PALETTE_ACTIVE = list(palette)

    from matplotlib.rcsetup import cycler
    plt.rcParams["axes.prop_cycle"] = cycler(color=palette)

    bg = _get_bg()
    if bg is not None:
        bg.PALETTE = list(palette)

    if verbose:
        _print_safe(f"✓ Palette custom appliquée ({len(palette)} couleurs)")
        _afficher_palette(palette)


def reinitialiser(verbose: bool = True) -> None:
    """Revient au thème défaut."""
    appliquer("defaut", verbose=verbose)


# ══════════════════════════════════════════════════════════════════════════════
# lister — aperçu des thèmes disponibles
# ══════════════════════════════════════════════════════════════════════════════

def lister() -> None:
    """Affiche tous les thèmes disponibles avec leurs couleurs."""
    _print_safe("┌" + "─"*60 + "┐")
    _print_safe(f"│  {'Thèmes disponibles':<58}│")
    _print_safe("├" + "─"*60 + "┤")
    for cle, t in THEMES.items():
        actif = " ◀ actif" if cle == _THEME_ACTIF else ""
        _print_safe(f"│  {cle:<22} {t['description'][:30]:<30}{actif:<8}│")
    _print_safe("└" + "─"*60 + "┘")
    _print_safe("\nUsage : appliquer('finance')  |  appliquer('daltonisme_safe')")


# ══════════════════════════════════════════════════════════════════════════════
# depuis_couleur — générateur de palette depuis une couleur de marque
# ══════════════════════════════════════════════════════════════════════════════

def depuis_couleur(
    couleur_base: str,
    n: int = 6,
    methode: str = "analogique",
    luminosite_min: float = 0.35,
    luminosite_max: float = 0.75,
) -> list:
    """
    Génère une palette harmonieuse depuis une couleur de marque.

    Parameters
    ----------
    couleur_base   : couleur hex de départ (ex: "#E63946" ou "#4361EE")
    n              : nombre de couleurs à générer (2–8)
    methode        : stratégie de génération :
                     "analogique"  → teintes voisines (palette douce, cohérente)
                     "complementaire" → couleur + son opposé + remplissage
                     "triadique"   → 3 couleurs équidistantes sur la roue
                     "monochrome"  → variations de luminosité sur la même teinte
                     "split"       → couleur + deux couleurs flanquant son complément
    luminosite_min, luminosite_max : plage de luminosité (0–1)

    Returns
    -------
    Liste de n couleurs hex

    Exemples
    --------
    >>> pal = depuis_couleur("#003566", n=6, methode="analogique")
    >>> pal = depuis_couleur("#E63946", n=5, methode="complementaire")
    >>> appliquer_palette(depuis_couleur("#7209B7"))
    """
    n = max(2, min(8, n))
    r, g, b = mc.to_rgb(couleur_base)
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    if methode == "monochrome":
        lums = np.linspace(luminosite_min, luminosite_max, n)
        palette = [_hls_to_hex(h, li, s) for li in lums]

    elif methode == "complementaire":
        hues = [h, (h + 0.5) % 1.0]
        hues += [((h + 0.5 + (i + 1) * 0.1) % 1.0) for i in range(n - 2)]
        lums = _lum_spread(n, luminosite_min, luminosite_max)
        palette = [_hls_to_hex(hues[i % len(hues)], lums[i], s) for i in range(n)]

    elif methode == "triadique":
        hues = [(h + i / 3.0) % 1.0 for i in range(3)]
        hues = hues * ((n // 3) + 1)
        lums = _lum_spread(n, luminosite_min, luminosite_max)
        palette = [_hls_to_hex(hues[i % len(hues)], lums[i], s) for i in range(n)]

    elif methode == "split":
        hues = [h, (h + 0.417) % 1.0, (h + 0.583) % 1.0]
        hues = hues * 3
        lums = _lum_spread(n, luminosite_min, luminosite_max)
        palette = [_hls_to_hex(hues[i % len(hues)], lums[i], s) for i in range(n)]

    else:  # analogique (défaut)
        step = 0.06
        hues = [(h + (i - n // 2) * step) % 1.0 for i in range(n)]
        lums = _lum_spread(n, luminosite_min, luminosite_max)
        palette = [_hls_to_hex(hues[i], lums[i], s) for i in range(n)]

    return palette


def _lum_spread(n, lo, hi):
    if n == 1:
        return [(lo + hi) / 2]
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def _hls_to_hex(h, l, s) -> str:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0, min(1, l)), max(0, min(1, s)))
    return "#{:02X}{:02X}{:02X}".format(int(r*255), int(g*255), int(b*255))


# ══════════════════════════════════════════════════════════════════════════════
# apercu — affichage d'une palette en notebook
# ══════════════════════════════════════════════════════════════════════════════

def apercu(palette_ou_theme=None, figsize=None):
    """
    Affiche visuellement une palette ou un thème.

    Parameters
    ----------
    palette_ou_theme : liste de couleurs hex, nom de thème, ou None (= thème actif)

    Exemple
    -------
    >>> apercu()                          # thème actif
    >>> apercu("finance")                 # thème nommé
    >>> apercu(["#E63946","#457B9D"])     # liste custom
    >>> apercu(depuis_couleur("#7209B7")) # palette générée
    """
    if palette_ou_theme is None:
        palette = PALETTE_ACTIVE
        titre   = f"Palette active — thème '{_THEME_ACTIF}'"
    elif isinstance(palette_ou_theme, str):
        theme   = _trouver_theme(palette_ou_theme)
        palette = theme["palette"]
        titre   = f"Thème : {theme['nom']} — {theme['description']}"
    else:
        palette = palette_ou_theme
        titre   = f"Palette custom ({len(palette_ou_theme)} couleurs)"

    n = len(palette)
    fig, ax = plt.subplots(figsize=figsize or (n * 1.1 + 1, 1.8))
    fig.patch.set_facecolor(plt.rcParams.get("figure.facecolor", "#F7F8FC"))
    ax.set_facecolor(plt.rcParams.get("figure.facecolor", "#F7F8FC"))

    for i, c in enumerate(palette):
        rect = plt.Rectangle([i, 0], 0.88, 1,
                              facecolor=c, edgecolor="white", linewidth=1.5)
        ax.add_patch(rect)
        # Contraste auto texte (blanc ou noir selon luminosité)
        r, g, b = mc.to_rgb(c)
        lum = 0.299*r + 0.587*g + 0.114*b
        tc = "white" if lum < 0.5 else "#1A1C2E"
        ax.text(i + 0.44, 0.62, c.upper(), ha="center", va="center",
                fontsize=7.5, color=tc, fontweight="bold")
        ax.text(i + 0.44, 0.28, f"#{i+1}", ha="center", va="center",
                fontsize=7, color=tc, alpha=0.75)

    ax.set_xlim(0, n)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title(titre, fontsize=11, fontweight="bold",
                 color=plt.rcParams.get("text.color", "#1A1C2E"),
                 pad=8, loc="left")
    fig.tight_layout()
    return fig, ax


def _afficher_palette(palette: list) -> None:
    """Affichage terminal simple d'une palette."""
    _print_safe("  Couleurs : " + "  ".join(palette))


# ══════════════════════════════════════════════════════════════════════════════
# palette_safe — retourne une palette daltonisme-safe pour n séries
# ══════════════════════════════════════════════════════════════════════════════

def palette_safe(n: int = 8, type_daltonisme: str = "universel") -> list:
    """
    Retourne les n premières couleurs d'une palette daltonisme-safe.

    Parameters
    ----------
    n               : nombre de couleurs nécessaires (max 8)
    type_daltonisme : "universel" | "deuteranopie" | "protanopie"

    Exemple
    -------
    >>> colors = palette_safe(4)
    >>> barres(cats, vals, couleur=colors[0])
    """
    mapping = {
        "universel":   THEMES["daltonisme_safe"]["palette"],
        "deuteranopie": THEMES["deuteranopie"]["palette"],
        "protanopie":  [
            "#0077BB", "#CC3311", "#EE7733",
            "#009988", "#BBBBBB", "#EE3377",
            "#33BBEE", "#000000",
        ],
    }
    base = mapping.get(type_daltonisme, mapping["universel"])
    if n > len(base):
        _print_safe(f"⚠ Seulement {len(base)} couleurs disponibles pour '{type_daltonisme}'.")
    return base[:n]


# ══════════════════════════════════════════════════════════════════════════════
# Utilitaires internes
# ══════════════════════════════════════════════════════════════════════════════

def _trouver_theme(nom: str) -> dict:
    """Recherche un thème par clé exacte ou correspondance partielle."""
    if nom in THEMES:
        return THEMES[nom]
    # Recherche floue
    matches = [k for k in THEMES if nom.lower() in k.lower()]
    if len(matches) == 1:
        return THEMES[matches[0]]
    if len(matches) > 1:
        raise ValueError(
            f"Thème '{nom}' ambigu. Correspondances : {matches}\n"
            f"Appelez lister() pour voir tous les thèmes."
        )
    raise ValueError(
        f"Thème '{nom}' introuvable.\n"
        f"Thèmes disponibles : {list(THEMES.keys())}\n"
        f"Ou appelez lister() pour un aperçu."
    )
