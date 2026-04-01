"""Tests for PawPal+ scheduling logic."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status() -> None:
    t = Task("Walk", "09:00", frequency="once")
    assert not t.completed
    t.mark_complete()
    assert t.completed


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "10:00"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Feed", "18:00"))
    assert len(pet.tasks) == 2


def test_sort_by_time_chronological() -> None:
    today = date(2026, 4, 1)
    owner = Owner(name="A")
    p = Pet(name="P")
    owner.add_pet(p)
    p.add_task(Task("Late", "14:00", task_date=today))
    p.add_task(Task("Early", "07:30", task_date=today))
    p.add_task(Task("Mid", "09:00", task_date=today))
    sched = Scheduler(owner)
    ordered = [t.description for t, _ in sched.sort_by_time()]
    assert ordered == ["Early", "Mid", "Late"]


def test_daily_recurrence_creates_next_day_task() -> None:
    today = date(2026, 4, 1)
    owner = Owner(name="O")
    pet = Pet(name="P")
    owner.add_pet(pet)
    daily = Task("Meds", "08:00", frequency="daily", task_date=today)
    pet.add_task(daily)
    sched = Scheduler(owner)
    new_task = sched.mark_task_complete(pet, daily)
    assert daily.completed
    assert new_task is not None
    assert new_task.task_date == today + timedelta(days=1)
    assert not new_task.completed
    assert new_task.frequency == "daily"


def test_conflict_detection_duplicate_times() -> None:
    today = date(2026, 4, 1)
    owner = Owner(name="O")
    a = Pet(name="A")
    b = Pet(name="B")
    owner.add_pet(a)
    owner.add_pet(b)
    a.add_task(Task("One", "10:00", task_date=today))
    b.add_task(Task("Two", "10:00", task_date=today))
    sched = Scheduler(owner)
    warnings = sched.detect_conflicts()
    assert len(warnings) == 1
    assert "10:00" in warnings[0]
    assert "One" in warnings[0] and "Two" in warnings[0]


def test_scheduler_mark_complete_unknown_task_raises() -> None:
    owner = Owner(name="O")
    pet = Pet(name="P")
    owner.add_pet(pet)
    orphan = Task("X", "12:00")
    sched = Scheduler(owner)
    with pytest.raises(ValueError):
        sched.mark_task_complete(pet, orphan)
