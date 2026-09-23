import React from "react";
import { Link } from "react-router-dom";
import PageLayout from "./PageLayout";

function Refunds() {
  return (
    <PageLayout
      title="Fees and refund policy"
      intro="Clear terms for programmes that carry a fee, in line with the Consumer Protection Act."
      updated="23 September 2026 (version 1.0)"
    >
      <div className="alert alert-info">
        Our current programmes are offered free of charge. This policy applies to any programme
        that carries a fee, as shown on its programme page before you enrol.
      </div>

      <h3>1. Fees</h3>
      <p>
        The fee for a programme, what it includes and any additional costs are published on the
        programme page and confirmed in your enrolment agreement before payment. Prices are in
        South African rand unless stated otherwise.
      </p>

      <h3>2. Cooling-off period</h3>
      <p>
        You may cancel within five working days of enrolling for a full refund of fees paid, less
        any bank charges.
      </p>

      <h3>3. Withdrawal</h3>
      <ul>
        <li>Before the programme start date: full refund less the published administration fee.</li>
        <li>Within the first two weeks of the programme: 75 percent refund.</li>
        <li>After the first two weeks: no refund, except on documented medical or compassionate grounds, which we consider individually.</li>
      </ul>

      <h3>4. If we cancel or change a programme</h3>
      <p>
        If DSN Research cancels a programme or materially changes its content, dates or delivery
        mode, you may choose a full refund or a transfer to an equivalent programme.
      </p>

      <h3>5. How refunds are paid</h3>
      <p>
        Approved refunds are paid to the original payment method within 15 working days.
        Certificates and statements of results are not withheld because of a fee dispute that is
        under a formal complaint.
      </p>

      <h3>6. Sponsored learners</h3>
      <p>
        Where an employer or funder pays your fee, refunds are paid to the sponsor under the terms
        of the sponsorship agreement.
      </p>

      <p className="mt-4">
        To request a refund, email <a href="mailto:info@dsnresearch.com">info@dsnresearch.com</a>{" "}
        with your name, programme and reason. Disputes follow our{" "}
        <Link to="/help/">complaints procedure</Link>.
      </p>
    </PageLayout>
  );
}

export default Refunds;
