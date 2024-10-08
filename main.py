from fasthtml.common import *
import random
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List
import os
import groq
from dotenv import load_dotenv
import json
import time

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
    highlight: str = ""

tasks: List[Task] = []
task_id_counter = 1

groq_client = groq.Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = FastHTML()

def generate_task_name():
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

    return chat_completion.choices[0].message.content.strip()

def generate_task():
    global task_id_counter
    task_name = generate_task_name()
    print(f"Generated task: {task_name}")
    new_task = Task(
        id=task_id_counter,
        name=task_name,
        deadline=random.randint(0, 999),
        status=random.choice([TaskStatus.DONE, TaskStatus.NOT_DONE]),
    )
    task_id_counter += 1
    tasks.append(new_task)

def delete_longest_deadline_task():
    if tasks:
        longest_deadline_task = max(tasks, key=lambda t: t.deadline)
        tasks.remove(longest_deadline_task)
        return longest_deadline_task.id
    return None

def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task.id != task_id]

def update_task(task_id, new_name=None):
    for task in tasks:
        if task.id == task_id:
            if new_name is None:
                new_name = generate_task_name()
            task.name = new_name
            task.highlight = "green"
            return task
    return None

def update_longest_deadline_task():
    if tasks:
        longest_deadline_task = max(tasks, key=lambda t: t.deadline)
        return update_task(longest_deadline_task.id)
    return None

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
                                let highlightTask = '';
                                if (task.highlight === 'green') {
                                    highlightTask = 'bg-green-200';
                                } else if (task.highlight === 'red') {
                                    highlightTask = 'bg-red-200';
                                }
                                row.innerHTML = `
                                    <td class="px-6 py-4 ${highlightTask}">${task.name}</td>
                                    <td class="px-6 py-4">${task.deadline} days</td>
                                    <td class="px-6 py-4">
                                        <div class="px-3 py-1 rounded-full text-sm inline-block 
                                            ${task.status === 'done' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                            ${task.status}
                                        </div>
                                    </td>
                                    <td class="px-6 py-4">
                                        <button onclick="updateTask(${task.id})" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded mr-2">
                                            Update
                                        </button>
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
                
                function updateTask(taskId) {
                    fetch(`/update_task/${taskId}`, { method: 'POST' })
                        .then(() => updateTasks());
                }
                
                function deleteLongestDeadlineTask() {
                    fetch('/delete_longest_deadline_task', { method: 'POST' })
                        .then(() => updateTasks());
                }
                
                function updateLongestDeadlineTask() {
                    fetch('/update_longest_deadline_task', { method: 'POST' })
                        .then(() => {
                            updateTasks();
                            setTimeout(() => {
                                fetch('/set_highlight_red', { method: 'POST' })
                                    .then(() => {
                                        updateTasks();
                                        setTimeout(() => {
                                            fetch('/clear_highlight', { method: 'POST' })
                                                .then(() => updateTasks());
                                        }, 3000);
                                    });
                            }, 3000);
                        });
                }
                
                setInterval(updateTasks, 30000);
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
                        cls="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mb-4 mr-2"
                    ),
                    Button(
                        "Update Longest Deadline Task",
                        onclick="updateLongestDeadlineTask()",
                        cls="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mb-4"
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
    generate_task()
    return json.dumps({
        "tasks": [
            {
                "id": task.id,
                "name": task.name,
                "deadline": task.deadline,
                "status": task.status.value,
                "highlight": task.highlight
            } for task in reversed(tasks)
        ]
    })

@app.post("/delete_task/{task_id}")
def delete_task_endpoint(task_id: int):
    delete_task(task_id)
    return "Task deleted"

@app.post("/update_task/{task_id}")
def update_task_endpoint(task_id: int):
    updated_task = update_task(task_id)
    return f"Task updated: {updated_task.name}" if updated_task else "Task not found"

@app.post("/delete_longest_deadline_task")
def delete_longest_deadline_task_endpoint():
    deleted_task_id = delete_longest_deadline_task()
    return f"Task with ID {deleted_task_id} deleted" if deleted_task_id else "No tasks to delete"

@app.post("/update_longest_deadline_task")
def update_longest_deadline_task_endpoint():
    updated_task = update_longest_deadline_task()
    return f"Task updated: {updated_task.name}" if updated_task else "No tasks to update"

@app.post("/set_highlight_red")
def set_highlight_red():
    if tasks:
        longest_deadline_task = max(tasks, key=lambda t: t.deadline)
        longest_deadline_task.highlight = "red"
    return "Highlight set to red"

@app.post("/clear_highlight")
def clear_highlight():
    if tasks:
        longest_deadline_task = max(tasks, key=lambda t: t.deadline)
        longest_deadline_task.highlight = ""
    return "Highlight cleared"

if __name__ == "__main__":
    try:
        generate_task()
        serve()
    except Exception as e:
        print(f"An error occurred: {e}")