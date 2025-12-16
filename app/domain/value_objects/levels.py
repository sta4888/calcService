from domain.value_objects.level import Level

LEVELS = [
    (0,    0.00),
    (100,  0.03),
    (200,  0.06),
    (400,  0.09),
    (800,  0.12),
    (1200, 0.15),
    (2000, 0.18),
    (3000, 0.21),
]

QUALIFICATIONS = [
    ("Hamkor", 0.00),
    ("Mentor", 0.20),
    ("Menejer", 0.35),
    ("Direktor", 0.45),
    ("Bronza", 0.55),
    ("Kumush", 0.65),
    ("Oltin", 0.75),
    ("Zumrad", 0.85),
    ("Brilliant", 0.90),
    ("Olmos", 0.95),
]

def qualification_by_percent(percent: float):
    for name, p in reversed(QUALIFICATIONS):
        if percent >= p:
            return name
    return "Hamkor"



def level_by_volume(volume: float) -> Level:
    percent = 0.0
    for threshold, p in LEVELS:
        if volume >= threshold:
            percent = p
    return Level(percent)