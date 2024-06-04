import json
import os
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

# Constants
TASK_FILE = 'tasks.json'
CATEGORY_ORDER = [
    "Urgent & Important",
    "Not Urgent & Important",
    "Urgent & Not Important",
    "Not Urgent & Not Important",
    "Backlog",
    "Archived",
    "Deleted"
]

def load_tasks():
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as file:
            return json.load(file)
    return {category: [] for category in CATEGORY_ORDER}

def save_tasks(tasks):
    with open(TASK_FILE, 'w') as file:
        json.dump(tasks, file, indent=4)

def generate_task_id(tasks):
    task_ids = [int(task['id']) for category in tasks.values() for task in category]
    if task_ids:
        return f"{max(task_ids) + 1:02}"
    return "00"

def display_tasks(stdscr, tasks):
    stdscr.clear()
    row = 0
    for category in CATEGORY_ORDER:
        stdscr.addstr(row, 0, category, curses.A_BOLD | curses.A_UNDERLINE)
        row += 1
        for task in tasks[category]:
            stdscr.addstr(row, 2, f"{task['id']}: {task['description']}")
            row += 1
        row += 1
    stdscr.refresh()

def add_task(stdscr, tasks):
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter task description:")
    editwin = curses.newwin(1, 60, 1, 0)
    rectangle(stdscr, 0, 0, 2, 61)
    stdscr.refresh()
    box = Textbox(editwin)
    box.edit()
    description = box.gather().strip()

    stdscr.addstr(3, 0, "Select category:")
    for idx, category in enumerate(CATEGORY_ORDER):
        stdscr.addstr(4 + idx, 2, f"{idx + 1}. {category}")
    stdscr.refresh()
    
    while True:
        key = stdscr.getch()
        if 49 <= key <= 49 + len(CATEGORY_ORDER) - 1:  # ASCII for numbers 1 to len(CATEGORY_ORDER)
            selected_category = CATEGORY_ORDER[key - 49]
            break

    task_id = generate_task_id(tasks)
    tasks[selected_category].append({"id": task_id, "description": description})
    save_tasks(tasks)

def move_task(stdscr, tasks):
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter task ID to move:")
    editwin = curses.newwin(1, 60, 1, 0)
    rectangle(stdscr, 0, 0, 2, 61)
    stdscr.refresh()
    box = Textbox(editwin)
    box.edit()
    task_id = box.gather().strip()

    task_to_move = None
    original_category = None
    for category in CATEGORY_ORDER:
        for task in tasks[category]:
            if task['id'] == task_id:
                task_to_move = task
                original_category = category
                break
        if task_to_move:
            break

    if not task_to_move:
        stdscr.addstr(3, 0, "Task ID not found.")
        stdscr.getch()
        return

    stdscr.addstr(3, 0, "Select new category:")
    for idx, category in enumerate(CATEGORY_ORDER):
        stdscr.addstr(4 + idx, 2, f"{idx + 1}. {category}")
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if 49 <= key <= 49 + len(CATEGORY_ORDER) - 1:
            new_category = CATEGORY_ORDER[key - 49]
            break

    tasks[original_category].remove(task_to_move)
    tasks[new_category].append(task_to_move)
    save_tasks(tasks)

def main_menu(stdscr):
    tasks = load_tasks()
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Eisenhower Matrix Task Manager", curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addstr(1, 0, "1. View Tasks")
        stdscr.addstr(2, 0, "2. Add Task")
        stdscr.addstr(3, 0, "3. Move Task")
        stdscr.addstr(4, 0, "4. Exit")
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == ord('1'):
            display_tasks(stdscr, tasks)
            stdscr.getch()
        elif key == ord('2'):
            add_task(stdscr, tasks)
        elif key == ord('3'):
            move_task(stdscr, tasks)
        elif key == ord('4'):
            break

def main():
    wrapper(main_menu)

if __name__ == "__main__":
    main()
