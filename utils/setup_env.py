import sys, os
import warnings
from dotenv import load_dotenv

def configure_environment():
    # Add root path
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_path not in sys.path:
        sys.path.append(root_path)

    # Suppress warnings
    warnings.filterwarnings("ignore")

    # Load .env variables
    load_dotenv()

    # Configure Google API (for Gemini / generative AI agents)
    google_api_key = "<API KEY>"

    if google_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            print("✅ Google Gemini API configured successfully")
        except Exception as e:
            print(f"❌ Failed to configure Gemini API: {e}")
    else:
        print("⚠️ GOOGLE_API_KEY not found in environment")
