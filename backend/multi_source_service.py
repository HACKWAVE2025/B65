"""
Multi-Source Knowledge API Integration Service

Combines multiple authoritative sources to provide accurate, verified information:
- Google Knowledge Graph (primary - most accurate)
- DBpedia (structured Wikipedia data)
- Wikidata (structured knowledge base)
- OpenLibrary (for literary works)
- Wikipedia (fallback)

This service prioritizes accuracy and recency by cross-referencing multiple sources.
Supports both parallel (fast) and sequential (safe) API calls.
"""

import requests
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()


class MultiSourceService:
    """Service for fetching entity information from multiple authoritative sources"""
    
    def __init__(self):
        # API endpoints
        self.knowledge_graph_api = "https://kgsearch.googleapis.com/v1/entities:search"
        self.dbpedia_api = "https://dbpedia.org/sparql"
        self.wikidata_api = "https://www.wikidata.org/w/api.php"
        self.openlibrary_api = "https://openlibrary.org/search.json"
        
        # API keys (Knowledge Graph requires API key)
        self.kg_api_key = os.getenv("GOOGLE_KNOWLEDGE_GRAPH_API_KEY")
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 0.1  # 100ms between requests per service
        
        print("✅ Multi-Source Knowledge Service initialized")
        if not self.kg_api_key:
            print("⚠️  Google Knowledge Graph API key not found - will skip KG lookups")
    
    def _rate_limit(self, service_name: str, skip_for_parallel: bool = False):
        """Enforce rate limiting between API requests"""
        # Skip rate limiting for parallel requests (they're simultaneous anyway)
        if skip_for_parallel:
            return
        
        current_time = time.time()
        last_time = self.last_request_time.get(service_name, 0)
        time_since_last = current_time - last_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time[service_name] = time.time()
    
    def get_knowledge_graph_info(
        self, 
        entity_name: str, 
        entity_type: str = "Thing"
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch information from Google Knowledge Graph (most accurate)
        
        Args:
            entity_name: Name of the entity
            entity_type: Type hint for better results
        
        Returns:
            Dictionary with Knowledge Graph data or None
        """
        if not self.kg_api_key:
            return None
        
        try:
            self._rate_limit("knowledge_graph")
            
            params = {
                'query': entity_name,
                'key': self.kg_api_key,
                'limit': 1,
                'indent': True
            }
            
            if entity_type:
                # Map to schema.org types
                type_mapping = {
                    "PERSON": "Person",
                    "ORG": "Organization",
                    "GPE": "Place",
                    "LOC": "Place",
                    "EVENT": "Event",
                    "WORK_OF_ART": "CreativeWork"
                }
                params['types'] = type_mapping.get(entity_type, "Thing")
            
            response = requests.get(
                self.knowledge_graph_api,
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('itemListElement'):
                return None
            
            # Get first result
            element = data['itemListElement'][0]
            item = element['result']
            
            # Extract relevant information
            return {
                "entity_name": item.get('name', entity_name),
                "description": item.get('description', ''),
                "detailed_description": item.get('detailedDescription', {}).get('articleBody', ''),
                "url": item.get('detailedDescription', {}).get('url', ''),
                "image_url": item.get('image', {}).get('contentUrl', ''),
                "types": item.get('@type', []),
                "source": "Google Knowledge Graph",
                "confidence": element.get('resultScore', 0),  # Score is in element, not item
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Knowledge Graph error for '{entity_name}': {e}")
            return None
    
    def get_dbpedia_info(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch structured data from DBpedia (structured Wikipedia)
        
        Args:
            entity_name: Name of the entity
        
        Returns:
            Dictionary with DBpedia data or None
        """
        try:
            self._rate_limit("dbpedia")
            
            # DBpedia resource URI (replace spaces with underscores)
            resource_name = entity_name.replace(' ', '_')
            resource_uri = f"http://dbpedia.org/resource/{resource_name}"
            
            # SPARQL query to get basic info
            query = f"""
            SELECT DISTINCT ?abstract ?type WHERE {{
                <{resource_uri}> dbo:abstract ?abstract .
                <{resource_uri}> rdf:type ?type .
                FILTER (lang(?abstract) = 'en')
            }} LIMIT 1
            """
            
            params = {
                'query': query,
                'format': 'json'
            }
            
            response = requests.get(
                self.dbpedia_api,
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('results', {}).get('bindings'):
                return None
            
            result = data['results']['bindings'][0]
            
            return {
                "entity_name": entity_name,
                "abstract": result.get('abstract', {}).get('value', ''),
                "resource_uri": resource_uri,
                "source": "DBpedia",
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ DBpedia error for '{entity_name}': {e}")
            return None
    
    def get_wikidata_enhanced(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """
        Enhanced Wikidata lookup with more details
        
        Args:
            entity_name: Name of the entity
        
        Returns:
            Dictionary with enhanced Wikidata information
        """
        try:
            self._rate_limit("wikidata")
            
            # Search for entity
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
            
            entity = search_data['search'][0]
            entity_id = entity['id']
            
            # Get detailed entity data
            entity_params = {
                'action': 'wbgetentities',
                'ids': entity_id,
                'format': 'json',
                'languages': 'en',
                'props': 'labels|descriptions|claims|sitelinks'
            }
            
            detail_response = requests.get(
                self.wikidata_api,
                params=entity_params,
                timeout=5
            )
            
            if detail_response.status_code != 200:
                return None
            
            entity_data = detail_response.json()
            entity_details = entity_data['entities'][entity_id]
            
            return {
                "entity_name": entity_name,
                "wikidata_id": entity_id,
                "label": entity_details.get('labels', {}).get('en', {}).get('value', ''),
                "description": entity_details.get('descriptions', {}).get('en', {}).get('value', ''),
                "url": f"https://www.wikidata.org/wiki/{entity_id}",
                "wikipedia_url": self._get_wikipedia_url_from_sitelinks(entity_details.get('sitelinks', {})),
                "source": "Wikidata Enhanced",
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Wikidata Enhanced error for '{entity_name}': {e}")
            # Debug info (can be removed in production)
            import traceback
            print(f"   Debug: {traceback.format_exc()[:200]}")
            return None
    
    def _get_wikipedia_url_from_sitelinks(self, sitelinks: Dict) -> Optional[str]:
        """Extract Wikipedia URL from Wikidata sitelinks"""
        if 'enwiki' in sitelinks:
            title = sitelinks['enwiki']['title']
            return f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        return None
    
    def get_openlibrary_info(self, work_title: str) -> Optional[Dict[str, Any]]:
        """
        Fetch information about literary works from OpenLibrary
        
        Args:
            work_title: Title of the book/work
        
        Returns:
            Dictionary with OpenLibrary data or None
        """
        try:
            self._rate_limit("openlibrary")
            
            params = {
                'title': work_title,
                'limit': 1
            }
            
            response = requests.get(
                self.openlibrary_api,
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if not data.get('docs'):
                return None
            
            book = data['docs'][0]
            
            return {
                "title": book.get('title', work_title),
                "author": book.get('author_name', []),
                "first_publish_year": book.get('first_publish_year', ''),
                "subject": book.get('subject', [])[:5],  # Top 5 subjects
                "isbn": book.get('isbn', []),
                "cover_url": f"https://covers.openlibrary.org/b/id/{book.get('cover_i', '')}-M.jpg" if book.get('cover_i') else None,
                "url": f"https://openlibrary.org{book.get('key', '')}",
                "source": "OpenLibrary",
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ OpenLibrary error for '{work_title}': {e}")
            return None
    
    def get_comprehensive_info(
        self, 
        entity_name: str, 
        entity_type: str = "MISC",
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Get comprehensive information by querying multiple sources
        and combining/cross-referencing results
        
        Sources priority:
        1. Google Knowledge Graph (most accurate, authoritative)
        2. DBpedia (structured Wikipedia data)
        3. Wikidata Enhanced (broad coverage)
        4. OpenLibrary (for literary works)
        
        Args:
            entity_name: Name of the entity
            entity_type: Type of entity (PERSON, ORG, GPE, WORK_OF_ART, etc.)
            parallel: If True, queries APIs in parallel (faster). If False, sequential (default: True)
        
        Returns:
            Combined enriched data from multiple sources
        """
        if parallel:
            return self._get_comprehensive_info_parallel(entity_name, entity_type)
        else:
            return self._get_comprehensive_info_sequential(entity_name, entity_type)
    
    def _get_comprehensive_info_parallel(
        self, 
        entity_name: str, 
        entity_type: str = "MISC"
    ) -> Dict[str, Any]:
        """
        Parallel version - queries all APIs simultaneously (FAST!)
        Reduces latency significantly by making concurrent requests
        """
        print(f"🔍 Multi-source lookup (parallel) for: {entity_name} (type: {entity_type})")
        
        combined_data = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "summary": None,
            "description": None,
            "url": None,
            "sources_consulted": [],
            "confidence": "low",
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
        # Create wrapper functions that make actual API calls without rate limiting
        # (since they're running in parallel, rate limiting doesn't make sense)
        def fetch_kg():
            try:
                if not self.kg_api_key:
                    return None
                params = {
                    'query': entity_name,
                    'key': self.kg_api_key,
                    'limit': 1,
                    'indent': True
                }
                if entity_type:
                    type_mapping = {
                        "PERSON": "Person",
                        "ORG": "Organization",
                        "GPE": "Place",
                        "LOC": "Place",
                        "EVENT": "Event",
                        "WORK_OF_ART": "CreativeWork"
                    }
                    params['types'] = type_mapping.get(entity_type, "Thing")
                
                response = requests.get(self.knowledge_graph_api, params=params, timeout=5)
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if not data.get('itemListElement'):
                    return None
                
                element = data['itemListElement'][0]
                item = element['result']
                
                return {
                    "entity_name": item.get('name', entity_name),
                    "description": item.get('description', ''),
                    "detailed_description": item.get('detailedDescription', {}).get('articleBody', ''),
                    "url": item.get('detailedDescription', {}).get('url', ''),
                    "image_url": item.get('image', {}).get('contentUrl', ''),
                    "types": item.get('@type', []),
                    "source": "Google Knowledge Graph",
                    "confidence": element.get('resultScore', 0),
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                print(f"  ⚠️  KG error: {e}")
                return None
        
        def fetch_dbpedia():
            try:
                resource_name = entity_name.replace(' ', '_')
                resource_uri = f"http://dbpedia.org/resource/{resource_name}"
                
                query = f"""
                SELECT DISTINCT ?abstract ?type WHERE {{
                    <{resource_uri}> dbo:abstract ?abstract .
                    <{resource_uri}> rdf:type ?type .
                    FILTER (lang(?abstract) = 'en')
                }} LIMIT 1
                """
                
                response = requests.get(
                    self.dbpedia_api,
                    params={'query': query, 'format': 'json'},
                    timeout=5
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if not data.get('results', {}).get('bindings'):
                    return None
                
                result = data['results']['bindings'][0]
                return {
                    "entity_name": entity_name,
                    "abstract": result.get('abstract', {}).get('value', ''),
                    "resource_uri": resource_uri,
                    "source": "DBpedia",
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                print(f"  ⚠️  DBpedia error: {e}")
                return None
        
        def fetch_wikidata():
            try:
                search_params = {
                    'action': 'wbsearchentities',
                    'search': entity_name,
                    'language': 'en',
                    'format': 'json',
                    'limit': 1
                }
                
                response = requests.get(self.wikidata_api, params=search_params, timeout=5)
                if response.status_code != 200:
                    return None
                
                search_data = response.json()
                if not search_data.get('search'):
                    return None
                
                entity = search_data['search'][0]
                entity_id = entity['id']
                
                entity_params = {
                    'action': 'wbgetentities',
                    'ids': entity_id,
                    'format': 'json',
                    'languages': 'en',
                    'props': 'labels|descriptions|claims|sitelinks'
                }
                
                detail_response = requests.get(self.wikidata_api, params=entity_params, timeout=5)
                if detail_response.status_code != 200:
                    return None
                
                entity_data = detail_response.json()
                entity_details = entity_data['entities'][entity_id]
                
                sitelinks = entity_details.get('sitelinks', {})
                wikipedia_url = None
                if 'enwiki' in sitelinks:
                    title = sitelinks['enwiki']['title']
                    wikipedia_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                
                return {
                    "entity_name": entity_name,
                    "wikidata_id": entity_id,
                    "label": entity_details.get('labels', {}).get('en', {}).get('value', ''),
                    "description": entity_details.get('descriptions', {}).get('en', {}).get('value', ''),
                    "url": f"https://www.wikidata.org/wiki/{entity_id}",
                    "wikipedia_url": wikipedia_url,
                    "source": "Wikidata Enhanced",
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                print(f"  ⚠️  Wikidata error: {e}")
                return None
        
        def fetch_openlibrary():
            try:
                response = requests.get(
                    self.openlibrary_api,
                    params={'title': entity_name, 'limit': 1},
                    timeout=5
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                if not data.get('docs'):
                    return None
                
                book = data['docs'][0]
                return {
                    "title": book.get('title', entity_name),
                    "author": book.get('author_name', []),
                    "first_publish_year": book.get('first_publish_year', ''),
                    "subject": book.get('subject', [])[:5],
                    "isbn": book.get('isbn', []),
                    "cover_url": f"https://covers.openlibrary.org/b/id/{book.get('cover_i', '')}-M.jpg" if book.get('cover_i') else None,
                    "url": f"https://openlibrary.org{book.get('key', '')}",
                    "source": "OpenLibrary",
                    "retrieved_at": datetime.utcnow().isoformat()
                }
            except Exception as e:
                print(f"  ⚠️  OpenLibrary error: {e}")
                return None
        
        # Execute all tasks in parallel using ThreadPoolExecutor
        tasks = {
            'kg': fetch_kg,
            'dbpedia': fetch_dbpedia,
            'wikidata': fetch_wikidata,
        }
        
        # Add OpenLibrary for literary works
        if entity_type == "WORK_OF_ART" or any(keyword in entity_name.lower() for keyword in ['book', 'novel', 'play']):
            tasks['openlibrary'] = fetch_openlibrary
        
        results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_source = {executor.submit(task): source for source, task in tasks.items()}
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results[source] = future.result()
                except Exception as e:
                    print(f"  ⚠️  Error in {source}: {e}")
                    results[source] = None
        
        # Process results (same logic as sequential, but from parallel results)
        
        # 1. Google Knowledge Graph
        kg_data = results.get('kg')
        if kg_data:
            combined_data["sources_consulted"].append("Google Knowledge Graph")
            combined_data["summary"] = kg_data.get("detailed_description") or kg_data.get("description")
            combined_data["description"] = kg_data.get("description")
            combined_data["url"] = kg_data.get("url")
            combined_data["image_url"] = kg_data.get("image_url")
            combined_data["confidence"] = "very high"
            combined_data["kg_confidence_score"] = kg_data.get("confidence", 0)
            print(f"  ✅ Found in Knowledge Graph (confidence: {kg_data.get('confidence', 0)})")
        
        # 2. DBpedia
        dbpedia_data = results.get('dbpedia')
        if dbpedia_data:
            combined_data["sources_consulted"].append("DBpedia")
            if not combined_data.get("summary"):
                combined_data["summary"] = dbpedia_data.get("abstract", "")[:500]
            combined_data["dbpedia_uri"] = dbpedia_data.get("resource_uri")
            if combined_data["confidence"] == "low":
                combined_data["confidence"] = "high"
            print(f"  ✅ Found in DBpedia")
        
        # 3. Wikidata
        wikidata_data = results.get('wikidata')
        if wikidata_data:
            combined_data["sources_consulted"].append("Wikidata")
            if not combined_data.get("description"):
                combined_data["description"] = wikidata_data.get("description")
            if not combined_data.get("url") and wikidata_data.get("wikipedia_url"):
                combined_data["url"] = wikidata_data.get("wikipedia_url")
            combined_data["wikidata_id"] = wikidata_data.get("wikidata_id")
            if combined_data["confidence"] == "low":
                combined_data["confidence"] = "medium"
            print(f"  ✅ Found in Wikidata")
        
        # 4. OpenLibrary
        ol_data = results.get('openlibrary')
        if ol_data:
            combined_data["sources_consulted"].append("OpenLibrary")
            combined_data["literary_info"] = ol_data
            if combined_data["confidence"] == "low":
                combined_data["confidence"] = "medium"
            print(f"  ✅ Found in OpenLibrary")
        
        # Determine confidence
        num_sources = len(combined_data["sources_consulted"])
        if num_sources >= 3:
            combined_data["confidence"] = "very high (cross-verified)"
        elif num_sources == 2:
            combined_data["confidence"] = "high (verified)"
        elif num_sources == 1 and "Google Knowledge Graph" in combined_data["sources_consulted"]:
            combined_data["confidence"] = "high"
        
        if num_sources == 0:
            combined_data["summary"] = "No information found in authoritative sources"
            combined_data["confidence"] = "none"
            print(f"  ❌ Not found in any source")
        
        print(f"  📊 Sources consulted: {num_sources}, Confidence: {combined_data['confidence']}")
        
        return combined_data
    
    def _get_comprehensive_info_sequential(
        self, 
        entity_name: str, 
        entity_type: str = "MISC"
    ) -> Dict[str, Any]:
        """
        Sequential version - queries APIs one by one (SLOWER but safer)
        Use this if you encounter rate limiting issues
        """
        print(f"🔍 Multi-source lookup (sequential) for: {entity_name} (type: {entity_type})")
        
        combined_data = {
            "entity_name": entity_name,
            "entity_type": entity_type,
            "summary": None,
            "description": None,
            "url": None,
            "sources_consulted": [],
            "confidence": "low",
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
        # 1. Try Google Knowledge Graph first (highest quality)
        kg_data = self.get_knowledge_graph_info(entity_name, entity_type)
        if kg_data:
            combined_data["sources_consulted"].append("Google Knowledge Graph")
            combined_data["summary"] = kg_data.get("detailed_description") or kg_data.get("description")
            combined_data["description"] = kg_data.get("description")
            combined_data["url"] = kg_data.get("url")
            combined_data["image_url"] = kg_data.get("image_url")
            combined_data["confidence"] = "very high"
            combined_data["kg_confidence_score"] = kg_data.get("confidence", 0)
            print(f"  ✅ Found in Knowledge Graph (confidence: {kg_data.get('confidence', 0)})")
        
        # 2. Try DBpedia (structured Wikipedia)
        dbpedia_data = self.get_dbpedia_info(entity_name)
        if dbpedia_data:
            combined_data["sources_consulted"].append("DBpedia")
            # Use DBpedia abstract if KG didn't provide detailed description
            if not combined_data.get("summary"):
                combined_data["summary"] = dbpedia_data.get("abstract", "")[:500]  # Limit length
            combined_data["dbpedia_uri"] = dbpedia_data.get("resource_uri")
            if combined_data["confidence"] == "low":
                combined_data["confidence"] = "high"
            print(f"  ✅ Found in DBpedia")
        
        # 3. Try Wikidata Enhanced
        wikidata_data = self.get_wikidata_enhanced(entity_name)
        if wikidata_data:
            combined_data["sources_consulted"].append("Wikidata")
            # Use Wikidata description if nothing else available
            if not combined_data.get("description"):
                combined_data["description"] = wikidata_data.get("description")
            if not combined_data.get("url") and wikidata_data.get("wikipedia_url"):
                combined_data["url"] = wikidata_data.get("wikipedia_url")
            combined_data["wikidata_id"] = wikidata_data.get("wikidata_id")
            if combined_data["confidence"] == "low":
                combined_data["confidence"] = "medium"
            print(f"  ✅ Found in Wikidata")
        
        # 4. For literary works, try OpenLibrary
        if entity_type == "WORK_OF_ART" or any(keyword in entity_name.lower() for keyword in ['book', 'novel', 'play']):
            ol_data = self.get_openlibrary_info(entity_name)
            if ol_data:
                combined_data["sources_consulted"].append("OpenLibrary")
                combined_data["literary_info"] = ol_data
                if combined_data["confidence"] == "low":
                    combined_data["confidence"] = "medium"
                print(f"  ✅ Found in OpenLibrary")
        
        # Determine overall confidence based on number of sources
        num_sources = len(combined_data["sources_consulted"])
        if num_sources >= 3:
            combined_data["confidence"] = "very high (cross-verified)"
        elif num_sources == 2:
            combined_data["confidence"] = "high (verified)"
        elif num_sources == 1 and "Google Knowledge Graph" in combined_data["sources_consulted"]:
            combined_data["confidence"] = "high"
        
        # If no sources found anything
        if num_sources == 0:
            combined_data["summary"] = "No information found in authoritative sources"
            combined_data["confidence"] = "none"
            print(f"  ❌ Not found in any source")
        
        print(f"  📊 Sources consulted: {num_sources}, Confidence: {combined_data['confidence']}")
        
        return combined_data


# Singleton instance
multi_source_service = MultiSourceService()
