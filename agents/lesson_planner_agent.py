import os
from datetime import datetime
from typing import Dict, List
from agents.base_agent import BaseAgent
from config.sahayak_config import SahayakConfig


class LessonPlannerAgent(BaseAgent):
    """Agent for creating lesson plans and schedules"""

    def __init__(self):
        super().__init__(
            name="Lesson Planner",
            description="Creates weekly lesson plans and activity schedules",
            model=SahayakConfig.DEFAULT_MODEL
        )

    def _get_project_root(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _save_text(self, content: str, filename: str) -> str:
        folder = os.path.join(self._get_project_root(), "data", "lesson_plans")
        os.makedirs(folder, exist_ok=True)

        filepath = os.path.join(folder, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def generate_weekly_plan(self, subjects: List[str], grade_levels: List[int],
                             total_hours: int = 30, language: str = 'english') -> Dict:
        """Generate a comprehensive weekly lesson plan"""

        language_name = SahayakConfig.LANGUAGES.get(language, 'English')
        subjects_str = ", ".join(subjects)
        grades_str = ", ".join(map(str, grade_levels))

        prompt = f"""
        Create a detailed weekly lesson plan in {language_name} for a multi-grade classroom:

        Subjects: {subjects_str}
        Grade Levels: {grades_str}
        Total Teaching Hours: {total_hours} per week
        Context: Rural Indian school with limited resources

        Requirements:
        1. Distribute time fairly among subjects and grades
        2. Include mixed-grade activities where possible
        3. Use locally available materials
        4. Add assessment methods for each subject
        5. Include break times and physical activities
        6. Consider different learning styles

        Format:
        **Week Overview:**
        - Total Hours: {total_hours}
        - Subjects Covered: {subjects_str}
        - Grade Levels: {grades_str}

        **Daily Breakdown:**
        **MONDAY**
        - 9:00–9:45: [Subject] – Grade [X] – [Topic] – [Activity]
        - 9:45–10:30: [Subject] – Grade [Y] – [Topic] – [Activity]
        - 10:30–10:45: BREAK
        ...

        **Assessment Schedule:**
        - [Subject]: [Assessment method and timing]

        **Resource Requirements:**
        - Materials: [List]
        - Preparation Time: [Hours]

        **Differentiation Strategies:**
        [How to handle different grade levels simultaneously]

        **Homework Plan:**
        [Weekly homework assignments by grade]
        """

        response = self._make_request(prompt)

        filename = f"weekly_plan_{'_'.join(subjects)}.txt".lower().replace(" ", "_")
        saved_path = self._save_text(response, filename)

        result = {
            'subjects': subjects,
            'grade_levels': grade_levels,
            'total_hours': total_hours,
            'language': language,
            'lesson_plan': response,
            'saved_path': saved_path,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }

        self.log_interaction(f"Weekly plan for {subjects_str}", response, {
            'subjects': subjects,
            'grade_levels': grade_levels,
            'total_hours': total_hours
        })

        return result

    def create_daily_schedule(self, date: str, subjects_today: List[str],
                              special_events: List[str] = None) -> Dict:
        """Create a detailed daily schedule"""

        special_events = special_events or []

        prompt = f"""
        Create a detailed daily schedule for {date}:

        Subjects Today: {', '.join(subjects_today)}
        Special Events: {', '.join(special_events) if special_events else 'None'}

        Include:
        1. Time slots with buffer time
        2. Transition activities
        3. Brain breaks
        4. Assessment opportunities
        5. Cleanup and preparation time

        Format: hour-by-hour with activities and teacher notes.
        """

        response = self._make_request(prompt)

        filename = f"daily_schedule_{date.replace('-', '_')}.txt"
        saved_path = self._save_text(response, filename)

        result = {
            'date': date,
            'subjects': subjects_today,
            'special_events': special_events,
            'schedule': response,
            'saved_path': saved_path,
            'timestamp': datetime.now().isoformat(),
            'agent': self.name
        }

        self.log_interaction(f"Daily schedule for {date}", response, {
            'subjects_today': subjects_today,
            'special_events': special_events
        })

        return result
    
    def plan_lessons(self, task_type: str = "weekly", **kwargs) -> Dict:

        """
        Generic dispatcher for lesson planning tasks.

        Accepts:
        - task_type: "weekly" or "daily"
        - kwargs: subjects, grade_levels, date, etc.
        """
        if task_type == "weekly":
            if not kwargs.get("subjects") or not kwargs.get("grade_levels"):
                raise ValueError("Both 'subjects' and 'grade_levels' are required for weekly planning.")
            return self.generate_weekly_plan(
                subjects=kwargs["subjects"],
                grade_levels=kwargs["grade_levels"],
                total_hours=kwargs.get("total_hours", 30),
                language=kwargs.get("language", "english")
            )

        elif task_type == "daily":
            if not kwargs.get("subjects") or not kwargs.get("date"):
                raise ValueError("Both 'subjects' and 'date' are required for daily planning.")
            return self.create_daily_schedule(
                date=kwargs["date"],
                subjects_today=kwargs["subjects"],
                special_events=kwargs.get("special_events", [])
            )

        else:
            raise ValueError(f"Unsupported task_type '{task_type}' in LessonPlannerAgent.")


        