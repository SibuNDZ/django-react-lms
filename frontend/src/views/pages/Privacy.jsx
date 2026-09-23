import React from "react";
import { Link } from "react-router-dom";
import PageLayout from "./PageLayout";

function Privacy() {
  return (
    <PageLayout
      title="Privacy notice"
      intro="How DSN Research collects, uses and protects your personal information under the Protection of Personal Information Act."
      updated="23 September 2026 (version 1.0)"
    >
      <h3>1. Responsible party</h3>
      <p>
        DSN Research Consulting (Pty) Ltd, registration 2015/191048/07, 25 Strangers Way,
        Dorchester Heights, East London, is the responsible party. The Information Officer is
        the Managing Director, Sibusiso Ndzukuma. Contact:{" "}
        <a href="mailto:privacy@dsnresearch.com">privacy@dsnresearch.com</a> or +27 66 296 3239.
      </p>

      <h3>2. What we collect</h3>
      <ul>
        <li><strong>Account and profile:</strong> name, email address, password (stored hashed), country, profile photo and bio if you add them.</li>
        <li><strong>Learning records:</strong> enrolments, lesson progress and time spent, quiz attempts with timestamps and scores, practical submissions (files, links and text), grades, feedback and outcomes, your notes and discussion posts.</li>
        <li><strong>Accreditation and reporting data:</strong> where required by a quality partner or funder, identity number, date of birth, gender, population group, disability status and home language. We collect these only when needed for a specific programme and tell you why.</li>
        <li><strong>Support and accommodation information:</strong> what you tell us when you ask for support or a reasonable accommodation, including health information you choose to share.</li>
        <li><strong>Technical data:</strong> login events, IP address and browser type in server logs, kept for 90 days.</li>
      </ul>

      <h3>3. Why we use it</h3>
      <ul>
        <li>To run your programme: teaching, assessment, moderation, feedback and certification.</li>
        <li>To support you and to apply reasonable accommodations you have requested.</li>
        <li>To meet our obligations to accreditation bodies and funders, including learner record submissions to the National Learner Records Database where a programme requires it.</li>
        <li>To keep the platform secure and to investigate misuse.</li>
        <li>To improve programmes, using aggregated and de-identified data.</li>
      </ul>
      <p>
        We do not sell personal information and we do not use it for marketing without your
        separate consent, which you can withdraw at any time.
      </p>

      <h3>4. Legal basis</h3>
      <p>
        Processing is necessary to perform our agreement with you (the{" "}
        <Link to="/terms/">Terms of use</Link>), to comply with legal obligations, and in some
        cases on your consent, which we record at registration and which you can withdraw.
        Special personal information (health, disability, population group) is processed only
        with your explicit consent or where the law requires it, and is restricted to staff who
        need it.
      </p>

      <h3>5. Who we share it with</h3>
      <ul>
        <li>Instructors, assessors and moderators assigned to your programme.</li>
        <li>Service providers that operate the platform on our behalf under written contracts: cloud hosting and database (Railway), object storage for uploaded files, email delivery (Resend), and payment processors where fees apply (Stripe, PayPal). Some of these providers store data outside South Africa; we only use providers whose contracts require protection equivalent to POPIA.</li>
        <li>Accreditation bodies, quality partners and funders where a programme requires reporting, and workplace hosts for placements.</li>
        <li>Authorities where the law requires it.</li>
      </ul>

      <h3>6. How long we keep it</h3>
      <ul>
        <li>Account and enrolment records: five years after you leave.</li>
        <li>Assessment evidence, grades and moderation records: five years after certification or exit.</li>
        <li>Certificate register: permanently, so certificates can be verified.</li>
        <li>Support and complaint records: five years after closure.</li>
        <li>Server logs: 90 days.</li>
      </ul>

      <h3>7. Security</h3>
      <p>
        Data is encrypted in transit, uploaded files are private and served through short-lived
        signed links, access is role based and reviewed, and administrative accounts use strong
        authentication. If a security compromise affects your information we will notify you and
        the Information Regulator as required by POPIA.
      </p>

      <h3>8. Your rights</h3>
      <p>
        You may ask what personal information we hold about you, ask us to correct or delete it,
        object to processing, and withdraw consent. Write to{" "}
        <a href="mailto:privacy@dsnresearch.com">privacy@dsnresearch.com</a>. We verify your
        identity and respond within 30 days. You may also complain to the Information Regulator
        of South Africa (<a href="https://inforegulator.org.za" target="_blank" rel="noreferrer">inforegulator.org.za</a>).
      </p>

      <h3 id="cookies">9. Cookies</h3>
      <p>
        The platform uses strictly necessary cookies to keep you signed in and to remember your
        cart. We do not use advertising or tracking cookies. You can clear cookies in your
        browser at any time; you will then need to sign in again.
      </p>

      <h3>10. Changes</h3>
      <p>
        We will update this notice when our processing changes. The version and date at the top
        of the page change when we do, and material changes are emailed to account holders.
      </p>
    </PageLayout>
  );
}

export default Privacy;
