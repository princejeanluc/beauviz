"""
Tests pour beau_graphique.mekko() — version neutre (socle), sans focus/accent.
Duplique les assertions géométriques/validation de tests/test_mekko.py
(version narrative), adaptées à l'absence de focus.

Exécuter avec : python -m pytest tests/test_mekko_socle.py -v
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pytest

from beau_graphique import mekko, dashboard


# ── Smoke tests ──────────────────────────────────────────────────────────────

def test_retour_fig_ax():
    fig, ax = mekko(["A", "B"], [100, 200], {"X": [30, 10], "Y": [70, 90]})
    assert fig is not None
    assert hasattr(ax, "get_xlim")
    plt.close('all')


def test_ax_externe():
    fig, axes = plt.subplots(1, 2)
    fig2, ax2 = mekko(["A"], [100], {"X": [50], "Y": [50]}, ax=axes[0])
    assert ax2 is axes[0]
    plt.close('all')


def test_integration_dashboard():
    fig, axes = dashboard([
        {"type": "mekko", "categories": ["A", "B"], "poids": [100, 200],
         "segments": {"X": [30, 10], "Y": [70, 90]}},
    ], ncols=1)
    assert fig is not None
    plt.close('all')


# ── Géométrique ──────────────────────────────────────────────────────────────

def test_largeur_colonne_proportionnelle_au_poids():
    fig, ax = mekko(["A", "B"], [100, 300], {"X": [30, 10], "Y": [70, 90]})
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    largeurs_A = sorted({r.get_width() for r in rects if r.get_x() == 0.0})
    largeurs_B = sorted({r.get_width() for r in rects if r.get_x() > 0.0})
    assert largeurs_A == [100.0]
    assert largeurs_B == [300.0]
    plt.close('all')


def test_hauteurs_normalisees_a_100():
    fig, ax = mekko(["A"], [100], {"X": [30], "Y": [90]})  # total brut = 120
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    hauteurs = sorted(r.get_height() for r in rects)
    assert sum(hauteurs) == pytest.approx(100.0)
    assert hauteurs == [pytest.approx(25.0), pytest.approx(75.0)]
    plt.close('all')


def test_segments_colores_differemment():
    fig, ax = mekko(["A"], [100], {"X": [30], "Y": [30], "Z": [40]})
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    couleurs = {r.get_facecolor() for r in rects}
    assert len(couleurs) == 3  # une couleur par segment
    plt.close('all')


# ── Validation d'entrée ──────────────────────────────────────────────────────

def test_longueurs_incoherentes_categories_poids():
    with pytest.raises(ValueError):
        mekko(["A", "B"], [100], {"X": [1, 1]})


def test_poids_negatif_ou_nul_rejete():
    with pytest.raises(ValueError):
        mekko(["A", "B"], [100, -5], {"X": [1, 1]})
    with pytest.raises(ValueError):
        mekko(["A", "B"], [100, 0], {"X": [1, 1]})


def test_segment_longueur_incorrecte():
    with pytest.raises(ValueError):
        mekko(["A", "B"], [100, 200], {"X": [1, 1, 1]})


def test_segment_valeur_negative_rejetee():
    with pytest.raises(ValueError):
        mekko(["A", "B"], [100, 200], {"X": [1, -1]})


def test_colonne_somme_nulle_rejetee():
    with pytest.raises(ValueError):
        mekko(["A", "B"], [100, 200], {"X": [0, 5], "Y": [0, 5]})


def test_segments_vide_rejete():
    with pytest.raises(ValueError):
        mekko(["A"], [100], {})


# ── Compatibilité thème ──────────────────────────────────────────────────────

def test_compatible_theme_sombre():
    import themes
    themes.appliquer("sombre", verbose=False)
    try:
        fig, ax = mekko(["A", "B"], [100, 200], {"X": [30, 10], "Y": [70, 90]}, titre="t")
        titre_couleur = ax.title.get_color()
        assert titre_couleur != "#1A1C2E"  # couleur "texte" du thème clair
    finally:
        themes.reinitialiser(verbose=False)
    plt.close('all')
