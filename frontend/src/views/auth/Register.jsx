import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

import apiInstance from "../../utils/axios";
import { register } from "../../utils/auth";
import Toast from "../plugin/Toast";

import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";

function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [role, setRole] = useState("student");
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useNavigate();

  // Password rules, checked live so the learner sees what is missing
  const rules = [
    { key: "length", label: "At least 10 characters", ok: password.length >= 10 },
    { key: "upper", label: "An uppercase letter", ok: /[A-Z]/.test(password) },
    { key: "lower", label: "A lowercase letter", ok: /[a-z]/.test(password) },
    { key: "digit", label: "A number", ok: /[0-9]/.test(password) },
    { key: "symbol", label: "A symbol (for example ! ? # @)", ok: /[^A-Za-z0-9]/.test(password) },
  ];
  const passed = rules.filter((r) => r.ok).length;
  const strength = password.length === 0 ? 0 : passed <= 2 ? 1 : passed <= 4 ? 2 : 3;
  const strengthLabel = ["", "Weak", "Fair", "Strong"][strength];
  const strengthClass = ["", "bg-danger", "bg-warning", "bg-success"][strength];
  const passwordsMatch = password2.length > 0 && password === password2;
  const canSubmit = passed === rules.length && passwordsMatch && fullName.trim() && email.trim() && !isLoading;
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    setIsLoading(true);

    const { error } = await register(fullName, email, password, password2, role);
    if (error) {
      Toast().fire({ icon: "error", title: error });
      setIsLoading(false);
      return;
    }
    Toast().fire({ icon: "success", title: "Welcome! Your account is ready." });
    navigate(role === "instructor" ? "/instructor/dashboard/" : "/student/dashboard/");
  };

  return (
    <>
      <BaseHeader />

      <section
        className="container d-flex flex-column vh-100"
        style={{ marginTop: "150px" }}
      >
        <div className="row align-items-center justify-content-center g-0 h-lg-100 py-8">
          <div className="col-lg-5 col-md-8 py-8 py-xl-0">
            <div className="card shadow">
              <div className="card-body p-6">
                <div className="mb-4">
                  <h1 className="mb-1 fw-bold">Sign up</h1>
                  <span>
                    Already have an account?
                    <Link to="/login/" className="ms-1">
                      Sign In
                    </Link>
                  </span>
                </div>
                {/* Form */}
                <form
                  className="needs-validation"
                  noValidate=""
                  onSubmit={handleSubmit}
                >
                  {/* Username */}
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">
                      Full Name
                    </label>
                    <input
                      type="text"
                      id="full_name"
                      className="form-control"
                      name="full_name"
                      placeholder="John Doe"
                      required=""
                      onChange={(e) => setFullName(e.target.value)}
                    />
                  </div>
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      className="form-control"
                      name="email"
                      placeholder="johndoe@dsnresearch.co.za"
                      required=""
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>

                  {/* Password */}
                  <div className="mb-2">
                    <label htmlFor="password" className="form-label">
                      Password
                    </label>
                    <div className="input-group">
                      <input
                        type={showPassword ? "text" : "password"}
                        id="password"
                        className="form-control"
                        name="password"
                        placeholder="Choose a strong password"
                        autoComplete="new-password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                      />
                      <button
                        type="button"
                        className="btn btn-outline-secondary"
                        onClick={() => setShowPassword((v) => !v)}
                        aria-label={showPassword ? "Hide password" : "Show password"}
                      >
                        <i className={`fas ${showPassword ? "fa-eye-slash" : "fa-eye"}`} />
                      </button>
                    </div>
                    {password.length > 0 && (
                      <>
                        <div className="progress mt-2" style={{ height: "6px" }}>
                          <div
                            className={`progress-bar ${strengthClass}`}
                            role="progressbar"
                            style={{ width: `${(strength / 3) * 100}%` }}
                            aria-valuenow={strength}
                            aria-valuemin={0}
                            aria-valuemax={3}
                          />
                        </div>
                        <small className="text-muted">Strength: {strengthLabel}</small>
                      </>
                    )}
                    <ul className="list-unstyled small mt-2 mb-0">
                      {rules.map((r) => (
                        <li key={r.key} className={r.ok ? "text-success" : "text-muted"}>
                          <i className={`fas ${r.ok ? "fa-check-circle" : "fa-circle"} me-2`} />
                          {r.label}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-3">
                    <label htmlFor="password2" className="form-label">
                      Confirm Password
                    </label>
                    <input
                      type={showPassword ? "text" : "password"}
                      id="password2"
                      className={`form-control ${password2.length > 0 ? (passwordsMatch ? "is-valid" : "is-invalid") : ""}`}
                      name="password2"
                      placeholder="Repeat your password"
                      autoComplete="new-password"
                      required
                      value={password2}
                      onChange={(e) => setPassword2(e.target.value)}
                    />
                    {password2.length > 0 && !passwordsMatch && (
                      <div className="invalid-feedback">Passwords do not match</div>
                    )}
                  </div>
                  <div className="mb-3 form-check">
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="instructorRole"
                      checked={role === "instructor"}
                      onChange={(e) => setRole(e.target.checked ? "instructor" : "student")}
                    />
                    <label className="form-check-label" htmlFor="instructorRole">
                      I want to teach on DSN LMS
                    </label>
                  </div>
                  <div>
                    <div className="d-grid">
                      {isLoading === true && (
                        <button
                          disabled
                          type="submit"
                          className="btn btn-primary"
                        >
                          Processing <i className="fas fa-spinner fa-spin"></i>
                        </button>
                      )}

                      {isLoading === false && (
                        <button type="submit" className="btn btn-primary" disabled={!canSubmit}>
                          Sign Up <i className="fas fa-user-plus"></i>
                        </button>
                      )}
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </section>

      <BaseFooter />
    </>
  );
}

export default Register;
