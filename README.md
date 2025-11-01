# Cultural Context Analyzer

A full-stack educational application that analyzes cultural and historical context in texts using Google Gemini AI. Built with FastAPI (backend), React + Vite (frontend), and Supabase (PostgreSQL database).

## 🚀 Live Demo

**Website:** [https://hack-wave-one.vercel.app/](https://hack-wave-one.vercel.app/)

**Test Credentials:**
- **Username:** test@gmail.com
- **Password:** test@123

Try it out now to see cultural context analysis in action!

## Features

### Core Analysis
- **Cultural Origin Analysis**: Identifies the primary culture related to the text
- **Cross-Cultural Connections**: Shows how the content relates to other cultures
- **Modern Analogies**: Contemporary parallels with student-friendly references (social media, gaming, tech culture)
- **Visual Context**: AI-generated descriptions for visualization
- **Multi-language Support**: Supports 12+ regional languages
- **History Tracking**: Persistent storage of all analyses

### Enhanced Interactive Features
- 📅 **Interactive Timelines** - Chronological historical events with cultural significance
- 🗺️ **Geographic Maps** - Interactive location mapping with Google Maps integration
- 📖 **Pop-Out Explainers** - Detailed explanations for key cultural concepts
- 🔗 **External Resources** - Curated links to educational materials

### Multi-Source Verification (v2.1)
- 🌐 **5 Authoritative Sources** - Google Knowledge Graph, DBpedia, Wikidata, OpenLibrary, Wikipedia
- ✅ **Cross-Verification** - Information validated across multiple sources
- 📊 **Confidence Scores** - Reliability indicators for each piece of information
- 🔄 **Up-to-Date Data** - Fresh information from regularly updated sources

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with auto-reload
- **Supabase** - Cloud PostgreSQL database (Python client SDK)
- **Google Gemini API** - AI-powered cultural analysis (`gemini-2.5-flash` model)
- **Multi-Source APIs** - Knowledge Graph, DBpedia, Wikidata, OpenLibrary, Wikipedia
- **SpaCy** - Natural Language Processing for entity extraction

### Frontend
- **React 18** with hooks (single-component architecture)
- **Vite** - Fast build tool with HMR
- **TailwindCSS** - Utility-first styling
- **Lucide React** - Icon library
- **Axios** - HTTP client

## Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Supabase Account** (free tier available at [supabase.com](https://supabase.com))
- **Google Gemini API Key** (free at [Google AI Studio](https://makersuite.google.com/app/apikey))
- **(Optional)** Google Knowledge Graph API Key for enhanced verification

## Quick Start

### 1. Database Setup (Supabase)

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project (note the database password)
3. Go to **SQL Editor** and run this schema:

```sql
CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    language VARCHAR(10) NOT NULL,
    cultural_origin TEXT,
    cross_cultural_connections TEXT,
    modern_analogy TEXT,
    visualization_description TEXT,
    image_url TEXT,
    timeline_events JSONB DEFAULT '[]'::jsonb,
    geographic_locations JSONB DEFAULT '[]'::jsonb,
    key_concepts JSONB DEFAULT '[]'::jsonb,
    external_resources JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);
```

4. Get credentials from **Project Settings → Database**:
   - Host: `db.xxxxxxxxxxxxx.supabase.co`
   - Database name: `postgres`
   - User: `postgres`
   - Port: `5432`

### 2. Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download SpaCy model
python -m spacy download en_core_web_sm
```

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Connection
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here

# Optional: Multi-source verification
GOOGLE_KG_API_KEY=your_knowledge_graph_key
```

### 3. Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install
```

Create `frontend/.env` (optional):
```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend (Terminal 1)

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

Backend runs on: `http://localhost:8000` (auto-reload enabled)

### Start Frontend (Terminal 2)

```powershell
cd frontend
npm run dev
```

Frontend runs on: `http://localhost:5173` (hot module reload enabled)

## Database Management

### View Data via Supabase Dashboard
1. Go to your project on [supabase.com](https://supabase.com)
2. Navigate to **Table Editor** → `analyses`

### Useful SQL Queries (SQL Editor)
```sql
-- List all analyses
SELECT * FROM analyses ORDER BY created_at DESC;

-- View enhanced fields
SELECT id, input_text, 
       jsonb_array_length(timeline_events) as events_count,
       jsonb_array_length(geographic_locations) as locations_count
FROM analyses;

-- Delete specific analysis
DELETE FROM analyses WHERE id = 1;

-- Clear all data
TRUNCATE TABLE analyses RESTART IDENTITY;
```

## API Endpoints

### `POST /api/analyze`
Analyze text for cultural context with enhanced features.

**Request:**
```json
{
  "text": "Your text here",
  "language": "en"
}
```

**Response:**
```json
{
  "id": 1,
  "input_text": "...",
  "cultural_origin": "...",
  "cross_cultural_connections": "...",
  "modern_analogy": "...",
  "timeline_events": [
    {"year": "1500", "title": "...", "description": "...", "significance": "..."}
  ],
  "geographic_locations": [
    {"name": "...", "coordinates": {"lat": 0, "lng": 0}, "significance": "..."}
  ],
  "key_concepts": [
    {"term": "...", "definition": "...", "cultural_context": "...", "modern_parallel": "..."}
  ],
  "external_resources": {
    "timelines": ["url1", "url2"],
    "maps": ["url1"],
    "further_reading": ["url1"]
  },
  "created_at": "2024-01-01T00:00:00"
}
```

### `GET /api/history`
Retrieve all past analyses (newest first).

### `GET /api/analysis/{id}`
Get specific analysis by ID.

### `DELETE /api/analysis/{id}`
Delete analysis from database.

## Configuration

### Getting API Keys

**Gemini API (Required):**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Add to `backend/.env` as `GEMINI_API_KEY`

**Google Knowledge Graph API (Optional - for multi-source verification):**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Knowledge Graph Search API
3. Create credentials (API key)
4. Add to `backend/.env` as `GOOGLE_KG_API_KEY`

### Supported Languages
English (en), Hindi (hi), Sanskrit (sa), Tamil (ta), Telugu (te), Kannada (kn), Malayalam (ml), Marathi (mr), Bengali (bn), Gujarati (gu), Punjabi (pa), Urdu (ur), Japanese (ja), Korean (ko), Chinese (zh)

## Project Structure

```
cultural-context-analyzer/
├── backend/
│   ├── main.py                    # FastAPI app & API endpoints
│   ├── database.py                # Supabase client & models
│   ├── gemini_service.py          # AI analysis with structured JSON parsing
│   ├── multi_source_service.py    # Multi-source verification
│   ├── nlp_service.py             # SpaCy entity extraction
│   ├── wikipedia_service.py       # Wikipedia fallback
│   ├── requirements.txt           # Python dependencies
│   └── .env                       # Environment variables (gitignored)
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main component (all features)
│   │   ├── components/
│   │   │   ├── Analyzer.jsx       # Analysis UI
│   │   │   └── EntityHighlight.jsx # NLP highlighting
│   │   ├── main.jsx               # React entry point
│   │   └── index.css              # TailwindCSS styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Architecture & Key Concepts

### Data Flow
1. **User Input** → React component (`Analyzer.jsx`)
2. **API Call** → `POST /api/analyze` (FastAPI)
3. **AI Processing** → `gemini_service.analyze_cultural_context()`
4. **JSON Parsing** → Structured response extraction with regex cleaning
5. **Multi-Source Verification** → Optional cross-validation (v2.1)
6. **NLP Enrichment** → Entity extraction with SpaCy
7. **Database Save** → Supabase insert via Python client
8. **Response** → Enhanced analysis with ID
9. **UI Render** → Interactive timelines, maps, concept modals

### Critical Design Decisions
- **No authentication** - All analyses publicly stored (educational use)
- **CORS wide open** - `allow_origins=["*"]` for local dev
- **Synchronous DB calls** - Supabase client doesn't require async
- **Single frontend component** - All logic in `App.jsx` (manageable scale)
- **Conditional enhanced features** - Only populate when culturally relevant
- **Real URLs only** - External resources must be verified links

### Enhanced Features (v2.0+)

**📅 Timeline Events** - Only for historical context with dates/periods; focuses on cultural period, NOT author biography

**🗺️ Geographic Locations** - Only when specific places matter; includes GPS coordinates + Google Maps links

**📖 Key Concepts** - Only cultural/technical terms needing explanation; modal popups with modern parallels

**🔗 External Resources** - Only real, verified URLs from Khan Academy, National Geographic, etc.

**🌐 Multi-Source Verification (v2.1)** - Cross-validates information from 5 sources with confidence scores

## Troubleshooting

### Database Connection Issues
**Symptom:** `Error connecting to Supabase` or `relation "analyses" does not exist`

**Solutions:**
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `backend/.env`
- Check Supabase project is active (not paused)
- Run the table creation SQL in Supabase SQL Editor
- Test connection in Supabase dashboard first

### Gemini API Errors
**Symptom:** `Failed to analyze text` or `API key not valid`

**Solutions:**
- Verify `GEMINI_API_KEY` in `backend/.env` is correct
- Check quota limits at [Google AI Studio](https://makersuite.google.com)
- Ensure internet connection is active
- Try regenerating the API key

### JSON Parsing Failures
**Symptom:** Backend logs show `Failed to parse JSON response`

**Solutions:**
- Check backend terminal for AI response preview (first 500 chars)
- Gemini sometimes wraps JSON in markdown - parsing handles this
- Very long texts may exceed token limits - try shorter input
- Check `gemini_service.py` regex cleaning logic

### SpaCy Model Missing
**Symptom:** `Can't find model 'en_core_web_sm'`

**Solution:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m spacy download en_core_web_sm
```

### Port Already in Use
**Solutions:**
- **Backend:** Change `port=8000` in `main.py` line with `uvicorn.run()`
- **Frontend:** Change `server.port` in `vite.config.js` (default: 5173)
- Or kill the process using the port

### CORS Errors
**Symptom:** Frontend shows `blocked by CORS policy`

**Solution:** Backend already has `allow_origins=["*"]` - check `VITE_API_URL` in `frontend/.env` matches backend URL

## Development Tips

- **View logs:** Backend prints emoji-prefixed logs (✅ success, ❌ error, 🤖 AI response)
- **Test database:** Use Supabase Table Editor before blaming code
- **Inspect JSON:** Check backend terminal for AI response previews
- **Hot reload:** Both servers auto-reload on file changes
- **Clear cache:** Delete `.vite/` in frontend if UI seems stale

## Testing

**Manual testing checklist:**
- [ ] Try 3 example texts from different cultures/time periods
- [ ] Test all 12+ supported languages
- [ ] Verify timeline appears for historical content
- [ ] Check map shows for location-specific content
- [ ] Click concept explainers (modal popups)
- [ ] Test history delete functionality
- [ ] Verify multi-source verification (if API key set)
- [ ] Check entity highlighting (SpaCy NLP)

**No automated tests yet** - This is an educational project

## License

MIT License - See LICENSE file for details

## Contributing

This is an educational project. Feel free to fork and experiment!

**Key areas for improvement:**
- Add user authentication (Supabase Auth)
- Implement rate limiting for API
- Add automated tests (pytest for backend, Vitest for frontend)
- Optimize Gemini prompts for better accuracy
- Add more external source integrations
- Improve error handling and user feedback
