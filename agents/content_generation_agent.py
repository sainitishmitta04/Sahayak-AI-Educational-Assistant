from datetime import datetime
from config.sahayak_config import SahayakConfig
from agents.base_agent import BaseAgent

class ContentGenerationAgent(BaseAgent):
    """Agent for generating educational content"""
    
    def __init__(self):
        super().__init__(
            name="Content Generator",
            description="Creates stories, explanations, and educational content",
            model=SahayakConfig.DEFAULT_MODEL
        )
    
    def create_story(self, topic: str, language: str = 'english', 
                     grade_level: int = 5, setting: str = 'rural') -> dict:
        """Create an educational story"""
        language_name = SahayakConfig.LANGUAGES.get(language, 'English')
        
        prompt = f"""
        Create an engaging educational story in {language_name} for grade {grade_level} students.

        Topic: {topic}
        Setting: {setting} India
        Target Age: {6 + grade_level} years old

        Requirements:
        1. Culturally relevant to the Indian context
        2. Include educational information about {topic}
        3. Use age-appropriate vocabulary
        4. Add relatable characters and dialogues
        5. Clear moral or learning outcome
        6. Limit: 200–300 words

        Format:
        **Title:** [Story title]
        **Characters:** [Main characters]
        **Story:** [The complete story]
        **Learning Points:** [Key educational takeaways]
        **Discussion Questions:** [2–3 questions for classroom discussion]
        """

        response = self._make_request(prompt)

        result = {
            'topic': topic,
            'story': response,
            'language': language,
            'grade_level': grade_level,
            'setting': setting,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }

        self.log_interaction(f"Story on {topic}", response, {
            'language': language,
            'grade_level': grade_level,
            'setting': setting
        })

        return result
    
    def create_explanation(self, concept: str, language: str = 'english',
                       difficulty: str = 'medium') -> dict:
        """Create a detailed explanation of a concept"""

        language_name = SahayakConfig.LANGUAGES.get(language, 'English')

        prompt = f"""
        Explain this concept in {language_name} with {difficulty} difficulty level:

        Concept: {concept}

        Requirements:
        1. Start with a simple definition
        2. Use analogies from daily Indian life
        3. Include real-world examples
        4. Break down complex ideas into simple parts
        5. Add visual descriptions where helpful
        6. Suggest simple experiments or activities if applicable

        Format:
        **Definition:** [Simple definition]
        **Explanation:** [Detailed explanation with analogies]
        **Examples:** [2-3 real-world examples]
        **Activity:** [A simple classroom activity]
        **Remember:** [Key points to remember]
        """

        raw_response = self._make_request(prompt)

        # Clean leading commentary like "Here's an explanation..."
        import re
        match = re.search(r"\*\*Definition:\*\*", raw_response)
        if match:
            cleaned_response = raw_response[match.start():].strip()
        else:
            cleaned_response = raw_response.strip()

        result = {
            'concept': concept,
            'explanation': cleaned_response,
            'language': language,
            'difficulty': difficulty,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }

        self.log_interaction(f"Explanation of {concept}", cleaned_response, {
            'language': language,
            'difficulty': difficulty
        })

        return result
    
    def generate_content(self, prompt: str, subject: str = "general", content_type: str = "story",
                     language: str = "english", grade_level: int = 5, context: str = "rural") -> dict:
        """
        Unified content generation method for orchestration
        Dispatches to story or explanation generator based on content_type
        """
        if content_type == "story":
            return self.create_story(
                topic=prompt,
                language=language,
                grade_level=grade_level,
                setting=context
            )
        elif content_type == "explanation":
            return self.create_explanation(
                concept=prompt,
                language=language,
                difficulty="medium"
            )
        else:
            raise ValueError(f"Unsupported content_type: {content_type}")
