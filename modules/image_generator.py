import requests
import logging
import time
import os
import base64
import textwrap
import urllib3
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from rembg import remove
from config import Config

# Disable SSL warnings for corporate networks
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Generate and compose banner images using AI."""
    
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url
        # Use original banner dimensions from the background image
        self.banner_width = 600  # Original width
        self.banner_height = 350  # Original height
        self.image_quality = Config.IMAGE_QUALITY
        
    def generate_banners(self, tagline: str, theme_context: List[Dict]) -> List[str]:
        """Generate 6 banner variations (3 prompts x 2 images each)."""
        banners = []
        
        try:
            # Generate 3 different prompts based on context
            prompts = self._generate_image_prompts(theme_context)
            
            for prompt in prompts:
                # Generate 2 images per prompt
                for variation in range(2):
                    logger.info(f"Generating image for prompt: {prompt[:50]}...")
                    
                    # Generate AI image
                    ai_image = self._generate_ai_image(prompt, variation)
                    
                    if ai_image:
                        # Compose banner with background and tagline
                        banner_url = self._compose_banner(ai_image, tagline, len(banners))
                        if banner_url:
                            banners.append(banner_url)
                    
                    # Rate limiting
                    time.sleep(2)
            
            # Ensure we have 6 banners (use fallbacks if needed)
            while len(banners) < 6:
                banners.append(self._get_fallback_banner(tagline, len(banners)))
            
            return banners[:6]
            
        except Exception as e:
            logger.error(f"Error generating banners: {str(e)}")
            return [self._get_fallback_banner(tagline, i) for i in range(6)]
    
    def _generate_image_prompts(self, theme_context: List[Dict]) -> List[str]:
        """Generate diverse image prompts based on content with random gender and shirt colors."""
        # Define color array
        shirt_colors = ['yellow', 'green', 'black', 'blue', 'orange', 'red', 'pink']
        
        # Define gender options
        genders = ['man', 'woman']
        
        # Define snack/activity variations
        activities = [
            "holding a bowl of popcorn",
            "holding a bowl of nachos", 
            "holding a tv remote as if changing the channel"
        ]
        
        # Generate 3 prompts with different random combinations
        enhanced_prompts = []
        for i in range(3):
            # Randomly select gender and color for each prompt
            gender = random.choice(genders)
            shirt_color = random.choice(shirt_colors)
            activity = activities[i]  # Use different activity for each prompt
            
            # Build the base prompt with random selections
            base_prompt = (
                f"A young {gender} sitting while watching something on TV, with an expression of joy. "
                f"Their body language conveys engagement, sitting straight and facing directly forward. "
                f"They are {activity}. Their posture reflects interest. "
                f"Clothing is casual, such as a t-shirt or a sweater in {shirt_color} color—avoiding white color."
            )
            
            # Add background and quality specifications
            enhanced_prompt = (
                f"{base_prompt} "
                "There is only one person in the image, upper body visible above the waist, photographed against a pure white background (RGB 255,255,255) with absolutely no shadows, shading, gradients, or text. The background must be completely flat white with no visual distractions. "
                "The subject should have smooth, straight, or slightly wavy hair with a neat and natural appearance, ensuring a well-groomed look. Their facial features should be clearly visible with a natural and relaxed expression. "
                "All elements must be in sharp focus with high clarity, no motion blur, and distinct edges. The objects held should appear crisp, well-defined, and naturally integrated with the hands. Ensure a high level of detail in the textures of the objects, making them visually clear and easy to distinguish."
            )
            
            enhanced_prompts.append(enhanced_prompt)
            
            # Log the random selections for debugging
            logger.info(f"Prompt {i+1}: Gender={gender}, Shirt Color={shirt_color}, Activity={activity}")
        
        return enhanced_prompts
    
    def _generate_ai_image(self, prompt: str, variation: int) -> Image.Image:
        """Generate AI image using Flux API with polling."""
        try:
            if not self.api_key or not self.api_url:
                logger.warning("Flux API credentials not configured")
                return self._generate_placeholder_image(prompt)
            
            # Step 1: Submit generation request to Flux API
            headers = {
                'X-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'prompt': prompt,
                'width': 512,  # Flux works better with standard sizes
                'height': 512,
                'steps': 28,
                'guidance': 3.5,
                'safety_tolerance': 2,
                'seed': variation * 1000,  # Different seed for variations
                'output_format': 'png'
            }
            
            logger.info(f"Submitting prompt to Flux API: {prompt[:50]}...")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60,
                verify=False  # For corporate SSL issues
            )
            
            if response.status_code != 200:
                logger.error(f"Flux API error: {response.status_code} - {response.text[:200]}")
                return self._generate_placeholder_image(prompt)
            
            result = response.json()
            task_id = result.get('id')
            polling_url = result.get('polling_url')
            
            if not polling_url:
                logger.error("No polling URL received from Flux API")
                return self._generate_placeholder_image(prompt)
            
            logger.info(f"Flux task ID: {task_id}, polling for result...")
            
            # Step 2: Poll for result
            max_attempts = 30
            for attempt in range(max_attempts):
                time.sleep(2)  # Wait between polls
                
                poll_response = requests.get(
                    polling_url,
                    headers={'X-Key': self.api_key},
                    verify=False
                )
                
                if poll_response.status_code == 200:
                    poll_data = poll_response.json()
                    status = poll_data.get('status')
                    
                    if status == 'Ready':
                        # Image is ready
                        image_url = poll_data.get('result', {}).get('sample')
                        if image_url:
                            logger.info("Flux image ready, downloading...")
                            
                            # Download image
                            img_response = requests.get(image_url, verify=False)
                            if img_response.status_code == 200:
                                return Image.open(BytesIO(img_response.content))
                            else:
                                logger.error(f"Failed to download Flux image: {img_response.status_code}")
                        break
                    elif status == 'Error':
                        logger.error(f"Flux generation error: {poll_data.get('error', 'Unknown')}")
                        break
                    # Continue polling if status is 'Pending' or other
            
            logger.warning("Flux API timeout or error, using placeholder")
            return self._generate_placeholder_image(prompt)
            
        except Exception as e:
            logger.error(f"Error generating AI image: {str(e)}")
            return self._generate_placeholder_image(prompt)
    
    def _get_non_transparent_bounds(self, image: Image.Image) -> Optional[Tuple[int, int]]:
        """Detect the non-transparent region bounds in the image."""
        if image.mode != 'RGBA':
            return None
        
        width, height = image.size
        pixels = image.load()
        
        # Find leftmost and rightmost non-transparent pixels
        min_x = width
        max_x = 0
        
        for x in range(width):
            for y in range(height):
                if pixels[x, y][3] > 0:  # Check alpha channel
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
        
        if min_x < width and max_x > 0:
            return (min_x, max_x)
        return None
    
    def _compose_banner(self, ai_image: Image.Image, tagline: str, index: int) -> str:
        """Compose final banner with background, AI image, and tagline using reference method."""
        try:
            # Load the background image (ensure RGBA for transparency)
            background = self._get_background_template(index)
            if not background:
                background = self._create_gradient_background(index)
            
            if background.mode != 'RGBA':
                background = background.convert('RGBA')
            
            width, height = background.size
            
            # Detect the area where background is non-transparent
            non_transparent_bounds = self._get_non_transparent_bounds(background)
            if non_transparent_bounds:
                min_x, max_x = non_transparent_bounds
            else:
                min_x, max_x = int(width * 0.5), width  # Default to the right half if no transparency detected
            
            # Convert AI image to RGBA and remove its background using rembg
            if ai_image.mode != 'RGBA':
                ai_image = ai_image.convert('RGBA')
            
            # Apply rembg with optimized settings for white background removal
            # Using alpha matting for better edge quality on white backgrounds
            foreground = remove(
                ai_image,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=10
            )
            
            # Additional cleanup: ensure pure white pixels are transparent
            # This helps with any remaining white background artifacts
            fg_data = foreground.getdata()
            new_data = []
            for item in fg_data:
                # Change all white (and near-white) pixels to transparent
                if item[0] > 250 and item[1] > 250 and item[2] > 250:
                    new_data.append((255, 255, 255, 0))  # Make transparent
                else:
                    new_data.append(item)
            foreground.putdata(new_data)
            
            # Calculate optimal size for the Flux image
            # Make the image bigger - about 55% of the banner width
            fg_width, fg_height = foreground.size
            max_fg_width = int(width * 0.55)  # Increased from 50% to 55%
            max_fg_height = int(height * 0.95)  # Increased from 90% to 95%
            
            # Scale to fit within these constraints while maintaining aspect ratio
            scale_factor = min(max_fg_width / fg_width, max_fg_height / fg_height)
            new_width = int(fg_width * scale_factor)
            new_height = int(fg_height * scale_factor)
            foreground = foreground.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Position on the right side of the banner, slightly lower
            fg_x = width - new_width - 15  # Reduced margin to 15px from right edge
            fg_y = int((height - new_height) / 2) + 15  # Moved 15px lower
            
            # Paste the foreground image using alpha channel to blend properly
            background.paste(foreground, (fg_x, fg_y), foreground)
            
            # Add text on the left side
            draw = ImageDraw.Draw(background)
            
            # Try to load custom font, fallback to Arial or default
            try:
                # First try Helvetica Bold if available
                font_path = "C:/Windows/Fonts/arialbd.ttf"  # Arial Bold
                if os.path.exists("static/fonts/HelveticaforTarget-Bold.ttf"):
                    font_path = "static/fonts/HelveticaforTarget-Bold.ttf"
                # Decreased font size for better fit
                font_size = 28 if height <= 350 else 30
                font = ImageFont.truetype(font_path, font_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", 28)
                except:
                    font = ImageFont.load_default()
            
            # Position text more to the right, with better wrapping
            # Calculate available space before the Flux image
            available_width = fg_x - 100  # Space from left margin to Flux image position
            text_x = 80  # Moved from 60 to 80 (further to the right)
            text_y = int(height / 2) - 50  # Adjusted vertical position
            
            # Calculate max characters per line based on available space
            # This prevents text from colliding with the Flux image
            max_chars_per_line = 13  # Adjusted for new spacing
            
            # Wrap text smartly - prefer 2-3 lines for better readability
            # Use break_long_words=False to prevent word splitting
            words = tagline.split()
            if len(tagline) > 20:  # For longer taglines
                max_chars_per_line = 10  # Use shorter lines for longer text
            
            # Use textwrap with break_long_words=False to prevent word splitting
            wrapped_lines = textwrap.wrap(
                tagline, 
                width=max_chars_per_line,
                break_long_words=False,  # Never split words across lines
                break_on_hyphens=False   # Don't break on hyphens either
            )
            
            # If any line is still too long because of a long word, adjust wrapping
            # This ensures words like "entertainment" stay on one line
            final_lines = []
            for line in wrapped_lines:
                # Check if any word in the line is being cut
                if len(line) > max_chars_per_line and ' ' not in line:
                    # Single long word - keep it on its own line
                    final_lines.append(line)
                else:
                    final_lines.append(line)
            
            wrapped_text = "\n".join(final_lines)
            
            # Draw text with transparency support
            text_layer = Image.new("RGBA", background.size, (255, 255, 255, 0))  # Transparent text layer
            text_draw = ImageDraw.Draw(text_layer)
            text_draw.text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255, 255))
            
            # Merge text layer with background
            final_banner = Image.alpha_composite(background, text_layer)
            
            # Set output directory
            banner_dir = os.path.join(Config.STATIC_FOLDER, "banners")
            os.makedirs(banner_dir, exist_ok=True)
            
            # Generate filename using current date and index
            current_date = datetime.now().strftime("%d_%B_%Y")
            filename = f"Banner_{current_date}_{index}.png"
            filepath = os.path.join(banner_dir, filename)
            
            # Save banner
            final_banner.save(filepath, 'PNG')
            
            # Return URL path
            return f"/static/banners/{filename}"
            
        except Exception as e:
            logger.error(f"Error composing banner: {str(e)}")
            return ""
    
    def _get_background_template(self, index: int) -> Image.Image:
        """Load or create background template."""
        try:
            # Always use the same background image (banner_bg_0) without resizing
            template_path = os.path.join(Config.ASSETS_FOLDER, 'backgrounds', 'banner_bg_0.png')
            if os.path.exists(template_path):
                bg = Image.open(template_path)
                # Update dimensions to match actual background
                self.banner_width, self.banner_height = bg.size
                return bg
            
            # Create gradient background if template doesn't exist
            return self._create_gradient_background(index)
            
        except Exception as e:
            logger.error(f"Error loading background: {str(e)}")
            return self._create_gradient_background(index)
    
    def _create_gradient_background(self, index: int) -> Image.Image:
        """Create a gradient background."""
        img = Image.new('RGB', (self.banner_width, self.banner_height))
        draw = ImageDraw.Draw(img)
        
        # Define gradient colors (purple theme)
        color_sets = [
            ((59, 16, 142), (139, 69, 185)),  # Purple gradient
            ((45, 12, 108), (103, 51, 154)),  # Dark purple gradient
            ((75, 20, 180), (150, 80, 200))   # Light purple gradient
        ]
        
        start_color, end_color = color_sets[index % 3]
        
        # Create gradient
        for i in range(self.banner_width):
            ratio = i / self.banner_width
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
            draw.rectangle([(i, 0), (i + 1, self.banner_height)], fill=(r, g, b))
        
        return img
    
    def _apply_gradient_fade(self, image: Image.Image) -> Image.Image:
        """Apply gradient fade to image edges."""
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create alpha mask
        alpha = Image.new('L', image.size, 255)
        draw = ImageDraw.Draw(alpha)
        
        # Apply gradient fade on left edge
        fade_width = 100
        for i in range(fade_width):
            opacity = int(255 * (i / fade_width))
            draw.rectangle([(i, 0), (i + 1, image.height)], fill=opacity)
        
        # Apply the alpha mask
        image.putalpha(alpha)
        
        return image
    
    
    def _generate_placeholder_image(self, prompt: str) -> Image.Image:
        """Generate a placeholder image when API fails."""
        img = Image.new('RGB', (self.banner_width, self.banner_height), color=(100, 50, 150))
        draw = ImageDraw.Draw(img)
        
        # Add some visual interest
        for i in range(0, self.banner_width, 50):
            for j in range(0, self.banner_height, 50):
                color = (
                    100 + (i % 100),
                    50 + (j % 100),
                    150 + ((i + j) % 50)
                )
                draw.ellipse([i, j, i + 30, j + 30], fill=color)
        
        return img
    
    def _get_fallback_banner(self, tagline: str, index: int) -> str:
        """Generate a fallback banner when API fails."""
        try:
            # Create simple gradient banner
            banner = self._create_gradient_background(index)
            
            # Add tagline
            draw = ImageDraw.Draw(banner)
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            # Draw centered text
            draw.text(
                (self.banner_width // 2 - 200, self.banner_height // 2),
                tagline[:50],
                font=font,
                fill='white'
            )
            
            # Save
            filename = f"fallback_banner_{index}.png"
            filepath = os.path.join(Config.TEMP_FOLDER, filename)
            banner.save(filepath, 'PNG', quality=self.image_quality)
            
            return f"/static/temp/{filename}"
            
        except Exception as e:
            logger.error(f"Error creating fallback banner: {str(e)}")
            return "/static/assets/default_banner.png"