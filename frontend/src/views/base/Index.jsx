import { useEffect, useState, useContext } from "react";
import { Link } from "react-router-dom";
import Rater from "react-rater";
import "react-rater/lib/react-rater.css";

import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";
import useAxios from "../../utils/useAxios";
import CartId from "../plugin/CartId";
import GetCurrentAddress from "../plugin/UserCountry";
import UserData from "../plugin/UserData";
import Toast from "../plugin/Toast";
import { CartContext } from "../plugin/Context";
import apiInstance from "../../utils/axios";
import { useAuthStore } from "../../store/auth";

function Index() {
  const [courses, setCourses] = useState([]);
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [, setCartCount] = useContext(CartContext);
  const [isLoggedIn, user] = useAuthStore((state) => [state.isLoggedIn, state.user]);

  const country = GetCurrentAddress().country;
  const userId = UserData()?.user_id;
  const cartId = CartId();

  // Fetch all courses
  const fetchCourses = async () => {
    setIsLoading(true);
    try {
      const res = await useAxios().get(`/course/course-list/`);
      // Handle both paginated response and plain array
      const courseData = res.data?.results || res.data || [];
      setCourses(Array.isArray(courseData) ? courseData : []);
    } catch (error) {
      console.log(error);
      setCourses([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch enrolled courses for logged-in users
  const fetchEnrolledCourses = async () => {
    if (userId) {
      try {
        const res = await useAxios().get(`/student/course-list/${userId}/`);
        const enrollmentData = res.data?.results || res.data || [];
        setEnrolledCourses(Array.isArray(enrollmentData) ? enrollmentData : []);
      } catch (error) {
        console.log(error);
        setEnrolledCourses([]);
      }
    }
  };

  useEffect(() => {
    fetchCourses();
    if (isLoggedIn()) {
      fetchEnrolledCourses();
    }
  }, []);

  const addToCart = async (courseId, userId, price, country, cartId) => {
    const formdata = new FormData();
    formdata.append("course_id", courseId);
    formdata.append("user_id", userId);
    formdata.append("price", price);
    formdata.append("country_name", country);
    formdata.append("cart_id", cartId);

    try {
      await useAxios().post(`course/cart/`, formdata);
      Toast().fire({ title: "Added To Cart", icon: "success" });
      const res = await apiInstance.get(`course/cart-list/${CartId()}/`);
      setCartCount(res.data?.length);
    } catch (error) {
      console.log(error);
    }
  };

  const addToWishlist = (courseId) => {
    const formdata = new FormData();
    formdata.append("user_id", UserData()?.user_id);
    formdata.append("course_id", courseId);

    useAxios()
      .post(`student/wishlist/${UserData()?.user_id}/`, formdata)
      .then((res) => {
        Toast().fire({ icon: "success", title: res.data.message });
      });
  };

  // Tech categories data
  const categories = [
    { icon: "fas fa-robot", title: "Prompt Engineering", count: "50+ Courses", color: "#ff7a59", search: "prompting" },
    { icon: "fas fa-brain", title: "Agentic AI", count: "30+ Courses", color: "#0f3d38", search: "agentic" },
    { icon: "fas fa-shield-alt", title: "Cybersecurity", count: "70+ Courses", color: "#1f2937", search: "security" },
    { icon: "fas fa-cloud", title: "Cloud & DevOps", count: "65+ Courses", color: "#2563eb", search: "cloud" },
    { icon: "fas fa-database", title: "Data Analytics", count: "90+ Courses", color: "#0ea5e9", search: "analytics" },
    { icon: "fas fa-layer-group", title: "Full Stack Dev", count: "100+ Courses", color: "#10b981", search: "fullstack" },
    { icon: "fab fa-python", title: "Python", count: "80+ Courses", color: "#3776ab", search: "python" },
    { icon: "fab fa-react", title: "React", count: "60+ Courses", color: "#61dafb", search: "react" },
    { icon: "fas fa-briefcase", title: "Product & PM", count: "45+ Courses", color: "#7c3aed", search: "product" },
    { icon: "fas fa-users", title: "Leadership", count: "40+ Courses", color: "#f59e0b", search: "leadership" },
    { icon: "fas fa-scale-balanced", title: "Compliance", count: "35+ Courses", color: "#475569", search: "compliance" },
    { icon: "fas fa-pen-ruler", title: "UX & Design", count: "55+ Courses", color: "#ec4899", search: "ux" },
  ];

  return (
    <>
      <BaseHeader />

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6 hero-card">
              {isLoggedIn() && user ? (
                <div className="welcome-banner" style={{ background: 'linear-gradient(135deg, #5624d0 0%, #a435f0 100%)' }}>
                  <h2>Welcome back, {user?.full_name?.split(' ')[0] || user?.username}!</h2>
                  <p className="mb-3">Ready to continue learning? Pick up where you left off.</p>
                  <Link to="/student/courses/" className="btn btn-light fw-bold">
                    My Learning <i className="fas fa-arrow-right ms-2"></i>
                  </Link>
                </div>
              ) : (
                <>
                  <span className="hero-pill">
                    <i className="fas fa-lock"></i> Enterprise-grade learning platform
                  </span>
                  <h1>Upskill teams with secure, modern learning</h1>
                  <p>
                    Combine AI, cloud, cybersecurity, and leadership training in one platform.
                    Designed for corporate subscriptions with secure video delivery and measurable outcomes.
                  </p>
                  <div className="d-flex gap-3 flex-wrap">
                    <Link to="/register/" className="btn btn-light btn-lg fw-bold px-4">
                      Get Started Free
                    </Link>
                    <Link to="/search/?search=enterprise" className="btn btn-outline-light btn-lg px-4">
                      Explore Courses
                    </Link>
                  </div>
                  <div className="hero-highlights">
                    <div className="hero-highlight">
                      <span>Security</span>
                      <strong>Signed playback</strong>
                    </div>
                    <div className="hero-highlight">
                      <span>Analytics</span>
                      <strong>Team insights</strong>
                    </div>
                    <div className="hero-highlight">
                      <span>Scale</span>
                      <strong>Global cohorts</strong>
                    </div>
                  </div>
                </>
              )}
            </div>
            <div className="col-lg-6 d-none d-lg-block text-center hero-media">
              <svg viewBox="0 0 500 400" className="img-fluid" style={{ maxHeight: '350px' }}>
                <defs>
                  <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style={{ stopColor: '#5624d0', stopOpacity: 0.8 }} />
                    <stop offset="100%" style={{ stopColor: '#a855f7', stopOpacity: 0.6 }} />
                  </linearGradient>
                </defs>
                <rect x="40" y="30" width="200" height="150" rx="12" fill="white" opacity="0.15" />
                <rect x="55" y="50" width="170" height="90" rx="8" fill="white" opacity="0.1" />
                <polygon points="120,70 120,120 155,95" fill="white" opacity="0.9" />
                <rect x="55" y="150" width="80" height="8" rx="4" fill="white" opacity="0.3" />
                <rect x="55" y="165" width="120" height="6" rx="3" fill="white" opacity="0.2" />
                <rect x="260" y="80" width="200" height="150" rx="12" fill="white" opacity="0.15" />
                <rect x="275" y="100" width="170" height="90" rx="8" fill="white" opacity="0.1" />
                <circle cx="360" cy="145" r="25" fill="none" stroke="white" strokeWidth="3" opacity="0.7" />
                <path d="M355 135 L355 155 M345 145 L365 145" stroke="white" strokeWidth="3" opacity="0.7" />
                <rect x="275" y="200" width="100" height="8" rx="4" fill="white" opacity="0.3" />
                <rect x="275" y="215" width="140" height="6" rx="3" fill="white" opacity="0.2" />
                <rect x="150" y="220" width="200" height="150" rx="12" fill="white" opacity="0.15" />
                <rect x="165" y="240" width="170" height="90" rx="8" fill="white" opacity="0.1" />
                <text x="220" y="290" fill="white" opacity="0.8" fontSize="28" fontFamily="monospace">&lt;/&gt;</text>
                <rect x="165" y="340" width="90" height="8" rx="4" fill="white" opacity="0.3" />
                <rect x="165" y="355" width="130" height="6" rx="3" fill="white" opacity="0.2" />
                <circle cx="450" cy="50" r="30" fill="white" opacity="0.08" />
                <circle cx="30" cy="300" r="20" fill="white" opacity="0.06" />
              </svg>
            </div>
          </div>
        </div>
      </section>

      <section className="enterprise-strip">
        <div className="container">
          <div className="row g-3 align-items-center">
            <div className="col-md-4">
              <div className="stat-item text-start">
                <div className="stat-number">Enterprise ready</div>
                <div className="stat-label text-white-50">
                  Secure streaming, role-based access, audit logs
                </div>
              </div>
            </div>
            <div className="col-md-8">
              <div className="row g-3">
                <div className="col-md-4">
                  <div className="enterprise-card">
                    <h6>Secure video delivery</h6>
                    <p>Signed URLs, watermarking, playback controls.</p>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="enterprise-card">
                    <h6>Insights that matter</h6>
                    <p>Completion, skill gaps, cohort performance.</p>
                  </div>
                </div>
                <div className="col-md-4">
                  <div className="enterprise-card">
                    <h6>Corporate compliance</h6>
                    <p>Policy training, exportable certifications.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Continue Learning Section (for logged-in users) */}
      {isLoggedIn() && enrolledCourses.length > 0 && (
        <section className="py-5">
          <div className="container">
            <div className="section-header d-flex justify-content-between align-items-center">
              <div>
                <h2 className="section-title">Let's start learning</h2>
                <p className="section-subtitle mb-0">Continue where you left off</p>
              </div>
              <Link to="/student/courses/" className="btn btn-dsn-outline">
                My Learning
              </Link>
            </div>
            <div className="row g-4 mt-2">
              {enrolledCourses.slice(0, 4).map((enrollment, index) => (
                <div className="col-md-6 col-lg-3" key={index}>
                  <Link to={`/student/course-detail/${enrollment.enrollment_id}/`} className="text-decoration-none">
                    <div className="progress-card">
                      <img
                        src={enrollment.course?.image || "https://via.placeholder.com/300x160?text=Course"}
                        alt={enrollment.course?.title}
                      />
                      <div className="progress-info">
                        <h6 className="progress-title text-dark">{enrollment.course?.title}</h6>
                        <div className="progress-dsn mt-2">
                          <div
                            className="progress-bar"
                            style={{ width: `${enrollment.progress || 0}%` }}
                          ></div>
                        </div>
                        <span className="progress-text">{enrollment.progress || 0}% complete</span>
                      </div>
                    </div>
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Categories Section */}
      <section className="categories-section">
        <div className="container">
          <div className="section-header text-center">
            <h2 className="section-title">Top Tech Categories</h2>
            <p className="section-subtitle">
              Master the skills that matter most in today's tech industry
            </p>
          </div>
          <div className="row g-4 mt-3">
            {categories.map((cat, index) => (
              <div className="col-6 col-md-4 col-lg-3 col-xl-2" key={index}>
                <Link to={`/search/?search=${cat.search}`} className="text-decoration-none">
                  <div className="category-card h-100">
                    <div className="icon" style={{ color: cat.color }}>
                      <i className={cat.icon}></i>
                    </div>
                    <h5>{cat.title}</h5>
                    <span>{cat.count}</span>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Courses Section */}
      <section className="py-5">
        <div className="container">
          <div className="section-header d-flex justify-content-between align-items-center">
            <div>
              <h2 className="section-title">Popular Courses</h2>
              <p className="section-subtitle mb-0">Learn from the best instructors</p>
            </div>
            <Link to="/search/" className="btn btn-dsn-outline">
              View All <i className="fas fa-arrow-right ms-2"></i>
            </Link>
          </div>

          {isLoading ? (
            <div className="text-center py-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : (
            <div className="row g-4 mt-2">
              {courses.slice(0, 8).map((course, index) => (
                <div className="col-sm-6 col-lg-3" key={index}>
                  <div className="course-card">
                    <Link to={`/course-detail/${course.slug}/`}>
                      <img
                        src={course.image || "https://via.placeholder.com/300x160?text=Course"}
                        alt={course.title}
                        className="card-img-top"
                      />
                    </Link>
                    <div className="card-body">
                      <Link to={`/course-detail/${course.slug}/`} className="text-decoration-none">
                        <h5 className="card-title text-dark">{course.title}</h5>
                      </Link>
                      <p className="instructor-name">{course.teacher?.full_name}</p>
                      <div className="rating">
                        <span className="rating-score">{course.average_rating?.toFixed(1) || "4.5"}</span>
                        <Rater total={5} rating={course.average_rating || 4.5} interactive={false} />
                        <span className="rating-count">({course.reviews?.length || 0})</span>
                      </div>
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <span className="price">${course.price}</span>
                          {course.original_price && course.original_price > course.price && (
                            <span className="original-price">${course.original_price}</span>
                          )}
                        </div>
                        <div className="d-flex gap-2">
                          <button
                            className="btn btn-sm p-1"
                            onClick={() => addToWishlist(course.id)}
                            title="Add to Wishlist"
                          >
                            <i className="fas fa-heart text-danger"></i>
                          </button>
                          <button
                            className="btn btn-sm p-1"
                            onClick={() => addToCart(course.id, userId, course.price, country, cartId)}
                            title="Add to Cart"
                          >
                            <i className="fas fa-shopping-cart text-primary"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {courses.length === 0 && !isLoading && (
            <div className="text-center py-5">
              <i className="fas fa-book-open fa-3x text-muted mb-3"></i>
              <p className="text-muted">No courses available yet. Check back soon!</p>
            </div>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section style={{ backgroundColor: '#f7f9fa' }} className="py-5">
        <div className="container">
          <div className="row">
            <div className="col-6 col-md-3">
              <div className="stat-item">
                <div className="stat-number">10K+</div>
                <div className="stat-label">Students</div>
              </div>
            </div>
            <div className="col-6 col-md-3">
              <div className="stat-item">
                <div className="stat-number">500+</div>
                <div className="stat-label">Courses</div>
              </div>
            </div>
            <div className="col-6 col-md-3">
              <div className="stat-item">
                <div className="stat-number">50+</div>
                <div className="stat-label">Instructors</div>
              </div>
            </div>
            <div className="col-6 col-md-3">
              <div className="stat-item">
                <div className="stat-number">4.8</div>
                <div className="stat-label">Avg. Rating</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Become an Instructor CTA */}
      <section className="py-5">
        <div className="container">
          <div className="instructor-cta">
            <div className="row align-items-center">
              <div className="col-lg-8">
                <h3 className="mb-3">Become an Instructor</h3>
                <p className="mb-4" style={{ opacity: 0.9, fontSize: '16px' }}>
                  Share your knowledge with thousands of students. Create and sell courses on
                  Prompt Engineering, AI, Full Stack Development, and more.
                </p>
                <Link to="/instructor/create-course/" className="btn btn-light fw-bold px-4 py-2">
                  Start Teaching Today <i className="fas fa-arrow-right ms-2"></i>
                </Link>
              </div>
              <div className="col-lg-4 d-none d-lg-block text-center">
                <i className="fas fa-chalkboard-teacher" style={{ fontSize: '120px', opacity: 0.3 }}></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Topics */}
      <section className="py-5" style={{ backgroundColor: '#f7f9fa' }}>
        <div className="container">
          <div className="section-header text-center mb-4">
            <h2 className="section-title">Featured Topics by Category</h2>
            <p className="section-subtitle">Explore our most popular tech courses</p>
          </div>
          <div className="row">
            <div className="col-md-4 mb-4">
              <h5 className="mb-3">AI & Automation</h5>
              <ul className="list-unstyled">
                <li className="mb-2">
                  <Link to="/search/?search=chatgpt" className="text-primary fw-bold">ChatGPT</Link>
                  <span className="text-muted ms-2">2.5M+ students</span>
                </li>
                <li className="mb-2">
                  <Link to="/search/?search=prompting" className="text-primary fw-bold">Prompt Engineering</Link>
                  <span className="text-muted ms-2">1.8M+ students</span>
                </li>
                <li className="mb-2">
                  <Link to="/search/?search=agentic" className="text-primary fw-bold">Agentic AI</Link>
                  <span className="text-muted ms-2">720K+ students</span>
                </li>
              </ul>
            </div>
            <div className="col-md-4 mb-4">
              <h5 className="mb-3">Cloud & Security</h5>
              <ul className="list-unstyled">
                <li className="mb-2">
                  <Link to="/search/?search=cloud" className="text-primary fw-bold">Cloud Architecture</Link>
                  <span className="text-muted ms-2">1.9M+ students</span>
                </li>
                <li className="mb-2">
                  <Link to="/search/?search=devops" className="text-primary fw-bold">DevOps</Link>
                  <span className="text-muted ms-2">2.2M+ students</span>
                </li>
                <li className="mb-2">
                  <Link to="/search/?search=security" className="text-primary fw-bold">Security Operations</Link>
                  <span className="text-muted ms-2">980K+ students</span>
                </li>
              </ul>
            </div>
            <div className="col-md-4 mb-4">
              <h5 className="mb-3">Leadership & Product</h5>
              <ul className="list-unstyled">
                <li className="mb-2">
                  <Link to="/search/?search=leadership" className="text-primary fw-bold">Leadership</Link>
                  <span className="text-muted ms-2">1.1M+ students</span>
                </li>
                <li className="mb-2">
                  <Link to="/search/?search=product" className="text-primary fw-bold">Product Strategy</Link>
                  <span className="text-muted ms-2">860K+ students</span>
                </li>
                <li className="mb-2">
                  <Link to="/search/?search=compliance" className="text-primary fw-bold">Compliance & Risk</Link>
                  <span className="text-muted ms-2">640K+ students</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <BaseFooter />
    </>
  );
}

export default Index;
