import streamlit as st
from datetime import date
from typing import cast

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner
sched = Scheduler(owner)

st.title("🐾 PawPal+")

st.markdown(
    """
Plan pet care tasks, see today's schedule sorted by time, and get warnings when two tasks start at the same moment.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** helps you track walks, feeding, meds, and more. Add pets and tasks below; the scheduler sorts by time and flags time conflicts.
"""
    )

st.divider()

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name, key="owner_name_input")

st.subheader("Add a pet")
col_p1, col_p2 = st.columns(2)
with col_p1:
    new_pet_name = st.text_input("Pet name", value="", key="new_pet_name")
with col_p2:
    new_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")

if st.button("Add pet"):
    if new_pet_name.strip():
        if owner.get_pet(new_pet_name.strip()) is None:
            owner.add_pet(Pet(name=new_pet_name.strip(), species=new_species))
            st.success(f"Added pet {new_pet_name.strip()}.")
        else:
            st.warning("A pet with that name already exists.")
    else:
        st.warning("Enter a pet name.")

if owner.pets:
    pet_names = [p.name for p in owner.pets]
    st.subheader("Add a task")
    task_pet = st.selectbox("Pet", pet_names, key="task_pet_select")
    t1, t2, t3 = st.columns(3)
    with t1:
        task_title = st.text_input("Task description", value="Morning walk", key="task_desc")
    with t2:
        task_time = st.text_input("Time (HH:MM)", value="08:00", key="task_time")
    with t3:
        freq = st.selectbox("Frequency", ["once", "daily", "weekly"], key="task_freq")
    p1, p2 = st.columns(2)
    with p1:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1, key="task_pri")
    with p2:
        task_day = st.date_input("Task date", value=date.today(), key="task_date")

    if st.button("Add task"):
        pet_obj = owner.get_pet(task_pet)
        if pet_obj:
            pet_obj.add_task(
                Task(
                    description=task_title,
                    time_str=task_time,
                    frequency=cast(Frequency, freq),
                    task_date=task_day,
                    priority=priority,
                )
            )
            st.success("Task added.")

    st.subheader("Mark task complete")
    all_pairs = sched.get_all_tasks()
    if all_pairs:
        labels = [
            f"{pet.name} — {task.description} @ {task.time_str} ({task.task_date})"
            for task, pet in sched.sort_by_time()
        ]
        choice = st.selectbox("Task", range(len(labels)), format_func=lambda i: labels[i])
        if st.button("Mark selected complete"):
            task, pet = sched.sort_by_time()[choice]
            sched.mark_task_complete(pet, task)
            st.success("Marked complete." + (" Next occurrence added for recurring task." if task.frequency != "once" else ""))
            st.rerun()
else:
    st.info("Add at least one pet to create tasks.")

st.divider()

st.subheader("Today's schedule")
show_completed = st.checkbox("Show completed tasks", value=True)
pairs = sched.get_all_tasks()
if not show_completed:
    pairs = sched.filter_by_completion(False, pairs)
sorted_pairs = sched.sort_by_time(pairs)

if sorted_pairs:
    rows = []
    for task, pet in sorted_pairs:
        rows.append(
            {
                "Time": task.time_str,
                "Date": str(task.task_date),
                "Pet": pet.name,
                "Task": task.description,
                "Frequency": task.frequency,
                "Priority": task.priority,
                "Status": "done" if task.completed else "pending",
            }
        )
    st.table(rows)
else:
    st.info("No tasks to show.")

conflicts = sched.detect_conflicts()
if conflicts:
    for c in conflicts:
        st.warning(c)
else:
    st.success("No time conflicts for identical start times.")

st.divider()
st.caption("Run `python main.py` for a terminal demo, or `python -m pytest` for tests.")
