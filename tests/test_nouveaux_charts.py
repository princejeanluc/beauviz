"""
Tests pour bump(), radar(), ridgeline() et le système style_kpi de layout_rapport().
Exécuter avec : py -3.11 -m pytest tests/test_nouveaux_charts.py -v
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
import numpy as np


# ── Fixtures communes ─────────────────────────────────────────────────────────

PERIODES = ["Q1", "Q2", "Q3", "Q4"]
SERIES_RANGS = {
    "Alpha": [1, 2, 1, 1],
    "Beta":  [2, 1, 2, 3],
    "Gamma": [3, 3, 3, 2],
}

CATEGORIES_RADAR = ["Vitesse", "Force", "Endurance", "Précision"]
SERIES_RADAR = {
    "Joueur A": [8, 7, 9, 6],
    "Joueur B": [6, 9, 7, 8],
}

NP_RNG = np.random.default_rng(42)
SERIES_DIST = {
    "Groupe A": NP_RNG.normal(5, 1, 150).tolist(),
    "Groupe B": NP_RNG.normal(7, 1.5, 150).tolist(),
    "Groupe C": NP_RNG.normal(4, 2, 150).tolist(),
}


# ══════════════════════════════════════════════════════════════════════════════
# Tests bump()
# ══════════════════════════════════════════════════════════════════════════════

def test_bump_retourne_fig_ax():
    from beau_graphique import bump
    result = bump(PERIODES, SERIES_RANGS)
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_bump_axe_y_inverse():
    """Rang 1 doit apparaître en haut (ymin > ymax en coordonnées matplotlib)."""
    from beau_graphique import bump
    fig, ax = bump(PERIODES, SERIES_RANGS)
    ymin, ymax = ax.get_ylim()
    assert ymin > ymax, "L'axe Y doit être inversé (rang 1 en haut)"
    plt.close("all")


def test_bump_nombre_series_scatter():
    """Un scatter par entité × périodes."""
    from beau_graphique import bump
    from matplotlib.collections import PathCollection
    fig, ax = bump(PERIODES, SERIES_RANGS)
    collections = [c for c in ax.collections if isinstance(c, PathCollection)]
    assert len(collections) == len(SERIES_RANGS)
    plt.close("all")


def test_bump_sans_valeurs():
    """montrer_valeurs=False ne doit pas lever d'erreur."""
    from beau_graphique import bump
    fig, ax = bump(PERIODES, SERIES_RANGS, montrer_valeurs=False)
    assert ax is not None
    plt.close("all")


def test_bump_deux_periodes():
    """Fonctionne avec seulement 2 périodes (pas de spline cubique possible)."""
    from beau_graphique import bump
    fig, ax = bump(["A", "B"], {"X": [1, 2], "Y": [2, 1]})
    assert ax is not None
    plt.close("all")


def test_bump_couleurs_multiples():
    from beau_graphique import bump
    fig, ax = bump(PERIODES, SERIES_RANGS, couleurs_multiples=["#FF0000", "#00FF00", "#0000FF"])
    plt.close("all")


# ══════════════════════════════════════════════════════════════════════════════
# Tests radar()
# ══════════════════════════════════════════════════════════════════════════════

def test_radar_retourne_fig_ax():
    from beau_graphique import radar
    result = radar(CATEGORIES_RADAR, SERIES_RADAR)
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_radar_axe_polaire():
    """L'axe retourné doit être un axe polaire."""
    from beau_graphique import radar
    fig, ax = radar(CATEGORIES_RADAR, SERIES_RADAR)
    assert ax.name == "polar"
    plt.close("all")


def test_radar_vmax_explicite():
    from beau_graphique import radar
    fig, ax = radar(CATEGORIES_RADAR, {"A": [5, 5, 5, 5]}, vmax=10)
    rmin, rmax = ax.get_ylim()
    assert abs(rmax - 10) < 1e-6
    plt.close("all")


def test_radar_serie_unique():
    """Radar avec une seule série — pas de légende."""
    from beau_graphique import radar
    fig, ax = radar(CATEGORIES_RADAR, {"Solo": [6, 7, 8, 5]})
    assert ax is not None
    plt.close("all")


def test_radar_sans_remplissage():
    from beau_graphique import radar
    fig, ax = radar(CATEGORIES_RADAR, SERIES_RADAR, remplir=False)
    assert ax is not None
    plt.close("all")


# ══════════════════════════════════════════════════════════════════════════════
# Tests ridgeline()
# ══════════════════════════════════════════════════════════════════════════════

def test_ridgeline_retourne_fig_ax():
    from beau_graphique import ridgeline
    result = ridgeline(SERIES_DIST)
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_ridgeline_yticks_correspondent_aux_noms():
    from beau_graphique import ridgeline
    fig, ax = ridgeline(SERIES_DIST)
    labels = [t.get_text() for t in ax.get_yticklabels()]
    for nom in SERIES_DIST:
        assert nom in labels
    plt.close("all")


def test_ridgeline_serie_unique():
    from beau_graphique import ridgeline
    fig, ax = ridgeline({"Seul": NP_RNG.normal(0, 1, 100).tolist()})
    assert ax is not None
    plt.close("all")


def test_ridgeline_chevauchement_fort():
    from beau_graphique import ridgeline
    fig, ax = ridgeline(SERIES_DIST, chevauchement=1.5)
    assert ax is not None
    plt.close("all")


# ══════════════════════════════════════════════════════════════════════════════
# Tests style_kpi dans layout_rapport()
# ══════════════════════════════════════════════════════════════════════════════

KPIS_EXEMPLE = [
    {"label": "Ventes",  "valeur": "1,24 M", "delta": "+12 %", "positif": True,
     "couleur": "#4361EE"},
    {"label": "Marge",   "valeur": "23 %",   "delta": "−2 pts", "positif": False},
]


def test_layout_style_kpi_accent():
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(kpis=KPIS_EXEMPLE, style_kpi="accent")
    assert len(zones["kpis"]) == 2
    plt.close("all")


def test_layout_style_kpi_minimal():
    """Style minimal : pas de bordure, pas de barre d'accent."""
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(kpis=KPIS_EXEMPLE, style_kpi="minimal")
    for ax_k in zones["kpis"]:
        assert all(not sp.get_visible() for sp in ax_k.spines.values())
    plt.close("all")


def test_layout_style_kpi_simple():
    """Style simple : toutes les bordures visibles."""
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(kpis=KPIS_EXEMPLE, style_kpi="simple")
    for ax_k in zones["kpis"]:
        assert all(sp.get_visible() for sp in ax_k.spines.values())
    plt.close("all")


def test_layout_style_kpi_dict_brut():
    """Un dict brut doit être accepté et fusionné sur le preset accent."""
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(
        kpis=KPIS_EXEMPLE,
        style_kpi={"border": True, "accent_bar": False, "bg_fill": False},
    )
    assert len(zones["kpis"]) == 2
    plt.close("all")


def test_layout_style_kpi_inconnu_leve_erreur():
    from beau_graphique import layout_rapport
    with pytest.raises(ValueError, match="style_kpi inconnu"):
        layout_rapport(kpis=KPIS_EXEMPLE, style_kpi="fantaisie")
    plt.close("all")


def test_layout_kpi_couleur_accent():
    """La clé couleur= dans un KPI dict ne doit pas lever d'erreur."""
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(
        kpis=[{"label": "CA", "valeur": "1 M", "couleur": "#F72585"}],
        style_kpi="filled",
    )
    assert len(zones["kpis"]) == 1
    plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
