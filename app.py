import streamlit as st
import os
from utils.setup_env import configure_environment
import time
from config.sahayak_config import SahayakConfig
import base64 # Added for base64 encoding

# ⚙️ Init Streamlit with custom config
st.set_page_config(
    page_title="Sahayak - AI Teaching Assistant", 
    layout="wide",
    page_icon="📚",
    initial_sidebar_state="expanded"
)

from agents.agent_manager import AgentManager
from agents.agent_router import AgentRouter, AgentType, RouteIntent
from agents.rag_agent import RAGAgent
from agents.video_agent import VideoAgent  # Add this import

# ⚙️ Configure environment
configure_environment()

# Initialize session state variables
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.rag_agent = RAGAgent()
    st.session_state.video_agent = VideoAgent()  # Add this line
    st.session_state.uploaded_files = []
    st.session_state.documents_processed = False
    
    # Initialize language preference in RAG agent's context
    st.session_state.rag_agent.context = {
        'language': 'english',  # default language
        'grade_level': 5,
        'context': 'rural'
    }
    st.session_state.current_game = None
    st.session_state.current_difficulty = 'medium'
    st.session_state.show_answer = False
    st.session_state.language = 'english'

# ⚙️ Custom CSS for beautiful styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Main container styling */
    .main {
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Custom header styling */
    .custom-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .custom-header h1 {
        color: white;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .custom-header p {
        color: rgba(255, 255, 255, 0.9);
        font-family: 'Poppins', sans-serif;
        font-size: 1.2rem;
        margin-bottom: 0;
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
        text-align: center;
    }
    
    .feature-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.3rem;
        color: #333;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-family: 'Poppins', sans-serif;
        color: #666;
        text-align: center;
        line-height: 1.6;
    }
    
    /* Input styling */
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        font-family: 'Poppins', sans-serif;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        margin: 1rem;
        padding: 1rem;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        border-radius: 15px;
        border-left: 5px solid #28a745;
    }
    
    .stError {
        border-radius: 15px;
        border-left: 5px solid #dc3545;
    }
    
    /* Progress indicator */
    .progress-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Floating particles background */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        animation: float 15s infinite linear;
    }
    
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); }
        100% { transform: translateY(-100vh) rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# 🎨 Custom header with animation
st.markdown("""
<div class="custom-header">
    <h1>🎓 SAHAYAK</h1>
    <p>Your Intelligent AI Teaching Assistant</p>
</div>
""", unsafe_allow_html=True)



# 🌟 Feature showcase section
st.markdown("## ✨ What Can Sahayak Do For You?")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">Smart Learning</div>
        <div class="feature-desc">AI-powered personalized learning experiences tailored to your needs</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🎮</div>
        <div class="feature-title">Educational Games</div>
        <div class="feature-desc">Play and learn with interactive games like Sudoku</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <div class="feature-title">Content Creation</div>
        <div class="feature-desc">Generate worksheets, stories, and educational content automatically</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Smart Search</div>
        <div class="feature-desc">Search through your documents and get context-aware responses</div>
    </div>
    """, unsafe_allow_html=True)

# 🔁 Init Agent Manager + Router (cached)
@st.cache_resource
def initialize_sahayak():
    return AgentManager(), AgentRouter()

agent_manager, agent_router = initialize_sahayak()

# Create sidebar for global settings
with st.sidebar:
    st.markdown("### 🌍 Language Settings")
    
    # Create a list of language options with native names
    language_options = {f"{lang_info['name']} ({lang_info['native']})": code 
                       for code, lang_info in SahayakConfig.LANGUAGES.items()}
    
    # Language selector
    selected_language_display = st.selectbox(
        "Select your preferred language:",
        options=list(language_options.keys()),
        index=0
    )
    
    # Update session state with selected language code
    st.session_state.language = language_options[selected_language_display]
    
    # Update RAG agent's context with new language
    if hasattr(st.session_state, 'rag_agent'):
        st.session_state.rag_agent.context['language'] = st.session_state.language

# Create tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Anything", "📚 Search Documents", "🎮 Educational Games", "🎥 Educational Videos"])

with tab1:
    st.markdown("### 💬 Ask Sahayak Anything")
    
    # Image Upload Section for general queries
    st.markdown("#### 📷 Upload Image (Optional)")
    uploaded_file = st.file_uploader(
        "Upload an image to extract text or analyze",
        type=["png", "jpg", "jpeg"],
        help="Upload an image if you want to extract text or analyze its content",
        key="general_image_upload"
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        st.success("✅ Image uploaded successfully!")
    
    # General query input
    general_query = st.text_area(
        "Ask any question:", 
        height=100,
        placeholder="Type your question here... Ask me anything about any subject!",
        help="Ask questions about any topic - science, math, history, etc."
    )
    
    # Submit button for general queries
    if st.button("🤔 Ask Sahayak", use_container_width=True):
        if not general_query and not uploaded_file:
            st.warning("⚠️ Please enter a question or upload an image!")
        else:
            # Show processing indicator
            st.markdown("""
            <div class="progress-container">
                <div class="pulse">🤔 Thinking...</div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                progress_bar.progress(30)
                status_text.text("🔍 Analyzing your request...")
                time.sleep(0.5)

                # Handle image processing if image is uploaded
                context = {
                    'language': st.session_state.language,
                    'grade_level': 5,
                    'context': 'rural'
                }
                
                if uploaded_file:
                    # Create images directory if it doesn't exist
                    image_dir = os.path.join("data", "images")
                    os.makedirs(image_dir, exist_ok=True)
                    
                    # Save the image
                    image_path = os.path.join(image_dir, uploaded_file.name)
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Add vision context
                    context.update({
                        'agent_type': AgentType.VISION_AGENT.value,
                        'task_type': 'extract_text',
                        'image_path': image_path,
                        'content': general_query if general_query else "Extract text from this image"
                    })

                progress_bar.progress(60)
                status_text.text("🧠 Generating response...")
                time.sleep(0.5)

                # Process the request
                response = agent_manager.process_request(general_query, context=context)

                progress_bar.progress(100)
                status_text.text("✅ Response ready!")
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

                if response.success:
                    st.success(f"✅ Response from **{response.agent_name}**")
                    
                    data = response.data if isinstance(response.data, dict) else {"raw_output": response.data}
                    
                    # Display results
                    st.markdown("### 📋 Response")
                    if isinstance(data, dict):
                        # Handle mindmap specifically
                        if "mindmap_structure" in data and "image_path" in data:
                            st.markdown("#### 🗺️ Mind Map")
                            # Display the image if it exists
                            if os.path.exists(data["image_path"]):
                                st.image(data["image_path"], use_container_width=True)
                            
                            # Display the structure in a collapsible section
                            with st.expander("📋 View Mind Map Structure"):
                                st.text(data["mindmap_structure"])
                            
                            # If there's a text file, show its contents
                            if "text_path" in data and os.path.exists(data["text_path"]):
                                with st.expander("📝 View Detailed Description"):
                                    with open(data["text_path"], 'r') as f:
                                        st.text(f.read())
                        
                        # Handle extracted text specifically
                        elif "extracted_text" in data:
                            st.markdown("#### 📝 Extracted Text")
                            st.text_area("", data["extracted_text"], height=200)
                            if "confidence" in data:
                                st.info(f"📊 Extraction confidence: {data['confidence']:.2%}")
                        
                        # Handle other types of responses
                        else:
                            for key, value in data.items():
                                if key not in ['status', 'timestamp', 'agent']:
                                    if key == 'topic':
                                        st.markdown(f"#### 📌 {value}")
                                    elif key == 'language':
                                        st.markdown(f"🌍 Language: {value['name']} ({value['native']})")
                                    elif key not in ['image_path', 'text_path']:  # Skip file paths
                                        st.markdown(f"**{key}:** {value}")
                    else:
                        st.markdown(data)
                        
                        # Clean up image file if it was created
                        if uploaded_file and os.path.exists(image_path):
                            os.remove(image_path)
                else:
                    st.error(f"❌ Error: {response.error}")

            except Exception as e:
                st.error(f"🚨 **Unexpected error:** {str(e)}")
                st.markdown("💡 **Tip:** Please try rephrasing your question.")

with tab2:
    st.markdown("### 💬 Ask Questions About Your Documents")
    
    # Document Upload Section
    st.markdown("#### 📎 Upload Documents")
    uploaded_docs = st.file_uploader(
        "Upload PDF, Word, or text documents",
        type=['txt', 'pdf', 'docx'],
        accept_multiple_files=True,
        help="Upload documents you want to ask questions about"
    )
    
    if uploaded_docs:
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join("data", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Check if we have new documents
        current_files = [doc.name for doc in uploaded_docs]
        previous_files = [doc.name for doc in st.session_state.uploaded_files]
        
        if current_files != previous_files:
            # Clear uploads directory
            for file in os.listdir(uploads_dir):
                os.remove(os.path.join(uploads_dir, file))
            
            # Save new documents
            for doc in uploaded_docs:
                file_path = os.path.join(uploads_dir, doc.name)
                with open(file_path, "wb") as f:
                    f.write(doc.getvalue())
                st.info(f"📄 Uploaded: {doc.name}")
            
            # Update session state
            st.session_state.uploaded_files = uploaded_docs
            st.session_state.documents_processed = False
            
            # Process documents
            with st.spinner("Processing documents..."):
                result = st.session_state.rag_agent.initialize_knowledge_base(uploads_dir)
                if result['status'] == 'success':
                    st.success("✅ Documents processed successfully")
                    st.session_state.documents_processed = True
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        # Display currently uploaded files
        st.markdown("#### 📑 Current Documents")
        for doc in uploaded_docs:
            st.text(f"• {doc.name}")
    
    # Query input for documents
    doc_query = st.text_area(
        "Ask a question about your documents:", 
        height=100,
        placeholder="What would you like to know about the uploaded documents?",
        help="Ask any question about the content of your uploaded documents"
    )
    
    # Submit button for document search
    if st.button("🔍 Search Documents", use_container_width=True):
        if not st.session_state.uploaded_files:
            st.warning("⚠️ Please upload some documents first!")
        elif not st.session_state.documents_processed:
            st.warning("⚠️ Please wait for documents to be processed!")
        elif not doc_query:
            st.warning("⚠️ Please enter a question!")
        else:
            # Show processing indicator
            st.markdown("""
            <div class="progress-container">
                <div class="pulse">🤔 Searching through documents...</div>
            </div>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                progress_bar.progress(30)
                status_text.text("🔍 Processing your question...")
                time.sleep(0.5)

                progress_bar.progress(60)
                status_text.text("📚 Searching through documents...")
                time.sleep(0.5)

                # Add language to the query context
                response = st.session_state.rag_agent.generate_response(
                    query=doc_query,
                    num_chunks=3  # You can adjust this value based on your needs
                )

                progress_bar.progress(100)
                status_text.text("✅ Search complete!")
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()

                if response['status'] == 'success':
                    st.success("✅ Found relevant information")
                    
                    # Display results
                    st.markdown("### 🔍 Search Results")
                    st.markdown(response['response'])
                    
                    if 'sources' in response:
                        st.markdown("### 📚 Sources")
                        for source in response['sources']:
                            st.markdown(f"• {source}")
                else:
                    st.error(f"❌ Error: {response.get('error', 'Unknown error')}")

            except Exception as e:
                st.error(f"🚨 **Unexpected error:** {str(e)}")
                st.markdown("💡 **Tip:** Please try again or check if your documents were uploaded correctly.")

with tab3:
    st.markdown("### 🎮 Educational Games")
    
    # Game selector
    game_type = st.selectbox(
        "Select game:",
        ["Sudoku", "Riddles"],
        key="game_selector"
    )
    
    # Difficulty selector - adjust options based on game type
    difficulties = ["basic", "medium", "hard"] if game_type == "Sudoku" else ["basic", "medium"]
    difficulty = st.selectbox(
        "Select difficulty level:",
        difficulties,
        index=0,
        key="difficulty_selector"
    )
    
    # Create two columns for the game display
    game_col, control_col = st.columns([3, 1])
    
    with control_col:
        # Show new game button
        if st.button("🎲 Show New Game"):
            st.session_state.show_answer = False
            st.session_state.current_difficulty = difficulty
            response = agent_manager.process_request(
                "show game",
                context={
                    "game_type": game_type.lower(),
                    "difficulty": difficulty,
                    "language": st.session_state.language
                }
            )
            
            if response.success and response.data.get('success', False):
                st.session_state.current_game = response.data
                st.success(f"✨ New {game_type} loaded!")
            else:
                error_msg = response.data.get('error', f'Failed to load {game_type}') if response.success else f'Failed to load {game_type}'
                st.error(error_msg)
        
        # Show/Hide answer button
        if st.session_state.current_game:
            if st.button("👀 Show/Hide Answer"):
                st.session_state.show_answer = not st.session_state.show_answer
    
    with game_col:
        if st.session_state.current_game:
            # Show game
            st.markdown(f"#### 🎯 Current {game_type}")
            puzzle_path = st.session_state.current_game.get('puzzle_path')
            if puzzle_path and os.path.exists(puzzle_path):
                st.image(puzzle_path, caption=f"{st.session_state.current_difficulty.title()} Difficulty {game_type}", use_container_width=True)
            
            # Show answer if requested
            if st.session_state.show_answer:
                st.markdown("#### ✅ Solution")
                response = agent_manager.process_request(
                    "show game answer",
                    context={
                        "game_type": game_type.lower(),
                        "difficulty": st.session_state.current_difficulty,
                        "language": st.session_state.language,
                        "request_type": "answer"
                    }
                )
                
                if response.success and response.data.get('success', False):
                    answer_path = response.data.get('answer_path')
                    if answer_path and os.path.exists(answer_path):
                        st.image(answer_path, caption="Solution", use_container_width=True)
                    else:
                        st.error("Answer image not found")
                else:
                    st.error("Failed to load answer")
        else:
            st.info("👆 Select a game and difficulty, then click 'Show New Game' to start!")

with tab4:
    st.markdown("### 🎥 Educational Videos with Sign Language Support")
    
    # Text input for video query
    video_query = st.text_area(
        "Enter your question or topic:",
        placeholder="Example: Show me a video about speed, or explain square concept, or help me with trigonometry...",
        help="Enter your question or topic to find relevant educational videos",
        key="video_query"
    )
    
    # Show video button
    if st.button("🎥 Show Video/Answer", use_container_width=True):
        if not video_query:
            st.warning("⚠️ Please enter a question or topic!")
        else:
            with st.spinner("Processing your request..."):
                # Convert query to lowercase for case-insensitive matching
                query_lower = video_query.lower()
                
                # Define video mapping and keywords
                video_mapping = {
                    'speed': {
                        'file': 'speed.mp4',
                        'keywords': ['speed', 'velocity', 'motion', 'fast', 'slow', 'movement']
                    },
                    'square': {
                        'file': 'square.mp4',
                        'keywords': ['square', 'rectangle', 'quadrilateral', 'four sides', 'geometry']
                    },
                    'trigonometry': {
                        'file': 'Trignometry.mp4',
                        'keywords': ['trigonometry', 'trignometry', 'sine', 'cosine', 'triangle', 'angles', 'trigonometric']
                    }
                }
                
                # Find matching video based on keywords
                matched_video = None
                for video_type, info in video_mapping.items():
                    if any(keyword in query_lower for keyword in info["keywords"]):
                        matched_video = {
                            "type": video_type,
                            "file": info["file"]
                        }
                        break
                
                if matched_video:
                    video_path = os.path.join("data", "videos", matched_video["file"])
                    if os.path.exists(video_path):
                        try:
                            # Check file size
                            file_size = os.path.getsize(video_path)
                            if file_size == 0:
                                st.error("⚠️ Video file exists but is empty (0 bytes). Please ensure the video file is properly uploaded.")
                            else:
                                # Get video information from VideoAgent
                                video_response = st.session_state.video_agent.get_video(
                                    concept=matched_video['type'],
                                    grade=6  # Default grade level
                                )
                                
                                if video_response['success']:
                                    # Display video information
                                    st.info(f"""
                                    📽️ {video_response['title']}
                                    
                                    {video_response['description']}
                                    
                                    📚 Topics covered:
                                    {' • '.join(video_response['topics'])}
                                    """)
                                    
                                    # Read video file in chunks
                                    try:
                                        with open(video_path, 'rb') as video_file:
                                            video_bytes = video_file.read()
                                            if len(video_bytes) > 0:
                                                st.video(video_bytes)
                                            else:
                                                st.error("⚠️ Could not read video data from file.")
                                    except Exception as read_error:
                                        st.error(f"⚠️ Error reading video file: {str(read_error)}")
                                        st.info("Please check if the video file is properly formatted and not corrupted.")
                                else:
                                    st.error(f"⚠️ Error getting video information: {video_response.get('error', 'Unknown error')}")
                            
                        except Exception as e:
                            st.error(f"⚠️ Error processing video: {str(e)}")
                            st.info("""
                            Troubleshooting tips:
                            1. Ensure video file exists in data/videos folder
                            2. Check if video file is properly formatted (MP4)
                            3. Verify file permissions
                            """)
                    else:
                        st.error(f"⚠️ Video file not found: {video_path}")
                        st.info("Please ensure the video file is present in the data/videos directory.")
                else:
                    # Show thinking animation for unmatched queries
                    st.markdown("""
                    <div style="display: flex; justify-content: center; margin: 20px 0;">
                        <svg width="120" height="120" viewBox="0 0 120 120">
                            <!-- Outer rotating circle -->
                            <circle cx="60" cy="60" r="50" stroke="#4CAF50" stroke-width="8" fill="none" opacity="0.3">
                                <animate attributeName="stroke-dasharray" 
                                    values="0 314.1;314.1 0;0 314.1" 
                                    dur="3s" 
                                    repeatCount="indefinite"/>
                                <animate attributeName="stroke-dashoffset" 
                                    values="0;-314.1;-628.2" 
                                    dur="3s" 
                                    repeatCount="indefinite"/>
                            </circle>
                        </svg>
                    </div>
                    <div style="text-align: center; color: #4CAF50; font-size: 1.2em; margin-top: 10px;">
                        🤔 Processing your request...
                    </div>
                    <div style="text-align: center; color: #666; font-size: 1em; margin-top: 5px;">
                        Analyzing query and searching for relevant content
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(1.5)  # Simulate processing time

# 🎨 Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.8);">
    <h3 style="color: rgba(255,255,255,0.9); margin-bottom: 1rem;">Sahayak</h3>
    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">Empowering Education Through Technology</p>
    <div style="margin: 1.5rem 0; border-top: 1px solid rgba(255,255,255,0.1); border-bottom: 1px solid rgba(255,255,255,0.1); padding: 1rem 0;">
        <p style="font-size: 1.2rem; font-weight: 500;">Team Activation-Relu</p>
        <p style="font-size: 0.9rem; opacity: 0.8;">Powered by Google Agentic AI</p>
    </div>
</div>
""", unsafe_allow_html=True)