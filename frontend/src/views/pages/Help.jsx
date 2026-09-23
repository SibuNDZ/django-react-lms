import React from "react";
import { Link } from "react-router-dom";
import PageLayout from "./PageLayout";

const FAQ = [
  {
    section: "Getting started",
    items: [
      ["How do I enrol?", "Create an account, open a programme page and click Enrol. Our current programmes are free to join. You will find the programme under My Learning straight away."],
      ["What do I need?", "A laptop with a modern browser and a stable internet connection. Practical modules use cloud development environments, so you do not need a powerful machine. Lab days at our East London site are optional."],
      ["Is there a start date?", "Programmes are self-paced on the platform with scheduled live sessions per cohort. Your facilitator will share the live session calendar after enrolment."],
    ],
  },
  {
    section: "Learning and assessment",
    items: [
      ["How is progress recorded?", "Lessons are marked complete as you work through them. Quiz and practical lessons are only marked complete when you pass the assessment; you cannot tick them off yourself."],
      ["How do knowledge checks work?", "Each module ends with a short timed quiz. The pass mark is 70 percent and you have three attempts. Results are marked immediately on the platform."],
      ["How are practicals graded?", "You submit a file, a link or a written answer. An instructor grades it against the module rubric within ten working days and records an outcome of competent or not yet competent, with feedback. If you are not yet competent you get one resubmission within two weeks."],
      ["Can I use AI tools?", "Yes, for assistance, as long as you declare it in your submission and can explain every part of the work you hand in. An instructor may ask you to walk through your code."],
      ["Do I get a certificate?", "Yes. When every module is competent, including the capstone, you receive a DSN Research certificate with a unique number. Until our accreditation is granted this is a certificate of completion, not a nationally registered qualification."],
    ],
  },
  {
    section: "Appeals and complaints",
    items: [
      ["I disagree with an assessment outcome.", "First ask your assessor for clarification. If you still disagree, lodge a written appeal within ten working days of the outcome. A second assessor who was not involved re-assesses your evidence, and you receive a written decision within fifteen working days. Appealing never counts against you."],
      ["How do I make a complaint?", "Email complaints@dsnresearch.com or tell any staff member. We acknowledge complaints within two working days and resolve them within ten, and we tell you how to escalate if you are not satisfied."],
    ],
  },
  {
    section: "Account and data",
    items: [
      ["I forgot my password.", "Use the Forgot password link on the login page. A reset link is emailed to you."],
      ["How do I change my details?", "Open Account Settings from your profile to update your name, photo and country, or to change your password."],
      ["What do you do with my data?", "We use it to run your programme, assess you, issue certificates and meet our reporting obligations. The Privacy Notice explains this in full and how to request, correct or delete your information."],
      ["Can I get a refund?", "The current programmes are free. Where fees apply, our Refund Policy sets out the cooling-off period and refund terms."],
    ],
  },
];

function Help() {
  return (
    <PageLayout title="Help centre" intro="Answers to the questions we hear most, and how to reach a person.">
      <div className="alert alert-light border mb-4">
        Need something not covered here? <Link to="/contact/">Contact us</Link> and we will
        respond within one working day.
      </div>
      {FAQ.map((group) => (
        <div key={group.section} className="mb-4">
          <h3 className="mb-3">{group.section}</h3>
          <div className="accordion" id={`faq-${group.section.replace(/\s+/g, "-")}`}>
            {group.items.map(([q, a], i) => {
              const id = `${group.section}-${i}`.replace(/[^a-z0-9]+/gi, "-");
              return (
                <div className="accordion-item" key={id}>
                  <h2 className="accordion-header" id={`h-${id}`}>
                    <button
                      className="accordion-button collapsed"
                      type="button"
                      data-bs-toggle="collapse"
                      data-bs-target={`#c-${id}`}
                      aria-expanded="false"
                      aria-controls={`c-${id}`}
                    >
                      {q}
                    </button>
                  </h2>
                  <div id={`c-${id}`} className="accordion-collapse collapse" aria-labelledby={`h-${id}`}>
                    <div className="accordion-body">{a}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
      <h3 className="mt-5">Policies</h3>
      <ul>
        <li><Link to="/terms/">Terms of use</Link></li>
        <li><Link to="/privacy/">Privacy notice</Link></li>
        <li><Link to="/refunds/">Fees and refund policy</Link></li>
      </ul>
    </PageLayout>
  );
}

export default Help;
