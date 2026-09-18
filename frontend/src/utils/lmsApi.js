import useAxios from "./useAxios";
import apiInstance from "./axios";
import CartId from "../views/plugin/CartId";

export const asList = (data) => {
  if (!data) return [];
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.results)) return data.results;
  if (Array.isArray(data.items)) return data.items;
  return [];
};

export const courseImage = (course) =>
  course?.thumbnail || course?.image || "";

export const cartItemCount = (data) => {
  if (!data) return 0;
  if (typeof data.item_count === "number") return data.item_count;
  if (typeof data.count === "number") return data.count;
  if (Array.isArray(data.items)) return data.items.length;
  if (Array.isArray(data)) return data.length;
  return 0;
};

export async function fetchCartCount(cartId = CartId()) {
  const res = await apiInstance.get(`cart/${cartId}/`);
  return cartItemCount(res.data);
}

export async function addCourseToCart(courseId, cartId = CartId()) {
  const client = useAxios();
  await client.post("cart/add/", {
    course_id: courseId,
    cart_id: cartId,
  });
  return fetchCartCount(cartId);
}
