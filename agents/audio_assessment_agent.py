import os
from datetime import datetime
from typing import Dict, List
from google import genai
from google.genai.types import HttpOptions, Part
from agents.base_agent import BaseAgent
from config.sahayak_config import SahayakConfig
# from google.ai.generativelanguage import Part  # Assuming you're using Google AI SDK (generativeai)

from datetime import datetime
import os
from google.generativeai import GenerativeModel, configure

class AudioAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Audio Assessment Agent",
            description="Assesses pronunciation and generates TTS",
            model="gemini-1.5-pro"  # or gemini-1.5-flash depending on your access
        )
        configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = GenerativeModel(self.model)

    def assess_pronunciation(self, audio_path: str, reference_text: str, language: str = 'english') -> dict:
        """Evaluate user's pronunciation against a reference sentence"""

        lang_name = SahayakConfig.LANGUAGES.get(language, 'English')

        with open(audio_path, "rb") as f:
            audio_data = f.read()

        # Construct prompt
        prompt_1 = f"Transcribe the following audio in {lang_name}."
        prompt_2 = (
            f"Compare it with the reference text:\n\"{reference_text}\"\n"
            "Give feedback in this format:\n"
            "- Pronunciation score (1 to 5)\n"
            "- Mispronounced words\n"
            "- Word Error Rate (WER)\n"
            "- Tips for improvement"
        )

        # Send request to Gemini
        response = self.model.generate_content([prompt_1, audio_data, prompt_2])
        result_text = response.text.strip()

        # Save result
        base = os.path.splitext(os.path.basename(audio_path))[0]
        save_path = os.path.join("data", "audio_feedback", f"{base}_assessment.txt")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(result_text)

        return {
            "assessment": result_text,
            "saved_path": save_path,
            "timestamp": datetime.now().isoformat()
        }


    # def generate_practice_audio(self, topic: str, language: str = 'english') -> Dict:
    #     """Generate both reading passage and TTS audio for practice"""

    #     lang_name = SahayakConfig.LANGUAGES.get(language, 'English')
    #     passage_resp = self.client.models.generate_content(
    #         model="gemini-2.0-flash",
    #         contents=f"Write a 50‑word reading passage in {lang_name} about {topic} with tricky pronunciations."
    #     )
    #     passage = passage_resp.text.strip()

    #     tts_resp = self.client.models.generate_content(
    #         model="gemini-2.5-flash",
    #         contents=[Part.from_text(passage)],
    #         config=HttpOptions(extra_body={
    #             "response_modalities": ["AUDIO"],
    #             "speech_config": {
    #                 "voice_config": {"prebuilt_voice_config": {"voice_name": "kore"}}
    #             }
    #         })
    #     )

    #     audio_data = tts_resp.candidates[0].content.parts[0].inline_data.data
    #     audio_path = self._save_file("tts", f"{topic.replace(' ', '_')}.wav", audio_data)

    #     return {"topic": topic, "passage": passage, "audio_path": audio_path,
    #             "timestamp": datetime.now().isoformat()}
