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
                Empowering the next generation of tech professionals with cutting-edge courses in
                AI, Full Stack Development, and emerging technologies.
              </p>
              {/* Social Links */}
              <div className="d-flex gap-3 mt-3">
                <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer"
                   className="text-white" style={{ fontSize: '20px', opacity: 0.7, transition: 'opacity 0.2s' }}>
                  <i className="fab fa-linkedin"></i>
                </a>
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer"
                   className="text-white" style={{ fontSize: '20px', opacity: 0.7 }}>
                  <i className="fab fa-twitter"></i>
                </a>
                <a href="https://github.com" target="_blank" rel="noopener noreferrer"
                   className="text-white" style={{ fontSize: '20px', opacity: 0.7 }}>
                  <i className="fab fa-github"></i>
                </a>
                <a href="https://youtube.com" target="_blank" rel="noopener noreferrer"
                   className="text-white" style={{ fontSize: '20px', opacity: 0.7 }}>
                  <i className="fab fa-youtube"></i>
                </a>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="col-lg-2 col-md-6 col-6 mb-4 mb-lg-0">
            <h5>Learn</h5>
            <ul>
              <li><Link to="/search/?search=prompting">Prompt Engineering</Link></li>
              <li><Link to="/search/?search=agentic">Agentic AI</Link></li>
              <li><Link to="/search/?search=fullstack">Full Stack Dev</Link></li>
              <li><Link to="/search/?search=python">Python</Link></li>
              <li><Link to="/search/?search=react">React</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div className="col-lg-2 col-md-6 col-6 mb-4 mb-lg-0">
            <h5>Company</h5>
            <ul>
              <li><Link to="/pages/about-us/">About Us</Link></li>
              <li><Link to="/pages/contact-us/">Contact</Link></li>
              <li><Link to="/instructor/create-course/">Teach on DSN</Link></li>
              <li><a href="#">Careers</a></li>
              <li><a href="#">Blog</a></li>
            </ul>
          </div>

          {/* Support */}
          <div className="col-lg-2 col-md-6 col-6 mb-4 mb-lg-0">
            <h5>Support</h5>
            <ul>
              <li><a href="#">Help Center</a></li>
              <li><a href="#">FAQ</a></li>
              <li><a href="#">Terms of Service</a></li>
              <li><a href="#">Privacy Policy</a></li>
              <li><a href="#">Refund Policy</a></li>
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
                <a href="tel:+27123456789">
                  <i className="fas fa-phone me-2"></i>
                  +27 12 345 6789
                </a>
              </li>
              <li style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px' }}>
                <i className="fas fa-map-marker-alt me-2"></i>
                South Africa
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="footer-bottom">
          <div className="row align-items-center">
            <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
              <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: '14px' }}>
                © {currentYear} DSN Research. All rights reserved.
              </span>
            </div>
            <div className="col-md-6 text-center text-md-end">
              <div className="d-flex justify-content-center justify-content-md-end gap-4">
                <a href="#" style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px' }}>Privacy</a>
                <a href="#" style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px' }}>Terms</a>
                <a href="#" style={{ color: 'rgba(255,255,255,0.6)', fontSize: '13px' }}>Cookies</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default BaseFooter;
