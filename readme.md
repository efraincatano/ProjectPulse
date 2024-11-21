# ProjectPulse 🚀

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation](#installation)
5. [Project Structure](#project-structure)
6. [Database Models](#database-models)
7. [Views and Functionality](#views-and-functionality)
8. [Authentication](#authentication)
9. [User Workflow](#user-workflow)
10. [API URLs](#api-urls)
11. [API Endpoints Detailed](#api-endpoints-detailed)


## Overview

ProjectPulse is a comprehensive project management web application designed to help teams collaborate, track progress, and manage tasks efficiently. Built with Django, it provides a robust platform for project tracking, task assignment, and team communication.

## Features

### User Management
- User registration and authentication
- Profile management
- Role-based access control

### Project Management
- Create, edit, and delete projects
- Assign multiple users to projects
- Track project start and end dates
- Mark projects as completed or restart

### Task Management
- Create tasks within projects
- Assign tasks to specific users
- Track task progress
- Add notes to tasks
- Mark tasks as complete

### Collaboration
- Multi-user project and task assignment
- Real-time notifications
- User invitation to projects

### Notification System
- Receive notifications for project and task assignments
- Mark notifications as read
- Track unread notifications

## Technology Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL / SQLite3 (development)
- **Frontend**: HTML5, Bootstrap
- **Authentication**: Django's built-in authentication system
- **ORM**: Django ORM with SQLite

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (recommended)

### Setup Steps

1. Clone the repository
```bash
git clone https://github.com/efraincatano/ProjectPulse.git
cd projectpulse
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server
```bash
python manage.py runserver
```

## Project Structure

```
projectpulse/
│
├── projects/
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # URL routing
│   └── templates/       # HTML templates
│
├── projectpulse/
│   ├── settings.py      # Django settings
│   └── urls.py          # Project-level URL configuration
│
└── manage.py            # Django management script
```

## Database Models

### Project Model
- `name`: Project name
- `description`: Project description
- `users`: Many-to-many relationship with User
- `startdate`: Project creation date
- `enddate`: Project completion date
- `createdby`: User who created the project

### Task Model
- `name`: Task name
- `description`: Task description
- `proyecto`: Foreign key to Project
- `user`: Many-to-many relationship with User
- `startdate`: Task creation date
- `enddate`: Task completion date

### Notes Model
- `task`: Foreign key to Task
- `user`: Foreign key to User
- `text`: Note content
- `created_at`: Note creation timestamp

### Notification Model
- `user`: Foreign key to User
- `message`: Notification text
- `created_at`: Notification timestamp
- `is_read`: Read status

## Views and Functionality

### Authentication Views
- `home`: Login page
- `signup`: User registration
- `close_session`: Logout

### Project Views
- `dashboard`: Display user's projects
- `project_detail`: Detailed project view
- `new_project`: Create new project
- `finished_project`: View completed projects

### Task Management
- Create tasks
- Assign users to tasks
- Add notes to tasks
- Delete/edit tasks

### Notification Management
- `notifications`: View notifications
- `mark_as_read`: Mark notifications as read

## Authentication

- User registration with username and password
- Django's built-in authentication
- Login required for most views
- Profile management with basic user information update

## User Workflow

1. Register/Login
2. Create or join a project
3. Create tasks within projects
4. Assign tasks to team members
5. Add notes and track progress
6. Receive notifications about assignments

## API URLs

- `/`: Home/Login
- `/signup`: User registration
- `/dashboard`: User dashboard
- `/project_detail/<project_id>`: Project details
- `/new_project`: Create new project
- `/profile`: User profile management

## API Endpoints Detailed 

### Authentication Views

#### `home(request)`
- **Endpoint**: `/` or `/home`
- **HTTP Methods**: GET, POST
- **Functionality**: 
  - GET: Renders login page with authentication form
  - POST: Handles user login authentication
- **Parameters**:
  - `username`: User's username
  - `password`: User's password
- **Responses**:
  - Successful login: Redirects to dashboard
  - Failed login: Renders login page with error message

#### `signup(request)`
- **Endpoint**: `/signup`
- **HTTP Methods**: GET, POST
- **Functionality**:
  - GET: Renders user registration form
  - POST: Handles user registration
- **Parameters**:
  - `username`: Desired username
  - `password1`: Password
  - `password2`: Password confirmation
- **Validation**:
  - Checks password match
  - Ensures username is unique
- **Responses**:
  - Successful registration: Logs in user, redirects to dashboard
  - Failed registration: Renders signup page with error

#### `close_session(request)`
- **Endpoint**: `/close_session`
- **HTTP Methods**: GET
- **Functionality**: 
  - Logs out current user
- **Responses**: 
  - Redirects to home page

### Dashboard Views

#### `dashboard(request)`
- **Endpoint**: `/dashboard`
- **HTTP Methods**: GET, POST
- **Authentication**: Login required
- **Functionality**:
  - GET: Displays user's projects
  - POST: Supports multiple operations:
    1. Delete project
    2. Complete project
    3. Restart project
    4. Create new project
- **Query Operations**:
  - Retrieves projects created by user or user is a member of
  - Fetches recent notifications
- **Parameters** (POST):
  - `projectid`: Project ID to delete
  - `complete_projectid`: Project ID to mark as complete
  - `restart_projectid`: Project ID to restart
  - `name`: New project name
  - `description`: New project description
- **Responses**:
  - Renders dashboard with project list
  - Redirects after successful operations

### Project Detail Views

#### `project_detail(request, project_id)`
- **Endpoint**: `/project_detail/<int:project_id>/`
- **HTTP Methods**: GET, POST
- **Authentication**: Login required
- **Comprehensive Functionality**:
  1. Project Management
     - Edit project details
     - Delete project
     - Add/remove users from project
  2. Task Management
     - Create tasks
     - Assign users to tasks
     - Delete tasks
     - Mark tasks as complete
     - Edit task details
  3. Notes Management
     - Add notes to tasks
     - Edit notes
     - Delete notes
- **Supported Operations**:
  - Edit Project
    - Update name and description
  - User Management
    - Add users to project
    - Remove users from project
  - Task Operations
    - Create new task
    - Assign users to task
    - Delete task
    - Complete task
    - Edit task details
  - Note Operations
    - Create note
    - Delete note
    - Edit note
- **Detailed Request Handling**:
  ```python
  # Example of operation detection
  if request.POST.get('name'):
      # Edit project details
  elif request.POST.get('add_task'):
      # Create new task
  elif request.POST.get('userto_task[]'):
      # Assign user to task
  ```

### Notification Views

#### `notifications(request)`
- **Endpoint**: `/notifications`
- **HTTP Methods**: GET
- **Authentication**: Login required
- **Functionality**:
  - Retrieve unread notifications
  - Display notification list

#### `mark_as_read(request)`
- **Endpoint**: `/mark-as-read/`
- **HTTP Methods**: POST
- **Authentication**: Login required
- **Functionality**:
  - Mark specific notification as read
- **Parameters**:
  - `notification_id`: ID of notification to mark as read

### Profile View

#### `profile(request)`
- **Endpoint**: `/profile/`
- **HTTP Methods**: GET, POST
- **Authentication**: Login required
- **Functionality**:
  - GET: Retrieve and display user profile
  - POST: Update user profile information
- **Updatable Fields**:
  - Username
  - Last Name
  - Email

### Database Interaction Utility Functions

#### `db_sentdata(sql, parameters)`
- **Purpose**: Execute database modification queries
- **Capabilities**:
  - Insert records
  - Update records
  - Delete records
- **Error Handling**:
  - Catches and logs SQLite errors
  - Returns boolean indication of operation success

#### `db_getdata(sql)`
- **Purpose**: Execute database read queries
- **Capabilities**:
  - Fetch records using raw SQL queries
  - Returns query results as a list of tuples



## Contact

Efrain Pescador : https://github.com/efraincatano

Project Link: [https://github.com/efraincatano/ProjectPulse](https://github.com/efraincatano/ProjectPulse)