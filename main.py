from fasthtml.common import *
import random
import threading
import time
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List

class TaskStatus(str, Enum):
    DONE = "done"
    NOT_DONE = "not_done"

@dataclass
class Task:
    name: str
    deadline: int
    status: TaskStatus

tasks: List[Task] = []

SAMPLE_TASKS = [
    "Write documentation",
    "Fix bugs",
    "Create backup",
    "Update website",
    "Review code",
    "Deploy app",
    "Test features",
    "Update dependencies",
    "Clean database",
    "Optimize code"
]

app = FastHTML()

def generate_task():
    new_task = Task(
        name=random.choice(SAMPLE_TASKS),
        deadline=random.randint(1, 7),
        status=random.choice([TaskStatus.DONE, TaskStatus.NOT_DONE]),
    )
    tasks.append(new_task)
    if len(tasks) > 10:
        tasks.pop(0)

def task_generator_thread():
    while True:
        generate_task()
        time.sleep(30) 

@app.get("/")
def home():
    return Main(
        Head(
            Title("Task Generator"),
            Link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css"
            ),
            Meta({"http-equiv": "refresh", "content": "30"}) 
        ),
        Body(
            Div(
                H1("Auto-Generated Tasks", cls="text-3xl font-bold mb-6 text-center"),
                Div(
                    P(
                        f"Total Tasks: {len(tasks)}", 
                        cls="text-lg mb-2"
                    ),
                    cls="text-center"
                ),
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Task Name", cls="px-6 py-3 text-left"),
                                Th("Deadline", cls="px-6 py-3 text-left"),
                                Th("Status", cls="px-6 py-3 text-left"),
                            ),
                            cls="bg-gray-100"
                        ),
                        Tbody(
                            *[
                                Tr(
                                    Td(task.name, cls="px-6 py-4"),
                                    Td(f"{task.deadline} days", cls="px-6 py-4"),
                                    Td(
                                        Div(
                                            task.status.value,
                                            cls=f"px-3 py-1 rounded-full text-sm inline-block "
                                                f"{'bg-green-100 text-green-800' if task.status == TaskStatus.DONE else 'bg-red-100 text-red-800'}"
                                        ),
                                        cls="px-6 py-4"
                                    ),
                                    cls="border-b border-gray-200 hover:bg-gray-50"
                                ) for task in reversed(tasks)
                            ]
                        ),
                        cls="min-w-full divide-y divide-gray-200"
                    ),
                    cls="shadow overflow-hidden border-b border-gray-200 rounded-lg bg-white"
                ),
                cls="container mx-auto px-4 py-8"
            )
        )
    )

if __name__ == "__main__":
    generate_task()
    
    generator = threading.Thread(target=task_generator_thread, daemon=True)
    generator.start()
    
    serve()