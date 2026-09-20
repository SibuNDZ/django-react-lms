import React from "react";

/**
 * Catches render errors below it and shows a recoverable message instead of
 * a blank page. Errors are logged to the console for diagnosis.
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("Unhandled render error", error, info?.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="container py-5 text-center">
        <h2 className="mb-3">Something went wrong on this page</h2>
        <p className="text-muted mb-4">
          The rest of the site is still available. Reloading usually fixes it.
        </p>
        <button type="button" className="btn btn-primary me-2" onClick={() => window.location.reload()}>
          Reload page
        </button>
        <a href="/" className="btn btn-outline-secondary">
          Go to home
        </a>
      </div>
    );
  }
}

export default ErrorBoundary;
