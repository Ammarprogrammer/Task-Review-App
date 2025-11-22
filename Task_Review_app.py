# task_app.py
import json
import random
import sys
from datetime import date



class Task:
    def __init__(self, task_name: str, assigned_duration: float,
                 actual_duration: float = None, date_str: str = None, completion_percent: float = None):
        self.task_name = task_name
        self.assigned_duration = float(assigned_duration)
        self.actual_duration = float(actual_duration) if actual_duration is not None else None
        self.date = date_str or date.today().isoformat()
        self.completion_percent = completion_percent

    def update_actual(self, actual_duration: float):
        self.actual_duration = float(actual_duration)
        self.completion_percent = self.calculate_progress()

    def calculate_progress(self):
        if self.actual_duration is None or self.assigned_duration == 0:
            return None
        percent = (self.actual_duration / self.assigned_duration) * 100
        return round(percent, 2)

    def to_dict(self):
        return {
            "task_name": self.task_name,
            "assigned_duration": self.assigned_duration,
            "actual_duration": self.actual_duration,
            "date": self.date,
            "completion_percent": self.completion_percent
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            task_name=d["task_name"],
            assigned_duration=d["assigned_duration"],
            actual_duration=d.get("actual_duration"),
            date_str=d.get("date"),
            completion_percent=d.get("completion_percent")
        )


class User:
    def __init__(self, user_id: str, name: str, password: str):
        self.user_id = str(user_id)
        self.name = name
        self.password = password
        self.tasks = []  # list of Task objects

    def add_task(self, task_name: str, assigned_duration: float):
        t = Task(task_name=task_name, assigned_duration=assigned_duration)
        self.tasks.append(t)

    def update_task(self, task_name: str, actual_duration: float):
        for task in self.tasks:
            if task.task_name == task_name:
                task.update_actual(actual_duration)
                return True
        return False

    def view_tasks(self):
        return [t.to_dict() for t in self.tasks]

    def to_dict(self):
        return {
            "name": self.name,
            "password": self.password,
            "tasks": [t.to_dict() for t in self.tasks]
        }

    @classmethod
    def from_dict(cls, user_id: str, d):
        u = cls(user_id=user_id, name=d["name"], password=d["password"])
        tasks = d.get("tasks", [])
        for td in tasks:
            u.tasks.append(Task.from_dict(td))
        return u


class TaskManager:
    DATA_FILE = "python/Task_data.json"

    def __init__(self):
        self.users = {}  # key: user_id (str), value: User object
        self.current_user = None
        self.load_data()

    # ---------- Persistence ----------
    def save_data(self):
        serial = {}
        for uid, user in self.users.items():
            serial[uid] = user.to_dict()
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(serial, f, indent=2)
        # no print here; called by menus

    def load_data(self):
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for uid, ud in raw.items():
                self.users[uid] = User.from_dict(uid, ud)
        except FileNotFoundError:
            # create empty file
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)
        except json.JSONDecodeError:
            print("Warning: Data file corrupted. Starting with empty data.")
            self.users = {}

    # ---------- Account management ----------
    def generate_unique_user_id(self):
        while True:
            uid = str(random.randint(10000, 99999))
            if uid not in self.users:
                return uid

    def create_account(self):
        name = input("Enter your name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return

        while True:
            pwd = input("Enter an 8-character alphanumeric password: ")
            if len(pwd) == 8 and pwd.isalnum():
                pwd_confirm = input("Confirm password: ")
                if pwd == pwd_confirm:
                    break
                else:
                    print("Passwords do not match. Try again.")
            else:
                print("Password must be exactly 8 alphanumeric characters.")

        uid = self.generate_unique_user_id()
        self.users[uid] = User(uid, name, pwd)
        self.save_data()
        print(f"✅ Account created! Your user ID is: {uid}")

    def login(self):
        uid = input("Enter your user ID: ").strip()
        if uid not in self.users:
            print("❌ Account not found.")
            return
        pwd = input("Enter your password: ")
        user = self.users[uid]
        if user.password != pwd:
            print("❌ Incorrect password.")
            return
        print(f"✅ Welcome, {user.name}!")
        self.current_user = user
        self.user_menu()

    def delete_account(self):
        if not self.current_user:
            print("❌ No user logged in.")
            return
        confirm = input(f"Are you sure you want to delete account {self.current_user.user_id}? (Y/N): ").strip().upper()
        if confirm != "Y":
            print("Cancelled.")
            return
        pwd = input("Enter your password to confirm deletion: ")
        if pwd != self.current_user.password:
            print("❌ Incorrect password. Account not deleted.")
            return
        del self.users[self.current_user.user_id]
        self.current_user = None
        self.save_data()
        print("✅ Account deleted successfully.")

    # ---------- Task operations ----------
    def add_task_for_current_user(self):
        if not self.current_user:
            print("❌ Please login first.")
            return
        name = input("Task name: ").strip()
        if not name:
            print("Task name cannot be empty.")
            return
        try:
            assigned = float(input("Assigned duration (hours, e.g. 2.5): ").strip())
            if assigned <= 0:
                print("Assigned duration must be positive.")
                return
        except ValueError:
            print("Invalid number.")
            return
        self.current_user.add_task(name, assigned)
        self.save_data()
        print(f"📝 Task '{name}' added for {self.current_user.name} on {date.today().isoformat()}")

    def update_task_for_current_user(self):
        if not self.current_user:
            print("❌ Please login first.")
            return
        tname = input("Enter exact task name to update: ").strip()
        try:
            actual = float(input("Actual duration (hours): ").strip())
            if actual < 0:
                print("Actual duration cannot be negative.")
                return
        except ValueError:
            print("Invalid number.")
            return
        ok = self.current_user.update_task(tname, actual)
        if ok:
            self.save_data()
            print(f"✅ Task '{tname}' updated.")
        else:
            print("❌ Task not found.")

    def view_tasks_for_current_user(self):
        if not self.current_user:
            print("❌ Please login first.")
            return
        tasks = self.current_user.view_tasks()
        if not tasks:
            print("No tasks yet.")
            return
        for i, t in enumerate(tasks, start=1):
            print(f"\n[{i}] {t['task_name']}")
            print(f"    Date: {t['date']}")
            print(f"    Assigned: {t['assigned_duration']} hrs")
            print(f"    Actual: {t['actual_duration']}")
            print(f"    Completion%: {t['completion_percent']}")

    # ---------- Menus ----------
    def user_menu(self):
        while True:
            print("\n--- USER MENU ---")
            print("1. Add Task")
            print("2. Update Task (enter actual duration)")
            print("3. View Tasks")
            print("4. Delete Account")
            print("5. Logout")
            choice = input("Choose (1-5): ").strip()
            if choice == "1":
                self.add_task_for_current_user()
            elif choice == "2":
                self.update_task_for_current_user()
            elif choice == "3":
                self.view_tasks_for_current_user()
            elif choice == "4":
                self.delete_account()
                return
            elif choice == "5":
                self.current_user = None
                print("Logged out.")
                return
            else:
                print("Invalid option.")

    def main_menu(self):
        while True:
            print("\n=== TASK MANAGER ===")
            print("1. Create account")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose (1-3): ").strip()
            if choice == "1":
                self.create_account()
            elif choice == "2":
                self.login()
            elif choice == "3":
                self.save_data()
                print("Goodbye.")
                sys.exit(0)
            else:
                print("Invalid option.")


def main():
    tm = TaskManager()
    tm.main_menu()


if __name__ == "__main__":
    main()
