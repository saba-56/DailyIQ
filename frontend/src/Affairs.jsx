
import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

function Affairs() {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const { bookmarkedIds, toggleBookmark, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleBookmarkClick = async (affairId) => {
        if (!isAuthenticated) {
            navigate("/login");
            return;
        }
        await toggleBookmark(affairId);
    };

    useEffect(() => {
        axios
            .get("http://127.0.0.1:8000/latest-affairs")
            .then((response) => {
                console.log("DailyIQ API response:", response.data);

                if (Array.isArray(response.data)) {
                    setNews(response.data);
                } else {
                    setError("The API returned an unexpected response.");
                }
            })
            .catch((err) => {
                console.error("Error fetching affairs:", err);

                if (err.response) {
                    setError("API error: " + err.response.status);
                } else {
                    setError(
                        "Cannot connect to the backend. Check that it is running."
                    );
                }
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="page">
                <h2>📰 Today's Affairs</h2>
                <p>Loading today's affairs...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="page">
                <h2>📰 Today's Affairs</h2>
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className="page">
            <h2>📰 Today's Affairs</h2>

            {news.length === 0 ? (
                <p>No affairs available right now.</p>
            ) : (
                <div className="news-grid">
                    {news.map((item) => (
                        <article className="news-card" key={item.id}>
                            <div className="card-top-row">
                                <span className="category">
                                    {item.category}
                                </span>
                                <button
                                    type="button"
                                    className={`bookmark-btn ${bookmarkedIds.includes(item.id) ? "active" : ""}`}
                                    onClick={() => handleBookmarkClick(item.id)}
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