import google.generativeai as genai
import time
from datetime import datetime
from typing import Dict, Optional
from collections import deque
from PIL import Image
import os

from config.sahayak_config import SahayakConfig

class BaseAgent:
    """Base class for all Sahayak AI agents"""

    def __init__(self, name: str, description: str, model: str = SahayakConfig.DEFAULT_MODEL):
        self.name = name
        self.description = description
        self.model = model
        self.conversation_history = []
        self.request_timestamps = deque(maxlen=5)  # Track last 5 requests for 5/s limit

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Required in .env

    def _wait_if_needed(self):
        """Auto-throttle to max 5 requests/sec"""
        now = time.time()
        if len(self.request_timestamps) == 5:
            elapsed = now - self.request_timestamps[0]
            if elapsed < 1:
                sleep_time = 1 - elapsed
                print(f"⏳ Waiting {sleep_time:.2f}s to avoid hitting rate limit...")
                time.sleep(sleep_time)
        self.request_timestamps.append(time.time())

    def _make_request(self, prompt: str, image_path: Optional[str] = None) -> str:
        self._wait_if_needed()
        try:
            model = genai.GenerativeModel(self.model)
            if image_path:
                image = Image.open(image_path)
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def log_interaction(self, request: str, response: str, metadata: Dict = None):
        """Log interaction for tracking"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.name,
            'request': request,
            'response': response,
            'metadata': metadata or {}
        }
        self.conversation_history.append(log_entry)

    def get_stats(self) -> Dict:
        """Return agent usage statistics"""
        return {
            'name': self.name,
            'total_requests': len(self.conversation_history),
            'last_used': self.request_timestamps[-1] if self.request_timestamps else None
        }
