# todo_cli.py
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class Task:
    def __init__(self, task_id: int, title: str, description: str = "", 
                 due_date: Optional[str] = None, priority: str = "medium", 
                 completed: bool = False):
        self.id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority  # low, medium, high
        self.completed = completed
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            due_date=data.get("due_date"),
            priority=data.get("priority", "medium"),
            completed=data.get("completed", False)
        )
    
    def __str__(self) -> str:
        status = "✓" if self.completed else "○"
        priority_symbols = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        priority_symbol = priority_symbols.get(self.priority, "🟡")
        due_info = f" | Due: {self.due_date}" if self.due_date else ""
        return f"{status} [{self.id}] {priority_symbol} {self.title}{due_info}"


class TodoList:
    def __init__(self, storage_file: str = "tasks.json"):
        self.storage_file = storage_file
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load_tasks()
    
    def add_task(self, title: str, description: str = "", 
                 due_date: Optional[str] = None, priority: str = "medium") -> Task:
        task = Task(self.next_id, title, description, due_date, priority)
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None,
                   due_date: Optional[str] = None,
                   priority: Optional[str] = None,
                   completed: Optional[bool] = None) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if priority is not None:
            task.priority = priority
        if completed is not None:
            task.completed = completed
        
        self.save_tasks()
        return True
    
    def delete_task(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        self.tasks.remove(task)
        self.save_tasks()
        return True
    
    def toggle_complete(self, task_id: int) -> bool:
        task = self.get_task(task_id)
        if not task:
            return False
        task.completed = not task.completed
        self.save_tasks()
        return True
    
    def get_all_tasks(self, show_completed: bool = True) -> List[Task]:
        if show_completed:
            return self.tasks
        return [t for t in self.tasks if not t.completed]
    
    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        return [t for t in self.tasks if t.priority == priority]
    
    def clear_completed(self) -> int:
        completed_tasks = [t for t in self.tasks if t.completed]
        for task in completed_tasks:
            self.tasks.remove(task)
        self.save_tasks()
        return len(completed_tasks)
    
    def save_tasks(self):
        data = {
            "next_id": self.next_id,
            "tasks": [task.to_dict() for task in self.tasks]
        }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_tasks(self):
        if not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                self.next_id = data.get("next_id", 1)
                self.tasks = [Task.from_dict(task_data) for task_data in data.get("tasks", [])]
        except (json.JSONDecodeError, FileNotFoundError):
            self.tasks = []
            self.next_id = 1


def display_tasks(tasks: List[Task], title: str = "Your Tasks"):
    if not tasks:
        print(f"\n📋 {title}: No tasks found.")
        return
    
    print(f"\n📋 {title}:")
    print("-" * 50)
    for task in tasks:
        print(task)
        if task.description:
            print(f"   📝 {task.description}")
    print("-" * 50)
    print(f"Total: {len(tasks)} tasks\n")


def main():
    todo = TodoList()
    
    while True:
        print("\n" + "="*50)
        print("📝 TO-DO LIST APPLICATION")
        print("="*50)
        print("1. Add Task")
        print("2. List All Tasks")
        print("3. List Active Tasks")
        print("4. Update Task")
        print("5. Toggle Complete/Incomplete")
        print("6. Delete Task")
        print("7. Clear Completed Tasks")
        print("8. View Tasks by Priority")
        print("9. Search Tasks")
        print("0. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye! Have a productive day!")
            break
        
        elif choice == "1":
            title = input("Task title: ").strip()
            if not title:
                print("❌ Title cannot be empty!")
                continue
            
            description = input("Description (optional): ").strip()
            due_date = input("Due date (YYYY-MM-DD, optional): ").strip()
            if due_date and not validate_date(due_date):
                print("❌ Invalid date format! Use YYYY-MM-DD")
                continue
            
            priority = input("Priority (low/medium/high, default: medium): ").strip().lower()
            if priority not in ["low", "medium", "high", ""]:
                print("❌ Invalid priority! Use low, medium, or high")
                continue
            priority = priority or "medium"
            
            task = todo.add_task(title, description, due_date, priority)
            print(f"✅ Task added successfully! (ID: {task.id})")
        
        elif choice == "2":
            display_tasks(todo.get_all_tasks(), "All Tasks")
        
        elif choice == "3":
            display_tasks(todo.get_all_tasks(show_completed=False), "Active Tasks")
        
        elif choice == "4":
            try:
                task_id = int(input("Enter task ID to update: "))
                task = todo.get_task(task_id)
                if not task:
                    print("❌ Task not found!")
                    continue
                
                print(f"Current: {task}")
                title = input(f"New title (current: {task.title}): ").strip()
                description = input(f"New description (current: {task.description}): ").strip()
                due_date = input(f"New due date (current: {task.due_date}): ").strip()
                if due_date and not validate_date(due_date):
                    print("❌ Invalid date format!")
                    continue
                priority = input(f"New priority (current: {task.priority}): ").strip().lower()
                if priority and priority not in ["low", "medium", "high"]:
                    print("❌ Invalid priority!")
                    continue
                
                todo.update_task(
                    task_id,
                    title=title or None,
                    description=description or None,
                    due_date=due_date or None,
                    priority=priority or None
                )
                print("✅ Task updated successfully!")
            except ValueError:
                print("❌ Invalid ID format!")
        
        elif choice == "5":
            try:
                task_id = int(input("Enter task ID to toggle: "))
                if todo.toggle_complete(task_id):
                    task = todo.get_task(task_id)
                    status = "completed" if task.completed else "incomplete"
                    print(f"✅ Task marked as {status}!")
                else:
                    print("❌ Task not found!")
            except ValueError:
                print("❌ Invalid ID format!")
        
        elif choice == "6":
            try:
                task_id = int(input("Enter task ID to delete: "))
                if todo.delete_task(task_id):
                    print("✅ Task deleted successfully!")
                else:
                    print("❌ Task not found!")
            except ValueError:
                print("❌ Invalid ID format!")
        
        elif choice == "7":
            count = todo.clear_completed()
            print(f"✅ Cleared {count} completed tasks!")
        
        elif choice == "8":
            priority = input("Enter priority (low/medium/high): ").strip().lower()
            if priority not in ["low", "medium", "high"]:
                print("❌ Invalid priority!")
                continue
            tasks = todo.get_tasks_by_priority(priority)
            display_tasks(tasks, f"{priority.upper()} Priority Tasks")
        
        elif choice == "9":
            keyword = input("Enter search keyword: ").strip().lower()
            if not keyword:
                print("❌ Keyword cannot be empty!")
                continue
            results = [t for t in todo.get_all_tasks() 
                      if keyword in t.title.lower() or keyword in t.description.lower()]
            display_tasks(results, f"Search Results: '{keyword}'")
        
        else:
            print("❌ Invalid choice! Please enter a number between 0 and 9.")


def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    main()