from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import connection
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import sqlite3
from .models import Notification
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
import os
from django.conf import settings

def home(request):
    if request.method == 'GET':
            return render(request, 'home.html',{
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], 
               password=request.POST['password'])
        if user is None:
            return render(request, 'home.html',{
            'form': AuthenticationForm,
            'error': 'Incorrect username or password'
        })
        else:
            login(request, user)
            return redirect('dashboard')

def signup(request):
    if request.method == 'GET':
        return render (request, 'signup.html', {
            'form' : UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                username = request.POST['username']
                password = request.POST['password1']
                user = User.objects.create_user(username=username, password=password)
                user.save()
                login(request, user)
                return redirect('dashboard')
            except:
                return render (request, 'signup.html', {
                'form' : UserCreationForm,
                'error': 'User already exists'
                })
        else:
            return render (request, 'signup.html', {
            'form' : UserCreationForm,
            'error': 'Password do not match'
            })
def close_session(request):
    logout(request)
    return redirect('home')

def dashboard(request):
    user_id = str(request.user.id)
    sql = """
    SELECT p.id, p.name, p.description, strftime('%d-%m-%Y', startdate) as startdate, strftime('%d-%m-%Y', enddate) as enddate, p.createdby FROM projects_project p
    WHERE p.createdby = {}

    UNION

    SELECT p.id, p.name, p.description, strftime('%d-%m-%Y', startdate) as startdate, strftime('%d-%m-%Y', enddate) as enddate, p.createdby
    FROM projects_project p
    JOIN projects_project_users up ON p.id = up.project_id
    WHERE up.user_id = {};
    """.format(user_id, user_id)
    result = db_getdata(sql)

    #Notifications
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    

    if request.method == 'GET':
        return render(request, 'dashboard.html', {
            'projects' : result, 
            'user_id': int(user_id),
            'notifications': notifications,
            'unread_count': unread_count
            })
    else:
        if request.POST.get('projectid'):
            projectid = request.POST['projectid']
            delete_queries = [
            "DELETE FROM projects_task_user WHERE project_id = ?",
            "DELETE FROM projects_task WHERE proyecto_id = ?",
            "DELETE FROM projects_project_users WHERE project_id = ?",
            "DELETE FROM projects_project WHERE id = ?"
            ]
            for query in delete_queries:
                db_sentdata(query, [projectid])
            result = db_getdata(sql)
            return redirect('dashboard')
        
        if request.POST.get('complete_projectid'):
            date_time = datetime.datetime.now()
            date_completed = str(date_time)
            complete_projectid = request.POST['complete_projectid']
            sql_update = "UPDATE projects_project set enddate = '"+date_completed+"' where id = " + complete_projectid
            if db_sentdata(sql_update, '') == False:
                print ('Error while updating de project')
            result = db_getdata(sql)
            return redirect('dashboard')
        
        if request.POST.get('restart_projectid'):
            project_id = request.POST['restart_projectid']
            sql_restart = "UPDATE projects_project set enddate = NULL where id = " + project_id
            if db_sentdata(sql_restart, '') == False:
                print ('Error while sql_restarting de project')
            result = db_getdata(sql)
            return redirect('dashboard')
        
        if request.POST.get('description'):
            name = request.POST['name']
            description = request.POST['description']
            startdate = datetime.datetime.now()
            user_id = str(request.user.id)
            values = (name, description, startdate, user_id)
            sql_insert = "INSERT INTO projects_project (name, description, startdate, createdby) VALUES (?, ?, ?, ?)"
            db_sentdata(sql_insert, values)
            result = db_getdata(sql)
            return redirect('dashboard')
        
        return render(request, 'dashboard.html', {
            'projects' : result, 
            'user_id': int(user_id),
            'notifications': notifications,
            'unread_count': unread_count,
            })

@login_required
def finished_project(request, project_id):
    user_id = str(request.user.id)
    projectid = str(project_id)

    sql_all_users = "SELECT id, username from auth_user"
    all_users = db_getdata(sql_all_users)
    
    sql = "SELECT id, name, description, strftime('%d-%m-%Y', startdate) as startdate, strftime('%d-%m-%Y', enddate) as enddate, createdby FROM projects_project  WHERE id =" + projectid
    project = db_getdata(sql)

    sql_user_in_project = """
    SELECT au.id, au.username
    FROM auth_user AS au 
    JOIN projects_project_users pu ON pu.user_id = au.id 
    WHERE pu.project_id = {} 

    UNION ALL 

    SELECT au.id, au.username
    FROM auth_user AS au 
    JOIN projects_project pp ON pp.createdby = au.id 
    WHERE pp.createdby = {} AND pp.id = {};
""".format(project_id, user_id, project_id)
    result_users_in_project = db_getdata(sql_user_in_project)

    #Tasks
    sql_task = "SELECT id, name, description, strftime('%d-%m-%Y', startdate) as startdate, enddate from projects_task where proyecto_id = " + projectid
    get_task = db_getdata(sql_task)
    sql_user_in_task = "SELECT t.task_id, t.user_id, u.username, t.id from projects_task_user t join projects_task p on p.id = t.task_id join auth_user u on t.user_id = u.id where p.proyecto_id = " + projectid
    user_in_task = db_getdata(sql_user_in_task)

    #Notes
    sql_notes = "SELECT n.id, n.text, strftime('%d-%m-%Y', n.created_at), n.task_id, n.user_id from projects_notes n join projects_task t on n.task_id = t.id where t.proyecto_id = " + projectid
    notes_for_proyect = db_getdata(sql_notes);

    if request.method == 'GET':
        return render (request, 'finished_project.html', {
            'user_id': int(user_id),
            'all_users': all_users,
            'project' : project,
            'users_in_project' : result_users_in_project,
            #Tasks
            'tasks' : get_task,
            "user_in_task": user_in_task,
            #Notes
            "notes": notes_for_proyect
            }) 

@login_required
def new_project(request):
    if request.method == 'GET':
        return render(request, 'new_project.html')
    else:
        return redirect('dashboard') 

@login_required
def project_detail(request, project_id):
    user_id = str(request.user.id)
    sql_all_users = "SELECT id, username from auth_user"
    all_users = db_getdata(sql_all_users)
    sql_users_select= """
    SELECT id, username 
    FROM auth_user 
    WHERE id <> {} 
    AND id NOT IN (SELECT user_id FROM projects_project_users WHERE project_id = {});
""".format(user_id, project_id)
    
    users_select = db_getdata(sql_users_select)
    projectid = str(project_id)
    sql = "SELECT id, name, description, strftime('%d-%m-%Y', startdate) as startdate, strftime('%d-%m-%Y', enddate) as enddate, createdby FROM projects_project  WHERE id =" + projectid
    project = db_getdata(sql)

    sql_user_in_project = """
    SELECT au.id, au.username
    FROM auth_user AS au 
    JOIN projects_project_users pu ON pu.user_id = au.id 
    WHERE pu.project_id = {} 

    UNION ALL 

    SELECT au.id, au.username
    FROM auth_user AS au 
    JOIN projects_project pp ON pp.createdby = au.id 
    WHERE pp.createdby = {} AND pp.id = {};
""".format(project_id, user_id, project_id)
    result_users_in_project = db_getdata(sql_user_in_project)
    #Tasks
    sql_task = "SELECT id, name, description, strftime('%d-%m-%Y', startdate) as startdate, strftime('%d-%m-%Y', enddate) as enddate from projects_task where proyecto_id = " + projectid
    get_task = db_getdata(sql_task)
    sql_user_in_task = "SELECT t.task_id, t.user_id, u.username, t.id from projects_task_user t join projects_task p on p.id = t.task_id join auth_user u on t.user_id = u.id where p.proyecto_id = " + projectid
    user_in_task = db_getdata(sql_user_in_task)
    #Notes
    sql_notes = "SELECT n.id, n.text, strftime('%d-%m-%Y', n.created_at), n.task_id, n.user_id from projects_notes n join projects_task t on n.task_id = t.id where t.proyecto_id = " + projectid
    notes_for_proyect = db_getdata(sql_notes);

    #Notifications
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    if request.method == 'GET':
        return render (request, 'project_detail.html', {
            'user_id': int(user_id),
            'all_users': all_users,
            'project' : project,
            'users_select' : users_select,
            'users_in_project' : result_users_in_project,
            #Tasks
            'tasks' : get_task,
            "user_in_task": user_in_task,
            #Notes
            "notes": notes_for_proyect,
            #Notifications
            'notifications': notifications,
            'unread_count': unread_count
            })  
    else:
        # Edit project
        if request.POST.get('name'):
            name = request.POST['name']
            description = request.POST['description']

            sql_update = "UPDATE projects_project SET name = ?, description = ? WHERE id =" + projectid
            values = (name, description)
            if db_sentdata(sql_update, values) == False:
                print ('Error while editing the project')
            return redirect('project_detail', project_id=project_id)
        
        # Delete project
        if request.POST.get('projectid'):
            project_id_del = request.POST['projectid']
            delete_queries = [
            "DELETE FROM projects_task_user WHERE project_id = ?",
            "DELETE FROM projects_task WHERE proyecto_id = ?",
            "DELETE FROM projects_project_users WHERE project_id = ?",
            "DELETE FROM projects_project WHERE id = ?"
            ]
            for query in delete_queries:
                db_sentdata(query, [project_id_del])
            result = db_getdata(sql)
            return redirect('dashboard')
        
        # Add users to project
        if request.POST.get('user[]'):
            user_toadd = request.POST['user[]']
            values = (projectid, user_toadd)
            sql_insert = "INSERT INTO projects_project_users (project_id, user_id) VALUES (?, ?)"
            db_sentdata(sql_insert, values)
            #Notification
            created_at = datetime.datetime.now()
            values_for_notification = ('You was assigned to a new project', created_at, False, user_toadd)
            sql_notification = "INSERT INTO projects_notification (message, created_at, is_read, user_id) VALUES (?, ?, ?, ?)"
            db_sentdata(sql_notification, values_for_notification)
            return redirect('project_detail', project_id=project_id)
        
        # Delete user from project
        if request.POST.get('del_user_from_pro'):
            user_to_del = request.POST['del_user_from_pro']
            sql_delete = "DELETE from projects_project_users where user_id = " + user_to_del + " AND project_id = " + projectid
            if db_sentdata(sql_delete, '') == False:
                print ('Error while unassigning the user')
            return redirect('project_detail', project_id=project_id)
        
        # Tasks view
        # Create task
        if request.POST.get('add_task'):
            name_task = request.POST['name_task']
            description_task = request.POST['description_task']
            startdate = str(datetime.datetime.now())

            values = (name_task, description_task, startdate, projectid)
            sql_insert_task = "INSERT INTO projects_task (name, description, startdate, proyecto_id) VALUES (?, ?, ?, ?)"
            task_id = db_sentdata(sql_insert_task, values)

            if task_id == False:
                print ('Error while creating the task')
            return redirect('project_detail', project_id=project_id)

        # Assign users to task
        if request.POST.get('userto_task[]'):
            user_to_task = request.POST['userto_task[]']
            task_id = request.POST['task_id']
            values = (task_id, user_to_task, projectid)
            insert_userto_taks = "INSERT into projects_task_user (task_id, user_id, project_id) VALUES (?, ?, ?)"
            if db_sentdata(insert_userto_taks, values) == False:
                print ('Error while assigning the user')
            else:
                created_at = datetime.datetime.now()
                values_for_notification = ('You was assigned to a new task', created_at, False, user_to_task)
                sql_notification = "INSERT INTO projects_notification (message, created_at, is_read, user_id) VALUES (?, ?, ?, ?)"
                db_sentdata(sql_notification, values_for_notification)
            return redirect('project_detail', project_id=project_id) 
        
        # Delete task   
        if request.POST.get('delete_task'):
            delete_task = request.POST['delete_task']
            sql_delete = "DELETE from projects_task where id =" + delete_task
            if db_sentdata(sql_delete, '') == False:
                print ('Error while deleting the task')
            return redirect('project_detail', project_id=project_id)
        
        # Mark task as done
        if request.POST.get('completed_task'):
            completed_task = request.POST['completed_task']
            date_time = datetime.datetime.now()
            date_completed = str(date_time)
            sql_completed_task = "UPDATE projects_task SET enddate = '" + date_completed + "' where id =" + completed_task
            if db_sentdata(sql_completed_task, '') == False:
                print ('Error while marking the task as done')
            return redirect('project_detail', project_id=project_id)
        
        # Edit task
        if request.POST.get('task_name_edit'):
            task_name_edit = request.POST['task_name_edit']
            task_desc_edit = request.POST['task_desc_edit']
            task_id_edit = request.POST['task_id_edit']

            sql_edit_task = "UPDATE projects_task SET name = ?, description = ? WHERE id =" + task_id_edit
            values = (task_name_edit, task_desc_edit)
            if db_sentdata(sql_edit_task, values) == False:
                print ('Error while editing the task')
            return redirect('project_detail', project_id=project_id)
        # Delete user from task
        if request.POST.get('del_user_from_task'):
            user_to_delete = request.POST['del_user_from_task']
            task_id_todel = request.POST['del_user_task_id']
            sql_delete = "DELETE from projects_task_user where task_id = " + task_id_todel + " AND user_id = " + user_to_delete
            if db_sentdata(sql_delete, '') == False:
                print ('Error while unassigning the user')
            return redirect('project_detail', project_id=project_id)
        
        #Notes
        # Create note in a task
        if request.POST.get('note_text'):
            task_id_note = request.POST['task_id_note']
            text = request.POST['note_text']
            user_id = str(request.user.id)
            created_at = str(datetime.datetime.now())
            values = (text, created_at, task_id_note, user_id)
            sql_insert_note = 'INSERT into projects_notes (text, created_at, task_id, user_id) VALUES (?, ?, ?, ?)'
            if db_sentdata(sql_insert_note, values) == False:
                print ('Error while creating the note')
            return redirect('project_detail', project_id=project_id)
        # Delete notes   
        if request.POST.get('delete_note'):
            delete_note = request.POST['delete_note']
            sql_delete = "DELETE from projects_notes where id =" + delete_note
            if db_sentdata(sql_delete, '') == False:
                print ('Error while deleting the note')
            return redirect('project_detail', project_id=project_id)
        # Edit note
        if request.POST.get('note_text_edit'):
            note_text_edit = request.POST['note_text_edit']
            note_id_edit = request.POST['note_id_edit']

            sql_edit_note = "UPDATE projects_notes SET text = ? WHERE id = ?" 
            values = (note_text_edit, note_id_edit)
            if db_sentdata(sql_edit_note, values) == False:
                print ('Error while editing the note')
            return redirect('project_detail', project_id=project_id)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    unread_count = notifications.count()

    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

@login_required
def profile(request):
    user_id = str(request.user.id)
    if request.method == "GET":
        
        sql_user_info = "SELECT username, last_name, email FROM auth_user WHERE id = " + user_id
        user_info = db_getdata(sql_user_info)

        #Notifications
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return render(request, "profile.html", {
            'user_info': user_info,
            'notifications': notifications,
            'unread_count': unread_count
            })
    else:
        username = request.POST.get("username")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        sql_update_profile = "UPDATE auth_user SET username = ?, last_name = ?, email = ? WHERE id = ?"
        values = (username, last_name, email, user_id)

        if db_sentdata(sql_update_profile, values) == False:
            print ('Error while update the user´s information')
        return redirect("profile")

# Mark notifications as read
@require_POST
def mark_as_read(request):
    notification_id = request.POST.get('notification_id')
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return redirect('dashboard')
    except Notification.DoesNotExist:
        return redirect('dashboard')


def db_sentdata(sql, parameters):
    try:
        with sqlite3.connect('db.sqlite3') as connection:
            cursor = connection.cursor()
            cursor.execute(sql, parameters)
            connection.commit()
            if sql.strip().upper().startswith("INSERT"):
                return cursor.lastrowid
            return True  
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        return False  
    except Exception as e:
        print(f"Error: {e}")
        return False  


def db_getdata(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = cursor.fetchall()
    return data

