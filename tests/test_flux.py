"""
Tests pour flux() (diagramme de Sankey) — smoke tests, assertions géométriques
réelles sur les rubans (voir tests/test_geometrie.py pour la même philosophie
appliquée aux autres fonctions), validation des erreurs, compatibilité thème.

Exécuter avec : python -m pytest tests/test_flux.py -v
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pytest

from beau_graphique import flux, dashboard


# ── Smoke tests ──────────────────────────────────────────────────────────────

def test_retour_fig_ax():
    fig, ax = flux([("A", "B", 10), ("B", "C", 6), ("B", "D", 4)])
    assert fig is not None
    assert hasattr(ax, "get_xlim")
    plt.close('all')


def test_multi_colonnes():
    fig, ax = flux([
        ("Recherche", "Site A", 120), ("Pub", "Site A", 60),
        ("Site A", "Achat", 90), ("Site A", "Abandon", 90),
    ], titre="t", sous_titre="s", note="n")
    assert fig is not None
    plt.close('all')


def test_ax_externe():
    fig, axes = plt.subplots(1, 2)
    fig2, ax2 = flux([("A", "B", 10)], ax=axes[0])
    assert ax2 is axes[0]
    plt.close('all')


def test_integration_dashboard():
    fig, axes = dashboard([
        {"type": "flux", "liens": [("A", "B", 10), ("B", "C", 6)]},
    ], ncols=1)
    assert fig is not None
    plt.close('all')


# ── Géométrique — épaisseur des rubans proportionnelle aux valeurs ──────────

def test_epaisseur_rubans_proportionnelle():
    # Deux liens sortant du même nœud, valeurs dans un rapport 1:3 connu.
    fig, ax = flux([("A", "B", 10), ("A", "C", 30)])
    rubans = [p for p in ax.patches if isinstance(p, mpatches.PathPatch)]
    assert len(rubans) == 2

    epaisseurs = []
    for r in rubans:
        v = r.get_path().vertices
        # v[0] = coin haut côté source, v[7] = coin bas côté source (avant CLOSEPOLY)
        epaisseurs.append(round(v[0][1] - v[7][1], 6))

    epaisseurs.sort()
    assert epaisseurs[1] / epaisseurs[0] == pytest.approx(3.0)
    plt.close('all')


def test_hauteur_noeud_egale_max_entrees_sorties():
    # B reçoit 10 de A et 30 de C -> total_in=40 ; B n'a pas de sortie -> valeur=40
    fig, ax = flux([("A", "B", 10), ("C", "B", 30)])
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    hauteur_b = max(r.get_height() for r in rects)
    assert hauteur_b == pytest.approx(40.0)
    plt.close('all')


# ── Validation d'entrée ──────────────────────────────────────────────────────

def test_cycle_detecte():
    with pytest.raises(ValueError, match="cycle"):
        flux([("A", "B", 10), ("B", "A", 5)])


def test_valeur_negative_rejetee():
    with pytest.raises(ValueError):
        flux([("A", "B", -5)])


def test_valeur_nulle_rejetee():
    with pytest.raises(ValueError):
        flux([("A", "B", 0)])


def test_liens_vide_rejete():
    with pytest.raises(ValueError):
        flux([])


def test_noeud_manquant_de_la_liste_explicite():
    with pytest.raises(ValueError):
        flux([("A", "B", 10), ("B", "C", 5)], noeuds=["A", "B"])  # 'C' manquant


# ── Compatibilité thème ──────────────────────────────────────────────────────

def test_compatible_theme_sombre():
    import themes
    themes.appliquer("sombre", verbose=False)
    try:
        fig, ax = flux([("A", "B", 10), ("B", "C", 6)], titre="t")
        # le texte du titre doit reprendre la couleur claire du thème sombre,
        # pas rester sur la valeur du thème clair (régression du bug _T corrigé
        # le 2026-08-10 : appliquer() ne patchait pas bg._T)
        titre_text = next(t for t in fig.texts if t.get_text() == "t")
        assert titre_text.get_color() != "#1A1C2E"  # couleur "texte" du thème clair
    finally:
        themes.reinitialiser(verbose=False)
    plt.close('all')
