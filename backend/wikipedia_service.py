"""
Wikipedia and Wikidata API Integration Service (Enhanced with Multi-Source)

This service fetches verified background summaries for cultural, historical,
and literary entities detected in text. Includes error handling, rate limiting,
and fallback mechanisms.

Now integrates with multi_source_service for cross-verification and accuracy.
"""

import requests
import wikipediaapi
from typing import Dict, Any, Optional, List
import time
from datetime import datetime
from multi_source_service import multi_source_service


class WikipediaService:
    """Service for fetching entity information from Wikipedia and Wikidata"""
    
    def __init__(self):
        # Initialize Wikipedia API with user agent
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            user_agent='CulturalContextAnalyzer/1.0 (educational project)'
        )
        
        # Rate limiting: track last request time
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Wikidata API endpoint
        self.wikidata_api = "https://www.wikidata.org/w/api.php"
        
        print("✅ Wikipedia service initialized")
    
    def _rate_limit(self):
        """Enforce rate limiting between API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    def get_entity_summary(
        self, 
        entity_name: str, 
        entity_type: str = "MISC"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch summary for a named entity from Wikipedia
        
        Args:
            entity_name: Name of the entity to look up
            entity_type: Type of entity (PERSON, ORG, GPE, EVENT, WORK_OF_ART, etc.)
        
        Returns:
            Dictionary with entity summary data or None if not found
        """
        try:
            self._rate_limit()
            
            # Clean entity name for better search
            clean_name = entity_name.strip()
            
            # Fetch Wikipedia page
            page = self.wiki.page(clean_name)
            
            if not page.exists():
                # Try search if direct lookup fails
                search_results = self._search_wikipedia(clean_name)
                if search_results:
                    page = self.wiki.page(search_results[0])
                else:
                    print(f"ℹ️  No Wikipedia page found for: {entity_name}")
                    return None
            
            # Extract summary (first few sentences)
            summary = self._extract_summary(page.summary)
            
            # Get categories for cultural classification
            categories = self._get_cultural_categories(page)
            
            # Determine cultural significance
            significance = self._classify_cultural_significance(entity_type, categories)
            
            return {
                "entity_name": entity_name,
                "entity_type": entity_type,
                "summary": summary,
                "url": page.fullurl,
                "categories": categories[:5],  # Top 5 relevant categories
                "cultural_significance": significance,
                "source": "Wikipedia",
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error fetching Wikipedia data for '{entity_name}': {e}")
            return None
    
    def _search_wikipedia(self, query: str, limit: int = 5) -> List[str]:
        """
        Search Wikipedia for matching pages
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of page titles
        """
        try:
            self._rate_limit()
            
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': limit,
                'format': 'json'
            }
            
            response = requests.get(
                'https://en.wikipedia.org/w/api.php',
                params=params,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data[1] if len(data) > 1 else []
            
            return []
            
        except Exception as e:
            print(f"❌ Wikipedia search error: {e}")
            return []
    
    def _extract_summary(self, full_summary: str, max_sentences: int = 3) -> str:
        """
        Extract a concise summary (first N sentences)
        
        Args:
            full_summary: Full Wikipedia summary
            max_sentences: Maximum number of sentences to include
        
        Returns:
            Shortened summary
        """
        if not full_summary:
            return ""
        
        # Split by sentences (simple approach)
        sentences = full_summary.split('. ')
        
        # Take first N sentences
        summary = '. '.join(sentences[:max_sentences])
        
        # Ensure it ends with a period
        if not summary.endswith('.'):
            summary += '.'
        
        # Limit length to ~300 characters for tooltips
        if len(summary) > 300:
            summary = summary[:297] + '...'
        
        return summary
    
    def _get_cultural_categories(self, page) -> List[str]:
        """
        Extract cultural/historical categories from Wikipedia page
        
        Args:
            page: Wikipedia page object
        
        Returns:
            List of relevant category names
        """
        cultural_keywords = [
            'history', 'historical', 'culture', 'cultural', 'literature',
            'literary', 'mythology', 'mythological', 'ancient', 'classical',
            'philosophy', 'philosophical', 'religion', 'religious', 'art',
            'architecture', 'tradition', 'folklore', 'legend'
        ]
        
        relevant_categories = []
        
        try:
            for category in page.categories.keys():
                # Remove "Category:" prefix
                cat_name = category.replace('Category:', '')
                
                # Check if category is culturally relevant
                if any(keyword in cat_name.lower() for keyword in cultural_keywords):
                    relevant_categories.append(cat_name)
            
        except Exception as e:
            print(f"⚠️  Error extracting categories: {e}")
        
        return relevant_categories
    
    def _classify_cultural_significance(
        self, 
        entity_type: str, 
        categories: List[str]
    ) -> str:
        """
        Classify the cultural significance of an entity
        
        Args:
            entity_type: spaCy entity type
            categories: Wikipedia categories
        
        Returns:
            Cultural significance classification
        """
        # Check categories for specific themes
        categories_text = ' '.join(categories).lower()
        
        if any(word in categories_text for word in ['mythology', 'mythological', 'folklore']):
            return "mythological"
        
        if any(word in categories_text for word in ['ancient', 'classical', 'medieval']):
            return "historical"
        
        if any(word in categories_text for word in ['literature', 'literary', 'novel', 'poetry']):
            return "literary"
        
        if any(word in categories_text for word in ['philosophy', 'philosophical']):
            return "philosophical"
        
        if any(word in categories_text for word in ['religion', 'religious', 'spiritual']):
            return "religious"
        
        if entity_type == "WORK_OF_ART":
            return "artistic"
        
        if entity_type in ["PERSON", "ORG"]:
            return "biographical"
        
        if entity_type in ["GPE", "LOC"]:
            return "geographical"
        
        return "general"
    
    def get_wikidata_info(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch additional structured data from Wikidata
        
        Args:
            entity_name: Name of the entity
        
        Returns:
            Dictionary with Wikidata information or None
        """
        try:
            self._rate_limit()
            
            # Search for Wikidata entity
            search_params = {
                'action': 'wbsearchentities',
                'search': entity_name,
                'language': 'en',
                'format': 'json',
                'limit': 1
            }
            
            response = requests.get(
                self.wikidata_api,
                params=search_params,
                timeout=5
            )
            
            if response.status_code != 200:
                return None
            
            search_data = response.json()
            
            if not search_data.get('search'):
                return None
            
            # Get first result
            entity_id = search_data['search'][0]['id']
            description = search_data['search'][0].get('description', '')
            
            return {
                "wikidata_id": entity_id,
                "description": description,
                "url": f"https://www.wikidata.org/wiki/{entity_id}"
            }
            
        except Exception as e:
            print(f"❌ Wikidata error for '{entity_name}': {e}")
            return None
    
    def enrich_entity(
        self, 
        entity_name: str, 
        entity_type: str = "MISC",
        use_multi_source: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive entity enrichment - now with multi-source verification!
        
        Strategy:
        1. If use_multi_source=True (default): Query multiple authoritative sources
        2. Fallback to Wikipedia if multi-source fails
        3. Cross-verify information when available from multiple sources
        
        Args:
            entity_name: Name of the entity
            entity_type: Type of entity
            use_multi_source: Whether to use multi-source lookup (default: True)
        
        Returns:
            Combined enriched data dictionary with confidence scores
        """
        enriched_data = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "summary": None,
            "url": None,
            "wikidata": None,
            "cultural_significance": "unknown",
            "source": None,
            "confidence": "low",
            "sources_consulted": []
        }
        
        # Try multi-source lookup first (more accurate and up-to-date)
        if use_multi_source:
            try:
                multi_data = multi_source_service.get_comprehensive_info(entity_name, entity_type)
                
                if multi_data and multi_data.get("sources_consulted"):
                    # Multi-source found data - prioritize this
                    enriched_data.update({
                        "summary": multi_data.get("summary") or multi_data.get("description"),
                        "description": multi_data.get("description"),
                        "url": multi_data.get("url"),
                        "image_url": multi_data.get("image_url"),
                        "confidence": multi_data.get("confidence"),
                        "sources_consulted": multi_data.get("sources_consulted", []),
                        "source": f"Multi-Source ({len(multi_data.get('sources_consulted', []))} sources)",
                        "wikidata_id": multi_data.get("wikidata_id"),
                        "dbpedia_uri": multi_data.get("dbpedia_uri"),
                        "literary_info": multi_data.get("literary_info")
                    })
                    
                    # Classify cultural significance from available data
                    enriched_data["cultural_significance"] = self._classify_from_multi_source(
                        entity_type, 
                        multi_data
                    )
                    
                    print(f"✅ Multi-source enrichment successful for '{entity_name}'")
                    return enriched_data
                    
            except Exception as e:
                print(f"⚠️  Multi-source lookup failed, falling back to Wikipedia: {e}")
        
        # Fallback to Wikipedia-only approach
        wiki_data = self.get_entity_summary(entity_name, entity_type)
        
        if wiki_data:
            enriched_data.update(wiki_data)
            enriched_data["sources_consulted"].append("Wikipedia")
            enriched_data["confidence"] = "medium (Wikipedia only)"
        else:
            # Last resort: try Wikidata only
            wikidata_info = self.get_wikidata_info(entity_name)
            
            if wikidata_info:
                enriched_data["summary"] = wikidata_info.get("description", "No description available")
                enriched_data["url"] = wikidata_info["url"]
                enriched_data["wikidata"] = wikidata_info
                enriched_data["source"] = "Wikidata"
                enriched_data["sources_consulted"].append("Wikidata")
                enriched_data["confidence"] = "low (Wikidata only)"
        
        return enriched_data
    
    def _classify_from_multi_source(
        self, 
        entity_type: str, 
        multi_data: Dict[str, Any]
    ) -> str:
        """
        Classify cultural significance using multi-source data
        
        Args:
            entity_type: spaCy entity type
            multi_data: Data from multi_source_service
        
        Returns:
            Cultural significance classification
        """
        # Check literary info first
        if multi_data.get("literary_info"):
            return "literary"
        
        # Check Knowledge Graph types
        kg_types = multi_data.get("types", [])
        if isinstance(kg_types, list):
            types_str = ' '.join(kg_types).lower()
            
            if 'book' in types_str or 'creativework' in types_str:
                return "literary"
            if 'person' in types_str:
                return "biographical"
            if 'place' in types_str:
                return "geographical"
            if 'event' in types_str:
                return "historical"
        
        # Check description for keywords
        description = (multi_data.get("description", "") + " " + 
                      multi_data.get("summary", "")).lower()
        
        if any(word in description for word in ['mythology', 'mythological', 'folklore', 'legend']):
            return "mythological"
        if any(word in description for word in ['ancient', 'classical', 'medieval', 'historical']):
            return "historical"
        if any(word in description for word in ['philosophy', 'philosophical', 'philosopher']):
            return "philosophical"
        if any(word in description for word in ['religion', 'religious', 'spiritual', 'sacred']):
            return "religious"
        
        # Fallback to entity type
        if entity_type == "WORK_OF_ART":
            return "artistic"
        if entity_type in ["PERSON", "ORG"]:
            return "biographical"
        if entity_type in ["GPE", "LOC"]:
            return "geographical"
        
        return "general"


# Singleton instance
wikipedia_service = WikipediaService()
