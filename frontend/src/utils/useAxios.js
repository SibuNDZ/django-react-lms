import axios from "axios";
import { getRefreshedToken, isAccessTokenExpired, setAuthUser } from "./auth";
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
      // Token refresh failed - user needs to login again
      console.log("Token refresh failed, user needs to re-authenticate");
    }
    return req;
  });

  return axiosInstance;
};

export default useAxios;
