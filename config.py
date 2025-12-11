import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")  # Optional - for image hosting

# Validate that all required keys are present
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
if not ZAPIER_WEBHOOK_URL:
    raise ValueError("ZAPIER_WEBHOOK_URL not found in environment variables")
if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN not found in environment variables")

# ImgBB is optional
if not IMGBB_API_KEY:
    print("⚠️  IMGBB_API_KEY not found - text overlay images won't be uploaded")
    print("   Get free API key at: https://api.imgbb.com/")
else:
    print("✓ ImgBB API key found - branded images will be uploaded")

print("✓ All required API keys loaded successfully")