import { Link } from "react-router-dom";

function Opportunities() {
    return (
        <div className="page upcoming-minimal-page">
            <div className="upcoming-minimal-content">
                <span className="upcoming-minimal-pill">🚀 Upcoming Feature</span>
                <h2>💼 Opportunities Hub</h2>
                <p className="upcoming-minimal-desc">
                    Personalized internships, verified scholarships, and career opportunities tailored to your degree and skills are coming soon.
                </p>
                <div className="upcoming-minimal-actions">
                    <Link to="/affairs">
                        <button className="minimal-primary-btn">Read Today's Affairs</button>
                    </Link>
                    <Link to="/quiz">
                        <button className="minimal-secondary-btn">Take Today's Quiz</button>
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Opportunities;
