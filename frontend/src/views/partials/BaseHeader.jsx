import React, { useContext, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CartContext } from "../plugin/Context";
import { useAuthStore } from "../../store/auth";

function BaseHeader() {
    const [cartCount, setCartCount] = useContext(CartContext);
    const [searchQuery, setSearchQuery] = useState("");
    const navigate = useNavigate();

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search/?search=${searchQuery}`);
        }
    };

    const [isLoggedIn, user] = useAuthStore((state) => [state.isLoggedIn, state.user]);

    const getUserInitials = () => {
        if (user?.full_name) {
            const names = user.full_name.split(' ');
            return names.map(n => n[0]).join('').toUpperCase().slice(0, 2);
        }
        return user?.username?.[0]?.toUpperCase() || 'U';
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-dsn sticky-top">
            <div className="container">
                {/* Logo */}
                <Link className="navbar-brand d-flex align-items-center" to="/">
                    <span style={{ color: '#5624d0', fontWeight: 800 }}>DSN</span>
                    <span style={{ color: '#1c1d1f', fontWeight: 600, marginLeft: '4px' }}>Research</span>
                </Link>

                {/* Mobile Toggle */}
                <button
                    className="navbar-toggler border-0"
                    type="button"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarMain"
                    aria-controls="navbarMain"
                    aria-expanded="false"
                    aria-label="Toggle navigation"
                >
                    <span className="navbar-toggler-icon"></span>
                </button>

                <div className="collapse navbar-collapse" id="navbarMain">
                    {/* Categories Dropdown */}
                    <div className="nav-item dropdown me-2">
                        <a
                            className="nav-link dropdown-toggle"
                            href="#"
                            role="button"
                            data-bs-toggle="dropdown"
                            aria-expanded="false"
                            style={{ fontWeight: 600 }}
                        >
                            Categories
                        </a>
                        <ul className="dropdown-menu dropdown-menu-start" style={{ minWidth: '220px' }}>
                            <li>
                                <Link className="dropdown-item py-2" to="/search/?search=prompting">
                                    <i className="fas fa-robot me-2 text-primary"></i>
                                    Prompt Engineering
                                </Link>
                            </li>
                            <li>
                                <Link className="dropdown-item py-2" to="/search/?search=agentic">
                                    <i className="fas fa-brain me-2 text-purple"></i>
                                    Agentic AI
                                </Link>
                            </li>
                            <li>
                                <Link className="dropdown-item py-2" to="/search/?search=fullstack">
                                    <i className="fas fa-layer-group me-2 text-success"></i>
                                    Full Stack Development
                                </Link>
                            </li>
                            <li><hr className="dropdown-divider" /></li>
                            <li>
                                <Link className="dropdown-item py-2" to="/search/?search=python">
                                    <i className="fab fa-python me-2 text-info"></i>
                                    Python
                                </Link>
                            </li>
                            <li>
                                <Link className="dropdown-item py-2" to="/search/?search=javascript">
                                    <i className="fab fa-js-square me-2 text-warning"></i>
                                    JavaScript
                                </Link>
                            </li>
                            <li>
                                <Link className="dropdown-item py-2" to="/search/?search=react">
                                    <i className="fab fa-react me-2 text-info"></i>
                                    React
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Search Bar */}
                    <form className="d-flex flex-grow-1 mx-lg-4 my-2 my-lg-0" onSubmit={handleSearchSubmit}>
                        <div className="search-bar-dsn w-100">
                            <i className="fas fa-search search-icon"></i>
                            <input
                                type="search"
                                placeholder="Search for courses..."
                                aria-label="Search"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    </form>

                    {/* Right Side Navigation */}
                    <ul className="navbar-nav align-items-center">
                        {isLoggedIn() ? (
                            <>
                                {/* My Learning */}
                                <li className="nav-item">
                                    <Link className="nav-link" to="/student/courses/" style={{ fontWeight: 600 }}>
                                        My Learning
                                    </Link>
                                </li>

                                {/* Instructor Dropdown */}
                                <li className="nav-item dropdown">
                                    <a
                                        className="nav-link dropdown-toggle"
                                        href="#"
                                        role="button"
                                        data-bs-toggle="dropdown"
                                        aria-expanded="false"
                                        style={{ fontWeight: 600 }}
                                    >
                                        Teach
                                    </a>
                                    <ul className="dropdown-menu dropdown-menu-end">
                                        <li>
                                            <Link className="dropdown-item" to="/instructor/dashboard/">
                                                <i className="fas fa-chart-line me-2"></i> Dashboard
                                            </Link>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/instructor/courses/">
                                                <i className="fas fa-book me-2"></i> My Courses
                                            </Link>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/instructor/create-course/">
                                                <i className="fas fa-plus-circle me-2"></i> Create Course
                                            </Link>
                                        </li>
                                        <li><hr className="dropdown-divider" /></li>
                                        <li>
                                            <Link className="dropdown-item" to="/instructor/earning/">
                                                <i className="fas fa-dollar-sign me-2"></i> Earnings
                                            </Link>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/instructor/reviews/">
                                                <i className="fas fa-star me-2"></i> Reviews
                                            </Link>
                                        </li>
                                    </ul>
                                </li>

                                {/* Wishlist */}
                                <li className="nav-item">
                                    <Link className="nav-link position-relative" to="/student/wishlist/">
                                        <i className="fas fa-heart" style={{ fontSize: '18px' }}></i>
                                    </Link>
                                </li>

                                {/* Cart */}
                                <li className="nav-item">
                                    <Link className="nav-link position-relative" to="/cart/">
                                        <i className="fas fa-shopping-cart" style={{ fontSize: '18px' }}></i>
                                        {cartCount > 0 && (
                                            <span
                                                className="position-absolute translate-middle badge rounded-pill"
                                                style={{
                                                    top: '8px',
                                                    right: '-4px',
                                                    backgroundColor: '#a435f0',
                                                    fontSize: '10px'
                                                }}
                                            >
                                                {cartCount}
                                            </span>
                                        )}
                                    </Link>
                                </li>

                                {/* User Dropdown */}
                                <li className="nav-item dropdown ms-2">
                                    <a
                                        className="nav-link dropdown-toggle d-flex align-items-center p-0"
                                        href="#"
                                        role="button"
                                        data-bs-toggle="dropdown"
                                        aria-expanded="false"
                                    >
                                        <div className="user-avatar">
                                            {getUserInitials()}
                                        </div>
                                    </a>
                                    <ul className="dropdown-menu dropdown-menu-end" style={{ minWidth: '200px' }}>
                                        <li className="px-3 py-2 border-bottom">
                                            <div className="fw-bold">{user?.full_name || user?.username}</div>
                                            <small className="text-muted">{user?.email}</small>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/student/dashboard/">
                                                <i className="fas fa-tachometer-alt me-2"></i> Dashboard
                                            </Link>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/student/courses/">
                                                <i className="fas fa-graduation-cap me-2"></i> My Courses
                                            </Link>
                                        </li>
                                        <li>
                                            <Link className="dropdown-item" to="/student/profile/">
                                                <i className="fas fa-user me-2"></i> Profile
                                            </Link>
                                        </li>
                                        <li><hr className="dropdown-divider" /></li>
                                        <li>
                                            <Link className="dropdown-item" to="/logout/">
                                                <i className="fas fa-sign-out-alt me-2"></i> Log Out
                                            </Link>
                                        </li>
                                    </ul>
                                </li>
                            </>
                        ) : (
                            <>
                                {/* Cart for non-logged in users */}
                                <li className="nav-item">
                                    <Link className="nav-link position-relative" to="/cart/">
                                        <i className="fas fa-shopping-cart" style={{ fontSize: '18px' }}></i>
                                        {cartCount > 0 && (
                                            <span
                                                className="position-absolute translate-middle badge rounded-pill"
                                                style={{
                                                    top: '8px',
                                                    right: '-4px',
                                                    backgroundColor: '#a435f0',
                                                    fontSize: '10px'
                                                }}
                                            >
                                                {cartCount}
                                            </span>
                                        )}
                                    </Link>
                                </li>

                                {/* Login Button */}
                                <li className="nav-item ms-2">
                                    <Link
                                        to="/login/"
                                        className="btn btn-dsn-outline btn-sm"
                                        style={{ padding: '8px 16px' }}
                                    >
                                        Log In
                                    </Link>
                                </li>

                                {/* Sign Up Button */}
                                <li className="nav-item ms-2">
                                    <Link
                                        to="/register/"
                                        className="btn btn-dsn-primary btn-sm"
                                        style={{ padding: '8px 16px' }}
                                    >
                                        Sign Up
                                    </Link>
                                </li>
                            </>
                        )}
                    </ul>
                </div>
            </div>
        </nav>
    );
}

export default BaseHeader;
