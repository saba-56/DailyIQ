
import axios from "axios";
import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Opportunities() {
    const [opportunities, setOpportunities] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [personalized, setPersonalized] = useState(true);
    const [category, setCategory] = useState("");
    const [retryCount, setRetryCount] = useState(0);

    useEffect(() => {
        let cancelled = false;

        async function fetchOpportunities() {
            setLoading(true);
            setError("");

            try {
                const token = localStorage.getItem("token");

                const response = await axios.get(
                    `${API_URL}/opportunities`,
                    {
                        params: {
                            personalized,
                            ...(category ? { type: category } : {}),
                        },
                        headers: token
                            ? { Authorization: `Bearer ${token}` }
                            : {},
                    }
                );

                if (!cancelled) {
                    setOpportunities(response.data);
                }
            } catch (err) {
                console.error("Error fetching opportunities:", err);

                if (!cancelled) {
                    setError(
                        "Couldn't load opportunities. Please check that the backend is running and try again."
                    );
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        }

        fetchOpportunities();

        return () => {
            cancelled = true;
        };
    }, [personalized, category, retryCount]);

    return (
        <div className="page">
            <h2>💼 Opportunities</h2>
            <p>Find jobs, internships and scholarships in one place.</p>

            <div className="opportunity-filters">
                <label htmlFor="opportunity-category">
                    Category:
                </label>

                <select
                    id="opportunity-category"
                    value={category}
                    onChange={(event) => setCategory(event.target.value)}
                >
                    <option value="">All opportunities</option>
                    <option value="Internship">Internships</option>
                    <option value="Job">Jobs</option>
                    <option value="Scholarship">Scholarships</option>
                    <option value="Hackathon">Hackathons</option>
                </select>

                <label>
                    <input
                        type="checkbox"
                        checked={personalized}
                        onChange={(event) =>
                            setPersonalized(event.target.checked)
                        }
                    />
                    Personalize for me
                </label>
            </div>

            {loading && <p>Loading opportunities...</p>}


            {error && (
                <div role="alert">
                    <p>{error}</p>
                    <button onClick={() => setRetryCount((count) => count + 1)}>
                        Try again
                    </button>
                </div>
            )}

            {!loading && !error && opportunities.length === 0 && (
                <p>No opportunities found for this category yet.</p>
            )}

            <div className="opportunity-grid">
                {opportunities.map((item) => (
                    <div className="opportunity-card" key={item.id}>
                        <span className="category">{item.type}</span>

                        {item.verified && (
                            <span className="verified-badge">
                                ✓ Verified listing
                            </span>
                        )}

                        <h3>{item.title}</h3>
                        <h4>{item.organization}</h4>

                        {item.match_score !== null &&
                            item.match_score !== undefined && (
                                <div className="match-info">
                                    <strong>
                                        Match score: {item.match_score}
                                    </strong>

                                    {item.match_reasons?.length > 0 && (
                                        <ul>
                                            {item.match_reasons.map(
                                                (reason, index) => (
                                                    <li key={index}>
                                                        {reason}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    )}
                                </div>
                            )}

                        <p>{item.description}</p>

                        {item.eligibility && (
                            <p>
                                <strong>Eligibility:</strong>{" "}
                                {item.eligibility}
                            </p>
                        )}

                        {item.deadline && (
                            <p>
                                <strong>Deadline:</strong> {item.deadline}
                            </p>
                        )}

                        {item.location && (
                            <p>
                                <strong>Location:</strong> {item.location}
                            </p>
                        )}

                        {item.link && (
                            <a
                                href={item.link}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                View Opportunity →
                            </a>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Opportunities;