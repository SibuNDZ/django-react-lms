import { Link } from 'react-router-dom';

function BaseFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer-dsn">
      <div className="container">
        <div className="row">
          {/* Company Info */}
          <div className="col-lg-4 col-md-6 mb-4 mb-lg-0">
            <div className="mb-4">
              <Link to="/" className="d-flex align-items-center mb-3 text-decoration-none">
                <span style={{ color: '#a435f0', fontWeight: 800, fontSize: '24px' }}>DSN</span>
                <span style={{ color: '#fff', fontWeight: 600, fontSize: '24px', marginLeft: '4px' }}>Research</span>
              </Link>
              <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px', lineHeight: '1.7' }}>
                Data, analytics and AI programmes built from real delivery work and aligned to the
                skills South African employers and public bodies are procuring.
              </p>
              <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px' }}>
                <a href="https://www.dsnresearch.com" target="_blank" rel="noopener noreferrer" className="text-white">
                  <i className="fas fa-globe me-2"></i>www.dsnresearch.com
                </a>
              </p>
            </div>
          </div>

          {/* Programmes */}
          <div className="col-lg-2 col-md-6 col-6 mb-4 mb-lg-0">
            <h5>Programmes</h5>
            <ul>
              <li><Link to="/course-detail/data-analytics-bi-foundation/">Data Analytics &amp; BI</Link></li>
              <li><Link to="/course-detail/applied-data-science-machine-learning/">Applied Data Science</Link></li>
              <li><Link to="/course-detail/full-stack-ai-mlops-engineering/">AI &amp; MLOps Engineering</Link></li>
              <li><Link to="/search/">All programmes</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div className="col-lg-2 col-md-6 col-6 mb-4 mb-lg-0">
            <h5>Company</h5>
            <ul>
              <li><Link to="/about/">About us</Link></li>
              <li><Link to="/contact/">Contact</Link></li>
              <li><Link to="/instructor/create-course/">Teach on DSN</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div className="col-lg-2 col-md-6 col-6 mb-4 mb-lg-0">
            <h5>Support</h5>
            <ul>
              <li><Link to="/help/">Help centre and FAQ</Link></li>
              <li><Link to="/terms/">Terms of use</Link></li>
              <li><Link to="/privacy/">Privacy notice</Link></li>
              <li><Link to="/refunds/">Fees and refunds</Link></li>
            </ul>
          </div>

          {/* Contact */}
          <div className="col-lg-2 col-md-6 col-6">
            <h5>Contact</h5>
            <ul>
              <li>
                <a href="mailto:info@dsnresearch.com">
                  <i className="fas fa-envelope me-2"></i>
                  info@dsnresearch.com
                </a>
              </li>
              <li>
                <a href="tel:+27662963239">
                  <i className="fas fa-phone me-2"></i>
                  +27 66 296 3239
                </a>
              </li>
              <li style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px' }}>
                <i className="fas fa-map-marker-alt me-2"></i>
                East London, South Africa
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div className="row align-items-center">
            <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
              <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: '14px' }}>
                © {currentYear} DSN Research Consulting (Pty) Ltd. Registration 2015/191048/07.
              </span>
            </div>
            <div className="col-md-6 text-center text-md-end">
              <div className="d-flex justify-content-center justify-content-md-end gap-4">
                <Link to="/privacy/" style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px' }}>Privacy</Link>
                <Link to="/terms/" style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px' }}>Terms</Link>
                <Link to="/privacy/#cookies" style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px' }}>Cookies</Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default BaseFooter;
