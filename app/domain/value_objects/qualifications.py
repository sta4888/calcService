from domain.value_objects.qualification import Qualification

QUALIFICATIONS = [
    Qualification("Hamkor", 0, 0.40, 0.00, 0.00, "-"),
    Qualification("Mentor", 500, 0.40, 0.20, 0.02, "Par dazmol"),
    Qualification("Menejer", 1_500, 0.40, 0.35, 0.03, "Changyutgich"),
    Qualification("Direktor", 3_500, 0.40, 0.45, 0.04, "Televizor smart-32"),
    Qualification("Bronza", 10_000, 0.40, 0.55, 0.05, "Gaz plita"),
    Qualification("Kumush", 25_000, 0.40, 0.65, 0.06, "Konditsioner"),
    Qualification("Oltin", 50_000, 0.40, 0.75, 0.07, "Kir yuvadigan mashina"),
    Qualification("Zumrad", 70_000, 0.40, 0.85, 0.08, "Chet el sayohati"),
    Qualification("Brilliant", 85_000, 0.40, 0.90, 0.09, "Onix avtomobili"),
    Qualification("Olmos", 100_000, 0.40, 0.95, 0.10, "Chery Tigo 7 Pro Max"),
]


def qualification_by_points(points: int) -> Qualification:
    for q in reversed(QUALIFICATIONS):
        if points >= q.min_points:
            return q

