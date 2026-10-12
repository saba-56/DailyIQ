
from database.database import engine, Base, SessionLocal
from models.affair import Affair
from models.opportunity import Opportunity
from models.user import User, UserToken
from models.bookmark import Bookmark
from models.student_profile import StudentProfile
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.affairs import router as affairs_router
from routes.opportunities import router as opportunities_router
from routes.auth import router as auth_router
from routes.student_profiles import router as student_profiles_router
from models.quiz_question import QuizQuestion
Base.metadata.create_all(bind=engine)
from routes.quiz import router as quiz_router
def refresh_news():
    db = SessionLocal()

    try:
        from services.news_service import import_news_to_database

        result = import_news_to_database(db)
        print("DailyIQ news refresh:", result)

    except Exception as e:
        print("News refresh failed:", e)

    finally:
        db.close()


app = FastAPI()
@app.on_event("startup")
def startup_event():
    refresh_news()
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(affairs_router)
app.include_router(opportunities_router)
app.include_router(auth_router)
app.include_router(student_profiles_router)
app.include_router(quiz_router)
@app.get("/")
def home():
    return {"message": "DailyIQ Backend is running!"}
