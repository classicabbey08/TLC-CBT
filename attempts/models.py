from django.conf import settings
from django.db import models
from django.utils import timezone

from exams.models import Choice, Exam, Question


class ExamAttempt(models.Model):
    """
    One attempt per (student, exam) — a student may only sit each CBT
    once. `started_at` is set the moment the attempt is created and is
    the single source of truth for the countdown; the timer shown to
    the student is only a UI reflection of time remaining relative to
    this timestamp, recomputed server-side on every request.
    """

    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        SUBMITTED = 'SUBMITTED', 'Submitted'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exam_attempts'
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'exam')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

    @property
    def deadline(self):
        return self.started_at + timezone.timedelta(minutes=self.exam.duration_minutes)

    @property
    def seconds_remaining(self):
        remaining = (self.deadline - timezone.now()).total_seconds()
        return max(0, int(remaining))

    @property
    def is_expired(self):
        return timezone.now() >= self.deadline

    @property
    def total_marks(self):
        return self.exam.total_marks


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    selected_choice = models.ForeignKey(
        Choice, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_answers'
    )

    class Meta:
        unique_together = ('attempt', 'question')

    def __str__(self):
        return f"{self.attempt} - Q{self.question_id}"
