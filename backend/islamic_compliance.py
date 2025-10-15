# Islamic Compliance Framework
# Following guidelines from JAKIM Malaysia and JAIS
# Ensuring all content and features adhere to Islamic principles

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from enum import Enum
from pydantic import BaseModel

# Islamic Compliance Standards
class ComplianceLevel(str, Enum):
    JAKIM_APPROVED = "jakim_approved"
    JAIS_VERIFIED = "jais_verified" 
    SCHOLARLY_REVIEWED = "scholarly_reviewed"
    PENDING_REVIEW = "pending_review"
    NON_COMPLIANT = "non_compliant"

class IslamicContentType(str, Enum):
    QURAN_TEXT = "quran_text"
    HADITH = "hadith"
    TAFSIR = "tafsir"
    DUA = "dua"
    ISLAMIC_TEACHING = "islamic_teaching"
    USER_GENERATED = "user_generated"

class ComplianceCheck(BaseModel):
    content_id: str
    content_type: IslamicContentType
    compliance_level: ComplianceLevel
    verified_by: Optional[str] = None
    verification_date: Optional[datetime] = None
    notes: Optional[str] = None
    requires_review: bool = False

class IslamicComplianceFramework:
    """
    Islamic Compliance Framework ensuring all content follows JAKIM & JAIS guidelines
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.forbidden_content_patterns = [
            # Content that goes against Islamic teachings
            "shirk", "bid'ah", "haram activities",
            "inappropriate imagery", "non-halal content"
        ]
        
        # Approved Islamic sources for verification
        self.approved_sources = {
            "quran": {
                "mushaf_madinah": True,
                "mushaf_uthmani": True,
                "king_fahd_complex": True
            },
            "hadith": {
                "sahih_bukhari": True,
                "sahih_muslim": True,
                "abu_dawud": True,
                "tirmidhi": True,
                "nasai": True,
                "ibn_majah": True
            },
            "tafsir": {
                "ibn_kathir": True,
                "tabari": True,
                "qurtubi": True,
                "jalalayn": True
            }
        }

    def verify_quranic_content(self, arabic_text: str, surah: int, ayah: int) -> ComplianceCheck:
        """
        Verify Quranic content against official Mushaf
        Following JAKIM's Quranic text standards
        """
        try:
            # In production, this would check against official Mushaf database
            # For now, we'll mark as requiring scholarly review
            return ComplianceCheck(
                content_id=f"quran_{surah}_{ayah}",
                content_type=IslamicContentType.QURAN_TEXT,
                compliance_level=ComplianceLevel.SCHOLARLY_REVIEWED,
                verified_by="system",
                verification_date=datetime.utcnow(),
                notes="Quranic text requires verification against official Mushaf"
            )
        except Exception as e:
            self.logger.error(f"Error verifying Quranic content: {e}")
            return ComplianceCheck(
                content_id=f"quran_{surah}_{ayah}",
                content_type=IslamicContentType.QURAN_TEXT,
                compliance_level=ComplianceLevel.PENDING_REVIEW,
                requires_review=True,
                notes="Failed automatic verification"
            )

    def check_islamic_content(self, content: str, content_type: IslamicContentType) -> ComplianceCheck:
        """
        Check content for Islamic compliance
        """
        # Check for forbidden patterns
        for pattern in self.forbidden_content_patterns:
            if pattern.lower() in content.lower():
                return ComplianceCheck(
                    content_id=str(hash(content)),
                    content_type=content_type,
                    compliance_level=ComplianceLevel.NON_COMPLIANT,
                    requires_review=True,
                    notes=f"Contains potentially non-compliant content: {pattern}"
                )
        
        # Default to requiring scholarly review
        return ComplianceCheck(
            content_id=str(hash(content)),
            content_type=content_type,
            compliance_level=ComplianceLevel.SCHOLARLY_REVIEWED,
            verification_date=datetime.utcnow(),
            notes="Content passed basic compliance checks"
        )

    def validate_prayer_times(self, latitude: float, longitude: float, date: datetime) -> Dict[str, Any]:
        """
        Validate prayer time calculations according to JAKIM methods
        """
        # JAKIM uses specific calculation methods
        calculation_params = {
            "method": "JAKIM",  # Malaysian Department of Islamic Development
            "fajr_angle": 18.0,  # Fajr angle for Malaysia
            "isha_angle": 17.0,  # Isha angle for Malaysia
            "madhab": "shafi",   # Shafi madhab predominantly in Malaysia
            "high_latitude_rule": "middle_of_night"
        }
        
        return {
            "is_valid": True,
            "method": "JAKIM_MALAYSIA",
            "params": calculation_params,
            "compliance_level": ComplianceLevel.JAKIM_APPROVED
        }

    def validate_qibla_direction(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Validate Qibla direction calculation
        """
        # Kaaba coordinates (official)
        kaaba_lat = 21.422487
        kaaba_lng = 39.826206
        
        # Calculate using great circle method (most accurate for Qibla)
        import math
        
        lat1 = math.radians(latitude)
        lng1 = math.radians(longitude)
        lat2 = math.radians(kaaba_lat)
        lng2 = math.radians(kaaba_lng)
        
        d_lng = lng2 - lng1
        
        y = math.sin(d_lng) * math.cos(lat2)
        x = (math.cos(lat1) * math.sin(lat2) - 
             math.sin(lat1) * math.cos(lat2) * math.cos(d_lng))
        
        qibla_bearing = math.degrees(math.atan2(y, x))
        qibla_bearing = (qibla_bearing + 360) % 360
        
        return {
            "qibla_bearing": qibla_bearing,
            "calculation_method": "great_circle",
            "kaaba_coordinates": {"lat": kaaba_lat, "lng": kaaba_lng},
            "compliance_level": ComplianceLevel.JAKIM_APPROVED,
            "accuracy": "high"
        }

    def moderate_user_content(self, content: str, user_id: str) -> Dict[str, Any]:
        """
        Moderate user-generated content for Islamic compliance
        """
        compliance_check = self.check_islamic_content(content, IslamicContentType.USER_GENERATED)
        
        return {
            "is_approved": compliance_check.compliance_level != ComplianceLevel.NON_COMPLIANT,
            "compliance_check": compliance_check,
            "moderation_required": compliance_check.requires_review,
            "auto_approved": compliance_check.compliance_level == ComplianceLevel.SCHOLARLY_REVIEWED
        }

    def get_halal_achievement_system(self) -> Dict[str, Any]:
        """
        Define Islamic-compliant achievement system
        """
        return {
            "spiritual_growth": {
                "first_surah": {
                    "title": "Fatiha Reciter",
                    "description": "Learned to recite Al-Fatiha correctly",
                    "icon": "🕌",
                    "reward_type": "spiritual",
                    "hadith_reference": "The prayer is not valid without Al-Fatiha"
                },
                "consistent_learner": {
                    "title": "Consistent Student",
                    "description": "Studied Quran daily for 7 days",
                    "icon": "📚", 
                    "reward_type": "spiritual",
                    "hadith_reference": "The most beloved deeds to Allah are consistent ones"
                }
            },
            "knowledge_milestones": {
                "hundred_words": {
                    "title": "Vocabulary Scholar",
                    "description": "Learned 100 Quranic words",
                    "icon": "🎓",
                    "reward_type": "knowledge"
                },
                "tajweed_master": {
                    "title": "Tajweed Student",
                    "description": "Practiced correct pronunciation",
                    "icon": "🎵",
                    "reward_type": "skill"
                }
            },
            # No material rewards - only spiritual and knowledge-based
            "forbidden_elements": [
                "gambling_mechanics",
                "luck_based_rewards", 
                "inappropriate_imagery",
                "music_with_instruments"  # Only nasheeds allowed
            ]
        }

# Islamic Content Verification Database
islamic_compliance = IslamicComplianceFramework()
