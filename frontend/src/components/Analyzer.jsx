import React, { useState, useEffect } from 'react';
import axiosInstance from '../utils/axiosConfig';
import ReactMarkdown from 'react-markdown';
import {
  BookOpen,
  Globe,
  Lightbulb,
  History,
  Loader2,
  Send,
  Trash2,
  Clock,
  Languages,
  MapPin,
  Calendar,
  BookMarked,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Info,
  X,
  Sparkles,
  LogOut,
  User,
  Volume2,
  VolumeX,
  Pause,
  Upload,
  Image as ImageIcon,
  X as XIcon,
  Mic,
  MicOff,
  Paperclip
} from 'lucide-react';
import { EntityHighlight, EntityLegend, EntitySummary } from './EntityHighlight';
import { speakText, stopSpeaking, isSpeaking, pauseSpeaking, resumeSpeaking } from '../utils/textToSpeech';
import speechToText, { getSpeechLanguageCode } from '../utils/speechToText';

function Analyzer() {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [error, setError] = useState(null);
  const [expandedConcept, setExpandedConcept] = useState(null);
  const [showTimeline, setShowTimeline] = useState(false);
  const [showMap, setShowMap] = useState(false);
  const [user, setUser] = useState(null);
  const [speakingSection, setSpeakingSection] = useState(null);
  const [speechPaused, setSpeechPaused] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [extractedText, setExtractedText] = useState('');
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState('');

  // Load user from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Fetch history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axiosInstance.get('/api/history?limit=10');
      setHistory(response.data);
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();

    if (!text.trim() || text.trim().length < 10) {
      setError('Please enter at least 10 characters of text to analyze.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axiosInstance.post('/api/analyze', {
        text: text.trim(),
        language: language
      });

      setResult(response.data);
      fetchHistory(); // Refresh history

    } catch (err) {
      console.error('Error analyzing text:', err);
      setError(err.response?.data?.detail || 'Failed to analyze text. Please check your API connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (item) => {
    setText(item.input_text);
    setLanguage(item.language);
    setResult(item);
    setShowHistory(false);
  };

  const handleDeleteHistory = async (id, e) => {
    e.stopPropagation();
    try {
      await axiosInstance.delete(`/api/analysis/${id}`);
      fetchHistory();
      if (result?.id === id) {
        setResult(null);
      }
    } catch (err) {
      console.error('Error deleting analysis:', err);
    }
  };

  const handleLogout = () => {
    stopSpeaking(); // Stop any ongoing speech
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  const handleSpeak = (text, sectionName) => {
    if (speakingSection === sectionName && isSpeaking()) {
      // If already speaking this section, pause/resume
      if (speechPaused) {
        resumeSpeaking();
        setSpeechPaused(false);
      } else {
        pauseSpeaking();
        setSpeechPaused(true);
      }
    } else {
      // Stop any current speech and start new
      stopSpeaking();
      setSpeakingSection(sectionName);
      setSpeechPaused(false);

      speakText(text, language, () => {
        // On end callback
        setSpeakingSection(null);
        setSpeechPaused(false);
      });
    }
  };

  const handleStopSpeaking = () => {
    stopSpeaking();
    setSpeakingSection(null);
    setSpeechPaused(false);
  };

  const handleStartRecording = () => {
    if (!speechToText.isSupported()) {
      setError('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    setIsRecording(true);
    setError(null);
    setInterimTranscript('');

    const speechLangCode = getSpeechLanguageCode(language);

    speechToText.start(
      speechLangCode,
      (result) => {
        // Handle speech result
        if (result.isFinal && result.finalTranscript) {
          // Append final transcript to existing text
          setText(prev => {
            const newText = prev ? prev + ' ' + result.finalTranscript : result.finalTranscript;
            return newText;
          });
          setInterimTranscript('');
        } else if (result.interimTranscript) {
          // Show interim results
          setInterimTranscript(result.interimTranscript);
        }
      },
      (error) => {
        // Handle error
        console.error('Speech recognition error:', error);
        setIsRecording(false);
        setInterimTranscript('');

        if (error === 'no-speech') {
          setError('No speech detected. Please try again.');
        } else if (error === 'not-allowed') {
          setError('Microphone access denied. Please allow microphone access in your browser settings.');
        } else {
          setError('Speech recognition error. Please try again.');
        }
      },
      () => {
        // Handle end
        setIsRecording(false);
        setInterimTranscript('');
      }
    );
  };

  const handleStopRecording = () => {
    speechToText.stop();
    setIsRecording(false);
    setInterimTranscript('');
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file (JPG, PNG, etc.)');
        return;
      }
      if (file.size > 20 * 1024 * 1024) {
        setError('Image file too large. Maximum size is 20MB.');
        return;
      }
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleRemoveImage = () => {
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
    setSelectedImage(null);
    setImagePreview(null);
    setExtractedText('');
    setError(null);
  };

  const handleExtractText = async () => {
    if (!selectedImage) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);

      const response = await axiosInstance.post('/api/ocr/extract', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setExtractedText(response.data.text);
        setText(response.data.text);
      } else {
        setError(response.data.error || 'Failed to extract text from image');
      }
    } catch (err) {
      console.error('Error extracting text:', err);
      setError(err.response?.data?.detail || 'Failed to extract text from image. Please check your API connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeImage = async (e) => {
    e.preventDefault();

    if (!selectedImage) {
      setError('Please upload an image first');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedImage);
      formData.append('language', language);

      const response = await axiosInstance.post('/api/analyze/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      if (response.data.input_text) {
        setExtractedText(response.data.input_text);
        setText(response.data.input_text);
      }
      fetchHistory(); // Refresh history

    } catch (err) {
      console.error('Error analyzing image:', err);
      setError(err.response?.data?.detail || 'Failed to analyze image. Please check your API connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopSpeaking();
      speechToText.stop();
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi (हिंदी)' },
    { code: 'es', name: 'Spanish (Español)' },
    { code: 'fr', name: 'French (Français)' },
    { code: 'de', name: 'German (Deutsch)' },
    { code: 'zh', name: 'Chinese (中文)' },
    { code: 'ja', name: 'Japanese (日本語)' },
    { code: 'ar', name: 'Arabic (العربية)' },
    { code: 'bn', name: 'Bengali (বাংলা)' },
    { code: 'ta', name: 'Tamil (தமிழ்)' },
    { code: 'te', name: 'Telugu (తెలుగు)' },
    { code: 'mr', name: 'Marathi (मराठी)' },
  ];

  const exampleTexts = [
    "After years of success, the company finally met its Waterloo when the new product failed.",
    "The Ramayana is an ancient Indian epic that tells the story of Prince Rama's quest to rescue his wife Sita from the demon king Ravana.",
    "పోతన రచించిన తెలుగు భాగవతం ఒక పవిత్రమైన ఆధ్యాత్మిక గ్రంథం, ఇది విష్ణువు యొక్క అవతారాల కథలను అందమైన తెలుగు కవిత్వంలో వివరిస్తుంది.",
  ];

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header with User Info */}
        <div className="mb-6 flex justify-end">
          {user && (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-gray-700">
                <User className="w-4 h-4" />
                <span className="text-sm font-medium">{user.name}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                style={{ backgroundColor: '#e6f7f9', color: '#0A5569' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#ccf2f6'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#e6f7f9'}
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          )}
        </div>

        {/* Hero Section */}
        <header className="text-center mb-20">
          <div className="max-w-4xl mx-auto">
            {/* Main title - clean and professional */}
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 tracking-tight"
              style={{ color: '#0A5569', lineHeight: '1.1' }}>
              Cultural Context Analyzer
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-gray-600 mb-8 font-light leading-relaxed">
              AI-powered insights into the cultural heritage of literature and historical texts
            </p>

            {/* Stats/Features - clean grid */}
            <div className="grid grid-cols-1 gap-6 max-w-2xl mx-auto mt-12">
              <div className="text-center">
                <div className="text-3xl font-bold mb-2" style={{ color: '#0A5569' }}>12+</div>
                <div className="text-sm text-gray-600 font-medium">Languages</div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Section */}
          <div className="lg:col-span-2">
            <div className="card">
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl font-bold text-gray-800">
                  Enter Text to Analyze
                </h2>
              </div>

              <form onSubmit={handleAnalyze} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Output Language
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="input-field"
                  >
                    {languages.map(lang => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-xs text-gray-500">
                    The analysis results will be displayed in <strong>{languages.find(l => l.code === language)?.name || language}</strong>
                  </p>
                </div>

                {/* Hidden file input */}
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="hidden"
                  id="image-attach"
                  disabled={loading}
                />

                {/* Image Preview (if image selected) */}
                {imagePreview && (
                  <div className="relative border-2 rounded-lg p-3" style={{ borderColor: '#b3dfe6', backgroundColor: '#f0f9fa' }}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium" style={{ color: '#0A5569' }}>
                        <ImageIcon className="w-4 h-4 inline mr-1" />
                        Attached Image
                      </span>
                      <button
                        type="button"
                        onClick={handleRemoveImage}
                        className="p-1 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors"
                        title="Remove image"
                      >
                        <XIcon className="w-4 h-4" />
                      </button>
                    </div>
                    <img
                      src={imagePreview}
                      alt="Preview"
                      className="w-full max-h-48 object-contain rounded-lg border bg-white"
                      style={{ borderColor: '#b3dfe6' }}
                    />
                    <div className="mt-2 flex gap-2">
                      <button
                        type="button"
                        onClick={handleExtractText}
                        disabled={loading}
                        className="flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                        style={{ backgroundColor: '#e6f7f9', color: '#0A5569' }}
                      >
                        {loading ? 'Extracting...' : 'Extract Text Only'}
                      </button>
                      <button
                        type="button"
                        onClick={handleAnalyzeImage}
                        disabled={loading}
                        className="flex-1 px-3 py-2 rounded-lg text-sm font-medium text-white transition-colors"
                        style={{ backgroundColor: '#0A5569' }}
                      >
                        {loading ? 'Analyzing...' : 'Extract & Analyze'}
                      </button>
                    </div>
                    {extractedText && (
                      <div className="mt-2 p-2 rounded bg-white text-sm text-gray-700 max-h-32 overflow-y-auto border" style={{ borderColor: '#b3dfe6' }}>
                        <p className="font-semibold mb-1 text-xs">Extracted Text ({extractedText.length} chars):</p>
                        <p className="text-xs">{extractedText}</p>
                      </div>
                    )}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Text or Passage
                  </label>
                  <div className="relative">
                    <textarea
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      placeholder="Enter a poem, historical text, cultural reference, or any passage you'd like to understand better... Use the attachment icon to add an image, or the microphone to speak!"
                      className="input-field min-h-[200px] resize-y pr-28"
                      disabled={loading}
                    />
                    {/* Action Buttons - Attachment and Microphone */}
                    <div className="absolute bottom-3 right-3 flex gap-2">
                      {/* Attachment/Image Button */}
                      <label
                        htmlFor="image-attach"
                        className={`p-3 rounded-full transition-all cursor-pointer ${imagePreview ? 'bg-green-500 text-white' : 'hover:bg-gray-100'
                          }`}
                        style={{
                          backgroundColor: imagePreview ? '#10b981' : '#e6f7f9',
                          color: imagePreview ? 'white' : '#0A5569'
                        }}
                        title={imagePreview ? 'Image attached' : 'Attach image'}
                      >
                        <Paperclip className="w-5 h-5" />
                      </label>

                      {/* Microphone Button */}
                      <button
                        type="button"
                        onClick={isRecording ? handleStopRecording : handleStartRecording}
                        disabled={loading}
                        className={`p-3 rounded-full transition-all ${isRecording
                          ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                          : 'hover:bg-gray-100'
                          }`}
                        style={{
                          backgroundColor: isRecording ? '#ef4444' : '#e6f7f9',
                          color: isRecording ? 'white' : '#0A5569'
                        }}
                        title={isRecording ? 'Stop recording' : 'Start voice input'}
                      >
                        {isRecording ? (
                          <MicOff className="w-5 h-5" />
                        ) : (
                          <Mic className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>
                  {/* Interim transcript display */}
                  {isRecording && interimTranscript && (
                    <div className="mt-2 p-3 rounded-lg border-2" style={{ borderColor: '#b3dfe6', backgroundColor: '#f0f9fa' }}>
                      <div className="flex items-center gap-2 mb-1">
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                          <span className="text-xs font-semibold" style={{ color: '#0A5569' }}>Listening...</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 italic">{interimTranscript}</p>
                    </div>
                  )}
                  {isRecording && !interimTranscript && (
                    <div className="mt-2 p-3 rounded-lg border-2" style={{ borderColor: '#b3dfe6', backgroundColor: '#f0f9fa' }}>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                        <span className="text-xs font-semibold" style={{ color: '#0A5569' }}>Recording... Speak now</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Example Texts */}
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Try an example:</p>
                  <div className="flex flex-wrap gap-2">
                    {exampleTexts.map((example, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setText(example)}
                        className="text-xs px-3 py-1 rounded-full transition-colors"
                        style={{ backgroundColor: '#e6f7f9', color: '#0A5569' }}
                        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#ccf2f6'}
                        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#e6f7f9'}
                        disabled={loading}
                      >
                        Example {idx + 1}
                      </button>
                    ))}
                  </div>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || !text.trim()}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze Text
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Results Section */}
            {result && (
              <div className="mt-6 space-y-4 animate-fade-in">
                {/* Stop All Speech Button */}
                {(speakingSection !== null) && (
                  <div className="flex justify-end mb-2">
                    <button
                      onClick={handleStopSpeaking}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-red-50 text-red-700 hover:bg-red-100"
                      title="Stop reading"
                    >
                      <VolumeX className="w-4 h-4" />
                      Stop Reading
                    </button>
                  </div>
                )}
                {/* Entity Highlights Section */}
                {result.detected_entities && result.detected_entities.length > 0 && (
                  <>
                    <EntitySummary entities={result.detected_entities} />

                    <div className="section-card">
                      <div className="flex items-start gap-4">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-800 mb-3">
                            ✨ Interactive Cultural Context
                          </h3>
                          <EntityLegend />
                          <div className="bg-white p-4 rounded-lg border-2" style={{ borderColor: '#b3dfe6' }}>
                            <EntityHighlight
                              text={result.input_text}
                              entities={result.detected_entities}
                            />
                          </div>
                          <p className="text-xs text-gray-500 mt-2 italic">
                            💡 Hover over highlighted terms to see cultural background from Wikipedia
                          </p>
                        </div>
                      </div>
                    </div>
                  </>
                )}

                {/* Cultural Origin */}
                <div className="section-card">
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xl font-bold text-gray-800">
                          1. Cultural Origin
                        </h3>
                        <button
                          onClick={() => handleSpeak(result.cultural_origin, 'cultural_origin')}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                          style={{
                            backgroundColor: speakingSection === 'cultural_origin' ? '#0A5569' : '#e6f7f9',
                            color: speakingSection === 'cultural_origin' ? 'white' : '#0A5569'
                          }}
                          title={speakingSection === 'cultural_origin' ? (speechPaused ? 'Resume' : 'Pause') : 'Read aloud'}
                        >
                          {speakingSection === 'cultural_origin' ? (
                            speechPaused ? (
                              <Volume2 className="w-4 h-4" />
                            ) : (
                              <Pause className="w-4 h-4" />
                            )
                          ) : (
                            <Volume2 className="w-4 h-4" />
                          )}
                          {speakingSection === 'cultural_origin' ? (speechPaused ? 'Resume' : 'Pause') : 'Read'}
                        </button>
                      </div>
                      <div className="text-gray-700 leading-relaxed prose prose-sm max-w-none">
                        <ReactMarkdown>{result.cultural_origin}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Cross-Cultural Connections */}
                <div className="section-card">
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xl font-bold text-gray-800">
                          2. Cross-Cultural Connections
                        </h3>
                        <button
                          onClick={() => handleSpeak(result.cross_cultural_connections, 'cross_cultural')}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                          style={{
                            backgroundColor: speakingSection === 'cross_cultural' ? '#0A5569' : '#e6f7f9',
                            color: speakingSection === 'cross_cultural' ? 'white' : '#0A5569'
                          }}
                          title={speakingSection === 'cross_cultural' ? (speechPaused ? 'Resume' : 'Pause') : 'Read aloud'}
                        >
                          {speakingSection === 'cross_cultural' ? (
                            speechPaused ? (
                              <Volume2 className="w-4 h-4" />
                            ) : (
                              <Pause className="w-4 h-4" />
                            )
                          ) : (
                            <Volume2 className="w-4 h-4" />
                          )}
                          {speakingSection === 'cross_cultural' ? (speechPaused ? 'Resume' : 'Pause') : 'Read'}
                        </button>
                      </div>
                      <div className="text-gray-700 leading-relaxed prose prose-sm max-w-none">
                        <ReactMarkdown>{result.cross_cultural_connections}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Modern Analogy */}
                <div className="section-card">
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xl font-bold text-gray-800">
                          3. Modern Analogy
                        </h3>
                        <button
                          onClick={() => handleSpeak(result.modern_analogy, 'modern_analogy')}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
                          style={{
                            backgroundColor: speakingSection === 'modern_analogy' ? '#0A5569' : '#e6f7f9',
                            color: speakingSection === 'modern_analogy' ? 'white' : '#0A5569'
                          }}
                          title={speakingSection === 'modern_analogy' ? (speechPaused ? 'Resume' : 'Pause') : 'Read aloud'}
                        >
                          {speakingSection === 'modern_analogy' ? (
                            speechPaused ? (
                              <Volume2 className="w-4 h-4" />
                            ) : (
                              <Pause className="w-4 h-4" />
                            )
                          ) : (
                            <Volume2 className="w-4 h-4" />
                          )}
                          {speakingSection === 'modern_analogy' ? (speechPaused ? 'Resume' : 'Pause') : 'Read'}
                        </button>
                      </div>
                      <div className="text-gray-700 leading-relaxed prose prose-sm max-w-none">
                        <ReactMarkdown>{result.modern_analogy}</ReactMarkdown>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Interactive Timeline */}
                {result.timeline_events && result.timeline_events.length > 0 && (
                  <div className="section-card">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-xl font-bold text-gray-800">
                            📅 Historical Timeline
                          </h3>
                          <button
                            onClick={() => setShowTimeline(!showTimeline)}
                            className="text-sm flex items-center gap-1"
                            style={{ color: '#0A5569' }}
                          >
                            {showTimeline ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            {showTimeline ? 'Collapse' : 'Expand'}
                          </button>
                        </div>

                        {showTimeline && (
                          <div className="relative pl-6 border-l-2 space-y-4" style={{ borderColor: '#b3dfe6' }}>
                            {result.timeline_events.map((event, idx) => (
                              <div key={idx} className="relative">
                                <div className="absolute -left-[25px] w-4 h-4 rounded-full border-4 border-white" style={{ backgroundColor: '#0A5569' }}></div>
                                <div className="p-4 rounded-lg" style={{ backgroundColor: '#e6f7f9' }}>
                                  <div className="flex items-start justify-between gap-2 mb-2">
                                    <span className="font-bold" style={{ color: '#0A5569' }}>{event.year}</span>
                                    <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: '#b3dfe6', color: '#0A5569' }}>
                                      Event {idx + 1}
                                    </span>
                                  </div>
                                  <h4 className="font-semibold text-gray-800 mb-1">{event.title}</h4>
                                  <p className="text-sm text-gray-700 mb-2">{event.description}</p>
                                  <div className="text-xs bg-white p-2 rounded border" style={{ color: '#0A5569', borderColor: '#b3dfe6' }}>
                                    <strong>Significance:</strong> {event.significance}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Interactive Map Locations */}
                {result.geographic_locations && result.geographic_locations.length > 0 && (
                  <div className="section-card">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-3">
                          <h3 className="text-xl font-bold text-gray-800">
                            🗺️ Geographic Context
                          </h3>
                          <button
                            onClick={() => setShowMap(!showMap)}
                            className="text-sm text-teal-600 hover:text-teal-700 flex items-center gap-1"
                          >
                            {showMap ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                            {showMap ? 'Collapse' : 'Expand'}
                          </button>
                        </div>

                        {showMap && (
                          <div className="space-y-3">
                            {result.geographic_locations.map((location, idx) => (
                              <div key={idx} className="bg-teal-50 p-4 rounded-lg border border-teal-200">
                                <div className="flex items-start justify-between gap-2 mb-2">
                                  <h4 className="font-bold text-teal-900">{location.name}</h4>
                                </div>
                                {location.modern_name && location.modern_name !== location.name && (
                                  <p className="text-xs text-teal-700 mb-2">
                                    Modern name: <span className="font-semibold">{location.modern_name}</span>
                                  </p>
                                )}
                                <p className="text-sm text-gray-700 mb-2">{location.significance}</p>
                                {location.coordinates && (
                                  <div className="flex gap-2 mt-2">
                                    <a
                                      href={`https://www.google.com/maps/search/?api=1&query=${location.coordinates.lat},${location.coordinates.lng}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs bg-teal-600 text-white px-3 py-1 rounded-full hover:bg-teal-700 flex items-center gap-1"
                                    >
                                      View on Google Maps
                                    </a>
                                    <span className="text-xs text-gray-500">
                                      {location.coordinates.lat.toFixed(4)}, {location.coordinates.lng.toFixed(4)}
                                    </span>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Key Concepts (Pop-out Explainers) */}
                {result.key_concepts && result.key_concepts.length > 0 && (
                  <div className="section-card">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-800 mb-3">
                          📖 Key Concepts Explained
                        </h3>
                        <p className="text-sm text-gray-600 mb-3">
                          Click on any concept to learn more
                        </p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {result.key_concepts.map((concept, idx) => (
                            <div key={idx}>
                              <button
                                onClick={() => setExpandedConcept(expandedConcept === idx ? null : idx)}
                                className="w-full text-left bg-pink-50 hover:bg-pink-100 p-3 rounded-lg border-2 border-pink-200 transition-all"
                              >
                                <div className="flex items-center justify-between">
                                  <span className="font-semibold text-pink-900">{concept.term}</span>
                                  <Info className={`w-4 h-4 text-pink-600 transition-transform ${expandedConcept === idx ? 'rotate-180' : ''}`} />
                                </div>
                              </button>

                              {/* Pop-out Explainer */}
                              {expandedConcept === idx && (
                                <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 animate-fade-in">
                                  <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                                    <div className="bg-gradient-to-r from-pink-600 to-rose-600 text-white p-6 rounded-t-xl">
                                      <div className="flex items-start justify-between">
                                        <div>
                                          <h4 className="text-2xl font-bold mb-1">{concept.term}</h4>
                                          <p className="text-pink-100 text-sm">Cultural Context Explainer</p>
                                        </div>
                                        <button
                                          onClick={() => setExpandedConcept(null)}
                                          className="text-white hover:text-pink-200 text-2xl font-bold"
                                        >
                                          ×
                                        </button>
                                      </div>
                                    </div>

                                    <div className="p-6 space-y-4">
                                      <div>
                                        <h5 className="font-bold text-gray-800 mb-2">
                                          Definition
                                        </h5>
                                        <p className="text-gray-700 leading-relaxed bg-gray-50 p-3 rounded-lg">
                                          {concept.definition}
                                        </p>
                                      </div>

                                      <div>
                                        <h5 className="font-bold text-gray-800 mb-2">
                                          Cultural Context
                                        </h5>
                                        <p className="text-gray-700 leading-relaxed p-3 rounded-lg" style={{ backgroundColor: '#e6f7f9' }}>
                                          {concept.context}
                                        </p>
                                      </div>

                                      <div>
                                        <h5 className="font-bold text-gray-800 mb-2">
                                          Modern Connection
                                        </h5>
                                        <p className="text-gray-700 leading-relaxed bg-green-50 p-3 rounded-lg">
                                          {concept.modern_parallel}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* External Resources */}
                {result.external_resources && Object.keys(result.external_resources).some(key => result.external_resources[key]?.length > 0) && (
                  <div className="section-card">
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-800 mb-3">
                          🔗 Learn More
                        </h3>
                        <div className="space-y-3">
                          {result.external_resources.timeline_links?.length > 0 && (
                            <div>
                              <h4 className="font-semibold text-gray-700 mb-2">
                                Interactive Timelines
                              </h4>
                              <div className="space-y-1">
                                {result.external_resources.timeline_links.map((link, idx) => (
                                  <a
                                    key={idx}
                                    href={link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-sm hover:underline block"
                                    style={{ color: '#0A5569' }}
                                  >
                                    {link}
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}

                          {result.external_resources.map_links?.length > 0 && (
                            <div>
                              <h4 className="font-semibold text-gray-700 mb-2">
                                Interactive Maps
                              </h4>
                              <div className="space-y-1">
                                {result.external_resources.map_links.map((link, idx) => (
                                  <a
                                    key={idx}
                                    href={link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-sm hover:underline block"
                                    style={{ color: '#0A5569' }}
                                  >
                                    {link}
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}

                          {result.external_resources.further_reading?.length > 0 && (
                            <div>
                              <h4 className="font-semibold text-gray-700 mb-2">
                                Further Reading
                              </h4>
                              <div className="space-y-1">
                                {result.external_resources.further_reading.map((link, idx) => (
                                  <a
                                    key={idx}
                                    href={link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-sm hover:underline block"
                                    style={{ color: '#0A5569' }}
                                  >
                                    {link}
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar - History */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8 animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                  <History className="w-5 h-5 text-blue-600" />
                  Recent Analyses
                </h2>
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {showHistory ? 'Hide' : 'Show'}
                </button>
              </div>

              {showHistory && (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {history.length === 0 ? (
                    <p className="text-gray-500 text-sm text-center py-8">
                      No analyses yet. Start by analyzing some text!
                    </p>
                  ) : (
                    history.map((item) => (
                      <div
                        key={item.id}
                        onClick={() => handleHistoryClick(item)}
                        className="bg-gray-50 p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors group"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-700 line-clamp-2 mb-1">
                              {item.input_text}
                            </p>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              <Clock className="w-3 h-3" />
                              {new Date(item.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          <button
                            onClick={(e) => handleDeleteHistory(item.id, e)}
                            className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-600 text-sm">
        </footer>
      </div>
    </div>
  );
}

export default Analyzer;

