import logging
import time
import os
from typing import List, Dict
from config import Config
import openai

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """Generate AI-powered content using OpenAI GPT."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        # Set API key as environment variable for OpenAI to use
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            logger.info("OpenAI API key configured")
        else:
            logger.warning("No OpenAI API key provided")
        
        self.rate_limit = Config.OPENAI_RATE_LIMIT
        self.retry_attempts = Config.API_RETRY_ATTEMPTS
        self.retry_delay = Config.API_RETRY_DELAY
        
    def generate_taglines(self, context: Dict, count: int = 3) -> List[str]:
        """Generate multiple tagline options."""
        taglines = []
        
        try:
            # Build context prompt
            prompt = self._build_tagline_prompt(context)
            
            for i in range(count):
                tagline = self._generate_with_retry(
                    prompt=prompt,
                    max_tokens=30,
                    temperature=0.8 + (i * 0.1),  # Vary temperature for diversity
                    is_tagline=True
                )
                
                if tagline:
                    # Clean and validate tagline
                    tagline_clean = self._clean_tagline(tagline)
                    if self._validate_tagline(tagline_clean):
                        taglines.append(tagline_clean)
                
                # Rate limiting
                if i < count - 1:  # Don't sleep after last iteration
                    time.sleep(60 / self.rate_limit)
            
            # Ensure we have the requested number of taglines
            while len(taglines) < count:
                taglines.append(self._get_fallback_tagline())
            
            return taglines[:count]
            
        except Exception as e:
            logger.error(f"Error generating taglines: {str(e)}")
            return [self._get_fallback_tagline() for _ in range(count)]
    
    def generate_introductions(self, context: Dict, count: int = 3) -> List[str]:
        """Generate multiple introduction options."""
        intros = []
        
        try:
            # Build context prompt
            prompt = self._build_intro_prompt(context)
            
            for i in range(count):
                intro = self._generate_with_retry(
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.7 + (i * 0.1)  # Vary temperature for diversity
                )
                
                if intro:
                    # Clean and validate introduction
                    intro_clean = self._clean_introduction(intro)
                    if self._validate_introduction(intro_clean):
                        intros.append(intro_clean)
                
                # Rate limiting
                if i < count - 1:  # Don't sleep after last iteration
                    time.sleep(60 / self.rate_limit)
            
            # Ensure we have the requested number of intros
            while len(intros) < count:
                intros.append(self._get_fallback_intro())
            
            return intros[:count]
            
        except Exception as e:
            logger.error(f"Error generating introductions: {str(e)}")
            return [self._get_fallback_intro() for _ in range(count)]
    
    def _generate_with_retry(self, prompt: str, max_tokens: int, temperature: float, is_tagline: bool = False) -> str:
        """Generate content with retry logic."""
        if not self.api_key:
            logger.error("OpenAI API key not provided")
            return ""
            
        for attempt in range(self.retry_attempts):
            try:
                # Use different system prompts for taglines vs body
                if is_tagline:
                    system_prompt = "You are an expert copywriter specializing in concise, engaging marketing copy. Your task is to generate short and compelling banner taglines for a streaming newsletter that highlights shows and movies for the upcoming week."
                else:
                    system_prompt = "You are an expert copywriter specializing in concise, engaging marketing copy for streaming newsletters."
                
                # Make the API call using the openai module
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for better availability
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    n=1
                )
                
                if response and response.choices:
                    content = response.choices[0].message.content.strip()
                    logger.debug(f"Generated {'tagline' if is_tagline else 'intro'}: {content[:50]}...")
                    return content
                    
            except Exception as e:
                error_str = str(e)
                if "rate_limit" in error_str.lower():
                    logger.warning(f"Rate limit hit, waiting {self.retry_delay * (attempt + 1)} seconds")
                    time.sleep(self.retry_delay * (attempt + 1))
                elif "api" in error_str.lower() and "key" in error_str.lower():
                    logger.error("API key issue detected. Please check your OPENAI_API_KEY in .env file")
                    break  # Don't retry on API key issues
                else:
                    logger.error(f"OpenAI API error (attempt {attempt + 1}): {error_str}")
                    time.sleep(self.retry_delay)
        
        return ""
    
    def _build_tagline_prompt(self, context: Dict) -> str:
        """Build prompt for tagline generation."""
        date_range = context.get('date_range', {})
        
        # Extract month from date range with error handling
        from datetime import datetime
        try:
            start_date_str = date_range.get('start', '')
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                month = start_date.strftime('%B')
            else:
                # Fallback to current month
                month = datetime.now().strftime('%B')
        except Exception as e:
            logger.warning(f"Error parsing date for tagline: {e}")
            month = datetime.now().strftime('%B')
        
        # Include highlights if available
        highlights = context.get('highlights', [])
        highlights_text = ""
        if highlights:
            highlights_text = f"\nFeatured shows include: {', '.join(highlights[:3])}"
        
        prompt = f"""Generate a short and engaging banner tagline for a streaming newsletter highlighting shows and movies for the upcoming week{highlights_text}. 
        
The tagline should be concise (maximum 4-5 words), exciting, and relevant to new releases. It should create anticipation and align with past examples like:
1. Your streaming spree for {month}.
2. Catch up on this week's releases.
3. Stream this week's best picks.

Generate exactly ONE tagline. Do not include numbering, quotes, or any explanation. Just the tagline text."""
        
        return prompt
    
    def _build_intro_prompt(self, context: Dict) -> str:
        """Build prompt for introduction generation."""
        tagline = context.get('tagline', '')
        
        # Don't mention specific shows - keep it generic
        prompt = f"""Generate a short and engaging streaming newsletter body introduction in maximum of two lines (one small paragraph).

The tone should be exciting and inviting, highlighting how users can stream the latest shows and movies from anywhere, ensuring they never miss out on global content. Keep it concise and action-driven, encouraging users to click 'Watch Now' for seamless access.

Use variations like:
- "Unlock endless entertainment! Stream the latest shows and movies from anywhere, ensuring you never miss out on global content. Click 'Watch Now' for seamless access!"
- "Never miss out on the hottest releases this week! Stream anywhere and enjoy global content effortlessly. Click 'Watch Now' and dive into a world of entertainment."
- "Get ready for your weekly dose of entertainment! Access the latest releases from anywhere in the world. Click 'Watch Now' to start streaming!"


Generate exactly ONE body text that is generic and does NOT mention any specific show names. Do not include numbering, quotes, or any explanation. You may use one appropriate emoji if needed."""
        
        return prompt
    
    def _clean_tagline(self, tagline: str) -> str:
        """Clean and format tagline."""
        # Remove quotes if present
        tagline = tagline.strip('"\'')
        
        # Remove any numbering or bullets
        import re
        tagline = re.sub(r'^[\d\.\-\*\•]+\s*', '', tagline)
        
        # Ensure proper capitalization
        if tagline and not tagline[0].isupper():
            tagline = tagline[0].upper() + tagline[1:]
        
        # Remove extra whitespace
        tagline = ' '.join(tagline.split())
        
        return tagline
    
    def _clean_introduction(self, intro: str) -> str:
        """Clean and format introduction."""
        # Remove quotes if present
        intro = intro.strip('"\'')
        
        # Remove any numbering or bullets
        import re
        intro = re.sub(r'^[\d\.\-\*\•]+\s*', '', intro)
        
        # Ensure proper paragraph formatting
        intro = ' '.join(intro.split())
        
        # Ensure streaming mention
        if 'streaming' not in intro.lower() and 'stream' not in intro.lower():
            intro = intro.replace('entertainment', 'streaming entertainment', 1)
        
        return intro
    
    def _validate_tagline(self, tagline: str) -> bool:
        """Validate tagline meets requirements."""
        if not tagline:
            return False
        word_count = len(tagline.split())
        # Maximum 6-7 words as per requirements
        return 3 <= word_count <= 8  # Slightly flexible
    
    def _validate_introduction(self, intro: str) -> bool:
        """Validate introduction meets requirements."""
        if not intro:
            return False
        # Maximum 2 lines means roughly 20-40 words
        word_count = len(intro.split())
        return 15 <= word_count <= 50
    
    def _get_fallback_tagline(self) -> str:
        """Get fallback tagline if generation fails."""
        from datetime import datetime
        month = datetime.now().strftime('%B')
        fallbacks = [
            f"Your streaming spree for {month}",
            "Catch up on this week's releases",
            "Stream this week's best picks",
            "Don't miss this week's premieres",
            "Your weekly streaming guide"
        ]
        import random
        return random.choice(fallbacks)
    
    def _get_fallback_intro(self) -> str:
        """Get fallback introduction if generation fails."""
        fallbacks = [
            "Unlock endless entertainment! Stream the latest shows and movies from anywhere, ensuring you never miss out on global content. Click 'Watch Now' for seamless access!",
            "Never miss out on the hottest releases this week! Stream anywhere and enjoy global content effortlessly. Click 'Watch Now' and dive into a world of entertainment.",
            "Get ready for your weekly dose of entertainment! Access the latest releases from anywhere in the world. Click 'Watch Now' to start streaming!",
            "Experience unlimited streaming! Access the newest shows and movies from any location and never be limited by geography. Click 'Watch Now' for instant entertainment!",
            "Your gateway to global entertainment awaits! Stream the week's best releases from anywhere. Click 'Watch Now' and unlock a world of content!"
        ]
        import random
        return random.choice(fallbacks)