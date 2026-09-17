from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from accounts.models import User
from exams.models import Exam

from .models import ExamAttempt
from .utils import finalize_attempt


# =========================================================
# HELPERS
# =========================================================

def student_can_take_exam(user, exam):
    """
    Check whether a student belongs to the class/department
    targeted by the exam.

    Department applies ONLY to SS students.

    JSS students:
        - Must match the target class.
        - Must use GENERAL department.

    SS students:
        - Must match the target class.
        - Must match the exam department.
    """

    # -----------------------------------------------------
    # CLASS MUST ALWAYS MATCH
    # -----------------------------------------------------

    if exam.target_class != user.student_class:
        return False

    # -----------------------------------------------------
    # DEPARTMENT ONLY APPLIES TO SS STUDENTS
    # -----------------------------------------------------

    if user.student_class.startswith("JSS"):

        return (
            exam.department
            == User.Department.GENERAL
        )

    # -----------------------------------------------------
    # SS STUDENTS
    # -----------------------------------------------------

    return (
        exam.department
        == user.department
    )


# =========================================================
# STUDENT - AVAILABLE EXAMS
# =========================================================

@role_required("STUDENT")
def available_exams(request):
    """
    Show only active exams available to the logged-in student.

    JSS:
        Class must match.
        Department must be GENERAL.

    SS:
        Class must match.
        Department must match the student's department.
    """

    user = request.user

    # -----------------------------------------------------
    # START WITH ACTIVE EXAMS FOR STUDENT'S CLASS
    # -----------------------------------------------------

    exams = (
        Exam.objects
        .filter(
            is_active=True,
            target_class=user.student_class,
        )
        .select_related(
            "subject",
            "created_by",
        )
    )

    # -----------------------------------------------------
    # JSS STUDENTS
    # -----------------------------------------------------

    if user.student_class.startswith("JSS"):

        exams = exams.filter(
            department=User.Department.GENERAL
        )

    # -----------------------------------------------------
    # SS STUDENTS
    # -----------------------------------------------------

    else:

        exams = exams.filter(
            department=user.department
        )

    # -----------------------------------------------------
    # NEWEST EXAMS FIRST
    # -----------------------------------------------------

    exams = exams.order_by(
        "-created_at"
    )

    # -----------------------------------------------------
    # FIND THIS STUDENT'S EXISTING ATTEMPTS
    # -----------------------------------------------------

    my_attempts = {
        attempt.exam_id: attempt
        for attempt in ExamAttempt.objects.filter(
            student=user
        )
    }

    # -----------------------------------------------------
    # BUILD EXAM ROWS
    # -----------------------------------------------------

    exam_rows = []

    for exam in exams:

        exam_rows.append(
            {
                "exam": exam,
                "attempt": my_attempts.get(
                    exam.id
                ),
            }
        )

    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render(
        request,
        "attempts/available_exams.html",
        {
            "exam_rows": exam_rows,
        },
    )


# =========================================================
# STUDENT - START EXAM
# =========================================================

@role_required("STUDENT")
def start_exam(request, exam_id):
    """
    Start an exam only if the student is eligible.
    """

    exam = get_object_or_404(
        Exam,
        id=exam_id,
        is_active=True,
    )

    # -----------------------------------------------------
    # CHECK ELIGIBILITY
    # -----------------------------------------------------

    if not student_can_take_exam(
        request.user,
        exam,
    ):

        messages.error(
            request,
            "You are not eligible to take this exam.",
        )

        return redirect(
            "attempts:available_exams"
        )

    # -----------------------------------------------------
    # GET OR CREATE ATTEMPT
    # -----------------------------------------------------

    attempt, created = (
        ExamAttempt.objects.get_or_create(
            student=request.user,
            exam=exam,
        )
    )

    # -----------------------------------------------------
    # ALREADY SUBMITTED
    # -----------------------------------------------------

    if (
        attempt.status
        == ExamAttempt.Status.SUBMITTED
    ):

        return redirect(
            "attempts:result_detail",
            attempt_id=attempt.id,
        )

    # -----------------------------------------------------
    # EXISTING UNFINISHED ATTEMPT
    # -----------------------------------------------------

    return redirect(
        "attempts:take_exam",
        attempt_id=attempt.id,
    )


# =========================================================
# STUDENT - TAKE EXAM
# =========================================================

@role_required("STUDENT")
def take_exam(request, attempt_id):
    """
    Display an active exam attempt.
    """

    attempt = get_object_or_404(
        ExamAttempt.objects.select_related(
            "exam",
            "exam__subject",
        ),
        id=attempt_id,
        student=request.user,
    )

    # -----------------------------------------------------
    # ALREADY SUBMITTED
    # -----------------------------------------------------

    if (
        attempt.status
        == ExamAttempt.Status.SUBMITTED
    ):

        return redirect(
            "attempts:result_detail",
            attempt_id=attempt.id,
        )

    # -----------------------------------------------------
    # SERVER-SIDE TIMEOUT CHECK
    # -----------------------------------------------------

    if attempt.is_expired:

        finalize_attempt(
            attempt,
            submitted_choice_ids={},
        )

        messages.warning(
            request,
            "Time is up. Your exam has been submitted automatically.",
        )

        return redirect(
            "attempts:result_detail",
            attempt_id=attempt.id,
        )

    # -----------------------------------------------------
    # LOAD QUESTIONS
    # -----------------------------------------------------

    questions = (
        attempt.exam.questions
        .prefetch_related(
            "choices"
        )
        .all()
    )

    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render(
        request,
        "attempts/take_exam.html",
        {
            "attempt": attempt,
            "exam": attempt.exam,
            "questions": questions,
            "seconds_remaining":
                attempt.seconds_remaining,
        },
    )


# =========================================================
# STUDENT - SUBMIT EXAM
# =========================================================

@role_required("STUDENT")
def submit_exam(request, attempt_id):
    """
    Submit and score an exam attempt.
    """

    attempt = get_object_or_404(
        ExamAttempt,
        id=attempt_id,
        student=request.user,
    )

    # -----------------------------------------------------
    # ONLY POST IS ALLOWED
    # -----------------------------------------------------

    if request.method != "POST":

        return redirect(
            "attempts:take_exam",
            attempt_id=attempt.id,
        )

    # -----------------------------------------------------
    # ALREADY SUBMITTED
    # -----------------------------------------------------

    if (
        attempt.status
        == ExamAttempt.Status.SUBMITTED
    ):

        return redirect(
            "attempts:result_detail",
            attempt_id=attempt.id,
        )

    # -----------------------------------------------------
    # COLLECT ANSWERS
    # -----------------------------------------------------

    submitted_choice_ids = {}

    for question in attempt.exam.questions.all():

        choice_id = request.POST.get(
            f"question_{question.id}"
        )

        if choice_id:

            submitted_choice_ids[
                question.id
            ] = choice_id

    # -----------------------------------------------------
    # CHECK SERVER TIMER
    # -----------------------------------------------------

    expired = attempt.is_expired

    if expired:

        messages.warning(
            request,
            "The exam time has expired. Your exam has been submitted.",
        )

    # -----------------------------------------------------
    # FINALIZE ATTEMPT
    # -----------------------------------------------------

    finalize_attempt(
        attempt,
        submitted_choice_ids,
    )

    # -----------------------------------------------------
    # NORMAL SUBMISSION MESSAGE
    # -----------------------------------------------------

    if not expired:

        messages.success(
            request,
            "Exam submitted successfully.",
        )

    # -----------------------------------------------------
    # SHOW RESULT
    # -----------------------------------------------------

    return redirect(
        "attempts:result_detail",
        attempt_id=attempt.id,
    )


# =========================================================
# STUDENT - RESULT DETAIL
# =========================================================

@role_required("STUDENT")
def result_detail(request, attempt_id):
    """
    Student submission confirmation only.

    IMPORTANT: Students must never see scores, percentages, answers,
    result breakdowns, or report/certificate download links.
    """

    attempt = get_object_or_404(
        ExamAttempt.objects.select_related(
            "exam",
            "exam__subject",
        ),
        id=attempt_id,
        student=request.user,
    )

    # -----------------------------------------------------
    # NOT SUBMITTED YET
    # -----------------------------------------------------

    if (
        attempt.status
        != ExamAttempt.Status.SUBMITTED
    ):

        return redirect(
            "attempts:take_exam",
            attempt_id=attempt.id,
        )

    # -----------------------------------------------------
    # SHOW RESULT CONFIRMATION
    # -----------------------------------------------------

    return render(
        request,
        "attempts/result_detail.html",
        {
            "attempt": attempt,
        },
    )


# =========================================================
# CERTIFICATE HELPERS
# =========================================================

def _get_certificate_attempt(request, attempt_id):
    """
    Return a submitted attempt the current user is allowed to view.

    Students: NEVER allowed to view/download reports.
    Teachers: only reports for exams they created.
    Super Admin: any submitted report.
    """

    attempt = get_object_or_404(
        ExamAttempt.objects.select_related(
            "student",
            "exam",
            "exam__subject",
        ),
        id=attempt_id,
        status=ExamAttempt.Status.SUBMITTED,
    )

    user = request.user

    # Students are intentionally blocked from reports/certificates.
    if user.is_student:
        messages.error(
            request,
            "Weekly progress reports are available through your school/teacher.",
        )
        return None

    if user.is_teacher and attempt.exam.created_by_id == user.id:
        return attempt

    if user.is_super_admin:
        return attempt

    messages.error(
        request,
        "You do not have permission to view this weekly progress report.",
    )
    return None


def _certificate_context(attempt):
    student = attempt.student

    percentage = (
        round((attempt.score / attempt.total_marks) * 100, 1)
        if attempt.total_marks
        else 0
    )

    if percentage >= 75:
        grade, remark = "A", "Excellent"
    elif percentage >= 65:
        grade, remark = "B", "Very Good"
    elif percentage >= 55:
        grade, remark = "C", "Good"
    elif percentage >= 45:
        grade, remark = "D", "Pass"
    elif percentage >= 40:
        grade, remark = "E", "Fair"
    else:
        grade, remark = "F", "Fail"

    return {
        "attempt": attempt,
        "student": student,
        "percentage": percentage,
        "grade": grade,
        "remark": remark,
        "is_jss": str(student.student_class or "").startswith("JSS"),
        "is_sss": str(student.student_class or "").startswith("SSS"),
        "certificate_number": f"TLC-{attempt.id:06d}",
    }


# =========================================================
# CERTIFICATE - PRINTABLE PAGE
# =========================================================

@login_required
def student_certificate(request, attempt_id):
    """
    Display a printable certificate for an authorized submitted attempt.
    """

    attempt = _get_certificate_attempt(request, attempt_id)

    if attempt is None:
        return redirect("accounts:dashboard_redirect")

    return render(
        request,
        "attempts/student_certificate.html",
        _certificate_context(attempt),
    )


# =========================================================
# CERTIFICATE - PDF DOWNLOAD
# =========================================================

@login_required
def student_certificate_pdf(request, attempt_id):
    """
    Generate and download a PDF certificate using the existing xhtml2pdf
    dependency. No new package is required.
    """

    attempt = _get_certificate_attempt(request, attempt_id)

    if attempt is None:
        return redirect("accounts:dashboard_redirect")

    context = _certificate_context(attempt)

    html = render(
        request,
        "attempts/student_certificate_pdf.html",
        context,
    ).content.decode("utf-8")

    pdf = HttpResponse(content_type="application/pdf")
    filename = f"certificate-{attempt.student.username}-{attempt.id}.pdf"
    pdf["Content-Disposition"] = f'attachment; filename="{filename}"'

    result = pisa.CreatePDF(
        html,
        dest=pdf,
        encoding="utf-8",
    )

    if result.err:
        return HttpResponse(
            "Unable to generate the certificate PDF.",
            status=500,
            content_type="text/plain",
        )

    return pdf


# =========================================================
# TEACHER - RESULTS
# =========================================================

@role_required("TEACHER")
def teacher_results(request):
    """
    Teachers can only see submitted attempts belonging
    to exams they created.
    """

    attempts = (
        ExamAttempt.objects
        .filter(
            exam__created_by=request.user,
            status=ExamAttempt.Status.SUBMITTED,
        )
        .select_related(
            "student",
            "exam",
            "exam__subject",
        )
        .order_by(
            "-submitted_at"
        )
    )

    return render(
        request,
        "attempts/teacher_results.html",
        {
            "attempts": attempts,
        },
    )


# =========================================================
# TEACHER - RESULT DETAIL
# =========================================================

@role_required("TEACHER")
def teacher_result_detail(
    request,
    attempt_id,
):
    """
    Teacher views the full result of a student
    who took one of the teacher's exams.
    """

    attempt = get_object_or_404(
        ExamAttempt.objects.select_related(
            "student",
            "exam",
            "exam__subject",
        ),
        id=attempt_id,
        exam__created_by=request.user,
        status=ExamAttempt.Status.SUBMITTED,
    )

    answers = (
        attempt.answers
        .select_related(
            "question",
            "selected_choice",
        )
        .prefetch_related(
            "question__choices",
        )
        .order_by(
            "question_id"
        )
    )

    return render(
        request,
        "attempts/teacher_result_detail.html",
        {
            "attempt": attempt,
            "answers": answers,
        },
    )


# =========================================================
# SUPER ADMIN - RESULTS
# =========================================================

@role_required("SUPER_ADMIN")
def admin_results(request):
    """
    Super Admin sees every submitted exam attempt.
    """

    attempts = (
        ExamAttempt.objects
        .filter(
            status=ExamAttempt.Status.SUBMITTED,
        )
        .select_related(
            "student",
            "exam",
            "exam__subject",
            "exam__created_by",
        )
        .order_by(
            "-submitted_at"
        )
    )

    return render(
        request,
        "attempts/admin_results.html",
        {
            "attempts": attempts,
        },
    )


# =========================================================
# SUPER ADMIN - RESULT DETAIL
# =========================================================

@role_required("SUPER_ADMIN")
def admin_result_detail(
    request,
    attempt_id,
):
    """
    Super Admin can inspect any submitted result.
    """

    attempt = get_object_or_404(
        ExamAttempt.objects.select_related(
            "student",
            "exam",
            "exam__subject",
            "exam__created_by",
        ),
        id=attempt_id,
        status=ExamAttempt.Status.SUBMITTED,
    )

    answers = (
        attempt.answers
        .select_related(
            "question",
            "selected_choice",
        )
        .prefetch_related(
            "question__choices",
        )
        .order_by(
            "question_id"
        )
    )

    return render(
        request,
        "attempts/admin_result_detail.html",
        {
            "attempt": attempt,
            "answers": answers,
        },
    )