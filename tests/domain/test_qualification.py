from domain.value_objects.qualifications import qualification_by_points


def test_hamkor():
    q = qualification_by_points(0)
    assert q.name == "Hamkor"


def test_mentor_threshold():
    q = qualification_by_points(500)
    assert q.name == "Mentor"


def test_director():
    q = qualification_by_points(4000)
    assert q.name == "Direktor"


def test_highest_qualification():
    q = qualification_by_points(120_000)
    assert q.name == "Olmos"
