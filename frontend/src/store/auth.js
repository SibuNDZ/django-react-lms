import { create } from "zustand";
import { mountStoreDevtool } from "simple-zustand-devtools";

const useAuthStore = create((set, get) => ({
  allUserData: null,
  loading: false,

  user: () => {
    const data = get().allUserData;
    if (!data) return null;
    return {
      user_id: data.user_id || null,
      username: data.username || null,
      email: data.email || null,
      full_name: data.full_name || null,
      role: data.role || "student",
    };
  },

  setUser: (user) =>
    set({
      allUserData: user,
    }),

  setLoading: (loading) => set({ loading }),

  isLoggedIn: () => get().allUserData !== null,

  isInstructor: () => get().allUserData?.role === "instructor",
}));


if (import.meta.env.DEV) {
  mountStoreDevtool("Store", useAuthStore);
}

export { useAuthStore };
