import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # type: ignore


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')  # type: ignore
        self.vision_model = genai.GenerativeModel('gemini-2.5-flash')  # type: ignore

    
    async def analyze_cultural_context(self, text: str, language: str = "en") -> dict:
        """
        Analyze text for cultural context using Gemini API
        
        Args:
            text: The input text to analyze
            language: Language code (default: en)
        
        Returns:
            Dictionary with cultural analysis results
        """
        
        # Map language codes to full names for better AI understanding
        language_names = {
            "en": "English",
            "hi": "Hindi (हिंदी)",
            "es": "Spanish (Español)",
            "fr": "French (Français)",
            "de": "German (Deutsch)",
            "zh": "Chinese (中文)",
            "ja": "Japanese (日本語)",
            "ar": "Arabic (العربية)",
            "bn": "Bengali (বাংলা)",
            "ta": "Tamil (தமிழ்)",
            "te": "Telugu (తెలుగు)",
            "mr": "Marathi (मराठी)",
        }
        
        language_name = language_names.get(language, "English")
        
        prompt = f"""
You are a cultural expert analyzing the following text. Provide a comprehensive cultural analysis.

Text to analyze: "{text}"

CRITICAL INSTRUCTION - OUTPUT LANGUAGE:
You MUST provide ALL response text in {language_name} ({language}) language. This includes:
- cultural_origin field
- cross_cultural_connections field
- modern_analogy field
- All descriptions, titles, and text in timeline_events
- All text in geographic_locations
- All definitions, context, and explanations in key_concepts
- ALL other text fields in your response

The analysis should be comprehensive and culturally sensitive, written entirely in {language_name}.

Return your response as valid JSON with the following structure:
{{
    "cultural_origin": "Brief origin and significance",
    "cross_cultural_connections": "Key influences and relationships",
    "modern_analogy": "Relevant Gen Z/Millennial comparison",
    "timeline_events": [
        {{
            "year": "YYYY",
            "title": "Event title",
            "description": "Brief context",
            "significance": "Impact"
        }}
    ],
    "geographic_locations": [
        {{
            "name": "Location",
            "coordinates": {{"lat": 0.0, "lng": 0.0}},
            "significance": "Brief importance",
            "modern_name": "Current name"
        }}
    ],
    "key_concepts": [
        {{
            "term": "Term",
            "definition": "Brief definition",
            "context": "Relevance",
            "modern_parallel": "Modern example"
        }}
    ],
    "external_resources": {{
        "timeline_links": [],
        "map_links": [],
        "further_reading": []
    }}
}}

Rules:
- ALL text must be in {language_name} ({language}) language - no exceptions
- Include timeline_events only for historical content (3-5 events)
- Include geographic_locations only for place-specific content (2-4 locations)
- Include key_concepts only for complex terms (3-5 terms)
- Use only verified URLs for external_resources
- Make modern_analogy specific to current trends
- Ensure cultural sensitivity and accuracy in the {language_name} language

Return ONLY valid JSON. Do not include any text before or after the JSON object.
"""
        
        try:
            # Generate content with safety settings to avoid blocking
            response = self.model.generate_content(
                prompt,
                generation_config={  # type: ignore
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            
            # Check if response was blocked
            if not response or not response.text:
                print(f"⚠️ Response blocked or empty. Safety ratings: {response.prompt_feedback if response else 'No response'}")
                return {
                    "cultural_origin": "Unable to analyze this text. The content may have triggered safety filters or the AI couldn't process it.",
                    "cross_cultural_connections": "Please try rephrasing your text or use a different passage.",
                    "modern_analogy": "Analysis was blocked or failed.",
                    "timeline_events": [],
                    "geographic_locations": [],
                    "key_concepts": [],
                    "external_resources": {}
                }
            
            result_text = response.text.strip()
            print(f"🤖 AI Response length: {len(result_text)} characters")
            
            # Clean up the response to extract JSON
            # Remove markdown code blocks if present
            result_text = re.sub(r'^```json\s*', '', result_text, flags=re.IGNORECASE)
            result_text = re.sub(r'^```\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            result_text = result_text.strip()
            
            # Find the JSON object - extract from first { to last matching }
            # This handles cases where AI adds text before or after the JSON
            start_idx = result_text.find('{')
            if start_idx != -1:
                # Count braces to find the matching closing brace
                brace_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(result_text)):
                    if result_text[i] == '{':
                        brace_count += 1
                    elif result_text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                
                if end_idx > start_idx:
                    result_text = result_text[start_idx:end_idx]
            
            print(f"📝 Cleaned JSON length: {len(result_text)} characters")
            
            # Parse JSON response
            analysis = json.loads(result_text)
            
            # Validate required fields
            required_fields = [
                "cultural_origin",
                "cross_cultural_connections", 
                "modern_analogy"
            ]
            
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add default empty arrays if enhanced fields are missing
            if "timeline_events" not in analysis:
                analysis["timeline_events"] = []
            if "geographic_locations" not in analysis:
                analysis["geographic_locations"] = []
            if "key_concepts" not in analysis:
                analysis["key_concepts"] = []
            if "external_resources" not in analysis:
                analysis["external_resources"] = {}
            
            print(f"✅ Analysis completed successfully")
            print(f"   - Timeline events: {len(analysis.get('timeline_events', []))}")
            print(f"   - Geographic locations: {len(analysis.get('geographic_locations', []))}")
            print(f"   - Key concepts: {len(analysis.get('key_concepts', []))}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📄 Response text preview: {result_text[:500]}...")
            # Return a structured error response
            return {
                "cultural_origin": "Error: The AI returned invalid JSON format. This is usually temporary.",
                "cross_cultural_connections": "Please try again. If the issue persists, try simplifying your text.",
                "modern_analogy": "The analysis could not be completed due to formatting issues.",
                "timeline_events": [],
                "geographic_locations": [],
                "key_concepts": [],
                "external_resources": {}
            }
        except Exception as e:
            print(f"❌ Error in cultural analysis: {e}")
            import traceback
            traceback.print_exc()
            return {
                "cultural_origin": f"Error: {str(e)}",
                "cross_cultural_connections": "Analysis failed. Please check your internet connection and API key.",
                "modern_analogy": "Please try again or contact support if the issue persists.",
                "timeline_events": [],
                "geographic_locations": [],
                "key_concepts": [],
                "external_resources": {}
            }
    
    async def extract_text_from_image(self, image_data: bytes, mime_type: str = "image/jpeg") -> dict:
        """
        Extract text from image using Gemini Vision API
        
        Args:
            image_data: Image file bytes
            mime_type: MIME type of the image (e.g., 'image/jpeg', 'image/png')
        
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            import io
            from PIL import Image
            
            # Open image from bytes to validate and convert to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Prompt for text extraction - focus on relevant content
            prompt = """You are a smart text extraction assistant. Analyze this image and extract ONLY the main, relevant text content.

RULES FOR EXTRACTION:
1. Extract the primary/main text content (articles, paragraphs, quotes, stories, etc.)
2. IGNORE irrelevant elements like:
   - Watermarks, logos, branding
   - Page numbers, headers, footers
   - Navigation elements, buttons, menu items
   - Copyright notices, disclaimers
   - Advertisement text
   - Decorative text or background elements
   - Author names/signatures (unless part of main content)
   - Publication details (unless essential context)

3. Focus on extracting:
   - Main body text/paragraphs
   - Titles and headings (when they're part of the content)
   - Quotes or important passages
   - Story or article text
   - Educational or informational content

4. Preserve structure:
   - Keep paragraph breaks
   - Maintain logical text flow
   - Separate distinct sections with line breaks

Return ONLY the relevant extracted text. Do not add explanations, comments, or metadata.
If the image contains no meaningful text content (only decorative/irrelevant text), return: "No relevant text found in image"
"""

            print(f"📸 Extracting relevant text from image using Gemini Vision API...")
            
            # Use vision model to extract text with focus on relevance
            # Pass PIL Image directly - Gemini API handles it
            response = self.vision_model.generate_content(
                [prompt, image],
                generation_config={  # type: ignore
                    "temperature": 0.2,  # Slightly higher for smart filtering of relevant vs irrelevant text
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 4096,
                }
            )
            
            # Check if response was blocked
            if not response or not response.text:
                print(f"⚠️ Response blocked or empty. Safety ratings: {response.prompt_feedback if response else 'No response'}")
                return {
                    "success": False,
                    "text": "",
                    "error": "Unable to extract text from this image. The content may have triggered safety filters or the image quality is too poor."
                }
            
            extracted_text = response.text.strip()
            
            # Check if no relevant text was found
            if not extracted_text or extracted_text.lower() == "no relevant text found in image":
                return {
                    "success": False,
                    "text": "",
                    "error": "No relevant text could be extracted from the image. The image may only contain decorative elements, watermarks, or irrelevant text."
                }
            
            # Validate minimum length for meaningful content (lowered to 15 for short quotes/headlines)
            if len(extracted_text) < 15:
                return {
                    "success": False,
                    "text": extracted_text,
                    "error": "Extracted text is too short to be meaningful. Please ensure the image contains substantial readable content."
                }
            
            word_count = len(extracted_text.split())
            character_count = len(extracted_text)
            
            print(f"✅ Extracted {character_count} characters ({word_count} words) from image")
            
            return {
                "success": True,
                "text": extracted_text,
                "character_count": character_count,
                "word_count": word_count,
                "mime_type": mime_type
            }
            
        except Exception as e:
            print(f"❌ Error extracting text from image: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "text": "",
                "error": f"Error extracting text from image: {str(e)}"
            }


# Create singleton instance
gemini_service = GeminiService()
