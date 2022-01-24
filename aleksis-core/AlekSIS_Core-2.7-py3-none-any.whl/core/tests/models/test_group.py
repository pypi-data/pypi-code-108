import pytest

from aleksis.core.models import Group, Person

pytestmark = pytest.mark.django_db


def test_child_groups_recursive():
    g_1st_grade = Group.objects.create(name="1st grade")
    g_1a = Group.objects.create(name="1a")
    g_1b = Group.objects.create(name="1b")
    g_2nd_grade = Group.objects.create(name="2nd grade")
    g_2a = Group.objects.create(name="2a")
    g_2b = Group.objects.create(name="2b")
    g_2c = Group.objects.create(name="2c")
    g_2nd_grade_french = Group.objects.create(name="2nd grade French")

    g_1a.parent_groups.set([g_1st_grade])
    g_1b.parent_groups.set([g_1st_grade])
    g_2a.parent_groups.set([g_2nd_grade])
    g_2b.parent_groups.set([g_2nd_grade])
    g_2c.parent_groups.set([g_2nd_grade])
    g_2nd_grade_french.parent_groups.set([g_2b, g_2c])

    assert g_2nd_grade_french in g_2nd_grade.child_groups_recursive
    assert g_2nd_grade_french in g_2b.child_groups_recursive
    assert g_2nd_grade_french in g_2c.child_groups_recursive
    assert g_2nd_grade_french not in g_2a.child_groups_recursive
    assert g_2nd_grade_french not in g_1st_grade.child_groups_recursive


def test_parent_groups_recursive():
    g_1st_grade = Group.objects.create(name="1st grade")
    g_1a = Group.objects.create(name="1a")
    g_1b = Group.objects.create(name="1b")
    g_2nd_grade = Group.objects.create(name="2nd grade")
    g_2a = Group.objects.create(name="2a")
    g_2b = Group.objects.create(name="2b")
    g_2c = Group.objects.create(name="2c")
    g_2nd_grade_french = Group.objects.create(name="2nd grade French")

    g_1a.parent_groups.set([g_1st_grade])
    g_1b.parent_groups.set([g_1st_grade])
    g_2a.parent_groups.set([g_2nd_grade])
    g_2b.parent_groups.set([g_2nd_grade])
    g_2c.parent_groups.set([g_2nd_grade])
    g_2nd_grade_french.parent_groups.set([g_2b, g_2c])

    assert g_1st_grade in g_1a.parent_groups_recursive
    assert g_2nd_grade in g_2a.parent_groups_recursive
    assert g_2nd_grade in g_2nd_grade_french.parent_groups_recursive
    assert g_1st_grade not in g_2nd_grade_french.parent_groups_recursive


def test_members_recursive():
    g_2nd_grade = Group.objects.create(name="2nd grade")
    g_2a = Group.objects.create(name="2a")
    g_2b = Group.objects.create(name="2b")
    g_2c = Group.objects.create(name="2c")
    g_2nd_grade_french = Group.objects.create(name="2nd grade French")

    g_2a.parent_groups.set([g_2nd_grade])
    g_2b.parent_groups.set([g_2nd_grade])
    g_2c.parent_groups.set([g_2nd_grade])
    g_2nd_grade_french.parent_groups.set([g_2b, g_2c])

    p_2a_1 = Person.objects.create(first_name="A", last_name="B")
    p_2a_2 = Person.objects.create(first_name="A", last_name="B")
    p_2b_1 = Person.objects.create(first_name="A", last_name="B")
    p_2b_2 = Person.objects.create(first_name="A", last_name="B")
    p_2c_1 = Person.objects.create(first_name="A", last_name="B")
    p_2c_2 = Person.objects.create(first_name="A", last_name="B")
    p_french_only = Person.objects.create(first_name="A", last_name="B")

    g_2a.members.set([p_2a_1, p_2a_2])
    g_2b.members.set([p_2b_1, p_2b_2])
    g_2c.members.set([p_2c_1, p_2c_2])
    g_2nd_grade_french.members.set([p_2b_1, p_2c_1, p_french_only])

    assert p_2a_1 in g_2nd_grade.members_recursive
    assert p_2a_2 in g_2nd_grade.members_recursive
    assert p_2b_1 in g_2nd_grade.members_recursive
    assert p_2b_2 in g_2nd_grade.members_recursive
    assert p_2c_1 in g_2nd_grade.members_recursive
    assert p_2c_2 in g_2nd_grade.members_recursive
    assert p_french_only in g_2nd_grade.members_recursive
    assert p_french_only in g_2b.members_recursive
    assert p_french_only in g_2c.members_recursive
    assert p_french_only not in g_2a.members_recursive


def test_member_of_recursive():
    g_2nd_grade = Group.objects.create(name="2nd grade")
    g_2a = Group.objects.create(name="2a")
    g_2b = Group.objects.create(name="2b")
    g_2c = Group.objects.create(name="2c")
    g_2nd_grade_french = Group.objects.create(name="2nd grade French")

    g_2a.parent_groups.set([g_2nd_grade])
    g_2b.parent_groups.set([g_2nd_grade])
    g_2c.parent_groups.set([g_2nd_grade])
    g_2nd_grade_french.parent_groups.set([g_2b, g_2c])

    p_2a_1 = Person.objects.create(first_name="A", last_name="B")
    p_2a_2 = Person.objects.create(first_name="A", last_name="B")
    p_2b_1 = Person.objects.create(first_name="A", last_name="B")
    p_2b_2 = Person.objects.create(first_name="A", last_name="B")
    p_2c_1 = Person.objects.create(first_name="A", last_name="B")
    p_2c_2 = Person.objects.create(first_name="A", last_name="B")
    p_french_only = Person.objects.create(first_name="A", last_name="B")

    g_2a.members.set([p_2a_1, p_2a_2])
    g_2b.members.set([p_2b_1, p_2b_2])
    g_2c.members.set([p_2c_1, p_2c_2])
    g_2nd_grade_french.members.set([p_2b_1, p_2c_1, p_french_only])

    assert g_2nd_grade in p_2a_1.member_of_recursive
    assert g_2nd_grade in p_2a_2.member_of_recursive
    assert g_2nd_grade in p_2b_1.member_of_recursive
    assert g_2nd_grade in p_2b_2.member_of_recursive
    assert g_2nd_grade in p_2c_1.member_of_recursive
    assert g_2nd_grade in p_2c_2.member_of_recursive
    assert g_2nd_grade in p_french_only.member_of_recursive
    assert g_2b in p_french_only.member_of_recursive
    assert g_2c in p_french_only.member_of_recursive


def test_owners_recursive():
    g_2nd_grade = Group.objects.create(name="2nd grade")
    g_2a = Group.objects.create(name="2a")
    g_2b = Group.objects.create(name="2b")

    g_2a.parent_groups.set([g_2nd_grade])
    g_2b.parent_groups.set([g_2nd_grade])

    p_1 = Person.objects.create(first_name="A", last_name="B")
    p_2 = Person.objects.create(first_name="A", last_name="B")

    g_2nd_grade.owners.set([p_1])

    assert p_1 in g_2a.owners_recursive
    assert p_1 in g_2b.owners_recursive
    assert p_2 not in g_2a.owners_recursive
    assert p_2 not in g_2b.owners_recursive


def test_owner_of_recursive():
    g_2nd_grade = Group.objects.create(name="2nd grade")
    g_2a = Group.objects.create(name="2a")
    g_2b = Group.objects.create(name="2b")

    g_2a.parent_groups.set([g_2nd_grade])
    g_2b.parent_groups.set([g_2nd_grade])

    p_1 = Person.objects.create(first_name="A", last_name="B")
    p_2 = Person.objects.create(first_name="A", last_name="B")

    g_2nd_grade.owners.set([p_1])

    assert g_2a in p_1.owner_of_recursive.all()
    assert g_2b in p_1.owner_of_recursive.all()
    assert g_2a not in p_2.owner_of_recursive.all()
    assert g_2b not in p_2.owner_of_recursive.all()
