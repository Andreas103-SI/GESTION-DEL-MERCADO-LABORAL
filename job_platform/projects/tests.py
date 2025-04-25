#projects/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Project, Task, Skill
from datetime import date

# Create your tests here.

class ProjectModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            start_date=date.today(),
            end_date=date.today(),
            manager=self.user
        )

    def test_project_creation(self):
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.manager, self.user)

class TaskModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            start_date=date.today(),
            end_date=date.today(),
            manager=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='A test task',
            state='pending',
            priority='medium',
            deadline=date.today(),
            project=self.project
        )
        self.task.collaborators.add(self.user)

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.project, self.project)
        self.assertIn(self.user, self.task.collaborators.all())

class SkillModelTests(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(name='Python')

    def test_skill_creation(self):
        self.assertEqual(self.skill.name, 'Python')
