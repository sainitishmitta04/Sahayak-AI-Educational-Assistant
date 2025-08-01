import os

def save_story_text(story_text: str, topic: str) -> str:
    folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "content_data")
    os.makedirs(folder, exist_ok=True)
    filename = f"story_{topic.lower().replace(' ', '_')}.txt"
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(story_text)
    return path

def save_explanation_text(explanation_text: str, concept: str) -> str:
    folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "content_data")
    os.makedirs(folder, exist_ok=True)
    filename = f"explanation_{concept.lower().replace(' ', '_')}.txt"
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(explanation_text)
    return path
