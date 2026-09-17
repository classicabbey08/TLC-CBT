from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Choice, Exam, Question, Subject


class ExamsTeacherFlowTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)
        self.other_teacher = User.objects.create_user(username='t2', password='pass12345', role=User.Role.TEACHER)
        self.student = User.objects.create_user(username='s1', password='pass12345', role=User.Role.STUDENT)

    def test_student_cannot_add_subject(self):
        self.client.login(username='s1', password='pass12345')
        response = self.client.get(reverse('exams:subject_create'))
        self.assertRedirects(response, reverse('accounts:dashboard_redirect'))

    def test_teacher_can_add_subject(self):
        self.client.login(username='t1', password='pass12345')
        response = self.client.post(reverse('exams:subject_create'), {'name': 'Mathematics', 'description': ''})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Subject.objects.filter(name='Mathematics', created_by=self.teacher).exists())

    def test_teacher_can_create_exam_and_question_with_choices(self):
        self.client.login(username='t1', password='pass12345')
        subject = Subject.objects.create(name='Physics', created_by=self.teacher)
        exam_resp = self.client.post(reverse('exams:exam_create'), {
            'subject': subject.id, 'title': 'Midterm', 'duration_minutes': 30, 'is_active': True,
        })
        exam = Exam.objects.get(title='Midterm')
        self.assertEqual(exam.created_by, self.teacher)

        post_data = {
            'text': 'What is gravity?',
            'marks': 2,
            'choices-TOTAL_FORMS': '4',
            'choices-INITIAL_FORMS': '0',
            'choices-MIN_NUM_FORMS': '2',
            'choices-MAX_NUM_FORMS': '1000',
            'choices-0-text': 'A force',
            'choices-0-is_correct': 'on',
            'choices-1-text': 'A color',
            'choices-1-is_correct': '',
            'choices-2-text': '',
            'choices-2-is_correct': '',
            'choices-3-text': '',
            'choices-3-is_correct': '',
        }
        response = self.client.post(reverse('exams:question_create', args=[exam.id]), post_data)
        self.assertEqual(response.status_code, 302)
        question = Question.objects.get(exam=exam)
        self.assertEqual(question.choices.count(), 2)
        self.assertEqual(question.choices.filter(is_correct=True).count(), 1)

    def test_teacher_cannot_access_other_teachers_exam(self):
        self.client.login(username='t2', password='pass12345')
        subject = Subject.objects.create(name='Chemistry', created_by=self.teacher)
        exam = Exam.objects.create(subject=subject, title='Quiz', created_by=self.teacher)
        response = self.client.get(reverse('exams:question_list', args=[exam.id]))
        self.assertEqual(response.status_code, 404)
