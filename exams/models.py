from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import User


# =========================================================
# SUBJECT
# =========================================================

class Subject(models.Model):

    name = models.CharField(
        max_length=150
    )

    description = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subjects",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "name"
        ]

    def __str__(self):

        return self.name


# =========================================================
# EXAM
# =========================================================

class Exam(models.Model):
    """
    A CBT exam.

    CLASS RULES
    -----------

    JSS1 / JSS2 / JSS3
        Department = GENERAL

    SSS1 / SSS2 / SSS3
        Department = SCIENCE / COMMERCIAL / ARTS
    """

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exams",
    )

    title = models.CharField(
        max_length=200
    )

    target_class = models.CharField(
        max_length=10,
        choices=User.StudentClass.choices,
    )

    department = models.CharField(
        max_length=20,
        choices=User.Department.choices,
        default=User.Department.GENERAL,
    )

    duration_minutes = models.PositiveIntegerField(
        default=30
    )

    is_active = models.BooleanField(
        default=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exams",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-created_at"
        ]

    # =====================================================
    # VALIDATION
    # =====================================================

    def clean(self):

        jss_classes = [
            User.StudentClass.JSS1,
            User.StudentClass.JSS2,
            User.StudentClass.JSS3,
        ]

        ss_classes = [
            User.StudentClass.SSS1,
            User.StudentClass.SSS2,
            User.StudentClass.SSS3,
        ]

        # -------------------------------------------------
        # JSS
        # -------------------------------------------------

        if self.target_class in jss_classes:

            self.department = (
                User.Department.GENERAL
            )

        # -------------------------------------------------
        # SSS
        # -------------------------------------------------

        elif self.target_class in ss_classes:

            valid_departments = [
                User.Department.SCIENCE,
                User.Department.COMMERCIAL,
                User.Department.ARTS,
            ]

            if self.department not in valid_departments:

                raise ValidationError(
                    {
                        "department":
                        "SSS exams must have Science, Commercial, or Arts as the department."
                    }
                )

    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self,
        *args,
        **kwargs
    ):

        self.full_clean()

        super().save(
            *args,
            **kwargs
        )

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):

        if self.target_class.startswith(
            "JSS"
        ):

            return (
                f"{self.title} "
                f"({self.target_class})"
            )

        return (
            f"{self.title} "
            f"({self.target_class} - "
            f"{self.department})"
        )

    # =====================================================
    # QUESTION COUNT
    # =====================================================

    @property
    def question_count(self):

        return self.questions.count()

    # =====================================================
    # TOTAL MARKS
    # =====================================================

    @property
    def total_marks(self):

        return sum(
            self.questions.values_list(
                "marks",
                flat=True,
            )
        )


# =========================================================
# QUESTION
# =========================================================

class Question(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    text = models.TextField()

    marks = models.PositiveIntegerField(
        default=1
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "id"
        ]

    def __str__(self):

        return self.text[:60]


# =========================================================
# CHOICE
# =========================================================

class Choice(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
    )

    text = models.CharField(
        max_length=500
    )

    is_correct = models.BooleanField(
        default=False
    )

    def __str__(self):

        return self.text[:60]