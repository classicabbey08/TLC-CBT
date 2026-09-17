from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [

    # ==========================
    # Landing Page
    # ==========================

    path(
        "",
        views.home,
        name="home",
    ),


    # ==========================
    # Authentication
    # ==========================

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),

    path(
        "student-login/",
        views.student_login,
        name="student_login",
    ),

    path(
        "teacher-login/",
        views.teacher_login,
        name="teacher_login",
    ),

    path(
        "api/students-by-class/",
        views.students_by_class,
        name="students_by_class",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path(
        "dashboard/",
        views.dashboard_redirect,
        name="dashboard_redirect",
    ),


    # ==========================
    # Super Admin
    # ==========================

    path(
        "users/",
        views.user_list,
        name="user_list",
    ),

    path(
        "users/create-teacher/",
        views.create_teacher,
        name="create_teacher",
    ),

    path(
        "users/create-student/",
        views.create_student,
        name="create_student",
    ),

    path(
        "users/<int:user_id>/reset-password/",
        views.reset_password,
        name="reset_password",
    ),


    # ==========================
    # Teacher - Students
    # ==========================

    path(
        "teacher/students/",
        views.teacher_students,
        name="teacher_students",
    ),

    path(
        "teacher/students/add/",
        views.teacher_add_student,
        name="teacher_add_student",
    ),

    path(
        "teacher/students/<int:user_id>/edit/",
        views.teacher_edit_student,
        name="teacher_edit_student",
    ),

    path(
        "teacher/students/<int:user_id>/delete/",
        views.teacher_delete_student,
        name="teacher_delete_student",
    ),
]