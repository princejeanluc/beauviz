"""
Tests de non-régression pour la Phase 2.
Exécuter avec : python -m pytest tests/test_phase2.py -v
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import pytest

# ── Tests dates ───────────────────────────────────────────────────────────────

def test_ligne_dates_python():
    from beau_graphique import init, ligne
    init()
    dates = [datetime.date(2024, m, 1) for m in range(1, 7)]
    fig, ax = ligne(x=dates, y_series={"A": [1,2,3,4,5,6]})
    assert 'ScalarFormatter' not in type(ax.xaxis.get_major_formatter()).__name__
    plt.close('all')

def test_ligne_dates_pandas():
    try:
        import pandas as pd
    except ImportError:
        pytest.skip("pandas non installé")
    from beau_graphique import ligne
    dates = list(pd.date_range("2022-01", periods=8, freq="ME"))
    fig, ax = ligne(x=dates, y_series={"B": list(range(8))})
    plt.close('all')

def test_ligne_entiers_inchangee():
    """Les entiers ne doivent pas être traités comme des dates."""
    from beau_graphique import ligne
    fig, ax = ligne(x=list(range(2015, 2025)),
                    y_series={"C": list(range(10))})
    assert 'DateFormatter' not in type(ax.xaxis.get_major_formatter()).__name__
    plt.close('all')

# ── Tests retour (fig, ax) ────────────────────────────────────────────────────

@pytest.mark.parametrize("fn_name,kwargs", [
    ("box_plot",   {"data": [[1,2,3,4,5],[3,4,5,6,7]], "categories": ["A","B"]}),
    ("violin",     {"data": [[1,2,3,4,5]*10, [3,4,5,6,7]*10], "categories": ["A","B"]}),
    ("waterfall",  {"categories": ["Revenus","Charges","Taxes"],
                    "valeurs": [100, -40, -15],
                    "total_debut": 0, "label_debut": "Départ"}),
    ("lollipop",   {"categories": ["A","B","C","D","E"],
                    "valeurs": [10,25,18,32,15]}),
    ("slope",      {"categories": ["X","Y","Z"],
                    "valeurs_gauche": [10,20,30],
                    "valeurs_droite": [15,18,35]}),
])
def test_retour_fig_ax(fn_name, kwargs):
    import beau_graphique as bg
    fn = getattr(bg, fn_name)
    result = fn(**kwargs)
    assert isinstance(result, tuple), f"{fn_name} doit retourner un tuple"
    assert len(result) == 2, f"{fn_name} doit retourner (fig, ax)"
    plt.close('all')

# ── Test facet ────────────────────────────────────────────────────────────────

def test_facet_avec_dataframe():
    try:
        import pandas as pd
    except ImportError:
        pytest.skip("pandas non installé")
    from beau_graphique import facet
    import numpy as np
    df = pd.DataFrame({
        "Mois": list(range(1,7)) * 3,
        "Ventes": np.random.randint(10, 50, 18),
        "Region": ["Nord"]*6 + ["Sud"]*6 + ["Est"]*6,
    })
    fig, axes = facet(df, x="Mois", y="Ventes", par="Region",
                      type_graphique="barres")
    assert fig is not None
    plt.close('all')

# ── Test paramètre ax= ────────────────────────────────────────────────────────

def test_ligne_accepte_ax_externe():
    from beau_graphique import ligne
    fig_ext, ax_ext = plt.subplots()
    fig, ax = ligne(x=[1,2,3], y_series={"A": [1,2,3]}, ax=ax_ext)
    assert ax is ax_ext, "ligne() doit tracer dans l'ax fourni"
    plt.close('all')

# ── Test compatibilité themes ─────────────────────────────────────────────────

def test_nouveaux_graphiques_respectent_theme():
    from themes import appliquer
    from beau_graphique import box_plot, waterfall
    appliquer("finance", verbose=False)
    fig, ax = box_plot(data=[[1,2,3,4,5],[3,4,5,6,7]])
    plt.close('all')
    fig, ax = waterfall(categories=["A","B"], valeurs=[10,-5],
                        total_debut=50, label_debut="Début")
    plt.close('all')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
