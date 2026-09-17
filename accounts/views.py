from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_GET

from .decorators import role_required

from .forms import (
    AdminPasswordResetForm,
    StudentCreationForm,
    TeacherCreationForm,
    StudentLoginForm,
    TeacherLoginForm,
    TeacherStudentCreationForm,
    TeacherStudentEditForm,
)

from .models import User


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard_redirect(request):

    if request.user.role == User.Role.SUPER_ADMIN:

        return render(
            request,
            "accounts/dashboard_placeholder.html",
            {
                "role": request.user.role,
            },
        )

    if request.user.role == User.Role.TEACHER:

        return render(
            request,
            "accounts/teacher_dashboard.html",
            {
                "teacher": request.user,
            },
        )

    if request.user.role == User.Role.STUDENT:

        # IMPORTANT:
        # Students go directly to the real exam page.
        return redirect(
            "attempts:available_exams"
        )

    return redirect(
        "accounts:home"
    )


# =========================================================
# SUPER ADMIN
# =========================================================

@role_required("SUPER_ADMIN")
def create_teacher(request):

    if request.method == "POST":

        form = TeacherCreationForm(
            request.POST
        )

        if form.is_valid():

            teacher = form.save()

            messages.success(
                request,
                (
                    f"Teacher account "
                    f"'{teacher.username}' "
                    f"created successfully."
                ),
            )

            return redirect(
                "accounts:user_list"
            )

    else:

        form = TeacherCreationForm()

    return render(
        request,
        "accounts/create_teacher.html",
        {
            "form": form,
        },
    )


@role_required("SUPER_ADMIN")
def create_student(request):

    if request.method == "POST":

        form = StudentCreationForm(
            request.POST
        )

        if form.is_valid():

            student = form.save()

            messages.success(
                request,
                (
                    f"Student account "
                    f"'{student.username}' "
                    f"created successfully."
                ),
            )

            return redirect(
                "accounts:user_list"
            )

    else:

        form = StudentCreationForm()

    return render(
        request,
        "accounts/create_student.html",
        {
            "form": form,
        },
    )


@role_required("SUPER_ADMIN")
def user_list(request):

    role_filter = request.GET.get(
        "role",
        "",
    )

    users = (
        User.objects
        .exclude(
            id=request.user.id
        )
        .order_by(
            "role",
            "username",
        )
    )

    if role_filter in {
        "TEACHER",
        "STUDENT",
    }:

        users = users.filter(
            role=role_filter
        )

    return render(
        request,
        "accounts/user_list.html",
        {
            "users": users,
            "role_filter": role_filter,
        },
    )


@role_required("SUPER_ADMIN")
def reset_password(
    request,
    user_id,
):

    target_user = get_object_or_404(
        User,
        id=user_id,
    )

    if request.method == "POST":

        form = AdminPasswordResetForm(
            request.POST
        )

        if form.is_valid():

            target_user.set_password(
                form.cleaned_data[
                    "new_password1"
                ]
            )

            target_user.save()

            messages.success(
                request,
                (
                    f"Password for "
                    f"'{target_user.username}' "
                    f"has been reset."
                ),
            )

            return redirect(
                "accounts:user_list"
            )

    else:

        form = AdminPasswordResetForm()

    return render(
        request,
        "accounts/reset_password.html",
        {
            "form": form,
            "target_user": target_user,
        },
    )


# =========================================================
# HOME
# =========================================================

def home(request):

    return render(
        request,
        "landing.html",
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

def student_login(request):

    if request.user.is_authenticated:

        logout(request)

    if request.method == "POST":

        form = StudentLoginForm(
            request.POST
        )

        if form.is_valid():

            user = form.cleaned_data[
                "user"
            ]

            login(
                request,
                user,
            )

            return redirect(
                "accounts:dashboard_redirect"
            )

    else:

        form = StudentLoginForm()

    return render(
        request,
        "accounts/student_login.html",
        {
            "form": form,
        },
    )


# =========================================================
# TEACHER LOGIN
# =========================================================

def teacher_login(request):

    if request.user.is_authenticated:

        logout(request)

    if request.method == "POST":

        form = TeacherLoginForm(
            request.POST
        )

        if form.is_valid():

            user = form.cleaned_data[
                "user"
            ]

            login(
                request,
                user,
            )

            return redirect(
                "accounts:dashboard_redirect"
            )

    else:

        form = TeacherLoginForm()

    return render(
        request,
        "accounts/teacher_login.html",
        {
            "form": form,
        },
    )


# =========================================================
# STUDENT AJAX
# =========================================================

@require_GET
def students_by_class(request):

    student_class = request.GET.get(
        "class",
        "",
    ).strip()

    if not student_class:

        return JsonResponse(
            [],
            safe=False,
        )

    students = (
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

    data = []

    for student in students:

        full_name = (
            f"{student.first_name} "
            f"{student.last_name}"
        ).strip()

        if not full_name:

            full_name = student.username

        data.append(
            {
                "id": student.id,
                "name": full_name,
                "admission_number":
                    student.admission_number or "",
                "department":
                    student.department or "",
            }
        )

    return JsonResponse(
        data,
        safe=False,
    )


# =========================================================
# TEACHER - STUDENTS
# =========================================================

@role_required("TEACHER")
def teacher_students(request):

    students = (
        User.objects
        .filter(
            role=User.Role.STUDENT,
        )
        .order_by(
            "student_class",
            "first_name",
            "last_name",
        )
    )

    return render(
        request,
        "accounts/teacher_students.html",
        {
            "students": students,
        },
    )


@role_required("TEACHER")
def teacher_add_student(request):

    if request.method == "POST":

        form = TeacherStudentCreationForm(
            request.POST
        )

        if form.is_valid():

            student = form.save()

            messages.success(
                request,
                (
                    f"Student "
                    f"'{student.username}' "
                    f"added successfully."
                ),
            )

            return redirect(
                "accounts:teacher_students"
            )

    else:

        form = TeacherStudentCreationForm()

    return render(
        request,
        "accounts/teacher_student_form.html",
        {
            "form": form,
            "editing": False,
        },
    )


@role_required("TEACHER")
def teacher_edit_student(
    request,
    user_id,
):

    student = get_object_or_404(
        User,
        id=user_id,
        role=User.Role.STUDENT,
    )

    if request.method == "POST":

        form = TeacherStudentEditForm(
            request.POST,
            instance=student,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                (
                    f"Student "
                    f"'{student.username}' "
                    f"updated successfully."
                ),
            )

            return redirect(
                "accounts:teacher_students"
            )

    else:

        form = TeacherStudentEditForm(
            instance=student
        )

    return render(
        request,
        "accounts/teacher_student_form.html",
        {
            "form": form,
            "student": student,
            "editing": True,
        },
    )


@role_required("TEACHER")
def teacher_delete_student(
    request,
    user_id,
):

    student = get_object_or_404(
        User,
        id=user_id,
        role=User.Role.STUDENT,
    )

    if request.method == "POST":

        username = student.username

        student.delete()

        messages.success(
            request,
            (
                f"Student "
                f"'{username}' "
                f"removed successfully."
            ),
        )

        return redirect(
            "accounts:teacher_students"
        )

    return render(
        request,
        "accounts/teacher_student_confirm_delete.html",
        {
            "student": student,
        },
    )