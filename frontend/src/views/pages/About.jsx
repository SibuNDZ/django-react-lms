import React from "react";
import { Link } from "react-router-dom";
import PageLayout from "./PageLayout";

function About() {
  return (
    <PageLayout
      title="About DSN Research"
      intro="Predictive analytics and agentic AI for enterprise, and the skills to apply them."
    >
      <p>
        DSN Research Consulting (Pty) Ltd is a South African data analytics and artificial
        intelligence company based in East London. We design and deliver predictive analytics
        and agentic AI capabilities, with a particular focus on making enterprise-grade data
        capability accessible to small and medium enterprises and to the public sector.
      </p>
      <p>
        Our learning platform is the training arm of that work. The programmes on it are built
        from the same tools and methods we use in delivery, and they are aligned to the skills
        that South African employers, municipalities and state entities are actively procuring:
        assurance analytics, data engineering, applied machine learning and MLOps.
      </p>

      <h3 className="mt-4">How our programmes work</h3>
      <ul>
        <li>Every module ends with a knowledge check and a graded practical assessed by an instructor.</li>
        <li>Completion is recorded from assessment outcomes, not from watching videos.</li>
        <li>Each programme closes with a capstone that mirrors a real employer brief.</li>
        <li>Learning is blended: self-paced content and labs on this platform, live sessions, and optional in-person lab days.</li>
      </ul>

      <h3 className="mt-4">Accreditation</h3>
      <p>
        DSN Research is preparing an application for accreditation as a Skills Development
        Provider with the Quality Council for Trades and Occupations, with MICT SETA as the
        intended quality partner. Until accreditation is granted, programmes lead to a DSN
        Research certificate of completion rather than a nationally registered qualification.
        We say this plainly so that learners can make an informed choice.
      </p>

      <h3 className="mt-4">Company details</h3>
      <table className="table table-sm w-auto">
        <tbody>
          <tr><th className="pe-3">Legal name</th><td>DSN Research Consulting (Pty) Ltd</td></tr>
          <tr><th className="pe-3">Registration number</th><td>2015/191048/07</td></tr>
          <tr><th className="pe-3">Founder and Director</th><td>Sibusiso Ndzukuma</td></tr>
          <tr><th className="pe-3">B-BBEE status</th><td>Level 1 contributor</td></tr>
          <tr><th className="pe-3">Website</th><td><a href="https://www.dsnresearch.com" target="_blank" rel="noreferrer">www.dsnresearch.com</a></td></tr>
        </tbody>
      </table>

      <p className="mt-4">
        Questions? See the <Link to="/help/">help centre</Link> or <Link to="/contact/">contact us</Link>.
      </p>
    </PageLayout>
  );
}

export default About;
