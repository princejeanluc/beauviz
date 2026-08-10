"""
pipeline.py
===========
Couche de résolution optionnelle entre vos données (DataFrame, dict, listes)
et les fonctions de beau_graphique / narratif.

Philosophie
-----------
  • Rien n'est obligatoire — chaque paramètre reste facultatif.
  • Si vous passez des listes brutes, ça marche exactement comme avant.
  • Si vous passez un DataFrame, la couche extrait, nettoie et rapporte
    automatiquement — puis passe le tout aux fonctions de graphique.
  • Aucune exception silencieuse : les problèmes de données sont signalés
    clairement avec des conseils, pas des erreurs cryptiques.

Fonctions publiques
-------------------
    depuis_df(df, x, y, groupe=None, ...)  → dict prêt pour ligne() / barres()
    inspecter(df)                           → rapport visuel sur les données
    nettoyer(df, ...)                       → DataFrame prêt à l'emploi
    resoudre(x, y, df, ...)                → résout x/y quelle que soit la source

Intégration transparente
------------------------
    # Avant (toujours valable)
    barres(categories=["A","B","C"], valeurs=[10,20,30])

    # Avec DataFrame (nouveau)
    barres(**depuis_df(df, x="Mois", y="Ventes"))

    # Ou directement via les wrappers
    barres_df(df, x="Mois", y="Ventes", groupe="Region")
"""

import datetime
import numpy as np
import warnings
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.dates as mdates
import matplotlib.ticker as mticker


def _print_safe(msg):
    """Affiche *msg* ; replie sur une version sans caractères non supportés
    si le terminal ne gère pas l'UTF-8 (ex: console Windows en cp1252 par
    défaut — sinon UnicodeEncodeError sur les symboles ✓/⚠/┌─┐ etc.)."""
    try:
        print(msg)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(msg.encode(enc, errors="replace").decode(enc))


# ── Import pandas / polars en optionnel ──────────────────────────────────────
try:
    import pandas as pd
    _PANDAS = True
except ImportError:
    _PANDAS = False

try:
    import polars as pl
    _POLARS = True
except ImportError:
    _POLARS = False


# ══════════════════════════════════════════════════════════════════════════════
# Types utilitaires
# ══════════════════════════════════════════════════════════════════════════════

_DF_TYPES = []
if _PANDAS:
    _DF_TYPES.append("pandas.core.frame.DataFrame")
if _POLARS:
    _DF_TYPES.append("polars.dataframe.frame.DataFrame")


def _is_df(obj) -> bool:
    """Vrai si obj est un DataFrame pandas ou polars."""
    return type(obj).__module__.split(".")[0] in ("pandas", "polars")


def _to_pandas(df):
    """Convertit polars → pandas si nécessaire."""
    if _POLARS and isinstance(df, pl.DataFrame):
        return df.to_pandas()
    return df


def _col_values(df, col: str) -> list:
    """Extrait une colonne en liste, quelle que soit la source."""
    df = _to_pandas(df)
    if col not in df.columns:
        raise KeyError(
            f"Colonne '{col}' introuvable.\n"
            f"Colonnes disponibles : {list(df.columns)}"
        )
    return df[col].tolist()


# ══════════════════════════════════════════════════════════════════════════════
# resoudre — cœur du système : accepte tout, retourne (x_list, y_list)
# ══════════════════════════════════════════════════════════════════════════════

def resoudre(
    x=None,
    y=None,
    df=None,
    col_x: str = None,
    col_y: str = None,
    trier: bool = False,
    dropna: bool = True,
) -> Tuple[list, list]:
    """
    Résout x et y depuis n'importe quelle combinaison de sources.

    Priorité de résolution :
      1. df + col_x + col_y  → extraits du DataFrame
      2. x liste + y liste   → utilisés tels quels
      3. x seul (dict)       → x = clés, y = valeurs
      4. y seul liste        → x = indices 0,1,2...

    Parameters
    ----------
    x, y        : listes, arrays, Series — données brutes (optionnel)
    df          : DataFrame pandas ou polars (optionnel)
    col_x       : nom de la colonne X dans df
    col_y       : nom de la colonne Y dans df
    trier       : trier par x croissant
    dropna      : supprimer les paires où x ou y est NaN

    Returns
    -------
    (x_list, y_list) — deux listes Python simples

    Exemples
    --------
    >>> x, y = resoudre(x=[1,2,3], y=[10,20,30])
    >>> x, y = resoudre(df=mon_df, col_x="Mois", col_y="Ventes")
    >>> x, y = resoudre(x={"Jan":10,"Fév":20})  # dict raccourci
    """
    # ── Cas 1 : DataFrame ───────────────────────────────────────────────────
    if df is not None and _is_df(df):
        if col_x is None or col_y is None:
            raise ValueError(
                "Quand df est fourni, col_x et col_y sont requis.\n"
                f"Colonnes disponibles : {list(_to_pandas(df).columns)}"
            )
        x_list = _col_values(df, col_x)
        y_list = _col_values(df, col_y)

    # ── Cas 2 : dict raccourci {label: valeur} ──────────────────────────────
    elif isinstance(x, dict):
        x_list = list(x.keys())
        y_list = list(x.values())

    # ── Cas 3 : x et y fournis directement ─────────────────────────────────
    elif x is not None and y is not None:
        x_list = list(x) if not isinstance(x, list) else x
        y_list = list(y) if not isinstance(y, list) else y
        if len(x_list) != len(y_list):
            raise ValueError(
                f"x ({len(x_list)} éléments) et y ({len(y_list)} éléments) "
                "doivent avoir la même longueur."
            )

    # ── Cas 4 : y seul → x = indices ───────────────────────────────────────
    elif y is not None:
        y_list = list(y) if not isinstance(y, list) else y
        x_list = list(range(len(y_list)))

    else:
        raise ValueError(
            "Impossible de résoudre les données.\n"
            "Fournissez : (x, y), (df, col_x, col_y), ou un dict {label: valeur}."
        )

    # ── Nettoyage NaN ───────────────────────────────────────────────────────
    if dropna:
        pairs = [
            (xi, yi) for xi, yi in zip(x_list, y_list)
            if not _is_nan(xi) and not _is_nan(yi)
        ]
        n_drop = len(x_list) - len(pairs)
        if n_drop > 0:
            warnings.warn(
                f"⚠ {n_drop} paire(s) supprimée(s) car x ou y est NaN.",
                stacklevel=3
            )
        if pairs:
            x_list, y_list = zip(*pairs)
            x_list, y_list = list(x_list), list(y_list)
        else:
            x_list, y_list = [], []

    # ── Tri optionnel ───────────────────────────────────────────────────────
    if trier and x_list:
        try:
            order = sorted(range(len(x_list)), key=lambda i: x_list[i])
            x_list = [x_list[i] for i in order]
            y_list = [y_list[i] for i in order]
        except TypeError:
            pass  # tri impossible (types mixtes) → on laisse

    return x_list, y_list


def _is_nan(v) -> bool:
    """Vrai si v est None ou float NaN."""
    if v is None:
        return True
    try:
        return float(v) != float(v)  # NaN != NaN
    except (TypeError, ValueError):
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Dates — détection et formatage de l'axe X sensible à la fréquence
# ══════════════════════════════════════════════════════════════════════════════

def _est_date(v) -> bool:
    """Vrai si v est une date ou datetime Python ou pandas Timestamp."""
    if isinstance(v, (datetime.date, datetime.datetime)):
        return True
    try:
        import pandas as pd
        if isinstance(v, pd.Timestamp):
            return True
    except ImportError:
        pass
    return False


def _liste_est_dates(lst) -> bool:
    """Vrai si la majorité des éléments non-None de lst sont des dates."""
    valeurs = [v for v in lst if v is not None]
    if not valeurs:
        return False
    return sum(1 for v in valeurs[:10] if _est_date(v)) >= min(3, len(valeurs))


def _formater_axe_dates(ax, x_list, freq: str = None) -> None:
    """
    Configure l'axe X comme axe temporel avec un format adapté à la fréquence
    réelle des données (jours, mois, trimestres, années) — plutôt que le
    format générique de matplotlib qui surcharge l'axe de chiffres bruts.

    Parameters
    ----------
    ax     : Axes matplotlib
    x_list : liste de dates (datetime.date/datetime ou pandas Timestamp)
    freq   : "D" | "M" | "Q" | "Y" — force la fréquence (sinon auto-détectée
             à partir de l'écart moyen entre points consécutifs)
    """
    if not _liste_est_dates(x_list):
        return

    dates = [v.to_pydatetime() if hasattr(v, "to_pydatetime") else v for v in x_list]

    if freq is None:
        if len(dates) > 1:
            deltas = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
            delta_moyen = sum(deltas) / len(deltas) if deltas else 30
        else:
            delta_moyen = 30
        if delta_moyen < 32:
            freq = "D"
        elif delta_moyen < 100:
            freq = "M"
        elif delta_moyen < 400:
            freq = "Q"
        else:
            freq = "Y"

    def _fmt_trimestre(x, pos=None):
        d = mdates.num2date(x)
        trimestre = (d.month - 1) // 3 + 1
        return f"T{trimestre} {d.year}"

    fmt_map = {
        "D": mdates.DateFormatter("%d %b"),
        "M": mdates.DateFormatter("%b %Y"),
        "Q": mticker.FuncFormatter(_fmt_trimestre),
        "Y": mdates.DateFormatter("%Y"),
    }

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(fmt_map.get(freq, fmt_map["M"]))

    if len(dates) > 6:
        for label in ax.get_xticklabels():
            label.set_rotation(35)
            label.set_ha("right")


# ══════════════════════════════════════════════════════════════════════════════
# depuis_df — extracteur multi-séries pour ligne() et barres_groupees()
# ══════════════════════════════════════════════════════════════════════════════

def depuis_df(
    df,
    x: str,
    y: Union[str, List[str]],
    groupe: str = None,
    agg: str = "sum",
    dropna: bool = True,
    trier: bool = False,
) -> dict:
    """
    Transforme un DataFrame en dict prêt à passer à ligne() ou barres_groupees().

    Parameters
    ----------
    df      : DataFrame pandas ou polars
    x       : colonne pour l'axe X
    y       : colonne(s) pour l'axe Y — str ou liste de str
    groupe  : colonne de regroupement → crée une série par valeur unique
    agg     : agrégation quand groupe est fourni : "sum" | "mean" | "count" | "max" | "min"
    dropna  : ignorer les lignes avec NaN dans x ou y
    trier   : trier par x

    Returns
    -------
    dict avec les clés :
      "x"        → liste de valeurs X
      "y_series" → dict {"Nom série": [valeurs]} — compatible ligne(), barres_groupees()
      "categories" → identique à "x" — compatible barres()
      "valeurs"    → première série (liste) — compatible barres() sans groupe

    Exemples
    --------
    >>> # Série simple
    >>> ligne(**depuis_df(df, x="Mois", y="Ventes"))

    >>> # Multi-colonnes Y
    >>> ligne(**depuis_df(df, x="Date", y=["Produit A", "Produit B"]))

    >>> # Groupé par catégorie
    >>> barres_groupees(**depuis_df(df, x="Trimestre", y="CA", groupe="Region"))
    """
    if not _is_df(df):
        raise TypeError(
            f"depuis_df() attend un DataFrame pandas/polars, reçu : {type(df).__name__}"
        )
    df_p = _to_pandas(df).copy()

    # ── Nettoyage NaN de base ───────────────────────────────────────────────
    cols_check = [x] + ([y] if isinstance(y, str) else y)
    if groupe:
        cols_check.append(groupe)
    if dropna:
        n_avant = len(df_p)
        df_p = df_p.dropna(subset=[c for c in cols_check if c in df_p.columns])
        n_drop = n_avant - len(df_p)
        if n_drop > 0:
            warnings.warn(f"⚠ {n_drop} ligne(s) supprimée(s) (NaN).", stacklevel=2)

    # ── Mode 1 : regroupement par colonne catégorielle ──────────────────────
    if groupe is not None:
        agg_fn = {"sum": "sum", "mean": "mean", "count": "count",
                  "max": "max", "min": "min"}.get(agg, "sum")
        y_col = y if isinstance(y, str) else y[0]
        pivot = df_p.groupby([x, groupe])[y_col].agg(agg_fn).unstack(fill_value=0)
        if trier:
            pivot = pivot.sort_index()
        x_vals = list(pivot.index)
        y_series = {str(col): list(pivot[col]) for col in pivot.columns}
        return {
            "x": x_vals,
            "categories": x_vals,
            "y_series": y_series,
            "valeurs": list(next(iter(y_series.values()))),
            "groupes": y_series,
        }

    # ── Mode 2 : multi-colonnes Y ───────────────────────────────────────────
    if isinstance(y, list):
        if trier:
            df_p = df_p.sort_values(x)
        x_vals = list(df_p[x])
        y_series = {col: list(df_p[col]) for col in y}
        return {
            "x": x_vals,
            "categories": x_vals,
            "y_series": y_series,
            "valeurs": list(df_p[y[0]]),
            "groupes": y_series,
        }

    # ── Mode 3 : colonne Y unique ────────────────────────────────────────────
    if trier:
        df_p = df_p.sort_values(x)
    x_vals  = list(df_p[x])
    y_vals  = list(df_p[y])
    return {
        "x": x_vals,
        "categories": x_vals,
        "y_series": {y: y_vals},
        "valeurs": y_vals,
        "groupes": {y: y_vals},
    }


# ══════════════════════════════════════════════════════════════════════════════
# inspecter — rapport rapide sur un DataFrame avant de tracer
# ══════════════════════════════════════════════════════════════════════════════

def inspecter(df, max_cols: int = 20) -> None:
    """
    Affiche un rapport visuel concis sur un DataFrame :
    types de colonnes, NaN, outliers évidents, doublons.

    Conçu pour être appelé en début d'analyse, avant les graphiques.

    Parameters
    ----------
    df       : DataFrame pandas ou polars
    max_cols : nombre max de colonnes affichées (tronqué si plus)

    Exemple
    -------
    >>> inspecter(df)
    ┌────────────────────────────────────────────────────────┐
    │  DataFrame — 500 lignes × 6 colonnes                  │
    ...
    """
    if not _is_df(df):
        _print_safe(f"⚠ inspecter() attend un DataFrame, reçu : {type(df).__name__}")
        return

    df_p = _to_pandas(df)
    n_rows, n_cols = df_p.shape
    cols = list(df_p.columns)[:max_cols]
    trunc = len(df_p.columns) > max_cols

    sep = "─" * 58
    _print_safe(f"┌{sep}┐")
    titre = f"  DataFrame — {n_rows:,} lignes × {n_cols} colonnes"
    if trunc:
        titre += f"  (affichage limité à {max_cols})"
    _print_safe(f"│{titre:<58}│")
    _print_safe(f"├{sep}┤")

    # En-tête colonnes
    _print_safe(f"│  {'Colonne':<22} {'Type':<12} {'NaN':>6} {'Unique':>8} {'Plage / Exemples':<18}│")
    _print_safe(f"├{sep}┤")

    for col in cols:
        serie = df_p[col]
        dtype = str(serie.dtype)[:11]
        n_nan = int(serie.isna().sum())
        pct_nan = n_nan / n_rows * 100 if n_rows else 0
        n_uniq = int(serie.nunique())

        nan_str = f"{n_nan} ({pct_nan:.0f}%)" if n_nan > 0 else "—"

        # Plage ou exemples
        if _PANDAS and _is_numeric(serie):
            vmin, vmax = serie.min(), serie.max()
            plage = f"{_fmt_num(vmin)} → {_fmt_num(vmax)}"
        else:
            exemples = [str(v) for v in serie.dropna().unique()[:3]]
            plage = ", ".join(exemples)
            if len(plage) > 18:
                plage = plage[:15] + "…"

        # Indicateur outlier pour numériques
        outlier_flag = ""
        if _PANDAS and _is_numeric(serie) and serie.dropna().shape[0] > 4:
            q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
            iqr = q3 - q1
            n_out = int(((serie < q1 - 1.5*iqr) | (serie > q3 + 1.5*iqr)).sum())
            if n_out > 0:
                outlier_flag = f" ⚡{n_out}"

        nan_display = f"{nan_str:>6}" if n_nan == 0 else f"\033[33m{nan_str:>6}\033[0m"
        _print_safe(
            f"│  {col:<22} {dtype:<12} {nan_str:>6} {n_uniq:>8}  "
            f"{plage:<18}{outlier_flag}│"
        )

    _print_safe(f"├{sep}┤")

    # Résumé
    total_nan  = int(df_p.isna().sum().sum())
    n_dup      = int(df_p.duplicated().sum())
    pct_complet = (1 - total_nan / (n_rows * n_cols)) * 100 if n_rows * n_cols else 100
    num_cols   = [c for c in df_p.columns if _is_numeric(df_p[c])]
    cat_cols   = [c for c in df_p.columns if not _is_numeric(df_p[c])]

    _print_safe(f"│  ✓ Complétude : {pct_complet:.1f}%   "
          f"NaN total : {total_nan}   "
          f"Doublons : {n_dup:<6}     │")
    _print_safe(f"│  Num : {len(num_cols)} col(s)   Cat : {len(cat_cols)} col(s)"
          f"{'':>30}│")
    _print_safe(f"└{sep}┘")

    # Conseils automatiques
    conseils = []
    if n_dup > 0:
        conseils.append(f"→ {n_dup} ligne(s) en doublon — utilisez nettoyer(df, dedup=True)")
    if total_nan > 0:
        cols_nan = df_p.columns[df_p.isna().any()].tolist()
        conseils.append(f"→ NaN dans : {cols_nan} — nettoyer(df, dropna=True) ou dropna='fill'")
    for col in num_cols[:max_cols]:
        serie = df_p[col]
        if serie.dropna().shape[0] > 4:
            q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
            iqr = q3 - q1
            n_out = int(((serie < q1 - 1.5*iqr) | (serie > q3 + 1.5*iqr)).sum())
            if n_out > 0:
                conseils.append(f"→ ⚡ '{col}' : {n_out} outlier(s) IQR — nettoyer(df, clip_outliers=True)")
    for c in conseils:
        _print_safe(f"  {c}")
    if not conseils:
        _print_safe("  ✓ Données propres, prêt à tracer.")


def _is_numeric(serie) -> bool:
    if not _PANDAS:
        return False
    import pandas as pd
    return pd.api.types.is_numeric_dtype(serie)


def _fmt_num(v) -> str:
    if v != v:  # NaN
        return "NaN"
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:.1f}k"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


# ══════════════════════════════════════════════════════════════════════════════
# nettoyer — préparation DataFrame avant tracé
# ══════════════════════════════════════════════════════════════════════════════

def nettoyer(
    df,
    dropna: Union[bool, str] = True,
    dedup: bool = False,
    clip_outliers: bool = False,
    cols_num: List[str] = None,
    renommer: Dict[str, str] = None,
    trier_par: str = None,
    verbose: bool = True,
) -> "pd.DataFrame":
    """
    Pipeline de nettoyage léger pour préparer un DataFrame au tracé.

    Parameters
    ----------
    dropna        : True → supprime les lignes avec NaN
                    "fill" → remplace les NaN numériques par la médiane,
                             les catégoriels par "Inconnu"
                    False  → ne touche pas aux NaN
    dedup         : supprimer les doublons exacts
    clip_outliers : écrêter les valeurs > Q3 + 3×IQR ou < Q1 - 3×IQR
                    (3×IQR = moins agressif que le standard 1.5)
    cols_num      : colonnes à traiter pour clip_outliers (défaut = toutes numériques)
    renommer      : dict {"ancien_nom": "nouveau_nom"} pour renommer des colonnes
    trier_par     : colonne sur laquelle trier le DataFrame
    verbose       : afficher le résumé des opérations

    Returns
    -------
    DataFrame pandas nettoyé

    Exemple
    -------
    >>> df_propre = nettoyer(df, dropna="fill", dedup=True,
    ...                      renommer={"rev": "Revenus"}, trier_par="Mois")
    """
    if not _is_df(df):
        raise TypeError(f"nettoyer() attend un DataFrame, reçu : {type(df).__name__}")

    df_p = _to_pandas(df).copy()
    ops  = []

    # ── Renommage ────────────────────────────────────────────────────────────
    if renommer:
        df_p = df_p.rename(columns=renommer)
        ops.append(f"renommage : {renommer}")

    # ── Doublons ─────────────────────────────────────────────────────────────
    if dedup:
        n = len(df_p)
        df_p = df_p.drop_duplicates()
        diff = n - len(df_p)
        if diff:
            ops.append(f"doublons supprimés : {diff}")

    # ── NaN ──────────────────────────────────────────────────────────────────
    if dropna is True:
        n = len(df_p)
        df_p = df_p.dropna()
        diff = n - len(df_p)
        if diff:
            ops.append(f"lignes NaN supprimées : {diff}")

    elif dropna == "fill":
        import pandas as pd
        for col in df_p.columns:
            if pd.api.types.is_numeric_dtype(df_p[col]):
                med = df_p[col].median()
                n_fill = df_p[col].isna().sum()
                if n_fill:
                    df_p[col] = df_p[col].fillna(med)
                    ops.append(f"NaN '{col}' → médiane ({med:.2f}) ×{n_fill}")
            else:
                n_fill = df_p[col].isna().sum()
                if n_fill:
                    df_p[col] = df_p[col].fillna("Inconnu")
                    ops.append(f"NaN '{col}' → 'Inconnu' ×{n_fill}")

    # ── Outliers ─────────────────────────────────────────────────────────────
    if clip_outliers:
        import pandas as pd
        target = cols_num or [c for c in df_p.columns if pd.api.types.is_numeric_dtype(df_p[c])]
        for col in target:
            q1, q3 = df_p[col].quantile(0.25), df_p[col].quantile(0.75)
            iqr = q3 - q1
            lo, hi = q1 - 3 * iqr, q3 + 3 * iqr
            n_clip = ((df_p[col] < lo) | (df_p[col] > hi)).sum()
            if n_clip:
                df_p[col] = df_p[col].clip(lo, hi)
                ops.append(f"outliers '{col}' écrêtés ×{n_clip} [{_fmt_num(lo)} – {_fmt_num(hi)}]")

    # ── Tri ──────────────────────────────────────────────────────────────────
    if trier_par and trier_par in df_p.columns:
        df_p = df_p.sort_values(trier_par).reset_index(drop=True)
        ops.append(f"trié par '{trier_par}'")

    if verbose:
        if ops:
            _print_safe(f"✓ nettoyer() — {len(df_p):,} lignes × {len(df_p.columns)} colonnes")
            for op in ops:
                _print_safe(f"  · {op}")
        else:
            _print_safe(f"✓ nettoyer() — aucune modification ({len(df_p):,} lignes)")

    return df_p


# ══════════════════════════════════════════════════════════════════════════════
# Wrappers directs — barres_df, ligne_df, nuage_df
# (sucre syntaxique : évitent le **depuis_df() intermédiaire)
# ══════════════════════════════════════════════════════════════════════════════

def _wrap_beau(fn_name: str, df, x: str, y, groupe: str = None,
               agg: str = "sum", dropna: bool = True,
               trier: bool = False, **kwargs):
    """Helper interne pour les wrappers df."""
    import beau_graphique as bg
    fn = getattr(bg, fn_name)
    data = depuis_df(df, x=x, y=y, groupe=groupe,
                     agg=agg, dropna=dropna, trier=trier)
    return fn(**{**data, **kwargs})


def barres_df(df, x: str, y: str, groupe: str = None,
              agg: str = "sum", trier: bool = False, **kwargs):
    """
    Version DataFrame de barres() ou barres_groupees().

    Si groupe est fourni → barres_groupees(), sinon → barres().

    Exemple
    -------
    >>> barres_df(df, x="Mois", y="Ventes", titre="CA mensuel")
    >>> barres_df(df, x="Région", y="CA", groupe="Produit",
    ...           titre="CA par région et produit")
    """
    return _wrap_beau("barres_groupees" if groupe else "barres",
                      df, x, y, groupe, agg, trier=trier, **kwargs)


def ligne_df(df, x: str, y, groupe: str = None,
             agg: str = "sum", trier: bool = False, **kwargs):
    """
    Version DataFrame de ligne().

    y peut être une colonne str ou une liste de colonnes.

    Exemple
    -------
    >>> ligne_df(df, x="Date", y="Revenus", titre="Évolution")
    >>> ligne_df(df, x="Date", y=["A","B","C"])
    >>> ligne_df(df, x="Date", y="Ventes", groupe="Region")
    """
    return _wrap_beau("ligne", df, x, y, groupe, agg, trier=trier, **kwargs)


def nuage_df(df, x: str, y: str, dropna: bool = True, **kwargs):
    """
    Version DataFrame de nuage().

    Exemple
    -------
    >>> nuage_df(df, x="Budget", y="Conversions", ligne_tendance=True)
    """
    import beau_graphique as bg
    x_vals, y_vals = resoudre(df=df, col_x=x, col_y=y, dropna=dropna)
    return bg.nuage(x=x_vals, y=y_vals, **kwargs)


def histogramme_df(df, col: str, dropna: bool = True, **kwargs):
    """
    Version DataFrame de histogramme().

    Exemple
    -------
    >>> histogramme_df(df, col="Salaire", bins=30, titre="Distribution des salaires")
    """
    import beau_graphique as bg
    vals = _col_values(df, col)
    if dropna:
        vals = [v for v in vals if not _is_nan(v)]
    return bg.histogramme(data=vals, **kwargs)
