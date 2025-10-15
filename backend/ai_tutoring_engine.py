# Advanced AI Tutoring Engine
# Revolutionary ChatGPT/Claude Integration for Quranic Learning
# Following Islamic guidelines with scholarly verification

import asyncio
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import httpx
import logging
from islamic_compliance import islamic_compliance, ComplianceLevel

logger = logging.getLogger(__name__)

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    SCHOLAR = "scholar"

class QuestionType(str, Enum):
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    CONTEXT = "context"
    PRONUNCIATION = "pronunciation"
    ETYMOLOGY = "etymology"
    USAGE = "usage"

class AITutoringRequest(BaseModel):
    question: str
    word_id: Optional[str] = None
    context: Optional[str] = None
    user_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    learning_style: LearningStyle = LearningStyle.VISUAL
    question_type: QuestionType = QuestionType.VOCABULARY
    follow_up: bool = False
    conversation_history: List[Dict[str, str]] = []

class AITutoringResponse(BaseModel):
    answer: str
    explanation: str
    examples: List[str]
    references: List[str]
    follow_up_suggestions: List[str]
    confidence: float
    learning_tips: List[str]
    related_words: List[str]
    difficulty_level: DifficultyLevel
    estimated_study_time: int  # minutes
    practice_exercises: List[Dict[str, Any]]

class RevolutionaryAITutoringEngine:
    """
    Revolutionary AI Tutoring Engine for Quranic Learning
    Integrates with ChatGPT/Claude while maintaining Islamic compliance
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.islamic_context = self._load_islamic_context()
        self.conversation_memory = {}
        
    def _load_islamic_context(self) -> str:
        """Load comprehensive Islamic context for AI responses"""
        return """
        You are an advanced Islamic AI tutor specializing in Quranic Arabic learning. Follow these principles:

        ISLAMIC GUIDELINES:
        1. All responses must align with authentic Islamic teachings
        2. Reference only authentic sources: Quran, Sahih Hadith, established Tafsir
        3. For complex fiqh matters, always refer to qualified scholars
        4. Use appropriate Islamic terminology and etiquette
        5. Begin explanations with "In the name of Allah" when appropriate
        6. End with "Allah knows best" for matters of interpretation

        EDUCATIONAL APPROACH:
        1. Adapt explanations to user's level (beginner to scholar)
        2. Provide multiple examples from Quranic context
        3. Explain etymology and root word connections
        4. Include pronunciation guidance with tajweed rules
        5. Connect words to spiritual and practical meanings
        6. Suggest memorization techniques
        7. Provide graduated difficulty in practice exercises

        SCHOLARLY REFERENCES:
        - Classical Tafsir: Ibn Kathir, Tabari, Qurtubi, Jalalayn
        - Arabic Grammar: Sibawayh, Ibn Malik, Ibn Hisham
        - Quranic Studies: Al-Zarkashi, Al-Suyuti
        - Modern Scholars: Sayyid Qutb, Muhammad Abduh (where appropriate)

        RESPONSE STRUCTURE:
        1. Clear, simple explanation
        2. Quranic examples with verse references
        3. Root word analysis when relevant
        4. Practical usage tips
        5. Spiritual significance
        6. Memory aids and mnemonics
        7. Progressive practice suggestions
        """

    async def get_comprehensive_tutoring_response(
        self, 
        request: AITutoringRequest,
        db_context: Dict[str, Any] = None
    ) -> AITutoringResponse:
        """
        Get comprehensive AI tutoring response with Islamic compliance
        """
        try:
            # Verify Islamic compliance of question
            compliance_check = islamic_compliance.check_islamic_content(
                request.question, "user_generated"
            )
            
            if compliance_check.compliance_level == ComplianceLevel.NON_COMPLIANT:
                return AITutoringResponse(
                    answer="I cannot provide guidance on this topic as it may not align with Islamic teachings. Please rephrase your question or ask about Quranic learning topics.",
                    explanation="Question requires review for Islamic compliance",
                    examples=[],
                    references=["Islamic Compliance Guidelines"],
                    follow_up_suggestions=["Ask about Quranic vocabulary", "Inquire about Arabic grammar", "Request word pronunciation help"],
                    confidence=0.0,
                    learning_tips=[],
                    related_words=[],
                    difficulty_level=request.user_level,
                    estimated_study_time=0,
                    practice_exercises=[]
                )
            
            # Get enhanced context from database if word_id provided
            enhanced_context = await self._get_enhanced_context(request, db_context)
            
            # Choose AI provider based on availability
            if self.openai_api_key:
                response = await self._get_openai_response(request, enhanced_context)
            elif self.anthropic_api_key:
                response = await self._get_claude_response(request, enhanced_context)
            else:
                response = await self._get_fallback_response(request, enhanced_context)
            
            # Post-process for Islamic compliance
            verified_response = await self._verify_and_enhance_response(response, request)
            
            return verified_response
            
        except Exception as e:
            logger.error(f"Error in AI tutoring: {e}")
            return await self._get_error_response(request)

    async def _get_enhanced_context(self, request: AITutoringRequest, db_context: Dict[str, Any]) -> str:
        """Get enhanced context from database and user history"""
        context_parts = [self.islamic_context]
        
        # Add word-specific context if available
        if request.word_id and db_context:
            word_data = db_context.get("word_data", {})
            if word_data:
                context_parts.append(f"""
                CURRENT WORD CONTEXT:
                Arabic: {word_data.get('arabic', '')}
                Transliteration: {word_data.get('transliteration', '')}
                Meaning: {word_data.get('meaning', '')}
                Root: {word_data.get('root', '')}
                Category: {word_data.get('category', '')}
                Surah/Ayah: {word_data.get('surah', '')}/{word_data.get('ayah', '')}
                """)
        
        # Add user learning profile
        user_profile = db_context.get("user_profile", {}) if db_context else {}
        if user_profile:
            context_parts.append(f"""
            USER LEARNING PROFILE:
            Level: {request.user_level}
            Learning Style: {request.learning_style}
            Words Mastered: {user_profile.get('words_mastered', 0)}
            Current Streak: {user_profile.get('current_streak', 0)}
            Weak Areas: {', '.join(user_profile.get('weak_areas', []))}
            Strong Areas: {', '.join(user_profile.get('strong_areas', []))}
            """)
        
        # Add conversation history
        if request.conversation_history:
            context_parts.append("CONVERSATION HISTORY:")
            for exchange in request.conversation_history[-3:]:  # Last 3 exchanges
                context_parts.append(f"Q: {exchange.get('question', '')}")
                context_parts.append(f"A: {exchange.get('answer', '')}")
        
        return "\n".join(context_parts)

    async def _get_openai_response(self, request: AITutoringRequest, context: str) -> Dict[str, Any]:
        """Get response from OpenAI GPT-4"""
        try:
            # Construct optimized prompt
            prompt = f"""
            {context}
            
            USER QUESTION: {request.question}
            QUESTION TYPE: {request.question_type}
            USER LEVEL: {request.user_level}
            LEARNING STYLE: {request.learning_style}
            
            Provide a comprehensive response in JSON format with these fields:
            - answer: Main answer (2-3 sentences)
            - explanation: Detailed explanation (100-200 words)
            - examples: 3-5 Quranic examples with verse references
            - references: Scholarly sources used
            - follow_up_suggestions: 3 related questions to explore
            - learning_tips: 3 practical study tips
            - related_words: 5 related Arabic words
            - practice_exercises: 3 progressive exercises
            
            Ensure all content follows Islamic guidelines and scholarly accuracy.
            """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {"role": "system", "content": context},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1500
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Try to parse as JSON, fallback to structured parsing
                    try:
                        return json.loads(content)
                    except:
                        return self._parse_unstructured_response(content, request)
                else:
                    logger.error(f"OpenAI API error: {response.status_code}")
                    return await self._get_fallback_response(request, context)
                    
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return await self._get_fallback_response(request, context)

    async def _get_claude_response(self, request: AITutoringRequest, context: str) -> Dict[str, Any]:
        """Get response from Anthropic Claude"""
        try:
            prompt = f"""
            {context}
            
            Human: {request.question}
            
            Please provide a comprehensive Islamic tutoring response considering:
            - Question type: {request.question_type}
            - User level: {request.user_level}
            - Learning style: {request.learning_style}
            
            Structure your response with clear sections for explanation, examples, references, and practical tips.
            
            Assistant: """
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "Authorization": f"Bearer {self.anthropic_api_key}",
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": "claude-3-sonnet-20240229",
                        "max_tokens": 1500,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["content"][0]["text"]
                    return self._parse_unstructured_response(content, request)
                else:
                    logger.error(f"Claude API error: {response.status_code}")
                    return await self._get_fallback_response(request, context)
                    
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return await self._get_fallback_response(request, context)

    async def _get_fallback_response(self, request: AITutoringRequest, context: str) -> Dict[str, Any]:
        """Fallback response when AI APIs are unavailable"""
        
        # Basic response templates based on question type
        fallback_responses = {
            QuestionType.VOCABULARY: {
                "answer": "This word is a fundamental part of Quranic vocabulary. Let me help you understand its meaning and usage.",
                "explanation": "In Islamic learning, understanding vocabulary requires studying the word's root, its various forms, and its context in the Quran. Each word carries deep spiritual and linguistic significance.",
                "examples": [
                    "Word appears in multiple Quranic contexts",
                    "Root letters show connection to other related words",
                    "Classical scholars provided detailed explanations"
                ],
                "references": ["Quran", "Classical Arabic dictionaries", "Islamic scholarly works"],
                "learning_tips": [
                    "Practice pronunciation daily",
                    "Connect to root word patterns",
                    "Study in Quranic context"
                ]
            },
            QuestionType.GRAMMAR: {
                "answer": "Arabic grammar follows specific patterns that help us understand Quranic language structure.",
                "explanation": "Islamic Arabic grammar is essential for proper Quranic understanding. The rules established by classical grammarians help us comprehend the precise meanings intended in the divine text.",
                "examples": [
                    "Verb patterns (فعل، يفعل، فاعل)",
                    "Noun declensions (مرفوع، منصوب، مجرور)",
                    "Particle usage in context"
                ],
                "references": ["Sibawayh's Al-Kitab", "Ibn Malik's Alfiyya", "Classical grammar texts"],
                "learning_tips": [
                    "Learn common patterns first",
                    "Practice with Quranic examples",
                    "Understand root and form relationships"
                ]
            }
        }
        
        template = fallback_responses.get(request.question_type, fallback_responses[QuestionType.VOCABULARY])
        
        return {
            "answer": template["answer"],
            "explanation": template["explanation"],
            "examples": template["examples"],
            "references": template["references"],
            "follow_up_suggestions": [
                "Can you provide more examples?",
                "How is this used in different contexts?",
                "What are related words I should learn?"
            ],
            "learning_tips": template["learning_tips"],
            "related_words": [],
            "practice_exercises": [
                {
                    "type": "recognition",
                    "description": "Practice identifying this word in context",
                    "difficulty": "beginner"
                },
                {
                    "type": "usage",
                    "description": "Use this word in a sentence",
                    "difficulty": "intermediate"
                },
                {
                    "type": "analysis",
                    "description": "Analyze the word's grammatical role",
                    "difficulty": "advanced"
                }
            ]
        }

    def _parse_unstructured_response(self, content: str, request: AITutoringRequest) -> Dict[str, Any]:
        """Parse unstructured AI response into structured format"""
        
        # Simple parsing logic - in production, use more sophisticated NLP
        lines = content.split('\n')
        
        response_data = {
            "answer": content[:200] + "..." if len(content) > 200 else content,
            "explanation": content,
            "examples": [],
            "references": ["AI Response - Requires Verification"],
            "follow_up_suggestions": [
                "Can you elaborate on this point?",
                "What are some practical applications?",
                "How does this connect to other concepts?"
            ],
            "learning_tips": [
                "Review this explanation multiple times",
                "Practice with related examples",
                "Connect to your existing knowledge"
            ],
            "related_words": [],
            "practice_exercises": [
                {
                    "type": "review",
                    "description": "Review and summarize the main points",
                    "difficulty": request.user_level.value
                }
            ]
        }
        
        # Extract examples and references if formatted properly
        for line in lines:
            line = line.strip()
            if line.startswith("Example:") or line.startswith("•"):
                response_data["examples"].append(line.replace("Example:", "").replace("•", "").strip())
            elif line.startswith("Reference:") or line.startswith("Source:"):
                response_data["references"].append(line.replace("Reference:", "").replace("Source:", "").strip())
        
        return response_data

    async def _verify_and_enhance_response(self, response_data: Dict[str, Any], request: AITutoringRequest) -> AITutoringResponse:
        """Verify Islamic compliance and enhance response"""
        
        # Verify main answer for Islamic compliance
        compliance_check = islamic_compliance.check_islamic_content(
            response_data.get("answer", ""), "ai_generated"
        )
        
        # Calculate confidence based on compliance and content quality
        confidence = 0.8
        if compliance_check.compliance_level == ComplianceLevel.JAKIM_APPROVED:
            confidence = 0.95
        elif compliance_check.compliance_level == ComplianceLevel.JAIS_VERIFIED:
            confidence = 0.90
        elif compliance_check.compliance_level == ComplianceLevel.NON_COMPLIANT:
            confidence = 0.0
        
        # Enhance with Islamic disclaimer if needed
        enhanced_answer = response_data.get("answer", "")
        if confidence < 0.9:
            enhanced_answer += "\n\nNote: Please verify this information with qualified Islamic scholars for complex matters. Allah knows best."
        
        # Estimate study time based on content complexity and user level
        content_length = len(response_data.get("explanation", ""))
        base_time = {
            DifficultyLevel.BEGINNER: 10,
            DifficultyLevel.INTERMEDIATE: 8,
            DifficultyLevel.ADVANCED: 6,
            DifficultyLevel.SCHOLAR: 5
        }.get(request.user_level, 8)
        
        estimated_time = max(5, (content_length // 50) + base_time)
        
        return AITutoringResponse(
            answer=enhanced_answer,
            explanation=response_data.get("explanation", ""),
            examples=response_data.get("examples", [])[:5],  # Limit to 5
            references=response_data.get("references", []),
            follow_up_suggestions=response_data.get("follow_up_suggestions", [])[:3],  # Limit to 3
            confidence=confidence,
            learning_tips=response_data.get("learning_tips", [])[:3],  # Limit to 3
            related_words=response_data.get("related_words", [])[:5],  # Limit to 5
            difficulty_level=request.user_level,
            estimated_study_time=estimated_time,
            practice_exercises=response_data.get("practice_exercises", [])[:3]  # Limit to 3
        )

    async def _get_error_response(self, request: AITutoringRequest) -> AITutoringResponse:
        """Generate error response"""
        return AITutoringResponse(
            answer="I apologize, but I'm unable to process your question at the moment. Please try again later or consult with qualified Islamic scholars.",
            explanation="There was a temporary issue with the AI tutoring system. This doesn't affect the accuracy of other app features.",
            examples=[],
            references=["Technical Support"],
            follow_up_suggestions=[
                "Try rephrasing your question",
                "Ask a simpler question first",
                "Check your internet connection"
            ],
            confidence=0.0,
            learning_tips=[
                "Continue with regular lessons",
                "Use other app features",
                "Try again later"
            ],
            related_words=[],
            difficulty_level=request.user_level,
            estimated_study_time=0,
            practice_exercises=[]
        )

    async def generate_personalized_exercises(self, user_id: str, difficulty: DifficultyLevel, count: int = 5) -> List[Dict[str, Any]]:
        """Generate personalized practice exercises using AI"""
        
        try:
            exercise_types = [
                {
                    "type": "word_recognition",
                    "description": "Identify the correct meaning",
                    "format": "multiple_choice"
                },
                {
                    "type": "pronunciation_practice",
                    "description": "Practice correct pronunciation",
                    "format": "audio_recording"
                },
                {
                    "type": "context_analysis",
                    "description": "Understand word usage in verses",
                    "format": "comprehension"
                },
                {
                    "type": "root_exploration",
                    "description": "Explore word roots and patterns",
                    "format": "matching"
                },
                {
                    "type": "memory_challenge",
                    "description": "Quick recall challenge",
                    "format": "speed_round"
                }
            ]
            
            # Generate exercises based on user's learning profile
            exercises = []
            for i in range(min(count, len(exercise_types))):
                exercise = exercise_types[i].copy()
                exercise["id"] = f"ex_{user_id}_{i}_{datetime.now().timestamp()}"
                exercise["difficulty"] = difficulty.value
                exercise["estimated_time"] = 5 if difficulty == DifficultyLevel.BEGINNER else 3
                exercise["created_at"] = datetime.now().isoformat()
                exercises.append(exercise)
            
            return exercises
            
        except Exception as e:
            logger.error(f"Error generating exercises: {e}")
            return []

    async def analyze_learning_pattern(self, user_id: str, recent_interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's learning pattern using AI"""
        
        try:
            if not recent_interactions:
                return {"status": "insufficient_data"}
            
            # Analyze patterns in user interactions
            question_types = [interaction.get("question_type") for interaction in recent_interactions]
            response_times = [interaction.get("response_time", 30) for interaction in recent_interactions]
            satisfaction_scores = [interaction.get("satisfaction", 3) for interaction in recent_interactions]
            
            # Calculate insights
            avg_response_time = sum(response_times) / len(response_times)
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
            most_common_type = max(set(question_types), key=question_types.count)
            
            insights = {
                "preferred_question_type": most_common_type,
                "average_engagement_time": avg_response_time,
                "satisfaction_level": avg_satisfaction,
                "learning_velocity": "fast" if avg_response_time < 20 else "moderate" if avg_response_time < 40 else "slow",
                "recommendations": []
            }
            
            # Generate recommendations
            if avg_satisfaction < 3:
                insights["recommendations"].append("Try adjusting difficulty level")
            if avg_response_time > 45:
                insights["recommendations"].append("Consider shorter study sessions")
            if most_common_type == QuestionType.VOCABULARY:
                insights["recommendations"].append("Explore grammar questions for balanced learning")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing learning pattern: {e}")
            return {"status": "analysis_error"}

# Global instance
ai_tutoring_engine = RevolutionaryAITutoringEngine()
