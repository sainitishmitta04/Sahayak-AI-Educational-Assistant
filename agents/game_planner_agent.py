import os
import logging
from config.sahayak_config import SahayakConfig
from agents.base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Optional

class GamePlannerAgent(BaseAgent):
    """Agent for handling various educational games"""
    
    def __init__(self):
        super().__init__(
            name="Game Planner",
            description="Handles educational games like Sudoku and Riddles",
            model=SahayakConfig.DEFAULT_MODEL
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Sudoku paths
        self.sudoku_dir = os.path.join("data", "sudoko")
        self.logger.info(f"Sudoku directory: {self.sudoku_dir}")
        
        # Initialize Riddles paths
        self.riddles_dir = os.path.join("data", "riddles")
        self.logger.info(f"Riddles directory: {self.riddles_dir}")
        
        # Verify directories exist
        for directory in [self.sudoku_dir, self.riddles_dir]:
            if not os.path.exists(directory):
                self.logger.error(f"Directory not found: {directory}")
                os.makedirs(directory, exist_ok=True)
        
        # Setup Sudoku paths
        self.sudoku_paths = {
            'basic': {
                'question': os.path.join(self.sudoku_dir, 'basic_question.jpeg'),
                'answer': os.path.join(self.sudoku_dir, 'basic_answer.jpeg')
            },
            'medium': {
                'question': os.path.join(self.sudoku_dir, 'medium_question.jpeg'),
                'answer': os.path.join(self.sudoku_dir, 'medium_answer.jpeg')
            },
            'hard': {
                'question': os.path.join(self.sudoku_dir, 'hard_question.jpeg'),
                'answer': os.path.join(self.sudoku_dir, 'hard_answer.jpeg')
            }
        }
        
        # Setup Riddles paths with actual file names
        self.riddles_paths = {
            'basic': {
                'question': os.path.join(self.riddles_dir, 'Riddle1.jpeg'),
                'answer': os.path.join(self.riddles_dir, 'riddle1_answer.jpeg')
            },
            'medium': {
                'question': os.path.join(self.riddles_dir, 'riddle_2.jpeg'),
                'answer': os.path.join(self.riddles_dir, 'riddle2_answer.jpeg')
            }
        }
        
        # Log available files
        self._log_available_files("Sudoku", self.sudoku_paths)
        self._log_available_files("Riddles", self.riddles_paths)
    
    def _log_available_files(self, game_type: str, paths: Dict) -> None:
        """Helper method to log available files"""
        self.logger.info(f"Checking available {game_type} files:")
        for difficulty, file_paths in paths.items():
            for key, path in file_paths.items():
                exists = os.path.exists(path)
                self.logger.info(f"{difficulty} {key}: {path} - {'Found' if exists else 'Not found'}")
    
    def get_game(self, game_type: str, difficulty: str = 'medium', **kwargs) -> Dict:
        """
        Get the game image path for the specified type and difficulty
        
        Args:
            game_type: Type of game ('sudoku' or 'riddles')
            difficulty: Difficulty level ('basic', 'medium', 'hard')
            
        Returns:
            Dict containing game image path
        """
        game_type = game_type.lower()
        difficulty = difficulty.lower()
        
        # Select appropriate paths based on game type
        if game_type == 'sudoku':
            paths = self.sudoku_paths
        elif game_type == 'riddles':
            paths = self.riddles_paths
        else:
            error_msg = f"Invalid game type: {game_type}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Validate difficulty
        if difficulty not in paths:
            self.logger.warning(f"Invalid difficulty '{difficulty}' for {game_type}, defaulting to 'basic'")
            difficulty = 'basic'
        
        puzzle_path = paths[difficulty]['question']
        
        # Log attempt to access puzzle
        self.logger.info(f"Attempting to access {game_type} puzzle: {puzzle_path}")
        self.logger.info(f"File exists: {os.path.exists(puzzle_path)}")
        
        # Verify file exists
        if not os.path.exists(puzzle_path):
            error_msg = f"{game_type.title()} image not found for {difficulty} difficulty at {puzzle_path}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        return {
            'success': True,
            'puzzle_path': puzzle_path,
            'difficulty': difficulty,
            'game_type': game_type,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }
    
    def get_answer(self, game_type: str, difficulty: str = 'medium', **kwargs) -> Dict:
        """
        Get the answer image path for the specified type and difficulty
        
        Args:
            game_type: Type of game ('sudoku' or 'riddles')
            difficulty: Difficulty level ('basic', 'medium', 'hard')
            
        Returns:
            Dict containing answer image path
        """
        game_type = game_type.lower()
        difficulty = difficulty.lower()
        
        # Select appropriate paths based on game type
        if game_type == 'sudoku':
            paths = self.sudoku_paths
        elif game_type == 'riddles':
            paths = self.riddles_paths
        else:
            error_msg = f"Invalid game type: {game_type}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Validate difficulty
        if difficulty not in paths:
            self.logger.warning(f"Invalid difficulty '{difficulty}' for {game_type}, defaulting to 'basic'")
            difficulty = 'basic'
        
        answer_path = paths[difficulty]['answer']
        
        # Log attempt to access answer
        self.logger.info(f"Attempting to access {game_type} answer: {answer_path}")
        self.logger.info(f"File exists: {os.path.exists(answer_path)}")
        
        # Verify file exists
        if not os.path.exists(answer_path):
            error_msg = f"{game_type.title()} answer not found for {difficulty} difficulty at {answer_path}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        return {
            'success': True,
            'answer_path': answer_path,
            'difficulty': difficulty,
            'game_type': game_type,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }
    
    def list_available_games(self) -> Dict:
        """
        List all available games and their status
        
        Returns:
            Dict containing available games and their status
        """
        available_games = {
            'sudoku': self._check_game_availability(self.sudoku_paths),
            'riddles': self._check_game_availability(self.riddles_paths)
        }
        
        return {
            'success': True,
            'available_games': available_games,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }
    
    def _check_game_availability(self, paths: Dict) -> Dict:
        """Helper method to check game file availability"""
        availability = {}
        for difficulty, file_paths in paths.items():
            availability[difficulty] = {
                'has_question': os.path.exists(file_paths['question']),
                'has_answer': os.path.exists(file_paths['answer'])
            }
        return availability 