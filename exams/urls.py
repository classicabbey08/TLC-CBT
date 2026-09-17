from django.urls import path

from . import views


app_name = "exams"


urlpatterns = [

    # SUBJECTS
    path("subjects/", views.subject_list, name="subject_list"),
    path("subjects/create/", views.subject_create, name="subject_create"),

    # EXAMS
    path("exams/", views.exam_list, name="exam_list"),
    path("exams/create/", views.exam_create, name="exam_create"),
    path("exams/<int:exam_id>/edit/", views.exam_edit, name="exam_edit"),
    path("exams/<int:exam_id>/delete/", views.exam_delete, name="exam_delete"),

    # QUESTIONS
    path("exams/<int:exam_id>/questions/", views.question_list, name="question_list"),
    path("exams/<int:exam_id>/questions/create/", views.question_create, name="question_create"),
    path("exams/<int:exam_id>/questions/<int:question_id>/edit/", views.question_edit, name="question_edit"),
    path("exams/<int:exam_id>/questions/<int:question_id>/delete/", views.question_delete, name="question_delete"),
    path("exams/<int:exam_id>/questions/bulk-upload/", views.bulk_upload_questions, name="bulk_upload_questions"),
]