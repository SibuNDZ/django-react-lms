import { Navigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

const PrivateRoute = ({ children, role }) => {
  const user = useAuthStore((state) => state.allUserData);

  if (!user) {
    return <Navigate to="/login/" replace />;
  }

  if (role === "instructor" && user.role !== "instructor") {
    return <Navigate to="/student/dashboard/" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;
