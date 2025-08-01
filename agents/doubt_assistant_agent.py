from config.sahayak_config import SahayakConfig
from agents.base_agent import BaseAgent
from datetime import datetime
from typing import Dict

class DoubtAssistantAgent(BaseAgent):
    """Agent for answering student and teacher doubts in multiple languages"""
    
    def __init__(self):
        super().__init__(
            name="Doubt Assistant",
            description="Answers student questions in simple, localized language",
            model=SahayakConfig.DEFAULT_MODEL
        )
        self.supported_languages = list(SahayakConfig.LANGUAGES.keys())
    
    def answer_question(
        self,
        question: str,
        language: str = 'english',
        grade_level: int = 5,
        context: str = 'rural'
    ) -> Dict:
        """
        Answer a student's question in the specified language
        
        Args:
            question: The question to answer
            language: Language code (e.g., 'english', 'hindi', etc.)
            grade_level: Student's grade level (1-12)
            context: Learning context ('rural', 'urban', etc.)
            
        Returns:
            Dict containing the answer and metadata
        """
        # Normalize language code and get language info
        language = language.lower()
        language_info = SahayakConfig.get_language_info(language)
        language_name = language_info['name']
        native_name = language_info['native']

        # Get context information
        context_info = SahayakConfig.get_context_info(context)
        adaptations = context_info['adaptations']

        prompt = f"""
        You are a helpful teaching assistant for a {context} Indian classroom.
        A student has asked the following question. Answer it in {language_name} language ({native_name}) using the native script (if applicable).

        Question: {question}
        Grade Level: {grade_level}
        Context: {context}
        Adaptations: {', '.join(adaptations)}

        Guidelines:
        1. Use simple, age-appropriate language for grade {grade_level}
        2. Keep the explanation concise and clear
        3. Use relatable Indian examples (village, festivals, farming, etc.)
        4. Encourage curiosity and engagement
        5. If possible, include a short practical activity or real-life analogy

        Return your answer in this format:

        **Answer:** [Main explanation]
        **Example:** [Simple, relatable example]
        **Fun Fact:** [Interesting fact, activity, or trivia related to the topic]
        """

        response = self._make_request(prompt)

        result = {
            "question": question,
            "language": {
                "code": language,
                "name": language_name,
                "native": native_name
            },
            "grade_level": grade_level,
            "context": context,
            "answer": response,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

        self.log_interaction(question, response, {
            "language": language,
            "grade_level": grade_level,
            "context": context
        })

        return result
