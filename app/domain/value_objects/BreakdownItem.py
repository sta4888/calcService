from dataclasses import dataclass
from typing import List

@dataclass
class BreakdownItem:
    description: str  # Описание строки
    volume: float     # Объем для расчета
    percent: float    # Процент
    money: int      # Деньги

@dataclass
class IncomeBreakdown:
    personal_items: List[BreakdownItem]      # Личные начисления
    group_items: List[BreakdownItem]         # Групповые начисления
    leader_items: List[BreakdownItem]        # Лидерские начисления
    total_money: int                       # Итоговая сумма