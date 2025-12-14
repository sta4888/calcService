from app.domain.models.member import Member
from app.domain.value_objects.levels import LEVELS

def get_level(volume: float) -> float:
    level = 0
    for threshold, percent in LEVELS:
        if volume >= threshold:
            level = percent
    return level


def calc_income(root: Member):
    # Личный бонус
    personal_bonus = root.lo * root.get_level()

    # Структурный бонус
    structure_bonus = sum(
        member.calc_structure_bonus(root.get_level()) for member in root.team
    )

    result = {
        "Имя": root.name,
        "ЛО": root.lo,
        "ГО": root.get_group_volume(),
        "Уровень (%)": root.get_level(),
        "Личный бонус": personal_bonus,
        "Структурный бонус": structure_bonus,
        "ИТОГО доход": personal_bonus + structure_bonus,
    }

    return result




# ====== КЛАСС УЧАСТНИКА СТРУКТУРЫ =======
class Member:
    def __init__(self, name, lo, team=None):
        """
        name — имя участника
        lo — личный объем
        team — список участников под ним (вложенная структура)
        """
        self.name = name
        self.lo = lo
        self.team = team if team else []

    def get_group_volume(self):
        """Считает групповой объем (личный + команда)."""
        return self.lo + sum(member.get_group_volume() for member in self.team)

    def get_level(self):
        """Возвращает уровень участника по ГО."""
        return get_level(self.get_group_volume())

    def calc_structure_bonus(self, upline_level):
        """
        Разница уровней для бонуса вышестоящего.
        Возвращает сумму бонусов со всей глубины.
        """
        my_level = self.get_level()
        diff = max(upline_level - my_level, 0)

        # Бонус с моего группового объема
        my_bonus = self.get_group_volume() * diff

        # Плюс бонус с глубины
        deep_bonus = sum(member.calc_structure_bonus(my_level) for member in self.team)

        return my_bonus + deep_bonus





# ====== ПРИМЕР ИСПОЛЬЗОВАНИЯ =======
if __name__ == "__main__":
    # Строим структуру
    structure = Member(
        name="Ты",
        lo=300,
        team=[
            Member("Партнёр 1", 600),
            Member("Партнёр 2", 200),
            Member("Партнёр 3", 500, team=[
                Member("Глубина 1", 350)
            ]),
        ],
    )

    result = calc_income(structure)

    # Красивый вывод
    for k, v in result.items():
        print(f"{k}: {v}")
