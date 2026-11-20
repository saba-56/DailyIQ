
import axios from "axios";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { API_BASE } from "./config";

const CATEGORIES = [
    { label: "All News", value: "All", icon: "🌐" },
    { label: "National", value: "National", icon: "🇮🇳" },
    { label: "Sports", value: "Sports", icon: "🏏" },
    { label: "Technology", value: "Technology", icon: "💻" },
    { label: "Economy", value: "Economy", icon: "📈" },
    { label: "Science", value: "Science", icon: "🔬" },
    { label: "Politics", value: "Politics", icon: "🏛️" },
    { label: "Education", value: "Education", icon: "🎓" },
    { label: "Environment", value: "Environment", icon: "🌱" },
];

function Affairs() {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [refreshFeedback, setRefreshFeedback] = useState("");
    const [error, setError] = useState("");
    const [selectedDay, setSelectedDay] = useState("today");
    const [selectedCategory, setSelectedCategory] = useState("All");

    const { bookmarkedIds, toggleBookmark, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleBookmarkClick = async (affairId) => {
        if (!isAuthenticated) {
            navigate("/login");
            return;
        }

        await toggleBookmark(affairId);
    };

    const fetchNews = useCallback(
        async (dayToFetch = selectedDay, categoryToFetch = selectedCategory) => {
            setLoading(true);
            setError("");

            try {
                const categoryParam =
                    categoryToFetch && categoryToFetch !== "All"
                        ? `&category=${encodeURIComponent(categoryToFetch)}`
                        : "";

                const response = await axios.get(
                    `${API_BASE}/latest-affairs?day=${dayToFetch}${categoryParam}`,
                    { timeout: 8000 }
                );

                if (!Array.isArray(response.data)) {
                    throw new Error("The API returned an unexpected response.");
                }

                setNews(response.data);
            } catch (err) {
                console.error("Error fetching affairs:", err);

                if (err.code === "ECONNABORTED") {
                    setError("Request timed out. The backend server took too long to respond.");
                } else if (err.response) {
                    setError(`API error: ${err.response.status}`);
                } else if (
                    err.message === "The API returned an unexpected response."
                ) {
                    setError(err.message);
                } else {
                    setError(
                        "Cannot connect to backend at http://127.0.0.1:8000. Please verify that your backend server is running."
                    );
                }

                setNews([]);
            } finally {
                setLoading(false);
            }
        },
        [selectedDay, selectedCategory]
    );

    useEffect(() => {
        fetchNews(selectedDay, selectedCategory);
    }, [selectedDay, selectedCategory, fetchNews]);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        setRefreshFeedback("");

        try {
            const response = await axios.post(
                `${API_BASE}/refresh-news`,
                {},
                { timeout: 15000 }
            );
            const data = response.data;

            if (data?.gnews_error) {
                setRefreshFeedback("News source limit reached or unavailable.");
            } else if (data && typeof data.added === "number") {
                if (data.added > 0) {
                    setRefreshFeedback(`Fetched ${data.added} new headlines!`);
                } else {
                    setRefreshFeedback("News is up to date!");
                }
            } else {
                setRefreshFeedback("News refreshed!");
            }

            await fetchNews(selectedDay, selectedCategory);
        } catch (err) {
            console.error("Error refreshing news:", err);
            setRefreshFeedback("Failed to fetch fresh news. Please try again.");
        } finally {
            setIsRefreshing(false);
            setTimeout(() => {
                setRefreshFeedback("");
            }, 4000);
        }
    };

    const pageTitle =
        selectedDay === "today" ? "Today's Briefing" : "Previous Day";

    return (
        <div className="page">
            <div className="affairs-header-row">
                <h2>📰 {pageTitle}</h2>

                {refreshFeedback && (
                    <span className="refresh-badge" role="status">
                        {refreshFeedback}
                    </span>
                )}
            </div>

            <div className="affairs-toolbar">
                <div className="day-selector">
                    <button
                        type="button"
                        className={
                            selectedDay === "today"
                                ? "day-btn active"
                                : "day-btn"
                        }
                        onClick={() => setSelectedDay("today")}
                        disabled={loading && selectedDay === "today"}
                    >
                        Today
                    </button>

                    <button
                        type="button"
                        className={
                            selectedDay === "previous"
                                ? "day-btn active"
                                : "day-btn"
                        }
                        onClick={() => setSelectedDay("previous")}
                        disabled={loading && selectedDay === "previous"}
                    >
                        Previous Day
                    </button>
                </div>

                <button
                    type="button"
                    className={`refresh-news-btn ${
                        isRefreshing ? "refreshing" : ""
                    }`}
                    onClick={handleRefresh}
                    disabled={isRefreshing || loading}
                    title="Fetch latest headlines from news sources"
                >
                    <span className="refresh-icon">🔄</span>
                    <span>
                        {isRefreshing ? "Fetching News..." : "Refresh News"}
                    </span>
                </button>
            </div>

            {/* Category Filter Chips */}
            <div className="category-filter-bar">
                {CATEGORIES.map((cat) => {
                    const isActive = selectedCategory === cat.value;
                    return (
                        <button
                            key={cat.value}
                            type="button"
                            className={`category-chip ${
                                isActive ? "active" : ""
                            }`}
                            onClick={() => setSelectedCategory(cat.value)}
                            disabled={loading && isActive}
                        >
                            <span className="cat-icon">{cat.icon}</span>
                            <span>{cat.label}</span>
                        </button>
                    );
                })}
            </div>

            {loading ? (
                <p>
                    Loading{" "}
                    {selectedDay === "today" ? "today's" : "previous day's"}{" "}
                    {selectedCategory !== "All" ? `${selectedCategory.toLowerCase()} ` : ""}news...
                </p>
            ) : error ? (
                <p role="alert">{error}</p>
            ) : news.length === 0 ? (
                <div className="empty-affairs-box">
                    <p>
                        No {selectedCategory !== "All" ? `${selectedCategory} ` : ""}news available for{" "}
                        {selectedDay === "today" ? "today" : "the previous day"}.
                    </p>
                    {selectedCategory !== "All" && (
                        <button
                            type="button"
                            className="category-chip active"
                            onClick={() => setSelectedCategory("All")}
                            style={{ margin: "10px 8px 0 0", display: "inline-flex" }}
                        >
                            🌐 View All News
                        </button>
                    )}
                    <button
                        type="button"
                        className="refresh-news-btn"
                        onClick={handleRefresh}
                        disabled={isRefreshing}
                        style={{ marginTop: "10px" }}
                    >
                        <span className="refresh-icon">🔄</span>
                        <span>
                            {isRefreshing ? "Fetching..." : "Fetch Latest News Now"}
                        </span>
                    </button>
                </div>
            ) : (
                <div className="news-grid">
                    {news.map((item) => (
                        <article className="news-card" key={item.id}>
                            <div className="card-top-row">
                                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                                    <span className="category">
                                        {item.category}
                                    </span>
                                    {item.published_at && (
                                        <span className="news-date-badge">
                                            📅 {item.published_at.slice(0, 10)}
                                        </span>
                                    )}
                                </div>

                                <button
                                    type="button"
                                    className={`bookmark-btn ${bookmarkedIds.includes(item.id)
                                        ? "active"
                                        : ""
                                        }`}
                                    onClick={() =>
                                        handleBookmarkClick(item.id)
                                    }
                                    title={
                                        bookmarkedIds.includes(item.id)
                                            ? "Saved to your Learning Hub"
                                            : "Save to your Learning Hub"
                                    }
                                >
                                    {bookmarkedIds.includes(item.id)
                                        ? "★ Saved"
                                        : "☆ Save"}
                                </button>
                            </div>

                            <h3>{item.title}</h3>

                            <p>{item.summary}</p>

                            <div className="remember">
                                <strong>⭐ Remember:</strong>

                                <ul>
                                    {Array.isArray(item.remember) &&
                                        item.remember.map((fact, index) => (
                                            <li key={index}>{fact}</li>
                                        ))}
                                </ul>
                            </div>

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
        </div>
    );
}

export default Affairs;