# Intelligent Agent Routing System
import google.generativeai as genai
import json
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import os
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from agents.base_agent import BaseAgent
from config.sahayak_config import SahayakConfig
from sentence_transformers import SentenceTransformer

class AgentType(Enum):
    """Available agent types in Sahayak system"""
    DOUBT_ASSISTANT = "doubt_assistant"
    CONTENT_GENERATION = "content_generation"
    VISION_AGENT = "vision_agent"
    GAME_PLANNER = "game_planner"  # Updated name
    LESSON_PLANNER = "lesson_planner"
    DRAWINGS_AGENT = "drawings_agent"
    MINDMAP_AGENT = "mindmap_agent"
    VIDEO_INTELLIGENCE = "video_intelligence"
    ACCESSIBILITY_AGENT = "accessibility_agent"
    BRAILLE_ASSISTANT = "braille_assistant"
    RAG = "rag"

@dataclass
class RouteIntent:
    """Intent classification result"""
    agent_type: AgentType
    confidence: float
    parameters: Dict
    reasoning: str

class AgentRouter:
    """
    Intelligent routing system that determines which agent should handle a request
    Uses Gemini for intent classification instead of regex patterns
    """
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        self.intent_classifier_prompt = self._build_intent_classifier_prompt()
        
    def _build_intent_classifier_prompt(self) -> str:
        """Build the master prompt for intent classification"""
        return """
You are an intelligent router for an AI teaching assistant system called "Sahayak". 
Your job is to analyze user requests and determine which specialized agent should handle them.

AVAILABLE AGENTS:
1. DOUBT_ASSISTANT: Answers questions, explanations, clarifications
   - Triggers: "why", "what is", "explain", "how does", questions ending with "?"
   - Examples: "Why is sky blue?", "What is photosynthesis?", "Explain gravity"

2. CONTENT_GENERATION: Creates stories, essays, lessons, explanations
   - Triggers: "create", "generate", "write", "make a story", "compose"
   - Examples: "Create a story about farmers", "Write lesson on water cycle"

3. VISION_AGENT: Processes images, extracts text, creates worksheets from images
   - Triggers: "image", "photo", "picture", "textbook page", "extract text from image"
   - Examples: "Extract text from this image", "Create worksheet from textbook page"

4. BRAILLE_ASSISTANT: Converts text and explanations to Braille format
   - Triggers: "in braille", "braille format", "convert to braille", "braille"
   - Examples: "explain photosynthesis in braille", "convert this to braille", "braille format"
   - Note: Takes highest priority when "braille" is mentioned

5. GAME_PLANNER: Creates educational games like Sudoku and Riddles
   - Triggers: "sudoku", "riddles", "game", "puzzle", "play", "show game", "show answer"
   - Examples: "Show game", "Show answer", "Play sudoku", "Play riddles"

6. LESSON_PLANNER: Plans lessons, schedules, curriculum structure
   - Triggers: "lesson plan", "schedule", "curriculum", "plan", "weekly", "daily plan"
   - Examples: "Plan weekly lessons", "Create schedule for grade 5", "Lesson plan for math"

7. DRAWINGS_AGENT: Creates visual aids, diagrams, simple drawings
   - Triggers: "draw", "diagram", "visual", "chart", "illustration", "drawing"
   - Examples: "Draw water cycle", "Create diagram of plant parts", "Visual for math concept"

8. MINDMAP_AGENT: Creates mind maps and concept maps
   - Triggers: "mind map", "concept map", "visual summary", "organize", "structure", "map of"
   - Notes: If the phrase contains both "generate/create" and "mind map", this agent should take priority over CONTENT_GENERATION.

9. VIDEO_INTELLIGENCE: Processes and analyzes video content
   - Triggers: "video", "analyze video", "video summary", "video content"
   - Examples: "Summarize this educational video", "Extract key points from video"

10. ACCESSIBILITY_AGENT: Supports students with disabilities, special needs
    - Triggers: "accessibility", "disability", "special needs", "visual impairment", "hearing impairment"
    - Examples: "Make content accessible for blind students", "Sign language support"

ANALYSIS INSTRUCTIONS:
1. Analyze the user's request carefully
2. Check for Braille-related keywords first (highest priority)
3. Identify other key trigger words and phrases
4. Determine the primary intent
5. Extract relevant parameters (language, grade, subject, etc.)
6. Assign confidence score (0.0 to 1.0)
7. Provide brief reasoning

RESPONSE FORMAT (JSON only):
{
    "agent_type": "agent_name",
    "confidence": 0.95,
    "parameters": {
        "language": "english",
        "grade_level": 5,
        "subject": "science",
        "specific_topic": "water cycle",
        "context": "rural",
        "additional_info": "any other relevant details"
    },
    "reasoning": "Brief explanation of why this agent was chosen"
}

Important: 
- Always respond with valid JSON only
- If unsure between agents, choose the one with highest relevance
- Extract language, grade level, and subject when mentioned
- Default to english/grade 5 if not specified
- If request is too vague, choose DOUBT_ASSISTANT as fallback

Now analyze this request:
"""

    def route_request(self, user_request: str, context: Dict = None) -> RouteIntent:
        """
        Route a user request to the appropriate agent
        
        Args:
            user_request: The user's input text
            context: Additional context (user_type, previous_agent, etc.)
            
        Returns:
            RouteIntent: Classification result with agent type and parameters
        """
        
        # Check for Braille keywords first (highest priority)
        request_lower = user_request.lower()
        braille_keywords = ['braille', 'in braille', 'braille format', 'convert to braille']
        if any(keyword in request_lower for keyword in braille_keywords):
            return RouteIntent(
                agent_type=AgentType.BRAILLE_ASSISTANT,
                confidence=1.0,
                parameters={
                    'language': 'english',
                    'grade_level': 5,
                },
                reasoning="Request contains Braille-related keywords"
            )
            
        # Check if documents are uploaded in context
        if context and 'uploaded_docs' in context and context['uploaded_docs']:
            # If documents are uploaded, route to RAG agent
            return RouteIntent(
                agent_type=AgentType.RAG,
                confidence=1.0,
                parameters={
                    'language': 'english',
                    'grade_level': 5,
                    'context': 'knowledge_base_search',
                    'documents': context['uploaded_docs']
                },
                reasoning="Routing to RAG agent due to document upload context"
            )
            
        # Add context to the request if available
        full_request = user_request
        if context:
            context_str = f"Context: {json.dumps(context)}\n"
            full_request = context_str + user_request
            
        prompt = self.intent_classifier_prompt + f"\nUser Request: {full_request}"
        
        try:
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            
            # Parse JSON response
            result_json = self._extract_json_from_response(response.text)
            result_dict = json.loads(result_json)
            
            # Create RouteIntent object
            intent = RouteIntent(
                agent_type=AgentType(result_dict['agent_type']),
                confidence=result_dict['confidence'],
                parameters=result_dict['parameters'],
                reasoning=result_dict['reasoning']
            )
            
            return intent
            
        except Exception as e:
            # Fallback routing using keyword matching
            return self._fallback_routing(user_request, context)
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON from Gemini response"""
        # Find JSON block in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        else:
            raise ValueError("No valid JSON found in response")
    
    def _fallback_routing(self, user_request: str, context: Dict = None) -> RouteIntent:
        """Fallback routing using simple keyword matching"""
        
        request_lower = user_request.lower()
        
        # Simple keyword-based routing as fallback
        routing_rules = {
            AgentType.VISION_AGENT: ['image', 'photo', 'picture', 'textbook', 'extract text'],
            AgentType.GAME_PLANNER: ['sudoku', 'riddles', 'game', 'puzzle', 'play', 'interactive', 'show game', 'show answer', 'answer'],
            AgentType.LESSON_PLANNER: ['lesson plan', 'schedule', 'curriculum', 'plan', 'weekly'],
            AgentType.DRAWINGS_AGENT: ['draw', 'diagram', 'visual', 'chart', 'illustration'],
            AgentType.MINDMAP_AGENT: ['mind map', 'concept map', 'organize', 'mindmap', 'visual summary'],
            AgentType.CONTENT_GENERATION: ['create', 'generate', 'write', 'story', 'compose'],
            AgentType.VIDEO_INTELLIGENCE: ['video', 'analyze video', 'video summary'],
            AgentType.ACCESSIBILITY_AGENT: ['accessibility', 'disability', 'special needs'],
            AgentType.BRAILLE_ASSISTANT: ['braille', 'in braille', 'convert to braille', 'braille format'],
            AgentType.RAG: [
                'search documents', 'find in documents', 'search knowledge base',
                'look up', 'find information', 'search files', 'context search'
            ]
        }
        
        # Check for matches
        for agent_type, keywords in routing_rules.items():
            if any(keyword in request_lower for keyword in keywords):
                return RouteIntent(
                    agent_type=agent_type,
                    confidence=0.7,
                    parameters={
                        'language': 'english',
                        'grade_level': 5,
                        'context': 'rural'
                    },
                    reasoning=f"Fallback routing based on keyword match"
                )
        
        # Default to doubt assistant
        return RouteIntent(
            agent_type=AgentType.DOUBT_ASSISTANT,
            confidence=0.5,
            parameters={
                'language': 'english',
                'grade_level': 5,
                'context': 'rural'
            },
            reasoning="Default routing - request unclear"
        )
    
    def batch_route_requests(self, requests: List[str]) -> List[RouteIntent]:
        """Route multiple requests at once"""
        return [self.route_request(request) for request in requests]
    
    def get_routing_confidence_threshold(self) -> float:
        """Get minimum confidence threshold for routing"""
        return 0.6
    
    def validate_routing(self, intent: RouteIntent) -> bool:
        """Validate if routing result meets confidence threshold"""
        return intent.confidence >= self.get_routing_confidence_threshold()