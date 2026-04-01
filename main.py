"""CLI demo for PawPal+ logic: owner, pets, tasks, and today's schedule."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def format_schedule(sched: Scheduler) -> str:
    lines = []
    for task, pet in sched.sort_by_time():
        status = "done" if task.completed else "pending"
        lines.append(
            f"  [{task.time_str}] {pet.name}: {task.description} "
            f"({task.frequency}, {status}) on {task.task_date}"
        )
    return "\n".join(lines) if lines else "  (no tasks)"


def main() -> None:
    today = date.today()
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Tasks in non-chronological order to exercise sorting
    mochi.add_task(
        Task("Evening walk", "19:00", frequency="once", task_date=today, priority="high")
    )
    mochi.add_task(
        Task("Morning walk", "08:30", frequency="daily", task_date=today, priority="high")
    )
    luna.add_task(
        Task("Feed breakfast", "07:00", frequency="daily", task_date=today, priority="medium")
    )
    # Intentional duplicate time for conflict demo
    luna.add_task(Task("Play session", "08:30", frequency="once", task_date=today))
    mochi.add_task(Task("Training", "08:30", frequency="once", task_date=today))

    sched = Scheduler(owner)

    print("=== Today's Schedule (sorted by time) ===")
    print(format_schedule(sched))

    print("\n=== Conflict warnings ===")
    for w in sched.detect_conflicts():
        print(f"  ! {w}")
    if not sched.detect_conflicts():
        print("  (none)")

    print("\n=== Filter: pending only ===")
    pending = sched.filter_by_completion(False)
    for task, pet in sched.sort_by_time(pending):
        print(f"  [{task.time_str}] {pet.name}: {task.description}")


if __name__ == "__main__":
    main()
