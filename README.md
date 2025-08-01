# Sahayak

# Sahayak - Educational AI Assistant

Sahayak is a comprehensive AI-powered educational assistant platform that provides various learning and teaching tools through specialized AI agents. The platform is designed to support both students and educators with features ranging from content generation to interactive learning experiences.

## Features

- **Content Generation**: Creates educational content and explanations
- **Audio Assessment**: Evaluates pronunciation and reading skills
- **Braille Assistant**: Provides braille-related assistance
- **Doubt Assistant**: Answers academic questions and clarifies concepts
- **Drawing Assistant**: Helps create and explain educational diagrams
- **Game Planner**: Creates educational games and activities
- **Lesson Planner**: Generates structured lesson plans
- **Mind Map Generator**: Creates visual concept maps
- **Video Analysis**: Processes and analyzes educational videos
- **Vision Assistant**: Handles image-based learning materials

## Project Structure


```
Final-Sahayak/
├── agents/              # AI agent implementations
├── app.py              # Main Streamlit application
├── config/             # Configuration files
├── data/               # Data storage
│   ├── audio/         # Audio files and assessments
│   ├── content_data/  # Generated content
│   ├── drawings/      # Drawing instructions
│   ├── images/        # Image resources
│   ├── mindmap_data/  # Generated mindmaps
│   └── videos/        # Video resources
├── notebooks/          # Testing notebooks
└── utils/             # Utility functions
```

## Prerequisites

- Python 3.11+
- Streamlit
- Required API keys (Gemini)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Final-Sahayak.git
cd Final-Sahayak
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory and add:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Access the web interface through your browser at `http://localhost:8501`

## Features in Detail

### Content Generation
- Creates educational content
- Generates explanations and stories
- Produces worksheets and exercises

### Audio Assessment
- Evaluates pronunciation
- Assesses reading skills
- Provides feedback on speech patterns

### Braille Assistant
- Assists with braille translation
- Provides braille learning resources

### Doubt Assistant
- Answers academic questions
- Provides detailed explanations
- Helps with problem-solving

### Drawing Assistant
- Creates educational diagrams
- Provides step-by-step drawing instructions
- Explains visual concepts

### Game Planner
- Designs educational games
- Creates interactive learning activities
- Develops engaging exercises

### Lesson Planner
- Generates structured lesson plans
- Creates daily and weekly schedules
- Organizes educational content

### Mind Map Generator
- Creates visual concept maps
- Organizes information hierarchically
- Helps understand relationships between concepts

### Video Analysis
- Processes educational videos
- Extracts key information
- Provides video-based learning support

### Vision Assistant
- Analyzes educational images
- Processes visual learning materials
- Provides image-based explanations

## Docker Support

The project includes Docker support for easy deployment. To run using Docker:

```bash
docker build -t sahayak .
docker run -p 8501:8501 sahayak
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the license included in the repository.




