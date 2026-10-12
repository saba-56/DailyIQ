import { Link } from "react-router-dom";

function Home() {
    return (
        <div className="home-page">
            <header className="header">
                <h2>Good Morning 👋</h2>
                <p className="tagline">
                    Your daily knowledge companion.
                </p>
            </header>

            <section className="feature-grid">

                <div className="feature-card">
                    <h2>📰 Daily Affairs</h2>
                    <p>
                        Read today's important current affairs in short
                        and easy-to-remember points.
                    </p>
                    <Link to="/affairs">
                        <button>Read Today's Affairs</button>
                    </Link>
                </div>

                <div className="feature-card">
                    <h2>💼 Opportunities</h2>
                    <p>
                        Discover jobs, internships and scholarships in
                        one place.
                    </p>
                    <Link to="/opportunities">
                        <button>Explore Opportunities</button>
                    </Link>
                </div>

                <div className="feature-card">
                    <h2>🎯 Daily Quiz</h2>
                    <p>
                        Test your knowledge with questions based on
                        important current affairs.
                    </p>
                    <Link to="/quiz">
                        <button>Take Today's Quiz</button>
                    </Link>
                </div>

                <div className="feature-card">
                    <h2>🤖 Ask AI</h2>
                    <p>
                        Ask questions and learn about current affairs
                        and general knowledge.
                    </p>
                    <Link to="/ask-ai">
                        <button>Ask AI</button>
                    </Link>
                </div>

            </section>
        </div>
    );
}

export default Home;