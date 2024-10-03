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
import json

load_dotenv()

class TaskStatus(str, Enum):
    DONE = "done"
    NOT_DONE = "not_done"

@dataclass
class Task:
    id: int
    name: str
    deadline: int
    status: TaskStatus

tasks: List[Task] = [
    Task(1, "Create a new landing page", 3, TaskStatus.NOT_DONE),
]
task_id_counter = 2

groq_client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = FastHTML()

def generate_task():
    global task_id_counter
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
        id=task_id_counter,
        name=task_name,
        deadline=random.randint(1, 7),
        status=random.choice([TaskStatus.DONE, TaskStatus.NOT_DONE]),
    )
    task_id_counter += 1
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

def delete_longest_deadline_task():
    if tasks:
        longest_deadline_task = max(tasks, key=lambda t: t.deadline)
        tasks.remove(longest_deadline_task)
        return longest_deadline_task.id
    return None

def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task.id != task_id]

@app.get("/")
def home():
    return Main(
        Head(
            Title("Task Generator"),
            Link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css"
            ),
            Script("""
                function updateTasks() {
                    fetch('/get_tasks')
                        .then(response => response.json())
                        .then(data => {
                            const tbody = document.querySelector('tbody');
                            tbody.innerHTML = '';
                            data.tasks.forEach(task => {
                                const row = document.createElement('tr');
                                row.innerHTML = `
                                    <td class="px-6 py-4">${task.name}</td>
                                    <td class="px-6 py-4">${task.deadline} days</td>
                                    <td class="px-6 py-4">
                                        <div class="px-3 py-1 rounded-full text-sm inline-block 
                                            ${task.status === 'done' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                            ${task.status}
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <button onclick="deleteTask(${task.id})" class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded">
                                            Delete
                                        </button>
                                    </td>
                                `;
                                row.className = 'border-b border-gray-200 hover:bg-gray-50';
                                tbody.appendChild(row);
                            });
                            document.getElementById('totalTasks').textContent = `Total Tasks: ${data.tasks.length}`;
                        });
                }
                
                function deleteTask(taskId) {
                    fetch(`/delete_task/${taskId}`, { method: 'POST' })
                        .then(() => updateTasks());
                }
                
                function deleteLongestDeadlineTask() {
                    fetch('/delete_longest_deadline_task', { method: 'POST' })
                        .then(() => updateTasks());
                }
                
                setInterval(updateTasks, 5000);
                updateTasks();
            """)
        ),
        Body(
            Div(
                H1("Auto-Generated Tasks", cls="text-3xl font-bold mb-6 text-center"),
                Div(
                    P(
                        "Total Tasks: 0", 
                        id="totalTasks",
                        cls="text-lg mb-2"
                    ),
                    Button(
                        "Delete Longest Deadline Task",
                        onclick="deleteLongestDeadlineTask()",
                        cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4"
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
                                Th("Actions", cls="px-6 py-3 text-left"),
                            ),
                            cls="bg-gray-100"
                        ),
                        Tbody(),
                        cls="min-w-full divide-y divide-gray-200"
                    ),
                    cls="shadow overflow-hidden border-b border-gray-200 rounded-lg bg-white"
                ),
                cls="container mx-auto px-4 py-8"
            )
        )
    )

@app.get("/get_tasks")
def get_tasks():
    return json.dumps({
        "tasks": [
            {
                "id": task.id,
                "name": task.name,
                "deadline": task.deadline,
                "status": task.status.value
            } for task in reversed(tasks)
        ]
    })

@app.post("/delete_task/{task_id}")
def delete_task_endpoint(task_id: int):
    delete_task(task_id)
    return "Task deleted"

@app.post("/delete_longest_deadline_task")
def delete_longest_deadline_task_endpoint():
    deleted_task_id = delete_longest_deadline_task()
    return f"Task with ID {deleted_task_id} deleted" if deleted_task_id else "No tasks to delete"

if __name__ == "__main__":
    try:
        generate_task()
        
        generator = threading.Thread(target=task_generator_thread, daemon=True)
        generator.start()
        
        serve()
    except Exception as e:
        print(f"An error occurred: {e}")