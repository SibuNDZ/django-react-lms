import React, { useEffect, useRef, useState } from "react";
import useAxios from "../../../utils/useAxios";
import Toast from "../../plugin/Toast";

const outcomeBadge = (outcome) => {
  if (outcome === "competent") return <span className="badge bg-success">Competent</span>;
  if (outcome === "not_yet_competent")
    return <span className="badge bg-warning text-dark">Not yet competent</span>;
  return <span className="badge bg-secondary">Pending</span>;
};

const formatSeconds = (total) => {
  const m = Math.floor(total / 60);
  const s = total % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
};

/**
 * Take a lesson's quiz: start an attempt, answer, submit, see the result.
 * Grading happens on the server; this component never sees the answer key.
 */
function QuizPlayer({ enrollmentId, lessonId, onCompleted }) {
  const base = `student/enrollments/${enrollmentId}/lessons/${lessonId}/quiz/`;

  const [status, setStatus] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(null);
  const submitRef = useRef(null);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await useAxios().get(base);
      setStatus(res.data);
      const open = (res.data.attempts || []).find((a) => a.status === "in_progress");
      if (open) setAttempt(open);
    } catch (err) {
      setError(err?.response?.data?.message || "This quiz is not available yet.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setAttempt(null);
    setAnswers({});
    setResult(null);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enrollmentId, lessonId]);

  // Countdown for timed quizzes; auto-submits when the clock runs out.
  useEffect(() => {
    if (!attempt?.expires_at) {
      setSecondsLeft(null);
      return undefined;
    }
    const tick = () => {
      const left = Math.max(0, Math.floor((new Date(attempt.expires_at) - Date.now()) / 1000));
      setSecondsLeft(left);
      if (left === 0 && submitRef.current) submitRef.current();
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [attempt]);

  const startAttempt = async () => {
    setBusy(true);
    try {
      const res = await useAxios().post(`${base}attempts/`);
      setAttempt(res.data);
      setAnswers({});
      setResult(null);
    } catch (err) {
      Toast().fire({
        icon: "error",
        title: err?.response?.data?.message || "Could not start the quiz",
      });
    } finally {
      setBusy(false);
    }
  };

  const toggleChoice = (question, choiceId) => {
    setAnswers((prev) => {
      const current = prev[question.question_id] || [];
      if (question.question_type === "multiple") {
        const next = current.includes(choiceId)
          ? current.filter((c) => c !== choiceId)
          : [...current, choiceId];
        return { ...prev, [question.question_id]: next };
      }
      return { ...prev, [question.question_id]: [choiceId] };
    });
  };

  const submitAttempt = async () => {
    if (!attempt || busy) return;
    setBusy(true);
    try {
      const res = await useAxios().post(`${base}attempts/${attempt.attempt_id}/submit/`, {
        answers,
      });
      setResult(res.data.attempt);
      setStatus(res.data);
      setAttempt(null);
      if (res.data.attempt.outcome === "competent") {
        Toast().fire({ icon: "success", title: "Quiz passed" });
        onCompleted?.();
      } else {
        Toast().fire({ icon: "info", title: "Quiz submitted" });
      }
    } catch (err) {
      Toast().fire({
        icon: "error",
        title: err?.response?.data?.message || "Could not submit the quiz",
      });
      // An expired attempt is closed server-side; reload to reflect it.
      if (err?.response?.data?.attempt) {
        setAttempt(null);
        load();
      }
    } finally {
      setBusy(false);
    }
  };
  submitRef.current = submitAttempt;

  if (loading) return <p className="text-muted mb-0">Loading quiz…</p>;
  if (error) return <div className="alert alert-warning mb-0">{error}</div>;
  if (!status) return null;

  const { quiz, attempts, attempts_remaining, best_percentage, passed } = status;
  const answeredCount = Object.values(answers).filter((v) => v.length > 0).length;

  return (
    <div className="quiz-player">
      <div className="d-flex flex-wrap justify-content-between align-items-start mb-3">
        <div>
          <h5 className="mb-1">{quiz.title}</h5>
          {quiz.description && <p className="text-muted mb-1">{quiz.description}</p>}
          <small className="text-muted">
            {quiz.total_questions} question{quiz.total_questions === 1 ? "" : "s"} ·{" "}
            {quiz.total_points} point{quiz.total_points === 1 ? "" : "s"} · pass mark {quiz.pass_mark}%
            {quiz.time_limit_minutes > 0 && ` · ${quiz.time_limit_minutes} min limit`}
          </small>
        </div>
        <div className="text-end">
          {passed && outcomeBadge("competent")}
          {best_percentage !== null && best_percentage !== undefined && (
            <div>
              <small className="text-muted">Best: {best_percentage}%</small>
            </div>
          )}
          <div>
            <small className="text-muted">
              Attempts: {attempts.length}
              {attempts_remaining !== null && ` / ${attempts.length + attempts_remaining}`}
            </small>
          </div>
        </div>
      </div>

      {attempt && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitAttempt();
          }}
        >
          {secondsLeft !== null && (
            <div className={`alert py-2 ${secondsLeft < 60 ? "alert-danger" : "alert-info"}`}>
              Time remaining: <strong>{formatSeconds(secondsLeft)}</strong>
            </div>
          )}
          {quiz.questions.map((q, index) => (
            <div className="card mb-3" key={q.question_id}>
              <div className="card-body">
                <p className="fw-semibold mb-1">
                  {index + 1}. {q.text}
                </p>
                <small className="text-muted d-block mb-2">
                  {q.question_type === "multiple" ? "Select all that apply" : "Select one"} ·{" "}
                  {q.points} pt{q.points === 1 ? "" : "s"}
                </small>
                {q.choices.map((c) => {
                  const selected = (answers[q.question_id] || []).includes(c.choice_id);
                  const inputId = `${q.question_id}-${c.choice_id}`;
                  return (
                    <div className="form-check" key={c.choice_id}>
                      <input
                        className="form-check-input"
                        type={q.question_type === "multiple" ? "checkbox" : "radio"}
                        name={q.question_id}
                        id={inputId}
                        checked={selected}
                        onChange={() => toggleChoice(q, c.choice_id)}
                      />
                      <label className="form-check-label" htmlFor={inputId}>
                        {c.text}
                      </label>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
          <div className="d-flex justify-content-between align-items-center">
            <small className="text-muted">
              {answeredCount} of {quiz.questions.length} answered
            </small>
            <button type="submit" className="btn btn-primary" disabled={busy}>
              {busy ? "Submitting…" : "Submit answers"}
            </button>
          </div>
        </form>
      )}

      {!attempt && result && (
        <div className="mb-3">
          <div className="alert alert-light border d-flex justify-content-between align-items-center">
            <div>
              <strong>Score: {result.percentage}%</strong>{" "}
              <span className="text-muted">
                ({result.score} / {result.max_score} points)
              </span>
            </div>
            {outcomeBadge(result.outcome)}
          </div>
          <ul className="list-group mb-3">
            {quiz.questions.map((q, index) => {
              const r = result.answers?.[q.question_id];
              const chosen = (r?.selected || [])
                .map((id) => q.choices.find((c) => c.choice_id === id)?.text)
                .filter(Boolean);
              return (
                <li className="list-group-item" key={q.question_id}>
                  <div className="d-flex justify-content-between">
                    <span>
                      {index + 1}. {q.text}
                    </span>
                    <span className={`badge ${r?.correct ? "bg-success" : "bg-danger"}`}>
                      {r?.correct ? "Correct" : "Incorrect"}
                    </span>
                  </div>
                  <small className="text-muted">
                    Your answer: {chosen.length ? chosen.join(", ") : "none"}
                  </small>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {!attempt && (
        <div className="d-flex flex-wrap gap-2 align-items-center">
          {!passed && (attempts_remaining === null || attempts_remaining > 0) && (
            <button type="button" className="btn btn-primary" onClick={startAttempt} disabled={busy}>
              {attempts.length ? "Try again" : "Start quiz"}
            </button>
          )}
          {!passed && attempts_remaining === 0 && (
            <span className="text-danger">No attempts remaining.</span>
          )}
          {passed && !result && (
            <span className="text-success">You have passed this quiz.</span>
          )}
        </div>
      )}

      {!attempt && attempts.filter((a) => a.status === "submitted").length > 0 && (
        <div className="mt-3">
          <h6 className="mb-2">Previous attempts</h6>
          <table className="table table-sm mb-0">
            <thead>
              <tr>
                <th>#</th>
                <th>Submitted</th>
                <th>Score</th>
                <th>Outcome</th>
              </tr>
            </thead>
            <tbody>
              {attempts
                .filter((a) => a.status === "submitted")
                .map((a) => (
                  <tr key={a.attempt_id}>
                    <td>{a.attempt_number}</td>
                    <td>{a.submitted_at ? new Date(a.submitted_at).toLocaleString() : "-"}</td>
                    <td>{a.percentage}%</td>
                    <td>{outcomeBadge(a.outcome)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default QuizPlayer;
