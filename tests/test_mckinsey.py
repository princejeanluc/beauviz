"""
Tests de fumée pour les graphiques McKinsey :
dot_plot_comparatif, bulle_4d, unit_chart (beau_graphique.py)
et barres_connectees (narratif.py).

Lancer avec : pytest tests/test_mckinsey.py
Nécessite le projet installé (pip install -e .) ou les modules sur le PYTHONPATH.
"""

import matplotlib
matplotlib.use("Agg")  # pas d'affichage pendant les tests
import matplotlib.pyplot as plt
import pytest

from beau_graphique import dot_plot_comparatif, bulle_4d, unit_chart
from narratif import barres_connectees
from themes import appliquer, reinitialiser


def _est_figure_axes(resultat):
    assert isinstance(resultat, tuple) and len(resultat) == 2
    fig, ax = resultat
    assert hasattr(ax, "get_xlim")
    return fig, ax


# ── dot_plot_comparatif ──────────────────────────────────────────────────────

def test_dot_plot_comparatif_retourne_fig_ax():
    resultat = dot_plot_comparatif({"A": (0.1, 0.3), "B": (0.5, 0.7)})
    _est_figure_axes(resultat)
    plt.close("all")


def test_dot_plot_comparatif_parametres_vides():
    dot_plot_comparatif({"X": (0, 1)}, titre="", note="", figsize=None)
    plt.close("all")


def test_dot_plot_comparatif_avec_descriptions():
    fig, ax = dot_plot_comparatif(
        {"News": (0.05, 0.15), "Searches": (0.08, 0.19)},
        descriptions={"News": "Press reports featuring trend-related phrases"},
        label_avant="2020", label_apres="2024",
    )
    _est_figure_axes((fig, ax))
    plt.close("all")


def test_dot_plot_comparatif_compatible_themes():
    appliquer("finance", verbose=False)
    fig, ax = dot_plot_comparatif({"X": (0.1, 0.8), "Y": (0.3, 0.6)})
    _est_figure_axes((fig, ax))
    plt.close("all")
    reinitialiser()


def test_dot_plot_comparatif_background_transparent():
    """background="transparent" → alpha=0 sur figure et axes."""
    fig, ax = dot_plot_comparatif(
        {"A": (0.1, 0.3), "B": (0.2, 0.5)},
        background="transparent",
    )
    assert fig.patch.get_alpha() == 0
    assert ax.patch.get_alpha() == 0
    plt.close("all")


def test_dot_plot_comparatif_background_hex():
    """background hex → facecolor de la figure."""
    fig, ax = dot_plot_comparatif(
        {"A": (0.1, 0.3)},
        background="#0D1B2A",
    )
    assert fig.get_facecolor() != (1, 1, 1, 1)  # pas blanc
    plt.close("all")


def test_dot_plot_comparatif_label_plage_format():
    """label_plage supporte les tokens {vmin} et {vmax}."""
    fig, ax = dot_plot_comparatif(
        {"A": (0.0, 0.5), "B": (0.1, 0.3)},
        label_plage="Score ({vmin}–{vmax})",
        vmin=0, vmax=1,
    )
    # Le texte rendu doit apparaître dans les artists textuels de l'axe
    texts = [t.get_text() for t in ax.texts]
    assert any("Score (0–1)" in t for t in texts)
    plt.close("all")


def test_dot_plot_comparatif_montrer_plage():
    """montrer_plage=True ajoute un patch Rectangle dans l'axe."""
    from matplotlib.patches import Rectangle
    fig, ax = dot_plot_comparatif(
        {"A": (0.05, 0.25), "B": (0.1, 0.3)},
        montrer_plage=True, vmin=0, vmax=1,
    )
    rects = [p for p in ax.patches if isinstance(p, Rectangle)]
    assert len(rects) >= 1
    plt.close("all")


def test_dot_plot_comparatif_couleurs_decouplees():
    """couleur_avant et couleur_apres sont indépendants."""
    fig, ax = dot_plot_comparatif(
        {"A": (0.1, 0.4)},
        couleur_avant="#FF0000",
        couleur_apres="#0000FF",
    )
    assert ax is not None
    plt.close("all")


def test_dot_plot_comparatif_sans_fleche():
    """montrer_fleche=False ne doit pas lever d'erreur."""
    fig, ax = dot_plot_comparatif(
        {"A": (0.1, 0.4), "B": (0.2, 0.3)},
        montrer_fleche=False,
    )
    assert ax is not None
    plt.close("all")


def test_dot_plot_comparatif_vmin_vmax_explicites():
    """vmin/vmax explicites bornent l'axe Y."""
    fig, ax = dot_plot_comparatif(
        {"A": (0.2, 0.6)},
        vmin=0, vmax=1,
    )
    ylo, _ = ax.get_ylim()
    assert ylo == 0.0
    plt.close("all")


def test_dot_plot_compatibilite_couleur_legacy():
    """L'ancien paramètre couleur= fonctionne encore (rétrocompatibilité)."""
    fig, ax = dot_plot_comparatif(
        {"A": (0.1, 0.3)},
        couleur="#4361EE",
    )
    assert ax is not None
    plt.close("all")


# ── bulle_4d ──────────────────────────────────────────────────────────────────

def test_bulle_4d_retourne_fig_ax():
    resultat = bulle_4d(
        x=[0.9, 0.15, 0.1], y=[0.9, 0.55, 0.4],
        taille=[200, 10, 30], couleur_var=[4, 3, 3],
    )
    _est_figure_axes(resultat)
    plt.close("all")


def test_bulle_4d_avec_labels_et_quadrants():
    fig, ax = bulle_4d(
        x=[0.9, 0.15, 0.1, 0.05], y=[0.9, 0.55, 0.4, 0.2],
        taille=[200, 10, 30, 5], couleur_var=[4, 3, 3, 1],
        labels=["IA", "Semi-conducteurs", "Connectivité", "Espace"],
        xlabel="Intérêt", ylabel="Innovation",
        label_taille="Investissement", label_couleur="Adoption",
        quadrants=True,
    )
    _est_figure_axes((fig, ax))
    plt.close("all")


def test_bulle_4d_taille_constante_ne_plante_pas():
    # toutes les bulles ont la même taille → division par zéro potentielle
    fig, ax = bulle_4d(x=[0.1, 0.2], y=[0.3, 0.4], taille=[50, 50], couleur_var=[1, 1])
    _est_figure_axes((fig, ax))
    plt.close("all")


# ── unit_chart ────────────────────────────────────────────────────────────────

def test_unit_chart_mode_proportion():
    fig, ax = unit_chart(
        categories=["Python", "C++", "GPU"], valeurs=[37, 21, 30], mode="proportion",
    )
    _est_figure_axes((fig, ax))
    plt.close("all")


def test_unit_chart_mode_ratio():
    fig, ax = unit_chart(
        categories=["Python", "C++"], valeurs=[0.5, 2.7], mode="ratio",
    )
    _est_figure_axes((fig, ax))
    plt.close("all")


def test_unit_chart_mode_ratio_avec_reference():
    fig, ax = unit_chart(
        categories=["Python", "C++"], valeurs=[10, 27], reference=[20, 10], mode="ratio",
    )
    _est_figure_axes((fig, ax))
    plt.close("all")


def test_unit_chart_parametres_vides():
    unit_chart(categories=["A"], valeurs=[10], titre="", note="", figsize=None)
    plt.close("all")


# ── barres_connectees ──────────────────────────────────────────────────────────

def test_barres_connectees_retourne_fig_ax():
    resultat = barres_connectees(
        categories=["IA", "Cloud"],
        periodes=["2022", "2023", "2024"],
        valeurs=[[295, 245, 290], [40, 63, 95]],
    )
    _est_figure_axes(resultat)
    plt.close("all")


def test_barres_connectees_sans_delta():
    fig, ax = barres_connectees(
        categories=["IA"], periodes=["2022", "2023"], valeurs=[[10, 20]],
        afficher_delta=False,
    )
    _est_figure_axes((fig, ax))
    plt.close("all")


def test_barres_connectees_avec_groupes():
    fig, ax = barres_connectees(
        categories=["IA", "Cloud", "Robotique"],
        periodes=["2022", "2023"],
        valeurs=[[10, 20], [30, 25], [5, 8]],
        groupes={"Numérique": ["IA", "Cloud"], "Physique": ["Robotique"]},
    )
    _est_figure_axes((fig, ax))
    plt.close("all")


def test_barres_connectees_compatible_themes():
    appliquer("sombre", verbose=False)
    fig, ax = barres_connectees(
        categories=["IA"], periodes=["2022", "2023"], valeurs=[[10, 20]],
    )
    _est_figure_axes((fig, ax))
    plt.close("all")
    reinitialiser()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
