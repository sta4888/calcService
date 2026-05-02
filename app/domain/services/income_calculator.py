# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple

from domain.models.member import Member
from domain.value_objects.BreakdownItem import BreakdownItem, IncomeBreakdown
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS
from web.scheme.schemas import IncomeResponse


# ============== КОНСТАНТЫ ==============

VERON_PRICE = 7000           # 1 Veron = 7000 сум
ACTIVITY_THRESHOLD = 50      # минимум LO для активности
SIDE_VOLUME_THRESHOLD = 500  # минимум yonbosh (Shart 1B)

HAMKOR = QUALIFICATIONS[0]
MENTOR = QUALIFICATIONS[1]


class IncomeCalculator:
    def __init__(self):
        # Кэш квалификаций по всему дереву: {user_id: Qualification}
        # Заполняется лениво при обходе снизу вверх
        self._q_cache: Dict[int, Qualification] = {}

    # ===================================================================
    # АКТИВНОСТЬ
    # ===================================================================

    def _is_active(self, member: Member) -> bool:
        """Hamkor активен если за месяц набрал >= 50 LO."""
        return member.lo >= ACTIVITY_THRESHOLD

    # ===================================================================
    # КВАЛИФИКАЦИЯ (рекурсивно снизу вверх с кэшем)
    # ===================================================================

    def _qualification_of(self, member: Member) -> Qualification:
        """Возвращает финальную квалификацию участника. Кэширует результат."""
        if member.user_id in self._q_cache:
            return self._q_cache[member.user_id]

        # Сначала считаем для всех детей (post-order DFS)
        for child in member.team:
            self._qualification_of(child)

        q = self._compute_qualification(member)
        self._q_cache[member.user_id] = q
        return q

    def _compute_qualification(self, member: Member) -> Qualification:
        """Применяет два условия из PDF и возвращает максимальную подходящую Q."""
        # Неактивный → Hamkor
        if not self._is_active(member):
            return HAMKOR

        group_volume = member.group_volume()

        # Перебор статусов сверху вниз (от Olmos к Mentor)
        for q in reversed(QUALIFICATIONS):
            if q is HAMKOR:
                continue  # Hamkor — это дефолт без условий

            # Shart 1A: GO >= Q.min_points
            if group_volume < q.min_points:
                continue

            # Shart 1B: yonbosh(Q) >= 500
            if self._yonbosh(member, q) < SIDE_VOLUME_THRESHOLD:
                continue

            # Оба условия выполнены — это наш статус
            return q

        return HAMKOR

    def _yonbosh(self, member: Member, q: Qualification) -> float:
        """
        Yonbosh ball относительно квалификации Q.
        = LO + сумма GO детей, чей подтверждённый статус строго ниже Q.
        Дети, "закрывшие Q" (их статус >= Q), исключаются — они "ушли".
        """
        total = member.lo
        for child in member.team:
            child_q = self._q_cache[child.user_id]  # уже посчитан выше
            if child_q.min_points < q.min_points:
                total += child.group_volume()
        return total

    # ===================================================================
    # ЛИЧНЫЙ БОНУС
    # ===================================================================

    def _personal(
            self, member: Member, q: Qualification
    ) -> Tuple[float, BreakdownItem]:
        money = member.lo * q.personal_percent * VERON_PRICE
        item = BreakdownItem(
            description=f"Личный объём – {q.personal_percent * 100:.0f}%",
            volume=member.lo,
            percent=q.personal_percent,
            money=money,
        )
        return money, item

    # ===================================================================
    # КОМАНДНЫЙ БОНУС (farq foizi с компрессией)
    # ===================================================================

    def _team(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        """
        Каждый потомок c вносит вклад в командный бонус member'а:
            (member_q.team_percent - taken_in_chain) × c.LO × VERON_PRICE
        где taken_in_chain — максимальный team_percent среди c и всех
        предков c между c и member (исключая member). Если значение
        отрицательное — вклад нулевой.
        """
        total = 0.0
        items: List[BreakdownItem] = []

        def walk(node: Member, taken: float):
            """
            taken — макс. team_percent уже "съеденный" в цепочке
            от node вверх до member (не включая member).
            """
            nonlocal total

            for child in node.team:
                child_q = self._qualification_of(child)
                # Сам child тоже "съедает" свой процент
                child_taken = max(taken, child_q.team_percent)

                # Сколько member может забрать с LO этого ребёнка?
                if member_q.team_percent > child_taken and child.lo > 0:
                    diff = member_q.team_percent - child_taken
                    money = child.lo * diff * VERON_PRICE
                    total += money
                    items.append(BreakdownItem(
                        description=(
                            f"С {child_q.name} (ID:{child.user_id}) – "
                            f"{diff * 100:.1f}%"
                        ),
                        volume=child.lo,
                        percent=diff,
                        money=money,
                    ))

                # Рекурсивно глубже с обновлённым потолком
                walk(child, child_taken)

        walk(member, taken=0.0)
        return total, items

    # ===================================================================
    # ЛИДЕРСКИЙ БОНУС
    # ===================================================================

    def _leader(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        """
        Лидерский бонус идёт с GO веток, чей подтверждённый статус >= нашего.
        Условие: сам как минимум Mentor.
        """
        if member_q.min_points < MENTOR.min_points:
            return 0.0, []

        strong_go = 0.0
        for child in member.team:
            child_q = self._qualification_of(child)
            if child_q.min_points >= member_q.min_points:
                strong_go += child.group_volume()

        if strong_go == 0:
            return 0.0, []

        money = strong_go * member_q.mentor_percent * VERON_PRICE
        item = BreakdownItem(
            description=f"С сильных веток – {member_q.mentor_percent * 100:.0f}%",
            volume=strong_go,
            percent=member_q.mentor_percent,
            money=money,
        )
        return money, [item]

    # ===================================================================
    # ГЛАВНЫЙ ВХОД
    # ===================================================================

    def calculate(self, member: Member) -> IncomeResponse:
        # Сбрасываем кэш на каждом новом дереве, чтобы не мешало
        self._q_cache.clear()

        # Прогреваем кэш — посчитаем квалификации всех потомков
        member_q = self._qualification_of(member)

        group_volume = member.group_volume()
        yonbosh = self._yonbosh(member, member_q) if member_q is not HAMKOR \
            else self._yonbosh_for_display(member)

        # Если неактивен — все нули
        if not self._is_active(member):
            return self._zero_response(member, group_volume, yonbosh)

        # Считаем все три типа дохода
        personal_money, personal_item = self._personal(member, member_q)
        team_money, team_items = self._team(member, member_q)
        leader_money, leader_items = self._leader(member, member_q)

        total = personal_money + team_money + leader_money
        veron = member.lo * member_q.personal_percent

        breakdown = IncomeBreakdown(
            personal_items=[personal_item],
            group_items=team_items,
            leader_items=leader_items,
            total_money=total,
        )

        return IncomeResponse(
            user_id=member.user_id,
            qualification=member_q.name,
            lo=member.lo,
            go=group_volume,
            side_volume=yonbosh,
            points=group_volume,
            personal_bonus=member_q.personal_percent,
            structure_bonus=member_q.team_percent,
            mentor_bonus=member_q.mentor_percent,
            extra_bonus=member_q.extra_bonus,
            personal_money=int(round(personal_money)),
            group_money=int(round(team_money)),
            leader_money=int(round(leader_money)),
            side_vol_money=0,
            total_money=int(round(total)),
            veron=int(round(veron)),
            total_income=float(round(total)),
            branches_info=[],
        )

    # ===================================================================
    # ВСПОМОГАТЕЛЬНЫЕ
    # ===================================================================

    def _yonbosh_for_display(self, member: Member) -> float:
        """yonbosh для неактивного / Hamkor — просто LO + GO всех детей < Mentor."""
        total = member.lo
        for child in member.team:
            child_q = self._q_cache.get(child.user_id, HAMKOR)
            if child_q.min_points < MENTOR.min_points:
                total += child.group_volume()
        return total

    def _zero_response(
            self, member: Member, group_volume: float, yonbosh: float
    ) -> IncomeResponse:
        return IncomeResponse(
            user_id=member.user_id,
            qualification=HAMKOR.name,
            lo=member.lo,
            go=group_volume,
            side_volume=yonbosh,
            points=0,
            personal_bonus=0,
            structure_bonus=0,
            mentor_bonus=0,
            extra_bonus=HAMKOR.extra_bonus,
            personal_money=0,
            group_money=0,
            leader_money=0,
            side_vol_money=0,
            total_money=0,
            veron=0,
            total_income=0.0,
            branches_info=[],
        )

    # ===================================================================
    # ОТЧЁТ
    # ===================================================================

    def format_breakdown_report(self, breakdown: IncomeBreakdown) -> str:
        lines = ["Личный:"]
        for it in breakdown.personal_items:
            lines.append(
                f"  {it.volume:.0f} × {it.percent*100:.0f}% × {VERON_PRICE} "
                f"= {it.money:,.0f}"
            )

        if breakdown.group_items:
            lines.append("\nКомандный:")
            for it in breakdown.group_items:
                lines.append(
                    f"  {it.description}: {it.volume:.0f} × "
                    f"{it.percent*100:.1f}% × {VERON_PRICE} = {it.money:,.0f}"
                )

        if breakdown.leader_items:
            lines.append("\nЛидерский:")
            for it in breakdown.leader_items:
                lines.append(
                    f"  {it.description}: {it.volume:.0f} × "
                    f"{it.percent*100:.0f}% × {VERON_PRICE} = {it.money:,.0f}"
                )

        lines.append(f"\nИТОГО: {breakdown.total_money:,.0f}")
        return "\n".join(lines)


# =====================================================================
# DEMO
# =====================================================================

if __name__ == "__main__":
    from tests.domain.factories import m

    memb = m(4, lo=1228, team=[
        m(5, lo=500, team=[
            m(6, lo=1000, team=[
                m(14, lo=2000, team=[m(38, lo=0, team=[])]),
                m(15, lo=256, team=[
                    m(16, lo=1064, team=[]),
                    m(28, lo=236, team=[]),
                    m(29, lo=513, team=[m(30, lo=0, team=[])]),
                ]),
                m(33, lo=190, team=[]),
            ]),
            m(8, lo=257, team=[
                m(25, lo=217, team=[]),
                m(26, lo=93, team=[]),
                m(32, lo=1000, team=[m(41, lo=0, team=[])]),
            ]),
            m(10, lo=0, team=[
                m(12, lo=1000, team=[
                    m(13, lo=1022, team=[
                        m(34, lo=0, team=[m(50, lo=0, team=[])]),
                        m(35, lo=444, team=[m(49, lo=0, team=[])]),
                        m(36, lo=1000, team=[m(48, lo=0, team=[])]),
                    ]),
                    m(18, lo=0, team=[]),
                    m(37, lo=0, team=[]),
                ]),
            ]),
        ]),
        m(17, lo=0, team=[
            m(19, lo=1000, team=[
                m(20, lo=0, team=[]),
                m(42, lo=0, team=[m(46, lo=500, team=[])]),
            ]),
        ]),
        m(21, lo=0, team=[
            m(45, lo=67, team=[]),
            m(51, lo=560, team=[]),
        ]),
        m(22, lo=1000, team=[
            m(27, lo=1000, team=[m(31, lo=0, team=[])]),
        ]),
        m(43, lo=0, team=[]),
    ])

    calc = IncomeCalculator()
    res = calc.calculate(memb)
    print(res)