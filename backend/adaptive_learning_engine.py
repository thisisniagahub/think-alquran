# Adaptive Learning Engine with Spaced Repetition System (SRS)
# Revolutionary learning algorithm that adapts to each user's pace and style
# Implements scientific memory optimization techniques

import asyncio
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel
from enum import Enum
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class MemoryStrength(str, Enum):
    WEAK = "weak"           # 0-30%
    MODERATE = "moderate"   # 31-70%
    STRONG = "strong"       # 71-90%
    MASTERED = "mastered"   # 91-100%

class LearningDifficulty(str, Enum):
    TOO_EASY = "too_easy"
    OPTIMAL = "optimal"
    TOO_HARD = "too_hard"

class ReviewPriority(str, Enum):
    URGENT = "urgent"       # Overdue reviews
    HIGH = "high"          # Due today
    MEDIUM = "medium"      # Due soon
    LOW = "low"           # Future reviews

@dataclass
class LearningMetrics:
    accuracy: float
    response_time: float
    retention_rate: float
    difficulty_rating: float
    engagement_score: float

class WordMemoryCard(BaseModel):
    word_id: str
    user_id: str
    
    # SRS Algorithm Variables
    ease_factor: float = 2.5          # How easy is this word (1.3-3.0)
    interval: int = 1                 # Days until next review
    repetitions: int = 0              # Number of successful reviews
    due_date: datetime                # When to review next
    
    # Learning Metrics
    total_reviews: int = 0
    correct_reviews: int = 0
    average_response_time: float = 0.0
    last_review_date: Optional[datetime] = None
    creation_date: datetime = datetime.utcnow()
    
    # Memory Strength Indicators
    memory_strength: MemoryStrength = MemoryStrength.WEAK
    stability: float = 0.0            # How stable is the memory (0-1)
    retrievability: float = 1.0       # How retrievable now (0-1)
    
    # Adaptive Factors
    difficulty_history: List[float] = []
    response_time_history: List[float] = []
    error_patterns: List[str] = []
    
    # Personalization
    optimal_review_time: Optional[int] = None  # Hour of day (0-23)
    learning_style_affinity: Dict[str, float] = {}

class AdaptiveLearningEngine:
    """
    Revolutionary Adaptive Learning Engine with Scientific Memory Optimization
    
    Implements:
    - Spaced Repetition System (SRS) based on SM-2+ algorithm
    - Adaptive difficulty adjustment
    - Personalized learning paths
    - Memory strength prediction
    - Forgetting curve analysis
    """
    
    def __init__(self, db):
        self.db = db
        
        # SRS Parameters (scientifically optimized)
        self.min_ease_factor = 1.3
        self.max_ease_factor = 3.0
        self.ease_factor_increment = 0.1
        self.ease_factor_decrement = 0.2
        
        # Memory Model Parameters
        self.forgetting_curve_constant = 0.5
        self.retrieval_threshold = 0.9
        self.stability_decay_rate = 0.95
        
        # Adaptive Parameters
        self.optimal_success_rate = 0.85  # Target 85% success rate
        self.difficulty_adjustment_sensitivity = 0.1

    async def initialize_word_card(self, user_id: str, word_id: str) -> WordMemoryCard:
        """Initialize a new memory card for a word"""
        
        card = WordMemoryCard(
            word_id=word_id,
            user_id=user_id,
            due_date=datetime.utcnow(),
            creation_date=datetime.utcnow()
        )
        
        # Save to database
        await self.db.memory_cards.insert_one(card.dict())
        
        logger.info(f"Initialized memory card for user {user_id}, word {word_id}")
        return card

    async def process_review_result(
        self, 
        user_id: str, 
        word_id: str, 
        is_correct: bool,
        response_time: float,
        difficulty_rating: float = 3.0  # 1-5 scale
    ) -> WordMemoryCard:
        """
        Process a review result and update the memory card using advanced SRS
        """
        
        # Get existing card or create new one
        card_data = await self.db.memory_cards.find_one({
            "user_id": user_id,
            "word_id": word_id
        })
        
        if card_data:
            card = WordMemoryCard(**card_data)
        else:
            card = await self.initialize_word_card(user_id, word_id)
        
        # Update basic metrics
        card.total_reviews += 1
        if is_correct:
            card.correct_reviews += 1
        
        # Update response time (weighted average)
        if card.average_response_time == 0:
            card.average_response_time = response_time
        else:
            # Weighted average with more weight on recent responses
            card.average_response_time = (
                card.average_response_time * 0.7 + response_time * 0.3
            )
        
        # Add to history
        card.difficulty_history.append(difficulty_rating)
        card.response_time_history.append(response_time)
        
        # Keep only last 20 entries
        card.difficulty_history = card.difficulty_history[-20:]
        card.response_time_history = card.response_time_history[-20:]
        
        # Calculate quality of response (0-5 scale)
        quality = self._calculate_response_quality(
            is_correct, response_time, difficulty_rating, card
        )
        
        # Update SRS parameters
        card = self._update_srs_parameters(card, quality)
        
        # Update memory strength indicators
        card = self._update_memory_strength(card)
        
        # Set next review date
        card.due_date = datetime.utcnow() + timedelta(days=card.interval)
        card.last_review_date = datetime.utcnow()
        
        # Save updated card
        await self.db.memory_cards.update_one(
            {"user_id": user_id, "word_id": word_id},
            {"$set": card.dict()},
            upsert=True
        )
        
        logger.info(f"Updated memory card: word {word_id}, interval {card.interval} days, ease {card.ease_factor}")
        
        return card

    def _calculate_response_quality(
        self, 
        is_correct: bool, 
        response_time: float, 
        difficulty_rating: float,
        card: WordMemoryCard
    ) -> float:
        """
        Calculate response quality (0-5 scale) considering multiple factors
        """
        
        if not is_correct:
            return 0.0  # Failed response
        
        # Base quality for correct response
        quality = 3.0
        
        # Adjust for response time (faster = better, up to a point)
        optimal_time = 5.0  # 5 seconds is optimal
        if response_time <= optimal_time:
            time_bonus = (optimal_time - response_time) / optimal_time * 0.5
            quality += time_bonus
        else:
            # Penalty for taking too long
            time_penalty = min(1.0, (response_time - optimal_time) / 20.0)
            quality -= time_penalty
        
        # Adjust for difficulty rating (easier = lower quality)
        if difficulty_rating < 2.0:  # Too easy
            quality -= 0.5
        elif difficulty_rating > 4.0:  # Too hard but got it right
            quality += 0.5
        
        # Consistency bonus (if user has been performing well)
        if card.total_reviews >= 5:
            recent_accuracy = card.correct_reviews / card.total_reviews
            if recent_accuracy > 0.8:
                quality += 0.3
        
        return max(0.0, min(5.0, quality))

    def _update_srs_parameters(self, card: WordMemoryCard, quality: float) -> WordMemoryCard:
        """
        Update SRS parameters based on SM-2+ algorithm with enhancements
        """
        
        if quality >= 3.0:  # Successful recall
            if card.repetitions == 0:
                card.interval = 1
            elif card.repetitions == 1:
                card.interval = 6
            else:
                card.interval = int(card.interval * card.ease_factor)
            
            card.repetitions += 1
            
            # Update ease factor based on quality
            ease_change = (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            card.ease_factor += ease_change
            
        else:  # Failed recall
            card.repetitions = 0
            card.interval = 1
            
            # Reduce ease factor for failed responses
            card.ease_factor -= self.ease_factor_decrement
        
        # Keep ease factor within bounds
        card.ease_factor = max(self.min_ease_factor, 
                              min(self.max_ease_factor, card.ease_factor))
        
        # Apply adaptive adjustments
        card = self._apply_adaptive_adjustments(card, quality)
        
        return card

    def _apply_adaptive_adjustments(self, card: WordMemoryCard, quality: float) -> WordMemoryCard:
        """
        Apply adaptive adjustments based on user's learning patterns
        """
        
        # Analyze recent performance
        if len(card.difficulty_history) >= 5:
            recent_difficulty = np.mean(card.difficulty_history[-5:])
            recent_times = np.mean(card.response_time_history[-5:])
            
            # Adjust based on consistent difficulty ratings
            if recent_difficulty < 2.0:  # Consistently too easy
                card.interval = int(card.interval * 1.2)  # Increase interval
            elif recent_difficulty > 4.0:  # Consistently too hard
                card.interval = int(card.interval * 0.8)  # Decrease interval
            
            # Adjust based on response times
            if recent_times > 15.0:  # Taking too long
                card.ease_factor *= 0.95  # Make reviews more frequent
            elif recent_times < 3.0:  # Very quick responses
                card.ease_factor *= 1.05  # Can extend intervals
        
        return card

    def _update_memory_strength(self, card: WordMemoryCard) -> WordMemoryCard:
        """
        Update memory strength indicators using cognitive science models
        """
        
        # Calculate accuracy rate
        accuracy = card.correct_reviews / card.total_reviews if card.total_reviews > 0 else 0
        
        # Update stability (how well the memory is consolidated)
        if card.last_review_date:
            days_since_review = (datetime.utcnow() - card.last_review_date).days
            stability_decay = self.stability_decay_rate ** days_since_review
            card.stability = min(1.0, card.stability * stability_decay + accuracy * 0.1)
        else:
            card.stability = accuracy * 0.5
        
        # Calculate retrievability (how likely to recall now)
        if card.due_date:
            days_overdue = (datetime.utcnow() - card.due_date).days
            if days_overdue <= 0:
                card.retrievability = 1.0  # Not due yet
            else:
                # Forgetting curve: R(t) = e^(-t/S)
                card.retrievability = math.exp(-days_overdue / max(1, card.stability * 10))
        
        # Determine memory strength category
        strength_score = (accuracy * 0.4 + card.stability * 0.3 + card.retrievability * 0.3) * 100
        
        if strength_score >= 91:
            card.memory_strength = MemoryStrength.MASTERED
        elif strength_score >= 71:
            card.memory_strength = MemoryStrength.STRONG
        elif strength_score >= 31:
            card.memory_strength = MemoryStrength.MODERATE
        else:
            card.memory_strength = MemoryStrength.WEAK
        
        return card

    async def get_due_reviews(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get words due for review, ordered by priority
        """
        
        try:
            now = datetime.utcnow()
            
            # Get all memory cards for user
            cards_cursor = self.db.memory_cards.find({"user_id": user_id})
            cards = await cards_cursor.to_list(1000)
            
            due_reviews = []
            
            for card_data in cards:
                card = WordMemoryCard(**card_data)
                
                # Calculate priority
                priority = self._calculate_review_priority(card, now)
                
                if priority != ReviewPriority.LOW or len(due_reviews) < limit:
                    # Get word details
                    word = await self.db.words.find_one({"_id": card.word_id})
                    if word:
                        due_reviews.append({
                            "word_id": card.word_id,
                            "word_data": word,
                            "memory_card": card.dict(),
                            "priority": priority,
                            "days_overdue": (now - card.due_date).days,
                            "memory_strength": card.memory_strength,
                            "estimated_difficulty": self._estimate_difficulty(card)
                        })
            
            # Sort by priority and overdue days
            priority_order = {
                ReviewPriority.URGENT: 0,
                ReviewPriority.HIGH: 1,
                ReviewPriority.MEDIUM: 2,
                ReviewPriority.LOW: 3
            }
            
            due_reviews.sort(key=lambda x: (
                priority_order[x["priority"]], 
                -x["days_overdue"]
            ))
            
            return due_reviews[:limit]
            
        except Exception as e:
            logger.error(f"Error getting due reviews: {e}")
            return []

    def _calculate_review_priority(self, card: WordMemoryCard, now: datetime) -> ReviewPriority:
        """Calculate review priority based on multiple factors"""
        
        days_overdue = (now - card.due_date).days
        
        if days_overdue >= 2:
            return ReviewPriority.URGENT
        elif days_overdue >= 0:
            return ReviewPriority.HIGH
        elif days_overdue >= -1:
            return ReviewPriority.MEDIUM
        else:
            return ReviewPriority.LOW

    def _estimate_difficulty(self, card: WordMemoryCard) -> float:
        """Estimate how difficult this review will be for the user"""
        
        base_difficulty = 3.0
        
        # Adjust based on memory strength
        if card.memory_strength == MemoryStrength.WEAK:
            base_difficulty += 1.0
        elif card.memory_strength == MemoryStrength.MASTERED:
            base_difficulty -= 1.0
        
        # Adjust based on retrievability
        base_difficulty += (1 - card.retrievability) * 1.5
        
        # Adjust based on historical difficulty
        if card.difficulty_history:
            avg_historical_difficulty = np.mean(card.difficulty_history)
            base_difficulty = (base_difficulty + avg_historical_difficulty) / 2
        
        return max(1.0, min(5.0, base_difficulty))

    async def generate_adaptive_lesson(self, user_id: str, target_duration: int = 15) -> Dict[str, Any]:
        """
        Generate an adaptive lesson based on user's learning state
        """
        
        try:
            # Get due reviews
            due_reviews = await self.get_due_reviews(user_id, limit=50)
            
            # Get user's learning analytics
            analytics = await self.get_user_learning_analytics(user_id)
            
            # Select optimal mix of content
            lesson_content = {
                "review_words": [],
                "new_words": [],
                "reinforcement_words": [],
                "estimated_duration": target_duration,
                "difficulty_level": analytics.get("current_level", "intermediate"),
                "focus_areas": analytics.get("weak_areas", []),
                "lesson_strategy": "adaptive"
            }
            
            # Allocate time for different activities
            review_time = target_duration * 0.6  # 60% for reviews
            new_content_time = target_duration * 0.3  # 30% for new content
            reinforcement_time = target_duration * 0.1  # 10% for reinforcement
            
            # Add review words (prioritize urgent/high priority)
            review_count = 0
            for review in due_reviews:
                if review["priority"] in [ReviewPriority.URGENT, ReviewPriority.HIGH]:
                    lesson_content["review_words"].append(review)
                    review_count += 1
                    if review_count * 1.5 >= review_time:  # 1.5 min per review word
                        break
            
            # Add new words if there's capacity
            if len(lesson_content["review_words"]) < 10:
                new_words = await self._get_new_words_for_user(user_id, analytics)
                new_word_count = min(3, int(new_content_time / 2))  # 2 min per new word
                lesson_content["new_words"] = new_words[:new_word_count]
            
            # Add reinforcement for weak areas
            weak_words = await self._get_weak_area_words(user_id, analytics.get("weak_areas", []))
            lesson_content["reinforcement_words"] = weak_words[:2]
            
            # Generate lesson metadata
            lesson_content["adaptive_insights"] = {
                "total_words": len(lesson_content["review_words"]) + len(lesson_content["new_words"]) + len(lesson_content["reinforcement_words"]),
                "review_focus": len(lesson_content["review_words"]) > len(lesson_content["new_words"]),
                "difficulty_distribution": self._analyze_lesson_difficulty(lesson_content),
                "predicted_success_rate": analytics.get("predicted_success_rate", 0.8),
                "optimal_study_time": analytics.get("optimal_study_time", "evening")
            }
            
            return lesson_content
            
        except Exception as e:
            logger.error(f"Error generating adaptive lesson: {e}")
            return {"error": "Failed to generate adaptive lesson"}

    async def get_user_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive learning analytics for a user
        """
        
        try:
            # Get all memory cards for user
            cards_cursor = self.db.memory_cards.find({"user_id": user_id})
            cards = await cards_cursor.to_list(1000)
            
            if not cards:
                return {"status": "no_data"}
            
            analytics = {
                "total_words_studied": len(cards),
                "words_mastered": 0,
                "words_in_progress": 0,
                "words_struggling": 0,
                "overall_accuracy": 0.0,
                "average_response_time": 0.0,
                "current_level": "beginner",
                "weak_areas": [],
                "strong_areas": [],
                "study_streak": 0,
                "optimal_study_time": "morning",
                "predicted_success_rate": 0.8,
                "learning_velocity": "moderate"
            }
            
            total_reviews = 0
            total_correct = 0
            total_time = 0
            
            memory_strengths = []
            response_times = []
            
            for card_data in cards:
                card = WordMemoryCard(**card_data)
                
                if card.memory_strength == MemoryStrength.MASTERED:
                    analytics["words_mastered"] += 1
                elif card.memory_strength in [MemoryStrength.WEAK]:
                    analytics["words_struggling"] += 1
                else:
                    analytics["words_in_progress"] += 1
                
                total_reviews += card.total_reviews
                total_correct += card.correct_reviews
                total_time += card.average_response_time * card.total_reviews
                
                memory_strengths.append(card.memory_strength.value)
                response_times.append(card.average_response_time)
            
            # Calculate overall metrics
            if total_reviews > 0:
                analytics["overall_accuracy"] = total_correct / total_reviews
                analytics["average_response_time"] = total_time / total_reviews
            
            # Determine current level
            mastery_rate = analytics["words_mastered"] / len(cards)
            if mastery_rate < 0.2:
                analytics["current_level"] = "beginner"
            elif mastery_rate < 0.6:
                analytics["current_level"] = "intermediate"
            elif mastery_rate < 0.8:
                analytics["current_level"] = "advanced"
            else:
                analytics["current_level"] = "expert"
            
            # Analyze weak and strong areas (simplified)
            analytics["weak_areas"] = ["pronunciation", "grammar"] if analytics["overall_accuracy"] < 0.7 else []
            analytics["strong_areas"] = ["vocabulary", "recognition"] if analytics["overall_accuracy"] > 0.8 else []
            
            # Predict success rate for next session
            analytics["predicted_success_rate"] = min(0.95, analytics["overall_accuracy"] * 1.1)
            
            # Determine learning velocity
            avg_response_time = analytics["average_response_time"]
            if avg_response_time < 5:
                analytics["learning_velocity"] = "fast"
            elif avg_response_time > 15:
                analytics["learning_velocity"] = "slow"
            else:
                analytics["learning_velocity"] = "moderate"
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting learning analytics: {e}")
            return {"status": "error"}

    async def _get_new_words_for_user(self, user_id: str, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get new words appropriate for user's current level"""
        
        try:
            # Get words user hasn't studied yet
            studied_words = await self.db.memory_cards.distinct("word_id", {"user_id": user_id})
            
            # Determine appropriate lesson level
            current_level = analytics.get("current_level", "beginner")
            lesson_mapping = {
                "beginner": [1, 2],
                "intermediate": [2, 3, 4],
                "advanced": [3, 4, 5],
                "expert": [4, 5]
            }
            
            appropriate_lessons = lesson_mapping.get(current_level, [1, 2])
            
            # Get new words from appropriate lessons
            new_words = await self.db.words.find({
                "_id": {"$nin": studied_words},
                "lesson_number": {"$in": appropriate_lessons}
            }).limit(5).to_list(5)
            
            return [{"word_data": word, "is_new": True} for word in new_words]
            
        except Exception as e:
            logger.error(f"Error getting new words: {e}")
            return []

    async def _get_weak_area_words(self, user_id: str, weak_areas: List[str]) -> List[Dict[str, Any]]:
        """Get words for reinforcing weak areas"""
        
        try:
            # Get words where user is struggling
            weak_cards = await self.db.memory_cards.find({
                "user_id": user_id,
                "memory_strength": {"$in": [MemoryStrength.WEAK.value, MemoryStrength.MODERATE.value]}
            }).limit(3).to_list(3)
            
            reinforcement_words = []
            for card_data in weak_cards:
                word = await self.db.words.find_one({"_id": card_data["word_id"]})
                if word:
                    reinforcement_words.append({
                        "word_data": word,
                        "memory_card": card_data,
                        "focus_reason": "weak_area_reinforcement"
                    })
            
            return reinforcement_words
            
        except Exception as e:
            logger.error(f"Error getting weak area words: {e}")
            return []

    def _analyze_lesson_difficulty(self, lesson_content: Dict[str, Any]) -> Dict[str, int]:
        """Analyze the difficulty distribution of a lesson"""
        
        difficulty_count = {"easy": 0, "medium": 0, "hard": 0}
        
        # Analyze review words
        for review in lesson_content.get("review_words", []):
            estimated_difficulty = review.get("estimated_difficulty", 3.0)
            if estimated_difficulty < 2.5:
                difficulty_count["easy"] += 1
            elif estimated_difficulty < 3.5:
                difficulty_count["medium"] += 1
            else:
                difficulty_count["hard"] += 1
        
        # New words are generally medium difficulty
        difficulty_count["medium"] += len(lesson_content.get("new_words", []))
        
        # Reinforcement words are generally hard
        difficulty_count["hard"] += len(lesson_content.get("reinforcement_words", []))
        
        return difficulty_count

# Global instance
adaptive_learning_engine = None  # Will be initialized with database
