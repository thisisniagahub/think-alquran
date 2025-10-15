"""
🌟 Revolutionary Integrated Guidance System
=============================================

This module provides seamless integration between AI Ustaz/Ustazah Assistant 
and Peace TV recommendations, creating the most comprehensive Islamic learning 
experience with contextual video suggestions and authentic Quranic guidance.

Features:
- Smart contextual Peace TV recommendations based on learning context
- Scholar-specific guidance matching with user's current study
- Progress-based content delivery system
- Seamless integration between AI guidance and video content
- Real-time learning path optimization
- Islamic calendar and prayer time integration

JAKIM/JAIS Compliance: All recommendations are vetted for Islamic authenticity
and appropriate for different learning levels and contexts.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import asyncio
import json
from dataclasses import dataclass
import logging

# Import our existing systems
from ai_ustaz_assistant import (
    RevolutionaryAIUstazAssistant, GuidanceContext, PersonaType, 
    QuranicReference, ai_ustaz_assistant
)
from peace_tv_integration import (
    RevolutionaryPeaceTVIntegration, PeaceTVVideo, PeaceTVContentType,
    ScholarName, PeaceTVLanguage, peace_tv_integration
)

# Setup logging
logger = logging.getLogger(__name__)

class LearningLevel(str, Enum):
    """User learning levels for content matching"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    SCHOLAR = "scholar"

class ContentMatchingStrategy(str, Enum):
    """Strategies for matching content to user context"""
    EXACT_TOPIC = "exact_topic"
    COMPLEMENTARY = "complementary"
    PROGRESSIVE = "progressive"
    REINFORCEMENT = "reinforcement"

@dataclass
class IntegratedRecommendation:
    """Combined AI guidance with Peace TV recommendations"""
    ustaz_guidance: Dict[str, Any]
    peace_tv_videos: List[PeaceTVVideo]
    quranic_reference: QuranicReference
    learning_path: List[str]
    next_actions: List[str]
    duas_for_context: str
    estimated_study_time: int
    islamic_benefits: List[str]

@dataclass
class ScholarGuidanceMatch:
    """Matching between scholar expertise and user needs"""
    scholar: ScholarName
    relevance_score: float
    why_recommended: str
    best_videos: List[PeaceTVVideo]
    learning_outcomes: List[str]
    suitable_for_level: LearningLevel

@dataclass
class ProgressBasedContent:
    """Content recommendations based on user progress"""
    current_level: LearningLevel
    recommended_videos: List[PeaceTVVideo]
    skill_focus_areas: List[str]
    next_milestone: str
    estimated_completion_time: int
    prerequisite_knowledge: List[str]

class RevolutionaryIntegratedGuidanceSystem:
    """
    🌟 Revolutionary Integrated Guidance System
    
    Seamlessly combines AI Ustaz guidance with Peace TV recommendations
    for the most comprehensive Islamic learning experience.
    """
    
    def __init__(self, db):
        self.db = db
        
        # Scholar expertise and teaching style mapping
        self.scholar_expertise_detailed = {
            ScholarName.DR_ZAKIR_NAIK: {
                "expertise": ["comparative_religion", "quran_science", "interfaith_dialogue", "medical_miracles"],
                "teaching_style": "analytical_evidence_based",
                "best_for_levels": [LearningLevel.INTERMEDIATE, LearningLevel.ADVANCED],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.QURAN_TAFSEER],
                "personality": "logical, systematic, comprehensive",
                "signature_topics": ["scientific_miracles", "comparative_study", "q_and_a_sessions"]
            },
            ScholarName.DR_ISRAR_AHMAD: {
                "expertise": ["quran_tafseer", "islamic_philosophy", "sufism", "urdu_lectures"],
                "teaching_style": "deep_spiritual_scholarly",
                "best_for_levels": [LearningLevel.INTERMEDIATE, LearningLevel.ADVANCED, LearningLevel.SCHOLAR],
                "content_types": [PeaceTVContentType.QURAN_TAFSEER, PeaceTVContentType.ISLAMIC_HISTORY],
                "personality": "profound, spiritual, philosophical",
                "signature_topics": ["deep_tafseer", "islamic_ideology", "spiritual_development"]
            },
            ScholarName.SHEIKH_AHMED_DEEDAT: {
                "expertise": ["comparative_religion", "bible_quran", "debates", "christian_dialogue"],
                "teaching_style": "debate_oriented_comparative",
                "best_for_levels": [LearningLevel.ADVANCED, LearningLevel.SCHOLAR],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.ISLAMIC_HISTORY],
                "personality": "sharp, logical, confrontational",
                "signature_topics": ["interfaith_dialogue", "bible_quran_comparison", "debate_techniques"]
            },
            ScholarName.DR_BILAL_PHILIPS: {
                "expertise": ["islamic_studies", "arabic_grammar", "hadith_sciences", "methodology"],
                "teaching_style": "systematic_academic",
                "best_for_levels": [LearningLevel.BEGINNER, LearningLevel.INTERMEDIATE],
                "content_types": [PeaceTVContentType.ARABIC_LANGUAGE, PeaceTVContentType.HADITH_EXPLANATION],
                "personality": "methodical, clear, educational",
                "signature_topics": ["arabic_grammar", "islamic_methodology", "hadith_studies"]
            },
            ScholarName.YUSUF_ESTES: {
                "expertise": ["new_muslim_guidance", "basic_islam", "practical_living", "conversion_stories"],
                "teaching_style": "practical_relatable",
                "best_for_levels": [LearningLevel.BEGINNER, LearningLevel.INTERMEDIATE],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.PRAYER_GUIDANCE],
                "personality": "warm, practical, encouraging",
                "signature_topics": ["new_muslim_guidance", "practical_islam", "daily_living"]
            },
            ScholarName.ABDUR_RAHEEM_GREEN: {
                "expertise": ["youth_guidance", "practical_islam", "q_and_a", "modern_challenges"],
                "teaching_style": "contemporary_practical",
                "best_for_levels": [LearningLevel.BEGINNER, LearningLevel.INTERMEDIATE],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.PRAYER_GUIDANCE],
                "personality": "energetic, practical, youth_focused",
                "signature_topics": ["youth_issues", "modern_challenges", "practical_guidance"]
            },
            ScholarName.HUSSEIN_YEE: {
                "expertise": ["chinese_muslim", "southeast_asia", "practical_guidance", "community_building"],
                "teaching_style": "community_focused_practical",
                "best_for_levels": [LearningLevel.BEGINNER, LearningLevel.INTERMEDIATE],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.PRAYER_GUIDANCE],
                "personality": "gentle, community_oriented, practical",
                "signature_topics": ["community_guidance", "family_islam", "practical_living"]
            }
        }
        
        # Context-specific video matching patterns
        self.context_video_matching = {
            GuidanceContext.ONBOARDING: {
                "primary_topics": ["basic_islam", "new_muslim_guidance", "quran_introduction"],
                "recommended_scholars": [ScholarName.YUSUF_ESTES, ScholarName.DR_BILAL_PHILIPS],
                "content_types": [PeaceTVContentType.QURAN_LEARNING, PeaceTVContentType.ISLAMIC_LECTURES],
                "duration_preference": "short_medium"  # 15-45 minutes
            },
            GuidanceContext.LESSON_START: {
                "primary_topics": ["arabic_grammar", "quran_recitation", "word_meanings"],
                "recommended_scholars": [ScholarName.DR_BILAL_PHILIPS, ScholarName.DR_ZAKIR_NAIK],
                "content_types": [PeaceTVContentType.ARABIC_LANGUAGE, PeaceTVContentType.QURAN_LEARNING],
                "duration_preference": "short"  # 10-30 minutes
            },
            GuidanceContext.LESSON_PROGRESS: {
                "primary_topics": ["motivation", "learning_benefits", "knowledge_importance"],
                "recommended_scholars": [ScholarName.DR_ZAKIR_NAIK, ScholarName.YUSUF_ESTES],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.QURAN_TAFSEER],
                "duration_preference": "medium"  # 20-45 minutes
            },
            GuidanceContext.LESSON_COMPLETE: {
                "primary_topics": ["gratitude", "sharing_knowledge", "continuous_learning"],
                "recommended_scholars": [ScholarName.DR_ISRAR_AHMAD, ScholarName.ABDUR_RAHEEM_GREEN],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.QURAN_TAFSEER],
                "duration_preference": "medium_long"  # 30-60 minutes
            },
            GuidanceContext.PRAYER_TIME: {
                "primary_topics": ["prayer_importance", "salah_guidance", "spiritual_connection"],
                "recommended_scholars": [ScholarName.YUSUF_ESTES, ScholarName.HUSSEIN_YEE],
                "content_types": [PeaceTVContentType.PRAYER_GUIDANCE, PeaceTVContentType.ISLAMIC_LECTURES],
                "duration_preference": "short"  # 5-20 minutes
            },
            GuidanceContext.ACHIEVEMENT_UNLOCK: {
                "primary_topics": ["gratitude", "success_in_islam", "continued_improvement"],
                "recommended_scholars": [ScholarName.DR_ZAKIR_NAIK, ScholarName.ABDUR_RAHEEM_GREEN],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.QURAN_TAFSEER],
                "duration_preference": "medium"  # 20-40 minutes
            },
            GuidanceContext.DIFFICULTY_FACING: {
                "primary_topics": ["patience", "overcoming_challenges", "trust_in_allah"],
                "recommended_scholars": [ScholarName.DR_ISRAR_AHMAD, ScholarName.YUSUF_ESTES],
                "content_types": [PeaceTVContentType.ISLAMIC_LECTURES, PeaceTVContentType.QURAN_TAFSEER],
                "duration_preference": "medium_long"  # 25-50 minutes
            }
        }
        
        # Progress-based content mapping
        self.progress_content_mapping = {
            LearningLevel.BEGINNER: {
                "focus_areas": ["basic_arabic", "prayer_basics", "fundamental_concepts"],
                "recommended_scholars": [ScholarName.YUSUF_ESTES, ScholarName.DR_BILAL_PHILIPS, ScholarName.HUSSEIN_YEE],
                "content_progression": [
                    "introduction_to_islam",
                    "basic_arabic_letters",
                    "simple_quran_words", 
                    "prayer_fundamentals",
                    "daily_islamic_practices"
                ],
                "avoid_topics": ["advanced_theology", "comparative_religion", "complex_tafseer"]
            },
            LearningLevel.INTERMEDIATE: {
                "focus_areas": ["quran_understanding", "hadith_basics", "islamic_history"],
                "recommended_scholars": [ScholarName.DR_ZAKIR_NAIK, ScholarName.DR_BILAL_PHILIPS, ScholarName.ABDUR_RAHEEM_GREEN],
                "content_progression": [
                    "surah_meanings",
                    "hadith_introduction",
                    "prophet_biography",
                    "islamic_civilization",
                    "contemporary_issues"
                ],
                "avoid_topics": ["deep_philosophy", "advanced_jurisprudence"]
            },
            LearningLevel.ADVANCED: {
                "focus_areas": ["deep_tafseer", "comparative_religion", "islamic_philosophy"],
                "recommended_scholars": [ScholarName.DR_ISRAR_AHMAD, ScholarName.DR_ZAKIR_NAIK, ScholarName.SHEIKH_AHMED_DEEDAT],
                "content_progression": [
                    "comprehensive_tafseer",
                    "interfaith_dialogue",
                    "islamic_sciences",
                    "scholarly_debates",
                    "research_methodology"
                ],
                "avoid_topics": ["very_basic_concepts"]
            }
        }
    
    async def get_integrated_guidance_with_videos(
        self, 
        user_id: str, 
        context: GuidanceContext,
        current_activity: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> IntegratedRecommendation:
        """
        🌟 Get comprehensive guidance combining AI Ustaz wisdom with Peace TV recommendations
        """
        try:
            # Get user's current state and preferences
            user_profile = await self._get_enhanced_user_profile(user_id)
            learning_level = self._determine_learning_level(user_profile)
            
            # Get AI Ustaz guidance
            ustaz_guidance = await ai_ustaz_assistant.get_contextual_guidance(
                user_id=user_id,
                context=context,
                user_data=user_profile,
                current_activity=current_activity
            )
            
            # Get contextual Peace TV recommendations
            contextual_videos = await self._get_contextual_peace_tv_recommendations(
                context=context,
                learning_level=learning_level,
                user_profile=user_profile,
                current_activity=current_activity
            )
            
            # Generate integrated learning path
            learning_path = self._generate_integrated_learning_path(
                context, learning_level, contextual_videos
            )
            
            # Create comprehensive next actions
            next_actions = self._generate_comprehensive_next_actions(
                ustaz_guidance, contextual_videos, context, learning_level
            )
            
            # Get context-specific duas
            duas_for_context = self._get_contextual_duas(context, ustaz_guidance)
            
            # Calculate estimated study time
            estimated_time = self._calculate_integrated_study_time(contextual_videos, context)
            
            # Generate Islamic benefits description
            islamic_benefits = self._generate_islamic_benefits(context, learning_level)
            
            return IntegratedRecommendation(
                ustaz_guidance={
                    "persona": ustaz_guidance.persona,
                    "main_message": ustaz_guidance.main_message,
                    "practical_advice": ustaz_guidance.practical_advice,
                    "encouragement": ustaz_guidance.encouragement,
                    "next_steps": ustaz_guidance.next_steps
                },
                peace_tv_videos=contextual_videos,
                quranic_reference=ustaz_guidance.quranic_reference,
                learning_path=learning_path,
                next_actions=next_actions,
                duas_for_context=duas_for_context,
                estimated_study_time=estimated_time,
                islamic_benefits=islamic_benefits
            )
            
        except Exception as e:
            logger.error(f"Error generating integrated guidance: {e}")
            return await self._get_fallback_integrated_guidance(context)
    
    async def get_scholar_specific_guidance(
        self, 
        user_id: str,
        preferred_scholar: ScholarName,
        learning_context: Optional[str] = None
    ) -> ScholarGuidanceMatch:
        """
        👨‍🏫 Get guidance specifically tailored to a scholar's expertise and teaching style
        """
        try:
            user_profile = await self._get_enhanced_user_profile(user_id)
            learning_level = self._determine_learning_level(user_profile)
            
            scholar_info = self.scholar_expertise_detailed[preferred_scholar]
            
            # Calculate relevance score
            relevance_score = self._calculate_scholar_relevance(
                scholar_info, learning_level, user_profile, learning_context
            )
            
            # Generate why this scholar is recommended
            why_recommended = self._generate_scholar_recommendation_reason(
                preferred_scholar, scholar_info, learning_level, learning_context
            )
            
            # Get best videos from this scholar
            best_videos = await peace_tv_integration.get_scholar_content(
                scholar=preferred_scholar,
                language=PeaceTVLanguage.ENGLISH,
                limit=5
            )
            
            # Define learning outcomes
            learning_outcomes = self._generate_scholar_learning_outcomes(
                scholar_info, learning_level, learning_context
            )
            
            return ScholarGuidanceMatch(
                scholar=preferred_scholar,
                relevance_score=relevance_score,
                why_recommended=why_recommended,
                best_videos=best_videos,
                learning_outcomes=learning_outcomes,
                suitable_for_level=learning_level
            )
            
        except Exception as e:
            logger.error(f"Error generating scholar guidance: {e}")
            return await self._get_fallback_scholar_guidance(preferred_scholar)
    
    async def get_progress_based_content_recommendations(
        self, 
        user_id: str,
        target_skill: Optional[str] = None
    ) -> ProgressBasedContent:
        """
        📈 Get content recommendations based on user's current progress and learning trajectory
        """
        try:
            user_profile = await self._get_enhanced_user_profile(user_id)
            current_level = self._determine_learning_level(user_profile)
            
            # Get level-specific content mapping
            level_mapping = self.progress_content_mapping[current_level]
            
            # Get recommended videos for current level
            recommended_videos = await self._get_level_appropriate_videos(
                current_level, level_mapping, target_skill
            )
            
            # Determine skill focus areas
            skill_focus_areas = self._determine_skill_focus_areas(
                user_profile, current_level, target_skill
            )
            
            # Calculate next milestone
            next_milestone = self._calculate_next_milestone(user_profile, current_level)
            
            # Estimate completion time
            estimated_time = self._estimate_level_completion_time(
                current_level, user_profile, recommended_videos
            )
            
            # Define prerequisite knowledge
            prerequisite_knowledge = self._get_prerequisite_knowledge(current_level, target_skill)
            
            return ProgressBasedContent(
                current_level=current_level,
                recommended_videos=recommended_videos,
                skill_focus_areas=skill_focus_areas,
                next_milestone=next_milestone,
                estimated_completion_time=estimated_time,
                prerequisite_knowledge=prerequisite_knowledge
            )
            
        except Exception as e:
            logger.error(f"Error generating progress-based content: {e}")
            return await self._get_fallback_progress_content()
    
    async def get_smart_daily_guidance(
        self, 
        user_id: str,
        time_of_day: str = "morning",
        available_time_minutes: int = 30
    ) -> IntegratedRecommendation:
        """
        🌅 Get smart daily guidance that adapts to user's time and preferences
        """
        try:
            user_profile = await self._get_enhanced_user_profile(user_id)
            
            # Determine best context for current time
            optimal_context = self._determine_optimal_daily_context(
                time_of_day, available_time_minutes, user_profile
            )
            
            # Get integrated guidance for the optimal context
            daily_guidance = await self.get_integrated_guidance_with_videos(
                user_id=user_id,
                context=optimal_context,
                current_activity="daily_study_session",
                user_preferences={
                    "time_of_day": time_of_day,
                    "available_time": available_time_minutes
                }
            )
            
            # Customize for daily routine
            daily_guidance.learning_path = self._customize_for_daily_routine(
                daily_guidance.learning_path, time_of_day, available_time_minutes
            )
            
            return daily_guidance
            
        except Exception as e:
            logger.error(f"Error generating smart daily guidance: {e}")
            return await self._get_fallback_daily_guidance()
    
    # Helper methods for comprehensive functionality
    
    async def _get_enhanced_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get enhanced user profile with learning analytics"""
        try:
            # Get basic user data
            user = await self.db.users.find_one({"_id": user_id}) if self.db else {}
            user_progress = await self.db.user_progress.find({"user_id": user_id}).to_list(100) if self.db else []
            
            # Calculate enhanced metrics
            total_lessons = user.get("total_lessons_completed", 0)
            words_learned = len([p for p in user_progress if p.get("mastery_level", 0) >= 50])
            current_streak = user.get("current_streak", 0)
            average_score = sum([p.get("mastery_level", 0) for p in user_progress]) / len(user_progress) if user_progress else 0
            
            return {
                "user_id": user_id,
                "total_lessons_completed": total_lessons,
                "words_learned": words_learned,
                "current_streak": current_streak,
                "average_score": average_score,
                "learning_style": user.get("learning_style", "visual"),
                "preferred_language": user.get("preferred_language", "english"),
                "gender": user.get("gender", "not_specified"),
                "time_zone": user.get("time_zone", "UTC"),
                "study_goals": user.get("study_goals", []),
                "difficulty_preference": user.get("difficulty_preference", "moderate")
            }
        except Exception as e:
            logger.error(f"Error getting enhanced user profile: {e}")
            return {"user_id": user_id, "total_lessons_completed": 0, "words_learned": 0}
    
    def _determine_learning_level(self, user_profile: Dict[str, Any]) -> LearningLevel:
        """Determine user's learning level based on comprehensive metrics"""
        lessons_completed = user_profile.get("total_lessons_completed", 0)
        words_learned = user_profile.get("words_learned", 0)
        average_score = user_profile.get("average_score", 0)
        current_streak = user_profile.get("current_streak", 0)
        
        # Calculate comprehensive learning score
        learning_score = (
            lessons_completed * 10 +
            words_learned * 2 +
            average_score * 0.5 +
            min(current_streak, 30) * 1
        )
        
        if learning_score >= 500:
            return LearningLevel.ADVANCED
        elif learning_score >= 200:
            return LearningLevel.INTERMEDIATE
        else:
            return LearningLevel.BEGINNER
    
    async def _get_contextual_peace_tv_recommendations(
        self,
        context: GuidanceContext,
        learning_level: LearningLevel,
        user_profile: Dict[str, Any],
        current_activity: Optional[str] = None
    ) -> List[PeaceTVVideo]:
        """Get Peace TV recommendations based on current context and user level"""
        try:
            # Get context matching patterns
            context_pattern = self.context_video_matching.get(context, {})
            
            recommended_scholars = context_pattern.get("recommended_scholars", [])
            content_types = context_pattern.get("content_types", [])
            
            # Filter scholars by learning level
            level_appropriate_scholars = []
            for scholar in recommended_scholars:
                scholar_info = self.scholar_expertise_detailed.get(scholar, {})
                if learning_level in scholar_info.get("best_for_levels", []):
                    level_appropriate_scholars.append(scholar)
            
            if not level_appropriate_scholars:
                level_appropriate_scholars = recommended_scholars[:2]  # Fallback
            
            # Get videos from Peace TV integration
            all_recommendations = []
            
            for scholar in level_appropriate_scholars[:2]:  # Limit to top 2 scholars
                try:
                    scholar_videos = await peace_tv_integration.get_scholar_content(
                        scholar=scholar,
                        language=PeaceTVLanguage.ENGLISH,
                        limit=3
                    )
                    all_recommendations.extend(scholar_videos)
                except Exception as e:
                    logger.error(f"Error getting videos for {scholar}: {e}")
                    continue
            
            # Also get contextual recommendations from Peace TV
            try:
                contextual_recs = await peace_tv_integration.get_contextual_recommendations(
                    user_id=user_profile["user_id"],
                    current_word=None,
                    lesson_context=current_activity,
                    language_preference=PeaceTVLanguage.ENGLISH,
                    limit=3
                )
                
                for rec in contextual_recs:
                    all_recommendations.append(rec.video)
                    
            except Exception as e:
                logger.error(f"Error getting contextual Peace TV recommendations: {e}")
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_recommendations = []
            for video in all_recommendations:
                if video.id not in seen_ids:
                    seen_ids.add(video.id)
                    unique_recommendations.append(video)
                    if len(unique_recommendations) >= 5:
                        break
            
            return unique_recommendations
            
        except Exception as e:
            logger.error(f"Error getting contextual Peace TV recommendations: {e}")
            return []
    
    def _generate_integrated_learning_path(
        self,
        context: GuidanceContext,
        learning_level: LearningLevel,
        videos: List[PeaceTVVideo]
    ) -> List[str]:
        """Generate a step-by-step integrated learning path"""
        
        base_paths = {
            GuidanceContext.ONBOARDING: [
                "🤲 Start with dua for seeking knowledge",
                "📖 Read AI Ustaz guidance with Quranic verse",
                "📺 Watch recommended Peace TV introduction video",
                "📝 Practice first Quranic words",
                "🎯 Set daily learning goals"
            ],
            GuidanceContext.LESSON_START: [
                "🤲 Recite 'Rabbi zidni ilma' (My Lord, increase me in knowledge)",
                "📖 Review AI Ustaz pre-lesson guidance",
                "🎥 Watch relevant Arabic grammar video (5-10 min)",
                "📚 Begin your lesson with focus and intention",
                "✍️ Take notes on new vocabulary"
            ],
            GuidanceContext.LESSON_COMPLETE: [
                "🤲 Say 'Alhamdulillahi rabbil alameen'",
                "📖 Read completion guidance from AI Ustaz",
                "🎬 Watch deeper explanation video (15-30 min)",
                "📝 Review and practice learned words",
                "👥 Share knowledge with others"
            ],
            GuidanceContext.PRAYER_TIME: [
                "⏰ Stop current learning activity",
                "🧼 Perform wudu with mindfulness",
                "🕌 Pray with focus and gratitude",
                "📺 Optional: Short post-prayer reminder video (5 min)",
                "📚 Return to studies with refreshed heart"
            ]
        }
        
        base_path = base_paths.get(context, [
            "📖 Read AI Ustaz guidance",
            "📺 Watch recommended videos",
            "📚 Apply learning practically",
            "🤲 Make dua for continued guidance"
        ])
        
        # Customize based on available videos
        if videos:
            video_steps = []
            for i, video in enumerate(videos[:3]):
                duration = f"({video.duration_minutes} min)"
                video_steps.append(f"🎥 Video {i+1}: {video.title} {duration}")
            
            # Insert video steps into appropriate positions
            if len(base_path) >= 3:
                base_path[2:3] = video_steps
            else:
                base_path.extend(video_steps)
        
        return base_path
    
    def _generate_comprehensive_next_actions(
        self,
        ustaz_guidance,
        videos: List[PeaceTVVideo],
        context: GuidanceContext,
        learning_level: LearningLevel
    ) -> List[str]:
        """Generate comprehensive next actions combining all systems"""
        
        actions = []
        
        # Add Ustaz guidance next steps
        actions.extend(ustaz_guidance.next_steps)
        
        # Add video-specific actions
        if videos:
            actions.append(f"🎬 Watch {len(videos)} recommended Peace TV videos")
            actions.append("📝 Take notes on key points from videos")
            actions.append("🤔 Reflect on how videos relate to your current lesson")
        
        # Add context-specific actions
        context_actions = {
            GuidanceContext.ONBOARDING: [
                "⚙️ Complete your profile setup",
                "🎯 Set daily learning reminders",
                "📱 Explore all app features"
            ],
            GuidanceContext.LESSON_START: [
                "🎧 Listen to proper pronunciation",
                "✍️ Practice writing Arabic letters",
                "🔄 Review previous lesson if needed"
            ],
            GuidanceContext.LESSON_COMPLETE: [
                "📊 Check your progress statistics",
                "🏆 View any unlocked achievements",
                "📅 Plan your next study session"
            ],
            GuidanceContext.PRAYER_TIME: [
                "📍 Use Qibla compass if needed",
                "📖 Read prayer time information",
                "⏰ Set reminder for next prayer"
            ]
        }
        
        actions.extend(context_actions.get(context, []))
        
        # Add level-specific actions
        if learning_level == LearningLevel.BEGINNER:
            actions.append("🐌 Take your time - quality over speed")
            actions.append("🔁 Review basics regularly")
        elif learning_level == LearningLevel.ADVANCED:
            actions.append("🔍 Explore deeper scholarly content")
            actions.append("📚 Consider teaching others what you've learned")
        
        return actions[:8]  # Limit to 8 actions to avoid overwhelming
    
    def _get_contextual_duas(self, context: GuidanceContext, ustaz_guidance) -> str:
        """Get specific duas for different contexts"""
        
        contextual_duas = {
            GuidanceContext.ONBOARDING: "رَبِّ اشْرَحْ لِي صَدْرِي وَيَسِّرْ لِي أَمْرِي (Rabbi ishrah li sadri wa yassir li amri) - My Lord, expand for me my breast and ease for me my task.",
            GuidanceContext.LESSON_START: "رَّبِّ زِدْنِي عِلْمًا (Rabbi zidni ilma) - My Lord, increase me in knowledge.",
            GuidanceContext.LESSON_COMPLETE: "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ (Alhamdulillahi rabbil alameen) - All praise is due to Allah, Lord of all the worlds.",
            GuidanceContext.PRAYER_TIME: "رَبَّنَا تَقَبَّلْ مِنَّا إِنَّكَ أَنْتَ السَّمِيعُ الْعَلِيمُ (Rabbana taqabbal minna) - Our Lord, accept from us. You are the Hearing, the Knowing.",
            GuidanceContext.ACHIEVEMENT_UNLOCK: "اللَّهُمَّ بَارِكْ لَنَا فِيمَا رَزَقْتَنَا (Allahumma barik lana feema razaqtana) - O Allah, bless for us what You have provided us.",
            GuidanceContext.DIFFICULTY_FACING: "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ (Hasbunallahu wa ni'mal wakeel) - Allah is sufficient for us, and He is the best Disposer of affairs."
        }
        
        return (ustaz_guidance.duas_recommendation or 
                contextual_duas.get(context, 
                "اللَّهُمَّ انْفَعْنِي بِمَا عَلَّمْتَنِي (Allahumma anfa'ni bima allamtani) - O Allah, benefit me with what You have taught me."))
    
    def _calculate_integrated_study_time(self, videos: List[PeaceTVVideo], context: GuidanceContext) -> int:
        """Calculate total estimated study time including videos and reflection"""
        
        # Base time for reading guidance and reflection
        base_time = {
            GuidanceContext.ONBOARDING: 15,  # minutes
            GuidanceContext.LESSON_START: 10,
            GuidanceContext.LESSON_COMPLETE: 10,
            GuidanceContext.PRAYER_TIME: 5,
            GuidanceContext.ACHIEVEMENT_UNLOCK: 8,
            GuidanceContext.DIFFICULTY_FACING: 12
        }.get(context, 10)
        
        # Add video time
        video_time = sum(video.duration_minutes for video in videos)
        
        # Add reflection and practice time (20% of video time)
        reflection_time = int(video_time * 0.2)
        
        return base_time + video_time + reflection_time
    
    def _generate_islamic_benefits(self, context: GuidanceContext, learning_level: LearningLevel) -> List[str]:
        """Generate Islamic benefits description for the learning activity"""
        
        base_benefits = [
            "🌟 Increased connection with Allah through His words",
            "📈 Spiritual growth and Islamic knowledge expansion", 
            "🤲 Reward for every letter of Quran learned (10 hasanat per letter)",
            "💎 Building foundation for understanding daily prayers",
            "🕊️ Inner peace through engaging with divine guidance"
        ]
        
        context_benefits = {
            GuidanceContext.ONBOARDING: [
                "🌱 Starting a blessed journey of Islamic learning",
                "🎯 Setting strong foundation for lifelong Quranic study"
            ],
            GuidanceContext.LESSON_START: [
                "🧠 Preparing mind and heart for divine knowledge",
                "✨ Seeking Allah's guidance before learning"
            ],
            GuidanceContext.LESSON_COMPLETE: [
                "🏆 Completing righteous deed of learning Quran",
                "📚 Adding to your treasure of Islamic knowledge"
            ],
            GuidanceContext.PRAYER_TIME: [
                "🕌 Fulfilling most important obligation to Allah",
                "💆‍♂️ Refreshing soul for continued learning"
            ]
        }
        
        level_benefits = {
            LearningLevel.BEGINNER: [
                "🌟 Every small step is recorded as a good deed",
                "🎯 Building habits that will benefit you forever"
            ],
            LearningLevel.INTERMEDIATE: [
                "📖 Deepening understanding of Allah's message",
                "🎓 Developing scholarly mindset in Islamic studies"
            ],
            LearningLevel.ADVANCED: [
                "👨‍🏫 Becoming qualified to teach others",
                "🔍 Exploring depths of divine wisdom"
            ]
        }
        
        all_benefits = base_benefits[:3]  # Take first 3 base benefits
        all_benefits.extend(context_benefits.get(context, [])[:2])  # Add 2 context benefits
        all_benefits.extend(level_benefits.get(learning_level, [])[:2])  # Add 2 level benefits
        
        return all_benefits[:6]  # Limit to 6 total benefits
    
    # Additional helper methods for fallback scenarios
    
    async def _get_fallback_integrated_guidance(self, context: GuidanceContext) -> IntegratedRecommendation:
        """Provide fallback guidance when main system fails"""
        fallback_quranic_ref = QuranicReference(
            surah_number=2,
            surah_name_arabic="البقرة",
            surah_name_english="Al-Baqarah",
            ayat_number=31,
            arabic_text="وَعَلَّمَ آدَمَ الْأَسْمَاءَ كُلَّهَا",
            english_translation="And He taught Adam the names - all of them.",
            context_relevance="Learning is a divine gift from Allah.",
            scholarly_note="Knowledge is the foundation of human excellence."
        )
        
        return IntegratedRecommendation(
            ustaz_guidance={
                "persona": "ustaz",
                "main_message": "SubhanAllah! Continue your blessed journey of learning Allah's words.",
                "practical_advice": "Take your time, be consistent, and always seek Allah's guidance.",
                "encouragement": "Every effort you make is seen and rewarded by Allah.",
                "next_steps": ["Continue with your current lesson", "Make dua for guidance"]
            },
            peace_tv_videos=[],
            quranic_reference=fallback_quranic_ref,
            learning_path=["📖 Read guidance", "📚 Continue learning", "🤲 Make dua"],
            next_actions=["Continue your studies", "Seek Allah's guidance"],
            duas_for_context="رَّبِّ زِدْنِي عِلْمًا - My Lord, increase me in knowledge.",
            estimated_study_time=15,
            islamic_benefits=["Spiritual growth", "Divine reward", "Knowledge increase"]
        )

# Global instance
integrated_guidance_system = RevolutionaryIntegratedGuidanceSystem(None)

async def initialize_integrated_guidance_system(db):
    """Initialize Integrated Guidance System with database"""
    global integrated_guidance_system
    integrated_guidance_system = RevolutionaryIntegratedGuidanceSystem(db)
    logger.info("🌟 Revolutionary Integrated Guidance System initialized successfully!")
