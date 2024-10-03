from fasthtml.common import *
import random
import threading
import time
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List
import os
import groq
from dotenv import load_dotenv

load_dotenv()

class TaskStatus(str, Enum):
    DONE = "done"
    NOT_DONE = "not_done"

@dataclass
class Task:
    name: str
    deadline: int
    status: TaskStatus

tasks: List[Task] = [
    Task("Create a new landing page", 3, TaskStatus.NOT_DONE),
]

groq_client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = FastHTML()

def generate_task():
    prompt = "Generate a random task for a software development team. Respond with just the task name, nothing else."
    
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    task_name = chat_completion.choices[0].message.content.strip()
    print(f"Generated task: {task_name}")
    new_task = Task(
        name=task_name,
        deadline=random.randint(1, 7),
        status=random.choice([TaskStatus.DONE, TaskStatus.NOT_DONE]),
    )
    tasks.append(new_task)
    if len(tasks) > 10:
        tasks.pop(0)

def task_generator_thread():
    while True:
        try:
            generate_task()
            time.sleep(30)
        except Exception as e:
            print(f"Error generating task: {e}")
            time.sleep(30)

def task_table():
    return Table(
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
    )


@app.get("/")
def home():
    return Main(
        Head(
            Title("Task Generator"),
            Link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css"
            ),
            # Meta({"http-equiv": "refresh", "content": "30"}) 
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
    try:
        generate_task()
        
        generator = threading.Thread(target=task_generator_thread, daemon=True)
        generator.start()
        
        serve()
    except Exception as e:
        print(f"An error occurred: {e}")