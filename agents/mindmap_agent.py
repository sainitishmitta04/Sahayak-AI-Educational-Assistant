from config.sahayak_config import SahayakConfig
from agents.base_agent import BaseAgent
from agents.visualizer import visualize_mindmap_with_networkx, save_mindmap_text

class MindMapAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MindMapAgent",
            description="Generates mind maps for classroom concepts",
            model=SahayakConfig.DEFAULT_MODEL
        )

    def create_topic_mindmap(self, topic: str, language: str = "english") -> dict:
        language_name = SahayakConfig.LANGUAGES.get(language.lower(), "English")

        prompt = (
            f"You are an educational assistant helping teachers explain the concept of **{topic}** using a clean, classroom-friendly mind map. "
            f"Generate a mind map in {language_name} with no more than 3 levels of depth and 3–4 items per level.\n\n"
            "Use this format exactly:\n"
            "**CENTRAL TOPIC: Photosynthesis**\n"
            "**MAIN BRANCHES (Level 1):**\n"
            "Branch 1: Reactants and Products\n"
            "  ├── Sub-branch 1.1: Reactants\n"
            "  │   └── 1.1.1: Water (H₂O), CO₂\n"
            "  └── Sub-branch 1.2: Products\n"
            "      └── 1.2.1: Glucose, Oxygen (O₂)\n"
            "Branch 2: Process Stages\n"
            "  ├── Sub-branch 2.1: Light Reaction\n"
            "  │   └── 2.1.1: ATP & NADPH formation\n"
            "  └── Sub-branch 2.2: Calvin Cycle\n"
            "      └── 2.2.1: Glucose synthesis\n"
            "Branch 3: Importance\n"
            "  ├── Sub-branch 3.1: Oxygen supply\n"
            "  └── Sub-branch 3.2: Basis of food chain\n\n"
            "Only return the mind map structure in this format. Do not add extra text, explanations, or headings."
        )

        response = self._make_request(prompt)

        return {
            "topic": topic,
            "language": language_name,
            "mindmap_structure": response
        }
    

    def generate_mindmap(self, topic: str, language: str = "english", **kwargs) -> dict:
        output = self.create_topic_mindmap(topic, language)
        
        # Save visual and text
        img_path = visualize_mindmap_with_networkx(output["mindmap_structure"], topic)
        txt_path = save_mindmap_text(output["mindmap_structure"], topic)

        # Include in output
        output["image_path"] = img_path
        output["text_path"] = txt_path

        return output
