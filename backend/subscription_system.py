"""
💰 Revolutionary Freemium & Premium Subscription System
========================================================

Multi-tier subscription model with premium features,
family plans, and institutional licensing.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    FAMILY = "family"
    INSTITUTIONAL = "institutional"

class FeatureAccess(str, Enum):
    BASIC_LESSONS = "basic_lessons"
    ADVANCED_LESSONS = "advanced_lessons"
    AI_TUTOR_UNLIMITED = "ai_tutor_unlimited"
    SPEECH_RECOGNITION = "speech_recognition"
    OFFLINE_MODE = "offline_mode"
    PEACE_TV_PREMIUM = "peace_tv_premium"
    ADVANCED_ANALYTICS = "advanced_analytics"
    STUDY_GROUPS = "study_groups"

@dataclass
class SubscriptionPlan:
    tier: SubscriptionTier
    price_monthly: float
    price_yearly: float
    features: List[FeatureAccess]
    max_users: int
    ai_queries_per_month: int

class SubscriptionSystem:
    """Revolutionary Freemium Model"""
    
    def __init__(self, db):
        self.db = db
        self.plans = {
            SubscriptionTier.FREE: SubscriptionPlan(
                tier=SubscriptionTier.FREE,
                price_monthly=0.0,
                price_yearly=0.0,
                features=[FeatureAccess.BASIC_LESSONS],
                max_users=1,
                ai_queries_per_month=10
            ),
            SubscriptionTier.PREMIUM: SubscriptionPlan(
                tier=SubscriptionTier.PREMIUM,
                price_monthly=9.99,
                price_yearly=99.99,
                features=[
                    FeatureAccess.BASIC_LESSONS,
                    FeatureAccess.ADVANCED_LESSONS,
                    FeatureAccess.AI_TUTOR_UNLIMITED,
                    FeatureAccess.SPEECH_RECOGNITION,
                    FeatureAccess.OFFLINE_MODE,
                    FeatureAccess.ADVANCED_ANALYTICS
                ],
                max_users=1,
                ai_queries_per_month=-1  # Unlimited
            ),
            SubscriptionTier.FAMILY: SubscriptionPlan(
                tier=SubscriptionTier.FAMILY,
                price_monthly=19.99,
                price_yearly=199.99,
                features=[
                    FeatureAccess.BASIC_LESSONS,
                    FeatureAccess.ADVANCED_LESSONS,
                    FeatureAccess.AI_TUTOR_UNLIMITED,
                    FeatureAccess.SPEECH_RECOGNITION,
                    FeatureAccess.OFFLINE_MODE,
                    FeatureAccess.PEACE_TV_PREMIUM,
                    FeatureAccess.ADVANCED_ANALYTICS,
                    FeatureAccess.STUDY_GROUPS
                ],
                max_users=5,
                ai_queries_per_month=-1
            )
        }
    
    def check_feature_access(self, tier: SubscriptionTier, feature: FeatureAccess) -> bool:
        """Check if subscription tier has access to feature"""
        plan = self.plans.get(tier)
        return plan and feature in plan.features

subscription_system = SubscriptionSystem(None)

async def initialize_subscription_system(db):
    global subscription_system
    subscription_system = SubscriptionSystem(db)
    logger.info("💰 Subscription System initialized!")
