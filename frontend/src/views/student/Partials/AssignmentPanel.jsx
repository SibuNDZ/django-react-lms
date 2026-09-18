import React, { useEffect, useState } from "react";
import useAxios from "../../../utils/useAxios";
import Toast from "../../plugin/Toast";

const outcomeBadge = (outcome, status) => {
  if (outcome === "competent") return <span className="badge bg-success">Competent</span>;
  if (outcome === "not_yet_competent")
    return <span className="badge bg-warning text-dark">Not yet competent</span>;
  return (
    <span className="badge bg-secondary">
      {status === "graded" ? "Graded" : "Awaiting grading"}
    </span>
  );
};

/**
 * View a lesson's assignment, hand in work, and see grades and feedback.
 * Grading is done by the instructor; passing completes the lesson.
 */
function AssignmentPanel({ enrollmentId, lessonId, onChange }) {
  const base = `student/enrollments/${enrollmentId}/lessons/${lessonId}/assignment/`;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [form, setForm] = useState({ text_answer: "", link: "", file: null });

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await useAxios().get(base);
      setData(res.data);
    } catch (err) {
      setError(err?.response?.data?.message || "This assignment is not available yet.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setForm({ text_answer: "", link: "", file: null });
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enrollmentId, lessonId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.file && !form.text_answer.trim() && !form.link.trim()) {
      Toast().fire({ icon: "warning", title: "Add a file, a written answer, or a link" });
      return;
    }
    setBusy(true);
    try {
      const body = new FormData();
      if (form.file) body.append("file", form.file);
      if (form.text_answer.trim()) body.append("text_answer", form.text_answer.trim());
      if (form.link.trim()) body.append("link", form.link.trim());
      await useAxios().post(`${base}submissions/`, body, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      Toast().fire({ icon: "success", title: "Assignment submitted" });
      setForm({ text_answer: "", link: "", file: null });
      await load();
      onChange?.();
    } catch (err) {
      const detail = err?.response?.data;
      const message =
        detail?.message ||
        detail?.file?.[0] ||
        detail?.non_field_errors?.[0] ||
        "Could not submit the assignment";
      Toast().fire({ icon: "error", title: message });
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <p className="text-muted mb-0">Loading assignment…</p>;
  if (error) return <div className="alert alert-warning mb-0">{error}</div>;
  if (!data) return null;

  const { assignment, submissions, can_submit, passed } = data;
  const dueDate = assignment.due_date ? new Date(assignment.due_date) : null;
  const overdue = dueDate && dueDate < new Date();

  return (
    <div className="assignment-panel">
      <div className="d-flex flex-wrap justify-content-between align-items-start mb-2">
        <div>
          <h5 className="mb-1">{assignment.title}</h5>
          <small className="text-muted">
            Max score {assignment.max_score} · pass mark {assignment.pass_mark}%
            {dueDate && (
              <>
                {" "}
                · due {dueDate.toLocaleString()}
                {overdue && <span className="text-danger"> (past due)</span>}
              </>
            )}
          </small>
        </div>
        {passed && outcomeBadge("competent")}
      </div>

      <div className="card mb-3">
        <div className="card-body" style={{ whiteSpace: "pre-wrap" }}>
          {assignment.instructions}
        </div>
      </div>

      {submissions.length > 0 && (
        <div className="mb-3">
          <h6 className="mb-2">Your submissions</h6>
          {submissions.map((s) => (
            <div className="border rounded p-3 mb-2" key={s.submission_id}>
              <div className="d-flex justify-content-between align-items-center mb-1">
                <span>
                  <strong>Attempt {s.attempt_number}</strong>{" "}
                  <small className="text-muted">
                    {new Date(s.submitted_at).toLocaleString()}
                    {s.is_late && <span className="text-danger"> · late</span>}
                  </small>
                </span>
                <span>
                  {s.score !== null && s.score !== undefined && (
                    <span className="me-2">
                      {s.score} / {s.max_score}
                    </span>
                  )}
                  {outcomeBadge(s.outcome, s.status)}
                </span>
              </div>
              {s.file && (
                <div>
                  <a href={s.file} target="_blank" rel="noreferrer">
                    <i className="fas fa-paperclip me-1" />
                    {s.file_name}
                  </a>
                </div>
              )}
              {s.link && (
                <div>
                  <a href={s.link} target="_blank" rel="noreferrer">
                    <i className="fas fa-link me-1" />
                    {s.link}
                  </a>
                </div>
              )}
              {s.text_answer && (
                <p className="mb-1 mt-1" style={{ whiteSpace: "pre-wrap" }}>
                  {s.text_answer}
                </p>
              )}
              {s.feedback && (
                <div className="alert alert-light border mt-2 mb-0 py-2">
                  <strong>Feedback:</strong> {s.feedback}
                  {s.graded_by?.full_name && (
                    <small className="text-muted"> ({s.graded_by.full_name})</small>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {can_submit ? (
        <form onSubmit={handleSubmit}>
          <h6 className="mb-2">
            {submissions.length ? "Submit a revised version" : "Hand in your work"}
          </h6>
          <div className="mb-2">
            <label className="form-label" htmlFor={`file-${lessonId}`}>
              File
              {assignment.allowed_file_types && (
                <small className="text-muted"> ({assignment.allowed_file_types})</small>
              )}
            </label>
            <input
              id={`file-${lessonId}`}
              type="file"
              className="form-control"
              onChange={(e) => setForm({ ...form, file: e.target.files?.[0] || null })}
            />
          </div>
          <div className="mb-2">
            <label className="form-label" htmlFor={`link-${lessonId}`}>
              Link (repository, notebook, demo)
            </label>
            <input
              id={`link-${lessonId}`}
              type="url"
              className="form-control"
              placeholder="https://"
              value={form.link}
              onChange={(e) => setForm({ ...form, link: e.target.value })}
            />
          </div>
          <div className="mb-3">
            <label className="form-label" htmlFor={`text-${lessonId}`}>
              Written answer or notes
            </label>
            <textarea
              id={`text-${lessonId}`}
              className="form-control"
              rows={5}
              value={form.text_answer}
              onChange={(e) => setForm({ ...form, text_answer: e.target.value })}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={busy}>
            {busy ? "Submitting…" : "Submit assignment"}
          </button>
        </form>
      ) : (
        <p className="text-muted mb-0">
          {passed
            ? "This assignment has been marked competent."
            : "This assignment does not allow resubmission."}
        </p>
      )}
    </div>
  );
}

export default AssignmentPanel;
