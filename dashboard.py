import streamlit as st
import os
from main import SocialMediaPipelineAgent


# -----------------------------------------------------------
# MAIN DASHBOARD CONTENT
# -----------------------------------------------------------
def main_authenticated():
    """Main dashboard content (called from auth.py navigation)"""
    
    # Page header
    st.title("📝 Campaign Creator")
    
    st.markdown("""
    Create and manage social media campaigns with AI-powered content generation.
    """)
    
    # Initialize agent
    agent = SocialMediaPipelineAgent()

    # -----------------------------
    # USER INPUTS
    # -----------------------------
    st.subheader("📝 Campaign Settings")
    
    topic = st.text_input(
        "Enter your campaign topic:",
        value="AI in Education UAE",
        help="The main topic/theme for your social media content"
    )

    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        use_ai_images = st.checkbox(
            "🎨 Generate AI Image",
            value=False,
            help="Generate ONE branded image using AI"
        )
    
    with col2:
        use_custom = st.checkbox(
            "🖼️ Use My Own Design",
            value=False,
            help="Upload your own custom image"
        )
    
    with col3:
        # Check if user is admin
        if st.session_state.get('user_role') == "admin":
            post_to_instagram = st.checkbox(
                "📤 Post to Instagram",
                value=False,
                help="Automatically publish to Instagram via Zapier"
            )
        else:
            st.info("📤 Instagram posting is admin-only")
            post_to_instagram = False
    
    # Text overlay settings
    st.markdown("---")
    st.subheader("✍️ Image Text Overlay")
    
    col_text1, col_text2, col_text3 = st.columns(3)
    
    with col_text1:
        brand_text = st.text_input(
            "Brand Text to Display on Image",
            value="Experts Group FZE",
            help="This text will appear on your generated image"
        )
    
    with col_text2:
        text_size = st.slider(
            "Text Size",
            min_value=30,
            max_value=150,
            value=80,
            step=10,
            help="Adjust the size of the text overlay (default: 80)"
        )
    
    with col_text3:
        add_text_overlay = st.checkbox(
            "Add Text Overlay to Image",
            value=True,
            help="Uncheck to generate image without text overlay"
        )
    
    # Custom image prompt settings
    st.markdown("---")
    st.subheader("🎨 Image Generation Control")
    
    use_custom_prompt = st.checkbox(
        "Use Custom Image Prompt",
        value=False,
        help="Enable to write your own detailed prompt for image generation"
    )
    
    custom_image_prompt = None
    if use_custom_prompt:
        st.markdown("**Custom Image Generation Prompt:**")
        custom_image_prompt = st.text_area(
            "Image Prompt Template",
            value="""Professional product photography showing [PRODUCTS].
Style: high-end commercial, studio lighting, luxury brand aesthetic.
Composition: [DESCRIBE LAYOUT]
Products visible: [LIST PRODUCTS]
Setting: elegant, modern, UAE market
Lighting: soft, professional, golden hour glow
Mood: aspirational, premium quality
Focus: products as hero, clean background
NO TEXT in image.""",
            height=200,
            help="Write a detailed prompt. Use [PRODUCTS], [STYLE], etc. as placeholders"
        )
        
        st.info("💡 **Tip:** Be specific about products, lighting, and composition for best results!")

    # Prevent both options from being selected
    if use_ai_images and use_custom:
        st.warning("⚠️ Please choose either AI-generated image OR custom upload, not both.")
        st.stop()

    custom_image_path = None

    # Custom image upload section
    if use_custom:
        st.markdown("---")
        st.subheader("📤 Upload Custom Image")
        
        uploaded_file = st.file_uploader(
            "Upload Your Custom Image",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG"
        )
        
        if uploaded_file:
            # Create images directory if it doesn't exist
            if not os.path.exists("images"):
                os.makedirs("images")

            # Save uploaded image locally
            custom_image_path = os.path.join("images", uploaded_file.name)

            with open(custom_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"✓ Image uploaded successfully: {uploaded_file.name}")
            
            # Try to upload to ImgBB for web URL
            try:
                from tools import upload_to_imgbb
                
                with st.spinner("Uploading to web hosting..."):
                    web_url = upload_to_imgbb(custom_image_path)
                    
                if web_url:
                    st.success(f"✓ Image hosted online: {web_url}")
                    # Use the web URL instead of local path
                    custom_image_path = web_url
                else:
                    st.warning("⚠️ Could not upload to web. Image will be saved locally only.")
                    st.info("💡 To post custom images to Instagram, add IMGBB_API_KEY to your .env file")
                    
            except Exception as e:
                st.warning(f"⚠️ Could not upload to web: {str(e)}")
            
            st.image(custom_image_path, caption="Uploaded Custom Image")

    # -----------------------------
    # ACTION BUTTON
    # -----------------------------
    st.markdown("---")
    
    if st.button("🚀 Run Campaign", type="primary", use_container_width=True):
        
        # Validation
        if not topic.strip():
            st.error("❌ Please enter a topic for your campaign.")
            st.stop()
        
        if use_custom and not custom_image_path:
            st.error("❌ Please upload a custom image or uncheck 'Use My Own Design'.")
            st.stop()

        # Show progress
        with st.spinner("🔄 Running campaign pipeline..."):
            try:
                result = agent.run(
                    topic=topic,
                    generate_image=use_ai_images,
                    use_custom_image=use_custom,
                    custom_image_path=custom_image_path,
                    push_to_zap=post_to_instagram,
                    brand_text=brand_text if add_text_overlay else None,
                    text_size=text_size
                )

                st.success("✅ Campaign Completed Successfully!")
                
                # -----------------------------
                # DISPLAY RESULTS
                # -----------------------------
                st.markdown("---")
                st.header("📊 Results")
                
                # Posts
                st.subheader("📝 Generated Posts")
                for i, post in enumerate(result["posts"], 1):
                    with st.expander(f"Post {i}: {post['title']}", expanded=(i == 1)):
                        st.write(f"**Caption:**")
                        st.write(post["caption"])
                        st.write(f"**Hashtags:** {post['hashtags']}")
                
                # Image - SINGLE IMAGE DISPLAY
                if result["images"]["image_urls"]:
                    st.subheader("🎨 Generated Image")
                    # Get the first (and only) image
                    img_url = result["images"]["image_urls"][0] if len(result["images"]["image_urls"]) > 0 else None
                    if img_url:
                        st.image(img_url, caption="Your Generated Image", use_container_width=True)
                        
                        # Add download/view options
                        st.markdown(f"""
                        **📥 Image URL:**
                        ```text
                        {img_url}
                        ```
                        """)
                        
                        # Button to open image in new tab
                        st.markdown(f'<a href="{img_url}" target="_blank"><button style="background-color:#FF4B4B;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Open Image in New Tab</button></a>', unsafe_allow_html=True)
                
                # Reel Script
                st.subheader("🎬 Reel Script")
                reel = result.get("reel_script", {}).get("reel_script", result.get("reel_script", {}))
                
                if isinstance(reel, dict):
                    st.write(f"**Hook:** {reel.get('hook', 'N/A')}")
                    
                    if "scenes" in reel:
                        st.write("**Scenes:**")
                        for scene in reel["scenes"]:
                            st.write(f"- Scene {scene.get('scene', 'N/A')}: {scene.get('description', 'N/A')}")
                    
                    st.write(f"**CTA:** {reel.get('cta', 'N/A')}")
                elif isinstance(reel, str):
                    st.write(reel)
                
                # Zapier Status
                if "zapier_status" in result:
                    st.subheader("📤 Zapier Publishing Status")
                    status = result["zapier_status"]
                    
                    if status.get("status") == 200:
                        st.success("✅ Successfully published to Instagram via Zapier!")
                    else:
                        st.warning(f"⚠️ Zapier status: {status.get('status', 'Unknown')}")
                    
                    with st.expander("View Zapier Details"):
                        st.json(status)
                
                # Full JSON output
                with st.expander("🔍 View Full JSON Output"):
                    st.json(result)

            except ValueError as e:
                st.error(f"❌ Validation Error: {e}")
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
                st.exception(e)


# -----------------------------------------------------------
# LEGACY MAIN FUNCTION (for direct running)
# -----------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Social Media Agent",
        layout="wide",
        page_icon="📢"
    )
    
    # For backward compatibility
    main_authenticated()


if __name__ == "__main__":
    main()