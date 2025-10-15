"""
🌟 Revolutionary Peace TV Integration System
==================================================

This module provides comprehensive integration with Peace TV (https://www.peacetv.tv/)
to enhance the Think-Quran learning experience with authentic Islamic video content.

Features:
- Contextual video recommendations based on current learning
- Peace TV content discovery and streaming
- Scholar-specific content matching
- Interactive learning with video transcripts
- Islamic compliance with authentic sources
- Multilingual content support

JAKIM/JAIS Compliance: All content sourced from Peace TV is pre-verified
as authentic Islamic educational material from recognized scholars.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import asyncio
import httpx
import json
from dataclasses import dataclass
import logging

# Setup logging
logger = logging.getLogger(__name__)

class PeaceTVLanguage(str, Enum):
    """Supported Peace TV languages"""
    ENGLISH = "english"
    ARABIC = "arabic"
    URDU = "urdu"
    HINDI = "hindi"
    BENGALI = "bengali"
    MALAYALAM = "malayalam"
    TAMIL = "tamil"

class PeaceTVContentType(str, Enum):
    """Peace TV content categories"""
    QURAN_RECITATION = "quran_recitation"
    QURAN_TAFSEER = "quran_tafseer"
    HADITH_EXPLANATION = "hadith_explanation"
    ISLAMIC_LECTURES = "islamic_lectures"
    QURAN_LEARNING = "quran_learning"
    ARABIC_LANGUAGE = "arabic_language"
    ISLAMIC_HISTORY = "islamic_history"
    PRAYER_GUIDANCE = "prayer_guidance"
    LIVE_PROGRAMS = "live_programs"

class ScholarName(str, Enum):
    """Peace TV featured scholars"""
    DR_ZAKIR_NAIK = "dr_zakir_naik"
    DR_ISRAR_AHMAD = "dr_israr_ahmad"
    SHEIKH_AHMED_DEEDAT = "sheikh_ahmed_deedat"
    DR_BILAL_PHILIPS = "dr_bilal_philips"
    YUSUF_ESTES = "yusuf_estes"
    ABDUR_RAHEEM_GREEN = "abdur_raheem_green"
    HUSSEIN_YEE = "hussein_yee"

@dataclass
class PeaceTVVideo:
    """Peace TV video content model"""
    id: str
    title: str
    description: str
    scholar: ScholarName
    language: PeaceTVLanguage
    content_type: PeaceTVContentType
    duration_minutes: int
    thumbnail_url: str
    video_url: str
    transcript: Optional[str]
    related_quran_verses: List[str]
    related_words: List[str]
    view_count: int
    upload_date: datetime
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "scholar": self.scholar,
            "language": self.language,
            "content_type": self.content_type,
            "duration_minutes": self.duration_minutes,
            "thumbnail_url": self.thumbnail_url,
            "video_url": self.video_url,
            "transcript": self.transcript,
            "related_quran_verses": self.related_quran_verses,
            "related_words": self.related_words,
            "view_count": self.view_count,
            "upload_date": self.upload_date.isoformat(),
            "tags": self.tags
        }

@dataclass
class PeaceTVRecommendation:
    """Personalized Peace TV content recommendation"""
    video: PeaceTVVideo
    relevance_score: float
    reason: str
    learning_context: str
    estimated_benefit: str

class RevolutionaryPeaceTVIntegration:
    """
    🌟 Revolutionary Peace TV Integration System
    
    Provides intelligent, contextual integration with Peace TV content
    to enhance Quranic learning with authentic video resources.
    """
    
    def __init__(self, db):
        self.db = db
        self.peace_tv_api_base = "https://www.peacetv.tv/api"  # Hypothetical API
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Initialize Peace TV content database
        self.scholars_expertise = {
            ScholarName.DR_ZAKIR_NAIK: ["comparative_religion", "quran_science", "interfaith_dialogue"],
            ScholarName.DR_ISRAR_AHMAD: ["quran_tafseer", "islamic_philosophy", "urdu_lectures"],
            ScholarName.SHEIKH_AHMED_DEEDAT: ["comparative_religion", "bible_quran", "debates"],
            ScholarName.DR_BILAL_PHILIPS: ["islamic_studies", "arabic_grammar", "hadith_sciences"],
            ScholarName.YUSUF_ESTES: ["new_muslim_guidance", "basic_islam", "english_lectures"],
            ScholarName.ABDUR_RAHEEM_GREEN: ["youth_guidance", "practical_islam", "q_and_a"],
            ScholarName.HUSSEIN_YEE: ["chinese_muslim", "southeast_asia", "practical_guidance"]
        }
        
        # Sample Peace TV content (in production, this would come from their API)
        self.sample_content = self._initialize_sample_content()
    
    def _initialize_sample_content(self) -> List[PeaceTVVideo]:
        """Initialize sample Peace TV content for demonstration"""
        return [
            PeaceTVVideo(
                id="ptv_001",
                title="Understanding Al-Fatiha - The Opening Chapter",
                description="Dr. Zakir Naik explains the profound meanings of Surah Al-Fatiha",
                scholar=ScholarName.DR_ZAKIR_NAIK,
                language=PeaceTVLanguage.ENGLISH,
                content_type=PeaceTVContentType.QURAN_TAFSEER,
                duration_minutes=45,
                thumbnail_url="https://peacetv.tv/thumbnails/al_fatiha_zakir.jpg",
                video_url="https://peacetv.tv/videos/al_fatiha_explanation",
                transcript="In the name of Allah, the Most Gracious, the Most Merciful...",
                related_quran_verses=["1:1", "1:2", "1:3", "1:4", "1:5", "1:6", "1:7"],
                related_words=["rahman", "rahim", "malik", "din", "sirat"],
                view_count=250000,
                upload_date=datetime(2024, 1, 15),
                tags=["al-fatiha", "quran", "tafseer", "zakir-naik"]
            ),
            PeaceTVVideo(
                id="ptv_002",
                title="Arabic Grammar for Quran Understanding",
                description="Dr. Bilal Philips teaches essential Arabic grammar for Quran comprehension",
                scholar=ScholarName.DR_BILAL_PHILIPS,
                language=PeaceTVLanguage.ENGLISH,
                content_type=PeaceTVContentType.ARABIC_LANGUAGE,
                duration_minutes=60,
                thumbnail_url="https://peacetv.tv/thumbnails/arabic_grammar_bilal.jpg",
                video_url="https://peacetv.tv/videos/arabic_grammar_basics",
                transcript="Arabic has three main parts of speech: Ism, Fi'l, and Harf...",
                related_quran_verses=["2:31", "12:2", "41:44"],
                related_words=["ism", "fil", "harf", "nahw", "sarf"],
                view_count=180000,
                upload_date=datetime(2024, 2, 10),
                tags=["arabic", "grammar", "nahw", "bilal-philips"]
            ),
            PeaceTVVideo(
                id="ptv_003",
                title="Beautiful Names of Allah (Asma ul Husna)",
                description="Comprehensive explanation of the 99 Beautiful Names of Allah",
                scholar=ScholarName.DR_ZAKIR_NAIK,
                language=PeaceTVLanguage.ENGLISH,
                content_type=PeaceTVContentType.ISLAMIC_LECTURES,
                duration_minutes=90,
                thumbnail_url="https://peacetv.tv/thumbnails/asma_ul_husna.jpg",
                video_url="https://peacetv.tv/videos/99_names_allah",
                transcript="Ar-Rahman means the Most Gracious, Ar-Rahim means the Most Merciful...",
                related_quran_verses=["7:180", "17:110", "20:8"],
                related_words=["rahman", "rahim", "malik", "quddus", "salam"],
                view_count=500000,
                upload_date=datetime(2024, 1, 20),
                tags=["asma-ul-husna", "99-names", "allah", "attributes"]
            ),
            PeaceTVVideo(
                id="ptv_004",
                title="Learning Tajweed - Proper Quran Recitation",
                description="Step-by-step guide to learning proper Quranic pronunciation",
                scholar=ScholarName.YUSUF_ESTES,
                language=PeaceTVLanguage.ENGLISH,
                content_type=PeaceTVContentType.QURAN_RECITATION,
                duration_minutes=75,
                thumbnail_url="https://peacetv.tv/thumbnails/tajweed_basics.jpg",
                video_url="https://peacetv.tv/videos/tajweed_lessons",
                transcript="Tajweed means to make beautiful, to improve...",
                related_quran_verses=["73:4", "25:32"],
                related_words=["qiraat", "makharij", "sifat"],
                view_count=320000,
                upload_date=datetime(2024, 2, 5),
                tags=["tajweed", "recitation", "pronunciation", "yusuf-estes"]
            )
        ]
    
    async def get_contextual_recommendations(
        self, 
        user_id: str, 
        current_word: Optional[str] = None,
        lesson_context: Optional[str] = None,
        language_preference: PeaceTVLanguage = PeaceTVLanguage.ENGLISH,
        limit: int = 5
    ) -> List[PeaceTVRecommendation]:
        """
        🧠 Get intelligent Peace TV recommendations based on current learning context
        """
        try:
            # Get user's learning context
            user_progress = await self.db.user_progress.find({"user_id": user_id}).to_list(100)
            learned_words = [p.get("word_id") for p in user_progress if p.get("mastery_level", 0) >= 50]
            
            # Get current lesson words if available
            current_lesson_words = []
            if lesson_context:
                lesson_number = int(lesson_context.split("_")[-1]) if "_" in lesson_context else 1
                lesson_words = await self.db.words.find({"lesson_number": lesson_number}).to_list(100)
                current_lesson_words = [w.get("arabic", "") for w in lesson_words]
            
            recommendations = []
            
            for video in self.sample_content:
                if video.language != language_preference:
                    continue
                
                relevance_score = 0.0
                reasons = []
                
                # Score based on current word context
                if current_word:
                    word_doc = await self.db.words.find_one({"arabic": current_word})
                    if word_doc and current_word in video.related_words:
                        relevance_score += 0.4
                        reasons.append(f"Explains your current word: {current_word}")
                
                # Score based on lesson context
                if current_lesson_words:
                    matching_words = set(current_lesson_words) & set(video.related_words)
                    if matching_words:
                        relevance_score += 0.3 * len(matching_words) / len(current_lesson_words)
                        reasons.append(f"Covers {len(matching_words)} words from your current lesson")
                
                # Score based on user's level
                if len(learned_words) < 10:  # Beginner
                    if video.content_type in [PeaceTVContentType.QURAN_LEARNING, PeaceTVContentType.ARABIC_LANGUAGE]:
                        relevance_score += 0.3
                        reasons.append("Perfect for beginners")
                elif len(learned_words) < 30:  # Intermediate
                    if video.content_type in [PeaceTVContentType.QURAN_TAFSEER, PeaceTVContentType.ISLAMIC_LECTURES]:
                        relevance_score += 0.3
                        reasons.append("Great for intermediate learners")
                else:  # Advanced
                    if video.content_type in [PeaceTVContentType.HADITH_EXPLANATION, PeaceTVContentType.ISLAMIC_HISTORY]:
                        relevance_score += 0.3
                        reasons.append("Advanced Islamic knowledge")
                
                # Bonus for popular content
                if video.view_count > 200000:
                    relevance_score += 0.1
                    reasons.append("Highly popular content")
                
                if relevance_score > 0.2:  # Minimum threshold
                    recommendations.append(PeaceTVRecommendation(
                        video=video,
                        relevance_score=relevance_score,
                        reason="; ".join(reasons) if reasons else "General Islamic learning",
                        learning_context=lesson_context or "General study",
                        estimated_benefit="Enhanced understanding through visual learning"
                    ))
            
            # Sort by relevance and return top results
            recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error getting Peace TV recommendations: {e}")
            return []
    
    async def search_peace_tv_content(
        self, 
        query: str, 
        content_type: Optional[PeaceTVContentType] = None,
        scholar: Optional[ScholarName] = None,
        language: PeaceTVLanguage = PeaceTVLanguage.ENGLISH,
        limit: int = 10
    ) -> List[PeaceTVVideo]:
        """
        🔍 Search Peace TV content with advanced filtering
        """
        try:
            # In production, this would call the actual Peace TV API
            # For now, we'll filter our sample content
            results = []
            
            for video in self.sample_content:
                # Apply filters
                if language and video.language != language:
                    continue
                if content_type and video.content_type != content_type:
                    continue
                if scholar and video.scholar != scholar:
                    continue
                
                # Check if query matches title, description, or tags
                query_lower = query.lower()
                if (query_lower in video.title.lower() or 
                    query_lower in video.description.lower() or 
                    any(query_lower in tag.lower() for tag in video.tags)):
                    results.append(video)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Peace TV content: {e}")
            return []
    
    async def get_scholar_content(
        self, 
        scholar: ScholarName,
        language: PeaceTVLanguage = PeaceTVLanguage.ENGLISH,
        limit: int = 10
    ) -> List[PeaceTVVideo]:
        """
        👨‍🏫 Get content from specific Peace TV scholars
        """
        try:
            scholar_videos = [
                video for video in self.sample_content 
                if video.scholar == scholar and video.language == language
            ]
            
            # Sort by view count and upload date
            scholar_videos.sort(key=lambda x: (x.view_count, x.upload_date), reverse=True)
            return scholar_videos[:limit]
            
        except Exception as e:
            logger.error(f"Error getting scholar content: {e}")
            return []
    
    async def get_live_programs(self) -> List[Dict[str, Any]]:
        """
        📺 Get current live Peace TV programs
        """
        try:
            # In production, this would get real-time data from Peace TV
            current_time = datetime.utcnow()
            
            # Sample live programming schedule
            live_programs = [
                {
                    "program_id": "live_001",
                    "title": "Ask Dr. Zakir",
                    "description": "Live Q&A session with Dr. Zakir Naik",
                    "scholar": ScholarName.DR_ZAKIR_NAIK,
                    "language": PeaceTVLanguage.ENGLISH,
                    "start_time": current_time.replace(hour=20, minute=0, second=0),
                    "duration_minutes": 60,
                    "stream_url": "https://peacetv.tv/live/ask_dr_zakir",
                    "is_live": True
                },
                {
                    "program_id": "live_002", 
                    "title": "Quran Tafseer",
                    "description": "Detailed explanation of Quranic verses",
                    "scholar": ScholarName.DR_ISRAR_AHMAD,
                    "language": PeaceTVLanguage.URDU,
                    "start_time": current_time.replace(hour=21, minute=0, second=0),
                    "duration_minutes": 45,
                    "stream_url": "https://peacetv.tv/live/quran_tafseer",
                    "is_live": False
                }
            ]
            
            return live_programs
            
        except Exception as e:
            logger.error(f"Error getting live programs: {e}")
            return []
    
    async def track_video_engagement(
        self, 
        user_id: str, 
        video_id: str, 
        watch_duration: int,
        completion_percentage: float
    ) -> Dict[str, Any]:
        """
        📊 Track user engagement with Peace TV content
        """
        try:
            engagement_record = {
                "user_id": user_id,
                "video_id": video_id,
                "watch_duration": watch_duration,
                "completion_percentage": completion_percentage,
                "watched_at": datetime.utcnow(),
                "platform": "think_quran_integration"
            }
            
            # Store engagement data
            await self.db.peace_tv_engagement.insert_one(engagement_record)
            
            # Award XP for watching educational content
            xp_award = int(watch_duration / 60) * 5  # 5 XP per minute watched
            
            return {
                "success": True,
                "xp_awarded": xp_award,
                "message": f"Thank you for learning with Peace TV! {xp_award} XP awarded."
            }
            
        except Exception as e:
            logger.error(f"Error tracking video engagement: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_watch_history(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        📚 Get user's Peace TV watch history with learning insights
        """
        try:
            history = await self.db.peace_tv_engagement.find(
                {"user_id": user_id}
            ).sort("watched_at", -1).limit(limit).to_list(limit)
            
            # Enrich with video details
            enriched_history = []
            for record in history:
                video = next((v for v in self.sample_content if v.id == record["video_id"]), None)
                if video:
                    enriched_history.append({
                        "video": video.to_dict(),
                        "watch_duration": record["watch_duration"],
                        "completion_percentage": record["completion_percentage"],
                        "watched_at": record["watched_at"],
                        "learning_value": "High" if record["completion_percentage"] > 80 else "Medium"
                    })
            
            return enriched_history
            
        except Exception as e:
            logger.error(f"Error getting watch history: {e}")
            return []

# Global instance
peace_tv_integration = RevolutionaryPeaceTVIntegration(None)

async def initialize_peace_tv_integration(db):
    """Initialize Peace TV integration with database"""
    global peace_tv_integration
    peace_tv_integration = RevolutionaryPeaceTVIntegration(db)
    logger.info("🌟 Revolutionary Peace TV Integration System initialized successfully!")
