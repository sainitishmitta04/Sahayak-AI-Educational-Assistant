
import os
import time
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from config.sahayak_config import SahayakConfig

from .agent_router import AgentRouter, AgentType, RouteIntent
from .doubt_assistant_agent import DoubtAssistantAgent
from .content_generation_agent import ContentGenerationAgent
from .vision_agent import GeminiVisionAgent
from .lesson_planner_agent import LessonPlannerAgent
from .drawings_agent import DrawingsAgent
from .mindmap_agent import MindMapAgent
from .base_agent import BaseAgent
from .rag_agent import RAGAgent
from .braille_assistant_agent import BrailleAssistantAgent
from .game_planner_agent import GamePlannerAgent

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class AgentResponse:
    success: bool
    data: Any
    agent_name: str
    execution_time: float
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class AgentManager:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.router = AgentRouter()
        self.agents = {}
        self.agent_stats = {}
        self.execution_history = []

        self._initialize_agents()

    def _initialize_agents(self):
        try:
            self.agents = {
                AgentType.DOUBT_ASSISTANT: DoubtAssistantAgent(),
                AgentType.CONTENT_GENERATION: ContentGenerationAgent(),
                AgentType.VISION_AGENT: GeminiVisionAgent(),
                AgentType.LESSON_PLANNER: LessonPlannerAgent(),
                AgentType.DRAWINGS_AGENT: DrawingsAgent(),
                AgentType.MINDMAP_AGENT: MindMapAgent(),
                AgentType.BRAILLE_ASSISTANT: BrailleAssistantAgent(),
                AgentType.RAG: RAGAgent(),
                AgentType.GAME_PLANNER: GamePlannerAgent(),
            }

            for agent_type in self.agents.keys():
                self.agent_stats[agent_type.value] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'avg_response_time': 0.0,
                    'last_used': None
                }

            self.logger.info(f"Initialized {len(self.agents)} agents successfully")

        except Exception as e:
            self.logger.error(f"Error initializing agents: {str(e)}")

    def process_request(self, user_request: str, context: Dict = None, priority: TaskPriority = TaskPriority.NORMAL) -> AgentResponse:
        context = context or {}
        start_time = time.time()

        try:
            routing_result = self.router.route_request(user_request, context)

            if not self.router.validate_routing(routing_result):
                self.logger.warning(f"Low confidence routing: {routing_result.confidence}")

            response = self._execute_agent_task(routing_result, user_request, context=context)

            self._update_agent_stats(routing_result.agent_type, response, time.time() - start_time)
            self._log_execution(user_request, routing_result, response, context)

            return response

        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            return AgentResponse(
                success=False,
                data=None,
                agent_name="AgentManager",
                execution_time=time.time() - start_time,
                error=str(e)
            )

    def _execute_agent_task(self, routing_result: RouteIntent, original_request: str, context: Dict = None) -> AgentResponse:
        context = context or {}
        agent_type = routing_result.agent_type
        agent = self.agents.get(agent_type)

        if not agent:
            raise ValueError(f"Agent {agent_type.value} not found")

        start_time = time.time()
        try:
            merged_params = {**routing_result.parameters, **context}  # ✅ merge routing + manual context
            method_name, parameters = self._prepare_agent_call(agent_type, merged_params, original_request)

            self.logger.info(f"Calling method '{method_name}' on {agent_type.value} with parameters: {parameters}")

            method = getattr(agent, method_name)
            result = method(**parameters)

            execution_time = time.time() - start_time
            return AgentResponse(
                success=True,
                data=result,
                agent_name=agent.name,
                execution_time=execution_time,
                metadata={
                    'routing_confidence': routing_result.confidence,
                    'routing_reasoning': routing_result.reasoning,
                    'parameters_used': parameters
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return AgentResponse(
                success=False,
                data=None,
                agent_name=agent.name,
                execution_time=execution_time,
                error=str(e)
            )

    def _prepare_agent_call(self, agent_type: AgentType, parameters: Dict, original_request: str) -> tuple:
        # Get language info from config
        language_code = parameters.get('language', 'english')
        
        base_params = {
            'language': language_code,
            'grade_level': parameters.get('grade_level', 5),
            'context': parameters.get('context', 'rural')
        }

        if agent_type == AgentType.VISION_AGENT:
            task_type = parameters.get('task_type', 'extract_text')
            call_params = {
                'task_type': task_type,
                'image_path': parameters.get('image_path'),
                'content': parameters.get('content'),
            }
            if task_type == 'generate_worksheets':
                call_params['target_grades'] = parameters.get('target_grades', [3, 5])
            return 'process_vision_task', call_params

        method_mappings = {
            AgentType.DOUBT_ASSISTANT: ('answer_question', {
                **base_params,
                'question': original_request
            }),

            AgentType.CONTENT_GENERATION: ('generate_content', {
                **base_params,
                'prompt': original_request,
                'content_type': parameters.get('content_type', 'story'),
                'subject': parameters.get('subject', 'general')
            }),

            AgentType.VISION_AGENT: ('process_vision_task', {
                'task_type': parameters.get('task_type', 'extract_text'),
                'image_path': parameters.get('image_path'),
                'content': parameters.get('content'),
                'target_grades': parameters.get('target_grades', [3, 5])
            }),


            AgentType.LESSON_PLANNER: ('plan_lessons', {
                'task_type': parameters.get('task_type', 'weekly'),
                'subjects': parameters.get('subjects'),
                'grade_levels': parameters.get('grade_levels'),
                'total_hours': parameters.get('total_hours', 30),
                'language': parameters.get('language', 'english'),
                'date': parameters.get('date'),
                'special_events': parameters.get('special_events')
            }),

            AgentType.DRAWINGS_AGENT: ('create_drawing', {
                **base_params,
                'description': original_request,
                'drawing_type': parameters.get('drawing_type', 'diagram'),
                'subject': parameters.get('subject', 'science')
            }),

            AgentType.MINDMAP_AGENT: ('generate_mindmap', {
                'topic': parameters.get('specific_topic', original_request),
                'language': parameters.get('language', 'english')
            }),

            AgentType.BRAILLE_ASSISTANT: ('convert_to_braille', {
                'text': original_request
            }),

            AgentType.RAG: ('generate_response', {
                'query': original_request,
                'num_chunks': parameters.get('num_chunks', 3)
            }),

            AgentType.GAME_PLANNER: (
                'get_answer' if any(word in original_request.lower() for word in ['answer', 'solution']) else 'get_game',
                {
                    'game_type': parameters.get('game_type', 'sudoku'),
                    'difficulty': parameters.get('difficulty', 'basic')
                }
            ),
        }

        return method_mappings.get(agent_type, ('process_request', {'request': original_request}))

    def _update_agent_stats(self, agent_type: AgentType, response: AgentResponse, execution_time: float):
        stats = self.agent_stats[agent_type.value]
        stats['total_requests'] += 1
        if response.success:
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1

        total_requests = stats['total_requests']
        current_avg = stats['avg_response_time']
        stats['avg_response_time'] = (current_avg * (total_requests - 1) + execution_time) / total_requests
        stats['last_used'] = datetime.now().isoformat()

    def _log_execution(self, request: str, routing_result: RouteIntent, response: AgentResponse, context: Dict = None):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'agent_used': routing_result.agent_type.value,
            'routing_confidence': routing_result.confidence,
            'success': response.success,
            'execution_time': response.execution_time,
            'context': context,
            'error': response.error
        }
        self.execution_history.append(log_entry)
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]

    def list_available_agents(self) -> Dict[str, str]:
        return {
            agent_type.value: agent.description
            for agent_type, agent in self.agents.items()
            if agent is not None
        }

    def health_check(self) -> Dict:
        health_status = {
            'system_status': 'healthy',
            'agent_status': {},
            'issues': []
        }

        for agent_type, agent in self.agents.items():
            try:
                if hasattr(agent, 'health_check'):
                    agent_health = agent.health_check()
                else:
                    agent_health = 'unknown'
                health_status['agent_status'][agent_type.value] = agent_health
            except Exception as e:
                health_status['agent_status'][agent_type.value] = 'error'
                health_status['issues'].append(f"{agent_type.value}: {str(e)}")

        if health_status['issues']:
            health_status['system_status'] = 'degraded'

        return health_status

    def get_agent_stats(self) -> Dict:
        return {
            'total_requests': sum(a['total_requests'] for a in self.agent_stats.values()),
            'agent_statistics': self.agent_stats,
        }
