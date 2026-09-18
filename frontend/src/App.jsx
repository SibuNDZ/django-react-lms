import { useState, useEffect } from "react";
import { Route, Routes, BrowserRouter } from "react-router-dom";

import { CartContext, ProfileContext } from "./views/plugin/Context";
import CartId from "./views/plugin/CartId";

import MainWrapper from "./layouts/MainWrapper";
import PrivateRoute from "./layouts/PrivateRoute";

import Register from "../src/views/auth/Register";
import Login from "../src/views/auth/Login";
import Logout from "./views/auth/Logout";
import ForgotPassword from "./views/auth/ForgotPassword";
import CreateNewPassword from "./views/auth/CreateNewPassword";

import Index from "./views/base/Index";
import CourseDetail from "./views/base/CourseDetail";
import Cart from "./views/base/Cart";
import Checkout from "./views/base/Checkout";
import Success from "./views/base/Success";
import Search from "./views/base/Search";

import StudentDashboard from "./views/student/Dashboard";
import StudentCourses from "./views/student/Courses";
import StudentCourseDetail from "./views/student/CourseDetail";
import Wishlist from "./views/student/Wishlist";
import StudentProfile from "./views/student/Profile";
import useAxios from "./utils/useAxios";
import StudentChangePassword from "./views/student/ChangePassword";
import Dashboard from "./views/instructor/Dashboard";
import Courses from "./views/instructor/Courses";
import Review from "./views/instructor/Review";
import Students from "./views/instructor/Students";
import Earning from "./views/instructor/Earning";
import Orders from "./views/instructor/Orders";
import Coupon from "./views/instructor/Coupon";
import TeacherNotification from "./views/instructor/TeacherNotification";
import QA from "./views/instructor/QA";
import ChangePassword from "./views/instructor/ChangePassword";
import Profile from "./views/instructor/Profile";
import CourseCreate from "./views/instructor/CourseCreate";
import CourseEdit from "./views/instructor/CourseEdit";
import { useAuthStore } from "./store/auth";
import { fetchCartCount } from "./utils/lmsApi";


function App() {
  const [cartCount, setCartCount] = useState(0);
  const [profile, setProfile] = useState({});
  const user = useAuthStore((state) => state.allUserData);

  useEffect(() => {
    fetchCartCount(CartId())
      .then(setCartCount)
      .catch(() => setCartCount(0));

    if (!user) {
      return;
    }

    useAxios()
      .get(`user/profile/`)
      .then((res) => {
        setProfile(res.data);
      })
      .catch(() => {});
  }, [user]);

  return (
    <CartContext.Provider value={[cartCount, setCartCount]}>
      <ProfileContext.Provider value={[profile, setProfile]}>
        <BrowserRouter>
          <MainWrapper>
            <Routes>
              <Route path="/register/" element={<Register />} />
              <Route path="/login/" element={<Login />} />
              <Route path="/logout/" element={<Logout />} />
              <Route path="/forgot-password/" element={<ForgotPassword />} />
              <Route
                path="/create-new-password/"
                element={<CreateNewPassword />}
              />

              {/* Base Routes */}
              <Route path="/" element={<Index />} />
              <Route path="/course-detail/:slug/" element={<CourseDetail />} />
              <Route path="/cart/" element={<Cart />} />
              <Route
                path="/checkout/:order_oid/"
                element={
                  <PrivateRoute>
                    <Checkout />
                  </PrivateRoute>
                }
              />
              <Route
                path="/payment-success/:order_oid/"
                element={
                  <PrivateRoute>
                    <Success />
                  </PrivateRoute>
                }
              />
              <Route path="/search/" element={<Search />} />

              {/* Student Routes */}
              <Route
                path="/student/dashboard/"
                element={
                  <PrivateRoute>
                    <StudentDashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/student/courses/"
                element={
                  <PrivateRoute>
                    <StudentCourses />
                  </PrivateRoute>
                }
              />
              <Route
                path="/student/courses/:enrollment_id/"
                element={
                  <PrivateRoute>
                    <StudentCourseDetail />
                  </PrivateRoute>
                }
              />
              <Route
                path="/student/wishlist/"
                element={
                  <PrivateRoute>
                    <Wishlist />
                  </PrivateRoute>
                }
              />
              <Route
                path="/student/profile/"
                element={
                  <PrivateRoute>
                    <StudentProfile />
                  </PrivateRoute>
                }
              />
              <Route
                path="/student/change-password/"
                element={
                  <PrivateRoute>
                    <StudentChangePassword />
                  </PrivateRoute>
                }
              />

              {/* Instructor Routes */}
              <Route
                path="/instructor/dashboard/"
                element={
                  <PrivateRoute role="instructor">
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/courses/"
                element={
                  <PrivateRoute role="instructor">
                    <Courses />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/reviews/"
                element={
                  <PrivateRoute role="instructor">
                    <Review />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/students/"
                element={
                  <PrivateRoute role="instructor">
                    <Students />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/earning/"
                element={
                  <PrivateRoute role="instructor">
                    <Earning />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/orders/"
                element={
                  <PrivateRoute role="instructor">
                    <Orders />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/coupon/"
                element={
                  <PrivateRoute role="instructor">
                    <Coupon />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/notifications/"
                element={
                  <PrivateRoute role="instructor">
                    <TeacherNotification />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/question-answer/"
                element={
                  <PrivateRoute role="instructor">
                    <QA />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/change-password/"
                element={
                  <PrivateRoute role="instructor">
                    <ChangePassword />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/profile/"
                element={
                  <PrivateRoute role="instructor">
                    <Profile />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/create-course/"
                element={
                  <PrivateRoute role="instructor">
                    <CourseCreate />
                  </PrivateRoute>
                }
              />
              <Route
                path="/instructor/edit-course/:course_id/"
                element={
                  <PrivateRoute role="instructor">
                    <CourseEdit />
                  </PrivateRoute>
                }
              />
            </Routes>
          </MainWrapper>
        </BrowserRouter>
      </ProfileContext.Provider>
    </CartContext.Provider>
  );
}

export default App;
