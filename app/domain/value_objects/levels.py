from app.domain.value_objects.level import Level

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


def level_by_volume(volume: float) -> Level:
    percent = 0.0
    for threshold, p in LEVELS:
        if volume >= threshold:
            percent = p
    return Level(percent)