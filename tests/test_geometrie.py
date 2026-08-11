"""
Tests géométriques — vérifient les coordonnées réelles des artistes matplotlib,
pas seulement l'absence de crash. Ciblent les fonctions où une régression
visuelle silencieuse s'est déjà produite (voir CONTEXT.md) ou serait grave.

Exécuter avec : python -m pytest tests/test_geometrie.py -v
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from beau_graphique import (
    tendances_comparatives, tendances_grille,
    waterfall, dot_plot_comparatif, bulle_4d,
)


# ── tendances_comparatives / tendances_grille ───────────────────────────────
# Régression connue : le polygone doit avoir exactement 5 sommets distincts
# (xl,0) → (xl,h0) → (xm,h1) → (xr,h2) → (xr,0), jamais un "plateau" plat
# entre deux sommets intermédiaires. matplotlib ferme le Polygon en répétant
# le premier sommet en 6e position.

def test_tendances_comparatives_polygone_5_sommets():
    items = [{"nom": "A", "valeurs": [95, 79, 117], "deltas": [-17, 48], "cumul": 22}]
    fig, axes = tendances_comparatives(items, ncols=1)
    ax = axes[0]
    polys = [p for p in ax.patches if isinstance(p, mpatches.Polygon)]
    assert len(polys) == 1
    xy = polys[0].get_xy()
    assert len(xy) == 6, "5 sommets + fermeture (répétition du 1er point)"
    ys = [pt[1] for pt in xy[:5]]
    assert ys == [0, 95, 79, 117, 0], (
        "les 3 sommets intermédiaires doivent reprendre exactement les valeurs "
        "d'entrée — un bug de géométrie (plateau plat) les ferait dévier"
    )
    plt.close('all')


def test_tendances_grille_barres_plates_hauteur_correcte():
    # tendances_grille() dessine des barres à sommet plat reliées par des
    # pentes diagonales (géométrie différente de tendances_comparatives, et
    # légitimement plate ici) — chaque valeur doit apparaître deux fois
    # consécutives (les 2 coins du sommet de sa barre), sans décalage.
    items = [{"nom": "A", "valeurs": [10, 25, 15], "deltas": [150, -40], "cumul": 50}]
    fig, axes = tendances_grille(items, ncols=1)
    ax = axes[0]
    polys = [p for p in ax.patches if isinstance(p, mpatches.Polygon)]
    assert len(polys) == 1
    xy = polys[0].get_xy()
    ys_top = [pt[1] for pt in xy[:6]]  # 3 barres x 2 coins de sommet
    assert ys_top == [10, 10, 25, 25, 15, 15]
    assert xy[6][1] == 0.0 and xy[7][1] == 0.0  # retour à la base après le dernier sommet
    plt.close('all')


# ── waterfall ────────────────────────────────────────────────────────────────
# Régression visée : les barres doivent former un pont cumulatif continu —
# chaque barre intermédiaire doit couvrir exactement [min(avant,après),
# max(avant,après)] de la valeur cumulée, sans écart ni chevauchement.

def test_waterfall_continuite_cumulative():
    categories = ["Nouveaux clients", "Churn", "Upsell"]
    valeurs = [80, -45, 30]
    fig, ax = waterfall(categories, valeurs, total_debut=500, total_fin=565)
    rects = [p for p in ax.patches if isinstance(p, mpatches.Rectangle)]
    assert len(rects) == 5  # départ + 3 contributions + arrivée

    cumul = 500.0
    attendus = [(0.0, 500.0)]  # barre de départ : [0, total_debut]
    for v in valeurs:
        avant = cumul
        cumul += v
        attendus.append((min(avant, cumul), max(avant, cumul)))
    attendus.append((0.0, 565.0))  # barre d'arrivée : [0, total_fin]

    for rect, (bas, haut) in zip(rects, attendus):
        assert rect.get_y() == bas
        assert rect.get_y() + rect.get_height() == haut
    plt.close('all')


# ── dot_plot_comparatif ──────────────────────────────────────────────────────
# Régression visée : le point creux (avant) et le point plein (après) doivent
# être positionnés à leurs valeurs Y réelles, pas interverties ou confondues.

def test_dot_plot_comparatif_positions_avant_apres():
    fig, ax = dot_plot_comparatif(colonnes={"A": (0.05, 0.20), "B": (0.10, 0.10)})
    scatters = [c for c in ax.collections if c.get_offsets().shape[0] == 1]
    # 2 colonnes x 2 points (avant + après) = 4 scatters ponctuels
    assert len(scatters) == 4
    ys_col_a = sorted(c.get_offsets()[0][1] for c in scatters
                       if c.get_offsets()[0][0] == 0.0)
    assert ys_col_a == [0.05, 0.20], "les points de la colonne A doivent être à 0.05 et 0.20"
    plt.close('all')


# ── bulle_4d ──────────────────────────────────────────────────────────────────
# Régression visée : la taille de chaque bulle doit suivre l'ordre des valeurs
# d'entrée — pas un ordre trié ou décalé par un bug d'indexation.

def test_bulle_4d_ordre_tailles():
    fig, ax = bulle_4d(x=[1, 2, 3], y=[1, 2, 3],
                        taille=[10, 500, 100], couleur_var=[1, 2, 3])
    # Le scatter de données porte autant de points que d'entrées ; les scatters
    # de légende (taille/couleur) ont un nombre de points différent du dataset.
    data_scatter = next(c for c in ax.collections if len(c.get_sizes()) == 3)
    tailles = data_scatter.get_sizes()
    # taille=[10, 500, 100] → la 2e bulle doit être la plus grande, la 1re la
    # plus petite, dans l'ordre d'entrée (pas trié).
    assert tailles[1] > tailles[2] > tailles[0]
    plt.close('all')
