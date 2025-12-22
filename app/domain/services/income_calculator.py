from typing import List
from domain.models.member import SIDE_VOLUME_THRESHOLD, Member
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
    ) -> tuple[float, List[BranchInfo]]:
        """
        Анализирует все ветки и собирает информацию о них.
        Возвращает (total_go_money, branches_info)
        """
        total_go_money = 0
        branches_info = []

        # Собственный side_volume родителя
        own_side_volume = member.lo

        # Сначала считаем деньги за собственный side_volume родителя
        # (это часть side_volume, которая не принадлежит веткам)
        own_side_money = own_side_volume * parent_qualification.team_percent * VERON_PRICE
        total_go_money += own_side_money

        # Добавляем информацию о "собственном side" родителя
        own_branch_info = BranchInfo(
            branch_id=0,  # 0 означает "собственный side родителя"
            branch_qualification_by_gv=parent_qualification.name,
            branch_qualification_by_side=parent_qualification.name,
            lo=member.lo,
            gv=own_side_volume,
            side_volume=own_side_volume,
            is_closed=False,
            is_stronger_than_parent=False,
            parent_earn_percent=parent_qualification.team_percent,
            parent_earn_money=own_side_money,
        )
        branches_info.append(own_branch_info)

        # Теперь анализируем все ветки
        for branch in member.team:
            # Базовые данные ветки
            branch_id = branch.user_id
            branch_lo = branch.lo
            branch_gv = branch.group_volume()
            branch_side = self._branch_side(branch)

            # Квалификации
            branch_side_q = qualification_by_points(int(branch_side))
            branch_gv_q = qualification_by_points(int(branch_gv))

            # Флаги
            is_closed = (branch_side >= SIDE_VOLUME_THRESHOLD and branch_side_q.name != "Hamkor")
            is_stronger_than_parent = branch_side_q.min_points >= parent_qualification.min_points

            # Инициализируем переменные для расчета
            parent_earn_percent = 0.0
            parent_earn_money = 0.0

            # Логика расчета денег родителя с этой ветки
            if not is_closed and not is_stronger_than_parent:
                # Для расчета используем квалификацию по side volume ветки
                branch_q = branch_side_q

                # Расчет процента, который получает родитель с этой ветки
                parent_percent = parent_qualification.team_percent
                branch_percent = branch_q.team_percent

                # Разница процентов (родитель получает эту разницу)
                parent_earn_percent = parent_percent - branch_percent

                # Процент не может быть отрицательным
                if parent_earn_percent > 0:
                    # Базовый объем для расчета - side volume ветки
                    base_volume = branch_side

                    # Расчет денег с этой ветки
                    parent_earn_money = base_volume * parent_earn_percent * VERON_PRICE
                    total_go_money += parent_earn_money

            # Собираем информацию о ветке
            branch_info = BranchInfo(
                branch_id=branch_id,
                branch_qualification_by_gv=branch_gv_q.name,
                branch_qualification_by_side=branch_side_q.name,
                lo=branch_lo,
                gv=branch_gv,
                side_volume=branch_side,
                is_closed=is_closed,
                is_stronger_than_parent=is_stronger_than_parent,
                parent_earn_percent=parent_earn_percent,
                parent_earn_money=parent_earn_money,
            )

            branches_info.append(branch_info)

        return total_go_money, branches_info

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
    ) -> tuple[dict, List[BranchInfo]]:
        """Рассчитывает все денежные компоненты и собирает информацию о ветках"""
        lo = member.lo

        # Личный объем
        lo_money = lo * qualification.personal_percent * VERON_PRICE

        # Групповой объем и информация о ветках
        go_money, branches_info = self._analyze_branches(
            member=member,
            parent_qualification=qualification,
            parent_side_volume=side_volume,
        )

        # Деньги за лидерство
        leader_money = self._calculate_leader_money(member, qualification)

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

        return money_data, branches_info

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

    def calculate(self, member: Member) -> IncomeResponse:
        # Базовые объемы
        group_volume = member.group_volume()
        base_qualification = qualification_by_points(int(group_volume))

        # Side volume
        side_volume = self.calculate_side_volume(member, base_qualification)

        # Финальная квалификация
        qualification, points = self._determine_qualification(
            member, group_volume, side_volume
        )

        # Деньги и информация о ветках
        money, branches_info = self._calculate_money(
            member, qualification, side_volume
        )

        # Округляем денежные значения до целых
        personal_money = int(round(money["lo"]))
        group_money = int(round(money["go"]))
        leader_money = int(round(money["leader_money"]))
        total_money = int(round(money["total"]))
        veron_money = int(round(money["veron"]))

        return IncomeResponse(
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