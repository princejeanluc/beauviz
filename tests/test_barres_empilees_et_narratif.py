"""
Tests pour barres_groupees empile/normalise et la cohérence thème de narratif.py.
Exécuter avec : py -3.11 -m pytest tests/test_barres_empilees_et_narratif.py -v
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest


GROUPES = {
    "Mobile":  [40, 50, 55, 60],
    "Desktop": [60, 50, 45, 40],
    "Tablette": [10, 15, 20, 25],
}
CATEGORIES = ["T1", "T2", "T3", "T4"]


# ══════════════════════════════════════════════════════════════════════════════
# barres_groupees — empilé / normalisé
# ══════════════════════════════════════════════════════════════════════════════

def test_barres_groupees_standard():
    from beau_graphique import barres_groupees
    fig, ax = barres_groupees(CATEGORIES, GROUPES)
    assert ax is not None
    plt.close("all")


def test_barres_groupees_empile():
    from beau_graphique import barres_groupees
    fig, ax = barres_groupees(CATEGORIES, GROUPES, empile=True)
    assert ax is not None
    plt.close("all")


def test_barres_groupees_normalise():
    """normalise=True → ylim ne dépasse pas 100."""
    from beau_graphique import barres_groupees
    fig, ax = barres_groupees(CATEGORIES, GROUPES, normalise=True)
    _, ymax = ax.get_ylim()
    assert abs(ymax - 100) < 1e-6
    plt.close("all")


def test_barres_groupees_empile_retourne_fig_ax():
    from beau_graphique import barres_groupees
    result = barres_groupees(CATEGORIES, GROUPES, empile=True)
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_barres_groupees_empile_background_transparent():
    from beau_graphique import barres_groupees
    fig, ax = barres_groupees(CATEGORIES, GROUPES, empile=True, background="transparent")
    assert fig.patch.get_alpha() == 0
    plt.close("all")


# ══════════════════════════════════════════════════════════════════════════════
# narratif.py — couplage thème
# ══════════════════════════════════════════════════════════════════════════════

def test_narratif_respecte_theme_dark():
    """Après init(theme='dark'), les fonctions narratif utilisent le fond sombre."""
    import beau_graphique as bg
    from narratif import barres_focus
    bg.init(theme="dark")
    fig, ax = barres_focus(["A", "B", "C"], [10, 30, 20], focus=1)
    fc = fig.get_facecolor()
    assert fc != (1.0, 1.0, 1.0, 1.0), "narratif doit suivre le thème dark"
    bg.init()
    plt.close("all")


def test_barres_focus_retourne_fig_ax():
    from narratif import barres_focus
    result = barres_focus(["Jan", "Fév", "Mar"], [42, 38, 71], focus=2)
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_barres_focus_horizontal():
    from narratif import barres_focus
    fig, ax = barres_focus(["A", "B", "C"], [10, 20, 30], focus=0, horizontal=True)
    assert ax is not None
    plt.close("all")


def test_barres_focus_background_transparent():
    from narratif import barres_focus
    fig, ax = barres_focus(["A", "B"], [10, 20], focus=0, background="transparent")
    assert fig.patch.get_alpha() == 0
    plt.close("all")


def test_ligne_focus_retourne_fig_ax():
    from narratif import ligne_focus
    result = ligne_focus(
        x=[2020, 2021, 2022],
        series={"France": [10, 12, 15], "Cameroun": [8, 14, 20]},
        focus_serie="Cameroun",
    )
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_comparaison_avant_apres_retourne_fig_ax():
    from narratif import comparaison_avant_apres
    result = comparaison_avant_apres(
        categories=["Conv.", "Panier"],
        avant=[3.2, 42], apres=[4.7, 55],
    )
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_barres_ranked_retourne_fig_ax():
    from narratif import barres_ranked
    result = barres_ranked(["A", "B", "C", "D"], [70, 90, 50, 80])
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_divergent_retourne_fig_ax():
    from narratif import divergent
    result = divergent(["Jan", "Fév", "Mar"], [-3.2, 5.1, 8.4])
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_bullet_chart_retourne_fig_axes():
    from narratif import bullet_chart
    result = bullet_chart([
        {"nom": "Conv.", "valeur": 4.7, "objectif": 5.0, "plages": [2, 4, 6]},
        {"nom": "Panier", "valeur": 68, "objectif": 75, "plages": [40, 60, 90]},
    ])
    assert isinstance(result, tuple) and len(result) == 2
    plt.close("all")


def test_bullet_chart_background():
    from narratif import bullet_chart
    fig, _ = bullet_chart(
        [{"nom": "KPI", "valeur": 5, "objectif": 8, "plages": [3, 6, 10]}],
        background="transparent",
    )
    assert fig.patch.get_alpha() == 0
    plt.close("all")


def test_barres_connectees_background():
    from narratif import barres_connectees
    fig, ax = barres_connectees(
        categories=["IA"], periodes=["2022", "2023"],
        valeurs=[[10, 20]], background="transparent",
    )
    assert fig.patch.get_alpha() == 0
    plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
