from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User


# =========================================================
# TEACHER CREATION
# =========================================================

class TeacherCreationForm(UserCreationForm):

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
        }

    def save(self, commit=True):

        user = super().save(commit=False)

        user.role = User.Role.TEACHER

        if commit:
            user.save()

        return user


# =========================================================
# SUPER ADMIN - STUDENT CREATION
# =========================================================

class StudentCreationForm(UserCreationForm):

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "admission_number",
            "student_class",
            "department",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "admission_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "student_class": forms.Select(
                attrs={"class": "form-select"}
            ),
            "department": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def clean(self):

        cleaned = super().clean()

        student_class = cleaned.get("student_class")
        department = cleaned.get("department")

        jss_classes = [
            User.StudentClass.JSS1,
            User.StudentClass.JSS2,
            User.StudentClass.JSS3,
        ]

        # JSS students do not have departments.
        if student_class in jss_classes:

            cleaned["department"] = User.Department.GENERAL

        # SS students must have a department.
        else:

            if (
                not department
                or department == User.Department.GENERAL
            ):

                self.add_error(
                    "department",
                    "SS students must have a department.",
                )

        return cleaned

    def save(self, commit=True):

        user = super().save(commit=False)

        user.role = User.Role.STUDENT

        jss_classes = [
            User.StudentClass.JSS1,
            User.StudentClass.JSS2,
            User.StudentClass.JSS3,
        ]

        if user.student_class in jss_classes:

            user.department = User.Department.GENERAL

        if commit:
            user.save()

        return user


# =========================================================
# TEACHER - STUDENT CREATION
# =========================================================

class TeacherStudentCreationForm(forms.ModelForm):
    """
    Form used by teachers to create student accounts.

    The student's PIN is stored through Django's password hashing
    system. The raw PIN is never stored in the database.
    """

    pin = forms.CharField(
        label="Student PIN",
        min_length=3,
        max_length=10,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "autocomplete": "new-password",
                "placeholder": "Enter a 3–10 digit PIN",
            }
        ),
        help_text="Use 3–10 digits. The PIN is saved securely and will not change unless explicitly reset.",
    )

    pin_confirm = forms.CharField(
        label="Confirm PIN",
        min_length=3,
        max_length=10,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "inputmode": "numeric",
                "autocomplete": "new-password",
                "placeholder": "Re-enter the PIN",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "admission_number",
            "student_class",
            "department",
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "admission_number": forms.TextInput(attrs={"class": "form-control"}),
            "student_class": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned = super().clean()

        pin = cleaned.get("pin")
        pin_confirm = cleaned.get("pin_confirm")

        if pin and not pin.isdigit():
            self.add_error("pin", "PIN must contain digits only.")

        if pin and pin_confirm and pin != pin_confirm:
            self.add_error("pin_confirm", "The PINs do not match.")

        student_class = cleaned.get("student_class")
        department = cleaned.get("department")

        jss_classes = [
            User.StudentClass.JSS1,
            User.StudentClass.JSS2,
            User.StudentClass.JSS3,
        ]

        if student_class in jss_classes:
            cleaned["department"] = User.Department.GENERAL
        elif not department or department == User.Department.GENERAL:
            self.add_error(
                "department",
                "SS students must have a department.",
            )

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data["pin"])

        jss_classes = [
            User.StudentClass.JSS1,
            User.StudentClass.JSS2,
            User.StudentClass.JSS3,
        ]

        if user.student_class in jss_classes:
            user.department = User.Department.GENERAL

        if commit:
            user.save()

        return user


# =========================================================
# TEACHER - STUDENT EDIT
# =========================================================

class TeacherStudentEditForm(forms.ModelForm):
    """
    Form used by teachers to edit student accounts.
    """

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "admission_number",
            "student_class",
            "department",
            "is_active",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "admission_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "student_class": forms.Select(
                attrs={"class": "form-select"}
            ),
            "department": forms.Select(
                attrs={"class": "form-select"}
            ),
            "is_active": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }

    def clean(self):

        cleaned = super().clean()

        student_class = cleaned.get("student_class")
        department = cleaned.get("department")

        jss_classes = [
            User.StudentClass.JSS1,
            User.StudentClass.JSS2,
            User.StudentClass.JSS3,
        ]

        if student_class in jss_classes:

            cleaned["department"] = User.Department.GENERAL

        else:

            if (
                not department
                or department == User.Department.GENERAL
            ):

                self.add_error(
                    "department",
                    "SS students must have a department (Science, Commercial, or Arts).",
                )

        return cleaned


# =========================================================
# ADMIN PASSWORD RESET
# =========================================================

class AdminPasswordResetForm(forms.Form):

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        ),
    )

    def clean(self):

        cleaned = super().clean()

        if (
            cleaned.get("new_password1")
            != cleaned.get("new_password2")
        ):

            raise forms.ValidationError(
                "The two password fields didn't match."
            )

        return cleaned


# =========================================================
# STUDENT LOGIN
# =========================================================
#
# IMPORTANT:
#
# Login is intentionally:
#
#     CLASS
#     STUDENT NAME
#     PIN
#
# Department is NOT used here.
#
# Department is already stored on the student's account
# and is used later when deciding which exams they can see.
#
# =========================================================

class StudentLoginForm(forms.Form):

    student_class = forms.ChoiceField(
        label="Class",

        choices=[
            ("", "---------")
        ] + list(
            User.StudentClass.choices
        ),

        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_student_class",
            }
        ),
    )

    student = forms.ModelChoiceField(
        label="Student Name",

        queryset=User.objects.none(),

        empty_label="---------",

        widget=forms.Select(
            attrs={
                "class": "form-select",
                "id": "id_student",
            }
        ),
    )

    pin = forms.CharField(
        label="PIN",

        max_length=10,

        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your PIN",
            }
        ),
    )

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        student_class = self.data.get(
            "student_class"
        )

        if student_class:

            self.fields[
                "student"
            ].queryset = (
                User.objects
                .filter(
                    role=User.Role.STUDENT,
                    student_class=student_class,
                    is_active=True,
                )
                .order_by(
                    "first_name",
                    "last_name",
                    "username",
                )
            )

    def clean(self):

        cleaned = super().clean()

        student = cleaned.get(
            "student"
        )

        pin = cleaned.get(
            "pin"
        )

        if not student:

            return cleaned

        if not pin:

            return cleaned

        user = authenticate(
            username=student.username,
            password=pin,
        )

        if user is None:

            raise forms.ValidationError(
                "Incorrect PIN."
            )

        if not user.is_student:

            raise forms.ValidationError(
                "This account is not a student account."
            )

        if not user.is_active:

            raise forms.ValidationError(
                "This student account is inactive."
            )

        cleaned["user"] = user

        return cleaned


# =========================================================
# TEACHER LOGIN
# =========================================================

class TeacherLoginForm(forms.Form):

    teacher = forms.ModelChoiceField(
        label="Teacher Name",

        queryset=(
            User.objects
            .filter(
                role=User.Role.TEACHER,
                is_active=True,
            )
            .order_by(
                "first_name",
                "last_name",
                "username",
            )
        ),

        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    pin = forms.CharField(
        label="PIN",

        max_length=10,

        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your PIN",
            }
        ),
    )

    def clean(self):

        cleaned = super().clean()

        teacher = cleaned.get(
            "teacher"
        )

        pin = cleaned.get(
            "pin"
        )

        if teacher and pin:

            user = authenticate(
                username=teacher.username,
                password=pin,
            )

            if user is None:

                raise forms.ValidationError(
                    "Incorrect PIN."
                )

            if not user.is_teacher:

                raise forms.ValidationError(
                    "This account is not a teacher account."
                )

            if not user.is_active:

                raise forms.ValidationError(
                    "This teacher account is inactive."
                )

            cleaned["user"] = user

        return cleaned