"""
🎥 Revolutionary Rich Media Content System
==========================================

Video lessons, podcasts, audio tafseer, and interactive
multimedia content for comprehensive Islamic learning.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class MediaType(str, Enum):
    VIDEO = "video"
    PODCAST = "podcast"
    AUDIO_TAFSEER = "audio_tafseer"
    INTERACTIVE = "interactive"
    LIVE_CLASS = "live_class"

class ContentLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SCHOLAR = "scholar"

@dataclass
class MediaContent:
    content_id: str
    title: str
    description: str
    media_type: MediaType
    content_level: ContentLevel
    duration_minutes: int
    instructor_name: str
    url: str
    thumbnail_url: str
    category: str
    views_count: int
    rating: float
    is_premium: bool

class RichMediaSystem:
    """Revolutionary Media Content Delivery"""
    
    def __init__(self, db):
        self.db = db
        self._initialize_sample_content()
    
    def _initialize_sample_content(self):
        """Initialize with curated Islamic content"""
        self.sample_content = [
            MediaContent(
                content_id="vid_001",
                title="Introduction to Tajweed - Makharij al-Huruf",
                description="Learn the 17 points of articulation in Quranic recitation",
                media_type=MediaType.VIDEO,
                content_level=ContentLevel.BEGINNER,
                duration_minutes=25,
                instructor_name="Sheikh Ahmad Al-Azhari",
                url="https://peace-tv/tajweed/makharij",
                thumbnail_url="https://peace-tv/thumbs/tajweed-01.jpg",
                category="Tajweed",
                views_count=15420,
                rating=4.9,
                is_premium=False
            ),
            MediaContent(
                content_id="pod_001",
                title="Stories from the Quran - Prophet Yusuf (AS)",
                description="Deep dive into the beautiful story of patience and trust",
                media_type=MediaType.PODCAST,
                content_level=ContentLevel.INTERMEDIATE,
                duration_minutes=45,
                instructor_name="Ustadh Nouman Ali Khan",
                url="https://peace-tv/podcasts/yusuf",
                thumbnail_url="https://peace-tv/thumbs/yusuf-story.jpg",
                category="Quranic Stories",
                views_count=28500,
                rating=5.0,
                is_premium=True
            ),
            MediaContent(
                content_id="tafseer_001",
                title="Tafseer Surah Al-Baqarah - Complete Series",
                description="Comprehensive tafseer by Sheikh Ibn Kathir",
                media_type=MediaType.AUDIO_TAFSEER,
                content_level=ContentLevel.ADVANCED,
                duration_minutes=180,
                instructor_name="Sheikh Ibn Kathir",
                url="https://peace-tv/tafseer/baqarah",
                thumbnail_url="https://peace-tv/thumbs/baqarah-tafseer.jpg",
                category="Tafseer",
                views_count=45200,
                rating=4.95,
                is_premium=True
            )
        ]
    
    async def get_recommended_content(
        self,
        user_id: str,
        content_type: Optional[MediaType] = None,
        level: Optional[ContentLevel] = None
    ) -> List[MediaContent]:
        """Get personalized media recommendations"""
        
        filtered = self.sample_content
        
        if content_type:
            filtered = [c for c in filtered if c.media_type == content_type]
        
        if level:
            filtered = [c for c in filtered if c.content_level == level]
        
        return filtered
    
    async def track_media_progress(
        self,
        user_id: str,
        content_id: str,
        progress_percentage: float,
        completed: bool = False
    ):
        """Track user's media consumption progress"""
        if self.db:
            await self.db.media_progress.update_one(
                {"user_id": user_id, "content_id": content_id},
                {
                    "$set": {
                        "progress_percentage": progress_percentage,
                        "completed": completed,
                        "last_watched": datetime.utcnow()
                    }
                },
                upsert=True
            )

rich_media_system = RichMediaSystem(None)

async def initialize_rich_media_system(db):
    global rich_media_system
    rich_media_system = RichMediaSystem(db)
    logger.info("🎥 Rich Media System initialized!")
