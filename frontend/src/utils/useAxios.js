import axios from "axios";
import { getRefreshedToken, isAccessTokenExpired, logout, setAuthUser } from "./auth";
import { API_BASE_URL } from "./constants";
import Cookies from "js-cookie";

const useAxios = () => {
  const accessToken = Cookies.get("access_token");
  const refreshToken = Cookies.get("refresh_token");

  const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : {},
  });

  axiosInstance.interceptors.request.use(async (req) => {
    // Skip token refresh if no tokens exist (user not logged in)
    if (!accessToken || !refreshToken) {
      return req;
    }

    // If access token is still valid, proceed with request
    if (!isAccessTokenExpired(accessToken)) {
      return req;
    }

    // Try to refresh the token
    try {
      const response = await getRefreshedToken(refreshToken);
      setAuthUser(response.access, response.refresh);
      req.headers.Authorization = `Bearer ${response.access}`;
    } catch (error) {
      // The refresh token is gone or blacklisted: the session is over. Clear
      // it so the app stops sending requests that can only get 401, and send
      // the user to log in again.
      logout();
      if (!window.location.pathname.startsWith("/login")) {
        window.location.assign(`/login/?next=${encodeURIComponent(window.location.pathname)}`);
      }
      throw error;
    }
    return req;
  });

  return axiosInstance;
};

export default useAxios;
