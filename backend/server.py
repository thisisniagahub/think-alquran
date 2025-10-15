from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class LessonResponse(BaseModel):
    id: str
    lesson_number: int
    title: str
    description: str
    word_count: int
    estimated_minutes: int
    is_completed: bool
    mastery_percentage: float

class WordInLesson(BaseModel):
    id: str
    arabic: str
    transliteration: str
    meaning: str
    example_verse: Optional[str] = None

class QuizAnswer(BaseModel):
    word_id: str
    is_correct: bool
    time_spent: int  # seconds

class LessonComplete(BaseModel):
    lesson_id: str
    answers: List[QuizAnswer]
    total_time: int

class DashboardStats(BaseModel):
    total_words_learned: int
    current_streak: int
    total_lessons_completed: int
    mastery_percentage: float
    words_practiced_today: int
    next_lesson: Optional[dict]

# Initialize sample data
@app.on_event("startup")
async def initialize_data():
    # Check if words exist
    word_count = await db.words.count_documents({})
    if word_count == 0:
        sample_words = [
            # Lesson 1 - Basic Words
            {"arabic": "اللَّهُ", "transliteration": "Allah", "meaning": "God", "lesson_number": 1, "category": "basic"},
            {"arabic": "رَبُّ", "transliteration": "Rabb", "meaning": "Lord", "lesson_number": 1, "category": "basic"},
            {"arabic": "رَحْمَٰنِ", "transliteration": "Rahman", "meaning": "Most Merciful", "lesson_number": 1, "category": "basic"},
            {"arabic": "رَحِيمِ", "transliteration": "Rahim", "meaning": "Most Compassionate", "lesson_number": 1, "category": "basic"},
            {"arabic": "مَلِكِ", "transliteration": "Malik", "meaning": "King", "lesson_number": 1, "category": "basic"},
            {"arabic": "يَوْمِ", "transliteration": "Yawm", "meaning": "Day", "lesson_number": 1, "category": "basic"},
            {"arabic": "دِينِ", "transliteration": "Deen", "meaning": "Judgment/Religion", "lesson_number": 1, "category": "basic"},
            {"arabic": "نَعْبُدُ", "transliteration": "Na'budu", "meaning": "We worship", "lesson_number": 1, "category": "basic"},
            {"arabic": "نَسْتَعِينُ", "transliteration": "Nasta'een", "meaning": "We seek help", "lesson_number": 1, "category": "basic"},
            {"arabic": "صِرَاطَ", "transliteration": "Sirat", "meaning": "Path", "lesson_number": 1, "category": "basic"},
            
            # Lesson 2 - Common Verbs
            {"arabic": "قَالَ", "transliteration": "Qala", "meaning": "He said", "lesson_number": 2, "category": "verbs"},
            {"arabic": "كَانَ", "transliteration": "Kana", "meaning": "Was/Were", "lesson_number": 2, "category": "verbs"},
            {"arabic": "جَاءَ", "transliteration": "Jaa'a", "meaning": "He came", "lesson_number": 2, "category": "verbs"},
            {"arabic": "ذَهَبَ", "transliteration": "Dhahaba", "meaning": "He went", "lesson_number": 2, "category": "verbs"},
            {"arabic": "عَمِلَ", "transliteration": "'Amila", "meaning": "He did/worked", "lesson_number": 2, "category": "verbs"},
            {"arabic": "آمَنَ", "transliteration": "Aamana", "meaning": "He believed", "lesson_number": 2, "category": "verbs"},
            {"arabic": "كَفَرَ", "transliteration": "Kafara", "meaning": "He disbelieved", "lesson_number": 2, "category": "verbs"},
            {"arabic": "عَلِمَ", "transliteration": "'Alima", "meaning": "He knew", "lesson_number": 2, "category": "verbs"},
            {"arabic": "سَمِعَ", "transliteration": "Sami'a", "meaning": "He heard", "lesson_number": 2, "category": "verbs"},
            {"arabic": "رَأَى", "transliteration": "Ra'a", "meaning": "He saw", "lesson_number": 2, "category": "verbs"},
            
            # Lesson 3 - Pronouns & Particles
            {"arabic": "هُوَ", "transliteration": "Huwa", "meaning": "He", "lesson_number": 3, "category": "pronouns"},
            {"arabic": "هِيَ", "transliteration": "Hiya", "meaning": "She", "lesson_number": 3, "category": "pronouns"},
            {"arabic": "أَنْتَ", "transliteration": "Anta", "meaning": "You (masculine)", "lesson_number": 3, "category": "pronouns"},
            {"arabic": "أَنَا", "transliteration": "Ana", "meaning": "I", "lesson_number": 3, "category": "pronouns"},
            {"arabic": "نَحْنُ", "transliteration": "Nahnu", "meaning": "We", "lesson_number": 3, "category": "pronouns"},
            {"arabic": "هُمْ", "transliteration": "Hum", "meaning": "They", "lesson_number": 3, "category": "pronouns"},
            {"arabic": "مِنْ", "transliteration": "Min", "meaning": "From", "lesson_number": 3, "category": "particles"},
            {"arabic": "إِلَىٰ", "transliteration": "Ila", "meaning": "To/Towards", "lesson_number": 3, "category": "particles"},
            {"arabic": "فِي", "transliteration": "Fee", "meaning": "In", "lesson_number": 3, "category": "particles"},
            {"arabic": "عَلَىٰ", "transliteration": "'Ala", "meaning": "On/Upon", "lesson_number": 3, "category": "particles"},
        ]
        await db.words.insert_many(sample_words)
        logger.info("Sample words initialized")

# Auth Routes
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user_doc = {
        "username": user_data.username,
        "password": hashed_password.decode('utf-8'),
        "created_at": datetime.utcnow(),
        "current_streak": 0,
        "last_activity": None,
        "total_words_learned": 0,
        "total_lessons_completed": 0
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Generate token
    access_token = create_access_token(data={"sub": str(result.inserted_id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(result.inserted_id),
            "username": user_data.username
        }
    }

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    # Find user
    user = await db.users.find_one({"username": user_data.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    if not bcrypt.checkpw(user_data.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "username": user["username"]
        }
    }

# Dashboard Route
@api_router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    # Get user progress
    progress_items = await db.user_progress.find({"user_id": user_id}).to_list(1000)
    
    # Calculate stats
    words_learned = len([p for p in progress_items if p.get("mastery_level", 0) >= 50])
    
    # Check streak
    last_activity = current_user.get("last_activity")
    current_streak = current_user.get("current_streak", 0)
    
    # Words practiced today
    today = datetime.utcnow().date()
    words_today = len([p for p in progress_items if p.get("last_practiced") and p["last_practiced"].date() == today])
    
    # Calculate overall mastery
    if progress_items:
        avg_mastery = sum([p.get("mastery_level", 0) for p in progress_items]) / len(progress_items)
    else:
        avg_mastery = 0
    
    # Get next lesson
    completed_lessons = current_user.get("total_lessons_completed", 0)
    next_lesson_num = completed_lessons + 1
    
    next_lesson = None
    if next_lesson_num <= 3:
        lesson_words = await db.words.find({"lesson_number": next_lesson_num}).to_list(100)
        if lesson_words:
            next_lesson = {
                "lesson_number": next_lesson_num,
                "word_count": len(lesson_words)
            }
    
    return {
        "total_words_learned": words_learned,
        "current_streak": current_streak,
        "total_lessons_completed": current_user.get("total_lessons_completed", 0),
        "mastery_percentage": round(avg_mastery, 1),
        "words_practiced_today": words_today,
        "next_lesson": next_lesson
    }

# Lesson Routes
@api_router.get("/lessons", response_model=List[LessonResponse])
async def get_lessons(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    lessons = [
        {"number": 1, "title": "Basic Words", "description": "Learn fundamental Quranic terms"},
        {"number": 2, "title": "Common Verbs", "description": "Master frequently used verbs"},
        {"number": 3, "title": "Pronouns & Particles", "description": "Understand connecting words"},
    ]
    
    result = []
    for lesson in lessons:
        # Get words for this lesson
        lesson_words = await db.words.find({"lesson_number": lesson["number"]}).to_list(100)
        word_ids = [str(w["_id"]) for w in lesson_words]
        
        # Get user progress for these words
        progress = await db.user_progress.find({
            "user_id": user_id,
            "word_id": {"$in": word_ids}
        }).to_list(1000)
        
        # Calculate completion
        is_completed = len(progress) >= len(lesson_words) and all(p.get("mastery_level", 0) >= 30 for p in progress)
        
        # Calculate mastery percentage
        if progress:
            mastery = sum([p.get("mastery_level", 0) for p in progress]) / len(lesson_words)
        else:
            mastery = 0
        
        result.append({
            "id": f"lesson_{lesson['number']}",
            "lesson_number": lesson["number"],
            "title": lesson["title"],
            "description": lesson["description"],
            "word_count": len(lesson_words),
            "estimated_minutes": 15,
            "is_completed": is_completed,
            "mastery_percentage": round(mastery, 1)
        })
    
    return result

@api_router.get("/lessons/{lesson_number}", response_model=List[WordInLesson])
async def get_lesson_words(lesson_number: int, current_user: dict = Depends(get_current_user)):
    words = await db.words.find({"lesson_number": lesson_number}).to_list(100)
    
    return [
        {
            "id": str(word["_id"]),
            "arabic": word["arabic"],
            "transliteration": word["transliteration"],
            "meaning": word["meaning"],
            "example_verse": word.get("example_verse")
        }
        for word in words
    ]

@api_router.post("/lessons/complete")
async def complete_lesson(completion: LessonComplete, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    # Update progress for each word
    for answer in completion.answers:
        existing_progress = await db.user_progress.find_one({
            "user_id": user_id,
            "word_id": answer.word_id
        })
        
        if existing_progress:
            # Update existing progress
            correct_count = existing_progress.get("correct_count", 0)
            total_attempts = existing_progress.get("total_attempts", 0)
            
            if answer.is_correct:
                correct_count += 1
            total_attempts += 1
            
            # Calculate mastery level (0-100)
            mastery_level = min(100, (correct_count / total_attempts) * 100)
            
            await db.user_progress.update_one(
                {"_id": existing_progress["_id"]},
                {
                    "$set": {
                        "mastery_level": mastery_level,
                        "last_practiced": datetime.utcnow(),
                        "correct_count": correct_count,
                        "total_attempts": total_attempts
                    }
                }
            )
        else:
            # Create new progress entry
            mastery_level = 100 if answer.is_correct else 0
            await db.user_progress.insert_one({
                "user_id": user_id,
                "word_id": answer.word_id,
                "mastery_level": mastery_level,
                "last_practiced": datetime.utcnow(),
                "correct_count": 1 if answer.is_correct else 0,
                "total_attempts": 1
            })
    
    # Update user stats
    progress_items = await db.user_progress.find({"user_id": user_id}).to_list(1000)
    words_learned = len([p for p in progress_items if p.get("mastery_level", 0) >= 50])
    
    # Update streak
    today = datetime.utcnow().date()
    last_activity = current_user.get("last_activity")
    current_streak = current_user.get("current_streak", 0)
    
    if last_activity:
        last_date = last_activity.date()
        if (today - last_date).days == 1:
            current_streak += 1
        elif (today - last_date).days > 1:
            current_streak = 1
    else:
        current_streak = 1
    
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {
            "$set": {
                "last_activity": datetime.utcnow(),
                "current_streak": current_streak,
                "total_words_learned": words_learned
            }
        }
    )
    
    return {"success": True, "message": "Lesson completed", "words_learned": words_learned}

# Progress Routes
@api_router.get("/progress/words")
async def get_word_progress(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    # Get all words with progress
    all_words = await db.words.find().to_list(1000)
    progress_items = await db.user_progress.find({"user_id": user_id}).to_list(1000)
    
    # Create progress map
    progress_map = {p["word_id"]: p for p in progress_items}
    
    result = []
    for word in all_words:
        word_id = str(word["_id"])
        progress = progress_map.get(word_id, {})
        
        result.append({
            "id": word_id,
            "arabic": word["arabic"],
            "transliteration": word["transliteration"],
            "meaning": word["meaning"],
            "mastery_level": progress.get("mastery_level", 0),
            "last_practiced": progress.get("last_practiced"),
            "total_attempts": progress.get("total_attempts", 0)
        })
    
    return result

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
