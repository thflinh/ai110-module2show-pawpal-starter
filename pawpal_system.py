"""PawPal+ logic layer: owners, pets, tasks, and scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Literal, Optional, Tuple

Frequency = Literal["once", "daily", "weekly"]


def _parse_hhmm(s: str) -> Tuple[int, int]:
    parts = s.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Time must be HH:MM, got {s!r}")
    h, m = int(parts[0]), int(parts[1])
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Invalid time: {s!r}")
    return h, m


@dataclass
class Task:
    """A single care activity with time, frequency, and completion state."""

    description: str
    time_str: str
    frequency: Frequency = "once"
    completed: bool = False
    task_date: date = field(default_factory=date.today)
    priority: str = "medium"

    def sort_key(self) -> Tuple[date, int, int]:
        """Sort key: date then clock time (HH:MM)."""
        h, m = _parse_hhmm(self.time_str)
        return (self.task_date, h, m)

    def mark_complete(self) -> None:
        self.completed = True


@dataclass
class Pet:
    """A pet with a list of care tasks."""

    name: str
    species: str = "dog"
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)


@dataclass
class Owner:
    """An owner who manages multiple pets."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        for p in self.pets:
            if p.name == name:
                return p
        return None

    def all_tasks_with_pet(self) -> List[Tuple[Task, Pet]]:
        out: List[Tuple[Task, Pet]] = []
        for pet in self.pets:
            for t in pet.tasks:
                out.append((t, pet))
        return out


class Scheduler:
    """Retrieves, sorts, filters tasks and detects scheduling conflicts."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def get_all_tasks(self) -> List[Tuple[Task, Pet]]:
        return self.owner.all_tasks_with_pet()

    def sort_by_time(self, pairs: Optional[List[Tuple[Task, Pet]]] = None) -> List[Tuple[Task, Pet]]:
        """Return tasks sorted by date then time (HH:MM)."""
        items = pairs if pairs is not None else self.get_all_tasks()
        return sorted(items, key=lambda tp: tp[0].sort_key())

    def filter_by_completion(self, completed: bool, pairs: Optional[List[Tuple[Task, Pet]]] = None) -> List[Tuple[Task, Pet]]:
        items = pairs if pairs is not None else self.get_all_tasks()
        return [(t, p) for t, p in items if t.completed == completed]

    def filter_by_pet_name(self, pet_name: str, pairs: Optional[List[Tuple[Task, Pet]]] = None) -> List[Tuple[Task, Pet]]:
        items = pairs if pairs is not None else self.get_all_tasks()
        return [(t, p) for t, p in items if p.name == pet_name]

    def detect_conflicts(self, pairs: Optional[List[Tuple[Task, Pet]]] = None) -> List[str]:
        """
        Warn if two or more tasks share the same date and time (exact match).
        Does not model overlapping durations—only identical start times.
        """
        items = pairs if pairs is not None else self.get_all_tasks()
        buckets: dict[Tuple[date, str], List[str]] = {}
        for task, pet in items:
            key = (task.task_date, task.time_str)
            buckets.setdefault(key, []).append(f"{pet.name}: {task.description}")

        warnings: List[str] = []
        for (d, tm), labels in buckets.items():
            if len(labels) > 1:
                warnings.append(
                    f"Conflict on {d} at {tm}: " + "; ".join(sorted(labels))
                )
        return warnings

    def mark_task_complete(self, pet: Pet, task: Task) -> Optional[Task]:
        """
        Mark a task complete. For daily/weekly recurrence, append the next occurrence.
        """
        if task not in pet.tasks:
            raise ValueError("Task does not belong to this pet.")

        task.mark_complete()
        if task.frequency == "once":
            return None

        next_date = task.task_date
        if task.frequency == "daily":
            next_date = task.task_date + timedelta(days=1)
        elif task.frequency == "weekly":
            next_date = task.task_date + timedelta(weeks=1)
        else:
            return None

        new_task = Task(
            description=task.description,
            time_str=task.time_str,
            frequency=task.frequency,
            completed=False,
            task_date=next_date,
            priority=task.priority,
        )
        pet.add_task(new_task)
        return new_task
