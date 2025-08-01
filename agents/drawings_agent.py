import os
from datetime import datetime
from typing import Dict, List
from agents.base_agent import BaseAgent


class DrawingsAgent(BaseAgent):
    """Agent for generating drawing instructions and visual aids"""

    def __init__(self):
        super().__init__(
            name="Drawings Agent",
            description="Creates instructions for simple drawings and visual aids"
        )

    def _get_root_folder(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _save_to_file(self, content: str, filename: str) -> str:
        folder = os.path.join(self._get_root_folder(), "data", "drawings")
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def generate_diagram_instructions(self, concept: str, diagram_type: str = "simple_drawing") -> Dict:
        """Generate step-by-step drawing instructions"""

        prompt = f"""
        Create step-by-step instructions for drawing a {diagram_type} to explain: {concept}

        Requirements:
        1. Use only basic shapes (circles, lines, rectangles, triangles)
        2. Suitable for blackboard/whiteboard drawing
        3. Clear, numbered steps
        4. Include labels and annotations
        5. Mention chalk colors if helpful
        6. Add teaching tips for each step

        Format:
        **Diagram Title:** [Title for the drawing]
        **Materials Needed:** [Chalk colors, tools needed]
        **Step-by-Step Instructions:**

        Step 1: [First step with detailed description]
        - Teacher tip: [Helpful teaching note]

        Step 2: [Second step]
        - Teacher tip: [Helpful teaching note]

        [Continue for all steps]

        **Labels to Add:** [All text labels needed]
        **Key Points to Explain:** [What to emphasize while drawing]
        **Common Mistakes:** [What to avoid]
        **Variations:** [How to adapt for different grades]
        """

        response = self._make_request(prompt)

        filename = f"instructions_{concept.lower().replace(' ', '_')}.txt"
        path = self._save_to_file(response, filename)

        result = {
            "concept": concept,
            "diagram_type": diagram_type,
            "instructions": response,
            "saved_path": path,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

        self.log_interaction(f"Diagram instructions for {concept}", response, {
            "diagram_type": diagram_type
        })

        return result

    def create_visual_aid_plan(self, topic: str, grade_levels: List[int]) -> Dict:
        """Create a comprehensive visual aid plan for a topic"""

        grades_str = ", ".join(map(str, grade_levels))

        prompt = f"""
        Create a comprehensive visual aid plan for teaching: {topic}
        Grade Levels: {grades_str}

        Include:
        1. List of all visual aids needed
        2. Drawing instructions for each
        3. When to use each visual during lesson
        4. How to adapt for different grades
        5. Student interaction opportunities

        Consider:
        - Progression from simple to complex
        - Interactive elements
        - Local/cultural relevance
        - Low-cost materials
        """

        response = self._make_request(prompt)

        filename = f"visual_plan_{topic.lower().replace(' ', '_')}.txt"
        path = self._save_to_file(response, filename)

        result = {
            "topic": topic,
            "grade_levels": grade_levels,
            "visual_aid_plan": response,
            "saved_path": path,
            "timestamp": datetime.now().isoformat(),
            "agent": self.name
        }

        self.log_interaction(f"Visual aid plan for {topic}", response, {
            "grade_levels": grade_levels
        })

        return result
    
    def handle_task(self, description: str, drawing_type: str = "simple_drawing", language: str = "english", grade_level: int = 5, **kwargs) -> Dict:
        """
        Handles generic drawing-related tasks.
        Defaults to generating drawing instructions based on the description.
        """
        return self.generate_diagram_instructions(concept=description, diagram_type=drawing_type)

    create_drawing = handle_task
