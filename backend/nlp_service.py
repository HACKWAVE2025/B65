"""
NLP and Cultural Context Enrichment Service

This service coordinates spaCy entity extraction, Wikipedia/Wikidata enrichment,
and caching to provide interactive cultural context highlights.
"""

import spacy
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from wikipedia_service import wikipedia_service
from database import get_cached_entity, save_entity_cache


class NLPEnrichmentService:
    """Service for NLP-based entity detection and cultural enrichment"""
    
    def __init__(self):
        """Initialize spaCy and load language model"""
        try:
            # Try to load the model
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model loaded successfully")
        except OSError:
            print("⚠️  spaCy model not found. Installing en_core_web_sm...")
            print("ℹ️  Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Define culturally relevant entity types
        self.cultural_entity_types = {
            "PERSON",      # People, including fictional
            "ORG",         # Organizations, companies, institutions
            "GPE",         # Geopolitical entities (countries, cities)
            "LOC",         # Non-GPE locations (mountains, rivers)
            "EVENT",       # Named events (battles, ceremonies)
            "WORK_OF_ART", # Titles of books, songs, paintings
            "FAC",         # Buildings, airports, highways
            "NORP",        # Nationalities, religious/political groups
            "LANGUAGE",    # Named languages
        }
        
        # Minimum entity length to avoid noise
        self.min_entity_length = 3
        
        # Common words to exclude (avoid false positives)
        self.exclude_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", 
            "for", "of", "with", "by", "from", "up", "about", "into"
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract culturally relevant named entities from text using spaCy
        
        Args:
            text: Input text to analyze
        
        Returns:
            List of detected entities with metadata
        """
        if not self.nlp:
            print("❌ spaCy model not available")
            return []
        
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            entities = []
            seen_entities = set()  # Deduplicate
            
            for ent in doc.ents:
                # Filter by relevant entity types
                if ent.label_ not in self.cultural_entity_types:
                    continue
                
                # Clean entity text
                entity_text = ent.text.strip()
                
                # Skip short or common words
                if len(entity_text) < self.min_entity_length:
                    continue
                
                if entity_text.lower() in self.exclude_words:
                    continue
                
                # Deduplicate (case-insensitive)
                entity_key = (entity_text.lower(), ent.label_)
                if entity_key in seen_entities:
                    continue
                
                seen_entities.add(entity_key)
                
                # Extract entity with position information
                entities.append({
                    "text": entity_text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 1.0  # spaCy doesn't provide scores for NER
                })
            
            print(f"📍 Detected {len(entities)} cultural entities")
            return entities
            
        except Exception as e:
            print(f"❌ Entity extraction error: {e}")
            return []
    
    def enrich_entity(
        self, 
        entity_text: str, 
        entity_type: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Enrich entity with cultural context from Wikipedia/Wikidata
        
        Args:
            entity_text: Entity name
            entity_type: Entity type (PERSON, ORG, etc.)
            use_cache: Whether to use cached data
        
        Returns:
            Enriched entity data
        """
        # Check cache first
        if use_cache:
            cached = get_cached_entity(entity_text, entity_type)
            if cached:
                print(f"💾 Using cached data for: {entity_text}")
                return cached
        
        # Fetch from Wikipedia
        enrichment = wikipedia_service.enrich_entity(entity_text, entity_type)
        
        # Save to cache if successful
        if enrichment.get("summary"):
            cache_data = {
                "entity_name": entity_text,
                "entity_type": entity_type,
                "summary": enrichment.get("summary"),
                "url": enrichment.get("url"),
                "categories": enrichment.get("categories", []),
                "cultural_significance": enrichment.get("cultural_significance", "general"),
                "wikidata": enrichment.get("wikidata"),
                "source": enrichment.get("source", "Wikipedia"),
                "created_at": datetime.utcnow().isoformat()
            }
            save_entity_cache(cache_data)
            print(f"✅ Cached enrichment for: {entity_text}")
        
        return enrichment
    
    def analyze_text_with_entities(
        self, 
        text: str,
        enrich_all: bool = True
    ) -> Dict[str, Any]:
        """
        Complete pipeline: extract entities and enrich with cultural context
        
        Args:
            text: Input text to analyze
            enrich_all: Whether to enrich all entities (can be slow)
        
        Returns:
            Dictionary with detected entities and enrichment data
        """
        # Extract entities
        entities = self.extract_entities(text)
        
        if not entities:
            return {
                "detected_entities": [],
                "enriched_count": 0,
                "total_detected": 0
            }
        
        # Enrich entities (limit to avoid long processing times)
        max_enrich = 10 if enrich_all else 5
        enriched_entities = []
        
        for i, entity in enumerate(entities[:max_enrich]):
            enrichment = self.enrich_entity(
                entity["text"], 
                entity["type"],
                use_cache=True
            )
            
            # Combine extraction and enrichment
            enriched = {
                **entity,
                "summary": enrichment.get("summary"),
                "url": enrichment.get("url"),
                "cultural_significance": enrichment.get("cultural_significance"),
                "source": enrichment.get("source")
            }
            
            enriched_entities.append(enriched)
        
        # Add remaining entities without full enrichment
        if len(entities) > max_enrich:
            for entity in entities[max_enrich:]:
                enriched_entities.append({
                    **entity,
                    "summary": None,
                    "url": None,
                    "cultural_significance": "unknown",
                    "source": None
                })
        
        print(f"✅ Enriched {min(len(entities), max_enrich)} of {len(entities)} entities")
        
        return {
            "detected_entities": enriched_entities,
            "enriched_count": min(len(entities), max_enrich),
            "total_detected": len(entities)
        }
    
    def get_entity_highlights(self, text: str) -> List[Dict[str, Any]]:
        """
        Get entity highlights optimized for frontend display
        
        Args:
            text: Input text
        
        Returns:
            List of highlight regions with tooltip data
        """
        result = self.analyze_text_with_entities(text, enrich_all=False)
        
        highlights = []
        for entity in result["detected_entities"]:
            highlight = {
                "start": entity["start"],
                "end": entity["end"],
                "text": entity["text"],
                "type": entity["type"],
                "tooltip": {
                    "title": entity["text"],
                    "summary": entity.get("summary", "No information available"),
                    "significance": entity.get("cultural_significance", "general"),
                    "url": entity.get("url"),
                    "source": entity.get("source")
                }
            }
            highlights.append(highlight)
        
        return highlights
    
    def classify_cultural_significance_ml(self, text: str, entity_text: str) -> str:
        """
        Use Hugging Face transformers for semantic classification (optional enhancement)
        
        Args:
            text: Full text context
            entity_text: Entity to classify
        
        Returns:
            Cultural significance category
        """
        # TODO: Implement HF transformers classification
        # This would use a model like distilbert-base-uncased fine-tuned
        # for cultural/historical classification
        # For now, return placeholder
        return "general"


# Singleton instance
nlp_service = NLPEnrichmentService()
