import os
import logging
from config.sahayak_config import SahayakConfig
from agents.base_agent import BaseAgent
from datetime import datetime
from typing import Dict, Optional

class VideoAgent(BaseAgent):
    """Agent for handling educational videos for different concepts"""
    
    def __init__(self):
        super().__init__(
            name="Video Agent",
            description="Handles educational videos for different concepts with sign language support",
            model=SahayakConfig.DEFAULT_MODEL
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize video paths
        self.videos_dir = os.path.join("data", "videos")
        self.logger.info(f"Videos directory: {self.videos_dir}")
        
        # Create videos directory if it doesn't exist
        if not os.path.exists(self.videos_dir):
            self.logger.info("Creating videos directory")
            os.makedirs(self.videos_dir, exist_ok=True)
        
        # Setup video paths for different concepts and grades
        self.video_paths = {
            'speed': {
                6: os.path.join(self.videos_dir, 'speed.mp4')
            },
            'square': {
                6: os.path.join(self.videos_dir, 'square.mp4')
            },
            'trigonometry': {  # Fixed spelling to match app.py
                6: os.path.join(self.videos_dir, 'Trignometry.mp4')
            }
        }
        
        # Define concept descriptions for better responses
        self.concept_descriptions = {
            'speed': {
                'title': 'Speed and Motion',
                'description': 'Learn about velocity, movement, and the fundamentals of speed calculation',
                'topics': ['Velocity calculation', 'Distance and time', 'Motion concepts']
            },
            'square': {
                'title': 'Square and Geometry',
                'description': 'Understand squares, their properties, and geometric principles',
                'topics': ['Square properties', 'Area calculation', 'Perimeter concepts']
            },
            'trigonometry': {
                'title': 'Trigonometry Basics',
                'description': 'Explore fundamental concepts of trigonometry and angle measurements',
                'topics': ['Sine, cosine, and tangent', 'Angle relationships', 'Triangle properties']
            }
        }
        
        # Log available videos
        self._log_available_videos()
    
    def _log_available_videos(self) -> None:
        """Helper method to log available video files"""
        self.logger.info("Checking available video files:")
        for concept, grade_paths in self.video_paths.items():
            for grade, path in grade_paths.items():
                exists = os.path.exists(path)
                file_size = os.path.getsize(path) if exists else 0
                self.logger.info(f"{concept} (Grade {grade}): {path} - {'Found' if exists else 'Not found'} - Size: {file_size} bytes")

    def validate_video_file(self, video_path: str) -> Dict:
        """Validate if a video file exists and is not empty"""
        if not os.path.exists(video_path):
            return {'valid': False, 'error': 'Video file not found'}
        
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            return {'valid': False, 'error': 'Video file is empty (0 bytes)'}
            
        return {'valid': True, 'size': file_size}

    def get_video(self, concept: str, grade: int, **kwargs) -> Dict:
        """
        Get the video path for the specified concept and grade
        
        Args:
            concept: Educational concept ('speed', 'square', 'trigonometry', etc.)
            grade: Grade level (integer)
            
        Returns:
            Dict containing video path and metadata
        """
        concept = concept.lower()
        
        # Check if concept exists
        if concept not in self.video_paths:
            error_msg = f"No video available for concept: {concept}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Check if grade exists for concept
        if grade not in self.video_paths[concept]:
            error_msg = f"No video available for {concept} at grade {grade}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        video_path = self.video_paths[concept][grade]
        
        # Validate video file
        validation = self.validate_video_file(video_path)
        if not validation['valid']:
            error_msg = f"Invalid video file for {concept} (Grade {grade}): {validation['error']}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg}
        
        # Get concept description
        concept_info = self.concept_descriptions.get(concept, {
            'title': concept.title(),
            'description': f'Educational video about {concept}',
            'topics': []
        })
        
        # Log successful video access
        self.logger.info(f"Successfully accessed video for {concept} (Grade {grade}): {video_path} - Size: {validation['size']} bytes")
        
        return {
            'success': True,
            'video_path': video_path,
            'concept': concept,
            'title': concept_info['title'],
            'description': concept_info['description'],
            'topics': concept_info['topics'],
            'grade': grade,
            'file_size': validation['size'],
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }
    
    def list_available_videos(self) -> Dict:
        """
        List all available educational videos
        
        Returns:
            Dict containing available videos and their status
        """
        available_videos = {}
        for concept, grade_paths in self.video_paths.items():
            available_videos[concept] = {}
            for grade, path in grade_paths.items():
                available_videos[concept][grade] = {
                    'available': os.path.exists(path),
                    'path': path
                }
        
        return {
            'success': True,
            'available_videos': available_videos,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }
    
    def add_video(self, concept: str, grade: int, video_path: str) -> Dict:
        """
        Add a new video to the collection
        
        Args:
            concept: Educational concept
            grade: Grade level
            video_path: Path to the video file
            
        Returns:
            Dict containing status of operation
        """
        concept = concept.lower()
        
        # Create concept entry if it doesn't exist
        if concept not in self.video_paths:
            self.video_paths[concept] = {}
        
        # Add or update video path
        target_path = os.path.join(self.videos_dir, f"{concept}_sign.mp4")
        
        try:
            # If video_path is different from target_path, copy the file
            if os.path.abspath(video_path) != os.path.abspath(target_path):
                import shutil
                shutil.copy2(video_path, target_path)
            
            self.video_paths[concept][grade] = target_path
            self.logger.info(f"Added video for {concept} (Grade {grade})")
            
            return {
                'success': True,
                'message': f"Successfully added video for {concept} (Grade {grade})",
                'path': target_path,
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }
            
        except Exception as e:
            error_msg = f"Failed to add video: {str(e)}"
            self.logger.error(error_msg)
            return {'success': False, 'error': error_msg} 