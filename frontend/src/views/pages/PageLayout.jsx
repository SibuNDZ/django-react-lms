import React from "react";
import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";

/** Shared frame for static information pages (about, contact, help, policies). */
function PageLayout({ title, intro, updated, children }) {
  return (
    <>
      <BaseHeader />
      <section className="py-0">
        <div className="container">
          <div className="bg-light p-4 p-md-5 rounded-3 mt-4">
            <h1 className="mb-2">{title}</h1>
            {intro && <p className="lead mb-0 text-muted">{intro}</p>}
            {updated && (
              <small className="text-muted d-block mt-2">Last updated {updated}</small>
            )}
          </div>
        </div>
      </section>
      <section className="py-5">
        <div className="container">
          <div className="row">
            <div className="col-lg-9">{children}</div>
          </div>
        </div>
      </section>
      <BaseFooter />
    </>
  );
}

export default PageLayout;
