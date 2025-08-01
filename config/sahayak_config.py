
import os
import json
from typing import Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    HACKATHON = "hackathon"
    PRODUCTION = "production"

class ModelTier(Enum):
    """Model tier for different usage scenarios"""
    FREE = "free"           # Free tier - Gemini 1.5 Flash
    HACKATHON = "hackathon" # Hackathon tier - All models with credits
    PREMIUM = "premium"     # Premium tier - All models unlimited

@dataclass
class ModelConfig:
    """Configuration for different AI models"""
    name: str
    max_tokens: int
    rate_limit_per_minute: int
    rate_limit_per_day: int
    supports_vision: bool = False
    supports_audio: bool = False
    cost_per_request: float = 0.0

class SahayakConfig:
    """
    Comprehensive configuration system for Sahayak AI Assistant
    Supports different environments and model tiers
    """
    
    # Current environment
    ENVIRONMENT = Environment.DEVELOPMENT
    MODEL_TIER = ModelTier.FREE
    
    # API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'sahayak-ai')
    
    # Model Configurations by Tier
    MODEL_CONFIGS = {
        ModelTier.FREE: {
            'text_model': ModelConfig(
                name="gemini-2.0-flash",
                max_tokens=8192,
                rate_limit_per_minute=15,
                rate_limit_per_day=1500,
                supports_vision=False,
                supports_audio=False
            ),
            'vision_model': ModelConfig(
                name="gemini-2.0-flash",
                max_tokens=8192,
                rate_limit_per_minute=15,
                rate_limit_per_day=1500,
                supports_vision=True,
                supports_audio=False
            ),
            'pro_model': None  # Not available in free tier
        },
        
        ModelTier.HACKATHON: {
            'text_model': ModelConfig(
                name="gemini-1.5-pro",
                max_tokens=32768,
                rate_limit_per_minute=60,
                rate_limit_per_day=10000,
                supports_vision=False,
                supports_audio=False
            ),
            'vision_model': ModelConfig(
                name="gemini-1.5-pro",
                max_tokens=32768,
                rate_limit_per_minute=60,
                rate_limit_per_day=10000,
                supports_vision=True,
                supports_audio=False
            ),
            'pro_model': ModelConfig(
                name="gemini-1.5-pro",
                max_tokens=32768,
                rate_limit_per_minute=60,
                rate_limit_per_day=10000,
                supports_vision=True,
                supports_audio=True
            )
        }
    }
    
    # Supported Languages with their native names
    LANGUAGES = {
        'english': {'name': 'English', 'native': 'English', 'code': 'en'},
        'hindi': {'name': 'Hindi', 'native': 'हिन्दी', 'code': 'hi'},
        'marathi': {'name': 'Marathi', 'native': 'मराठी', 'code': 'mr'},
        'gujarati': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'code': 'gu'},
        'bengali': {'name': 'Bengali', 'native': 'বাংলা', 'code': 'bn'},
        'tamil': {'name': 'Tamil', 'native': 'தமிழ்', 'code': 'ta'},
        'telugu': {'name': 'Telugu', 'native': 'తెలుగు', 'code': 'te'},
        'kannada': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'code': 'kn'},
        'malayalam': {'name': 'Malayalam', 'native': 'മലയാളം', 'code': 'ml'},
        'punjabi': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ', 'code': 'pa'},
        'urdu': {'name': 'Urdu', 'native': 'اردو', 'code': 'ur'}
    }
    
    # Grade Levels and Age Groups
    GRADE_LEVELS = {
        1: {'age_range': '6-7', 'level': 'beginner'},
        2: {'age_range': '7-8', 'level': 'beginner'},
        3: {'age_range': '8-9', 'level': 'elementary'},
        4: {'age_range': '9-10', 'level': 'elementary'},
        5: {'age_range': '10-11', 'level': 'elementary'},
        6: {'age_range': '11-12', 'level': 'middle'},
        7: {'age_range': '12-13', 'level': 'middle'},
        8: {'age_range': '13-14', 'level': 'middle'},
        9: {'age_range': '14-15', 'level': 'secondary'},
        10: {'age_range': '15-16', 'level': 'secondary'},
        11: {'age_range': '16-17', 'level': 'senior'},
        12: {'age_range': '17-18', 'level': 'senior'}
    }

    # Default model
    DEFAULT_MODEL = "gemini-2.0-flash"  # Free tier model
    
    # Subject Categories
    SUBJECTS = {
        'mathematics': {
            'name': 'Mathematics',
            'subcategories': ['arithmetic', 'algebra', 'geometry', 'statistics'],
            'icon': '🔢'
        },
        'science': {
            'name': 'Science',
            'subcategories': ['physics', 'chemistry', 'biology', 'environmental'],
            'icon': '🔬'
        },
        'social_studies': {
            'name': 'Social Studies',
            'subcategories': ['history', 'geography', 'civics', 'economics'],
            'icon': '🌍'
        },
        'languages': {
            'name': 'Languages',
            'subcategories': ['hindi', 'english', 'regional_languages', 'literature'],
            'icon': '📚'
        },
        'arts': {
            'name': 'Arts & Crafts',
            'subcategories': ['drawing', 'music', 'dance', 'crafts'],
            'icon': '🎨'
        },
        'general': {
            'name': 'General Knowledge',
            'subcategories': ['current_affairs', 'general_awareness', 'life_skills'],
            'icon': '💡'
        }
    }
    
    # Context Types for Different School Settings
    CONTEXT_TYPES = {
        'rural': {
            'description': 'Rural school with limited resources',
            'characteristics': ['low_tech', 'multi_grade', 'local_language_focus'],
            'adaptations': ['simple_language', 'local_examples', 'low_bandwidth']
        },
        'urban': {
            'description': 'Urban school with better resources',
            'characteristics': ['higher_tech', 'single_grade', 'english_focus'],
            'adaptations': ['advanced_concepts', 'tech_integration', 'global_examples']
        },
        'semi_urban': {
            'description': 'Semi-urban school with moderate resources',
            'characteristics': ['moderate_tech', 'mixed_grades', 'bilingual'],
            'adaptations': ['balanced_approach', 'regional_examples', 'moderate_complexity']
        }
    }
    
    # Agent-Specific Configuration
    AGENT_CONFIGS = {
        'doubt_assistant': {
            'max_explanation_length': 500,
            'include_examples': True,
            'use_local_context': True,
            'fallback_language': 'english'
        },
        'content_generation': {
            'max_content_length': 1000,
            'include_moral_values': True,
            'cultural_relevance': True,
            'age_appropriate': True
        },
        'vision_agent': {
            'supported_formats': ['jpg', 'jpeg', 'png', 'webp'],
            'max_file_size_mb': 10,
            'ocr_languages': ['hi', 'en', 'mr', 'gu'],
            'worksheet_difficulty_levels': 3
        },
        'audio_agent': {
            'supported_formats': ['mp3', 'wav', 'm4a'],
            'max_duration_seconds': 300,
            'assessment_criteria': ['fluency', 'pronunciation', 'comprehension'],
            'feedback_detail_level': 'detailed'
        },
        'game_planner': {
            'game_types': ['quiz', 'memory', 'puzzle', 'story'],
            'max_questions': 20,
            'difficulty_adaptive': True,
            'multiplayer_support': False
        },
        'lesson_planner': {
            'planning_duration': ['daily', 'weekly', 'monthly'],
            'include_activities': True,
            'resource_suggestions': True,
            'assessment_integration': True
        }
    }
    
    # File Storage Configuration
    STORAGE_CONFIG = {
        'max_file_size_mb': 50,
        'allowed_image_types': ['.jpg', '.jpeg', '.png', '.webp'],
        'allowed_audio_types': ['.mp3', '.wav', '.m4a'],
        'allowed_video_types': ['.mp4', '.avi', '.mov'],
        'temp_file_expiry_hours': 24,
        'max_files_per_user': 100
    }
    
    # Performance and Monitoring
    PERFORMANCE_CONFIG = {
        'max_response_time_seconds': 30,
        'retry_attempts': 3,
        'cache_enabled': True,
        'cache_expiry_minutes': 60,
        'log_level': 'INFO',
        'metrics_collection': True
    }
    
    # Security Configuration
    SECURITY_CONFIG = {
        'max_requests_per_minute': 60,
        'max_requests_per_day': 1000,
        'content_filter_enabled': True,
        'inappropriate_content_detection': True,
        'user_data_encryption': True
    }
    
    @classmethod
    def get_current_model_config(cls, model_type: str = 'text_model') -> ModelConfig:
        """Get current model configuration based on tier"""
        return cls.MODEL_CONFIGS[cls.MODEL_TIER][model_type]
    
    @classmethod
    def set_environment(cls, env: Environment, tier: ModelTier = None):
        """Set environment and optionally model tier"""
        cls.ENVIRONMENT = env
        if tier:
            cls.MODEL_TIER = tier
        
        # Adjust configurations based on environment
        if env == Environment.HACKATHON:
            cls.MODEL_TIER = ModelTier.HACKATHON
            cls.PERFORMANCE_CONFIG['max_response_time_seconds'] = 60
            cls.SECURITY_CONFIG['max_requests_per_minute'] = 120
        elif env == Environment.DEVELOPMENT:
            cls.MODEL_TIER = ModelTier.FREE
            cls.PERFORMANCE_CONFIG['log_level'] = 'DEBUG'
    
    @classmethod
    def get_language_info(cls, language_code: str) -> Dict:
        """Get detailed language information"""
        return cls.LANGUAGES.get(language_code, cls.LANGUAGES['english'])
    
    @classmethod
    def get_grade_info(cls, grade: int) -> Dict:
        """Get grade level information"""
        return cls.GRADE_LEVELS.get(grade, cls.GRADE_LEVELS[5])
    
    @classmethod
    def get_subject_info(cls, subject: str) -> Dict:
        """Get subject information"""
        return cls.SUBJECTS.get(subject, cls.SUBJECTS['general'])
    
    @classmethod
    def get_context_info(cls, context: str) -> Dict:
        """Get context type information"""
        return cls.CONTEXT_TYPES.get(context, cls.CONTEXT_TYPES['rural'])
    
    @classmethod
    def validate_request_parameters(cls, **kwargs) -> Dict:
        """Validate and normalize request parameters"""
        
        # Default values
        defaults = {
            'language': 'english',
            'grade_level': 5,
            'subject': 'general',
            'context': 'rural'
        }
        
        # Merge with defaults
        params = {**defaults, **kwargs}
        
        # Validate language
        if params['language'] not in cls.LANGUAGES:
            params['language'] = 'english'
        
        # Validate grade level
        if params['grade_level'] not in cls.GRADE_LEVELS:
            params['grade_level'] = 5
        
        # Validate subject
        if params['subject'] not in cls.SUBJECTS:
            params['subject'] = 'general'
        
        # Validate context
        if params['context'] not in cls.CONTEXT_TYPES:
            params['context'] = 'rural'
        
        return params
    
    @classmethod
    def get_rate_limits(cls) -> Dict:
        """Get current rate limits based on model tier"""
        model_config = cls.get_current_model_config()
        
        return {
            'requests_per_minute': model_config.rate_limit_per_minute,
            'requests_per_day': model_config.rate_limit_per_day,
            'max_tokens': model_config.max_tokens
        }
    
    @classmethod
    def is_feature_available(cls, feature: str) -> bool:
        """Check if a feature is available in current tier"""
        
        feature_availability = {
            ModelTier.FREE: [
                'basic_text_generation', 'simple_vision', 'basic_routing',
                'doubt_assistance', 'simple_content_generation'
            ],
            ModelTier.HACKATHON: [
                'advanced_text_generation', 'advanced_vision', 'audio_processing',
                'video_intelligence', 'complex_workflows', 'all_agents',
                'advanced_analytics', 'multi_modal_processing'
            ]
        }
        
        return feature in feature_availability.get(cls.MODEL_TIER, [])
    
    @classmethod
    def get_hackathon_config(cls) -> Dict:
        """Get special configuration for hackathon environment"""
        
        if cls.ENVIRONMENT == Environment.HACKATHON:
            return {
                'credits_available': 300,  # USD
                'premium_features_enabled': True,
                'advanced_models_enabled': True,
                'extended_rate_limits': True,
                'demonstration_mode': True,
                'analytics_detailed': True,
                'all_agents_enabled': True
            }
        
        return {}
    
    @classmethod
    def save_config_to_file(cls, filepath: str):
        """Save current configuration to JSON file"""
        
        config_data = {
            'environment': cls.ENVIRONMENT.value,
            'model_tier': cls.MODEL_TIER.value,
            'languages': cls.LANGUAGES,
            'grade_levels': cls.GRADE_LEVELS,
            'subjects': cls.SUBJECTS,
            'context_types': cls.CONTEXT_TYPES,
            'agent_configs': cls.AGENT_CONFIGS,
            'performance_config': cls.PERFORMANCE_CONFIG,
            'security_config': cls.SECURITY_CONFIG
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_config_from_file(cls, filepath: str):
        """Load configuration from JSON file"""
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Update class attributes
            cls.ENVIRONMENT = Environment(config_data.get('environment', 'development'))
            cls.MODEL_TIER = ModelTier(config_data.get('model_tier', 'free'))
            
            # Update other configurations
            if 'agent_configs' in config_data:
                cls.AGENT_CONFIGS.update(config_data['agent_configs'])
            
            if 'performance_config' in config_data:
                cls.PERFORMANCE_CONFIG.update(config_data['performance_config'])

# Environment-specific setup
def setup_development_environment():
    """Setup for development environment"""
    SahayakConfig.set_environment(Environment.DEVELOPMENT, ModelTier.FREE)
    print("🔧 Development environment configured with FREE tier models")

def setup_hackathon_environment():
    """Setup for hackathon environment"""
    SahayakConfig.set_environment(Environment.HACKATHON, ModelTier.HACKATHON)
    print("🏆 Hackathon environment configured with PREMIUM models and $300 credits!")

def setup_testing_environment():
    """Setup for testing environment"""
    SahayakConfig.set_environment(Environment.TESTING, ModelTier.FREE)
    SahayakConfig.PERFORMANCE_CONFIG['log_level'] = 'DEBUG'
    print("🧪 Testing environment configured")