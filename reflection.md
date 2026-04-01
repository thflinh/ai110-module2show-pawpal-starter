# PawPal+ Project Reflection

## 1. System Design

### Core user actions (three things a user should be able to do)

1. **Register pets and add care tasks** — Enter the owner’s name, add one or more pets, and attach tasks with a time, date, frequency (once, daily, weekly), and priority so the system has structured data to schedule against.

2. **See an organized daily schedule** — View tasks sorted by time (and date) so the owner can follow a clear plan for the day without manually ordering items.

3. **Complete tasks and handle repeats safely** — Mark tasks done; for recurring work, the system should create the next occurrence and warn when two tasks start at the same time so the owner can spot clashes.

---

**a. Initial design**

The initial UML-style design centers on four types:

- **`Task`** — Holds what to do (`description`), when (`time_str` as HH:MM, `task_date`), how often it repeats (`frequency`), completion state, and `priority`. It knows how to compare itself for sorting (`sort_key`) and can be marked complete.

- **`Pet`** — Represents an animal with a name, species, and a list of `Task` objects; `add_task` is the main mutation.

- **`Owner`** — Holds the human’s name and a list of `Pet`s; aggregates all `(Task, Pet)` pairs for scheduling via `all_tasks_with_pet()`.

- **`Scheduler`** — The service layer over an `Owner`: it **sorts** tasks by time, **filters** by completion or pet name, **detects time conflicts** (same date + same start time), and **marks tasks complete** while creating the next instance for daily/weekly recurrence.

Relationships: an `Owner` owns many `Pet`s; each `Pet` has many `Task`s; the `Scheduler` reads from the `Owner` but does not own pets itself.

---

**b. Design changes**

One change was to keep **conflict detection** in the `Scheduler` as a **warning list** (strings) rather than raising exceptions or blocking saves. That keeps the UI and CLI demo resilient while still surfacing problems. Another change was representing time as **`time_str` plus `task_date`** instead of a single datetime everywhere, which simplified sorting and tests but pushes parsing responsibility into a small helper (`_parse_hhmm`).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers **calendar date**, **clock time (HH:MM)**, **completion status**, and **pet identity** for filtering. **Priority** is stored on each task for future ordering or display; the current sort is primarily **time-based** (then date). The owner’s preferences are implicit in which tasks they add and which pet they attach them to.

**b. Tradeoffs**

**Tradeoff:** Conflict detection only checks **identical start times** on the same date—not overlapping intervals (e.g., a 30-minute walk starting at 08:00 vs. a 20-minute feed starting at 08:15). That keeps the implementation small and deterministic for a class project, but a real app would model **duration** and **overlaps**. This tradeoff is reasonable for a first version focused on “double-booked slot” awareness without a full interval tree or calendar engine.

---

## 3. AI Collaboration

**a. How you used AI**

AI was useful for turning the assignment’s phases into a **concrete module layout** (`pawpal_system.py`, `main.py`, tests, and Streamlit wiring), for choosing **dataclasses** and a **Scheduler** service object, and for drafting **pytest** cases for sorting, recurrence, and conflicts. Short, file-scoped questions work well (“implement `sort_by_time` using `sorted` and a key lambda”) compared to vague prompts.

**b. Judgment and verification**

One suggestion to merge `Owner` and `Scheduler` into one class was **rejected** to keep **domain data** (owner/pets) separate from **algorithms** (sort/filter/conflicts), which makes testing and reuse easier. Verification was done by running **`python main.py`** for integration output and **`python -m pytest`** for regressions.

---

## 4. Testing and Verification

**a. What you tested**

Behaviors tested include: **`mark_complete`** toggles completion; **adding tasks** increases a pet’s task count; **sort order** matches chronological order; **daily recurrence** adds a new task on the next day after complete; **conflicts** are reported when two tasks share date and time; **invalid mark_complete** raises when the task is not on that pet.

**b. Confidence**

Confidence is **high for the covered behaviors** (roughly **4/5**), because the tests match the implemented rules. If there were more time, I would add tests for **weekly** recurrence, **invalid time strings**, and a small **Streamlit/session_state** integration test or manual checklist.

---

## 5. Reflection

**a. What went well**

The split between **`pawpal_system.py`** (logic) and **`app.py`** (UI) made it easy to validate behavior in the terminal first, then wire the same objects into Streamlit.

**b. What you would improve**

A next iteration would add **task duration**, **overlap-based conflicts**, and richer **priority** rules (e.g., sort by priority when times tie).

**c. Key takeaway**

Acting as the **lead architect** means **owning requirements and tradeoffs** while using AI for speed: AI drafts and refactors, but **you** decide boundaries (classes vs. god-object), **you** choose what to test, and **you** run the code to confirm it matches reality.

---

## AI strategy (VS Code Copilot–style workflow)

- **Most effective features:** Scoped prompts tied to a file (e.g., “fill in `Scheduler.detect_conflicts`”), generating **tests** from behavior descriptions, and **small refactors** (docstrings, rename) without touching architecture.
- **Example of a rejected or modified suggestion:** A flatter design with fewer classes was adjusted to keep **Owner / Pet / Task / Scheduler** separation for clarity and testability.
- **Separate chat sessions:** Using different sessions (or topics) for **design**, **algorithms**, and **tests** reduces context noise and stops earlier ideas from overwriting later decisions.
- **Lead architect role:** You set **invariants** (what “conflict” means, how recurrence works); AI accelerates coding inside those lines.
