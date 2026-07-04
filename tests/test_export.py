"""
Tests pour export.py.
Exécuter avec : py -3.11 -m pytest tests/test_export.py -v
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest


def _fig_simple():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [4, 5, 6])
    return fig, ax


# ── sauvegarder ───────────────────────────────────────────────────────────────

def test_sauvegarder_png(tmp_path):
    from export import sauvegarder
    fig, ax = _fig_simple()
    chemin = sauvegarder(fig, "test", dossier=tmp_path, fmt="png")
    assert chemin.exists()
    assert chemin.suffix == ".png"
    plt.close("all")


def test_sauvegarder_accepte_tuple_fig_ax(tmp_path):
    """sauvegarder() accepte directement le tuple (fig, ax) de beau_graphique."""
    from export import sauvegarder
    fig_ax = _fig_simple()
    chemin = sauvegarder(fig_ax, "test_tuple", dossier=tmp_path)
    assert chemin.exists()
    plt.close("all")


def test_sauvegarder_multi_format(tmp_path):
    """Plusieurs formats créent autant de fichiers."""
    from export import sauvegarder
    fig, _ = _fig_simple()
    chemins = sauvegarder(fig, "multi", dossier=tmp_path, fmt=["png", "svg"])
    assert isinstance(chemins, list)
    assert len(chemins) == 2
    assert (tmp_path / "multi.png").exists()
    assert (tmp_path / "multi.svg").exists()
    plt.close("all")


def test_sauvegarder_cree_dossier(tmp_path):
    """Le répertoire de sortie est créé automatiquement."""
    from export import sauvegarder
    fig, _ = _fig_simple()
    dossier = tmp_path / "sous" / "dossier"
    sauvegarder(fig, "fig", dossier=dossier)
    assert dossier.exists()
    plt.close("all")


def test_sauvegarder_pdf(tmp_path):
    from export import sauvegarder
    fig, _ = _fig_simple()
    chemin = sauvegarder(fig, "rapport", dossier=tmp_path, fmt="pdf")
    assert chemin.exists()
    assert chemin.suffix == ".pdf"
    plt.close("all")


# ── pdf_rapport ───────────────────────────────────────────────────────────────

def test_pdf_rapport_basique(tmp_path):
    from export import pdf_rapport
    figs = [_fig_simple(), _fig_simple(), _fig_simple()]
    chemin = pdf_rapport(figs, "rapport", dossier=tmp_path)
    assert chemin.exists()
    assert chemin.suffix == ".pdf"
    # Vérifier que le PDF a du contenu
    assert chemin.stat().st_size > 1000
    plt.close("all")


def test_pdf_rapport_avec_titres_de_page(tmp_path):
    from export import pdf_rapport
    fig1, _ = _fig_simple()
    fig2, _ = _fig_simple()
    figs = [
        (fig1, "Vue d'ensemble"),
        (fig2, "Détail"),
    ]
    chemin = pdf_rapport(figs, "rapport_titres", dossier=tmp_path,
                         titre="Test", auteur="Pytest")
    assert chemin.exists()
    plt.close("all")


def test_pdf_rapport_mixte(tmp_path):
    """Mélange de Figure seule et de (Figure, titre)."""
    from export import pdf_rapport
    fig1, _ = _fig_simple()
    fig2, ax2 = _fig_simple()
    figs = [fig1, (fig2, "Avec titre")]
    chemin = pdf_rapport(figs, "mixte", dossier=tmp_path)
    assert chemin.exists()
    plt.close("all")


# ── export_batch ──────────────────────────────────────────────────────────────

def test_export_batch_dict(tmp_path):
    from export import export_batch
    figs = {
        "alpha": _fig_simple(),
        "beta":  _fig_simple(),
        "gamma": _fig_simple(),
    }
    chemins = export_batch(figs, dossier=tmp_path, fmt="png")
    assert len(chemins) == 3
    for nom in ("alpha", "beta", "gamma"):
        assert (tmp_path / f"{nom}.png").exists()
    plt.close("all")


def test_export_batch_liste_tuples(tmp_path):
    from export import export_batch
    figs = [("fig1", _fig_simple()), ("fig2", _fig_simple())]
    chemins = export_batch(figs, dossier=tmp_path)
    assert len(chemins) == 2
    plt.close("all")


def test_export_batch_multi_format(tmp_path):
    from export import export_batch
    figs = {"test": _fig_simple()}
    chemins = export_batch(figs, dossier=tmp_path, fmt=["png", "svg"])
    assert len(chemins) == 2
    plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
