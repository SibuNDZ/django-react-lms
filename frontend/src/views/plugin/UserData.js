import Cookie from "js-cookie";
import jwtDecode from "jwt-decode";

function UserData() {
  const access_token = Cookie.get("access_token");

  if (!access_token) {
    return null;
  }

  try {
    return jwtDecode(access_token);
  } catch (error) {
    return null;
  }
}

export default UserData;
