# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple

from domain.models.member import Member
from domain.value_objects.BreakdownItem import BreakdownItem, IncomeBreakdown
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import QUALIFICATIONS
from web.scheme.schemas import IncomeResponse


VERON_PRICE = 7000
ACTIVITY_THRESHOLD = 50
SIDE_VOLUME_THRESHOLD = 500

HAMKOR = QUALIFICATIONS[0]
MENTOR = QUALIFICATIONS[1]


class IncomeCalculator:
    def __init__(self):
        # Кэш итоговых квалификаций: {user_id: Qualification}
        self._q_cache: Dict[int, Qualification] = {}

    # ===================================================================
    # АКТИВНОСТЬ
    # ===================================================================

    def _is_active(self, member: Member) -> bool:
        return member.lo >= ACTIVITY_THRESHOLD

    # ===================================================================
    # КВАЛИФИКАЦИЯ
    # ===================================================================

    def _qualification_of(self, member: Member) -> Qualification:
        """Возвращает итоговую квалификацию участника. Кэширует."""
        if member.user_id in self._q_cache:
            return self._q_cache[member.user_id]

        # Сначала рекурсивно для детей (post-order)
        for child in member.team:
            self._qualification_of(child)

        q = self._compute_qualification(member)
        self._q_cache[member.user_id] = q
        return q

    def _potential_qualification(self, group_volume: float) -> Qualification:
        """По полному GO — самая высокая квалификация, под которую он попадает."""
        for q in reversed(QUALIFICATIONS):
            if group_volume >= q.min_points:
                return q
        return HAMKOR

    def _compute_qualification(self, member: Member) -> Qualification:
        # Неактивный → Hamkor
        if not self._is_active(member):
            return HAMKOR

        total_go = member.group_volume()
        q_pot = self._potential_qualification(total_go)

        if q_pot is HAMKOR:
            return HAMKOR

        # Сильные ветки — прямые дети с квалификацией >= q_pot
        strong_branches_go = 0.0
        clean_yonbosh = member.lo
        for child in member.team:
            child_q = self._q_cache[child.user_id]
            if child_q.min_points >= q_pot.min_points:
                # сильная — выбрасываем из всего
                strong_branches_go += child.group_volume()
            else:
                # обычная — добавляется в yonbosh
                clean_yonbosh += child.group_volume()

        clean_go = total_go - strong_branches_go

        # Может ли родитель сам закрыть q_pot?
        if clean_go >= q_pot.min_points and clean_yonbosh >= SIDE_VOLUME_THRESHOLD:
            return q_pot

        # Не может — ищем максимальную Q по clean_go и clean_yonbosh
        for q in reversed(QUALIFICATIONS):
            if q is HAMKOR:
                continue
            if clean_go >= q.min_points and clean_yonbosh >= SIDE_VOLUME_THRESHOLD:
                return q

        return HAMKOR

    # ===================================================================
    # СЛУЖЕБНОЕ — для отчёта/ответа
    # ===================================================================

    def _strong_branches(
            self, member: Member, q_pot: Qualification
    ) -> List[Member]:
        """Список сильных прямых веток относительно q_pot."""
        strong = []
        for child in member.team:
            child_q = self._q_cache[child.user_id]
            if child_q.min_points >= q_pot.min_points:
                strong.append(child)
        return strong

    def _yonbosh_for_response(self, member: Member) -> float:
        """yonbosh для отображения — LO + GO детей, не закрывших итоговую квалификацию."""
        member_q = self._q_cache[member.user_id]
        total = member.lo
        for child in member.team:
            child_q = self._q_cache[child.user_id]
            if child_q.min_points < member_q.min_points:
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
        total = 0.0
        items: List[BreakdownItem] = []

        def walk(node: Member, taken: float):
            nonlocal total
            for child in node.team:
                child_q = self._qualification_of(child)
                child_taken = max(taken, child_q.team_percent)

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

                walk(child, child_taken)

        walk(member, taken=0.0)
        return total, items

    # ===================================================================
    # ЛИДЕРСКИЙ БОНУС
    # ===================================================================

    def _leader(
            self, member: Member, member_q: Qualification
    ) -> Tuple[float, List[BreakdownItem]]:
        # Только если сам Mentor или выше
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
        self._q_cache.clear()
        member_q = self._qualification_of(member)

        group_volume = member.group_volume()
        yonbosh = self._yonbosh_for_response(member)

        if not self._is_active(member):
            return self._zero_response(member, group_volume, yonbosh)

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