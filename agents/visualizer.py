import os
import re
import matplotlib.pyplot as plt
import networkx as nx


def sanitize_filename(name: str) -> str:
    """Remove characters invalid in file names across operating systems"""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    return name.strip().replace(' ', '_')


def save_mindmap_text(text, topic, folder=None):
    # Ensure consistent absolute path to project-root-level data/mindmap_data
    if folder is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder = os.path.join(root_dir, "data", "mindmap_data")

    os.makedirs(folder, exist_ok=True)
    safe_topic = sanitize_filename(topic.lower())
    filename = f"mindmap_{safe_topic}.txt"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    return filepath


def parse_mindmap_to_graph(structure_text):
    G = nx.DiGraph()
    current_branch = None

    for line in structure_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("**CENTRAL TOPIC"):
            topic = line.split("**")[-2].split(":")[-1].strip()
            G.add_node(topic, level=0)
            root = topic
        elif line.startswith("Branch"):
            parts = line.split(":")
            current_branch = parts[1].strip()
            G.add_node(current_branch, level=1)
            G.add_edge(root, current_branch)
        elif line.startswith("├──") or line.startswith("└──"):
            child = line.split(":")[-1].strip()
            if current_branch:
                G.add_node(child, level=2)
                G.add_edge(current_branch, child)

    return G


def visualize_mindmap_with_networkx(structure_text, topic, folder=None):
    # Ensure consistent absolute path to project-root-level data/mindmap_data
    if folder is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder = os.path.join(root_dir, "data", "mindmap_data")

    os.makedirs(folder, exist_ok=True)

    G = parse_mindmap_to_graph(structure_text)

    # Layout
    pos = nx.multipartite_layout(G, subset_key="level")

    # Node styling
    color_map = []
    for node in G:
        level = G.nodes[node].get("level", 3)
        if level == 0:
            color_map.append("gold")
        elif level == 1:
            color_map.append("skyblue")
        elif level == 2:
            color_map.append("lightgreen")
        else:
            color_map.append("lightgray")

    # Draw
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, arrows=True,
            node_color=color_map, node_size=2500,
            font_size=10, font_weight="bold", edge_color="gray")

    plt.title(f"Mind Map: {topic}", fontsize=14)

    # Save
    safe_topic = sanitize_filename(topic.lower())
    image_filename = f"mindmap_{safe_topic}.png"
    image_path = os.path.join(folder, image_filename)
    plt.savefig(image_path, bbox_inches="tight")  # Ensures layout fits
    plt.close()

    return image_path
