from tools import (
    generate_posts,
    generate_image_prompts,
    generate_images,
    generate_reels_script,
    send_to_zapier,
    save_result_to_json
)


class SocialMediaPipelineAgent:
    """
    Main agent class that orchestrates the social media content generation pipeline.
    """

    def run(
        self,
        topic,
        generate_image=False,
        use_custom_image=False,
        custom_image_path=None,
        push_to_zap=False,
        brand_text="Experts Group FZE",
        text_size=80,
        custom_image_prompt=None
    ):
        """
        Run the complete social media content generation pipeline.
        
        Args:
            topic (str): The topic/theme for content generation
            generate_image (bool): Whether to generate AI images
            use_custom_image (bool): Whether to use a custom uploaded image
            custom_image_path (str): Path to custom image file
            push_to_zap (bool): Whether to send to Zapier for Instagram posting
            brand_text (str): Text to overlay on images (None = no overlay)
            text_size (int): Font size for text overlay (default: 80)
            custom_image_prompt (str): Custom prompt template for image generation (None = auto-generate)
            
        Returns:
            dict: Complete pipeline output including posts, images, scripts, etc.
        """
        
        print(f"\n{'='*60}")
        print(f"🚀 Starting Social Media Pipeline")
        print(f"{'='*60}")
        print(f"📌 Topic: {topic}")
        print(f"🎨 Generate AI Image: {generate_image}")
        print(f"🖼️  Use Custom Image: {use_custom_image}")
        print(f"📤 Push to Zapier: {push_to_zap}")
        print(f"{'='*60}\n")

        # Validate input
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")

        # ----------------------------
        # 1️⃣ Generate Text Posts
        # ----------------------------
        print("📝 Step 1: Generating text posts...")
        posts = generate_posts(topic)
        print(f"✓ Generated {len(posts['posts'])} posts\n")

        # ----------------------------
        # 2️⃣ Generate Image Prompts (always)
        # ----------------------------
        print("🎨 Step 2: Generating image prompts...")
        prompts = generate_image_prompts(posts, custom_prompt_template=custom_image_prompt)
        print(f"✓ Generated {len(prompts['image_prompts'])} prompts\n")

        # ----------------------------
        # 3️⃣ Generate Reels Script
        # ----------------------------
        print("🎬 Step 3: Generating reel script...")
        reel_script = generate_reels_script(topic)
        print("✓ Reel script generated\n")

        # ----------------------------
        # 4️⃣ Image Selection Logic - SINGLE IMAGE
        # ----------------------------
        print("🖼️  Step 4: Processing image...")
        
        if use_custom_image:
            # User provides own design
            if not custom_image_path:
                raise ValueError("Custom image path must be provided when use_custom_image=True")
            
            print(f"   Using custom image: {custom_image_path}")
            
            # Check if it's already a web URL or local file
            if custom_image_path.startswith("http://") or custom_image_path.startswith("https://"):
                # Already a web URL (uploaded via dashboard)
                images = {"image_urls": [custom_image_path]}
            else:
                # Local file - try to upload
                print(f"   ⚠️  Custom image is a local file, attempting to upload...")
                from tools import upload_to_imgbb
                
                web_url = upload_to_imgbb(custom_image_path)
                
                if web_url:
                    print(f"   ✓ Uploaded custom image: {web_url}")
                    images = {"image_urls": [web_url]}
                else:
                    print(f"   ⚠️  Could not upload custom image to web")
                    print(f"   ⚠️  Zapier won't be able to use this image")
                    images = {"image_urls": []}

        elif generate_image:
            # AI generates ONE branded image
            print("   Generating ONE perfect AI image...")
            images = generate_images(prompts, brand_text=brand_text, text_size=text_size)

        else:
            # No image at all
            print("   No image requested")
            images = {"image_urls": []}
        
        print(f"✓ Image processing complete ({len(images['image_urls'])} image)\n")

        # ----------------------------
        # 5️⃣ FINAL OUTPUT PACKAGE
        # ----------------------------
        print("📦 Step 5: Assembling output package...")
        output = {
            "topic": topic,
            "posts": posts["posts"],
            "image_prompts": prompts["image_prompts"],
            "reel_script": reel_script,
            "images": images,
        }
        print("✓ Output package ready\n")

        # ----------------------------
        # 6️⃣ Optional Zapier Publishing
        # ----------------------------
        if push_to_zap:
            print("📤 Step 6: Publishing to Instagram via Zapier...")
            try:
                zap_result = send_to_zapier(output)
                output["zapier_status"] = zap_result
                print("✓ Published to Zapier\n")
            except Exception as e:
                print(f"⚠️ Zapier publishing failed: {e}\n")
                output["zapier_status"] = {"status": "error", "error": str(e)}
        else:
            print("⏭️  Step 6: Skipping Zapier (not requested)\n")

        # ----------------------------
        # 7️⃣ Save a copy to JSON file
        # ----------------------------
        print("💾 Step 7: Saving results to file...")
        save_result_to_json(output)
        
        print(f"\n{'='*60}")
        print("✅ Pipeline completed successfully!")
        print(f"{'='*60}\n")

        return output