from datetime import datetime
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import hashlib

# Load environment variables
load_dotenv()

# Supabase connection configuration (NO PASSWORD NEEDED!)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project-ref.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "your-anon-key")

if not SUPABASE_URL or not SUPABASE_ANON_KEY or "your-" in SUPABASE_URL or "your-" in SUPABASE_ANON_KEY:
    raise ValueError(
        "❌ Missing Supabase configuration!\n"
        "Please add SUPABASE_URL and SUPABASE_ANON_KEY to your .env file.\n"
        "Get them from: Supabase Dashboard > Project Settings > API"
    )

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
print(f"✅ Connected to Supabase at {SUPABASE_URL}")


class Analysis:
    """Data model for cultural context analyses"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.input_text = kwargs.get('input_text')
        self.language = kwargs.get('language', 'en')
        self.cultural_origin = kwargs.get('cultural_origin')
        self.cross_cultural_connections = kwargs.get('cross_cultural_connections')
        self.modern_analogy = kwargs.get('modern_analogy')
        self.image_url = kwargs.get('image_url')
        self.timeline_events = kwargs.get('timeline_events', [])
        self.geographic_locations = kwargs.get('geographic_locations', [])
        self.key_concepts = kwargs.get('key_concepts', [])
        self.external_resources = kwargs.get('external_resources', {})
        self.detected_entities = kwargs.get('detected_entities', [])
        self.created_at = kwargs.get('created_at', datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Supabase insert"""
        return {
            'input_text': self.input_text,
            'language': self.language,
            'cultural_origin': self.cultural_origin,
            'cross_cultural_connections': self.cross_cultural_connections,
            'modern_analogy': self.modern_analogy,
            'image_url': self.image_url,
            'timeline_events': self.timeline_events,
            'geographic_locations': self.geographic_locations,
            'key_concepts': self.key_concepts,
            'external_resources': self.external_resources,
            'detected_entities': self.detected_entities,
            'created_at': self.created_at
        }


def init_db():
    """Initialize database tables - Not needed with Supabase (use SQL Editor instead)"""
    print("ℹ️  Using Supabase - Tables should be created via SQL Editor in Supabase Dashboard")
    print("ℹ️  Run the SQL script from supabase_setup.sql if you haven't already")


def save_analysis(analysis_data: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
    """Save analysis to Supabase"""
    try:
        if user_id:
            analysis_data['user_id'] = user_id
        response = supabase.table('analyses').insert(analysis_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error saving analysis: {e}")
        raise


def get_analysis(analysis_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Get analysis by ID from Supabase, optionally filtered by user_id"""
    try:
        query = supabase.table('analyses').select('*').eq('id', analysis_id)
        if user_id:
            query = query.eq('user_id', user_id)
        response = query.execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error fetching analysis: {e}")
        raise


def get_all_analyses(limit: int = 100, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get all analyses from Supabase, optionally filtered by user_id"""
    try:
        query = supabase.table('analyses').select('*')
        if user_id:
            query = query.eq('user_id', user_id)
        response = query.order('created_at', desc=True).limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error fetching analyses: {e}")
        raise


def get_db():
    """Dependency for database access - returns Supabase client"""
    return supabase


# Entity Cache Functions

def get_cached_entity(entity_name: str, entity_type: str) -> Optional[Dict[str, Any]]:
    """
    Get cached entity data from Supabase
    
    Args:
        entity_name: Name of the entity
        entity_type: Type of entity (PERSON, ORG, etc.)
    
    Returns:
        Cached entity data or None if not found
    """
    try:
        response = supabase.table('entity_cache').select('*').eq('entity_name', entity_name).eq('entity_type', entity_type).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error fetching cached entity: {e}")
        return None


def save_entity_cache(entity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Save entity enrichment data to cache
    
    Args:
        entity_data: Dictionary with entity information
    
    Returns:
        Saved entity record or None on error
    """
    try:
        # Use upsert to handle duplicates gracefully
        response = supabase.table('entity_cache').upsert(entity_data, on_conflict='entity_name,entity_type').execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error caching entity: {e}")
        return None


def get_all_cached_entities(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get all cached entities
    
    Args:
        limit: Maximum number of records
    
    Returns:
        List of cached entity records
    """
    try:
        response = supabase.table('entity_cache').select('*').order('created_at', desc=True).limit(limit).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error fetching cached entities: {e}")
        return []


def clear_old_entity_cache(days_old: int = 30):
    """
    Clear entity cache entries older than specified days
    
    Args:
        days_old: Number of days to keep in cache
    """
    try:
        from datetime import timedelta
        cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
        
        supabase.table('entity_cache').delete().lt('created_at', cutoff_date).execute()
        print(f"✅ Cleared entity cache entries older than {days_old} days")
    except Exception as e:
        print(f"❌ Error clearing old cache: {e}")


# Analysis Cache Functions (for Gemini API response caching)

def generate_text_hash(text: str, language: str) -> str:
    """
    Generate a consistent hash for text + language combination
    
    Args:
        text: Input text to hash
        language: Language code
    
    Returns:
        SHA-256 hash string
    """
    # Normalize text: lowercase, strip whitespace
    normalized_text = text.strip().lower()
    # Combine text and language for unique hash
    hash_input = f"{normalized_text}|{language}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()


def get_cached_analysis(text: str, language: str) -> Optional[Dict[str, Any]]:
    """
    Get cached Gemini analysis result
    
    Args:
        text: Input text
        language: Language code
    
    Returns:
        Cached analysis data or None if not found/expired
    """
    try:
        text_hash = generate_text_hash(text, language)
        
        # Query cache with TTL check (30 days)
        from datetime import timedelta
        cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        response = supabase.table('analysis_cache')\
            .select('*')\
            .eq('text_hash', text_hash)\
            .eq('language', language)\
            .gt('created_at', cutoff_date)\
            .execute()
        
        if response.data and len(response.data) > 0:
            cached_entry = response.data[0]
            
            # Increment hit count asynchronously
            try:
                supabase.rpc('increment_cache_hit', {'cache_id': cached_entry['id']}).execute()
            except:
                pass  # Don't fail if hit counter update fails
            
            print(f"🎯 Cache HIT for text_hash: {text_hash[:16]}... (Hit count: {cached_entry.get('hit_count', 0) + 1})")
            
            return {
                'cultural_origin': cached_entry['cultural_origin'],
                'cross_cultural_connections': cached_entry['cross_cultural_connections'],
                'modern_analogy': cached_entry['modern_analogy'],
                'timeline_events': cached_entry.get('timeline_events', []),
                'geographic_locations': cached_entry.get('geographic_locations', []),
                'key_concepts': cached_entry.get('key_concepts', []),
                'external_resources': cached_entry.get('external_resources', {}),
            }
        
        print(f"❌ Cache MISS for text_hash: {text_hash[:16]}...")
        return None
        
    except Exception as e:
        print(f"⚠️ Error checking analysis cache: {e}")
        return None  # Fail gracefully, don't block the request


def save_analysis_cache(text: str, language: str, analysis_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Save Gemini analysis result to cache
    
    Args:
        text: Original input text
        language: Language code
        analysis_result: Analysis data from Gemini
    
    Returns:
        Cached record or None on error
    """
    try:
        text_hash = generate_text_hash(text, language)
        
        cache_data = {
            'text_hash': text_hash,
            'language': language,
            'original_text': text[:5000],  # Store first 5000 chars for verification
            'cultural_origin': analysis_result['cultural_origin'],
            'cross_cultural_connections': analysis_result['cross_cultural_connections'],
            'modern_analogy': analysis_result['modern_analogy'],
            'timeline_events': analysis_result.get('timeline_events', []),
            'geographic_locations': analysis_result.get('geographic_locations', []),
            'key_concepts': analysis_result.get('key_concepts', []),
            'external_resources': analysis_result.get('external_resources', {}),
            'hit_count': 0,
            'created_at': datetime.utcnow().isoformat(),
            'last_accessed': datetime.utcnow().isoformat()
        }
        
        # Use upsert to handle duplicates (update if exists)
        response = supabase.table('analysis_cache')\
            .upsert(cache_data, on_conflict='text_hash,language')\
            .execute()
        
        print(f"💾 Cached analysis for text_hash: {text_hash[:16]}...")
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"⚠️ Error saving to analysis cache: {e}")
        return None  # Fail gracefully


def get_cache_statistics() -> Dict[str, Any]:
    """
    Get cache performance statistics
    
    Returns:
        Dictionary with cache stats
    """
    try:
        # Query the statistics view
        response = supabase.table('analysis_cache_stats').select('*').execute()
        
        if response.data and len(response.data) > 0:
            stats = response.data[0]
            
            # Calculate additional metrics
            total_hits = stats.get('total_cache_hits', 0)
            total_entries = stats.get('total_cached_entries', 0)
            
            return {
                'total_cached_entries': total_entries,
                'total_cache_hits': total_hits,
                'languages_cached': stats.get('languages_cached', 0),
                'avg_hits_per_entry': float(stats.get('avg_hits_per_entry', 0)) if stats.get('avg_hits_per_entry') else 0,
                'max_hits': stats.get('max_hits', 0),
                'oldest_entry': stats.get('oldest_entry'),
                'newest_entry': stats.get('newest_entry'),
                'entries_last_7_days': stats.get('entries_last_7_days', 0),
                'active_today': stats.get('active_today', 0),
                'cache_hit_rate': round((total_hits / total_entries * 100) if total_entries > 0 else 0, 2)
            }
        
        return {
            'total_cached_entries': 0,
            'total_cache_hits': 0,
            'languages_cached': 0,
            'cache_hit_rate': 0
        }
        
    except Exception as e:
        print(f"⚠️ Error fetching cache statistics: {e}")
        return {'error': str(e)}


def cleanup_expired_cache(days_old: int = 30) -> int:
    """
    Clean up expired cache entries
    
    Args:
        days_old: Age threshold in days
    
    Returns:
        Number of deleted entries
    """
    try:
        result = supabase.rpc('cleanup_analysis_cache').execute()
        deleted_count = result.data if result.data else 0
        print(f"🧹 Cleaned up {deleted_count} expired cache entries")
        return deleted_count
    except Exception as e:
        print(f"⚠️ Error cleaning up cache: {e}")
        return 0


# User Authentication Functions

def create_user(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new user in the database
    
    Args:
        user_data: Dictionary containing name, email, phone, password_hash
    
    Returns:
        Created user record or None on error
    """
    try:
        response = supabase.table('users').insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        raise


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user by email from Supabase
    
    Args:
        email: User's email address
    
    Returns:
        User record or None if not found
    """
    try:
        response = supabase.table('users').select('*').eq('email', email).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user by ID from Supabase
    
    Args:
        user_id: User's ID
    
    Returns:
        User record or None if not found
    """
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None
