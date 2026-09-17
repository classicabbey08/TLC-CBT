from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from exams.models import Choice, Exam, Question, Subject

from .models import ExamAttempt


class CBTEngineTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='t1', password='pass12345', role=User.Role.TEACHER)
        self.student = User.objects.create_user(username='s1', password='pass12345', role=User.Role.STUDENT)

        self.subject = Subject.objects.create(name='Math', created_by=self.teacher)
        self.exam = Exam.objects.create(
            subject=self.subject, title='Algebra Test', duration_minutes=30, created_by=self.teacher
        )
        self.q1 = Question.objects.create(exam=self.exam, text='2 + 2 = ?', marks=1)
        self.c1_correct = Choice.objects.create(question=self.q1, text='4', is_correct=True)
        self.c1_wrong = Choice.objects.create(question=self.q1, text='5', is_correct=False)

        self.q2 = Question.objects.create(exam=self.exam, text='3 + 3 = ?', marks=2)
        self.c2_correct = Choice.objects.create(question=self.q2, text='6', is_correct=True)
        self.c2_wrong = Choice.objects.create(question=self.q2, text='7', is_correct=False)

    def test_full_student_flow_and_scoring(self):
        self.client.login(username='s1', password='pass12345')

        start_resp = self.client.get(reverse('attempts:start_exam', args=[self.exam.id]))
        attempt = ExamAttempt.objects.get(student=self.student, exam=self.exam)
        self.assertRedirects(start_resp, reverse('attempts:take_exam', args=[attempt.id]))

        take_resp = self.client.get(reverse('attempts:take_exam', args=[attempt.id]))
        self.assertEqual(take_resp.status_code, 200)

        submit_resp = self.client.post(reverse('attempts:submit_exam', args=[attempt.id]), {
            f'question_{self.q1.id}': self.c1_correct.id,
            f'question_{self.q2.id}': self.c2_wrong.id,
        })
        self.assertRedirects(submit_resp, reverse('attempts:result_detail', args=[attempt.id]))

        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.Status.SUBMITTED)
        self.assertEqual(attempt.score, 1)  # only q1 correct (1 mark), q2 wrong (2 marks missed)
        self.assertEqual(attempt.total_marks, 3)

    def test_cannot_resubmit(self):
        self.client.login(username='s1', password='pass12345')
        self.client.get(reverse('attempts:start_exam', args=[self.exam.id]))
        attempt = ExamAttempt.objects.get(student=self.student, exam=self.exam)

        self.client.post(reverse('attempts:submit_exam', args=[attempt.id]), {
            f'question_{self.q1.id}': self.c1_correct.id,
        })
        attempt.refresh_from_db()
        first_score = attempt.score

        # Try to submit again with a different (better) answer set.
        self.client.post(reverse('attempts:submit_exam', args=[attempt.id]), {
            f'question_{self.q1.id}': self.c1_correct.id,
            f'question_{self.q2.id}': self.c2_correct.id,
        })
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, first_score)

    def test_expired_attempt_is_auto_finalized_server_side(self):
        self.client.login(username='s1', password='pass12345')
        attempt = ExamAttempt.objects.create(student=self.student, exam=self.exam)
        # Force the attempt to look like it started long before the exam's duration.
        ExamAttempt.objects.filter(id=attempt.id).update(
            started_at=timezone.now() - timezone.timedelta(minutes=self.exam.duration_minutes + 5)
        )

        response = self.client.get(reverse('attempts:take_exam', args=[attempt.id]))
        self.assertRedirects(response, reverse('attempts:result_detail', args=[attempt.id]))

        attempt.refresh_from_db()
        self.assertEqual(attempt.status, ExamAttempt.Status.SUBMITTED)
        self.assertEqual(attempt.score, 0)

    def test_other_students_cannot_view_each_others_attempt(self):
        other = User.objects.create_user(username='s2', password='pass12345', role=User.Role.STUDENT)
        attempt = ExamAttempt.objects.create(student=self.student, exam=self.exam)

        self.client.login(username='s2', password='pass12345')
        response = self.client.get(reverse('attempts:take_exam', args=[attempt.id]))
        self.assertEqual(response.status_code, 404)

    def test_teacher_sees_only_own_exam_results(self):
        other_teacher = User.objects.create_user(username='t2', password='pass12345', role=User.Role.TEACHER)
        other_subject = Subject.objects.create(name='Physics', created_by=other_teacher)
        other_exam = Exam.objects.create(
            subject=other_subject, title='Physics Test', created_by=other_teacher, duration_minutes=30
        )
        ExamAttempt.objects.create(
            student=self.student, exam=other_exam,
            status=ExamAttempt.Status.SUBMITTED, submitted_at=timezone.now(), score=5,
        )
        ExamAttempt.objects.create(
            student=self.student, exam=self.exam,
            status=ExamAttempt.Status.SUBMITTED, submitted_at=timezone.now(), score=2,
        )

        self.client.login(username='t1', password='pass12345')
        response = self.client.get(reverse('attempts:teacher_results'))
        self.assertContains(response, 'Algebra Test')
        self.assertNotContains(response, 'Physics Test')

    def test_super_admin_sees_all_results(self):
        admin = User.objects.create_superuser(username='admin', password='pass12345', email='a@a.com')
        ExamAttempt.objects.create(
            student=self.student, exam=self.exam,
            status=ExamAttempt.Status.SUBMITTED, submitted_at=timezone.now(), score=3,
        )
        self.client.login(username='admin', password='pass12345')
        response = self.client.get(reverse('attempts:admin_results'))
        self.assertContains(response, 'Algebra Test')
        self.assertContains(response, 's1')
