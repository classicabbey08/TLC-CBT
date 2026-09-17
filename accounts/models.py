from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    """
    Single user model for all roles.
    """

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    class StudentClass(models.TextChoices):
        JSS1 = "JSS1", "JSS1"
        JSS2 = "JSS2", "JSS2"
        JSS3 = "JSS3", "JSS3"
        SSS1 = "SSS1", "SSS1"
        SSS2 = "SSS2", "SSS2"
        SSS3 = "SSS3", "SSS3"

    class Department(models.TextChoices):
        GENERAL = "GENERAL", "General"
        SCIENCE = "SCIENCE", "Science"
        COMMERCIAL = "COMMERCIAL", "Commercial"
        ARTS = "ARTS", "Arts"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    # Student information
    admission_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
    )

    student_class = models.CharField(
        max_length=10,
        choices=StudentClass.choices,
        blank=True,
        null=True,
        help_text="Only used for students",
    )

    department = models.CharField(
        max_length=20,
        choices=Department.choices,
        default=Department.GENERAL,
        blank=True,
        help_text="General for JSS students; Science, Commercial or Arts for SSS students.",
    )

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT