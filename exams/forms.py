from django import forms
from django.forms import inlineformset_factory

from accounts.models import User

from .models import Subject, Exam, Question, Choice


# =========================================================
# HELPERS
# =========================================================

JSS_CLASSES = [
    User.StudentClass.JSS1,
    User.StudentClass.JSS2,
    User.StudentClass.JSS3,
]

SS_CLASSES = [
    User.StudentClass.SSS1,
    User.StudentClass.SSS2,
    User.StudentClass.SSS3,
]


# =========================================================
# SUBJECT FORM
# =========================================================

class SubjectForm(forms.ModelForm):

    class Meta:
        model = Subject

        fields = [
            "name",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


# =========================================================
# EXAM FORM
# =========================================================

class ExamForm(forms.ModelForm):

    class Meta:
        model = Exam

        fields = [
            "subject",
            "title",
            "target_class",
            "department",
            "duration_minutes",
            "is_active",
        ]

        widgets = {
            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "target_class": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_target_class",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "id_department",
                }
            ),

            "duration_minutes": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }

    def __init__(
        self,
        *args,
        teacher=None,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        # -------------------------------------------------
        # SUBJECT PERMISSIONS
        # -------------------------------------------------

        if teacher is not None:

            if getattr(
                teacher,
                "is_super_admin",
                False,
            ):

                self.fields[
                    "subject"
                ].queryset = (
                    Subject.objects
                    .all()
                    .order_by("name")
                )

            else:

                self.fields[
                    "subject"
                ].queryset = (
                    Subject.objects
                    .filter(
                        created_by=teacher
                    )
                    .order_by("name")
                )

        # -------------------------------------------------
        # DEPARTMENT
        #
        # We include GENERAL here so JSS exams can use it.
        #
        # The clean() method below makes sure SSS exams
        # cannot use GENERAL.
        # -------------------------------------------------

        self.fields[
            "department"
        ].choices = [
            (
                User.Department.GENERAL,
                "General",
            ),
            (
                User.Department.SCIENCE,
                "Science",
            ),
            (
                User.Department.COMMERCIAL,
                "Commercial",
            ),
            (
                User.Department.ARTS,
                "Arts",
            ),
        ]

        # -------------------------------------------------
        # EXISTING EXAM
        #
        # If editing an existing JSS exam, General remains
        # selected.
        # -------------------------------------------------

        if self.instance and self.instance.pk:

            if self.instance.target_class in JSS_CLASSES:
                self.fields[
                    "department"
                ].initial = User.Department.GENERAL

    # =====================================================
    # CLEAN
    # =====================================================

    def clean(self):

        cleaned = super().clean()

        target_class = cleaned.get(
            "target_class"
        )

        department = cleaned.get(
            "department"
        )

        # -------------------------------------------------
        # JSS
        #
        # JSS1, JSS2 and JSS3 always use GENERAL.
        # -------------------------------------------------

        if target_class in JSS_CLASSES:

            cleaned[
                "department"
            ] = User.Department.GENERAL

        # -------------------------------------------------
        # SSS
        #
        # SSS1, SSS2 and SSS3 must use:
        #
        # Science
        # Commercial
        # Arts
        #
        # They cannot use General.
        # -------------------------------------------------

        elif target_class in SS_CLASSES:

            if not department:

                self.add_error(
                    "department",
                    "Please select a department for this SSS exam.",
                )

            elif department == User.Department.GENERAL:

                self.add_error(
                    "department",
                    "SSS exams must use Science, Commercial, or Arts.",
                )

        return cleaned


# =========================================================
# QUESTION FORM
# =========================================================

class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question

        fields = [
            "text",
            "marks",
        ]

        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                }
            ),
        }


# =========================================================
# CHOICE FORM
# =========================================================

class ChoiceForm(forms.ModelForm):

    class Meta:
        model = Choice

        fields = [
            "text",
            "is_correct",
        ]

        widgets = {
            "text": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "is_correct": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


# =========================================================
# CHOICE FORMSET
# =========================================================

ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=4,
    min_num=4,
    max_num=4,
    validate_min=True,
    validate_max=True,
    can_delete=False,
)