from django.utils import timezone

from .models import ExamAttempt, StudentAnswer


def finalize_attempt(attempt: ExamAttempt, submitted_choice_ids: dict):
    """
    Save the student's answers, calculate the score, and submit the attempt.

    submitted_choice_ids:
        {
            question_id: choice_id,
            ...
        }

    This function is the single source of truth for scoring.
    """

    # Prevent double submission/scoring
    if attempt.status == ExamAttempt.Status.SUBMITTED:
        return attempt

    total_score = 0

    questions = (
        attempt.exam.questions
        .prefetch_related("choices")
        .all()
    )

    for question in questions:
        choice_id = submitted_choice_ids.get(question.id)

        selected_choice = None

        if choice_id:
            try:
                choice_id = int(choice_id)
            except (TypeError, ValueError):
                choice_id = None

        if choice_id:
            selected_choice = next(
                (
                    choice
                    for choice in question.choices.all()
                    if choice.id == choice_id
                ),
                None,
            )

        StudentAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "selected_choice": selected_choice,
            },
        )

        if selected_choice and selected_choice.is_correct:
            total_score += question.marks

    attempt.score = total_score
    attempt.status = ExamAttempt.Status.SUBMITTED
    attempt.submitted_at = timezone.now()
    attempt.save(
        update_fields=[
            "score",
            "status",
            "submitted_at",
        ]
    )

    return attempt