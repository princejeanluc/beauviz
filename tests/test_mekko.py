"""
Tests pour mekko() (Marimekko chart, narratif.py) — smoke tests, assertions
géométriques réelles (largeur de colonne, hauteurs normalisées), validation
des erreurs, comportement focus/gris, compatibilité thème.

Exécuter avec : python -m pytest tests/test_mekko.py -v
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pytest

from narratif import mekko, ACCENTS


# ── Smoke tests ──────────────────────────────────────────────────────────────

def test_retour_fig_ax_sans_focus():
    fig, ax = mekko(["A", "B"], [100, 200], {"X": [30, 10], "Y": [70, 90]})
    assert fig is not None
    assert hasattr(ax, "get_xlim")
    plt.close('all')


def test_retour_fig_ax_avec_focus():
    fig, ax = mekko(["A", "B"], [100, 200], {"X": [30, 10], "Y": [70, 90]}, focus="X")
    assert fig is not None
    plt.close('all')


def test_focus_liste():
    fig, ax = mekko(
        ["A", "B"], [100, 200],
        {"X": [30, 10], "Y": [40, 50], "Z": [30, 40]},
        focus=["X", "Z"],
    )
    assert fig is not None
    plt.close('all')


def test_ax_externe():
    fig, axes = plt.subplots(1, 2)
    fig2, ax2 = mekko(["A"], [100], {"X": [50], "Y": [50]}, ax=axes[0])
    assert ax2 is axes[0]
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
    # Valeurs brutes qui ne somment pas à 100 -> doit être normalisé.
    fig, ax = mekko(["A"], [100], {"X": [30], "Y": [90]})  # total brut = 120
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    hauteurs = sorted(r.get_height() for r in rects)
    assert sum(hauteurs) == pytest.approx(100.0)
    # 30/120*100 = 25, 90/120*100 = 75
    assert hauteurs == [pytest.approx(25.0), pytest.approx(75.0)]
    plt.close('all')


def test_rapport_segments_preserve_apres_normalisation():
    # Deux segments dans un rapport connu (1:3) doivent le rester après normalisation.
    fig, ax = mekko(["A"], [100], {"X": [10], "Y": [30]})
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    hauteurs = sorted(r.get_height() for r in rects)
    assert hauteurs[1] / hauteurs[0] == pytest.approx(3.0)
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


def test_focus_nom_inconnu_rejete():
    with pytest.raises(ValueError):
        mekko(["A"], [100], {"X": [50], "Y": [50]}, focus="Inconnu")


# ── Focus / gris ─────────────────────────────────────────────────────────────

def test_focus_colore_accent_reste_gris():
    accent = ACCENTS["rouge"]
    fig, ax = mekko(
        ["A"], [100], {"X": [30], "Y": [70]}, focus="X", accent=accent,
    )
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    couleurs = {r.get_facecolor() for r in rects}
    # 2 couleurs distinctes attendues : l'accent et le gris du thème
    assert len(couleurs) == 2
    plt.close('all')


def test_sans_focus_segments_colores_differemment():
    fig, ax = mekko(["A"], [100], {"X": [30], "Y": [30], "Z": [40]})
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    couleurs = {r.get_facecolor() for r in rects}
    assert len(couleurs) == 3  # une couleur par segment, pas de gris
    plt.close('all')


# ── Compatibilité thème ──────────────────────────────────────────────────────

def test_compatible_theme_sombre():
    import themes
    themes.appliquer("sombre", verbose=False)
    try:
        fig, ax = mekko(["A", "B"], [100, 200], {"X": [30, 10], "Y": [70, 90]},
                         focus="X", titre="t")
        titre_couleur = ax.title.get_color()
        assert titre_couleur != "#1A1C2E"  # couleur "texte" du thème clair
    finally:
        themes.reinitialiser(verbose=False)
    plt.close('all')
