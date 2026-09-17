from django.test import TestCase
from django.urls import reverse

from .models import User


class UserModelTests(TestCase):
    def test_create_teacher_and_student(self):
        teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)
        student = User.objects.create_user(username='s1', password='pass12345', role=User.Role.STUDENT)
        self.assertTrue(teacher.is_teacher)
        self.assertTrue(student.is_student)
        self.assertFalse(teacher.is_super_admin)


class SuperAdminAccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='pass12345', email='a@a.com')
        self.teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)

    def test_teacher_cannot_create_teacher(self):
        self.client.login(username='t1', password='pass12345')
        response = self.client.get(reverse('accounts:create_teacher'))
        self.assertRedirects(response, reverse('accounts:dashboard_redirect'))

    def test_admin_can_create_teacher(self):
        self.client.login(username='admin', password='pass12345')
        response = self.client.post(reverse('accounts:create_teacher'), {
            'username': 't2',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='t2', role=User.Role.TEACHER).exists())

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'admin', 'password': 'pass12345',
        })
        self.assertRedirects(response, reverse('accounts:dashboard_redirect'))
