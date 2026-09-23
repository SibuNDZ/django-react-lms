import { useState, useEffect, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import moment from "moment";
import Rater from "react-rater";
import "react-rater/lib/react-rater.css";
import Swal from "sweetalert2";

import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";
import { useParams } from "react-router-dom";
import useAxios from "../../utils/useAxios";
import CartId from "../plugin/CartId";
import GetCurrentAddress from "../plugin/UserCountry";
import UserData from "../plugin/UserData";
import Toast from "../plugin/Toast";
import { CartContext } from "../plugin/Context";
import { addCourseToCart } from "../../utils/lmsApi";

function CourseDetail() {
  const [course, setCourse] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [addToCartBtn, setAddToCartBtn] = useState("Add To Cart");
  const [enrolling, setEnrolling] = useState(false);
  const [relatedCourses, setRelatedCourses] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [reviewForm, setReviewForm] = useState({ rating: 5, text: "" });
  const [reviewBusy, setReviewBusy] = useState(false);
  const myReview = reviews.find((r) => r.student?.id === userId) || null;

  const fetchReviews = async () => {
    try {
      const res = await useAxios().get(`courses/${param.slug}/reviews/`);
      setReviews(res.data?.results || res.data || []);
    } catch (error) {
      setReviews([]);
    }
  };

  useEffect(() => {
    fetchReviews();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [param.slug]);

  useEffect(() => {
    if (myReview) setReviewForm({ rating: myReview.rating, text: myReview.review_text || "" });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [myReview?.id]);

  const submitReview = async (e) => {
    e.preventDefault();
    setReviewBusy(true);
    try {
      await useAxios().post(`courses/${param.slug}/reviews/create/`, {
        rating: Number(reviewForm.rating),
        review_text: reviewForm.text.trim(),
      });
      Toast().fire({ icon: "success", title: myReview ? "Review updated" : "Thanks for your review" });
      await fetchReviews();
      fetchCourse();
    } catch (error) {
      Toast().fire({ icon: "error", title: error?.response?.data?.message || "Could not save your review" });
    } finally {
      setReviewBusy(false);
    }
  };
  const [cartCount, setCartCount] = useContext(CartContext);

  const param = useParams();
  const navigate = useNavigate();

  const country = GetCurrentAddress().country;
  const userId = UserData()?.user_id;

  const fetchCourse = () => {
    useAxios()
      .get(`courses/${param.slug}/`)
      .then((res) => {
        setCourse({
          ...res.data,
          image: res.data.thumbnail,
          teacher: res.data.instructor,
          curriculum: (res.data.sections || []).map((section) => ({
            ...section,
            variant_id: section.section_id,
            variant_items: section.lessons || [],
          })),
        });
        setIsLoading();
      });
  };

  useEffect(() => {
    fetchCourse();
  }, []);

  useEffect(() => {
    useAxios()
      .get(`courses/?page_size=4`)
      .then((res) => {
        const items = res.data?.results || res.data || [];
        setRelatedCourses(items.filter((c) => c.slug !== param.slug).slice(0, 3));
      })
      .catch(() => setRelatedCourses([]));
  }, [param.slug]);

  const addToCart = async (courseId) => {
    setAddToCartBtn("Adding To Cart");
    try {
      const count = await addCourseToCart(courseId, CartId());
      setAddToCartBtn("Added To Cart");
      Toast().fire({
        title: "Added To Cart",
        icon: "success",
      });
      setCartCount(count);
    } catch (error) {
      const message = error?.response?.data?.message || "Could not add to cart";
      if (/already in cart/i.test(message)) {
        setAddToCartBtn("Added To Cart");
      } else {
        setAddToCartBtn("Add To Cart");
      }
      Toast().fire({ icon: "info", title: message });
    }
  };

  // Free courses skip the cart and checkout entirely.
  const enrollFree = async (courseId) => {
    if (!UserData()) {
      navigate(`/login/?next=/course-detail/${param.slug}/`);
      return;
    }
    setEnrolling(true);
    try {
      await useAxios().post(`student/enroll-free/${courseId}/`);
      Toast().fire({ icon: "success", title: "You are enrolled. Happy learning!" });
      navigate(`/student/courses/`);
    } catch (error) {
      const message = error?.response?.data?.message || "";
      if (/already enrolled/i.test(message)) {
        navigate(`/student/courses/`);
      } else {
        Toast().fire({ icon: "error", title: message || "Could not enrol" });
      }
    } finally {
      setEnrolling(false);
    }
  };

  return (
    <>
      <BaseHeader />

      <>
        {isLoading === true ? (
          <p>
            Loading <i className="fas fa-spinner fa-spin"></i>
          </p>
        ) : (
          <>
            <section className="bg-light py-0 py-sm-5">
              <div className="container">
                <div className="row py-5">
                  <div className="col-lg-8">
                    {/* Badge */}
                    <h6 className="mb-3 font-base bg-primary text-white py-2 px-4 rounded-2 d-inline-block">
                      {course.category.title}
                    </h6>
                    {/* Title */}
                    <h1 className="mb-3">{course.title}</h1>
                    <p
                      className="mb-3"
                      dangerouslySetInnerHTML={{
                        __html: `${course?.description?.slice(0, 200)}`,
                      }}
                    ></p>
                    {/* Content */}
                    <ul className="list-inline mb-0">
                      <li className="list-inline-item h6 me-3 mb-1 mb-sm-0">
                        <i className="fas fa-star text-warning me-2" />
                        {course.average_rating}/5
                      </li>
                      <li className="list-inline-item h6 me-3 mb-1 mb-sm-0">
                        <i className="fas fa-user-graduate text-orange me-2" />
                        {course.students?.length} Enrolled
                      </li>
                      <li className="list-inline-item h6 me-3 mb-1 mb-sm-0">
                        <i className="fas fa-signal text-success me-2" />
                        {course.level}
                      </li>
                      <li className="list-inline-item h6 me-3 mb-1 mb-sm-0">
                        <i className="bi bi-patch-exclamation-fill text-danger me-2" />
                        {moment(course.date).format("DD MMM, YYYY")}
                      </li>
                      <li className="list-inline-item h6 mb-0">
                        <i className="fas fa-globe text-info me-2" />
                        {course.language}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>
            <section className="pb-0 py-lg-5">
              <div className="container">
                <div className="row">
                  {/* Main content START */}
                  <div className="col-lg-8">
                    <div className="card shadow rounded-2 p-0">
                      {/* Tabs START */}
                      <div className="card-header border-bottom px-4 py-3">
                        <ul
                          className="nav nav-pills nav-tabs-line py-0"
                          id="course-pills-tab"
                          role="tablist"
                        >
                          {/* Tab item */}
                          <li
                            className="nav-item me-2 me-sm-4"
                            role="presentation"
                          >
                            <button
                              className="nav-link mb-2 mb-md-0 active"
                              id="course-pills-tab-1"
                              data-bs-toggle="pill"
                              data-bs-target="#course-pills-1"
                              type="button"
                              role="tab"
                              aria-controls="course-pills-1"
                              aria-selected="true"
                            >
                              Overview
                            </button>
                          </li>
                          {/* Tab item */}
                          <li
                            className="nav-item me-2 me-sm-4"
                            role="presentation"
                          >
                            <button
                              className="nav-link mb-2 mb-md-0"
                              id="course-pills-tab-2"
                              data-bs-toggle="pill"
                              data-bs-target="#course-pills-2"
                              type="button"
                              role="tab"
                              aria-controls="course-pills-2"
                              aria-selected="false"
                            >
                              Curriculum
                            </button>
                          </li>
                          {/* Tab item */}
                          <li
                            className="nav-item me-2 me-sm-4"
                            role="presentation"
                          >
                            <button
                              className="nav-link mb-2 mb-md-0"
                              id="course-pills-tab-3"
                              data-bs-toggle="pill"
                              data-bs-target="#course-pills-3"
                              type="button"
                              role="tab"
                              aria-controls="course-pills-3"
                              aria-selected="false"
                            >
                              Instructor
                            </button>
                          </li>
                          {/* Tab item */}
                          <li
                            className="nav-item me-2 me-sm-4"
                            role="presentation"
                          >
                            <button
                              className="nav-link mb-2 mb-md-0"
                              id="course-pills-tab-4"
                              data-bs-toggle="pill"
                              data-bs-target="#course-pills-4"
                              type="button"
                              role="tab"
                              aria-controls="course-pills-4"
                              aria-selected="false"
                            >
                              Reviews
                            </button>
                          </li>
                          {/* Tab item */}
                        </ul>
                      </div>
                      {/* Tabs END */}
                      {/* Tab contents START */}
                      <div className="card-body p-4">
                        <div
                          className="tab-content pt-2"
                          id="course-pills-tabContent"
                        >
                          {/* Content START */}
                          <div
                            className="tab-pane fade show active"
                            id="course-pills-1"
                            role="tabpanel"
                            aria-labelledby="course-pills-tab-1"
                          >
                            <h5 className="mb-3">Course Description</h5>
                            <p
                              className="mb-3"
                              dangerouslySetInnerHTML={{
                                __html: `${course?.description}`,
                              }}
                            ></p>

                            {/* Course detail END */}
                          </div>
                          {/* Content END */}
                          {/* Content START */}
                          <div
                            className="tab-pane fade"
                            id="course-pills-2"
                            role="tabpanel"
                            aria-labelledby="course-pills-tab-2"
                          >
                            <div className="d-flex justify-content-between align-items-center mb-3">
                              <h5 className="mb-0">Curriculum</h5>
                              <small className="text-muted">
                                {course.total_sections ?? course.curriculum?.length ?? 0} modules ·{" "}
                                {course.total_lessons ?? 0} lessons
                                {course.total_duration > 0 && ` · ${Math.round(course.total_duration / 60)} hours`}
                              </small>
                            </div>
                            <div className="accordion accordion-icon accordion-bg-light" id="curriculumAccordion">
                              {course?.curriculum?.map((section, index) => (
                                <div className="accordion-item mb-3" key={section.variant_id}>
                                  <h6 className="accordion-header font-base" id={`heading-${section.variant_id}`}>
                                    <button
                                      className={`accordion-button fw-bold rounded d-sm-flex d-inline-block ${index > 0 ? "collapsed" : ""}`}
                                      type="button"
                                      data-bs-toggle="collapse"
                                      data-bs-target={`#collapse-${section.variant_id}`}
                                      aria-expanded={index === 0}
                                      aria-controls={`collapse-${section.variant_id}`}
                                    >
                                      {section.title}
                                      <span className="small ms-0 ms-sm-2 text-muted fw-normal">
                                        ({section.variant_items?.length || 0} lesson
                                        {(section.variant_items?.length || 0) === 1 ? "" : "s"})
                                      </span>
                                    </button>
                                  </h6>
                                  <div
                                    id={`collapse-${section.variant_id}`}
                                    className={`accordion-collapse collapse ${index === 0 ? "show" : ""}`}
                                    aria-labelledby={`heading-${section.variant_id}`}
                                    data-bs-parent="#curriculumAccordion"
                                  >
                                    <div className="accordion-body mt-3">
                                      {section.description && (
                                        <p className="text-muted small mb-3">{section.description}</p>
                                      )}
                                      {section.variant_items?.map((lesson) => {
                                        const icon =
                                          lesson.lesson_type === "quiz" ? "fa-question" :
                                          lesson.lesson_type === "assignment" ? "fa-upload" :
                                          lesson.lesson_type === "text" ? "fa-file-alt" :
                                          lesson.lesson_type === "resource" ? "fa-paperclip" : "fa-play";
                                        const label =
                                          lesson.lesson_type === "quiz" ? "Knowledge check" :
                                          lesson.lesson_type === "assignment" ? "Graded practical" :
                                          lesson.lesson_type === "text" ? "Reading" :
                                          lesson.lesson_type === "resource" ? "Resource" : "Video";
                                        return (
                                          <div key={lesson.lesson_id}>
                                            <div className="d-flex justify-content-between align-items-center">
                                              <div className="d-flex align-items-center">
                                                <span className={`btn btn-sm btn-round mb-0 ${lesson.is_free_preview ? "btn-success-soft" : "btn-light"}`}>
                                                  <i className={`fas ${lesson.is_free_preview ? icon : "fa-lock"} me-0`} />
                                                </span>
                                                <span className="ms-2 mb-0 h6 fw-light">
                                                  {lesson.title}
                                                  <small className="text-muted d-block">
                                                    {label}
                                                    {lesson.is_free_preview && <span className="badge bg-success ms-2">Preview</span>}
                                                  </small>
                                                </span>
                                              </div>
                                              <p className="mb-0 text-muted small">
                                                {lesson.duration ? `${lesson.duration}m` : ""}
                                              </p>
                                            </div>
                                            <hr />
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </div>
                                </div>
                              ))}
                              {(!course?.curriculum || course.curriculum.length === 0) && (
                                <p className="text-muted">The curriculum for this course has not been published yet.</p>
                              )}
                            </div>
                          </div>

                          <div
                            className="tab-pane fade"
                            id="course-pills-3"
                            role="tabpanel"
                            aria-labelledby="course-pills-tab-3"
                          >
                            <div className="card mb-0 mb-md-4">
                              <div className="row g-0 align-items-center">
                                <div className="col-md-3 p-3">
                                  <img
                                    src={course.teacher?.image || course.instructor?.image}
                                    className="img-fluid rounded-circle"
                                    alt={course.teacher?.full_name || "Instructor"}
                                    style={{ width: "160px", height: "160px", objectFit: "cover" }}
                                  />
                                </div>
                                <div className="col-md-9">
                                  <div className="card-body">
                                    <h3 className="card-title mb-1">{course.teacher?.full_name}</h3>
                                    <p className="text-muted mb-2">Instructor</p>
                                    {course.teacher?.about ? (
                                      <p className="mb-0" style={{ whiteSpace: "pre-wrap" }}>{course.teacher.about}</p>
                                    ) : (
                                      <p className="mb-0 text-muted">This instructor has not added a biography yet.</p>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div
                            className="tab-pane fade"
                            id="course-pills-4"
                            role="tabpanel"
                            aria-labelledby="course-pills-tab-4"
                          >
                            <div className="row mb-4">
                              <div className="col-md-4 text-center border-end">
                                <h1 className="display-4 mb-0">
                                  {reviews.length ? Number(course.average_rating || 0).toFixed(1) : "New"}
                                </h1>
                                <Rater total={5} rating={Number(course.average_rating) || 0} interactive={false} />
                                <p className="text-muted mb-0">
                                  {reviews.length} review{reviews.length === 1 ? "" : "s"}
                                </p>
                              </div>
                              <div className="col-md-8">
                                {[5, 4, 3, 2, 1].map((star) => {
                                  const n = reviews.filter((r) => Number(r.rating) === star).length;
                                  const pct = reviews.length ? Math.round((n / reviews.length) * 100) : 0;
                                  return (
                                    <div className="d-flex align-items-center mb-1" key={star}>
                                      <small className="me-2" style={{ width: "48px" }}>{star} star</small>
                                      <div className="progress flex-grow-1" style={{ height: "8px" }}>
                                        <div className="progress-bar bg-warning" style={{ width: `${pct}%` }} />
                                      </div>
                                      <small className="ms-2 text-muted" style={{ width: "36px" }}>{pct}%</small>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>

                            {reviews.length === 0 && (
                              <p className="text-muted">No reviews yet. Enrolled learners can leave the first one.</p>
                            )}
                            {reviews.map((r) => (
                              <div className="d-flex mb-4" key={r.review_id || r.id}>
                                <img
                                  className="rounded-circle me-3"
                                  src={r.profile?.image}
                                  alt=""
                                  style={{ width: "48px", height: "48px", objectFit: "cover" }}
                                />
                                <div>
                                  <div className="d-flex align-items-center flex-wrap">
                                    <h6 className="me-3 mb-0">{r.profile?.full_name || r.student?.full_name || "Learner"}</h6>
                                    <Rater total={5} rating={Number(r.rating) || 0} interactive={false} />
                                    <small className="text-muted ms-3">{moment(r.created_at).format("D MMM YYYY")}</small>
                                  </div>
                                  <p className="mb-0 mt-1">{r.review_text}</p>
                                </div>
                              </div>
                            ))}

                            <hr />
                            {userId ? (
                              <form className="row g-3" onSubmit={submitReview}>
                                <div className="col-12">
                                  <h5 className="mb-0">{myReview ? "Update your review" : "Leave a review"}</h5>
                                  <small className="text-muted">Reviews can be posted by enrolled learners.</small>
                                </div>
                                <div className="col-md-4">
                                  <select
                                    className="form-select"
                                    value={reviewForm.rating}
                                    onChange={(e) => setReviewForm({ ...reviewForm, rating: e.target.value })}
                                  >
                                    {[5, 4, 3, 2, 1].map((v) => (
                                      <option key={v} value={v}>
                                        {"★".repeat(v)}{"☆".repeat(5 - v)} ({v}/5)
                                      </option>
                                    ))}
                                  </select>
                                </div>
                                <div className="col-12">
                                  <textarea
                                    className="form-control"
                                    rows={3}
                                    placeholder="What did you think of this course?"
                                    value={reviewForm.text}
                                    onChange={(e) => setReviewForm({ ...reviewForm, text: e.target.value })}
                                  />
                                </div>
                                <div className="col-12">
                                  <button type="submit" className="btn btn-primary" disabled={reviewBusy || !reviewForm.text.trim()}>
                                    {reviewBusy ? "Saving…" : myReview ? "Update review" : "Post review"}
                                  </button>
                                </div>
                              </form>
                            ) : (
                              <p className="text-muted mb-0">
                                <Link to={`/login/?next=/course-detail/${param.slug}/`}>Log in</Link> and enrol to leave a review.
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  {/* Main content END */}
                  {/* Right sidebar START */}
                  <div className="col-lg-4 pt-5 pt-lg-0">
                    <div className="row mb-5 mb-lg-0">
                      <div className="col-md-6 col-lg-12">
                        {/* Video START */}
                        <div className="card shadow p-2 mb-4 z-index-9">
                          <div className="overflow-hidden rounded-3">
                            <img
                              src={course.image}
                              className="card-img"
                              alt="course image"
                            />
                            {course.intro_video && (
                            <div
                              className="m-auto rounded-2 mt-2 d-flex justify-content-center align-items-center"
                              style={{ backgroundColor: "#ededed" }}
                            >
                              <button
                                type="button"
                                data-bs-toggle="modal"
                                data-bs-target="#introVideoModal"
                                className="btn btn-lg text-danger btn-round btn-white-shadow mb-0"
                              >
                                <i className="fas fa-play" />
                              </button>
                              <span
                                data-bs-toggle="modal"
                                data-bs-target="#introVideoModal"
                                className="fw-bold"
                                role="button"
                              >
                                Course Introduction Video
                              </span>

                              <div
                                className="modal fade"
                                id="introVideoModal"
                                tabIndex={-1}
                                aria-labelledby="introVideoModalLabel"
                              >
                                <div className="modal-dialog modal-lg">
                                  <div className="modal-content">
                                    <div className="modal-header">
                                      <h1 className="modal-title fs-5" id="introVideoModalLabel">
                                        Course introduction
                                      </h1>
                                      <button
                                        type="button"
                                        className="btn-close"
                                        data-bs-dismiss="modal"
                                        aria-label="Close"
                                      />
                                    </div>
                                    <div className="modal-body p-0">
                                      <div className="ratio ratio-16x9">
                                        <iframe
                                          src={course.intro_video}
                                          title="Course introduction video"
                                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                          allowFullScreen
                                        />
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                            )}
                          </div>
                          {/* Card body */}
                          <div className="card-body px-3">
                            {/* Info */}
                            <div className="d-flex justify-content-between align-items-center">
                              {/* Price and time */}
                              <div>
                                <div className="d-flex align-items-center">
                                  <h3 className="fw-bold mb-0 me-2">
                                    ${course.price}
                                  </h3>
                                </div>
                              </div>
                              {/* Share button with dropdown */}
                              <div className="dropdown">
                                {/* Share button */}
                                <a
                                  href="#"
                                  className="btn btn-sm btn-light rounded small"
                                  role="button"
                                  id="dropdownShare"
                                  data-bs-toggle="dropdown"
                                  aria-expanded="false"
                                >
                                  <i className="fas fa-fw fa-share-alt" />
                                </a>
                                {/* dropdown button */}
                                <ul
                                  className="dropdown-menu dropdown-w-sm dropdown-menu-end min-w-auto shadow rounded"
                                  aria-labelledby="dropdownShare"
                                >
                                  <li>
                                    <a className="dropdown-item" href="#">
                                      <i className="fab fa-twitter-square me-2" />
                                      Twitter
                                    </a>
                                  </li>
                                  <li>
                                    <a className="dropdown-item" href="#">
                                      <i className="fab fa-facebook-square me-2" />
                                      Facebook
                                    </a>
                                  </li>
                                  <li>
                                    <a className="dropdown-item" href="#">
                                      <i className="fab fa-linkedin me-2" />
                                      LinkedIn
                                    </a>
                                  </li>
                                  <li>
                                    <a className="dropdown-item" href="#">
                                      <i className="fas fa-copy me-2" />
                                      Copy link
                                    </a>
                                  </li>
                                </ul>
                              </div>
                            </div>
                            {/* Buttons */}
                            {course.is_free || Number(course.price) === 0 ? (
                              <div className="mt-3">
                                <button
                                  type="button"
                                  className="btn btn-success mb-0 w-100"
                                  disabled={enrolling}
                                  onClick={() => enrollFree(course?.course_id)}
                                >
                                  {enrolling ? (
                                    <>
                                      <i className="fas fa-spinner fa-spin"></i> Enrolling
                                    </>
                                  ) : (
                                    <>
                                      Enrol for free <i className="fas fa-arrow-right"></i>
                                    </>
                                  )}
                                </button>
                              </div>
                            ) : (
                            <div className="mt-3 d-sm-flex justify-content-sm-between ">
                              {addToCartBtn === "Add To Cart" && (
                                <button
                                  type="button"
                                  className="btn btn-primary mb-0 w-100 me-2"
                                  onClick={() => addToCart(course?.course_id)}
                                >
                                  <i className="fas fa-shopping-cart"></i> Add
                                  To Cart
                                </button>
                              )}

                              {addToCartBtn === "Added To Cart" && (
                                <button
                                  type="button"
                                  className="btn btn-primary mb-0 w-100 me-2"
                                  onClick={() =>
                                    addToCart(course.course_id)
                                  }
                                >
                                  <i className="fas fa-check-circle"></i> Added
                                  To Cart
                                </button>
                              )}

                              {addToCartBtn === "Adding To Cart" && (
                                <button
                                  type="button"
                                  className="btn btn-primary mb-0 w-100 me-2"
                                  onClick={() =>
                                    addToCart(course.course_id)
                                  }
                                >
                                  <i className="fas fa-spinner fa-spin"></i>{" "}
                                  Adding To Cart
                                </button>
                              )}
                              <Link
                                to="/cart/"
                                className="btn btn-success mb-0 w-100"
                              >
                                Enroll Now{" "}
                                <i className="fas fa-arrow-right"></i>
                              </Link>
                            </div>
                            )}
                          </div>
                        </div>
                        {/* Video END */}
                        {/* Course info START */}
                        <div className="card card-body shadow p-4 mb-4">
                          {/* Title */}
                          <h4 className="mb-3">This course includes</h4>
                          <ul className="list-group list-group-borderless">
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                              <span className="h6 fw-light mb-0">
                                <i className="fas fa-fw fa-book-open text-primary me-2" />
                                Lessons
                              </span>
                              <span>{course.total_lessons ?? 0}</span>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                              <span className="h6 fw-light mb-0">
                                <i className="fas fa-fw fa-layer-group text-primary me-2" />
                                Modules
                              </span>
                              <span>{course.total_sections ?? course.sections?.length ?? 0}</span>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                              <span className="h6 fw-light mb-0">
                                <i className="fas fa-fw fa-signal text-primary me-2" />
                                Level
                              </span>
                              <span className="text-capitalize">{course.level || "beginner"}</span>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                              <span className="h6 fw-light mb-0">
                                <i className="fas fa-fw fa-globe text-primary me-2" />
                                Language
                              </span>
                              <span>{course.language === "en" ? "English" : course.language}</span>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                              <span className="h6 fw-light mb-0">
                                <i className="fas fa-fw fa-calendar text-primary me-2" />
                                Published
                              </span>
                              <span>{moment(course.published_at || course.created_at).format("D MMM YYYY")}</span>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                              <span className="h6 fw-light mb-0">
                                <i className="fas fa-fw fa-medal text-primary me-2" />
                                Assessment
                              </span>
                              <span>Knowledge checks and graded practicals</span>
                            </li>
                          </ul>
                        </div>
                        {/* Course info END */}
                      </div>
                    </div>
                    {/* Row End */}
                  </div>
                  {/* Right sidebar END */}
                </div>
                {/* Row END */}
              </div>
            </section>
            {relatedCourses.length > 0 && (
              <section className="mb-5">
                <div className="container">
                  <div className="row mb-4 mt-3">
                    <div className="col-12">
                      <h2 className="mb-1 h1">Other programmes</h2>
                      <p>More DSN Research programmes you can enrol in.</p>
                    </div>
                  </div>
                  <div className="row">
                    {relatedCourses.map((rc) => (
                      <div className="col-lg-4 col-md-6 col-12 mb-4" key={rc.course_id}>
                        <div className="card card-hover h-100">
                          <Link to={`/course-detail/${rc.slug}/`}>
                            <img src={rc.thumbnail} alt={rc.title} className="card-img-top" />
                          </Link>
                          <div className="card-body">
                            <span className="badge bg-info text-capitalize">{rc.level}</span>
                            <h4 className="mb-2 mt-2 text-truncate-line-2">
                              <Link to={`/course-detail/${rc.slug}/`} className="text-inherit text-decoration-none text-dark">
                                {rc.title}
                              </Link>
                            </h4>
                            <small>By: {rc.instructor?.full_name}</small>
                            <br />
                            <small>{rc.total_lessons ?? 0} lessons</small>
                          </div>
                          <div className="card-footer d-flex justify-content-between align-items-center">
                            <h5 className="mb-0">{Number(rc.price) === 0 ? "Free" : `$${rc.price}`}</h5>
                            <Link to={`/course-detail/${rc.slug}/`} className="btn btn-primary btn-sm">
                              View programme <i className="fas fa-arrow-right ms-1" />
                            </Link>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            )}
          </>
        )}
      </>

      <BaseFooter />
    </>
  );
}

export default CourseDetail;
