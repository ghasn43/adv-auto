from main import SocialMediaPipelineAgent

# -------------------------------
# INITIALIZE AGENT
# -------------------------------
agent = SocialMediaPipelineAgent()

# -------------------------------
# USER SETTINGS (EDIT FREELY)
# -------------------------------

TOPIC = "AI in Education UAE"

GENERATE_IMAGE = True          # True → generate AI images
USE_CUSTOM_IMAGE = False       # True → use your own design
CUSTOM_IMAGE_PATH = "images/mydesign.jpg"  # Used only if USE_CUSTOM_IMAGE=True

PUSH_TO_ZAPIER = True          # True → send to Instagram via Zapier

# Text Overlay Settings
BRAND_TEXT = "Experts Group FZE"  # Text to display on images
TEXT_SIZE = 80                    # Font size (30-150)
ADD_TEXT_OVERLAY = True           # True → add text, False → clean images

# Custom Image Prompt (Optional)
USE_CUSTOM_PROMPT = False
CUSTOM_IMAGE_PROMPT = """
Professional product photography.
Products: [describe your products]
Style: [your style preferences]
Lighting: [lighting description]
Composition: [layout description]
NO TEXT in image.
"""

# -------------------------------
# VALIDATION
# -------------------------------
if USE_CUSTOM_IMAGE and GENERATE_IMAGE:
    print("\n⚠️ Warning: Both USE_CUSTOM_IMAGE and GENERATE_IMAGE are True.")
    print("   Only USE_CUSTOM_IMAGE will be used.\n")

if USE_CUSTOM_IMAGE:
    import os
    if not os.path.exists(CUSTOM_IMAGE_PATH):
        print(f"\n❌ Error: Custom image not found at: {CUSTOM_IMAGE_PATH}")
        print("   Please check the path or set USE_CUSTOM_IMAGE=False\n")
        exit(1)

# -------------------------------
# RUN THE PIPELINE
# -------------------------------
if __name__ == "__main__":
    try:
        result = agent.run(
            topic=TOPIC,
            generate_image=GENERATE_IMAGE,
            use_custom_image=USE_CUSTOM_IMAGE,
            custom_image_path=CUSTOM_IMAGE_PATH,
            push_to_zap=PUSH_TO_ZAPIER,
            brand_text=BRAND_TEXT if ADD_TEXT_OVERLAY else None,
            text_size=TEXT_SIZE,
            custom_image_prompt=CUSTOM_IMAGE_PROMPT if USE_CUSTOM_PROMPT else None
        )

        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"\n📌 Topic: {result['topic']}")
        print(f"📝 Posts: {len(result['posts'])}")
        print(f"🎨 Images: {len(result['images']['image_urls'])}")
        print(f"🎬 Reel Script: {'✓' if result.get('reel_script') else '✗'}")
        
        if result.get('zapier_status'):
            status = result['zapier_status'].get('status', 'Unknown')
            print(f"📤 Zapier: {status}")
        
        print("\n💾 Full result saved to JSON file")
        print("="*60 + "\n")

    except ValueError as e:
        print(f"\n❌ Validation Error: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}\n")
        import traceback
        traceback.print_exc()
        exit(1)