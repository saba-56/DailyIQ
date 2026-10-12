from database.database import SessionLocal
from models.opportunity import Opportunity

db = SessionLocal()

# Clear old samples to refresh with full profile fields
db.query(Opportunity).delete()

sample_opportunities = [
    Opportunity(
        type="Internship",
        title="Software Development Engineer Intern",
        organization="DailyIQ Tech Labs",
        description="Work on core backend APIs, database design, and cloud services in a fast-paced environment.",
        eligibility="Students pursuing B.Tech, BCA or MCA in Computer Science / IT.",
        deadline="2026-11-15",
        link="https://example.com/apply-sde",
        degree="B.Tech, BCA, MCA",
        branch="CSE, IT",
        study_year="3rd year, 4th year",
        required_skills="Python, SQL, Web Development, Java",
        location="Bangalore / Remote",
        source_url="https://example.com",
        verified=True
    ),
    Opportunity(
        type="Job",
        title="Junior Data Analyst & BI Associate",
        organization="FinAnalytics Global",
        description="Analyze large datasets, develop dashboards, and uncover business insights.",
        eligibility="Graduates or final year students with strong analytical and database problem-solving skills.",
        deadline="2026-11-20",
        link="https://example.com/apply-data",
        degree="B.Tech, B.Sc, BCA",
        branch="CSE, IT, ECE, Data Science",
        study_year="4th year, Graduate",
        required_skills="SQL, Python, Excel, PowerBI",
        location="Hyderabad / Hybrid",
        source_url="https://example.com",
        verified=True
    ),
    Opportunity(
        type="Internship",
        title="Frontend Web & React Developer Intern",
        organization="Nexus Digital Studio",
        description="Craft beautiful, responsive user interfaces and modern web applications with React.",
        eligibility="Undergraduate students with passion for web design, JavaScript, and responsive UI.",
        deadline="2026-11-25",
        link="https://example.com/apply-frontend",
        degree="B.Tech, BCA, B.Sc",
        branch="CSE, IT, AI/DS",
        study_year="2nd year, 3rd year, 4th year",
        required_skills="Web Development, JavaScript, React, CSS",
        location="Mumbai / Remote",
        source_url="https://example.com",
        verified=True
    ),
    Opportunity(
        type="Scholarship",
        title="National Women in Tech & Engineering Fellowship",
        organization="EmpowerTech Foundation",
        description="Financial grant of INR 50,000 and 1-on-1 industry mentorship for aspiring female engineers.",
        eligibility="Female students in 2nd, 3rd, or 4th year pursuing technology degrees with minimum 7.5 CGPA.",
        deadline="2026-12-01",
        link="https://example.com/scholarship-women",
        degree="B.Tech, M.Tech, BCA",
        branch="CSE, IT, ECE, Electrical",
        study_year="2nd year, 3rd year, 4th year",
        required_skills="Python, Web Development, Academic Excellence",
        location="All India",
        source_url="https://example.com",
        verified=True
    ),
    Opportunity(
        type="Internship",
        title="AI & Machine Learning Research Intern",
        organization="Cognitive Systems AI",
        description="Explore deep learning models, natural language processing, and neural network experiments.",
        eligibility="Students with foundational knowledge of Python and machine learning algorithms.",
        deadline="2026-11-30",
        link="https://example.com/apply-ai",
        degree="B.Tech, M.Tech",
        branch="CSE, IT, AI/DS",
        study_year="3rd year, 4th year",
        required_skills="Python, Machine Learning, Java",
        location="Pune / Remote",
        source_url="https://example.com",
        verified=True
    ),
    Opportunity(
        type="Job",
        title="Embedded Systems & IoT Associate",
        organization="CircuitCraft Solutions",
        description="Design and test microcontroller firmware and connected sensor hardware for smart devices.",
        eligibility="Graduates in Electronics or Electrical engineering.",
        deadline="2026-12-10",
        link="https://example.com/apply-iot",
        degree="B.Tech",
        branch="ECE, Electrical, Instrumentation",
        study_year="4th year, Graduate",
        required_skills="C, C++, Embedded Systems, IoT",
        location="Chennai",
        source_url="https://example.com",
        verified=True
    ),
    Opportunity(
        type="Scholarship",
        title="Merit-Cum-Means Engineering Scholarship",
        organization="DailyIQ Educational Trust",
        description="Full tuition fee support and study laptop grant for high-achieving undergraduate students.",
        eligibility="Open to students from all engineering branches with family annual income under 5 LPA.",
        deadline="2026-12-15",
        link="https://example.com/scholarship-merit",
        degree="B.Tech, BE",
        branch="All Branches",
        study_year="1st year, 2nd year, 3rd year, 4th year",
        required_skills="Academic Excellence, Leadership",
        location="All India",
        source_url="https://example.com",
        verified=True
    )
]

db.add_all(sample_opportunities)
db.commit()
db.close()

print("Sample opportunities with full student profile matching fields seeded successfully!")