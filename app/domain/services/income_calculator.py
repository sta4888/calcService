from typing import List, Optional, Set
from domain.models.member import SIDE_VOLUME_THRESHOLD, Member
from domain.value_objects.BreakdownItem import BreakdownItem, IncomeBreakdown
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import qualification_by_points
from web.scheme.schemas import IncomeResponse, BranchInfo

VERON_PRICE = 7000


class IncomeCalculator:
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

    def _analyze_branches(
            self,
            member: Member,
            parent_qualification: Qualification,
            parent_side_volume: float,
    ) -> tuple[float, List[BranchInfo], List[BreakdownItem]]:
        """
        Анализирует все ветки и собирает информацию о них.
        Возвращает (total_go_money, branches_info, breakdown_items)
        """
        total_go_money = 0
        all_branches_info = []
        breakdown_items = []

        # 1️⃣ С бокового балла (parent_side_volume)
        if parent_side_volume > 0:
            side_money = parent_side_volume * parent_qualification.team_percent * VERON_PRICE
            total_go_money += side_money

            breakdown_items.append(
                BreakdownItem(
                    description=f"С бокового балла – {parent_qualification.team_percent * 100:.0f}%",
                    volume=parent_side_volume,
                    percent=parent_qualification.team_percent,
                    money=side_money
                )
            )

        # 2️⃣ Анализируем все непосредственные ветки
        for branch in member.team:
            # Собираем информацию о всей ветке
            branch_side = self._branch_side(branch)
            branch_side_q = qualification_by_points(int(branch_side))
            is_branch_stronger = branch_side_q.min_points >= parent_qualification.min_points

            # Если вся ветка сильнее родителя - пропускаем
            if is_branch_stronger:
                continue

            # Находим самые глубокие сильные ветки
            deepest_strong_branches = self._find_strongest_sub_branches(branch)

            if deepest_strong_branches:
                # Группируем по квалификациям
                qual_groups = {}
                for strong_branch in deepest_strong_branches:
                    strong_branch_side = self._branch_side(strong_branch)
                    strong_branch_q = qualification_by_points(int(strong_branch_side))

                    # Проверяем, что ветка слабее родителя
                    if strong_branch_q.min_points >= parent_qualification.min_points:
                        continue

                    qual_name = strong_branch_q.name
                    if qual_name not in qual_groups:
                        qual_groups[qual_name] = []
                    qual_groups[qual_name].append((strong_branch, strong_branch_side, strong_branch_q))

                # Для каждой квалификации считаем сумму
                for qual_name, branches_data in qual_groups.items():
                    total_volume = 0
                    percent = parent_qualification.team_percent - branches_data[0][2].team_percent

                    if percent <= 0:
                        continue

                    for strong_branch, branch_side, branch_q in branches_data:
                        is_closed = (branch_side >= SIDE_VOLUME_THRESHOLD and branch_q.name != "Hamkor")
                        base_volume = strong_branch.lo if is_closed else branch_side
                        total_volume += base_volume

                    if total_volume > 0:
                        money = total_volume * percent * VERON_PRICE
                        total_go_money += money

                        branch_count = len(branches_data)
                        if branch_count == 1:
                            strong_branch = branches_data[0][0]
                            description = f"С {qual_name} (ID: {strong_branch.user_id}) – {percent * 100:.0f}%"
                        else:
                            description = f"С {branch_count} {qual_name} – {percent * 100:.0f}%"

                        breakdown_items.append(
                            BreakdownItem(
                                description=description,
                                volume=total_volume,
                                percent=percent,
                                money=money
                            )
                        )

            # 3️⃣ Если нет сильных подветок, но сама ветка не Hamkor
            elif branch_side_q.name != "Hamkor":
                percent = parent_qualification.team_percent - branch_side_q.team_percent

                if percent > 0:
                    is_closed = (branch_side >= SIDE_VOLUME_THRESHOLD
                                 and branch_side_q.name != "Hamkor")
                    base_volume = branch.lo if is_closed else branch_side
                    money = base_volume * percent * VERON_PRICE
                    total_go_money += money

                    breakdown_items.append(
                        BreakdownItem(
                            description=f"С {branch_side_q.name} (ID: {branch.user_id}) – {percent * 100:.0f}%",
                            volume=base_volume,
                            percent=percent,
                            money=money
                        )
                    )

        return total_go_money, all_branches_info, breakdown_items

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
            parent_side_volume=side_volume,
        )

        # Деньги за лидерство
        leader_money, leader_items = self._calculate_leader_money_with_breakdown(member, qualification)

        # Итоговые суммы
        total_money = lo_money + go_money + leader_money
        veron_money = lo_money + go_money

        money_data = {
            "lo": lo_money,
            "go": go_money,
            "leader_money": leader_money,
            "total": total_money,
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