# Task Generator App

This project is a dynamic task generation application built with FastHTML. It creates a todo-list-style interface where tasks are automatically generated and managed.

## Features

1. Automatic task generation every 30 seconds
2. Integration with Groq API for task creation
3. Display of tasks in a responsive table
4. Automatic deletion of the longest-duration task on button click

## How It Works

### 1. Task Generation

- Every 30 seconds, the app generates a new task.
- The task generation process involves:
  - Calling the Groq API to get a random task
  - Assigning a random deadline (0-9999 days)
  - Setting a random status (done/not done)

### 2. Task Display

- Tasks are displayed in a table format.
- The table shows:
  - Task name
  - Deadline
  - Status
- The table is updated every 30 seconds to reflect new tasks.

### 3. Task Management

- The app maintains a maximum of 10 tasks at any time.
- When a new task is added and the list exceeds 10 tasks, the oldest task is automatically removed.

### 4. Task Deletion

- A button is provided to manually trigger task deletion.
- When clicked, the task with the longest duration (deadline) is automatically removed from the list.

## Technical Implementation

### Backend

- Uses FastHTML for server-side rendering
- Implements a threaded task generator that runs in the background
- Integrates with Groq API for task content generation

### Frontend

- Utilizes Tailwind CSS for styling
- Implements auto-refresh every 30 seconds to update the task list

## Setup and Running

1. Install required dependencies (FastHTML, etc.) - pip install -r requirements.txt
2. Set up Groq API credentials in env.
3. Run the main script to start the server
4. Access the application through a web browser

## Future Enhancements

- User authentication for personalized task lists
- Task editing capabilities
- Persistence of tasks using a database
- More detailed task information and categories