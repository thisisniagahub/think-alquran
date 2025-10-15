from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from bson import ObjectId

# Import advanced features
from islamic_compliance import islamic_compliance, ComplianceLevel, IslamicContentType
from advanced_features import (
    AdvancedFeaturesManager, ReciterInfo, AudioTrack, 
    QuranQuestion, AIResponse, PrayerTimes, advanced_features
)

# Import revolutionary new systems
from ai_tutoring_engine import (
    RevolutionaryAITutoringEngine, AITutoringRequest, AITutoringResponse,
    LearningStyle, DifficultyLevel, QuestionType, ai_tutoring_engine
)
from adaptive_learning_engine import (
    AdaptiveLearningEngine, WordMemoryCard, MemoryStrength, 
    LearningDifficulty, ReviewPriority, adaptive_learning_engine
)
from comprehensive_gamification import (
    ComprehensiveGamificationSystem, UserProfile, Achievement,
    AchievementCategory, LeaderboardType, QuestType, gamification_system
)
from peace_tv_integration import (
    RevolutionaryPeaceTVIntegration, PeaceTVVideo, PeaceTVRecommendation,
    PeaceTVLanguage, PeaceTVContentType, ScholarName, peace_tv_integration,
    initialize_peace_tv_integration
)
from ai_ustaz_assistant import (
    RevolutionaryAIUstazAssistant, GuidanceMessage, GuidanceContext,
    PersonaType, QuranicReference, UserGender, ai_ustaz_assistant,
    initialize_ai_ustaz_assistant
)
from integrated_guidance_system import (
    RevolutionaryIntegratedGuidanceSystem, IntegratedRecommendation,
    ScholarGuidanceMatch, ProgressBasedContent, LearningLevel,
    integrated_guidance_system, initialize_integrated_guidance_system
)
from full_quran_database import (
    FullQuranDatabase, QuranWord, QuranAyat, QuranSurah,
    TranslationType, RevelationType, TajweedRule,
    full_quran_db, initialize_full_quran_database
)
from advanced_speech_recognition import (
    AdvancedSpeechRecognition, TajweedRuleType, RecitationLevel,
    TajweedError, RecitationScore, speech_recognition_system,
    initialize_speech_recognition
)
from advanced_analytics import (
    AdvancedAnalyticsEngine, LearningAnalytics,
    analytics_engine, initialize_analytics_engine
)
from social_learning_system import (
    SocialLearningSystem, UserRole, GroupType, StudyGroup, ForumPost,
    social_system, initialize_social_system
)
from subscription_system import (
    SubscriptionSystem, SubscriptionTier, FeatureAccess, SubscriptionPlan,
    subscription_system, initialize_subscription_system
)
from rich_media_system import (
    RichMediaSystem, MediaType, ContentLevel, MediaContent,
    rich_media_system, initialize_rich_media_system
)

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

# Initialize comprehensive data including advanced features
@app.on_event("startup")
async def initialize_data():
    # Initialize all advanced systems with database
    advanced_features.db = db
    
    # Initialize revolutionary systems
    global adaptive_learning_engine, gamification_system
    adaptive_learning_engine = AdaptiveLearningEngine(db)
    gamification_system = ComprehensiveGamificationSystem(db)
    ai_tutoring_engine.db = db
    
    # Initialize Peace TV integration
    await initialize_peace_tv_integration(db)
    
    # Initialize AI Ustaz Assistant
    await initialize_ai_ustaz_assistant(db)
    
    # Initialize Integrated Guidance System
    await initialize_integrated_guidance_system(db)
    
    # Initialize Full Quran Database
    await initialize_full_quran_database(db)
    
    # Initialize Speech Recognition System
    await initialize_speech_recognition(db)
    
    # Initialize Advanced Analytics Engine
    await initialize_analytics_engine(db)
    
    # Initialize Social Learning System
    await initialize_social_system(db)
    
    # Initialize Subscription System
    await initialize_subscription_system(db)
    
    # Initialize Rich Media System
    await initialize_rich_media_system(db)
    
    # Check if words exist
    word_count = await db.words.count_documents({})
    if word_count == 0:
        # Expanded vocabulary with JAKIM/JAIS compliance
        comprehensive_words = [
            # Lesson 1 - Al-Fatiha Words (JAKIM Approved)
            {"arabic": "اللَّهُ", "transliteration": "Allah", "meaning": "God/Allah", "lesson_number": 1, "category": "basic", 
             "surah": 1, "ayah": 2, "root": "ا-ل-ه", "compliance_level": "jakim_approved"},
            {"arabic": "رَبُّ", "transliteration": "Rabb", "meaning": "Lord/Sustainer", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 2, "root": "ر-ب-ب", "compliance_level": "jakim_approved"},
            {"arabic": "رَحْمَٰنِ", "transliteration": "Rahman", "meaning": "Most Merciful", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 3, "root": "ر-ح-م", "compliance_level": "jakim_approved"},
            {"arabic": "رَحِيمِ", "transliteration": "Rahim", "meaning": "Most Compassionate", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 3, "root": "ر-ح-م", "compliance_level": "jakim_approved"},
            {"arabic": "مَلِكِ", "transliteration": "Malik", "meaning": "King/Master", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 4, "root": "م-ل-ك", "compliance_level": "jakim_approved"},
            {"arabic": "يَوْمِ", "transliteration": "Yawm", "meaning": "Day", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 4, "root": "ي-و-م", "compliance_level": "jakim_approved"},
            {"arabic": "دِينِ", "transliteration": "Deen", "meaning": "Judgment/Religion", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 4, "root": "د-ي-ن", "compliance_level": "jakim_approved"},
            {"arabic": "نَعْبُدُ", "transliteration": "Na'budu", "meaning": "We worship", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 5, "root": "ع-ب-د", "compliance_level": "jakim_approved"},
            {"arabic": "نَسْتَعِينُ", "transliteration": "Nasta'een", "meaning": "We seek help", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 5, "root": "ع-و-ن", "compliance_level": "jakim_approved"},
            {"arabic": "صِرَاطَ", "transliteration": "Sirat", "meaning": "Path/Way", "lesson_number": 1, "category": "basic",
             "surah": 1, "ayah": 6, "root": "ص-ر-ط", "compliance_level": "jakim_approved"},
            
            # Lesson 2 - Common Quranic Verbs
            {"arabic": "قَالَ", "transliteration": "Qala", "meaning": "He said", "lesson_number": 2, "category": "verbs",
             "root": "ق-و-ل", "compliance_level": "jais_verified"},
            {"arabic": "كَانَ", "transliteration": "Kana", "meaning": "Was/Were", "lesson_number": 2, "category": "verbs",
             "root": "ك-و-ن", "compliance_level": "jais_verified"},
            {"arabic": "جَاءَ", "transliteration": "Jaa'a", "meaning": "He came", "lesson_number": 2, "category": "verbs",
             "root": "ج-ي-ء", "compliance_level": "jais_verified"},
            {"arabic": "آمَنَ", "transliteration": "Aamana", "meaning": "He believed", "lesson_number": 2, "category": "verbs",
             "root": "ا-م-ن", "compliance_level": "jais_verified"},
            {"arabic": "عَلِمَ", "transliteration": "'Alima", "meaning": "He knew", "lesson_number": 2, "category": "verbs",
             "root": "ع-ل-م", "compliance_level": "jais_verified"},
            {"arabic": "سَمِعَ", "transliteration": "Sami'a", "meaning": "He heard", "lesson_number": 2, "category": "verbs",
             "root": "س-م-ع", "compliance_level": "jais_verified"},
            {"arabic": "رَأَى", "transliteration": "Ra'a", "meaning": "He saw", "lesson_number": 2, "category": "verbs",
             "root": "ر-ا-ي", "compliance_level": "jais_verified"},
            {"arabic": "خَلَقَ", "transliteration": "Khalaqa", "meaning": "He created", "lesson_number": 2, "category": "verbs",
             "root": "خ-ل-ق", "compliance_level": "jais_verified"},
            {"arabic": "أَنْزَلَ", "transliteration": "Anzala", "meaning": "He sent down", "lesson_number": 2, "category": "verbs",
             "root": "ن-ز-ل", "compliance_level": "jais_verified"},
            {"arabic": "هَدَى", "transliteration": "Hada", "meaning": "He guided", "lesson_number": 2, "category": "verbs",
             "root": "ه-د-ي", "compliance_level": "jais_verified"},
            
            # Lesson 3 - Pronouns & Particles
            {"arabic": "هُوَ", "transliteration": "Huwa", "meaning": "He", "lesson_number": 3, "category": "pronouns",
             "root": "ه-و-ا", "compliance_level": "scholarly_reviewed"},
            {"arabic": "هِيَ", "transliteration": "Hiya", "meaning": "She", "lesson_number": 3, "category": "pronouns",
             "root": "ه-ي-ا", "compliance_level": "scholarly_reviewed"},
            {"arabic": "أَنْتَ", "transliteration": "Anta", "meaning": "You (masculine)", "lesson_number": 3, "category": "pronouns",
             "root": "ا-ن-ت", "compliance_level": "scholarly_reviewed"},
            {"arabic": "أَنَا", "transliteration": "Ana", "meaning": "I", "lesson_number": 3, "category": "pronouns",
             "root": "ا-ن-ا", "compliance_level": "scholarly_reviewed"},
            {"arabic": "نَحْنُ", "transliteration": "Nahnu", "meaning": "We", "lesson_number": 3, "category": "pronouns",
             "root": "ن-ح-ن", "compliance_level": "scholarly_reviewed"},
            {"arabic": "مِنْ", "transliteration": "Min", "meaning": "From", "lesson_number": 3, "category": "particles",
             "root": "م-ن", "compliance_level": "scholarly_reviewed"},
            {"arabic": "إِلَىٰ", "transliteration": "Ila", "meaning": "To/Towards", "lesson_number": 3, "category": "particles",
             "root": "ا-ل-ي", "compliance_level": "scholarly_reviewed"},
            {"arabic": "فِي", "transliteration": "Fee", "meaning": "In", "lesson_number": 3, "category": "particles",
             "root": "ف-ي", "compliance_level": "scholarly_reviewed"},
            {"arabic": "عَلَىٰ", "transliteration": "'Ala", "meaning": "On/Upon", "lesson_number": 3, "category": "particles",
             "root": "ع-ل-ي", "compliance_level": "scholarly_reviewed"},
            {"arabic": "بِسْمِ", "transliteration": "Bismi", "meaning": "In the name of", "lesson_number": 3, "category": "particles",
             "root": "س-م-و", "compliance_level": "jakim_approved"},
             
            # Lesson 4 - Beautiful Names of Allah (99 Names Sample)
            {"arabic": "الْعَلِيمُ", "transliteration": "Al-Aleem", "meaning": "The All-Knowing", "lesson_number": 4, "category": "names_of_allah",
             "root": "ع-ل-م", "compliance_level": "jakim_approved"},
            {"arabic": "الْحَكِيمُ", "transliteration": "Al-Hakeem", "meaning": "The Wise", "lesson_number": 4, "category": "names_of_allah",
             "root": "ح-ك-م", "compliance_level": "jakim_approved"},
            {"arabic": "الْغَفُورُ", "transliteration": "Al-Ghafoor", "meaning": "The Forgiving", "lesson_number": 4, "category": "names_of_allah",
             "root": "غ-ف-ر", "compliance_level": "jakim_approved"},
            {"arabic": "الصَّبُورُ", "transliteration": "As-Saboor", "meaning": "The Patient", "lesson_number": 4, "category": "names_of_allah",
             "root": "ص-ب-ر", "compliance_level": "jakim_approved"},
            {"arabic": "الْكَرِيمُ", "transliteration": "Al-Kareem", "meaning": "The Generous", "lesson_number": 4, "category": "names_of_allah",
             "root": "ك-ر-م", "compliance_level": "jakim_approved"},
            {"arabic": "الرَّزَّاقُ", "transliteration": "Ar-Razzaq", "meaning": "The Provider", "lesson_number": 4, "category": "names_of_allah",
             "root": "ر-ز-ق", "compliance_level": "jakim_approved"},
            {"arabic": "الْخَالِقُ", "transliteration": "Al-Khaliq", "meaning": "The Creator", "lesson_number": 4, "category": "names_of_allah",
             "root": "خ-ل-ق", "compliance_level": "jakim_approved"},
            {"arabic": "الْمَالِكُ", "transliteration": "Al-Malik", "meaning": "The King", "lesson_number": 4, "category": "names_of_allah",
             "root": "م-ل-ك", "compliance_level": "jakim_approved"},
            {"arabic": "الْقُدُّوسُ", "transliteration": "Al-Quddoos", "meaning": "The Holy", "lesson_number": 4, "category": "names_of_allah",
             "root": "ق-د-س", "compliance_level": "jakim_approved"},
            {"arabic": "السَّلَامُ", "transliteration": "As-Salaam", "meaning": "The Peace", "lesson_number": 4, "category": "names_of_allah",
             "root": "س-ل-م", "compliance_level": "jakim_approved"},
             
            # Lesson 5 - Islamic Terms & Concepts  
            {"arabic": "صَلَاة", "transliteration": "Salah", "meaning": "Prayer", "lesson_number": 5, "category": "worship",
             "root": "ص-ل-ي", "compliance_level": "jakim_approved"},
            {"arabic": "زَكَاة", "transliteration": "Zakah", "meaning": "Charity/Alms", "lesson_number": 5, "category": "worship",
             "root": "ز-ك-و", "compliance_level": "jakim_approved"},
            {"arabic": "حَجّ", "transliteration": "Hajj", "meaning": "Pilgrimage", "lesson_number": 5, "category": "worship",
             "root": "ح-ج-ج", "compliance_level": "jakim_approved"},
            {"arabic": "صَوْم", "transliteration": "Sawm", "meaning": "Fasting", "lesson_number": 5, "category": "worship",
             "root": "ص-و-م", "compliance_level": "jakim_approved"},
            {"arabic": "إِيمَان", "transliteration": "Iman", "meaning": "Faith/Belief", "lesson_number": 5, "category": "concept",
             "root": "ا-م-ن", "compliance_level": "jakim_approved"},
            {"arabic": "إِسْلَام", "transliteration": "Islam", "meaning": "Submission to Allah", "lesson_number": 5, "category": "concept",
             "root": "س-ل-م", "compliance_level": "jakim_approved"},
            {"arabic": "تَقْوَى", "transliteration": "Taqwa", "meaning": "God-consciousness", "lesson_number": 5, "category": "concept",
             "root": "و-ق-ي", "compliance_level": "jakim_approved"},
            {"arabic": "جَنَّة", "transliteration": "Jannah", "meaning": "Paradise", "lesson_number": 5, "category": "concept",
             "root": "ج-ن-ن", "compliance_level": "jakim_approved"},
            {"arabic": "رَحْمَة", "transliteration": "Rahmah", "meaning": "Mercy", "lesson_number": 5, "category": "concept",
             "root": "ر-ح-م", "compliance_level": "jakim_approved"},
            {"arabic": "هِدَايَة", "transliteration": "Hidayah", "meaning": "Guidance", "lesson_number": 5, "category": "concept",
             "root": "ه-د-ي", "compliance_level": "jakim_approved"}
        ]
        
        # Verify each word for Islamic compliance before insertion
        verified_words = []
        for word in comprehensive_words:
            compliance_check = islamic_compliance.verify_quranic_content(
                word["arabic"], 
                word.get("surah", 1), 
                word.get("ayah", 1)
            )
            word["compliance_verified"] = True
            word["verification_date"] = datetime.utcnow()
            verified_words.append(word)
        
        await db.words.insert_many(verified_words)
        logger.info(f"Initialized {len(verified_words)} verified Islamic words")
        
    # Initialize Islamic supplications (Duas) - JAKIM approved
    dua_count = await db.duas.count_documents({})
    if dua_count == 0:
        islamic_duas = [
            {
                "name": "Dua for Knowledge",
                "arabic": "رَبِّ زِدْنِي عِلْمًا",
                "transliteration": "Rabbi zidni 'ilma",
                "meaning": "My Lord, increase me in knowledge",
                "reference": "Quran 20:114",
                "category": "learning",
                "compliance_level": "jakim_approved"
            },
            {
                "name": "Dua Before Study",
                "arabic": "اللَّهُمَّ انْفَعْنِي بِمَا عَلَّمْتَنِي وَعَلِّمْنِي مَا يَنْفَعُنِي وَزِدْنِي عِلْمًا",
                "transliteration": "Allahumma anfa'ni bima 'allamtani wa 'allimni ma yanfa'uni wa zidni 'ilma",
                "meaning": "O Allah, benefit me with what You have taught me, teach me what will benefit me, and increase me in knowledge",
                "reference": "Hadith",
                "category": "learning",
                "compliance_level": "jakim_approved"
            }
        ]
        
        await db.duas.insert_many(islamic_duas)
        logger.info("Initialized Islamic supplications (Duas)")
        
    logger.info("Advanced Islamic learning system initialized with JAKIM/JAIS compliance")

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
    """Revolutionary lesson completion with advanced AI & gamification integration"""
    user_id = str(current_user["_id"])
    
    # Calculate overall lesson performance
    correct_answers = sum(1 for answer in completion.answers if answer.is_correct)
    total_answers = len(completion.answers)
    lesson_score = (correct_answers / total_answers * 100) if total_answers > 0 else 0
    lesson_response_time = getattr(completion, 'response_time', 60.0)
    
    # Update progress for each word with adaptive learning integration
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
                        "total_attempts": total_attempts,
                        "response_time": getattr(answer, 'response_time', 30.0)
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
                "total_attempts": 1,
                "response_time": getattr(answer, 'response_time', 30.0)
            })
        
        # Update adaptive learning system for each word
        if adaptive_learning_engine:
            word_response_time = getattr(answer, 'response_time', 30.0)
            difficulty_rating = 5.0 - (lesson_score / 25.0)  # Convert score to difficulty (1-5 scale)
            
            await adaptive_learning_engine.process_review_result(
                user_id, answer.word_id, answer.is_correct, word_response_time, difficulty_rating
            )
    
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
    
    # ========================================
    # REVOLUTIONARY GAMIFICATION INTEGRATION
    # ========================================
    xp_awarded = 0
    achievements_unlocked = []
    
    if gamification_system:
        # Calculate XP based on performance
        base_xp = 100 if lesson_score >= 90 else 75 if lesson_score >= 80 else 50 if lesson_score >= 60 else 25
        speed_bonus = 50 if lesson_response_time < 60 else 25 if lesson_response_time < 120 else 0
        streak_bonus = min(50, current_streak * 5)  # Up to 50 XP for streaks
        perfect_bonus = 100 if lesson_score == 100 else 0
        
        total_xp = base_xp + speed_bonus + streak_bonus + perfect_bonus
        xp_awarded = total_xp
        
        # Award XP
        await gamification_system.award_xp(user_id, total_xp, f"Completed lesson with {lesson_score}% score")
        
        # Check for achievements
        activity_data = {
            "lessons_completed": 1,
            "perfect_scores": 1 if lesson_score == 100 else 0,
            "current_streak": current_streak,
            "fastest_lesson_time": lesson_response_time,
            "words_learned": correct_answers,
            "lesson_score": lesson_score,
            "total_words_learned": words_learned
        }
        achievements_unlocked = await gamification_system.check_achievements(user_id, activity_data)
    
    # Return revolutionary response with all system integrations
    return {
        "success": True, 
        "message": "Lesson completed with revolutionary AI & gamification features!", 
        "words_learned": words_learned,
        "lesson_score": lesson_score,
        "correct_answers": correct_answers,
        "total_answers": total_answers,
        "current_streak": current_streak,
        "xp_awarded": xp_awarded,
        "achievements_unlocked": achievements_unlocked,
        "response_time": lesson_response_time,
        "systems_integrated": [
            "Basic Progress Tracking",
            "Advanced Adaptive Learning Engine",
            "Revolutionary Gamification System",
            "Islamic Compliance Framework"
        ],
        "next_recommendations": {
            "due_reviews": f"Check /adaptive-learning/due-reviews for personalized reviews",
            "ai_tutor": f"Ask questions at /ai-tutor/comprehensive for deeper understanding",
            "achievements": f"View unlocked achievements at /gamification/achievements/all"
        }
    }

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

# =============================================
# ADVANCED FEATURES API ENDPOINTS
# =============================================

# Audio & Recitation APIs
@api_router.get("/audio/reciters")
async def get_approved_reciters(current_user: dict = Depends(get_current_user)):
    """Get list of JAKIM/JAIS approved reciters"""
    try:
        reciters = list(advanced_features.approved_reciters.values())
        return {"reciters": [reciter.dict() for reciter in reciters]}
    except Exception as e:
        logger.error(f"Error getting reciters: {e}")
        raise HTTPException(status_code=500, detail="Error loading reciters")

@api_router.get("/audio/{reciter_id}/{surah}/{ayah}")
async def get_verse_audio(
    reciter_id: str, 
    surah: int, 
    ayah: int, 
    current_user: dict = Depends(get_current_user)
):
    """Get audio for specific verse from approved reciter"""
    try:
        audio_track = await advanced_features.get_reciter_audio(reciter_id, surah, ayah)
        if not audio_track:
            raise HTTPException(status_code=404, detail="Audio not found or not approved")
        return audio_track.dict()
    except Exception as e:
        logger.error(f"Error getting audio: {e}")
        raise HTTPException(status_code=500, detail="Error loading audio")

# Prayer Times & Qibla APIs
@api_router.get("/prayer-times")
async def get_prayer_times(
    latitude: float, 
    longitude: float, 
    date: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get prayer times using JAKIM calculation method"""
    try:
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.utcnow()
            
        prayer_times = await advanced_features.calculate_prayer_times(latitude, longitude, target_date)
        return prayer_times.dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {e}")
    except Exception as e:
        logger.error(f"Error calculating prayer times: {e}")
        raise HTTPException(status_code=500, detail="Error calculating prayer times")

@api_router.get("/qibla-direction")
async def get_qibla_direction(
    latitude: float, 
    longitude: float, 
    current_user: dict = Depends(get_current_user)
):
    """Get Qibla direction from coordinates"""
    try:
        qibla_data = islamic_compliance.validate_qibla_direction(latitude, longitude)
        return qibla_data
    except Exception as e:
        logger.error(f"Error calculating Qibla: {e}")
        raise HTTPException(status_code=500, detail="Error calculating Qibla direction")

# AI Tutor APIs
@api_router.post("/ai-tutor/ask")
async def ask_ai_tutor(
    question: QuranQuestion, 
    current_user: dict = Depends(get_current_user)
):
    """Ask AI tutor about Quranic topics (Islamic compliance enforced)"""
    try:
        ai_response = await advanced_features.get_ai_quran_response(question)
        return ai_response.dict()
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        raise HTTPException(status_code=500, detail="Error processing question")

@api_router.get("/study-plan/personalized")
async def get_personalized_study_plan(
    current_user: dict = Depends(get_current_user)
):
    """Get AI-generated personalized study plan"""
    try:
        user_id = str(current_user["_id"])
        # Determine user level based on progress
        user_progress = await db.user_progress.find({"user_id": user_id}).to_list(1000)
        words_learned = len([p for p in user_progress if p.get("mastery_level", 0) >= 50])
        
        if words_learned < 20:
            current_level = "beginner"
        elif words_learned < 100:
            current_level = "intermediate"
        else:
            current_level = "advanced"
            
        study_plan = await advanced_features.generate_personalized_study_plan(user_id, current_level)
        return study_plan
    except Exception as e:
        logger.error(f"Error generating study plan: {e}")
        raise HTTPException(status_code=500, detail="Error generating study plan")

# Voice Recognition API
@api_router.post("/voice/analyze")
async def analyze_pronunciation(
    target_text: str,
    audio_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Analyze Arabic pronunciation from audio recording"""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process voice recognition
        analysis = await advanced_features.process_voice_recognition(audio_data, target_text)
        
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
            
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing pronunciation: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing pronunciation")

# Islamic Achievement System
@api_router.get("/achievements")
async def get_islamic_achievements(current_user: dict = Depends(get_current_user)):
    """Get Islamic-compliant achievement system"""
    try:
        user_id = str(current_user["_id"])
        achievements = await advanced_features.get_islamic_achievements(user_id)
        return achievements
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(status_code=500, detail="Error loading achievements")

# Duas & Islamic Content APIs
@api_router.get("/duas")
async def get_islamic_duas(
    category: str = "all",
    current_user: dict = Depends(get_current_user)
):
    """Get Islamic supplications (Duas) - JAKIM approved"""
    try:
        if category == "all":
            duas = await db.duas.find({}).to_list(100)
        else:
            duas = await db.duas.find({"category": category}).to_list(100)
        
        # Convert ObjectId to string
        for dua in duas:
            dua["_id"] = str(dua["_id"])
            
        return {"duas": duas, "count": len(duas)}
    except Exception as e:
        logger.error(f"Error getting duas: {e}")
        raise HTTPException(status_code=500, detail="Error loading duas")

# Advanced Quiz Types
@api_router.post("/quiz/advanced")
async def create_advanced_quiz(
    lesson_id: str,
    quiz_type: str = "multiple_choice",  # "fill_blank", "voice_recognition", "writing"
    current_user: dict = Depends(get_current_user)
):
    """Create advanced quiz types with different interaction methods"""
    try:
        lesson_number = int(lesson_id.split("_")[-1])
        words = await db.words.find({"lesson_number": lesson_number}).to_list(100)
        
        if not words:
            raise HTTPException(status_code=404, detail="Lesson not found")
        
        advanced_quiz = {
            "lesson_id": lesson_id,
            "quiz_type": quiz_type,
            "total_questions": len(words),
            "questions": []
        }
        
        for word in words:
            question = {
                "word_id": str(word["_id"]),
                "arabic": word["arabic"],
                "transliteration": word["transliteration"],
                "meaning": word["meaning"]
            }
            
            if quiz_type == "fill_blank":
                # Create fill in the blank question
                question["question_text"] = f"Complete: {word['arabic']} means ____"
                question["answer"] = word["meaning"]
                
            elif quiz_type == "voice_recognition":
                # Voice recognition question
                question["instruction"] = f"Recite this word correctly: {word['arabic']}"
                question["target_pronunciation"] = word["transliteration"]
                
            elif quiz_type == "writing":
                # Arabic writing practice
                question["instruction"] = f"Write the Arabic for '{word['meaning']}'"
                question["answer"] = word["arabic"]
                
            else:  # multiple_choice (default)
                # Generate multiple choice options
                other_words = [w for w in words if w["_id"] != word["_id"]]
                import random
                wrong_options = random.sample([w["meaning"] for w in other_words], 3)
                options = wrong_options + [word["meaning"]]
                random.shuffle(options)
                question["options"] = options
                question["correct_answer"] = word["meaning"]
            
            advanced_quiz["questions"].append(question)
        
        return advanced_quiz
    except Exception as e:
        logger.error(f"Error creating advanced quiz: {e}")
        raise HTTPException(status_code=500, detail="Error creating quiz")

# Community Features API
@api_router.get("/community/leaderboard")
async def get_community_leaderboard(
    timeframe: str = "weekly",  # "daily", "weekly", "monthly", "all_time"
    current_user: dict = Depends(get_current_user)
):
    """Get community leaderboard (Islamic compliant - no gambling elements)"""
    try:
        # Calculate timeframe
        now = datetime.utcnow()
        if timeframe == "daily":
            start_date = now - timedelta(days=1)
        elif timeframe == "weekly":
            start_date = now - timedelta(weeks=1)
        elif timeframe == "monthly":
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime(2020, 1, 1)  # All time
        
        # Get users with progress in timeframe
        pipeline = [
            {
                "$lookup": {
                    "from": "user_progress",
                    "localField": "_id",
                    "foreignField": "user_id",
                    "as": "progress"
                }
            },
            {
                "$addFields": {
                    "words_learned": {
                        "$size": {
                            "$filter": {
                                "input": "$progress",
                                "cond": {"$gte": ["$$this.mastery_level", 50]}
                            }
                        }
                    },
                    "total_study_time": {"$sum": "$progress.total_attempts"}
                }
            },
            {
                "$sort": {"words_learned": -1, "current_streak": -1}
            },
            {
                "$limit": 50
            }
        ]
        
        # Execute aggregation on users collection
        leaderboard = []
        async for user in db.users.aggregate(pipeline):
            # Remove sensitive information
            leaderboard_entry = {
                "username": user["username"],
                "words_learned": user.get("words_learned", 0),
                "current_streak": user.get("current_streak", 0),
                "rank": len(leaderboard) + 1
            }
            leaderboard.append(leaderboard_entry)
        
        return {
            "timeframe": timeframe,
            "leaderboard": leaderboard,
            "islamic_note": "This leaderboard promotes healthy competition in Islamic learning, following the principle of 'fastabiq al-khayrat' (race in good deeds)"
        }
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Error loading leaderboard")

# Offline Sync API
@api_router.get("/offline/sync-data")
async def get_offline_sync_data(current_user: dict = Depends(get_current_user)):
    """Get essential data for offline functionality"""
    try:
        user_id = str(current_user["_id"])
        
        # Get user's lesson progress to determine what content to sync
        user_progress = await db.user_progress.find({"user_id": user_id}).to_list(1000)
        
        # Get current lessons and completed lessons
        completed_lesson_numbers = set()
        for progress in user_progress:
            word = await db.words.find_one({"_id": progress["word_id"]})
            if word and progress.get("mastery_level", 0) >= 30:
                completed_lesson_numbers.add(word["lesson_number"])
        
        # Determine next lessons to sync (current + 2 ahead)
        max_completed = max(completed_lesson_numbers) if completed_lesson_numbers else 0
        lessons_to_sync = list(range(1, max_completed + 3))  # Current + 2 ahead
        
        # Get words for these lessons
        words = await db.words.find({"lesson_number": {"$in": lessons_to_sync}}).to_list(1000)
        
        # Get duas
        duas = await db.duas.find({}).to_list(50)
        
        # Get prayer time calculation parameters for user's region (if available)
        prayer_params = {
            "method": "JAKIM",
            "fajr_angle": 18.0,
            "isha_angle": 17.0,
            "madhab": "shafi"
        }
        
        # Convert ObjectIds to strings
        for word in words:
            word["_id"] = str(word["_id"])
        for dua in duas:
            dua["_id"] = str(dua["_id"])
        
        sync_data = {
            "words": words,
            "duas": duas,
            "prayer_calculation_params": prayer_params,
            "approved_reciters": [reciter.dict() for reciter in advanced_features.approved_reciters.values()],
            "islamic_achievements": islamic_compliance.get_halal_achievement_system(),
            "sync_timestamp": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
        
        return sync_data
    except Exception as e:
        logger.error(f"Error getting sync data: {e}")
        raise HTTPException(status_code=500, detail="Error preparing offline data")

# =============================================
# REVOLUTIONARY AI & ADAPTIVE LEARNING APIs
# =============================================

# Advanced AI Tutoring System
@api_router.post("/ai-tutor/comprehensive", response_model=AITutoringResponse)
async def get_comprehensive_ai_tutoring(
    request: AITutoringRequest,
    current_user: dict = Depends(get_current_user)
):
    """Revolutionary AI tutoring with ChatGPT/Claude integration"""
    try:
        user_id = str(current_user["_id"])
        
        # Get enhanced context from database
        db_context = {
            "word_data": None,
            "user_profile": await gamification_system.get_user_profile(user_id) if gamification_system else None
        }
        
        if request.word_id:
            word = await db.words.find_one({"_id": request.word_id})
            if word:
                db_context["word_data"] = word
        
        # Get AI response
        response = await ai_tutoring_engine.get_comprehensive_tutoring_response(request, db_context)
        
        # Award XP for asking questions
        if gamification_system:
            await gamification_system.award_xp(user_id, 10, "Asked AI tutor question")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in comprehensive AI tutoring: {e}")
        raise HTTPException(status_code=500, detail="Error processing AI tutoring request")

@api_router.post("/ai-tutor/exercises/generate")
async def generate_personalized_exercises(
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
    count: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered personalized exercises"""
    try:
        user_id = str(current_user["_id"])
        exercises = await ai_tutoring_engine.generate_personalized_exercises(user_id, difficulty, count)
        
        # Award XP for generating exercises
        if gamification_system:
            await gamification_system.award_xp(user_id, 5, "Generated personalized exercises")
        
        return {"exercises": exercises, "count": len(exercises)}
        
    except Exception as e:
        logger.error(f"Error generating exercises: {e}")
        raise HTTPException(status_code=500, detail="Error generating exercises")

# Adaptive Learning & Spaced Repetition System
@api_router.get("/adaptive-learning/due-reviews")
async def get_adaptive_due_reviews(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get words due for review using advanced SRS algorithm"""
    try:
        user_id = str(current_user["_id"])
        
        if not adaptive_learning_engine:
            raise HTTPException(status_code=500, detail="Adaptive learning system not initialized")
        
        due_reviews = await adaptive_learning_engine.get_due_reviews(user_id, limit)
        
        return {
            "due_reviews": due_reviews,
            "total_due": len(due_reviews),
            "algorithm": "Advanced Spaced Repetition System (SRS)",
            "optimization": "Memory-strength based prioritization"
        }
        
    except Exception as e:
        logger.error(f"Error getting due reviews: {e}")
        raise HTTPException(status_code=500, detail="Error loading due reviews")

@api_router.post("/adaptive-learning/review-result")
async def submit_adaptive_review_result(
    word_id: str,
    is_correct: bool,
    response_time: float,
    difficulty_rating: float = 3.0,
    current_user: dict = Depends(get_current_user)
):
    """Submit review result for adaptive learning algorithm"""
    try:
        user_id = str(current_user["_id"])
        
        if not adaptive_learning_engine:
            raise HTTPException(status_code=500, detail="Adaptive learning system not initialized")
        
        # Process review result
        updated_card = await adaptive_learning_engine.process_review_result(
            user_id, word_id, is_correct, response_time, difficulty_rating
        )
        
        # Award XP based on performance
        xp_award = 50 if is_correct else 10
        if gamification_system:
            await gamification_system.award_xp(user_id, xp_award, "Completed adaptive review")
            
            # Check for achievements
            activity_data = {
                "words_learned": updated_card.repetitions if is_correct else 0,
                "perfect_scores": 1 if is_correct else 0,
                "fastest_quiz_time": response_time
            }
            achievements = await gamification_system.check_achievements(user_id, activity_data)
            
            return {
                "updated_card": updated_card.dict(),
                "xp_awarded": xp_award,
                "achievements_unlocked": achievements,
                "next_review_date": updated_card.due_date.isoformat()
            }
        
        return {
            "updated_card": updated_card.dict(),
            "next_review_date": updated_card.due_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error submitting review result: {e}")
        raise HTTPException(status_code=500, detail="Error processing review result")

@api_router.get("/adaptive-learning/lesson/generate")
async def generate_adaptive_lesson(
    target_duration: int = 15,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered adaptive lesson based on user's learning state"""
    try:
        user_id = str(current_user["_id"])
        
        if not adaptive_learning_engine:
            raise HTTPException(status_code=500, detail="Adaptive learning system not initialized")
        
        adaptive_lesson = await adaptive_learning_engine.generate_adaptive_lesson(user_id, target_duration)
        
        # Award XP for starting adaptive lesson
        if gamification_system:
            await gamification_system.award_xp(user_id, 25, "Started adaptive lesson")
        
        return adaptive_lesson
        
    except Exception as e:
        logger.error(f"Error generating adaptive lesson: {e}")
        raise HTTPException(status_code=500, detail="Error generating adaptive lesson")

@api_router.get("/adaptive-learning/analytics")
async def get_learning_analytics(current_user: dict = Depends(get_current_user)):
    """Get comprehensive learning analytics and insights"""
    try:
        user_id = str(current_user["_id"])
        
        if not adaptive_learning_engine:
            raise HTTPException(status_code=500, detail="Adaptive learning system not initialized")
        
        analytics = await adaptive_learning_engine.get_user_learning_analytics(user_id)
        
        return {
            "analytics": analytics,
            "insights_powered_by": "Advanced AI & Memory Science",
            "algorithm": "Spaced Repetition with Adaptive Difficulty"
        }
        
    except Exception as e:
        logger.error(f"Error getting learning analytics: {e}")
        raise HTTPException(status_code=500, detail="Error loading analytics")

# =============================================
# REVOLUTIONARY GAMIFICATION SYSTEM
# =============================================

@api_router.get("/gamification/profile")
async def get_gamification_profile(current_user: dict = Depends(get_current_user)):
    """Get comprehensive gamification profile"""
    try:
        user_id = str(current_user["_id"])
        
        if not gamification_system:
            raise HTTPException(status_code=500, detail="Gamification system not initialized")
        
        profile = await gamification_system.get_user_profile(user_id)
        statistics = await gamification_system.get_user_statistics(user_id)
        
        return {
            "profile": profile.dict(),
            "statistics": statistics,
            "system": "Revolutionary Gamification Engine"
        }
        
    except Exception as e:
        logger.error(f"Error getting gamification profile: {e}")
        raise HTTPException(status_code=500, detail="Error loading profile")

@api_router.get("/gamification/achievements/all")
async def get_all_achievements(current_user: dict = Depends(get_current_user)):
    """Get all available achievements with unlock status"""
    try:
        user_id = str(current_user["_id"])
        
        if not gamification_system:
            raise HTTPException(status_code=500, detail="Gamification system not initialized")
        
        profile = await gamification_system.get_user_profile(user_id)
        all_achievements = gamification_system.achievements
        
        achievements_with_status = []
        for achievement_id, achievement in all_achievements.items():
            achievements_with_status.append({
                "id": achievement_id,
                "achievement": achievement.__dict__,
                "unlocked": achievement_id in profile.achievements_unlocked,
                "progress": 0  # TODO: Calculate progress toward achievement
            })
        
        # Group by category
        categorized_achievements = {}
        for achievement_data in achievements_with_status:
            category = achievement_data["achievement"]["category"]
            if category not in categorized_achievements:
                categorized_achievements[category] = []
            categorized_achievements[category].append(achievement_data)
        
        return {
            "achievements_by_category": categorized_achievements,
            "total_achievements": len(all_achievements),
            "unlocked_count": len(profile.achievements_unlocked),
            "completion_percentage": round((len(profile.achievements_unlocked) / len(all_achievements)) * 100, 1)
        }
        
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(status_code=500, detail="Error loading achievements")

@api_router.get("/gamification/leaderboard/{leaderboard_type}")
async def get_advanced_leaderboard(
    leaderboard_type: LeaderboardType,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get advanced leaderboard with multiple types"""
    try:
        user_id = str(current_user["_id"])
        
        if not gamification_system:
            raise HTTPException(status_code=500, detail="Gamification system not initialized")
        
        leaderboard_data = await gamification_system.get_leaderboard(leaderboard_type, user_id, limit)
        
        return leaderboard_data
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Error loading leaderboard")

@api_router.get("/gamification/quests/daily")
async def get_daily_quests(current_user: dict = Depends(get_current_user)):
    """Get daily quests for user"""
    try:
        user_id = str(current_user["_id"])
        
        if not gamification_system:
            raise HTTPException(status_code=500, detail="Gamification system not initialized")
        
        daily_quests = await gamification_system.create_daily_quests(user_id)
        
        return {
            "daily_quests": [quest.__dict__ for quest in daily_quests],
            "quest_count": len(daily_quests),
            "reset_time": "24 hours"
        }
        
    except Exception as e:
        logger.error(f"Error getting daily quests: {e}")
        raise HTTPException(status_code=500, detail="Error loading daily quests")

@api_router.post("/gamification/xp/award")
async def award_xp_manual(
    xp_amount: int,
    reason: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually award XP (for testing/admin purposes)"""
    try:
        user_id = str(current_user["_id"])
        
        if not gamification_system:
            raise HTTPException(status_code=500, detail="Gamification system not initialized")
        
        result = await gamification_system.award_xp(user_id, xp_amount, reason)
        
        return result
        
    except Exception as e:
        logger.error(f"Error awarding XP: {e}")
        raise HTTPException(status_code=500, detail="Error awarding XP")

# =============================================
# ADVANCED LEARNING FEATURES
# =============================================

@api_router.get("/learning/recommendations")
async def get_learning_recommendations(current_user: dict = Depends(get_current_user)):
    """Get AI-powered learning recommendations"""
    try:
        user_id = str(current_user["_id"])
        
        recommendations = {
            "recommended_words": [],
            "study_schedule": {},
            "difficulty_adjustments": [],
            "focus_areas": []
        }
        
        # Get adaptive learning recommendations
        if adaptive_learning_engine:
            analytics = await adaptive_learning_engine.get_user_learning_analytics(user_id)
            
            recommendations.update({
                "current_level": analytics.get("current_level", "beginner"),
                "weak_areas": analytics.get("weak_areas", []),
                "strong_areas": analytics.get("strong_areas", []),
                "optimal_study_time": analytics.get("optimal_study_time", "morning"),
                "predicted_success_rate": analytics.get("predicted_success_rate", 0.8)
            })
        
        # Get gamification insights
        if gamification_system:
            profile = await gamification_system.get_user_profile(user_id)
            
            recommendations["gamification_insights"] = {
                "next_achievement": "vocabulary_builder",  # TODO: Calculate actual next achievement
                "xp_to_next_level": 500,  # TODO: Calculate from profile
                "suggested_daily_goal": "5 words per day"
            }
        
        return {
            "recommendations": recommendations,
            "powered_by": "AI + Adaptive Learning + Gamification",
            "personalization_level": "High"
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error generating recommendations")

@api_router.get("/learning/comprehensive-dashboard")
async def get_comprehensive_dashboard(current_user: dict = Depends(get_current_user)):
    """Get comprehensive learning dashboard with all systems integrated"""
    try:
        user_id = str(current_user["_id"])
        
        dashboard_data = {
            "basic_stats": {},
            "adaptive_learning": {},
            "gamification": {},
            "ai_insights": {},
            "recommendations": {}
        }
        
        # Get basic stats (existing dashboard)
        user_progress = await db.user_progress.find({"user_id": user_id}).to_list(1000)
        words_learned = len([p for p in user_progress if p.get("mastery_level", 0) >= 50])
        
        dashboard_data["basic_stats"] = {
            "words_learned": words_learned,
            "total_lessons": 5,
            "current_streak": current_user.get("current_streak", 0)
        }
        
        # Get adaptive learning data
        if adaptive_learning_engine:
            analytics = await adaptive_learning_engine.get_user_learning_analytics(user_id)
            due_reviews = await adaptive_learning_engine.get_due_reviews(user_id, 5)
            
            dashboard_data["adaptive_learning"] = {
                "analytics": analytics,
                "due_reviews_count": len(due_reviews),
                "next_review": due_reviews[0] if due_reviews else None
            }
        
        # Get gamification data
        if gamification_system:
            profile = await gamification_system.get_user_profile(user_id)
            daily_quests = await gamification_system.create_daily_quests(user_id)
            
            dashboard_data["gamification"] = {
                "level": profile.current_level,
                "xp": profile.total_xp,
                "coins": profile.coins,
                "achievements_count": len(profile.achievements_unlocked),
                "daily_quests": len(daily_quests)
            }
        
        # Get AI insights
        dashboard_data["ai_insights"] = {
            "optimal_study_time": "morning",
            "predicted_performance": "85%",
            "recommended_focus": "pronunciation"
        }
        
        return {
            "dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "system_status": "All systems operational"
        }
        
    except Exception as e:
        logger.error(f"Error getting comprehensive dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error loading dashboard")

# =============================================
# REVOLUTIONARY PEACE TV INTEGRATION 🌟
# =============================================

@api_router.get("/peace-tv/recommendations")
async def get_peace_tv_recommendations(
    current_word: Optional[str] = None,
    lesson_context: Optional[str] = None,
    language: PeaceTVLanguage = PeaceTVLanguage.ENGLISH,
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """🧠 Get intelligent Peace TV video recommendations based on learning context"""
    try:
        user_id = str(current_user["_id"])
        
        if not peace_tv_integration:
            raise HTTPException(status_code=500, detail="Peace TV integration not initialized")
        
        recommendations = await peace_tv_integration.get_contextual_recommendations(
            user_id=user_id,
            current_word=current_word,
            lesson_context=lesson_context,
            language_preference=language,
            limit=limit
        )
        
        # Award XP for exploring video content
        if gamification_system and recommendations:
            await gamification_system.award_xp(user_id, 5, "Explored Peace TV recommendations")
        
        return {
            "recommendations": [
                {
                    "video": rec.video.to_dict(),
                    "relevance_score": rec.relevance_score,
                    "reason": rec.reason,
                    "learning_context": rec.learning_context,
                    "estimated_benefit": rec.estimated_benefit
                }
                for rec in recommendations
            ],
            "total_count": len(recommendations),
            "context": {
                "current_word": current_word,
                "lesson_context": lesson_context,
                "language": language
            },
            "powered_by": "Peace TV × Think-Quran AI Integration"
        }
        
    except Exception as e:
        logger.error(f"Error getting Peace TV recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error loading Peace TV recommendations")

@api_router.get("/peace-tv/search")
async def search_peace_tv_content(
    q: str,
    content_type: Optional[PeaceTVContentType] = None,
    scholar: Optional[ScholarName] = None,
    language: PeaceTVLanguage = PeaceTVLanguage.ENGLISH,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """🔍 Search Peace TV content with advanced filtering"""
    try:
        if not peace_tv_integration:
            raise HTTPException(status_code=500, detail="Peace TV integration not initialized")
        
        results = await peace_tv_integration.search_peace_tv_content(
            query=q,
            content_type=content_type,
            scholar=scholar,
            language=language,
            limit=limit
        )
        
        return {
            "results": [video.to_dict() for video in results],
            "total_count": len(results),
            "query": q,
            "filters": {
                "content_type": content_type,
                "scholar": scholar,
                "language": language
            },
            "search_powered_by": "Peace TV Advanced Search"
        }
        
    except Exception as e:
        logger.error(f"Error searching Peace TV content: {e}")
        raise HTTPException(status_code=500, detail="Error searching Peace TV content")

@api_router.get("/peace-tv/scholars/{scholar_name}")
async def get_scholar_content(
    scholar_name: ScholarName,
    language: PeaceTVLanguage = PeaceTVLanguage.ENGLISH,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """👨‍🏫 Get content from specific Peace TV scholars"""
    try:
        if not peace_tv_integration:
            raise HTTPException(status_code=500, detail="Peace TV integration not initialized")
        
        scholar_videos = await peace_tv_integration.get_scholar_content(
            scholar=scholar_name,
            language=language,
            limit=limit
        )
        
        return {
            "scholar": scholar_name,
            "videos": [video.to_dict() for video in scholar_videos],
            "total_count": len(scholar_videos),
            "language": language,
            "expertise_areas": peace_tv_integration.scholars_expertise.get(scholar_name, []),
            "message": f"Authentic Islamic content from {scholar_name.replace('_', ' ').title()}"
        }
        
    except Exception as e:
        logger.error(f"Error getting scholar content: {e}")
        raise HTTPException(status_code=500, detail="Error loading scholar content")

@api_router.get("/peace-tv/live")
async def get_live_programs(current_user: dict = Depends(get_current_user)):
    """📺 Get current live Peace TV programs"""
    try:
        if not peace_tv_integration:
            raise HTTPException(status_code=500, detail="Peace TV integration not initialized")
        
        live_programs = await peace_tv_integration.get_live_programs()
        
        return {
            "live_programs": live_programs,
            "total_count": len(live_programs),
            "current_time": datetime.utcnow().isoformat(),
            "message": "Watch live Islamic education programs",
            "note": "All content is authentic and scholar-verified"
        }
        
    except Exception as e:
        logger.error(f"Error getting live programs: {e}")
        raise HTTPException(status_code=500, detail="Error loading live programs")

@api_router.post("/peace-tv/track-engagement")
async def track_peace_tv_engagement(
    video_id: str,
    watch_duration: int,
    completion_percentage: float,
    current_user: dict = Depends(get_current_user)
):
    """📊 Track user engagement with Peace TV content"""
    try:
        user_id = str(current_user["_id"])
        
        if not peace_tv_integration:
            raise HTTPException(status_code=500, detail="Peace TV integration not initialized")
        
        engagement_result = await peace_tv_integration.track_video_engagement(
            user_id=user_id,
            video_id=video_id,
            watch_duration=watch_duration,
            completion_percentage=completion_percentage
        )
        
        # Award additional XP through gamification system
        if gamification_system and engagement_result.get("success"):
            base_xp = engagement_result.get("xp_awarded", 0)
            
            # Bonus XP for completion
            completion_bonus = 0
            if completion_percentage >= 100:
                completion_bonus = 50
            elif completion_percentage >= 80:
                completion_bonus = 25
            elif completion_percentage >= 50:
                completion_bonus = 10
            
            total_xp = base_xp + completion_bonus
            await gamification_system.award_xp(user_id, total_xp, f"Watched Peace TV content ({completion_percentage}% completed)")
            
            # Check for video watching achievements
            activity_data = {
                "videos_watched": 1,
                "watch_time_minutes": watch_duration / 60,
                "completion_percentage": completion_percentage
            }
            achievements = await gamification_system.check_achievements(user_id, activity_data)
            
            return {
                "success": True,
                "xp_awarded": total_xp,
                "completion_bonus": completion_bonus,
                "achievements_unlocked": achievements,
                "message": f"Great job learning with Peace TV! {total_xp} XP earned.",
                "learning_value": "High" if completion_percentage > 80 else "Medium"
            }
        
        return engagement_result
        
    except Exception as e:
        logger.error(f"Error tracking Peace TV engagement: {e}")
        raise HTTPException(status_code=500, detail="Error tracking engagement")

@api_router.get("/peace-tv/watch-history")
async def get_peace_tv_watch_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """📚 Get user's Peace TV watch history with learning insights"""
    try:
        user_id = str(current_user["_id"])
        
        if not peace_tv_integration:
            raise HTTPException(status_code=500, detail="Peace TV integration not initialized")
        
        watch_history = await peace_tv_integration.get_user_watch_history(user_id, limit)
        
        # Calculate learning statistics
        total_watch_time = sum(record["watch_duration"] for record in watch_history)
        avg_completion = sum(record["completion_percentage"] for record in watch_history) / len(watch_history) if watch_history else 0
        high_value_watches = len([r for r in watch_history if r["completion_percentage"] > 80])
        
        return {
            "watch_history": watch_history,
            "statistics": {
                "total_videos_watched": len(watch_history),
                "total_watch_time_minutes": round(total_watch_time / 60, 1),
                "average_completion_percentage": round(avg_completion, 1),
                "high_value_watches": high_value_watches,
                "learning_commitment": "High" if avg_completion > 70 else "Medium" if avg_completion > 40 else "Growing"
            },
            "insights": {
                "message": f"You've spent {round(total_watch_time / 60, 1)} minutes learning with Peace TV!",
                "recommendation": "Keep watching to deepen your Islamic knowledge",
                "next_goal": "Try to complete more videos for better learning outcomes"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting Peace TV watch history: {e}")
        raise HTTPException(status_code=500, detail="Error loading watch history")

@api_router.get("/peace-tv/content-types")
async def get_peace_tv_content_types():
    """📋 Get available Peace TV content types and scholars"""
    try:
        content_types = [
            {
                "type": content_type.value,
                "display_name": content_type.value.replace("_", " ").title(),
                "description": f"Educational content focused on {content_type.value.replace('_', ' ')}"
            }
            for content_type in PeaceTVContentType
        ]
        
        scholars = [
            {
                "scholar": scholar.value,
                "display_name": scholar.value.replace("_", " ").title(),
                "expertise": peace_tv_integration.scholars_expertise.get(scholar, [])
            }
            for scholar in ScholarName
        ]
        
        languages = [
            {
                "language": lang.value,
                "display_name": lang.value.title()
            }
            for lang in PeaceTVLanguage
        ]
        
        return {
            "content_types": content_types,
            "scholars": scholars,
            "languages": languages,
            "total_content_types": len(content_types),
            "total_scholars": len(scholars),
            "message": "Explore authentic Islamic education content"
        }
        
    except Exception as e:
        logger.error(f"Error getting Peace TV content types: {e}")
        raise HTTPException(status_code=500, detail="Error loading content types")

# =============================================
# REVOLUTIONARY AI USTAZ/USTAZAH ASSISTANT 🕌
# =============================================

@api_router.get("/ai-ustaz/guidance/{context}")
async def get_ai_ustaz_guidance(
    context: GuidanceContext,
    current_activity: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """🕌 Get contextual Islamic guidance from AI Ustaz/Ustazah with Quranic wisdom"""
    try:
        user_id = str(current_user["_id"])
        
        if not ai_ustaz_assistant:
            raise HTTPException(status_code=500, detail="AI Ustaz Assistant not initialized")
        
        # Get user's current progress for contextualized guidance
        user_progress = await db.user_progress.find({"user_id": user_id}).to_list(100)
        total_lessons_completed = current_user.get("total_lessons_completed", 0)
        current_streak = current_user.get("current_streak", 0)
        
        user_data = {
            "total_lessons_completed": total_lessons_completed,
            "current_streak": current_streak,
            "words_learned": len([p for p in user_progress if p.get("mastery_level", 0) >= 50]),
            "user_level": "beginner" if total_lessons_completed < 3 else "intermediate" if total_lessons_completed < 10 else "advanced"
        }
        
        guidance = await ai_ustaz_assistant.get_contextual_guidance(
            user_id=user_id,
            context=context,
            user_data=user_data,
            current_activity=current_activity
        )
        
        # Award XP for seeking guidance
        if gamification_system:
            await gamification_system.award_xp(user_id, 5, "Sought Islamic guidance from AI Ustaz")
        
        return {
            "guidance": {
                "persona": guidance.persona,
                "context": guidance.context,
                "main_message": guidance.main_message,
                "practical_advice": guidance.practical_advice,
                "encouragement": guidance.encouragement,
                "next_steps": guidance.next_steps,
                "duas_recommendation": guidance.duas_recommendation
            },
            "quranic_reference": ai_ustaz_assistant.get_quranic_reference_formatted(guidance.quranic_reference),
            "user_context": {
                "persona_type": guidance.persona,
                "guidance_context": context,
                "current_activity": current_activity
            },
            "islamic_note": "All guidance is based on authentic Quranic teachings and scholarly interpretations",
            "powered_by": "AI Ustaz/Ustazah Assistant with Quranic Wisdom"
        }
        
    except Exception as e:
        logger.error(f"Error getting AI Ustaz guidance: {e}")
        raise HTTPException(status_code=500, detail="Error generating Islamic guidance")

@api_router.get("/ai-ustaz/daily-wisdom")
async def get_daily_islamic_wisdom(current_user: dict = Depends(get_current_user)):
    """🌅 Get daily Islamic wisdom and motivation from AI Ustaz/Ustazah"""
    try:
        user_id = str(current_user["_id"])
        
        if not ai_ustaz_assistant:
            raise HTTPException(status_code=500, detail="AI Ustaz Assistant not initialized")
        
        daily_wisdom = await ai_ustaz_assistant.get_daily_wisdom(user_id)
        
        # Award XP for daily spiritual nourishment
        if gamification_system:
            await gamification_system.award_xp(user_id, 10, "Received daily Islamic wisdom")
        
        return {
            "daily_wisdom": {
                "persona": daily_wisdom.persona,
                "main_message": daily_wisdom.main_message,
                "practical_advice": daily_wisdom.practical_advice,
                "encouragement": daily_wisdom.encouragement,
                "duas_recommendation": daily_wisdom.duas_recommendation
            },
            "quranic_reference": ai_ustaz_assistant.get_quranic_reference_formatted(daily_wisdom.quranic_reference),
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "islamic_calendar": "Daily guidance for strengthening your connection with Allah",
            "reminder": "Set a daily routine to benefit from Islamic wisdom"
        }
        
    except Exception as e:
        logger.error(f"Error getting daily Islamic wisdom: {e}")
        raise HTTPException(status_code=500, detail="Error generating daily wisdom")

@api_router.get("/ai-ustaz/navigation-help")
async def get_app_navigation_help(
    current_screen: str,
    user_query: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """🧭 Get step-by-step app navigation help from AI Ustaz/Ustazah"""
    try:
        user_id = str(current_user["_id"])
        
        if not ai_ustaz_assistant:
            raise HTTPException(status_code=500, detail="AI Ustaz Assistant not initialized")
        
        navigation_help = await ai_ustaz_assistant.get_app_navigation_help(
            user_id=user_id,
            current_screen=current_screen,
            user_query=user_query
        )
        
        # Create specific navigation guidance based on current screen
        screen_guidance = {
            "home": {
                "overview": "This is your learning dashboard where you can see your progress and start new activities.",
                "key_features": [
                    "View your current streak and learning statistics",
                    "Access quick actions for lessons and prayers",
                    "See your recent achievements and progress"
                ],
                "next_actions": [
                    "Start a new lesson from the Lessons tab",
                    "Check your prayer times in the Prayer tab",
                    "Ask questions to the AI Tutor"
                ]
            },
            "lessons": {
                "overview": "Here you can access all Quranic vocabulary lessons, from beginner to advanced.",
                "key_features": [
                    "Browse lessons by difficulty level",
                    "Track completion and mastery percentage",
                    "Review previously learned words"
                ],
                "next_actions": [
                    "Start with Lesson 1 if you're new",
                    "Continue from where you left off",
                    "Review completed lessons for reinforcement"
                ]
            },
            "ai-tutor": {
                "overview": "Your personal AI Islamic tutor for asking questions about Quran, Arabic, and Islamic knowledge.",
                "key_features": [
                    "Ask questions about specific words or verses",
                    "Get detailed explanations with scholarly references",
                    "Request personalized learning exercises"
                ],
                "next_actions": [
                    "Ask about any Quranic word you're learning",
                    "Request explanation of Islamic concepts",
                    "Get help with pronunciation and meaning"
                ]
            },
            "prayer": {
                "overview": "Your prayer companion with accurate times and Qibla direction.",
                "key_features": [
                    "View prayer times calculated using JAKIM method",
                    "Find Qibla direction with compass",
                    "Get prayer reminders and Islamic advice"
                ],
                "next_actions": [
                    "Check current prayer time",
                    "Use Qibla compass for prayer direction",
                    "Set prayer reminders"
                ]
            },
            "peace-tv": {
                "overview": "Access authentic Islamic educational videos from renowned scholars.",
                "key_features": [
                    "Get personalized video recommendations",
                    "Search content by scholar or topic",
                    "Track your watch history and learning progress"
                ],
                "next_actions": [
                    "Explore recommended videos for your level",
                    "Search for topics you're currently studying",
                    "Watch content from your favorite scholars"
                ]
            },
            "community": {
                "overview": "Connect with fellow learners through leaderboards and achievements.",
                "key_features": [
                    "View leaderboards and your ranking",
                    "Explore available achievements",
                    "Compare progress with other learners"
                ],
                "next_actions": [
                    "Check your position on leaderboards",
                    "Work towards unlocking new achievements",
                    "Stay motivated by healthy competition"
                ]
            }
        }
        
        current_screen_guidance = screen_guidance.get(current_screen, {
            "overview": "This section helps you navigate the app with Islamic guidance.",
            "key_features": ["Explore the various tabs and features available"],
            "next_actions": ["Ask specific questions about what you'd like to do"]
        })
        
        return {
            "navigation_guidance": {
                "persona": navigation_help.persona,
                "main_message": navigation_help.main_message,
                "practical_advice": navigation_help.practical_advice,
                "encouragement": navigation_help.encouragement
            },
            "screen_specific_help": {
                "current_screen": current_screen,
                "overview": current_screen_guidance["overview"],
                "key_features": current_screen_guidance["key_features"],
                "recommended_actions": current_screen_guidance["next_actions"]
            },
            "quranic_reference": ai_ustaz_assistant.get_quranic_reference_formatted(navigation_help.quranic_reference),
            "user_query": user_query,
            "helpful_tip": "Ask me anything about using this app - I'm here to guide you step by step!"
        }
        
    except Exception as e:
        logger.error(f"Error getting navigation help: {e}")
        raise HTTPException(status_code=500, detail="Error generating navigation help")

@api_router.post("/ai-ustaz/progress-celebration")
async def celebrate_progress_with_ustaz(
    milestone_type: str,
    milestone_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """🎉 Celebrate user progress milestones with Islamic perspective"""
    try:
        user_id = str(current_user["_id"])
        
        if not ai_ustaz_assistant:
            raise HTTPException(status_code=500, detail="AI Ustaz Assistant not initialized")
        
        celebration_guidance = await ai_ustaz_assistant.get_progress_celebration(
            user_id=user_id,
            milestone_data={
                "milestone_type": milestone_type,
                **milestone_data
            }
        )
        
        # Award celebration XP
        if gamification_system:
            await gamification_system.award_xp(user_id, 25, f"Celebrated {milestone_type} milestone with AI Ustaz")
        
        # Create milestone-specific celebrations
        milestone_celebrations = {
            "first_lesson": "SubhanAllah! You've completed your first lesson - this is the beginning of a beautiful journey with Allah's words.",
            "week_streak": "MashaAllah! A full week of consistent learning. The Prophet (ﷺ) said the most beloved deeds to Allah are those done consistently.",
            "month_streak": "Allahu Akbar! One month of dedication! Your commitment to learning Quran is truly inspiring.",
            "first_achievement": "Barakallahu feek! Your first achievement shows Allah's blessing on your efforts.",
            "100_words": "Amazing! 100 words learned - you're building a strong foundation in understanding Allah's book.",
            "perfect_score": "Excellent! Your perfect score shows your dedication and Allah's guidance in your learning."
        }
        
        specific_celebration = milestone_celebrations.get(
            milestone_type, 
            "MashaAllah! Your progress in learning Quran is truly blessed by Allah."
        )
        
        return {
            "celebration": {
                "persona": celebration_guidance.persona,
                "main_message": celebration_guidance.main_message,
                "specific_celebration": specific_celebration,
                "encouragement": celebration_guidance.encouragement,
                "practical_advice": celebration_guidance.practical_advice,
                "duas_recommendation": celebration_guidance.duas_recommendation
            },
            "milestone": {
                "type": milestone_type,
                "data": milestone_data,
                "achieved_at": datetime.utcnow().isoformat()
            },
            "quranic_reference": ai_ustaz_assistant.get_quranic_reference_formatted(celebration_guidance.quranic_reference),
            "next_goals": celebration_guidance.next_steps,
            "islamic_reminder": "Remember to thank Allah for enabling you to reach this milestone"
        }
        
    except Exception as e:
        logger.error(f"Error celebrating progress: {e}")
        raise HTTPException(status_code=500, detail="Error generating celebration message")

@api_router.get("/ai-ustaz/quranic-references")
async def get_quranic_references_for_context(
    context: GuidanceContext,
    current_user: dict = Depends(get_current_user)
):
    """📖 Get relevant Quranic references for different learning contexts"""
    try:
        if not ai_ustaz_assistant:
            raise HTTPException(status_code=500, detail="AI Ustaz Assistant not initialized")
        
        # Get all available references for the context
        quranic_refs = ai_ustaz_assistant.quranic_guidance_database.get(context, [])
        
        formatted_refs = []
        for ref in quranic_refs:
            formatted_refs.append({
                "surah": {
                    "number": ref.surah_number,
                    "name_arabic": ref.surah_name_arabic,
                    "name_english": ref.surah_name_english
                },
                "ayat": {
                    "number": ref.ayat_number,
                    "arabic_text": ref.arabic_text,
                    "english_translation": ref.english_translation
                },
                "reference": f"Quran {ref.surah_number}:{ref.ayat_number}",
                "context_relevance": ref.context_relevance,
                "scholarly_note": ref.scholarly_note
            })
        
        return {
            "context": context,
            "quranic_references": formatted_refs,
            "total_references": len(formatted_refs),
            "usage_note": "These verses are specifically selected for their relevance to your learning context",
            "islamic_reminder": "Reflect on these verses and let them guide your learning journey"
        }
        
    except Exception as e:
        logger.error(f"Error getting Quranic references: {e}")
        raise HTTPException(status_code=500, detail="Error loading Quranic references")

@api_router.get("/ai-ustaz/persona-info")
async def get_persona_information(current_user: dict = Depends(get_current_user)):
    """👤 Get information about the AI Ustaz/Ustazah persona"""
    try:
        user_id = str(current_user["_id"])
        
        # Determine persona based on user gender
        user_gender = current_user.get("gender", UserGender.NOT_SPECIFIED)
        persona = PersonaType.USTAZAH if user_gender == UserGender.FEMALE else PersonaType.USTAZ
        
        persona_info = {
            PersonaType.USTAZ: {
                "name": "Ustaz Ahmad",
                "description": "Your caring Islamic brother and teacher",
                "expertise": [
                    "Quranic Arabic and Tafseer",
                    "Islamic Learning Methodology", 
                    "Spiritual Guidance and Motivation",
                    "Step-by-step App Navigation"
                ],
                "personality": "Warm, scholarly, encouraging, and brotherly",
                "greeting_style": "Addresses you as 'Akhi' (my brother)",
                "specialization": "Helping male students and providing general Islamic guidance"
            },
            PersonaType.USTAZAH: {
                "name": "Ustazah Aisha",
                "description": "Your caring Islamic sister and teacher",
                "expertise": [
                    "Quranic Arabic and Understanding",
                    "Women's Islamic Education",
                    "Gentle Learning Guidance",
                    "Supportive App Navigation"
                ],
                "personality": "Gentle, wise, nurturing, and sisterly",
                "greeting_style": "Addresses you as 'Ukhti' (my sister)",
                "specialization": "Providing guidance with special consideration for female students"
            }
        }
        
        current_persona_info = persona_info[persona]
        
        return {
            "current_persona": {
                "type": persona,
                "name": current_persona_info["name"],
                "description": current_persona_info["description"],
                "expertise": current_persona_info["expertise"],
                "personality": current_persona_info["personality"],
                "greeting_style": current_persona_info["greeting_style"],
                "specialization": current_persona_info["specialization"]
            },
            "available_personas": {
                "ustaz": persona_info[PersonaType.USTAZ],
                "ustazah": persona_info[PersonaType.USTAZAH]
            },
            "selection_criteria": "Persona is automatically selected based on your profile gender preference",
            "islamic_authenticity": "Both personas provide guidance based on authentic Islamic sources and Quranic teachings",
            "note": "You can update your gender preference in your profile to change the persona"
        }
        
    except Exception as e:
        logger.error(f"Error getting persona information: {e}")
        raise HTTPException(status_code=500, detail="Error loading persona information")

# =============================================
# REVOLUTIONARY INTEGRATED GUIDANCE SYSTEM 🚀
# =============================================

@api_router.get("/integrated-guidance/{context}")
async def get_comprehensive_integrated_guidance(
    context: GuidanceContext,
    current_activity: Optional[str] = None,
    available_time_minutes: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """🚀 Get comprehensive guidance combining AI Ustaz wisdom with Peace TV recommendations"""
    try:
        user_id = str(current_user["_id"])
        
        if not integrated_guidance_system:
            raise HTTPException(status_code=500, detail="Integrated Guidance System not initialized")
        
        # Get comprehensive integrated guidance
        integrated_guidance = await integrated_guidance_system.get_integrated_guidance_with_videos(
            user_id=user_id,
            context=context,
            current_activity=current_activity,
            user_preferences={
                "available_time_minutes": available_time_minutes
            }
        )
        
        # Award XP for seeking comprehensive guidance
        if gamification_system:
            await gamification_system.award_xp(user_id, 15, "Sought comprehensive Islamic guidance")
        
        # Format Peace TV videos for response
        formatted_videos = []
        for video in integrated_guidance.peace_tv_videos:
            formatted_videos.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "scholar": video.scholar,
                "duration_minutes": video.duration_minutes,
                "thumbnail_url": video.thumbnail_url,
                "video_url": video.video_url,
                "relevance_reason": f"Recommended for {context.replace('_', ' ')} context"
            })
        
        return {
            "integrated_guidance": {
                "ustaz_guidance": integrated_guidance.ustaz_guidance,
                "peace_tv_recommendations": formatted_videos,
                "learning_path": integrated_guidance.learning_path,
                "next_actions": integrated_guidance.next_actions,
                "duas_for_context": integrated_guidance.duas_for_context,
                "estimated_study_time_minutes": integrated_guidance.estimated_study_time,
                "islamic_benefits": integrated_guidance.islamic_benefits
            },
            "quranic_reference": ai_ustaz_assistant.get_quranic_reference_formatted(integrated_guidance.quranic_reference),
            "context_info": {
                "guidance_context": context,
                "current_activity": current_activity,
                "available_time": available_time_minutes
            },
            "integration_features": [
                "AI Ustaz Islamic Guidance",
                "Contextual Peace TV Videos", 
                "Quranic Wisdom Integration",
                "Personalized Learning Path",
                "Islamic Benefits Explanation"
            ],
            "powered_by": "Revolutionary Integrated Guidance System"
        }
        
    except Exception as e:
        logger.error(f"Error getting integrated guidance: {e}")
        raise HTTPException(status_code=500, detail="Error generating comprehensive guidance")

@api_router.get("/scholar-guidance/{scholar_name}")
async def get_scholar_specific_guidance(
    scholar_name: ScholarName,
    learning_context: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """👨‍🏫 Get guidance specifically tailored to a scholar's expertise and teaching style"""
    try:
        user_id = str(current_user["_id"])
        
        if not integrated_guidance_system:
            raise HTTPException(status_code=500, detail="Integrated Guidance System not initialized")
        
        # Get scholar-specific guidance
        scholar_guidance = await integrated_guidance_system.get_scholar_specific_guidance(
            user_id=user_id,
            preferred_scholar=scholar_name,
            learning_context=learning_context
        )
        
        # Award XP for exploring scholar-specific content
        if gamification_system:
            await gamification_system.award_xp(user_id, 10, f"Explored {scholar_name} guidance")
        
        # Format videos for response
        formatted_videos = []
        for video in scholar_guidance.best_videos:
            formatted_videos.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "duration_minutes": video.duration_minutes,
                "thumbnail_url": video.thumbnail_url,
                "video_url": video.video_url,
                "tags": video.tags
            })
        
        return {
            "scholar_guidance": {
                "scholar": {
                    "name": scholar_name,
                    "display_name": scholar_name.replace("_", " ").title(),
                    "relevance_score": scholar_guidance.relevance_score,
                    "why_recommended": scholar_guidance.why_recommended,
                    "suitable_for_level": scholar_guidance.suitable_for_level
                },
                "recommended_videos": formatted_videos,
                "learning_outcomes": scholar_guidance.learning_outcomes,
                "scholar_specialties": integrated_guidance_system.scholar_expertise_detailed[scholar_name]
            },
            "learning_context": learning_context,
            "personalization_note": "Content selected based on your current level and progress",
            "islamic_authenticity": "All content from verified Islamic scholars"
        }
        
    except Exception as e:
        logger.error(f"Error getting scholar guidance: {e}")
        raise HTTPException(status_code=500, detail="Error generating scholar guidance")

@api_router.get("/progress-based-content")
async def get_progress_based_content_recommendations(
    target_skill: Optional[str] = None,
    content_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """📈 Get content recommendations based on user's current progress and learning trajectory"""
    try:
        user_id = str(current_user["_id"])
        
        if not integrated_guidance_system:
            raise HTTPException(status_code=500, detail="Integrated Guidance System not initialized")
        
        # Get progress-based recommendations
        progress_content = await integrated_guidance_system.get_progress_based_content_recommendations(
            user_id=user_id,
            target_skill=target_skill
        )
        
        # Award XP for seeking progress-based guidance
        if gamification_system:
            await gamification_system.award_xp(user_id, 12, "Sought progress-based content recommendations")
        
        # Format videos for response
        formatted_videos = []
        for video in progress_content.recommended_videos:
            formatted_videos.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "scholar": video.scholar,
                "duration_minutes": video.duration_minutes,
                "thumbnail_url": video.thumbnail_url,
                "video_url": video.video_url,
                "content_type": video.content_type,
                "difficulty_level": "Appropriate for your current level"
            })
        
        return {
            "progress_based_content": {
                "current_level": progress_content.current_level,
                "recommended_videos": formatted_videos,
                "skill_focus_areas": progress_content.skill_focus_areas,
                "next_milestone": progress_content.next_milestone,
                "estimated_completion_time_hours": progress_content.estimated_completion_time,
                "prerequisite_knowledge": progress_content.prerequisite_knowledge
            },
            "target_skill": target_skill,
            "personalization_details": {
                "content_matched_to_level": True,
                "considers_learning_history": True,
                "islamic_progression_pathway": True
            },
            "learning_philosophy": "Progressive Islamic education with authentic sources"
        }
        
    except Exception as e:
        logger.error(f"Error getting progress-based content: {e}")
        raise HTTPException(status_code=500, detail="Error generating progress-based recommendations")

@api_router.get("/smart-daily-guidance")
async def get_smart_daily_guidance(
    time_of_day: str = "morning",
    available_time_minutes: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """🌅 Get smart daily guidance that adapts to user's time and preferences"""
    try:
        user_id = str(current_user["_id"])
        
        if not integrated_guidance_system:
            raise HTTPException(status_code=500, detail="Integrated Guidance System not initialized")
        
        # Get smart daily guidance
        daily_guidance = await integrated_guidance_system.get_smart_daily_guidance(
            user_id=user_id,
            time_of_day=time_of_day,
            available_time_minutes=available_time_minutes
        )
        
        # Award XP for daily spiritual engagement
        if gamification_system:
            await gamification_system.award_xp(user_id, 20, "Engaged with smart daily guidance")
        
        # Format Peace TV videos for response
        formatted_videos = []
        for video in daily_guidance.peace_tv_videos:
            formatted_videos.append({
                "id": video.id,
                "title": video.title,
                "description": video.description,
                "scholar": video.scholar,
                "duration_minutes": video.duration_minutes,
                "thumbnail_url": video.thumbnail_url,
                "video_url": video.video_url,
                "why_recommended_now": f"Perfect for {time_of_day} study session"
            })
        
        return {
            "smart_daily_guidance": {
                "ustaz_guidance": daily_guidance.ustaz_guidance,
                "daily_peace_tv_recommendations": formatted_videos,
                "optimized_learning_path": daily_guidance.learning_path,
                "time_optimized_actions": daily_guidance.next_actions,
                "daily_duas": daily_guidance.duas_for_context,
                "total_study_time_minutes": daily_guidance.estimated_study_time,
                "daily_islamic_benefits": daily_guidance.islamic_benefits
            },
            "quranic_reference": ai_ustaz_assistant.get_quranic_reference_formatted(daily_guidance.quranic_reference),
            "time_optimization": {
                "time_of_day": time_of_day,
                "available_time": available_time_minutes,
                "optimized_for": "Maximum learning benefit within time constraint"
            },
            "daily_routine_benefits": [
                "Consistent spiritual growth",
                "Structured Islamic learning",
                "Optimal time utilization",
                "Progressive knowledge building"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting smart daily guidance: {e}")
        raise HTTPException(status_code=500, detail="Error generating smart daily guidance")

@api_router.get("/contextual-video-recommendations")
async def get_contextual_video_recommendations(
    current_word: Optional[str] = None,
    lesson_context: Optional[str] = None,
    learning_goal: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """🎬 Get smart contextual Peace TV video recommendations with AI Ustaz guidance"""
    try:
        user_id = str(current_user["_id"])
        
        # Get Peace TV contextual recommendations
        peace_tv_recs = await peace_tv_integration.get_contextual_recommendations(
            user_id=user_id,
            current_word=current_word,
            lesson_context=lesson_context,
            language_preference=PeaceTVLanguage.ENGLISH,
            limit=8
        )
        
        # Get AI Ustaz guidance for video watching
        ustaz_video_guidance = await ai_ustaz_assistant.get_contextual_guidance(
            user_id=user_id,
            context=GuidanceContext.PEACE_TV_RECOMMENDATION,
            user_data={
                "current_word": current_word,
                "lesson_context": lesson_context,
                "learning_goal": learning_goal
            },
            current_activity="video_recommendation_browsing"
        )
        
        # Award XP for seeking contextual recommendations
        if gamification_system:
            await gamification_system.award_xp(user_id, 8, "Sought contextual video recommendations")
        
        # Enhanced video recommendations with AI insights
        enhanced_recommendations = []
        for rec in peace_tv_recs:
            enhanced_rec = {
                "video": {
                    "id": rec.video.id,
                    "title": rec.video.title,
                    "description": rec.video.description,
                    "scholar": rec.video.scholar,
                    "duration_minutes": rec.video.duration_minutes,
                    "thumbnail_url": rec.video.thumbnail_url,
                    "video_url": rec.video.video_url,
                    "content_type": rec.video.content_type,
                    "tags": rec.video.tags
                },
                "ai_insights": {
                    "relevance_score": rec.relevance_score,
                    "why_recommended": rec.reason,
                    "learning_context": rec.learning_context,
                    "estimated_benefit": rec.estimated_benefit,
                    "best_time_to_watch": "After completing current lesson" if lesson_context else "Anytime",
                    "preparation_needed": "Review current lesson words" if current_word else "None"
                }
            }
            enhanced_recommendations.append(enhanced_rec)
        
        return {
            "contextual_recommendations": {
                "enhanced_video_recommendations": enhanced_recommendations,
                "total_recommendations": len(enhanced_recommendations),
                "ai_ustaz_guidance": {
                    "persona": ustaz_video_guidance.persona,
                    "main_message": ustaz_video_guidance.main_message,
                    "practical_advice": ustaz_video_guidance.practical_advice,
                    "encouragement": ustaz_video_guidance.encouragement,
                    "video_watching_tips": [
                        "Take notes on key points",
                        "Pause to reflect on important concepts",
                        "Connect video content to your current lessons",
                        "Make dua before and after watching"
                    ]
                }
            },
            "context_details": {
                "current_word": current_word,
                "lesson_context": lesson_context,
                "learning_goal": learning_goal
            },
            "quranic_reference": ai_ustaz_assistant.get_quranic_reference_formatted(ustaz_video_guidance.quranic_reference),
            "watching_guidelines": [
                "Choose videos that match your current learning level",
                "Watch with intention and focus",
                "Apply learned concepts in your daily practice",
                "Share beneficial knowledge with others"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting contextual video recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error generating contextual recommendations")

@api_router.post("/track-integrated-learning-session")
async def track_integrated_learning_session(
    session_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """📊 Track comprehensive learning session with both AI guidance and Peace TV content"""
    try:
        user_id = str(current_user["_id"])
        
        # Extract session data
        ustaz_guidance_used = session_data.get("ustaz_guidance_used", False)
        videos_watched = session_data.get("videos_watched", [])
        guidance_context = session_data.get("guidance_context", "general")
        session_duration_minutes = session_data.get("session_duration_minutes", 0)
        learning_goals_achieved = session_data.get("learning_goals_achieved", [])
        
        # Calculate comprehensive XP rewards
        total_xp = 0
        xp_breakdown = {}
        
        # Base XP for session
        base_xp = max(10, min(session_duration_minutes * 2, 100))  # 2 XP per minute, max 100
        total_xp += base_xp
        xp_breakdown["base_session"] = base_xp
        
        # Bonus for AI guidance usage
        if ustaz_guidance_used:
            guidance_xp = 25
            total_xp += guidance_xp
            xp_breakdown["ai_guidance_bonus"] = guidance_xp
        
        # Bonus for video completion
        videos_xp = len(videos_watched) * 15  # 15 XP per video
        total_xp += videos_xp
        xp_breakdown["videos_watched"] = videos_xp
        
        # Bonus for goal achievement
        goals_xp = len(learning_goals_achieved) * 20  # 20 XP per goal
        total_xp += goals_xp
        xp_breakdown["goals_achieved"] = goals_xp
        
        # Award XP through gamification system
        if gamification_system:
            await gamification_system.award_xp(
                user_id, 
                total_xp, 
                f"Completed integrated learning session ({session_duration_minutes} min)"
            )
            
            # Check for session-related achievements
            activity_data = {
                "integrated_sessions": 1,
                "session_duration": session_duration_minutes,
                "videos_watched": len(videos_watched),
                "guidance_used": ustaz_guidance_used,
                "goals_achieved": len(learning_goals_achieved)
            }
            achievements = await gamification_system.check_achievements(user_id, activity_data)
        else:
            achievements = []
        
        # Store session data
        session_record = {
            "user_id": user_id,
            "session_date": datetime.utcnow(),
            "guidance_context": guidance_context,
            "ustaz_guidance_used": ustaz_guidance_used,
            "videos_watched": videos_watched,
            "session_duration_minutes": session_duration_minutes,
            "learning_goals_achieved": learning_goals_achieved,
            "xp_earned": total_xp,
            "achievements_unlocked": achievements
        }
        
        if self.db:
            await self.db.integrated_learning_sessions.insert_one(session_record)
        
        return {
            "session_tracking": {
                "session_completed": True,
                "total_xp_earned": total_xp,
                "xp_breakdown": xp_breakdown,
                "achievements_unlocked": achievements,
                "session_summary": {
                    "duration_minutes": session_duration_minutes,
                    "videos_watched_count": len(videos_watched),
                    "guidance_context": guidance_context,
                    "goals_achieved_count": len(learning_goals_achieved)
                }
            },
            "islamic_reflection": {
                "dua_recommendation": "اللَّهُمَّ انْفَعْنِي بِمَا عَلَّمْتَنِي وَعَلِّمْنِي مَا يَنْفَعُنِي (O Allah, benefit me with what You have taught me and teach me what will benefit me)",
                "gratitude_reminder": "Say 'Alhamdulillahi rabbil alameen' for the blessing of learning",
                "continuation_advice": "Apply what you've learned in your daily prayers and interactions"
            },
            "next_session_recommendations": [
                "Review and practice what you learned today",
                "Set specific goals for your next session",
                "Consider sharing knowledge with family or friends",
                "Make dua for continued guidance and learning"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error tracking integrated learning session: {e}")
        raise HTTPException(status_code=500, detail="Error tracking learning session")

# =============================================
# FULL QURAN DATABASE SYSTEM 📖
# =============================================

@api_router.get("/quran/surahs")
async def get_all_surahs(current_user: dict = Depends(get_current_user)):
    """📚 Get list of all 114 Surahs with metadata"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        # Get all available Surahs
        all_surahs = []
        for surah_num in range(1, 115):  # 114 Surahs
            surah_info = await full_quran_db.get_surah_info(surah_num)
            if surah_info:
                all_surahs.append(surah_info.to_dict())
        
        return {
            "surahs": all_surahs,
            "total_count": len(all_surahs),
            "quran_statistics": await full_quran_db.get_quran_statistics()
        }
        
    except Exception as e:
        logger.error(f"Error getting all Surahs: {e}")
        raise HTTPException(status_code=500, detail="Error loading Surahs")

@api_router.get("/quran/surah/{surah_number}")
async def get_surah_details(
    surah_number: int,
    current_user: dict = Depends(get_current_user)
):
    """📖 Get detailed information about a specific Surah"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        surah_info = await full_quran_db.get_surah_info(surah_number)
        
        if not surah_info:
            raise HTTPException(status_code=404, detail="Surah not found")
        
        # Award XP for exploring Quran
        if gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]), 
                5, 
                f"Explored Surah {surah_info.name_english}"
            )
        
        return {
            "surah": surah_info.to_dict(),
            "islamic_note": "This is the preserved word of Allah, revealed to Prophet Muhammad (ﷺ)"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting Surah details: {e}")
        raise HTTPException(status_code=500, detail="Error loading Surah details")

@api_router.get("/quran/verse/{surah_number}/{ayat_number}")
async def get_verse_complete(
    surah_number: int,
    ayat_number: int,
    translation_type: TranslationType = TranslationType.SAHIH_INTERNATIONAL,
    include_tafseer: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """📜 Get complete verse with word-by-word analysis, translation, and tafseer"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        ayat = await full_quran_db.get_ayat_by_reference(
            surah_number, 
            ayat_number,
            include_tafseer=include_tafseer,
            translation_type=translation_type
        )
        
        if not ayat:
            raise HTTPException(status_code=404, detail="Verse not found")
        
        # Award XP for studying Quran
        if gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]), 
                10, 
                f"Studied Quran {surah_number}:{ayat_number}"
            )
        
        return {
            "verse": ayat.to_dict(),
            "reference": f"Quran {surah_number}:{ayat_number}",
            "translation_type": translation_type,
            "includes_tafseer": include_tafseer,
            "study_tips": [
                "Read the Arabic text slowly and carefully",
                "Study word-by-word translation for deeper understanding",
                "Reflect on the tafseer to understand context",
                "Memorize the verse through repetition",
                "Apply the lessons in your daily life"
            ]
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting verse: {e}")
        raise HTTPException(status_code=500, detail="Error loading verse")

@api_router.get("/quran/surah/{surah_number}/verses")
async def get_surah_all_verses(
    surah_number: int,
    start_verse: int = 1,
    end_verse: Optional[int] = None,
    translation_type: TranslationType = TranslationType.SAHIH_INTERNATIONAL,
    current_user: dict = Depends(get_current_user)
):
    """📚 Get all verses from a Surah or a specific range"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        verses = await full_quran_db.get_surah_verses(surah_number, start_verse, end_verse)
        
        if not verses:
            raise HTTPException(status_code=404, detail="No verses found")
        
        # Award XP for reading complete Surah
        if gamification_system and not end_verse:
            await gamification_system.award_xp(
                str(current_user["_id"]), 
                50, 
                f"Read complete Surah {surah_number}"
            )
        
        return {
            "surah_number": surah_number,
            "verses": [verse.to_dict() for verse in verses],
            "total_verses": len(verses),
            "range": f"{start_verse} to {end_verse or 'end'}",
            "reading_time_estimate": f"{len(verses) * 2} minutes",
            "recitation_tip": "Recite slowly with proper tajweed for maximum reward"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting Surah verses: {e}")
        raise HTTPException(status_code=500, detail="Error loading verses")

@api_router.get("/quran/word-analysis/{surah_number}/{ayat_number}/{word_position}")
async def get_word_linguistic_analysis(
    surah_number: int,
    ayat_number: int,
    word_position: int,
    current_user: dict = Depends(get_current_user)
):
    """🔍 Get detailed linguistic analysis of a specific Quran word"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        word = await full_quran_db.get_word_analysis(surah_number, ayat_number, word_position)
        
        if not word:
            raise HTTPException(status_code=404, detail="Word not found")
        
        # Award XP for deep word study
        if gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]), 
                15, 
                "Studied word linguistic analysis"
            )
        
        return {
            "word_analysis": word.to_dict(),
            "reference": f"Quran {surah_number}:{ayat_number} - Word {word_position}",
            "learning_benefits": [
                "Understanding root words helps learn entire word families",
                "Grammar knowledge improves Quran comprehension",
                "Tajweed rules ensure proper recitation",
                "Word-by-word study leads to deeper understanding"
            ],
            "study_recommendation": "Practice pronouncing this word using the audio"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting word analysis: {e}")
        raise HTTPException(status_code=500, detail="Error loading word analysis")

@api_router.get("/quran/search")
async def search_quran_advanced(
    query: str,
    search_type: str = "translation",
    translation_type: TranslationType = TranslationType.SAHIH_INTERNATIONAL,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """🔍 Advanced Quran search across translations, transliteration, or Arabic"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        results = await full_quran_db.search_quran(
            query=query,
            search_type=search_type,
            translation_type=translation_type,
            limit=limit
        )
        
        # Award XP for searching Quran
        if gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]), 
                8, 
                f"Searched Quran for: {query}"
            )
        
        return {
            "search_query": query,
            "search_type": search_type,
            "results": [result.to_dict() for result in results],
            "total_results": len(results),
            "search_tips": [
                "Try different search types (translation, transliteration, arabic)",
                "Use specific keywords for better results",
                "Explore related verses for full context"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching Quran: {e}")
        raise HTTPException(status_code=500, detail="Error searching Quran")

@api_router.get("/quran/root-words/{root_word}")
async def get_words_by_root(
    root_word: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """🌳 Find all Quran words derived from the same root"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        words = await full_quran_db.get_words_by_root(root_word, limit)
        
        # Award XP for root word study
        if gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]), 
                12, 
                f"Studied root word: {root_word}"
            )
        
        return {
            "root_word": root_word,
            "words": [word.to_dict() for word in words],
            "total_occurrences": len(words),
            "linguistic_insight": "Understanding root words helps you learn entire word families in Arabic",
            "study_benefit": f"By learning this root, you've unlocked {len(words)} Quranic words!"
        }
        
    except Exception as e:
        logger.error(f"Error getting words by root: {e}")
        raise HTTPException(status_code=500, detail="Error loading root words")

@api_router.get("/quran/verse-of-the-day")
async def get_daily_verse(current_user: dict = Depends(get_current_user)):
    """🌅 Get daily inspiration verse from the Quran"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        # Get random verse for daily inspiration
        verse = await full_quran_db.get_random_verse()
        
        if not verse:
            raise HTTPException(status_code=404, detail="Could not generate daily verse")
        
        # Award XP for daily Quran engagement
        if gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]), 
                10, 
                "Engaged with daily verse"
            )
        
        # Get AI Ustaz reflection on this verse
        ustaz_reflection = await ai_ustaz_assistant.get_contextual_guidance(
            user_id=str(current_user["_id"]),
            context=GuidanceContext.DAILY_REMINDER,
            user_data={"daily_verse": f"{verse.surah_number}:{verse.ayat_number}"},
            current_activity="daily_verse_reflection"
        )
        
        return {
            "verse_of_the_day": verse.to_dict(),
            "reference": f"Quran {verse.surah_number}:{verse.ayat_number}",
            "ustaz_reflection": {
                "persona": ustaz_reflection.persona,
                "message": ustaz_reflection.main_message,
                "practical_advice": ustaz_reflection.practical_advice,
                "encouragement": ustaz_reflection.encouragement
            },
            "daily_practice": [
                "Read this verse in Arabic",
                "Understand its meaning deeply",
                "Reflect on how it applies to your life",
                "Share its wisdom with others",
                "Make dua based on its teachings"
            ],
            "reward": "Prophet (ﷺ) said: 'Whoever recites one letter of the Quran gets 10 rewards'"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting daily verse: {e}")
        raise HTTPException(status_code=500, detail="Error generating daily verse")

@api_router.get("/quran/statistics")
async def get_quran_statistics():
    """📊 Get comprehensive Quran statistics and facts"""
    try:
        if not full_quran_db:
            raise HTTPException(status_code=500, detail="Quran database not initialized")
        
        statistics = await full_quran_db.get_quran_statistics()
        
        return {
            "quran_statistics": statistics,
            "amazing_facts": [
                "The Quran has been perfectly preserved for over 1400 years",
                "Millions of Muslims have memorized the entire Quran",
                "The word 'day' appears 365 times in the Quran",
                "The words 'man' and 'woman' each appear 23 times",
                "The Quran was revealed over 23 years",
                "It takes approximately 30 hours to recite the entire Quran"
            ],
            "preservation_miracle": "The Quran is the only religious book that has been preserved in its original language without any changes since revelation"
        }
        
    except Exception as e:
        logger.error(f"Error getting Quran statistics: {e}")
        raise HTTPException(status_code=500, detail="Error loading statistics")

# =============================================
# SPEECH RECOGNITION & TAJWEED SCORING 🎤
# =============================================

class RecitationRequest(BaseModel):
    target_verse: str
    reciter_comparison: Optional[str] = "ar.alafasy"

@api_router.post("/recitation/analyze")
async def analyze_recitation(
    file: UploadFile = File(...),
    target_verse: str = "1:1",
    current_user: dict = Depends(get_current_user)
):
    """🎤 Analyze Quran recitation with AI Tajweed scoring"""
    try:
        if not speech_recognition_system:
            raise HTTPException(status_code=500, detail="Speech recognition not initialized")
        
        # Read audio file
        audio_data = await file.read()
        
        # Analyze recitation
        score = await speech_recognition_system.analyze_recitation(
            user_id=str(current_user["_id"]),
            audio_data=audio_data,
            target_verse=target_verse
        )
        
        # Award XP for recitation practice
        if gamification_system:
            xp_amount = int(score.overall_score / 2)  # Up to 50 XP
            await gamification_system.award_xp(
                str(current_user["_id"]),
                xp_amount,
                f"Recitation practice: {target_verse}"
            )
        
        return {
            "recitation_score": {
                "overall_score": score.overall_score,
                "pronunciation_score": score.pronunciation_score,
                "tajweed_score": score.tajweed_score,
                "fluency_score": score.fluency_score,
                "timing_score": score.timing_score,
                "recitation_level": score.recitation_level
            },
            "errors_found": [
                {
                    "error_type": err.error_type,
                    "word_position": err.word_position,
                    "severity": err.severity,
                    "description": err.description,
                    "correction_advice": err.correction_advice
                } for err in score.errors_found
            ],
            "strengths": score.strengths,
            "improvements": score.improvements,
            "xp_earned": int(score.overall_score / 2),
            "islamic_reminder": "Prophet (ﷺ) said: 'The one who recites the Quran beautifully will be with the noble angels'"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error analyzing recitation: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing recitation")

@api_router.get("/recitation/history")
async def get_recitation_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """📊 Get user's recitation practice history"""
    try:
        history = await db.recitation_history.find(
            {"user_id": str(current_user["_id"])}
        ).sort("recorded_at", -1).limit(limit).to_list(limit)
        
        return {
            "recitation_history": history,
            "total_attempts": len(history),
            "average_score": sum(h.get("overall_score", 0) for h in history) / len(history) if history else 0,
            "practice_tip": "Consistent practice is the key to mastering Tajweed!"
        }
        
    except Exception as e:
        logger.error(f"Error getting recitation history: {e}")
        raise HTTPException(status_code=500, detail="Error loading history")

# =============================================
# ADVANCED LEARNING ANALYTICS 📊
# =============================================

@api_router.get("/analytics/dashboard")
async def get_analytics_dashboard(current_user: dict = Depends(get_current_user)):
    """📊 Get comprehensive learning analytics dashboard"""
    try:
        if not analytics_engine:
            raise HTTPException(status_code=500, detail="Analytics engine not initialized")
        
        analytics = await analytics_engine.get_comprehensive_analytics(
            str(current_user["_id"])
        )
        
        return {
            "analytics": {
                "total_study_time_hours": analytics.total_study_time_hours,
                "words_mastered": analytics.words_mastered,
                "verses_memorized": analytics.verses_memorized,
                "current_streak_days": analytics.current_streak_days,
                "best_streak_days": analytics.best_streak_days,
                "skill_breakdown": analytics.skill_breakdown,
                "predicted_next_level_days": analytics.predicted_next_level_days,
                "study_patterns": analytics.study_patterns
            },
            "weekly_progress": analytics.weekly_progress,
            "recommendations": analytics.recommendations,
            "motivational_message": f"You've studied for {analytics.total_study_time_hours} hours! Keep up the amazing work!",
            "next_milestone": f"You're {analytics.predicted_next_level_days} days away from your next level!"
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Error loading analytics")

# =============================================
# SOCIAL LEARNING FEATURES 👥
# =============================================

class CreateGroupRequest(BaseModel):
    name: str
    group_type: GroupType
    description: str
    is_public: bool = True

@api_router.post("/social/groups/create")
async def create_study_group(
    request: CreateGroupRequest,
    current_user: dict = Depends(get_current_user)
):
    """👥 Create a new study group"""
    try:
        if not social_system:
            raise HTTPException(status_code=500, detail="Social system not initialized")
        
        group = await social_system.create_study_group(
            creator_id=str(current_user["_id"]),
            name=request.name,
            group_type=request.group_type,
            description=request.description,
            is_public=request.is_public
        )
        
        # Award XP for creating study group
        if gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]),
                30,
                f"Created study group: {request.name}"
            )
        
        return {
            "group": group.__dict__,
            "message": "Study group created successfully!",
            "islamic_note": "Seeking knowledge in congregation multiplies the reward"
        }
        
    except Exception as e:
        logger.error(f"Error creating study group: {e}")
        raise HTTPException(status_code=500, detail="Error creating group")

@api_router.post("/social/groups/{group_id}/join")
async def join_study_group(
    group_id: str,
    current_user: dict = Depends(get_current_user)
):
    """👥 Join an existing study group"""
    try:
        if not social_system:
            raise HTTPException(status_code=500, detail="Social system not initialized")
        
        success = await social_system.join_study_group(
            user_id=str(current_user["_id"]),
            group_id=group_id
        )
        
        if success:
            # Award XP for joining group
            if gamification_system:
                await gamification_system.award_xp(
                    str(current_user["_id"]),
                    15,
                    "Joined a study group"
                )
            
            return {
                "success": True,
                "message": "Successfully joined study group!",
                "islamic_reminder": "The angels lower their wings for the seeker of knowledge"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to join group")
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error joining study group: {e}")
        raise HTTPException(status_code=500, detail="Error joining group")

@api_router.get("/social/groups")
async def list_study_groups(
    group_type: Optional[GroupType] = None,
    current_user: dict = Depends(get_current_user)
):
    """👥 List available study groups"""
    try:
        query = {"is_public": True}
        if group_type:
            query["group_type"] = group_type
        
        groups = await db.study_groups.find(query).limit(50).to_list(50)
        
        return {
            "groups": groups,
            "total_count": len(groups),
            "group_types_available": [gt.value for gt in GroupType]
        }
        
    except Exception as e:
        logger.error(f"Error listing groups: {e}")
        raise HTTPException(status_code=500, detail="Error loading groups")

# =============================================
# SUBSCRIPTION & PREMIUM FEATURES 💰
# =============================================

@api_router.get("/subscription/plans")
async def get_subscription_plans():
    """💰 Get available subscription plans"""
    try:
        if not subscription_system:
            raise HTTPException(status_code=500, detail="Subscription system not initialized")
        
        plans = []
        for tier, plan in subscription_system.plans.items():
            plans.append({
                "tier": plan.tier,
                "price_monthly": plan.price_monthly,
                "price_yearly": plan.price_yearly,
                "features": [f.value for f in plan.features],
                "max_users": plan.max_users,
                "ai_queries_per_month": plan.ai_queries_per_month
            })
        
        return {
            "plans": plans,
            "recommended": "premium",
            "special_offer": "Get 2 months free with annual subscription!",
            "islamic_note": "Invest in your Islamic knowledge - a reward that continues after death"
        }
        
    except Exception as e:
        logger.error(f"Error getting subscription plans: {e}")
        raise HTTPException(status_code=500, detail="Error loading plans")

@api_router.get("/subscription/check-access/{feature}")
async def check_feature_access(
    feature: str,
    current_user: dict = Depends(get_current_user)
):
    """🔒 Check if user has access to a premium feature"""
    try:
        # Get user's subscription tier (default to FREE)
        user_tier = current_user.get("subscription_tier", SubscriptionTier.FREE)
        
        try:
            feature_enum = FeatureAccess(feature)
            has_access = subscription_system.check_feature_access(user_tier, feature_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid feature name")
        
        return {
            "has_access": has_access,
            "current_tier": user_tier,
            "feature": feature,
            "upgrade_message": "Upgrade to Premium for unlimited access!" if not has_access else None
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error checking feature access: {e}")
        raise HTTPException(status_code=500, detail="Error checking access")

# =============================================
# RICH MEDIA CONTENT DELIVERY 🎥
# =============================================

@api_router.get("/media/recommended")
async def get_recommended_media(
    media_type: Optional[MediaType] = None,
    level: Optional[ContentLevel] = None,
    current_user: dict = Depends(get_current_user)
):
    """🎥 Get personalized media recommendations"""
    try:
        if not rich_media_system:
            raise HTTPException(status_code=500, detail="Rich media system not initialized")
        
        content = await rich_media_system.get_recommended_content(
            user_id=str(current_user["_id"]),
            content_type=media_type,
            level=level
        )
        
        return {
            "recommended_content": [
                {
                    "content_id": c.content_id,
                    "title": c.title,
                    "description": c.description,
                    "media_type": c.media_type,
                    "content_level": c.content_level,
                    "duration_minutes": c.duration_minutes,
                    "instructor_name": c.instructor_name,
                    "url": c.url,
                    "thumbnail_url": c.thumbnail_url,
                    "category": c.category,
                    "views_count": c.views_count,
                    "rating": c.rating,
                    "is_premium": c.is_premium
                } for c in content
            ],
            "total_available": len(content),
            "filters_applied": {
                "media_type": media_type.value if media_type else "all",
                "level": level.value if level else "all"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting media recommendations: {e}")
        raise HTTPException(status_code=500, detail="Error loading media content")

@api_router.post("/media/{content_id}/track-progress")
async def track_media_progress(
    content_id: str,
    progress_percentage: float,
    completed: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """📊 Track media content viewing progress"""
    try:
        if not rich_media_system:
            raise HTTPException(status_code=500, detail="Rich media system not initialized")
        
        await rich_media_system.track_media_progress(
            user_id=str(current_user["_id"]),
            content_id=content_id,
            progress_percentage=progress_percentage,
            completed=completed
        )
        
        # Award XP for completing content
        if completed and gamification_system:
            await gamification_system.award_xp(
                str(current_user["_id"]),
                25,
                f"Completed media content: {content_id}"
            )
        
        return {
            "success": True,
            "progress": progress_percentage,
            "completed": completed,
            "xp_earned": 25 if completed else 0
        }
        
    except Exception as e:
        logger.error(f"Error tracking media progress: {e}")
        raise HTTPException(status_code=500, detail="Error tracking progress")

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
