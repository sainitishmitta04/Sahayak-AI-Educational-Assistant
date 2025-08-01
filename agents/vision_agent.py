import os
from datetime import datetime
from typing import Dict, List
from agents.base_agent import BaseAgent

class GeminiVisionAgent(BaseAgent):
    """Agent for processing images and creating differentiated content"""

    def __init__(self):
        super().__init__(
            "Vision Agent",
            "Processes textbook images and creates differentiated worksheets"
        )

    def _get_project_root(self):
        # This ensures all paths resolve to project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def extract_text_from_textbook(self, image_path: str) -> Dict:
        """Extract text and structure from a textbook page"""

        prompt = """
        Analyze this textbook page and extract:
        1. All visible text content
        2. The subject/topic being covered
        3. Grade level (if identifiable)
        4. Key concepts mentioned
        5. Any diagrams, charts, or images described

        Format your response as:
        **Subject:** [Subject identified]
        **Grade Level:** [Estimated grade level]
        **Main Topic:** [Primary topic]
        **Text Content:** [All text content]
        **Key Concepts:** [Important concepts listed]
        **Visual Elements:** [Description of any diagrams/images]
        **Learning Objectives:** [What students should learn from this page]
        """

        response = self._make_request(prompt, image_path=image_path)

        # Save response
        image_filename = os.path.splitext(os.path.basename(image_path))[0]
        root = self._get_project_root()
        save_folder = os.path.join(root, "data", "extracted_text")
        os.makedirs(save_folder, exist_ok=True)

        text_path = os.path.join(save_folder, f"{image_filename}_extracted.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(response)

        result = {
            'image_path': image_path,
            'extracted_content': response,
            'saved_path': text_path,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }

        self.log_interaction("Textbook image analysis", response, {
            'image_path': image_path
        })

        return result

    def generate_differentiated_worksheets(self, content: str, target_grades: List[int]) -> Dict:
        """Generate worksheets for different grade levels"""

        worksheets = {}
        root = self._get_project_root()
        save_folder = os.path.join(root, "data", "worksheets")
        os.makedirs(save_folder, exist_ok=True)

        for grade in target_grades:
            prompt = f"""
            Create a worksheet for Grade {grade} based on this textbook content:

            Content: {content}

            Requirements for Grade {grade}:
            1. Adjust vocabulary to grade level
            2. Create age-appropriate questions
            3. Include variety: MCQ, short answer, fill-in-blanks, true/false
            4. Add visual thinking questions
            5. Include practical applications

            Format:
            **Worksheet Title:** [Title for the worksheet]
            **Instructions:** [Clear instructions for students]
            **Section A - Multiple Choice:** [3 MCQ questions with options]
            **Section B - Short Answers:** [3 short answer questions]
            **Section C - Fill in the Blanks:** [3 fill-in-the-blank questions]
            **Section D - Think and Apply:** [1 practical application question]
            **Answer Key:** [All correct answers]
            """

            response = self._make_request(prompt)
            worksheets[f'grade_{grade}'] = response

            # Save each worksheet
            worksheet_path = os.path.join(save_folder, f"worksheet_grade_{grade}.txt")
            with open(worksheet_path, "w", encoding="utf-8") as f:
                f.write(response)

        result = {
            'original_content': content,
            'target_grades': target_grades,
            'worksheets': worksheets,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }

        self.log_interaction("Differentiated worksheets creation",
                             f"Created worksheets for grades {target_grades}", {
                                 'target_grades': target_grades
                             })

        return result
    
    def process_image(self, task_description: str, image_path: str = None,
                  task_type: str = "extract_text", content: str = None,
                  target_grades: List[int] = [3, 5], **kwargs) -> dict:
        """
        Unified interface to process vision tasks.

        task_type:
            - 'extract_text' → calls extract_text_from_textbook()
            - 'generate_worksheets' → calls generate_differentiated_worksheets()
        """

        if task_type == "extract_text":
            if not image_path:
                raise ValueError("image_path is required for extract_text task")
            return self.extract_text_from_textbook(image_path)

        elif task_type == "generate_worksheets":
            if not content:
                raise ValueError("content is required for worksheet generation")
            return self.generate_differentiated_worksheets(content, target_grades)

        else:
            raise ValueError(f"Unsupported vision task type: {task_type}")
        
    def process_vision_task(self, task_type: str = "extract_text", image_path: str = None,
                        content: str = None, target_grades: List[int] = None, **kwargs) -> Dict:
        """Unified method to process image-based tasks"""

        if task_type == "extract_text":
            if not image_path:
                raise ValueError("image_path is required for extract_text task")
            return self.extract_text_from_textbook(image_path=image_path)

        elif task_type == "generate_worksheets":
            # ✅ Automatically extract if only image is given
            if not content and image_path:
                extract_result = self.extract_text_from_textbook(image_path=image_path)
                content = extract_result.get("extracted_content", "")

            if not content or not target_grades:
                raise ValueError("Both 'content' and 'target_grades' are required for generating worksheets")

            return self.generate_differentiated_worksheets(content=content, target_grades=target_grades)

        else:
            raise ValueError(f"Unsupported task_type '{task_type}' in VisionAgent.")

