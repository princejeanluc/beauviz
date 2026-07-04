"""
Tests pour layout_rapport() et _dessiner_kpi().
Exécuter avec : py -3.11 -m pytest tests/test_layout.py -v
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest


KPIS_EXEMPLE = [
    {"label": "Ventes",  "valeur": "1,24 M", "delta": "+12 %",   "positif": True},
    {"label": "Clients", "valeur": "4 832",  "delta": "+5 %",    "positif": True},
    {"label": "Marge",   "valeur": "23 %",   "delta": "−2 pts",  "positif": False},
]


def test_layout_retourne_fig_et_zones():
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(titre="Test", kpis=KPIS_EXEMPLE)
    assert hasattr(fig, "savefig")
    assert "graphiques" in zones and "kpis" in zones
    plt.close("all")


def test_layout_axes_graphiques_count():
    from beau_graphique import layout_rapport
    for n in (1, 2, 3):
        fig, zones = layout_rapport(n_graphiques=n)
        assert len(zones["graphiques"]) == n
        plt.close("all")


def test_layout_kpis_count():
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(kpis=KPIS_EXEMPLE)
    assert len(zones["kpis"]) == 3
    plt.close("all")


def test_layout_sans_kpis():
    """Sans KPIs la rangée de titre est absente — seulement les graphiques."""
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(titre="Titre simple", kpis=[], n_graphiques=2)
    assert len(zones["graphiques"]) == 2
    assert len(zones["kpis"]) == 0
    plt.close("all")


def test_layout_format_slide():
    from beau_graphique import layout_rapport
    fig, _ = layout_rapport(format="slide")
    w, h = fig.get_size_inches()
    assert abs(w - 13.33) < 0.1 and abs(h - 7.5) < 0.1
    plt.close("all")


def test_layout_figsize_prioritaire_sur_format():
    from beau_graphique import layout_rapport
    fig, _ = layout_rapport(figsize=(8, 5), format="slide")
    w, h = fig.get_size_inches()
    assert abs(w - 8) < 0.1 and abs(h - 5) < 0.1
    plt.close("all")


def test_layout_axes_utilisables_avec_barres():
    """Les axes retournés acceptent les fonctions beau_graphique via ax=."""
    from beau_graphique import layout_rapport, barres, init
    init()
    fig, zones = layout_rapport(
        titre="Test barres dans layout",
        kpis=[{"label": "KPI", "valeur": "42"}],
        n_graphiques=1,
    )
    barres(["A", "B", "C"], [10, 25, 18], ax=zones["graphiques"][0])
    assert len(zones["graphiques"][0].patches) == 3
    plt.close("all")


def test_layout_two_charts():
    from beau_graphique import layout_rapport, barres, ligne, init
    init()
    fig, zones = layout_rapport(
        titre="Deux graphiques",
        kpis=KPIS_EXEMPLE,
        n_graphiques=2,
    )
    barres(["X", "Y"], [10, 20], ax=zones["graphiques"][0])
    ligne(x=[1, 2, 3], y_series={"S": [1, 2, 3]}, ax=zones["graphiques"][1])
    plt.close("all")


def test_layout_kpi_sans_delta():
    """Un KPI sans delta ne lève pas d'erreur."""
    from beau_graphique import layout_rapport
    fig, zones = layout_rapport(kpis=[{"label": "Score", "valeur": "87"}])
    assert len(zones["kpis"]) == 1
    plt.close("all")


def test_layout_dark_theme():
    """layout_rapport() respecte le thème sombre actif."""
    from beau_graphique import layout_rapport, init
    init(theme="dark")
    fig, zones = layout_rapport(
        titre="Slide sombre",
        kpis=KPIS_EXEMPLE,
        n_graphiques=1,
    )
    assert fig.get_facecolor() != (1.0, 1.0, 1.0, 1.0)  # pas blanc
    init()  # reset
    plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
