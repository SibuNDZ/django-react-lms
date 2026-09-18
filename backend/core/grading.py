"""Server-side grading of quiz attempts."""

from decimal import Decimal

from django.utils import timezone


def grade_quiz_attempt(attempt, answers):
    """
    Grade an in-progress attempt against the quiz's answer key.

    ``answers`` maps question_id to a list of selected choice_ids. Raises
    ValueError for unknown question or choice ids, or for more than one
    selection on a single-answer question. Saves and returns the attempt.
    """
    questions = list(attempt.quiz.questions.prefetch_related('choices'))
    known = {q.question_id: q for q in questions}

    unknown = sorted(set(answers) - set(known))
    if unknown:
        raise ValueError(f"Unknown question ids: {', '.join(unknown)}")

    score = Decimal(0)
    max_score = Decimal(0)
    results = {}

    for question in questions:
        max_score += question.points
        choices = {c.choice_id: c for c in question.choices.all()}
        selected = list(dict.fromkeys(answers.get(question.question_id, [])))

        bad = [cid for cid in selected if cid not in choices]
        if bad:
            raise ValueError(
                f"Choice ids {', '.join(bad)} do not belong to question {question.question_id}"
            )
        if question.question_type != 'multiple' and len(selected) > 1:
            raise ValueError(f"Question {question.question_id} accepts a single answer")

        correct_ids = {cid for cid, c in choices.items() if c.is_correct}
        if question.question_type == 'multiple':
            is_correct = bool(selected) and set(selected) == correct_ids
        else:
            is_correct = len(selected) == 1 and selected[0] in correct_ids

        awarded = question.points if is_correct else 0
        score += awarded
        results[question.question_id] = {
            'selected': selected,
            'correct': is_correct,
            'points_awarded': awarded,
        }

    attempt.answers = results
    attempt.score = score
    attempt.max_score = max_score
    attempt.percentage = (
        (score / max_score * 100).quantize(Decimal('0.01')) if max_score else Decimal(0)
    )
    attempt.status = 'submitted'
    attempt.submitted_at = timezone.now()
    attempt.outcome = (
        'competent' if attempt.percentage >= attempt.quiz.pass_mark else 'not_yet_competent'
    )
    attempt.save()
    return attempt


def expire_quiz_attempt(attempt):
    """Close an attempt whose time limit has passed without a submission."""
    attempt.status = 'submitted'
    attempt.submitted_at = timezone.now()
    attempt.outcome = 'not_yet_competent'
    attempt.score = Decimal(0)
    attempt.max_score = Decimal(attempt.quiz.total_points)
    attempt.percentage = Decimal(0)
    attempt.save()
    return attempt
