"""
demo_mckinsey.py
================
Génère une figure de démonstration pour chacune des 4 fonctions McKinsey
(dot_plot_comparatif, bulle_4d, unit_chart, barres_connectees) avec des
données réalistes. Les images sont enregistrées dans demo_mckinsey_output/.

Usage
-----
    python demo_mckinsey.py
"""

import os
import matplotlib.pyplot as plt

from beau_graphique import init, dot_plot_comparatif, bulle_4d, unit_chart
from narratif import barres_connectees

DOSSIER_SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_mckinsey_output")


def main():
    os.makedirs(DOSSIER_SORTIE, exist_ok=True)
    init()

    fig1, _ = dot_plot_comparatif(
        colonnes={
            "News":           (0.05, 0.15),
            "Searches":       (0.08, 0.19),
            "Research":       (0.06, 0.09),
            "Patents":        (0.20, 0.30),
            "Equity invest.": (0.02, 0.02),
            "Talent demand":  (0.04, 0.05),
        },
        descriptions={
            "News":           "Press reports featuring trend-related phrases",
            "Searches":       "Search engine queries for terms related to trend",
            "Research":       "Scientific publications on topics associated with trend",
            "Patents":        "Patent filings for technologies related to trend",
            "Equity invest.": "Private and public market capital raises",
            "Talent demand":  "Ratio of skilled people to job vacancies",
        },
        label_avant="2020", label_apres="2024",
        titre="Score par vecteur (0 = faible ; 1 = élevé)",
    )
    fig1.savefig(os.path.join(DOSSIER_SORTIE, "dot_plot_comparatif.png"), dpi=120, bbox_inches="tight")
    plt.close(fig1)

    fig2, _ = bulle_4d(
        x=[0.9, 0.15, 0.1, 0.15, 0.2, 0.05, 0.6, 0.15, 0.1, 0.05],
        y=[0.9, 0.55, 0.4, 0.4, 0.35, 0.2, 0.35, 0.2, 0.1, 0.05],
        taille=[200, 10, 30, 50, 20, 15, 400, 25, 5, 2],
        couleur_var=[4, 3, 3, 3, 3, 2, 3, 2, 2, 1],
        labels=["IA", "Semi-conducteurs", "Connectivité", "Bioingénierie",
                "Cloud/Edge", "Robotique", "Énergie", "Mobilité",
                "Espace", "Agentic AI"],
        xlabel="Intérêt (0 = faible ; 1 = élevé)",
        ylabel="Innovation (0 = faible ; 1 = élevé)",
        label_taille="Investissement (Md$)",
        label_couleur="Niveau d'adoption",
        niveaux_couleur=[1, 2, 3, 4, 5],
        quadrants=True,
        titre="Innovation, intérêt, investissement et adoption — 2024",
    )
    fig2.savefig(os.path.join(DOSSIER_SORTIE, "bulle_4d.png"), dpi=120, bbox_inches="tight")
    plt.close(fig2)

    fig3a, _ = unit_chart(
        categories=["Python", "Comp. Science", "GPU", "C++", "ML", "Architectures", "Firmware"],
        valeurs=[37, 33, 30, 21, 17, 15, 6],
        mode="proportion",
        titre="Talent requis",
        sous_titre="% des offres d'emploi nécessitant cette compétence",
    )
    fig3a.savefig(os.path.join(DOSSIER_SORTIE, "unit_chart_proportion.png"), dpi=120, bbox_inches="tight")
    plt.close(fig3a)

    fig3b, _ = unit_chart(
        categories=["Python", "Comp. Science", "GPU", "C++", "ML", "Architectures", "Firmware"],
        valeurs=[0.5, 0.2, 0.1, 2.7, 0.0, 0.2, 0.4],
        mode="ratio",
        titre="Disponibilité du talent",
        sous_titre="ratio talent disponible / demande",
    )
    fig3b.savefig(os.path.join(DOSSIER_SORTIE, "unit_chart_ratio.png"), dpi=120, bbox_inches="tight")
    plt.close(fig3b)

    fig4, _ = barres_connectees(
        categories=["IA", "Cloud & Edge", "Cybersécurité", "Connectivité avancée"],
        periodes=["2022", "2023", "2024"],
        valeurs=[
            [295, 245, 290],
            [40, 63, 95],
            [55, 22, 79],
            [38, 46, 25],
        ],
        couleurs=["#003566", "#0077B6", "#0096C7", "#00B4D8"],
        titre="Les investissements equity ont augmenté dans 10 des 13 tendances tech en 2024",
        sous_titre="Investissements par tendance, 2022–2024 (Mds$)",
        note="Source : McKinsey Technology Trends Outlook 2024",
    )
    fig4.savefig(os.path.join(DOSSIER_SORTIE, "barres_connectees.png"), dpi=120, bbox_inches="tight")
    plt.close(fig4)

    print(f"✓ 5 figures de démonstration générées dans {DOSSIER_SORTIE}/")


if __name__ == "__main__":
    main()
