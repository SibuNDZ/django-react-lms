import React from "react";
import { Link } from "react-router-dom";
import PageLayout from "./PageLayout";

function Contact() {
  return (
    <PageLayout title="Contact us" intro="We answer within one working day.">
      <div className="row g-4">
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body">
              <h4 className="card-title">Learner support</h4>
              <p className="text-muted">
                Platform access, technical problems, assessment questions and anything else
                about your programme.
              </p>
              <p className="mb-1">
                <i className="fas fa-envelope me-2 text-primary" />
                <a href="mailto:info@dsnresearch.com">info@dsnresearch.com</a>
              </p>
              <p className="mb-0">
                <i className="fas fa-phone me-2 text-primary" />
                <a href="tel:+27662963239">+27 66 296 3239</a>
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body">
              <h4 className="card-title">Complaints and appeals</h4>
              <p className="text-muted">
                Complaints are acknowledged within two working days and resolved within ten.
                Assessment appeals are decided within fifteen working days. See the{" "}
                <Link to="/help/">help centre</Link> for how both work.
              </p>
              <p className="mb-0">
                <i className="fas fa-envelope me-2 text-primary" />
                <a href="mailto:complaints@dsnresearch.com">complaints@dsnresearch.com</a>
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body">
              <h4 className="card-title">Privacy and your data</h4>
              <p className="text-muted">
                Requests to access, correct or delete your personal information go to the
                Information Officer and are answered within 30 days.
              </p>
              <p className="mb-0">
                <i className="fas fa-envelope me-2 text-primary" />
                <a href="mailto:privacy@dsnresearch.com">privacy@dsnresearch.com</a>
              </p>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card h-100">
            <div className="card-body">
              <h4 className="card-title">Office</h4>
              <p className="mb-1">DSN Research Consulting (Pty) Ltd</p>
              <p className="mb-1">25 Strangers Way, Dorchester Heights</p>
              <p className="mb-1">East London, 5241, South Africa</p>
              <p className="mb-0">
                <a href="https://www.dsnresearch.com" target="_blank" rel="noreferrer">
                  www.dsnresearch.com
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}

export default Contact;
