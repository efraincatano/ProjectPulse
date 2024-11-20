import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import RequestFactory
from .models import Notification
from .views import home, signup, dashboard, project_detail, notifications

class ProjectManagementTests(TestCase):
    def setUp(self):
        # Create a test user
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            password='12345'
        )
        self.factory = RequestFactory()

    def test_home_view_get(self):
        """Test home view renders login form"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_view_post_invalid_credentials(self):
        """Test home view with invalid login credentials"""
        response = self.client.post(reverse('home'), {
            'username': 'wronguser', 
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect username or password')

    def test_signup_view_get(self):
        """Test signup view renders signup form"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_view_valid_registration(self):
        """Test successful user registration"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser', 
            'password1': 'testpass123', 
            'password2': 'testpass123'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_view_password_mismatch(self):
        """Test signup with mismatched passwords"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser', 
            'password1': 'testpass123', 
            'password2': 'differentpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password do not match')

    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated user"""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_dashboard_view_unauthenticated(self):
        """Test dashboard view redirects unauthenticated users"""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_project_creation(self):
        """Test creating a new project"""
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('dashboard'), {
            'name': 'Test Project',
            'description': 'A test project description'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_notifications_view(self):
        """Test notifications view"""
        # Create some test notifications
        Notification.objects.create(
            user=self.user, 
            message='Test notification', 
            is_read=False
        )
        
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications.html')

    def test_mark_notifications_as_read(self):
        """Test marking notifications as read"""
        notification = Notification.objects.create(
            user=self.user, 
            message='Test notification', 
            is_read=False
        )
        
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('mark_as_read'), {
            'notification_id': notification.id
        })
        
        # Refresh notification from database
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        self.assertRedirects(response, reverse('dashboard'))

    def test_profile_view(self):
        """Test profile view and update"""
        self.client.login(username='testuser', password='12345')
        
        # GET request
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        
        # POST request to update profile
        response = self.client.post(reverse('profile'), {
            'username': 'updateduser',
            'last_name': 'TestLastName',
            'email': 'updated@example.com'
        })
        self.assertRedirects(response, reverse('profile'))
        
        # Verify user was updated
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertEqual(updated_user.last_name, 'TestLastName')
        self.assertEqual(updated_user.email, 'updated@example.com')

# Additional test for database utility functions
def test_db_sentdata():
    """Test database sending data function"""
    from .views import db_sentdata
    import sqlite3

    # Test successful insert
    result = db_sentdata(
        "INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)", 
        ('test_table', 1)
    )
    assert result is True

def test_db_getdata():
    """Test database getting data function"""
    from .views import db_getdata
    
    # Test retrieving data
    result = db_getdata("SELECT 1")
    assert result is not None

    