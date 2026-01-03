from typing import List, Optional, Set
from domain.models.member import SIDE_VOLUME_THRESHOLD, Member
from domain.value_objects.BreakdownItem import BreakdownItem, IncomeBreakdown
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import qualification_by_points, QUALIFICATIONS
from web.scheme.schemas import IncomeResponse, BranchInfo

VERON_PRICE = 7000
HAMKOR_POINTS = QUALIFICATIONS[0].min_points


class IncomeCalculator:

    def _is_strong_member(self, member: Member) -> Qualification:
        group_volume = member.group_volume()
        base_qualification = qualification_by_points(int(group_volume))

        side_volume = self.calculate_side_volume(member, base_qualification)

        qualification, points = self._determine_qualification(
            member, group_volume, side_volume
        )

        # ⬇️ КРИТЕРИЙ СИЛЫ (ты можешь менять)
        return qualification
        # или: return points > 0
        # или: return qualification.level >= 1

    def _walk_branch(
            self,
            anchor: Member | None,
            member: Member,
            chain: list[Member],
            result: list[list[Member]],
    ):
        member_q = self._is_strong_member(member)

        # ⛔ сравнение с якорем
        if anchor is not None:
            anchor_q = self._is_strong_member(anchor)
            if anchor_q.min_points > member_q.min_points:
                return

        new_chain = chain.copy()

        # ✅ добавляем ТОЛЬКО если выше Hamkor
        if member_q.min_points > HAMKOR_POINTS:
            new_chain.append(member)

        # 🟢 1. ЕСЛИ ЛИСТ — ФИКСИРУЕМ ЦЕПОЧКУ
        if not member.team:
            if new_chain:
                result.append(new_chain)
            return

        # 🟢 2. ЕСЛИ СИЛЬНЕЕ ВСЕХ ДЕТЕЙ — ТОЖЕ ФИКСИРУЕМ
        if all(
                member_q.min_points > self._is_strong_member(child).min_points
                for child in member.team
        ):
            if new_chain:
                result.append(new_chain)
            return

        # ➡️ иначе идём глубже
        for child in member.team:
            self._walk_branch(
                anchor=member,
                member=child,
                chain=new_chain,
                result=result,
            )

    def collect_strong_members(self, root: Member) -> list[list[Member]]:
        result: list[list[Member]] = []

        for child in root.team:
            self._walk_branch(
                anchor=None,
                member=child,
                chain=[],
                result=result,
            )

        return result

    def _collect_branch_representatives(self, member: Member) -> list[Member]:
        # Базовый случай: лист
        if not member.team:
            # Если лист сильный - возвращаем его, иначе пустой список
            if self._is_strong_member(member):
                return [member]
            return []

        # Собираем представителей от всех детей
        child_reps: list[Member] = []
        for child in member.team:
            reps = self._collect_branch_representatives(child)
            child_reps.extend(reps)

        # Если нет представителей от детей - проверяем текущий элемент
        if not child_reps:
            return [member] if self._is_strong_member(member) else []

        # Проверяем, сильнее ли текущий член ВСЕХ найденных представителей
        is_member_strong = self._is_strong_member(member)
        if is_member_strong and all(self._is_stronger(member, rep) for rep in child_reps):
            # Родитель сильнее всех детей - берем только родителя
            return [member]

        # Иначе возвращаем представителей от детей
        return child_reps

    def _is_stronger(self, a: Member, b: Member) -> bool:
        qa = self._is_strong_member(a)
        qb = self._is_strong_member(b)
        return qa.min_points >= qb.min_points

    def _strong_branches_go(self, member: Member, qualification: Qualification) -> float:
        """Рассчитывает ГО сильных веток (квалификация >= родителя)"""
        strong_go = 0

        for branch in member.team:
            branch_go = branch.group_volume()
            branch_q = qualification_by_points(int(branch_go))

            if branch_q.min_points >= qualification.min_points:
                strong_go += branch_go

        return strong_go

    def _find_strongest_sub_branches(self, branch: Member) -> List[Member]:
        """
        Находит все САМЫЕ СИЛЬНЫЕ подветки в ветке, учитывая иерархию.
        Если есть несколько одинаково сильных квалификаций, выбирает ТОЛЬКО САМЫЕ ГЛУБОКИЕ.

        Пример:
        - Direktor (1-я линия) → Direktor (2-я линия) → Hamkor
        Вернет только Direktor (2-я линия)
        """

        # Вспомогательная функция для рекурсивного поиска
        def _find_deepest_strongest(node: Member, current_level: int) -> List[tuple[Member, int]]:
            """
            Возвращает список (подветка, уровень) самых глубоких сильных подветок.
            """
            result = []

            # Проверяем, есть ли у этой ветки еще более сильные подветки
            has_stronger_children = False
            child_results = []

            # Сначала проверяем всех детей
            for child in node.team:
                child_side = self._branch_side(child)
                child_q = qualification_by_points(int(child_side))
                node_side = self._branch_side(node)
                node_q = qualification_by_points(int(node_side))

                # Если у ребенка квалификация >= родителя, ищем у него
                if child_q.min_points >= node_q.min_points:
                    has_stronger_children = True
                    child_results.extend(_find_deepest_strongest(child, current_level + 1))

            # Если есть дети с такими же или лучшими квалификациями
            if has_stronger_children:
                # Находим максимальную квалификацию среди детей
                max_child_qualification = None
                for child, _ in child_results:
                    child_side = self._branch_side(child)
                    child_q = qualification_by_points(int(child_side))
                    if max_child_qualification is None or child_q.min_points > max_child_qualification.min_points:
                        max_child_qualification = child_q

                # Оставляем только детей с максимальной квалификацией
                filtered_children = []
                for child, level in child_results:
                    child_side = self._branch_side(child)
                    child_q = qualification_by_points(int(child_side))
                    if child_q.min_points == max_child_qualification.min_points:
                        filtered_children.append((child, level))

                return filtered_children
            else:
                # Если у этой ветки нет более сильных детей, это конечная сильная подветка
                return [(node, current_level)]

        # Запускаем поиск
        deepest_branches = _find_deepest_strongest(branch, 0)

        # Извлекаем только ветки (без уровней)
        result = [branch for branch, level in deepest_branches]

        return result

    def _branch_side(self, branch: Member) -> float:
        """Рекурсивно рассчитывает side volume ветки"""
        side = branch.lo

        for child in branch.team:
            child_side = self._branch_side(child)
            child_q = qualification_by_points(int(child_side))

            # Если child закрыл квалификацию — не учитываем
            if child_side >= SIDE_VOLUME_THRESHOLD and child_q.name != "Hamkor":
                continue

            side += child_side

        return side

    def _branch_side_contribution(
            self,
            branch: Member,
            parent_qualification: Qualification,
    ) -> float:
        """Определяет, сколько side volume ветки учитывается в side volume родителя"""
        branch_side = self._branch_side(branch)
        branch_side_q = qualification_by_points(int(branch_side))

        # 1️⃣ Ветка закрыта по side volume
        if branch_side >= SIDE_VOLUME_THRESHOLD and branch_side_q.name != "Hamkor":
            return 0

        # 2️⃣ Ветка сильнее или равна родителю
        if branch_side_q.min_points >= parent_qualification.min_points:
            return 0

        # 3️⃣ Обычная ветка
        return branch_side

    def calculate_side_volume(self, member: Member, qualification: Qualification) -> float:
        """Рассчитывает side volume участника"""
        side = member.lo

        for branch in member.team:
            contribution = self._branch_side_contribution(branch, qualification)
            side += contribution

        return side

    def _calculate_leader_money(
            self,
            member: Member,
            qualification: Qualification,
    ) -> float:
        """Рассчитывает деньги за лидерство (с сильных веток)"""
        strong_go = self._strong_branches_go(member, qualification)
        return strong_go * qualification.mentor_percent * VERON_PRICE

    def _calculate_money(
            self,
            member: Member,
            qualification: Qualification,
            side_volume: float,
    ) -> tuple[dict, List[BranchInfo], IncomeBreakdown]:
        """Рассчитывает все денежные компоненты и собирает информацию о ветках"""
        lo = member.lo

        # Личный объем
        lo_money = lo * qualification.personal_percent * VERON_PRICE
        side_vol = side_volume * qualification.team_percent * VERON_PRICE
        print(f"side_vol = {side_vol}")

        personal_items = [
            BreakdownItem(
                description=f"Личный объем – {qualification.personal_percent * 100:.0f}%",
                volume=lo,
                percent=qualification.personal_percent,
                money=lo_money
            )
        ]

        # Групповой объем
        go_money, branches_info, group_items = self._analyze_branches(
            member=member,
            parent_qualification=qualification,
            side_volume=side_volume,
        )

        # Деньги за лидерство
        leader_money, leader_items = self._calculate_leader_money_with_breakdown(member, qualification)

        # Итоговые суммы
        total_money = lo_money + leader_money + side_vol + (0 if go_money == side_vol else go_money)
        veron_money = lo * qualification.personal_percent

        money_data = {
            "lo": lo_money,
            "go": go_money,
            "leader_money": leader_money,
            "total": total_money,
            "side_vol_money": side_vol,
            "veron": veron_money,
        }

        breakdown = IncomeBreakdown(
            personal_items=personal_items,
            group_items=group_items,
            leader_items=leader_items,
            total_money=total_money
        )

        return money_data, branches_info, breakdown

    def _calculate_leader_money_with_breakdown(
            self,
            member: Member,
            qualification: Qualification,
    ) -> tuple[float, List[BreakdownItem]]:
        """Рассчитывает деньги за лидерство с детализацией"""
        strong_go = self._strong_branches_go(member, qualification)
        leader_money = strong_go * qualification.mentor_percent * VERON_PRICE

        leader_items = []
        if strong_go > 0:
            leader_items.append(
                BreakdownItem(
                    description=f"С сильных веток – {qualification.mentor_percent * 100:.0f}%",
                    volume=strong_go,
                    percent=qualification.mentor_percent,
                    money=leader_money
                )
            )

        return leader_money, leader_items

    def _determine_qualification(
            self,
            member: Member,
            group_volume: float,
            side_volume: float,
    ) -> tuple[Qualification, float]:
        """
        Определяет финальную квалификацию и points.
        Возвращает (qualification, points)
        """
        base_qualification = qualification_by_points(int(group_volume))

        # Проверяем, есть ли у родителя сильные ветки
        has_stronger_branches = False
        for branch in member.team:
            branch_side = self._branch_side(branch)
            branch_side_q = qualification_by_points(int(branch_side))

            # Ветка сильнее родителя (по side volume квалификации)
            if branch_side_q.min_points >= base_qualification.min_points:
                has_stronger_branches = True
                break

        # Определяем points для квалификации
        if side_volume >= SIDE_VOLUME_THRESHOLD and not has_stronger_branches:
            # Обычный случай: side ≥ 500 и нет сильных веток → берем GV
            points = group_volume
        else:
            # Либо side < 500, либо есть сильные ветки → берем side volume
            points = side_volume

        qualification = qualification_by_points(int(points))
        return qualification, points

    def calculate(self, member: Member) -> tuple[IncomeResponse, IncomeBreakdown]:
        """Рассчитывает доход и возвращает ответ с детализированным отчетом"""
        # Базовые объемы
        group_volume = member.group_volume()
        base_qualification = qualification_by_points(int(group_volume))

        # Side volume
        side_volume = self.calculate_side_volume(member, base_qualification)

        # Финальная квалификация
        qualification, points = self._determine_qualification(
            member, group_volume, side_volume
        )

        # Деньги, информация о ветках и детализация
        money, branches_info, breakdown = self._calculate_money(
            member, qualification, side_volume
        )

        # Округляем денежные значения до целых
        personal_money = int(round(money["lo"]))
        group_money = int(round(money["go"]))
        side_vol_money = int(round(money["side_vol_money"]))
        leader_money = int(round(money["leader_money"]))
        total_money = int(round(money["total"]))
        veron_money = int(round(money["veron"]))

        response = IncomeResponse(
            user_id=member.user_id,
            qualification=qualification.name,
            lo=member.lo,
            go=group_volume,
            side_volume=side_volume,
            points=points,
            personal_bonus=qualification.personal_percent,
            structure_bonus=qualification.team_percent,
            mentor_bonus=qualification.mentor_percent,
            extra_bonus=qualification.extra_bonus,
            personal_money=personal_money,
            group_money=group_money,
            leader_money=leader_money,
            side_vol_money=side_vol_money,
            total_money=total_money,
            veron=veron_money,
            total_income=float(total_money),
            branches_info=branches_info,
        )

        return response, breakdown

    def format_breakdown_report(self, breakdown: IncomeBreakdown) -> str:
        """Форматирует детализированный отчет в текстовый вид"""
        report_lines = ["Личный:"]

        # Личные начисления
        for item in breakdown.personal_items:
            report_lines.append(
                f"{item.volume:.0f} × {item.percent * 100:.0f}% × {VERON_PRICE} = {item.money:,.0f}"
            )

        report_lines.append("\nКомандный:")

        # Групповые начисления
        for item in breakdown.group_items:
            report_lines.append(
                f"{item.description} = {item.volume:.0f} × {item.percent * 100:.0f}% × {VERON_PRICE} = {item.money:,.0f}"
            )

        # Лидерские начисления
        if breakdown.leader_items:
            report_lines.append("\nЛидерский:")
            for item in breakdown.leader_items:
                report_lines.append(
                    f"{item.description} = {item.volume:.0f} × {item.percent * 100:.0f}% × {VERON_PRICE} = {item.money:,.0f}"
                )

        report_lines.append(f"\nИТОГО: {breakdown.total_money:,.0f}")

        return "\n".join(report_lines)

    def _build_strong_chains(self, member: Member) -> dict[Member, list[Member]]:
        """
        Возвращает:
        {
            Hamkor: [Mentor],
            Mentor: [Menejer],
        }
        """
        chains: dict[Member, list[Member]] = {}

        def dfs(anchor: Member | None, m: Member):
            if anchor:
                chains.setdefault(anchor, []).append(m)

            for c in m.team:
                dfs(m, c)

        for child in member.team:
            dfs(None, child)

        return chains

    def _pure_go(self, member: Member, strong_children: list[Member]) -> float:
        pure_go = member.group_volume()

        for child in strong_children:
            pure_go -= child.group_volume()

        return max(pure_go, 0)

    #####################################################
    #####################################################
    #####################################################

    def _analyze_branches(
            self,
            member: Member,
            parent_qualification: Qualification,
            side_volume: float,
    ) -> tuple[float, List[BranchInfo], List[BreakdownItem]]:

        total_go_money = 0
        breakdown_items: list[BreakdownItem] = []

        # Для каждой ветки первого уровня
        strong_leafs_list = self.recursive_walk(member)

        if len(strong_leafs_list) == 0:
            gv = member.group_volume()
            branch_q = qualification_by_points(int(gv))
            total_go_money += gv * branch_q.team_percent * VERON_PRICE
        else:
            for chain in strong_leafs_list:
                for i, member in enumerate(chain):
                    gv = member.group_volume()
                    if i + 1 < len(chain):
                        gv -= chain[i + 1].group_volume()
                    branch_q = qualification_by_points(int(gv))
                    if parent_qualification.team_percent < branch_q.team_percent:
                        total_go_money += side_volume * parent_qualification.team_percent * VERON_PRICE
                    else:
                        percent_diff = parent_qualification.team_percent - branch_q.team_percent
                        total_go_money += gv * percent_diff * VERON_PRICE

        return total_go_money, [], breakdown_items

    def recursive_walk(self, member: Member) -> List[List[Member]]:
        return self.collect_strong_members(member)

    def _income_from_strong_sub_branches(
            self,
            branch: Member,
            parent_qualification: Qualification,
    ) -> tuple[float, list[BreakdownItem]]:

        deepest = self._find_strongest_sub_branches(branch)
        if not deepest:
            return 0, []

        total_money = 0
        items: list[BreakdownItem] = []

        groups: dict[str, list[tuple[Member, float, Qualification]]] = {}

        for b in deepest:
            side = self._branch_side(b)
            q = qualification_by_points(int(side))

            if q.min_points >= parent_qualification.min_points:
                continue

            groups.setdefault(q.name, []).append((b, side, q))

        for qual_name, data in groups.items():
            percent = parent_qualification.team_percent - data[0][2].team_percent
            if percent <= 0:
                continue

            volume = 0
            for member, side, q in data:
                is_closed = side >= SIDE_VOLUME_THRESHOLD and q.name != "Hamkor"
                volume += member.lo if is_closed else side

            if volume <= 0:
                continue

            money = volume * percent * VERON_PRICE
            total_money += money

            items.append(
                BreakdownItem(
                    description=f"С {qual_name} – {percent * 100:.0f}%",
                    volume=volume,
                    percent=percent,
                    money=money,
                )
            )

        return total_money, items

    def _income_from_plain_branch(
            self,
            branch: Member,
            branch_side: float,
            branch_q: Qualification,
            parent_qualification: Qualification,
    ) -> tuple[float, list[BreakdownItem]]:

        if branch_q.name == "Hamkor":
            return 0, []

        percent = parent_qualification.team_percent - branch_q.team_percent
        if percent <= 0:
            return 0, []

        is_closed = branch_side >= SIDE_VOLUME_THRESHOLD
        volume = branch.lo if is_closed else branch_side
        money = volume * percent * VERON_PRICE

        return money, [
            BreakdownItem(
                description=f"С {branch_q.name} (ID: {branch.user_id}) – {percent * 100:.0f}%",
                volume=volume,
                percent=percent,
                money=money,
            )
        ]

    ##################################################
    ##################################################
    ##################################################


if __name__ == "__main__":
    from tests.domain.factories import m

    memb = m(1213, lo=500, team=[
        m(1310, lo=500),
        m(1311, lo=500),
        m(1312, lo=500, team=[
            m(1410, lo=1500)  # допустим >= SIDE_VOLUME_THRESHOLD
        ]),
    ])

    calculator = IncomeCalculator()
    res = calculator.calculate(memb)
    print(res)
