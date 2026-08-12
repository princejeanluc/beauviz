"""
Tests pour nuage_annote(zones_colorees=..., zone_couleurs=...) — rectangles
translucides remplissant les 4 quadrants (voir tests/test_geometrie.py pour
la même philosophie de vérification géométrique réelle).

Exécuter avec : python -m pytest tests/test_nuage_annote_zones.py -v
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pytest

from narratif import nuage_annote


X = [22, 45, 78, 31, 60]
Y = [3.2, 1.8, 4.5, 2.1, 3.8]
LABELS = ["A", "B", "C", "D", "E"]


def _rectangles(ax):
    return [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]


def test_zones_colorees_ajoute_4_rectangles():
    fig, ax = nuage_annote(X, Y, LABELS, quadrants=True, zones_colorees=True)
    assert len(_rectangles(ax)) == 4
    plt.close('all')


def test_sans_zones_colorees_aucun_rectangle():
    fig, ax = nuage_annote(X, Y, LABELS, quadrants=True, zones_colorees=False)
    assert len(_rectangles(ax)) == 0
    plt.close('all')


def test_zones_colorees_sans_quadrants_ignore_silencieusement():
    # zones_colorees=True mais quadrants=False (défaut) -> pas d'erreur, pas de rectangle
    fig, ax = nuage_annote(X, Y, LABELS, zones_colorees=True)
    assert len(_rectangles(ax)) == 0
    plt.close('all')


def test_zone_couleurs_personnalisees_appliquees():
    couleurs = ("#E63946", "#2DC653", "#A8ABBC", "#F4A261")
    fig, ax = nuage_annote(X, Y, LABELS, quadrants=True, zones_colorees=True,
                            zone_couleurs=couleurs)
    rects = _rectangles(ax)
    assert len(rects) == 4
    # les facecolors doivent correspondre aux 4 couleurs demandées (RGBA)
    import matplotlib.colors as mcolors
    attendues = {mcolors.to_rgba(c, alpha=0.10) for c in couleurs}
    obtenues = {r.get_facecolor() for r in rects}
    assert obtenues == attendues
    plt.close('all')


def test_zones_couvrent_les_quadrants_corrects():
    # Les 4 rectangles doivent couvrir exactement les 4 quadrants délimités
    # par les médianes (pas de chevauchement, pas de trou).
    import numpy as np
    fig, ax = nuage_annote(X, Y, LABELS, quadrants=True, zones_colorees=True)
    rects = _rectangles(ax)
    xm, ym = np.median(X), np.median(Y)
    coins = sorted((round(r.get_x(), 4), round(r.get_y(), 4)) for r in rects)
    xs_gauche = {c[0] for c in coins}
    ys_bas = {c[1] for c in coins}
    assert len(xs_gauche) == 2  # deux bords gauche distincts (avant/après xm)
    assert len(ys_bas) == 2     # deux bords bas distincts (avant/après ym)
    plt.close('all')
