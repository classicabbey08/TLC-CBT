from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User

from .forms import ChoiceFormSet, ExamForm, QuestionForm, SubjectForm
from .importer import import_questions_from_xlsx
from .models import Exam, Question, Subject


# =====================================================
# PERMISSIONS / HELPERS
# =====================================================

def _is_manager(user):
    return user.is_authenticated and (
        user.role == User.Role.TEACHER
        or user.role == User.Role.SUPER_ADMIN
    )


def _get_accessible_exam(request, exam_id):
    if request.user.role == User.Role.SUPER_ADMIN:
        return get_object_or_404(Exam, id=exam_id)
    return get_object_or_404(Exam, id=exam_id, created_by=request.user)


def _manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not _is_manager(request.user):
            messages.error(request, "You do not have permission to access this page.")
            return redirect("accounts:dashboard_redirect")
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


# =====================================================
# SUBJECTS
# =====================================================

@_manager_required
def subject_list(request):
    if request.user.role == User.Role.SUPER_ADMIN:
        subjects = Subject.objects.all().order_by("name")
    else:
        subjects = Subject.objects.filter(created_by=request.user).order_by("name")

    return render(request, "exams/subject_list.html", {"subjects": subjects})


@_manager_required
def subject_create(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.created_by = request.user
            subject.save()
            messages.success(request, f"Subject '{subject.name}' added.")
            return redirect("exams:subject_list")
    else:
        form = SubjectForm()

    return render(request, "exams/subject_form.html", {"form": form})


# =====================================================
# EXAMS
# =====================================================

@_manager_required
def exam_list(request):
    if request.user.role == User.Role.SUPER_ADMIN:
        exams = (
            Exam.objects.all()
            .select_related("subject", "created_by")
            .order_by("-created_at")
        )
    else:
        exams = (
            Exam.objects.filter(created_by=request.user)
            .select_related("subject")
            .order_by("-created_at")
        )

    return render(request, "exams/exam_list.html", {"exams": exams})


@_manager_required
def exam_create(request):
    if request.user.role == User.Role.SUPER_ADMIN:
        has_subjects = Subject.objects.exists()
    else:
        has_subjects = Subject.objects.filter(created_by=request.user).exists()

    if not has_subjects:
        messages.warning(request, "Add a subject first before creating an exam.")
        return redirect("exams:subject_create")

    if request.method == "POST":
        form = ExamForm(request.POST, teacher=request.user)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            messages.success(request, f"Exam '{exam.title}' created.")
            return redirect("exams:question_list", exam_id=exam.id)
    else:
        form = ExamForm(teacher=request.user)

    return render(request, "exams/exam_form.html", {"form": form})


@_manager_required
def exam_edit(request, exam_id):
    exam = _get_accessible_exam(request, exam_id)

    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Exam '{exam.title}' updated successfully.")
            return redirect("exams:exam_list")
    else:
        form = ExamForm(instance=exam, teacher=request.user)

    return render(request, "exams/exam_form.html", {
        "form": form,
        "editing": True,
        "exam": exam,
    })


@_manager_required
def exam_delete(request, exam_id):
    exam = _get_accessible_exam(request, exam_id)

    if request.method == "POST":
        title = exam.title
        exam.delete()
        messages.success(request, f"Exam '{title}' deleted successfully.")
        return redirect("exams:exam_list")

    return render(request, "exams/exam_confirm_delete.html", {"exam": exam})


# =====================================================
# QUESTIONS
# =====================================================

@_manager_required
def question_list(request, exam_id):
    exam = _get_accessible_exam(request, exam_id)
    questions = exam.questions.prefetch_related("choices")
    return render(request, "exams/question_list.html", {
        "exam": exam,
        "questions": questions,
    })


@_manager_required
def question_create(request, exam_id):
    exam = _get_accessible_exam(request, exam_id)

    if request.method == "POST":
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST, instance=Question(exam=exam))

        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            formset.instance = question
            formset.save()
            messages.success(request, "Question added.")
            return redirect("exams:question_list", exam_id=exam.id)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet(instance=Question())

    return render(request, "exams/question_form.html", {
        "form": form,
        "formset": formset,
        "exam": exam,
        "editing": False,
    })


@_manager_required
def question_edit(request, exam_id, question_id):
    exam = _get_accessible_exam(request, exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(request.POST, instance=question)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Question updated.")
            return redirect("exams:question_list", exam_id=exam.id)
    else:
        form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)

    return render(request, "exams/question_form.html", {
        "form": form,
        "formset": formset,
        "exam": exam,
        "editing": True,
    })


@_manager_required
def question_delete(request, exam_id, question_id):
    exam = _get_accessible_exam(request, exam_id)
    question = get_object_or_404(Question, id=question_id, exam=exam)

    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted.")
        return redirect("exams:question_list", exam_id=exam.id)

    return render(request, "exams/question_confirm_delete.html", {
        "exam": exam,
        "question": question,
    })


# =====================================================
# BULK QUESTION UPLOAD
# =====================================================

@_manager_required
def bulk_upload_questions(request, exam_id):
    exam = _get_accessible_exam(request, exam_id)

    if request.method == "POST":
        excel_file = request.FILES.get("excel_file")

        if not excel_file:
            messages.error(request, "Please select an Excel file.")
            return redirect("exams:bulk_upload_questions", exam_id=exam.id)

        if not excel_file.name.lower().endswith((".xlsx", ".xls")):
            messages.error(request, "Only .xlsx files are allowed.")
            return redirect("exams:bulk_upload_questions", exam_id=exam.id)

        result = import_questions_from_xlsx(exam, excel_file)

        if result["imported"]:
            messages.success(request, f"Successfully imported {result['imported']} question(s).")

        if result["skipped_duplicates"]:
            messages.info(request, f"Skipped {result['skipped_duplicates']} duplicate question(s).")

        for err in result["errors"][:10]:
            messages.warning(request, err)

        if len(result["errors"]) > 10:
            messages.warning(request, f"... and {len(result['errors']) - 10} more issue(s).")

        if not result["imported"] and not result["errors"] and not result["skipped_duplicates"]:
            messages.warning(request, "No valid questions found in the file.")

        return redirect("exams:question_list", exam_id=exam.id)

    return render(request, "exams/bulk_upload.html", {"exam": exam})