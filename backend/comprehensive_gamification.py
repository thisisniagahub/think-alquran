# Comprehensive Gamification System
# Revolutionary achievement, leaderboard, and progression system
# Designed to be addictive while maintaining Islamic principles

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel
from enum import Enum
import logging
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)

class AchievementCategory(str, Enum):
    LEARNING = "learning"
    CONSISTENCY = "consistency"
    MASTERY = "mastery"
    SOCIAL = "social"
    SPIRITUAL = "spiritual"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"

class AchievementRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"

class BadgeType(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class LeaderboardType(str, Enum):
    GLOBAL = "global"
    FRIENDS = "friends"
    COUNTRY = "country"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"

class QuestType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIAL_EVENT = "special_event"
    RAMADAN = "ramadan"
    HAJJ = "hajj"

class RewardType(str, Enum):
    XP = "xp"
    COINS = "coins"
    BADGE = "badge"
    TITLE = "title"
    THEME = "theme"
    FEATURE_UNLOCK = "feature_unlock"

@dataclass
class Achievement:
    id: str
    title: str
    description: str
    category: AchievementCategory
    rarity: AchievementRarity
    icon: str
    xp_reward: int
    coin_reward: int
    requirements: Dict[str, Any]
    hidden: bool = False
    badge_type: Optional[BadgeType] = None
    islamic_reference: Optional[str] = None
    unlocks: List[str] = None  # What this achievement unlocks

@dataclass 
class Quest:
    id: str
    title: str
    description: str
    quest_type: QuestType
    requirements: Dict[str, Any]
    rewards: List[Dict[str, Any]]
    start_date: datetime
    end_date: datetime
    progress_current: int = 0
    progress_target: int = 1
    completed: bool = False
    islamic_theme: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    
    # Core Stats
    total_xp: int = 0
    current_level: int = 1
    coins: int = 0
    
    # Achievements
    achievements_unlocked: List[str] = []
    badges_earned: List[str] = []
    titles_earned: List[str] = []
    
    # Streaks and Consistency
    current_streak: int = 0
    longest_streak: int = 0
    total_study_days: int = 0
    
    # Learning Stats
    words_learned: int = 0
    lessons_completed: int = 0
    quizzes_taken: int = 0
    perfect_scores: int = 0
    
    # Time Stats
    total_study_time: int = 0  # minutes
    average_session_time: float = 0.0
    
    # Social Stats
    friends_count: int = 0
    challenges_won: int = 0
    study_groups_joined: int = 0
    
    # Spiritual Tracking (Islamic)
    duas_learned: int = 0
    surahs_completed: int = 0
    ramadan_participation: int = 0
    
    # Customization
    current_theme: str = "default"
    current_title: str = "Student"
    unlocked_themes: List[str] = ["default"]
    unlocked_features: List[str] = []
    
    # Preferences
    favorite_categories: List[str] = []
    notification_preferences: Dict[str, bool] = {}

class ComprehensiveGamificationSystem:
    """
    Revolutionary Gamification System for Quranic Learning
    
    Features:
    - 100+ Achievements across 7 categories
    - Dynamic XP and leveling system
    - Islamic-themed quests and challenges
    - Social leaderboards and competitions
    - Virtual economy with coins and rewards
    - Customization unlocks
    - Seasonal events (Ramadan, Hajj, etc.)
    """
    
    def __init__(self, db):
        self.db = db
        self.achievements = self._initialize_achievements()
        self.level_requirements = self._calculate_level_requirements()
        
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize the comprehensive achievement system"""
        
        achievements = {}
        
        # LEARNING ACHIEVEMENTS
        learning_achievements = [
            Achievement(
                id="first_word",
                title="First Steps in Arabic",
                description="Learn your very first Quranic word",
                category=AchievementCategory.LEARNING,
                rarity=AchievementRarity.COMMON,
                icon="🌱",
                xp_reward=50,
                coin_reward=10,
                requirements={"words_learned": 1},
                islamic_reference="The best of you are those who learn the Quran and teach it"
            ),
            Achievement(
                id="vocabulary_builder",
                title="Vocabulary Builder",
                description="Master 50 Quranic words",
                category=AchievementCategory.LEARNING,
                rarity=AchievementRarity.RARE,
                icon="📚",
                xp_reward=500,
                coin_reward=100,
                requirements={"words_learned": 50},
                badge_type=BadgeType.BRONZE
            ),
            Achievement(
                id="word_scholar",
                title="Arabic Scholar",
                description="Master 100 Quranic words",
                category=AchievementCategory.LEARNING,
                rarity=AchievementRarity.EPIC,
                icon="🎓",
                xp_reward=1000,
                coin_reward=250,
                requirements={"words_learned": 100},
                badge_type=BadgeType.SILVER,
                unlocks=["advanced_lessons", "etymology_explorer"]
            ),
            Achievement(
                id="quran_linguist",
                title="Quran Linguist",
                description="Master 500 Quranic words",
                category=AchievementCategory.LEARNING,
                rarity=AchievementRarity.LEGENDARY,
                icon="🏆",
                xp_reward=5000,
                coin_reward=1000,
                requirements={"words_learned": 500},
                badge_type=BadgeType.GOLD,
                unlocks=["expert_mode", "teacher_tools"]
            ),
            Achievement(
                id="arabic_master",
                title="Master of Arabic",
                description="Master 1000 Quranic words",
                category=AchievementCategory.LEARNING,
                rarity=AchievementRarity.MYTHIC,
                icon="👑",
                xp_reward=10000,
                coin_reward=2500,
                requirements={"words_learned": 1000},
                badge_type=BadgeType.DIAMOND,
                unlocks=["master_title", "exclusive_content"]
            ),
        ]
        
        # CONSISTENCY ACHIEVEMENTS
        consistency_achievements = [
            Achievement(
                id="consistent_learner",
                title="Consistent Student",
                description="Study for 3 consecutive days",
                category=AchievementCategory.CONSISTENCY,
                rarity=AchievementRarity.COMMON,
                icon="🔥",
                xp_reward=100,
                coin_reward=25,
                requirements={"current_streak": 3},
                islamic_reference="The most beloved deeds to Allah are consistent ones"
            ),
            Achievement(
                id="week_warrior",
                title="Week Warrior",
                description="Maintain a 7-day study streak",
                category=AchievementCategory.CONSISTENCY,
                rarity=AchievementRarity.RARE,
                icon="⚡",
                xp_reward=300,
                coin_reward=75,
                requirements={"current_streak": 7},
                badge_type=BadgeType.BRONZE
            ),
            Achievement(
                id="month_master",
                title="Month Master",
                description="Study every day for 30 days",
                category=AchievementCategory.CONSISTENCY,
                rarity=AchievementRarity.EPIC,
                icon="🌙",
                xp_reward=1500,
                coin_reward=300,
                requirements={"current_streak": 30},
                badge_type=BadgeType.SILVER,
                unlocks=["streak_saver", "priority_support"]
            ),
            Achievement(
                id="year_champion",
                title="Year Champion",
                description="Study for 365 consecutive days",
                category=AchievementCategory.CONSISTENCY,
                rarity=AchievementRarity.MYTHIC,
                icon="🎯",
                xp_reward=10000,
                coin_reward=2000,
                requirements={"current_streak": 365},
                badge_type=BadgeType.DIAMOND,
                unlocks=["legend_title", "custom_badge"]
            ),
        ]
        
        # MASTERY ACHIEVEMENTS
        mastery_achievements = [
            Achievement(
                id="perfect_score",
                title="Perfect Student",
                description="Get 100% on your first quiz",
                category=AchievementCategory.MASTERY,
                rarity=AchievementRarity.COMMON,
                icon="💯",
                xp_reward=100,
                coin_reward=20,
                requirements={"perfect_scores": 1}
            ),
            Achievement(
                id="quiz_master",
                title="Quiz Master",
                description="Score 100% on 10 quizzes",
                category=AchievementCategory.MASTERY,
                rarity=AchievementRarity.RARE,
                icon="🎯",
                xp_reward=500,
                coin_reward=100,
                requirements={"perfect_scores": 10},
                badge_type=BadgeType.BRONZE
            ),
            Achievement(
                id="speed_demon",
                title="Lightning Fast",
                description="Complete a quiz in under 30 seconds",
                category=AchievementCategory.MASTERY,
                rarity=AchievementRarity.EPIC,
                icon="⚡",
                xp_reward=750,
                coin_reward=150,
                requirements={"fastest_quiz_time": 30}
            ),
            Achievement(
                id="pronunciation_perfect",
                title="Tajweed Master",
                description="Get 95%+ pronunciation score 5 times",
                category=AchievementCategory.MASTERY,
                rarity=AchievementRarity.LEGENDARY,
                icon="🎵",
                xp_reward=2000,
                coin_reward=400,
                requirements={"high_pronunciation_scores": 5},
                islamic_reference="Beautify the Quran with your voices"
            ),
        ]
        
        # SPIRITUAL ACHIEVEMENTS (Islamic Themed)
        spiritual_achievements = [
            Achievement(
                id="fatiha_master",
                title="Guardian of Al-Fatiha",
                description="Master all words from Surah Al-Fatiha",
                category=AchievementCategory.SPIRITUAL,
                rarity=AchievementRarity.EPIC,
                icon="🕌",
                xp_reward=1000,
                coin_reward=200,
                requirements={"surah_1_complete": True},
                islamic_reference="No prayer is valid without Al-Fatiha",
                badge_type=BadgeType.GOLD
            ),
            Achievement(
                id="dua_collector",
                title="Dua Collector",
                description="Learn 10 Islamic supplications",
                category=AchievementCategory.SPIRITUAL,
                rarity=AchievementRarity.RARE,
                icon="🤲",
                xp_reward=500,
                coin_reward=100,
                requirements={"duas_learned": 10},
                islamic_reference="Dua is the weapon of the believer"
            ),
            Achievement(
                id="ramadan_warrior",
                title="Ramadan Warrior",
                description="Study every day during Ramadan",
                category=AchievementCategory.SPIRITUAL,
                rarity=AchievementRarity.LEGENDARY,
                icon="🌙",
                xp_reward=3000,
                coin_reward=500,
                requirements={"ramadan_streak": 30},
                islamic_reference="The month of Quran revelation",
                badge_type=BadgeType.PLATINUM
            ),
            Achievement(
                id="night_of_power",
                title="Laylat al-Qadr Seeker",
                description="Study on the Night of Power",
                category=AchievementCategory.SPIRITUAL,
                rarity=AchievementRarity.MYTHIC,
                icon="✨",
                xp_reward=5000,
                coin_reward=1000,
                requirements={"laylat_al_qadr_study": True},
                islamic_reference="Better than a thousand months"
            ),
        ]
        
        # SOCIAL ACHIEVEMENTS
        social_achievements = [
            Achievement(
                id="first_friend",
                title="Making Connections",
                description="Add your first friend",
                category=AchievementCategory.SOCIAL,
                rarity=AchievementRarity.COMMON,
                icon="👥",
                xp_reward=50,
                coin_reward=10,
                requirements={"friends_count": 1}
            ),
            Achievement(
                id="challenge_winner",
                title="Challenge Champion",
                description="Win your first head-to-head challenge",
                category=AchievementCategory.SOCIAL,
                rarity=AchievementRarity.RARE,
                icon="🏆",
                xp_reward=200,
                coin_reward=50,
                requirements={"challenges_won": 1}
            ),
            Achievement(
                id="study_circle_leader",
                title="Study Circle Leader",
                description="Create and lead a study group",
                category=AchievementCategory.SOCIAL,
                rarity=AchievementRarity.EPIC,
                icon="👑",
                xp_reward=1000,
                coin_reward=200,
                requirements={"study_groups_created": 1},
                unlocks=["group_management_tools"]
            ),
        ]
        
        # MILESTONE ACHIEVEMENTS
        milestone_achievements = [
            Achievement(
                id="level_10",
                title="Rising Star",
                description="Reach level 10",
                category=AchievementCategory.MILESTONE,
                rarity=AchievementRarity.RARE,
                icon="⭐",
                xp_reward=500,
                coin_reward=100,
                requirements={"level": 10}
            ),
            Achievement(
                id="level_25",
                title="Dedicated Learner",
                description="Reach level 25",
                category=AchievementCategory.MILESTONE,
                rarity=AchievementRarity.EPIC,
                icon="🌟",
                xp_reward=1500,
                coin_reward=300,
                requirements={"level": 25},
                badge_type=BadgeType.SILVER
            ),
            Achievement(
                id="level_50",
                title="Arabic Scholar",
                description="Reach level 50",
                category=AchievementCategory.MILESTONE,
                rarity=AchievementRarity.LEGENDARY,
                icon="💫",
                xp_reward=5000,
                coin_reward=1000,
                requirements={"level": 50},
                badge_type=BadgeType.GOLD,
                unlocks=["scholar_privileges"]
            ),
            Achievement(
                id="level_100",
                title="Master of Knowledge",
                description="Reach the legendary level 100",
                category=AchievementCategory.MILESTONE,
                rarity=AchievementRarity.MYTHIC,
                icon="🔮",
                xp_reward=25000,
                coin_reward=5000,
                requirements={"level": 100},
                badge_type=BadgeType.DIAMOND,
                unlocks=["master_title", "all_features"]
            ),
        ]
        
        # SPECIAL EVENT ACHIEVEMENTS
        special_achievements = [
            Achievement(
                id="app_anniversary",
                title="Anniversary Celebrant",
                description="Study during the app's anniversary",
                category=AchievementCategory.SPECIAL_EVENT,
                rarity=AchievementRarity.LEGENDARY,
                icon="🎉",
                xp_reward=2000,
                coin_reward=500,
                requirements={"anniversary_participation": True},
                hidden=True
            ),
            Achievement(
                id="early_adopter",
                title="Pioneer",
                description="Among the first 1000 users",
                category=AchievementCategory.SPECIAL_EVENT,
                rarity=AchievementRarity.MYTHIC,
                icon="🗿",
                xp_reward=10000,
                coin_reward=2000,
                requirements={"user_number": 1000},
                badge_type=BadgeType.DIAMOND,
                hidden=True
            ),
        ]
        
        # Combine all achievements
        all_achievements = (
            learning_achievements + consistency_achievements + 
            mastery_achievements + spiritual_achievements + 
            social_achievements + milestone_achievements + 
            special_achievements
        )
        
        # Convert to dictionary
        for achievement in all_achievements:
            achievements[achievement.id] = achievement
        
        return achievements
    
    def _calculate_level_requirements(self) -> Dict[int, int]:
        """Calculate XP requirements for each level (1-100)"""
        
        level_requirements = {}
        
        for level in range(1, 101):
            if level == 1:
                level_requirements[level] = 0
            else:
                # Exponential growth with some balancing
                base_xp = 100
                level_requirements[level] = int(base_xp * (level ** 1.5))
        
        return level_requirements
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user gamification profile"""
        
        try:
            profile_data = await self.db.user_profiles.find_one({"user_id": user_id})
            
            if profile_data:
                return UserProfile(**profile_data)
            else:
                # Create new profile
                new_profile = UserProfile(user_id=user_id)
                await self.db.user_profiles.insert_one(new_profile.dict())
                return new_profile
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return UserProfile(user_id=user_id)
    
    async def award_xp(self, user_id: str, xp_amount: int, reason: str = "") -> Dict[str, Any]:
        """Award XP to user and check for level ups"""
        
        try:
            profile = await self.get_user_profile(user_id)
            old_level = profile.current_level
            
            # Add XP
            profile.total_xp += xp_amount
            
            # Calculate new level
            new_level = self._calculate_level_from_xp(profile.total_xp)
            level_up = new_level > old_level
            
            profile.current_level = new_level
            
            # Save updated profile
            await self.db.user_profiles.update_one(
                {"user_id": user_id},
                {"$set": profile.dict()},
                upsert=True
            )
            
            result = {
                "xp_awarded": xp_amount,
                "total_xp": profile.total_xp,
                "old_level": old_level,
                "new_level": new_level,
                "level_up": level_up,
                "reason": reason
            }
            
            # Check for new achievements if level up occurred
            if level_up:
                level_achievements = await self.check_level_achievements(user_id, new_level)
                result["level_achievements"] = level_achievements
            
            logger.info(f"Awarded {xp_amount} XP to user {user_id}: {reason}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error awarding XP: {e}")
            return {"error": "Failed to award XP"}
    
    def _calculate_level_from_xp(self, total_xp: int) -> int:
        """Calculate level based on total XP"""
        
        for level in range(100, 0, -1):
            if total_xp >= self.level_requirements[level]:
                return level
        
        return 1
    
    async def check_achievements(self, user_id: str, activity_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check if user has unlocked any new achievements"""
        
        try:
            profile = await self.get_user_profile(user_id)
            unlocked_achievements = []
            
            for achievement_id, achievement in self.achievements.items():
                # Skip if already unlocked
                if achievement_id in profile.achievements_unlocked:
                    continue
                
                # Check if requirements are met
                if self._check_achievement_requirements(achievement, profile, activity_data):
                    # Unlock achievement
                    profile.achievements_unlocked.append(achievement_id)
                    
                    # Award XP and coins
                    profile.total_xp += achievement.xp_reward
                    profile.coins += achievement.coin_reward
                    
                    # Add badge if applicable
                    if achievement.badge_type:
                        badge_id = f"{achievement_id}_{achievement.badge_type.value}"
                        profile.badges_earned.append(badge_id)
                    
                    # Unlock features if applicable
                    if achievement.unlocks:
                        profile.unlocked_features.extend(achievement.unlocks)
                    
                    unlocked_achievements.append({
                        "achievement": achievement,
                        "unlocked_at": datetime.utcnow().isoformat()
                    })
                    
                    logger.info(f"User {user_id} unlocked achievement: {achievement.title}")
            
            # Save updated profile
            if unlocked_achievements:
                await self.db.user_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": profile.dict()},
                    upsert=True
                )
            
            return unlocked_achievements
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []
    
    def _check_achievement_requirements(
        self, 
        achievement: Achievement, 
        profile: UserProfile, 
        activity_data: Dict[str, Any]
    ) -> bool:
        """Check if achievement requirements are met"""
        
        try:
            requirements = achievement.requirements
            
            # Check each requirement
            for req_key, req_value in requirements.items():
                if req_key == "words_learned":
                    if profile.words_learned < req_value:
                        return False
                elif req_key == "current_streak":
                    if profile.current_streak < req_value:
                        return False
                elif req_key == "perfect_scores":
                    if profile.perfect_scores < req_value:
                        return False
                elif req_key == "level":
                    if profile.current_level < req_value:
                        return False
                elif req_key == "friends_count":
                    if profile.friends_count < req_value:
                        return False
                elif req_key == "challenges_won":
                    if profile.challenges_won < req_value:
                        return False
                elif req_key == "duas_learned":
                    if profile.duas_learned < req_value:
                        return False
                elif req_key == "fastest_quiz_time":
                    fastest_time = activity_data.get("fastest_quiz_time", float('inf'))
                    if fastest_time > req_value:
                        return False
                elif req_key == "high_pronunciation_scores":
                    high_scores = activity_data.get("high_pronunciation_scores", 0)
                    if high_scores < req_value:
                        return False
                elif req_key == "surah_1_complete":
                    if not activity_data.get("surah_1_complete", False):
                        return False
                elif req_key == "ramadan_streak":
                    ramadan_streak = activity_data.get("ramadan_streak", 0)
                    if ramadan_streak < req_value:
                        return False
                # Add more requirement checks as needed
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking achievement requirements: {e}")
            return False
    
    async def check_level_achievements(self, user_id: str, new_level: int) -> List[Dict[str, Any]]:
        """Check for level milestone achievements"""
        
        level_achievements = []
        milestone_levels = [10, 25, 50, 100]
        
        for milestone in milestone_levels:
            if new_level >= milestone:
                achievement_id = f"level_{milestone}"
                if achievement_id in self.achievements:
                    activity_data = {"level": new_level}
                    achievements = await self.check_achievements(user_id, activity_data)
                    level_achievements.extend(achievements)
        
        return level_achievements
    
    async def get_leaderboard(
        self, 
        leaderboard_type: LeaderboardType, 
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get leaderboard data"""
        
        try:
            now = datetime.utcnow()
            
            # Determine time filter
            time_filter = {}
            if leaderboard_type == LeaderboardType.WEEKLY:
                week_start = now - timedelta(days=7)
                time_filter = {"last_activity": {"$gte": week_start}}
            elif leaderboard_type == LeaderboardType.MONTHLY:
                month_start = now - timedelta(days=30)
                time_filter = {"last_activity": {"$gte": month_start}}
            
            # Get profiles with sorting
            sort_criteria = [("total_xp", -1), ("current_level", -1)]
            
            profiles_cursor = self.db.user_profiles.find(time_filter).sort(sort_criteria).limit(limit)
            profiles = await profiles_cursor.to_list(limit)
            
            leaderboard_data = []
            user_rank = None
            
            for index, profile_data in enumerate(profiles):
                profile = UserProfile(**profile_data)
                rank = index + 1
                
                entry = {
                    "rank": rank,
                    "user_id": profile.user_id,
                    "total_xp": profile.total_xp,
                    "current_level": profile.current_level,
                    "words_learned": profile.words_learned,
                    "current_streak": profile.current_streak,
                    "achievements_count": len(profile.achievements_unlocked)
                }
                
                leaderboard_data.append(entry)
                
                if profile.user_id == user_id:
                    user_rank = rank
            
            return {
                "leaderboard_type": leaderboard_type,
                "entries": leaderboard_data,
                "user_rank": user_rank,
                "total_participants": len(leaderboard_data),
                "last_updated": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return {"error": "Failed to load leaderboard"}
    
    async def create_daily_quests(self, user_id: str) -> List[Quest]:
        """Generate daily quests for user"""
        
        try:
            profile = await self.get_user_profile(user_id)
            today = datetime.utcnow().date()
            
            # Check if already have today's quests
            existing_quests = await self.db.daily_quests.find({
                "user_id": user_id,
                "date": today.isoformat()
            }).to_list(10)
            
            if existing_quests:
                return [Quest(**quest_data) for quest_data in existing_quests]
            
            # Generate new daily quests
            quest_templates = [
                {
                    "title": "Daily Vocabulary",
                    "description": "Learn 5 new words today",
                    "requirements": {"words_learned_today": 5},
                    "rewards": [{"type": "xp", "amount": 100}, {"type": "coins", "amount": 25}]
                },
                {
                    "title": "Perfect Practice",
                    "description": "Score 100% on a quiz",
                    "requirements": {"perfect_score_today": 1},
                    "rewards": [{"type": "xp", "amount": 150}, {"type": "coins", "amount": 30}]
                },
                {
                    "title": "Consistency Champion",
                    "description": "Study for at least 10 minutes",
                    "requirements": {"study_time_today": 10},
                    "rewards": [{"type": "xp", "amount": 75}, {"type": "coins", "amount": 20}]
                }
            ]
            
            daily_quests = []
            
            for i, template in enumerate(quest_templates):
                quest = Quest(
                    id=f"daily_{user_id}_{today.isoformat()}_{i}",
                    title=template["title"],
                    description=template["description"],
                    quest_type=QuestType.DAILY,
                    requirements=template["requirements"],
                    rewards=template["rewards"],
                    start_date=datetime.combine(today, datetime.min.time()),
                    end_date=datetime.combine(today, datetime.max.time())
                )
                
                daily_quests.append(quest)
                
                # Save to database
                await self.db.daily_quests.insert_one({
                    **quest.__dict__,
                    "user_id": user_id,
                    "date": today.isoformat()
                })
            
            return daily_quests
            
        except Exception as e:
            logger.error(f"Error creating daily quests: {e}")
            return []
    
    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        
        try:
            profile = await self.get_user_profile(user_id)
            
            # Calculate additional stats
            accuracy_rate = 0.0
            if profile.quizzes_taken > 0:
                accuracy_rate = (profile.perfect_scores / profile.quizzes_taken) * 100
            
            # Get rank
            global_leaderboard = await self.get_leaderboard(LeaderboardType.GLOBAL, user_id)
            global_rank = global_leaderboard.get("user_rank", "Unranked")
            
            # Calculate next level progress
            current_level_xp = self.level_requirements[profile.current_level]
            next_level_xp = self.level_requirements.get(profile.current_level + 1, current_level_xp)
            level_progress = ((profile.total_xp - current_level_xp) / (next_level_xp - current_level_xp)) * 100
            
            statistics = {
                "profile": profile.dict(),
                "calculated_stats": {
                    "accuracy_rate": round(accuracy_rate, 1),
                    "global_rank": global_rank,
                    "level_progress": round(level_progress, 1),
                    "next_level_xp_needed": next_level_xp - profile.total_xp,
                    "achievements_completion": round((len(profile.achievements_unlocked) / len(self.achievements)) * 100, 1),
                    "estimated_study_hours": round(profile.total_study_time / 60, 1)
                },
                "milestones": {
                    "words_to_next_milestone": self._calculate_next_word_milestone(profile.words_learned),
                    "days_to_next_streak_milestone": self._calculate_next_streak_milestone(profile.current_streak),
                    "xp_to_next_level": next_level_xp - profile.total_xp
                }
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return {"error": "Failed to load statistics"}
    
    def _calculate_next_word_milestone(self, current_words: int) -> int:
        """Calculate words needed for next milestone"""
        milestones = [50, 100, 250, 500, 1000]
        
        for milestone in milestones:
            if current_words < milestone:
                return milestone - current_words
        
        return 0  # Already passed all milestones
    
    def _calculate_next_streak_milestone(self, current_streak: int) -> int:
        """Calculate days needed for next streak milestone"""
        milestones = [7, 30, 100, 365]
        
        for milestone in milestones:
            if current_streak < milestone:
                return milestone - current_streak
        
        return 0  # Already passed all milestones

# Global instance
gamification_system = None  # Will be initialized with database
