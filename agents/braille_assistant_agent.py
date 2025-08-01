import os
import requests
from datetime import datetime
from typing import Dict, Optional
from docx import Document
from .base_agent import BaseAgent
from config.sahayak_config import SahayakConfig

class BrailleAssistantAgent(BaseAgent):
    """Agent for converting text to Braille"""

    def __init__(self):
        super().__init__(
            name="Braille Assistant",
            description="Converts text to Braille format",
            model=SahayakConfig.DEFAULT_MODEL
        )
        # Basic English to Braille mapping
        self.braille_map = {
            'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋',
            'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇',
            'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗',
            's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
            'y': '⠽', 'z': '⠵', ' ': ' ', ',': '⠂', '.': '⠲', '!': '⠖',
            '?': '⠦', '"': '⠦', "'": '⠄', '-': '⠤', '1': '⠼⠁', '2': '⠼⠃',
            '3': '⠼⠉', '4': '⠼⠙', '5': '⠼⠑', '6': '⠼⠋', '7': '⠼⠛',
            '8': '⠼⠓', '9': '⠼⠊', '0': '⠼⠚'
        }

    def _text_to_braille(self, text: str) -> str:
        """Convert text to Braille"""
        result = []
        for char in text.lower():
            result.append(self.braille_map.get(char, char))
        return ''.join(result)

    def convert_to_braille(self, text: str) -> Dict:
        """Convert text to Braille format"""
        try:
            # First get the explanation from the model
            prompt = f"Explain this concept in simple, clear language: {text}"
            explanation = self._make_request(prompt)
            
            # Convert the explanation to Braille
            braille_text = self._text_to_braille(explanation)
            
            return {
                'status': 'success',
                'original_text': explanation,
                'braille_text': braille_text,
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'agent': self.name
            }
