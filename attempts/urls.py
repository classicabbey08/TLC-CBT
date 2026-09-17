from django.urls import path

from . import views


app_name = "attempts"


urlpatterns = [

    # =====================================================
    # STUDENT
    # =====================================================

    path(
        "available/",
        views.available_exams,
        name="available_exams",
    ),

    path(
        "start/<int:exam_id>/",
        views.start_exam,
        name="start_exam",
    ),

    path(
        "take/<int:attempt_id>/",
        views.take_exam,
        name="take_exam",
    ),

    path(
        "submit/<int:attempt_id>/",
        views.submit_exam,
        name="submit_exam",
    ),

    path(
        "result/<int:attempt_id>/",
        views.result_detail,
        name="result_detail",
    ),

    path(
        "certificate/<int:attempt_id>/",
        views.student_certificate,
        name="student_certificate",
    ),

    path(
        "certificate/<int:attempt_id>/download/",
        views.student_certificate_pdf,
        name="student_certificate_pdf",
    ),


    # =====================================================
    # TEACHER
    # =====================================================

    path(
        "teacher/results/",
        views.teacher_results,
        name="teacher_results",
    ),

    path(
        "teacher/results/<int:attempt_id>/",
        views.teacher_result_detail,
        name="teacher_result_detail",
    ),


    # =====================================================
    # SUPER ADMIN
    # =====================================================

    path(
        "admin/results/",
        views.admin_results,
        name="admin_results",
    ),

    path(
        "admin/results/<int:attempt_id>/",
        views.admin_result_detail,
        name="admin_result_detail",
    ),
]