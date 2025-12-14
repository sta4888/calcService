class Level:
    def __init__(self, percent: float):
        self.percent = percent

    def diff(self, other: "Level") -> float:
        return max(self.percent - other.percent, 0)