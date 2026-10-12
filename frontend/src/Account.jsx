import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

function Account() {
    const { user, isAuthenticated, loading, logout, bookmarks, fetchBookmarks, toggleBookmark } = useAuth();
    const [fetchingBookmarks, setFetchingBookmarks] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            setFetchingBookmarks(true);
            fetchBookmarks().finally(() => setFetchingBookmarks(false));
        }
    }, [isAuthenticated]);

    if (loading) {
        return (
            <div className="page account-page">
                <h2>Account & Learning Hub</h2>
                <p>Loading your profile...</p>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="page account-page">
                <div className="account-empty-card">
                    <span className="auth-badge">Account Required</span>
                    <h2>Sign in to access your Learning Hub</h2>
                    <p>
                        Track your daily current-affairs reading streaks, save important articles, and access your personalized knowledge dashboard.
                    </p>
                    <div className="account-empty-actions">
                        <Link to="/login">
                            <button className="auth-submit-btn">Sign In / Create Account</button>
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    const initials = user?.name
        ? user.name
              .split(" ")
              .map((n) => n[0])
              .join("")
              .toUpperCase()
              .slice(0, 2)
        : "IQ";

    const formattedDate = user?.created_at
        ? new Date(user.created_at).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric"
          })
        : "Recently";

    const handleLogout = async () => {
        await logout();
        navigate("/");
    };

    return (
        <div className="page account-page">
            {/* Profile Overview Card */}
            <div className="profile-card">
                <div className="profile-left">
                    <div className="profile-avatar">{initials}</div>
                    <div className="profile-details">
                        <h2>{user?.name}</h2>
                        <p className="profile-email">{user?.email}</p>
                        <span className="profile-member-date">
                            Member since {formattedDate}
                        </span>
                    </div>
                </div>
                <div className="profile-right">
                    <button onClick={handleLogout} className="logout-btn">
                        Sign Out
                    </button>
                </div>
            </div>

            {/* Learning Hub Statistics */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">🔥</div>
                    <div className="stat-content">
                        <h3>{user?.study_streak || 1} Days</h3>
                        <p>Current Study Streak</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">🔖</div>
                    <div className="stat-content">
                        <h3>{bookmarks.length}</h3>
                        <p>Saved Articles</p>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">🧠</div>
                    <div className="stat-content">
                        <h3>Daily Learner</h3>
                        <p>Knowledge Level</p>
                    </div>
                </div>
            </div>

            {/* Saved / Bookmarked Affairs Section */}
            <section className="saved-affairs-section">
                <div className="section-title-row">
                    <div>
                        <h2>🔖 Saved Affairs & Notes</h2>
                        <p>Key takeaways and articles you saved for quick revision.</p>
                    </div>
                </div>

                {fetchingBookmarks ? (
                    <p className="loading-text">Loading saved articles...</p>
                ) : bookmarks.length === 0 ? (
                    <div className="empty-bookmarks-box">
                        <p>You haven't bookmarked any affairs yet.</p>
                        <p className="empty-hint">
                            Click the <strong>⭐ Save</strong> button on any article in Today's Affairs to keep it handy here.
                        </p>
                        <Link to="/affairs">
                            <button className="browse-affairs-btn">Explore Today's Affairs</button>
                        </Link>
                    </div>
                ) : (
                    <div className="news-grid">
                        {bookmarks.map((item) => (
                            <article className="news-card" key={item.id}>
                                <div className="card-top-row">
                                    <span className="category">{item.category}</span>
                                    <button
                                        className="remove-bookmark-btn"
                                        onClick={() => toggleBookmark(item.id)}
                                        title="Remove from saved"
                                    >
                                        Remove ✕
                                    </button>
                                </div>

                                <h3>{item.title}</h3>
                                <p>{item.summary}</p>

                                {item.remember && item.remember.length > 0 && (
                                    <div className="remember">
                                        <strong>⭐ Remember:</strong>
                                        <ul>
                                            {item.remember.map((fact, index) => (
                                                <li key={index}>{fact}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {item.source_url && (
                                    <div className="source">
                                        Source:{" "}
                                        <a
                                            href={item.source_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {item.source || "Read Article"}
                                        </a>
                                    </div>
                                )}
                            </article>
                        ))}
                    </div>
                )}
            </section>
        </div>
    );
}

export default Account;
