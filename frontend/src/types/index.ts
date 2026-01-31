// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
}

export interface UserProfile {
  id: number;
  user: User;
  image: string | null;
  full_name: string;
  country: string | null;
  about: string | null;
  date: string;
}

export interface DecodedToken {
  token_type: string;
  exp: number;
  iat: number;
  jti: string;
  user_id: number;
  full_name: string;
  email: string;
  username: string;
}

// Auth Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  full_name: string;
  email: string;
  password: string;
  password2: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface AuthState {
  allUserData: DecodedToken | null;
  loading: boolean;
  user: () => { user_id: number; username: string } | null;
  setUser: (user: DecodedToken | null) => void;
  setLoading: (loading: boolean) => void;
  isLoggedIn: () => boolean;
}

// Course Types
export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  image: string | null;
  course_count: number;
}

export interface Course {
  id: number;
  course_id: string;
  title: string;
  slug: string;
  short_description: string | null;
  description: string;
  thumbnail: string | null;
  intro_video: string | null;
  category: Category | null;
  language: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  tags: string | null;
  instructor: User;
  price: number;
  original_price: number | null;
  is_free: boolean;
  requirements: string | null;
  what_you_learn: string | null;
  target_audience: string | null;
  status: 'draft' | 'review' | 'published' | 'archived';
  is_featured: boolean;
  published_at: string | null;
  total_sections: number;
  total_lessons: number;
  total_duration: number;
  total_students: number;
  total_reviews: number;
  average_rating: number;
  discount_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface Section {
  id: number;
  section_id: string;
  course: number;
  title: string;
  description: string | null;
  order: number;
  total_lessons: number;
  total_duration: number;
  lessons: Lesson[];
}

export interface Lesson {
  id: number;
  lesson_id: string;
  section: number;
  title: string;
  description: string | null;
  lesson_type: 'video' | 'text' | 'quiz' | 'assignment' | 'resource';
  content: string | null;
  video_url: string | null;
  video_file: string | null;
  duration: number;
  order: number;
  is_free_preview: boolean;
  is_published: boolean;
}

// Enrollment Types
export interface Enrollment {
  id: number;
  enrollment_id: string;
  student: User;
  course: Course;
  status: 'active' | 'completed' | 'dropped' | 'expired';
  progress_percentage: number;
  lessons_completed: number;
  enrolled_at: string;
  last_accessed: string | null;
  completed_at: string | null;
  certificate_issued: boolean;
  certificate_id: string | null;
}

export interface LessonProgress {
  id: number;
  enrollment: number;
  lesson: number;
  is_completed: boolean;
  completed_at: string | null;
  time_spent: number;
  last_position: number;
}

// Cart Types
export interface CartItem {
  id: number;
  cart: number;
  course: Course;
  price: number;
  added_at: string;
}

export interface Cart {
  id: number;
  cart_id: string;
  user: number | null;
  items: CartItem[];
  total: number;
  item_count: number;
}

// Order Types
export interface OrderItem {
  id: number;
  order: number;
  course: Course;
  instructor: User;
  price: number;
}

export interface Order {
  id: number;
  order_id: string;
  student: User;
  items: OrderItem[];
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded';
  subtotal: number;
  tax: number;
  discount: number;
  total: number;
  coupon: string | null;
  payment_method: 'stripe' | 'paypal' | 'free';
  payment_id: string | null;
  created_at: string;
  completed_at: string | null;
}

// Review Types
export interface CourseReview {
  id: number;
  review_id: string;
  student: User;
  course: number;
  rating: 1 | 2 | 3 | 4 | 5;
  review_text: string;
  is_approved: boolean;
  helpful_count: number;
  created_at: string;
  updated_at: string;
}

// Q&A Types
export interface Question {
  id: number;
  question_id: string;
  course: number;
  student: User;
  lesson: number | null;
  title: string;
  content: string;
  is_resolved: boolean;
  answers: Answer[];
  created_at: string;
}

export interface Answer {
  id: number;
  answer_id: string;
  question: number;
  user: User;
  content: string;
  is_accepted: boolean;
  created_at: string;
}

// Notification Types
export interface Notification {
  id: number;
  user: number;
  notification_type: 'enrollment' | 'review' | 'order' | 'course' | 'system';
  title: string;
  message: string;
  is_read: boolean;
  course: number | null;
  order: number | null;
  created_at: string;
}

// Coupon Types
export interface Coupon {
  id: number;
  code: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number;
  instructor: number | null;
  is_active: boolean;
  is_valid: boolean;
  valid_from: string;
  valid_until: string;
}

// API Response Types
export interface APIResponse<T> {
  data: T;
  error: string | null;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
