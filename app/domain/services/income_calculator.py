from domain.models.member import SIDE_VOLUME_THRESHOLD, Member
from domain.value_objects.qualification import Qualification
from domain.value_objects.qualifications import qualification_by_points
from web.scheme.schemas import IncomeResponse

VERON_PRICE = 7000


class IncomeCalculator:

    def _strong_branches_go(self, member: Member, qualification: Qualification) -> float:
        strong_go = 0

        for branch in member.team:
            branch_go = branch.group_volume()
            branch_q = qualification_by_points(int(branch_go))

            if branch_q.min_points >= qualification.min_points:
                strong_go += branch_go

        return strong_go

    def _leader_volume(self, member: Member, qualification: Qualification) -> float:
        go = member.group_volume()
        strong_go = self._strong_branches_go(member, qualification)

        leader_volume = go - strong_go
        return max(leader_volume, 0)

    def _strongest_branch(self, member: Member) -> Member | None:
        if not member.team:
            return None

        return max(
            member.team,
            key=lambda b: qualification_by_points(int(b.group_volume())).min_points
        )

    def _raw_side_volume(self, branch: Member) -> float:
        side = branch.lo
        for child in branch.team:
            side += self._raw_side_volume(child)
        return side


    def _branch_side_contribution(
            self,
            branch: Member,
            parent_qualification: Qualification,
    ) -> float:
        branch_side = self._branch_side(branch)
        branch_side_q = qualification_by_points(int(branch_side))

        # 1️⃣ Ветка закрыта по side volume
        if branch_side >= SIDE_VOLUME_THRESHOLD and branch_side_q.name != "Hamkor":
            return 0

        # 2️⃣ Ветка сильнее или равна родителю
        if branch_side_q.min_points >= parent_qualification.min_points:
            return 0  # ← даем 0, а не branch.lo!

        # 3️⃣ Обычная ветка
        return branch_side

    def calculate_side_volume(self, member: Member, qualification: Qualification) -> float:
        side = member.lo
        print(f"Начальный side: {side}, квалификация родителя: {qualification.name}")

        for i, branch in enumerate(member.team, 1):
            contribution = self._branch_side_contribution(branch, qualification)
            print(f"Ветка {i}: contribution={contribution}, branch.lo={branch.lo}, branch.gv={branch.group_volume()}")
            side += contribution

        print(f"Итоговый side: {side}")
        return side

    def _is_branch_closed(self, branch: Member) -> bool:
        branch_gv = branch.group_volume()
        branch_qualification = qualification_by_points(int(branch_gv))

        return (
                branch_gv >= SIDE_VOLUME_THRESHOLD
                and branch_qualification.name != "Hamkor"
        )

    def _branch_side(self, branch: Member) -> float:
        side = branch.lo

        for child in branch.team:
            child_side = self._branch_side(child)
            child_q = qualification_by_points(int(child_side))

            # Если child закрыл квалификацию — не учитываем
            if child_side >= SIDE_VOLUME_THRESHOLD and child_q.name != "Hamkor":
                continue

            side += child_side

        return side

    def _calculate_money(
            self,
            member: Member,
            qualification: Qualification,
            side_volume: float,
    ) -> dict:
        lo = member.lo
        go = member.group_volume()

        lo_money = lo * qualification.personal_percent * VERON_PRICE

        # Находим самую сильную ветку (по квалификации, а не по объему)
        strongest_branch = None
        strongest_branch_q = None

        for branch in member.team:
            branch_gv = branch.group_volume()
            branch_q = qualification_by_points(int(branch_gv))

            if strongest_branch_q is None or branch_q.min_points > strongest_branch_q.min_points:
                strongest_branch = branch
                strongest_branch_q = branch_q

        # Определяем процент для расчета ГО
        if strongest_branch_q is None:
            # Нет веток - считаем обычным способом
            go_percent = qualification.team_percent
            go_money = side_volume * go_percent * VERON_PRICE
        elif strongest_branch_q.min_points > qualification.min_points:
            # Ветка сильнее родителя - родитель получает ГО как обычно
            go_percent = qualification.team_percent
            go_money = side_volume * go_percent * VERON_PRICE
        elif strongest_branch_q.min_points == qualification.min_points:
            # Такая же квалификация - родитель ничего не получает за ГО
            go_percent = 0
            go_money = 0
        else:
            # Ветка слабее родителя
            # Проверяем, закрыл ли ребенок квалификацию (и не является ли Hamkor)
            branch_side = self._branch_side(strongest_branch)
            branch_side_q = qualification_by_points(int(branch_side))

            if branch_side >= SIDE_VOLUME_THRESHOLD and branch_side_q.name != "Hamkor":
                # Ребенок закрыл квалификацию - вычитаем его процент
                go_percent = qualification.team_percent - strongest_branch_q.team_percent
            else:
                # Ребенок не закрыл квалификацию - родитель получает полный процент
                go_percent = qualification.team_percent

            go_money = go * go_percent * VERON_PRICE  # Важно: умножаем на ГО родителя, а не на side_volume!

        strong_go = self._strong_branches_go(member, qualification)
        leader_money = strong_go * qualification.mentor_percent * VERON_PRICE

        return {
            "lo": lo_money,
            "go": go_money,
            "leader_money": leader_money,
            "total": lo_money + go_money + leader_money,
        }

    def calculate(self, member: Member):
        group_volume = member.group_volume()
        base_qualification = qualification_by_points(int(group_volume))
        side_volume = self.calculate_side_volume(member, base_qualification)

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
            points = int(group_volume)
        else:
            # Либо side < 500, либо есть сильные ветки → берем side volume
            points = int(side_volume)

        qualification = qualification_by_points(int(points))

        money = self._calculate_money(
            member,
            qualification,
            side_volume=side_volume,
        )

        return IncomeResponse(
            user_id=member.user_id,
            qualification=qualification.name,
            lo=member.lo,
            go=group_volume,
            points=points,
            personal_bonus=qualification.personal_percent,
            structure_bonus=qualification.team_percent,
            mentor_bonus=qualification.mentor_percent,
            side_volume=side_volume,
            extra_bonus=qualification.extra_bonus,
            personal_money=money["lo"],
            group_money=money["go"],
            leader_money=money["leader_money"],
            total_money=money["total"],
            veron=money["lo"] + money["go"],
            total_income=money["total"],
        )
