import { useEffect, useState, useContext } from "react";
import BaseHeader from "../partials/BaseHeader";
import BaseFooter from "../partials/BaseFooter";
import { Link, useSearchParams } from "react-router-dom";
import Rater from "react-rater";
import "react-rater/lib/react-rater.css";

import useAxios from "../../utils/useAxios";
import CartId from "../plugin/CartId";
import GetCurrentAddress from "../plugin/UserCountry";
import UserData from "../plugin/UserData";
import Toast from "../plugin/Toast";
import { CartContext } from "../plugin/Context";
import { addCourseToCart } from "../../utils/lmsApi";

function Search() {
  const [courses, setCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [cartCount, setCartCount] = useContext(CartContext);

  const country = GetCurrentAddress().country;
  const userId = UserData()?.user_id;
  const cartId = CartId();

  const [params] = useSearchParams();
  const urlSearch = params.get("search") || "";
  const urlCategory = params.get("category") || "";

  const fetchCourse = async () => {
    setIsLoading(true);
    try {
      const query = new URLSearchParams();
      if (urlSearch) query.set("search", urlSearch);
      if (urlCategory) query.set("category", urlCategory);
      query.set("page_size", "50");
      const res = await useAxios().get(`/courses/?${query.toString()}`);
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

  useEffect(() => {
    fetchCourse();
    setSearchQuery(urlSearch);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [urlSearch, urlCategory]);

  const addToCart = async (courseId) => {
    try {
      const count = await addCourseToCart(courseId, CartId());
      Toast().fire({
        title: "Added To Cart",
        icon: "success",
      });
      setCartCount(count);
    } catch (error) {
      console.log(error);
    }
  };

  // Search Feature (typing filters the loaded list client-side)

  const handleSeach = (e) => {
    const query = e.target.value.toLowerCase();
    setSearchQuery(query);

    if (query === "") {
      fetchCourse();
    } else {
      const course = courses.filter((course) => {
        return course.title.toLowerCase().includes(query);
      });
      setCourses(course);
    }
  };

  return (
    <>
      <BaseHeader />

      <section className="mb-5" style={{ marginTop: "100px" }}>
        <div className="container mb-lg-8 ">
          <div className="row mb-5 mt-3">
            {/* col */}
            <div className="col-12">
              <div className="mb-6">
                <h2 className="mb-1 h1">
                  {urlCategory
                    ? `Programmes in ${urlCategory.replace(/-/g, " ")}`
                    : searchQuery
                    ? `Showing results for "${searchQuery}"`
                    : "All programmes"}
                </h2>
              </div>
            </div>
            <div className="row">
              <div className="col-lg-6">
                <input
                  type="text"
                  className="form-control lg mt-3"
                  placeholder="Search Courses..."
                  name=""
                  id=""
                  onChange={handleSeach}
                />
              </div>
            </div>
          </div>
          <div className="row">
            <div className="col-md-12">
              <div className="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
                {courses?.map((c, index) => (
                  <div className="col">
                    {/* Card */}
                    <div className="card card-hover">
                      <Link to={`/course-detail/${c.slug}/`}>
                        <img
                          src={c.thumbnail || c.image}
                          alt="course"
                          className="card-img-top"
                          style={{
                            width: "100%",
                            height: "200px",
                            objectFit: "cover",
                          }}
                        />
                      </Link>
                      {/* Card Body */}
                      <div className="card-body">
                        <div className="d-flex justify-content-between align-items-center mb-3">
                          <div>
                            <span className="badge bg-info">{c.level}</span>
                            <span className="badge bg-success ms-2">
                              {c.language}
                            </span>
                          </div>
                          <a href="#" className="fs-5">
                            <i className="fas fa-heart text-danger align-middle" />
                          </a>
                        </div>
                        <h4 className="mb-2 text-truncate-line-2 ">
                          <Link
                            to={`/course-detail/${c.slug}/`}
                            className="text-inherit text-decoration-none text-dark fs-5"
                          >
                            {c.title}
                          </Link>
                        </h4>
                        <small>By: {c.instructor?.full_name || c.teacher?.full_name}</small> <br />
                        <small>
                          {c.total_students ?? c.students?.length ?? 0} Student
                          {(c.total_students ?? c.students?.length ?? 0) !== 1 && "s"}
                        </small>{" "}
                        <br />
                        <div className="lh-1 mt-3 d-flex">
                          <span className="align-text-top">
                            <span className="fs-6">
                              <Rater total={5} rating={c.average_rating || 0} />
                            </span>
                          </span>
                          <span className="text-warning">
                            {Number(c.average_rating) > 0 ? Number(c.average_rating).toFixed(1) : "New"}
                          </span>
                          <span className="fs-6 ms-2">
                            ({c.total_reviews ?? c.reviews?.length ?? 0} Reviews)
                          </span>
                        </div>
                      </div>
                      {/* Card Footer */}
                      <div className="card-footer">
                        <div className="row align-items-center g-0">
                          <div className="col">
                            <h5 className="mb-0">${c.price}</h5>
                          </div>
                          <div className="col-auto">
                            <button
                              type="button"
                              onClick={() => addToCart(c.course_id)}
                              className="text-inherit text-decoration-none btn btn-primary me-2"
                            >
                              <i className="fas fa-shopping-cart text-primary text-white" />
                            </button>
                            <Link
                              to={`/course-detail/${c.slug}/`}
                              className="text-inherit text-decoration-none btn btn-primary"
                            >
                              {Number(c.price) === 0 ? "Enrol free" : "Enroll Now"}{" "}
                              <i className="fas fa-arrow-right text-primary align-middle me-2 text-white" />
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <nav className="d-flex mt-5">
                <ul className="pagination">
                  <li className="">
                    <button className="page-link me-1">
                      <i className="ci-arrow-left me-2" />
                      Previous
                    </button>
                  </li>
                </ul>
                <ul className="pagination">
                  <li key={1} className="active">
                    <button className="page-link">1</button>
                  </li>
                </ul>
                <ul className="pagination">
                  <li className={`totalPages`}>
                    <button className="page-link ms-1">
                      Next
                      <i className="ci-arrow-right ms-3" />
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </section>

      <section className="my-8 py-lg-8">
        {/* container */}
        <div className="container">
          {/* row */}
          <div className="row align-items-center bg-primary gx-0 rounded-3 mt-5">
            {/* col */}
            <div className="col-lg-6 col-12 d-none d-lg-block">
              <div className="d-flex justify-content-center pt-4">
                {/* img */}
                <div className="position-relative">
                  <img
                    src="https://geeksui.codescandy.com/geeks/assets/images/png/cta-instructor-1.png"
                    alt="image"
                    className="img-fluid mt-n8"
                  />
                  <div className="ms-n8 position-absolute bottom-0 start-0 mb-6">
                    <img
                      src="https://geeksui.codescandy.com/geeks/assets/images/svg/dollor.svg"
                      alt="dollor"
                    />
                  </div>
                  {/* img */}
                  <div className="me-n4 position-absolute top-0 end-0">
                    <img
                      src="https://geeksui.codescandy.com/geeks/assets/images/svg/graph.svg"
                      alt="graph"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="col-lg-5 col-12">
              <div className="text-white p-5 p-lg-0">
                {/* text */}
                <h2 className="h1 text-white">Become an instructor today</h2>
                <p className="mb-0">
                  Instructors from around the world teach millions of students
                  on Geeks. We provide the tools and skills to teach what you
                  love.
                </p>
                <a href="#" className="btn bg-white text-dark fw-bold mt-4">
                  Start Teaching Today <i className="fas fa-arrow-right"></i>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <BaseFooter />
    </>
  );
}

export default Search;
