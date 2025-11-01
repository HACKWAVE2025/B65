from fastapi import FastAPI, HTTPException, Depends, status, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import uvicorn
import bcrypt
from jose import JWTError, jwt

from database import (
    get_db, init_db, save_analysis, get_analysis, get_all_analyses,
    get_cached_analysis, save_analysis_cache, get_cache_statistics,
    create_user, get_user_by_email, get_user_by_id
)
from gemini_service import gemini_service
from nlp_service import nlp_service

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    init_db()
    print("✅ Database initialized successfully")
    print("🚀 Cultural Context Analyzer API is running")
    yield
    # Shutdown (if needed)


# Initialize FastAPI app
app = FastAPI(
    title="Cultural Context Analyzer API",
    description="API for analyzing cultural and historical context in texts",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class AnalyzeRequest(BaseModel):
    text: str
    language: Optional[str] = "en"


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]


class AnalysisResponse(BaseModel):
    id: int
    input_text: str
    language: str
    cultural_origin: str
    cross_cultural_connections: str
    modern_analogy: str
    image_url: Optional[str]
    timeline_events: Optional[List[Dict[str, Any]]] = []
    geographic_locations: Optional[List[Dict[str, Any]]] = []
    key_concepts: Optional[List[Dict[str, Any]]] = []
    external_resources: Optional[Dict[str, Any]] = {}
    detected_entities: Optional[List[Dict[str, Any]]] = []
    created_at: datetime

    model_config = {"from_attributes": True}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify JWT token and return user"""
    try:
        # Handle case where security dependency doesn't extract credentials
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"🔐 Verifying token: {token[:20]}...")  # Debug log
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert string back to int for database lookup
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: invalid user ID format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"✅ Token verified for user {user_id}")
        return user
    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cultural Context Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/api/auth/register",
            "login": "/api/auth/login",
            "analyze": "/api/analyze",
            "history": "/api/history",
            "analysis": "/api/analysis/{id}"
        }
    }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint to prevent cold starts on Render
    
    This lightweight endpoint can be called by the frontend on page load
    to keep the backend warm and reduce response times for actual requests.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Cultural Context Analyzer API"
    }


@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register a new user
    
    Args:
        request: Registration data (name, email, phone, password)
    
    Returns:
        JWT token and user data
    """
    # Check if user already exists
    existing_user = get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password length
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Validate phone number (basic check)
    if not request.phone or len(request.phone.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number must be at least 10 characters"
        )
    
    try:
        # Hash password
        password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user_data = {
            'name': request.name,
            'email': request.email.lower(),
            'phone': request.phone,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat()
        }
        
        user = create_user(user_data)
        
        # Create access token (sub must be a string for JWT)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user['id'])}, expires_delta=access_token_expires
        )
        
        # Remove password hash from response
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except Exception as e:
        print(f"Error in register: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login user
    
    Args:
        request: Login credentials (email, password)
    
    Returns:
        JWT token and user data
    """
    # Get user by email
    user = get_user_by_email(request.email.lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not bcrypt.checkpw(request.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token (sub must be a string for JWT)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user['id'])}, expires_delta=access_token_expires
    )
    
    # Remove password hash from response
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@app.get("/api/auth/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current authenticated user"""
    user_response = {k: v for k, v in current_user.items() if k != 'password_hash'}
    return user_response


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_text(
    request: AnalyzeRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Analyze text for cultural context with NLP entity enrichment
    
    This endpoint uses Supabase persistent caching to reduce API calls:
    - Check Supabase cache (30-day TTL)
    - On cache miss, call Gemini API and save to cache
    - NLP entity detection runs every time for accuracy
    
    This endpoint:
    1. Identifies the cultural origin
    2. Finds cross-cultural connections
    3. Provides modern analogies
    4. Generates visualization descriptions
    5. Detects and enriches cultural entities
    """
    
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Text must be at least 10 characters long"
        )
    
    try:
        # Check Supabase persistent cache first
        print(f"🔍 Checking Supabase cache...")
        cached_result = get_cached_analysis(request.text, request.language or "en")
        
        if cached_result:
            print(f"🎯 Cache HIT! Skipping Gemini API call...")
            analysis_result = cached_result
        else:
            print(f"❌ Cache MISS. Calling Gemini API...")
            
            # Call Gemini API
            analysis_result = await gemini_service.analyze_cultural_context(
                text=request.text,
                language=request.language or "en"
            )
            
            # Save to Supabase cache for future requests
            print(f"💾 Saving to Supabase cache...")
            save_analysis_cache(request.text, request.language or "en", analysis_result)
        
        # Extract and enrich cultural entities with NLP (always runs for accuracy)
        print("🔍 Extracting cultural entities with NLP...")
        entity_analysis = nlp_service.analyze_text_with_entities(
            text=request.text,
            enrich_all=True
        )
        
        # Prepare data for Supabase
        analysis_data = {
            'input_text': request.text,
            'language': request.language,
            'cultural_origin': analysis_result["cultural_origin"],
            'cross_cultural_connections': analysis_result["cross_cultural_connections"],
            'modern_analogy': analysis_result["modern_analogy"],
            'image_url': None,  # Removed visualization feature
            'timeline_events': analysis_result.get("timeline_events", []),
            'geographic_locations': analysis_result.get("geographic_locations", []),
            'key_concepts': analysis_result.get("key_concepts", []),
            'external_resources': analysis_result.get("external_resources", {}),
            'detected_entities': entity_analysis.get("detected_entities", []),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save to Supabase with user_id
        saved_analysis = save_analysis(analysis_data, user_id=current_user['id'])
        
        print(f"✅ Analysis completed with {entity_analysis.get('enriched_count', 0)} enriched entities")
        
        return saved_analysis
        
    except Exception as e:
        print(f"Error in analyze_text: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing text: {str(e)}"
        )


class OCRResponse(BaseModel):
    success: bool
    text: str
    character_count: Optional[int] = None
    word_count: Optional[int] = None
    error: Optional[str] = None
    mime_type: Optional[str] = None


@app.post("/api/ocr/extract", response_model=OCRResponse)
async def extract_text_from_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(verify_token)
):
    """
    Extract text from uploaded image using Gemini Vision API
    
    Args:
        file: Image file (JPG, PNG, etc.)
    
    Returns:
        Extracted text and metadata
    """
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPG, PNG, etc.)"
        )
    
    # Read image data
    try:
        image_data = await file.read()
        
        if len(image_data) > 20 * 1024 * 1024:  # 20MB limit for Gemini
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Maximum size is 20MB."
            )
        
        # Extract text using Gemini Vision API
        result = await gemini_service.extract_text_from_image(
            image_data, 
            mime_type=file.content_type or "image/jpeg"
        )
        
        return OCRResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/api/analyze/image", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    language: str = Form(default='en'),
    current_user: dict = Depends(verify_token)
):
    """
    Extract text from image and analyze it for cultural context
    
    Args:
        file: Image file containing text
        language: Output language for analysis (default: 'en')
        current_user: Authenticated user (from token)
    
    Returns:
        Cultural analysis of the extracted text
    """
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPG, PNG, etc.)"
        )
    
    try:
        # Read image data
        image_data = await file.read()
        
        if len(image_data) > 20 * 1024 * 1024:  # 20MB limit for Gemini
            raise HTTPException(
                status_code=400,
                detail="Image file too large. Maximum size is 20MB."
            )
        
        # Extract text using Gemini Vision API
        print(f"📸 Extracting text from uploaded image using Gemini Vision...")
        ocr_result = await gemini_service.extract_text_from_image(
            image_data, 
            mime_type=file.content_type or "image/jpeg"
        )
        
        if not ocr_result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=ocr_result.get('error', 'Failed to extract text from image')
            )
        
        extracted_text = ocr_result.get('text', '').strip()
        
        if len(extracted_text) < 15:
            raise HTTPException(
                status_code=400,
                detail="Extracted text is too short (less than 15 characters). The image may only contain irrelevant text like watermarks or page numbers. Please upload an image with more content."
            )
        
        print(f"✅ Extracted {len(extracted_text)} characters from image")
        
        # Now analyze the extracted text using the regular analyze endpoint logic
        # Check Supabase persistent cache first
        print(f"🔍 Checking Supabase cache...")
        cached_result = get_cached_analysis(extracted_text, language or "en")
        
        if cached_result:
            print(f"🎯 Cache HIT! Skipping Gemini API call...")
            analysis_result = cached_result
        else:
            print(f"❌ Cache MISS. Calling Gemini API...")
            
            # Call Gemini API
            analysis_result = await gemini_service.analyze_cultural_context(
                text=extracted_text,
                language=language or "en"
            )
            
            # Save to Supabase cache for future requests
            print(f"💾 Saving to Supabase cache...")
            save_analysis_cache(extracted_text, language or "en", analysis_result)
        
        # Extract and enrich cultural entities with NLP
        print("🔍 Extracting cultural entities with NLP...")
        entity_analysis = nlp_service.analyze_text_with_entities(
            text=extracted_text,
            enrich_all=True
        )
        
        # Prepare data for Supabase
        analysis_data = {
            'input_text': extracted_text,
            'language': language,
            'cultural_origin': analysis_result["cultural_origin"],
            'cross_cultural_connections': analysis_result["cross_cultural_connections"],
            'modern_analogy': analysis_result["modern_analogy"],
            'image_url': None,
            'timeline_events': analysis_result.get("timeline_events", []),
            'geographic_locations': analysis_result.get("geographic_locations", []),
            'key_concepts': analysis_result.get("key_concepts", []),
            'external_resources': analysis_result.get("external_resources", {}),
            'detected_entities': entity_analysis.get("detected_entities", []),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save to Supabase with user_id
        saved_analysis = save_analysis(analysis_data, user_id=current_user['id'])
        
        print(f"✅ Analysis completed with {entity_analysis.get('enriched_count', 0)} enriched entities")
        
        return saved_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing image: {str(e)}"
        )


@app.get("/api/history", response_model=List[AnalysisResponse])
async def get_history(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(verify_token)
):
    """
    Get analysis history for the current user
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        current_user: Authenticated user (from token)
    
    Returns:
        List of analyses belonging to the current user
    """
    
    # Get user's analyses from Supabase (already ordered by created_at desc)
    analyses = get_all_analyses(limit=limit, user_id=current_user['id'])
    
    # Apply skip manually if needed
    if skip > 0:
        analyses = analyses[skip:]
    
    return analyses


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_by_id(
    analysis_id: int,
    current_user: dict = Depends(verify_token)
):
    """
    Get specific analysis by ID (only if owned by current user)
    
    Args:
        analysis_id: ID of the analysis to retrieve
        current_user: Authenticated user (from token)
    """
    
    analysis = get_analysis(analysis_id, user_id=current_user['id'])
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    return analysis


@app.delete("/api/analysis/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: dict = Depends(verify_token)
):
    """
    Delete specific analysis by ID (only if owned by current user)
    
    Args:
        analysis_id: ID of the analysis to delete
        current_user: Authenticated user (from token)
    """
    
    supabase = get_db()
    
    # Check if exists and belongs to user
    analysis = get_analysis(analysis_id, user_id=current_user['id'])
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {analysis_id} not found"
        )
    
    # Delete from Supabase (already verified ownership)
    try:
        supabase.table('analyses').delete().eq('id', analysis_id).eq('user_id', current_user['id']).execute()
        return {"message": f"Analysis {analysis_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting analysis: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """Get statistics about analyses"""
    
    # Get all analyses to compute stats
    all_analyses = get_all_analyses(limit=1000)
    
    total_analyses = len(all_analyses)
    
    # Get language distribution
    language_distribution = {}
    for analysis in all_analyses:
        lang = analysis.get('language', 'en')
        language_distribution[lang] = language_distribution.get(lang, 0) + 1
    
    return {
        "total_analyses": total_analyses,
        "language_distribution": language_distribution
    }


class EntityExtractionRequest(BaseModel):
    text: str


@app.post("/api/entities/extract")
async def extract_entities(request: EntityExtractionRequest):
    """
    Extract and enrich cultural entities from text on-demand
    
    Args:
        request: Text to extract entities from
    
    Returns:
        List of detected and enriched entities
    """
    
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Text must be at least 10 characters long"
        )
    
    try:
        result = nlp_service.analyze_text_with_entities(
            text=request.text,
            enrich_all=True
        )
        
        return {
            "entities": result["detected_entities"],
            "total_detected": result["total_detected"],
            "enriched_count": result["enriched_count"]
        }
        
    except Exception as e:
        print(f"Error extracting entities: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting entities: {str(e)}"
        )


@app.get("/api/entities/highlights")
async def get_entity_highlights(text: str):
    """
    Get entity highlights optimized for frontend display
    
    Args:
        text: Text to highlight (query parameter)
    
    Returns:
        List of highlight regions with tooltip data
    """
    
    if not text or len(text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Text must be at least 10 characters long"
        )
    
    try:
        highlights = nlp_service.get_entity_highlights(text)
        
        return {
            "highlights": highlights,
            "count": len(highlights)
        }
        
    except Exception as e:
        print(f"Error getting highlights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting highlights: {str(e)}"
        )


@app.get("/api/cache/stats")
async def get_cache_stats():
    """
    Get Supabase cache statistics
    
    Returns statistics for persistent Supabase cache:
    - Total cached entries
    - Cache hit counts
    - Hit rate percentage
    - Language distribution
    """
    
    try:
        # Get Supabase cache stats
        cache_stats = get_cache_statistics()
        
        return {
            "cache": cache_stats,
            "cache_info": {
                "type": "Supabase persistent cache",
                "ttl": "30 days",
                "scope": "Shared across all instances (cloud-ready)",
                "storage": "PostgreSQL JSONB columns"
            }
        }
        
    except Exception as e:
        print(f"Error fetching cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching cache statistics: {str(e)}"
        )


@app.post("/api/cache/clear")
async def clear_cache():
    """
    Clear expired Supabase cache entries
    
    Removes entries older than 30 days (or all if forced)
    
    Returns:
        Confirmation message with count of deleted entries
    """
    
    try:
        from database import cleanup_expired_cache
        deleted_count = cleanup_expired_cache(days_old=30)
        
        return {
            "message": "Cache cleared successfully",
            "entries_deleted": deleted_count,
            "cache_type": "supabase"
        }
        
    except Exception as e:
        print(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
