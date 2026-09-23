import React from "react";
import { Link } from "react-router-dom";
import PageLayout from "./PageLayout";

function Terms() {
  return (
    <PageLayout
      title="Terms of use"
      intro="The agreement between you and DSN Research Consulting (Pty) Ltd when you use this learning platform."
      updated="23 September 2026 (version 1.0)"
    >
      <h3>1. Who we are</h3>
      <p>
        This platform is operated by DSN Research Consulting (Pty) Ltd, registration number
        2015/191048/07, of 25 Strangers Way, Dorchester Heights, East London, South Africa
        ("DSN Research", "we"). By creating an account or enrolling in a programme you agree to
        these terms, to our <Link to="/privacy/">Privacy Notice</Link> and, where fees apply, to
        our <Link to="/refunds/">Fees and Refund Policy</Link>.
      </p>

      <h3>2. Your account</h3>
      <ul>
        <li>You must be at least 16 years old, or have a parent or guardian's consent, to hold an account.</li>
        <li>You must give accurate information and keep it up to date. Your name on the platform is the name that will appear on any certificate.</li>
        <li>Your login is personal. Do not share it, and tell us immediately if you think it has been compromised.</li>
      </ul>

      <h3>3. Enrolment and learning</h3>
      <ul>
        <li>Each programme page states its entry requirements, duration, assessment method and any fee before you enrol.</li>
        <li>Enrolment gives you access to the programme content for the programme duration plus six months, for your own personal learning.</li>
        <li>We may update content to keep it current. Material changes to assessment rules are communicated before they apply to you.</li>
        <li>We may withdraw or reschedule a programme. If we do, you may transfer to an equivalent programme or, where you paid a fee, receive a full refund.</li>
      </ul>

      <h3>4. Assessment and academic integrity</h3>
      <ul>
        <li>Work you submit must be your own. Sources and collaboration must be cited, and any use of generative AI tools must be declared.</li>
        <li>We run similarity checks and may ask you to explain your work in a viva before confirming an outcome.</li>
        <li>Knowledge checks are timed and limited to three attempts. Practicals allow one resubmission after feedback.</li>
        <li>You may appeal an assessment outcome within ten working days. The appeal is decided by people not involved in the original decision, within fifteen working days.</li>
        <li>Dishonesty in assessment is a disciplinary matter and may result in a not yet competent outcome, suspension or removal from the programme.</li>
      </ul>

      <h3>5. Certificates</h3>
      <p>
        A certificate is issued only when every module, including the capstone, has been assessed
        as competent and the results have been moderated. Until DSN Research holds accreditation
        as a Skills Development Provider, certificates are DSN Research certificates of completion
        and are not registered qualifications on the National Qualifications Framework.
      </p>

      <h3>6. Conduct</h3>
      <p>
        Treat staff, other learners and workplace hosts with respect. Harassment, discrimination,
        hate speech and misuse of the platform are prohibited and may lead to warnings, suspension
        or removal. You may report any concern to <a href="mailto:complaints@dsnresearch.com">complaints@dsnresearch.com</a>,
        and you will not be disadvantaged for doing so.
      </p>

      <h3>7. Intellectual property</h3>
      <p>
        Course content belongs to DSN Research or its licensors and is provided for your personal
        study. You may not copy, share, sell or publish it. You keep ownership of the work you
        submit for assessment; you give us a licence to store and assess it, to use it for
        moderation and quality assurance, and to show it to accreditation bodies when required.
      </p>

      <h3>8. Availability and liability</h3>
      <p>
        We aim to keep the platform available at all times but cannot guarantee uninterrupted
        access. Where an outage affects a deadline we will extend it. To the extent permitted by
        South African law, including the Consumer Protection Act, our liability to you is limited
        to the fees you paid for the affected programme.
      </p>

      <h3>9. Complaints and disputes</h3>
      <p>
        Complaints are handled under our complaints procedure: acknowledged within two working
        days and resolved within ten, with an escalation route to the Managing Director and, for
        accreditation matters, to the quality partner. These terms are governed by the laws of the
        Republic of South Africa.
      </p>

      <h3>10. Changes</h3>
      <p>
        We may update these terms. The version and date at the top of this page change when we
        do, and material changes are emailed to account holders before they take effect.
      </p>

      <p className="mt-4">
        Questions about these terms: <a href="mailto:info@dsnresearch.com">info@dsnresearch.com</a>.
      </p>
    </PageLayout>
  );
}

export default Terms;
