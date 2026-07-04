"""
export.py
=========
Utilitaires pour sauvegarder et exporter des graphiques beau_graphique.

Fonctions publiques
-------------------
    sauvegarder(fig, nom, dossier=".", fmt="png")
        → une figure dans un ou plusieurs formats.

    pdf_rapport(figures, nom, dossier=".")
        → plusieurs figures en PDF multi-pages.

    export_batch(figures, dossier=".", fmt="png")
        → dict {nom: fig} ou list[(nom, fig)] en masse.

Usage
-----
    from export import sauvegarder, pdf_rapport, export_batch

    fig, ax = barres(mois, ventes, titre="Ventes Q4")
    sauvegarder(fig, "ventes_q4", dossier="exports/")

    pdf_rapport([fig1, fig2, fig3], "rapport_q4", dossier="exports/",
                titre="Rapport commercial Q4 2024", auteur="Jean Luc")

    export_batch({"ventes": fig1, "parts": fig2}, dossier="exports/")
"""

import datetime
import os
import pathlib
import subprocess
import sys

# ── Résolution par défaut selon le format ────────────────────────────────────
_DPI_DEFAUT = {
    "png":  180,   # écran haute densité
    "jpg":  150,
    "jpeg": 150,
    "pdf":  150,   # presse PDF
    "eps":  150,
    "svg":  None,  # vectoriel : pas de dpi
}


# ══════════════════════════════════════════════════════════════════════════════
# Helpers internes
# ══════════════════════════════════════════════════════════════════════════════

def _fig(obj):
    """Extrait la Figure depuis (fig, ax) ou depuis une Figure seule."""
    if isinstance(obj, tuple) and len(obj) >= 1:
        f = obj[0]
        if hasattr(f, "savefig"):
            return f
    if hasattr(obj, "savefig"):
        return obj
    raise TypeError(
        f"Attendu une Figure matplotlib ou un tuple (fig, ax), reçu {type(obj).__name__}"
    )


def _resoudre_dossier(dossier) -> pathlib.Path:
    """Crée le répertoire de sortie si absent et retourne un Path."""
    p = pathlib.Path(dossier)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _ouvrir(chemin):
    """Ouvre le fichier dans l'application système par défaut."""
    chemin = str(chemin)
    if sys.platform == "win32":
        os.startfile(chemin)          # noqa: S606
    elif sys.platform == "darwin":
        subprocess.run(["open", chemin], check=False)
    else:
        subprocess.run(["xdg-open", chemin], check=False)


# ══════════════════════════════════════════════════════════════════════════════
# API publique
# ══════════════════════════════════════════════════════════════════════════════

def sauvegarder(fig, nom, dossier=".", fmt="png", dpi=None, ouvrir=False):
    """
    Sauvegarde une figure matplotlib dans un ou plusieurs formats.

    Parameters
    ----------
    fig     : Figure matplotlib **ou** tuple ``(fig, ax)`` retourné par
              les fonctions beau_graphique — les deux sont acceptés.
    nom     : Nom de fichier sans extension (ex: ``"ventes_q4"``).
    dossier : Répertoire de sortie.  Créé automatiquement si absent.
    fmt     : ``"png"`` | ``"svg"`` | ``"pdf"`` | ``"jpg"`` **ou**
              liste de formats, ex: ``["png", "svg"]``.
    dpi     : Résolution en ppp.  Défaut : 180 pour PNG, 150 pour PDF/JPG,
              pas de dpi pour SVG (vectoriel).
    ouvrir  : ``True`` → ouvre le premier fichier créé dans le viewer système.

    Returns
    -------
    ``pathlib.Path`` si un seul format, ``list[pathlib.Path]`` si plusieurs.

    Exemple
    -------
    >>> fig, ax = barres(mois, ventes, titre="Ventes Q4")
    >>> sauvegarder(fig, "ventes_q4")
    >>> sauvegarder(fig, "ventes_q4", dossier="exports/", fmt=["png", "svg"])
    >>> sauvegarder(fig, "slide", fmt="png", dpi=300, ouvrir=True)
    """
    figure = _fig(fig)
    dossier_p = _resoudre_dossier(dossier)
    formats = [fmt] if isinstance(fmt, str) else list(fmt)
    chemins = []

    for f in formats:
        f = f.lower().lstrip(".")
        resolution = dpi if dpi is not None else _DPI_DEFAUT.get(f, 180)
        chemin = dossier_p / f"{nom}.{f}"

        kw = dict(bbox_inches="tight")
        if resolution is not None:
            kw["dpi"] = resolution

        figure.savefig(chemin, **kw)
        chemins.append(chemin)
        print(f"  ✓ {chemin}")

    if ouvrir and chemins:
        _ouvrir(chemins[0])

    return chemins[0] if len(chemins) == 1 else chemins


def pdf_rapport(figures, nom, dossier=".", titre="", auteur="", dpi=150):
    """
    Regroupe plusieurs figures en un PDF multi-pages.

    Parameters
    ----------
    figures : ``list`` dont chaque élément est :

              * une Figure matplotlib ou un tuple ``(fig, ax)`` ;
              * un tuple ``(figure, "titre de la page")`` pour ajouter
                un sur-titre à cette page spécifique.

    nom     : Nom du fichier PDF sans extension.
    dossier : Répertoire de sortie.  Créé automatiquement si absent.
    titre   : Métadonnée *Title* du document PDF.
    auteur  : Métadonnée *Author* du document PDF.
    dpi     : Résolution des pages.

    Returns
    -------
    ``pathlib.Path`` du fichier créé.

    Exemple
    -------
    >>> figs = [
    ...     (fig1, "Vue d'ensemble — Douala"),
    ...     (fig2, "Détail par ville"),
    ...     fig3,                          # pas de sur-titre de page
    ... ]
    >>> chemin = pdf_rapport(figs, "rapport_q4", dossier="exports/",
    ...                      titre="Rapport Q4 2024", auteur="Jean Luc")
    """
    from matplotlib.backends.backend_pdf import PdfPages  # import local pour ne pas
                                                           # bloquer si PDF non dispo

    # Normaliser : chaque item → (Figure, titre_page)
    pages = []
    for item in figures:
        if isinstance(item, tuple) and len(item) == 2:
            a, b = item
            if isinstance(b, str):
                # (figure_ou_tuple, "titre page")
                pages.append((_fig(a), b))
            else:
                # (fig, ax) tuple de beau_graphique sans titre de page
                pages.append((_fig(item), ""))
        else:
            pages.append((_fig(item), ""))

    dossier_p = _resoudre_dossier(dossier)
    chemin = dossier_p / f"{nom}.pdf"

    with PdfPages(chemin) as pdf:
        meta = pdf.infodict()
        if titre:
            meta["Title"] = titre
        if auteur:
            meta["Author"] = auteur
        meta["CreationDate"] = datetime.datetime.now()
        meta["ModDate"] = datetime.datetime.now()

        for figure, titre_page in pages:
            if titre_page:
                figure.suptitle(titre_page, fontsize=11, y=1.01)
            pdf.savefig(figure, bbox_inches="tight", dpi=dpi)

    n = len(pages)
    print(f"  ✓ {chemin}  ({n} page{'s' if n > 1 else ''})")
    return chemin


def export_batch(figures, dossier=".", fmt="png", dpi=None):
    """
    Exporte plusieurs figures en masse.

    Parameters
    ----------
    figures : ``dict {nom: figure}`` **ou** ``list[(nom, figure)]``
              Les figures peuvent être des Figure matplotlib ou des tuples
              ``(fig, ax)`` retournés par les fonctions beau_graphique.
    dossier : Répertoire de sortie.  Créé automatiquement si absent.
    fmt     : Format ou liste de formats (ex: ``["png", "svg"]``).
    dpi     : Résolution (optionnel — utilise le défaut du format sinon).

    Returns
    -------
    ``list[pathlib.Path]`` de tous les fichiers créés.

    Exemple
    -------
    >>> export_batch(
    ...     {
    ...         "ventes_douala":  fig1,
    ...         "ventes_yaounde": fig2,
    ...         "parts_marche":   fig3,
    ...     },
    ...     dossier="exports/rapport_q4/",
    ...     fmt=["png", "svg"],
    ... )
    """
    items = list(figures.items()) if isinstance(figures, dict) else list(figures)
    fmt_label = fmt if isinstance(fmt, str) else "+".join(fmt)
    print(f"Export batch → {dossier}  ({len(items)} figure(s), fmt={fmt_label})")

    tous = []
    for nom, fig in items:
        res = sauvegarder(fig, nom, dossier=dossier, fmt=fmt, dpi=dpi)
        tous.extend(res if isinstance(res, list) else [res])

    print(f"  {len(tous)} fichier(s) créé(s).")
    return tous
