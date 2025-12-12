class Member:
    def __init__(self, name, lo, team=None, min_lo_active=100):
        self.name = name
        self.lo = lo
        self.team = team or []
        self.min_lo_active = min_lo_active

    def is_active(self):
        return self.lo >= self.min_lo_active

    def get_group_volume(self):
        return self.lo + sum(m.get_group_volume() for m in self.team)
