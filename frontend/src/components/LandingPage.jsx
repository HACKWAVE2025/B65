import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Globe, Lightbulb, Sparkles, ChevronRight, Map, Clock, Languages, Check } from 'lucide-react';
import api from '../utils/axiosConfig';

function LandingPage() {
    const navigate = useNavigate();

    // Warm up the backend on component mount to prevent cold starts on Render
    useEffect(() => {
        const warmUpBackend = async () => {
            try {
                console.log('🔥 Warming up backend...');
                await api.get('/api/health');
                console.log('✅ Backend is warm and ready');
            } catch (error) {
                console.log('⚠️ Backend warm-up failed (may still be spinning up):', error.message);
                // Silent fail - this is just an optimization, not critical
            }
        };

        warmUpBackend();
    }, []);

    return (
        <div className="min-h-screen bg-gradient-to-br from-white via-blue-50 to-teal-50">
            {/* Navigation */}
            <nav className="bg-white shadow-sm sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <BookOpen className="w-8 h-8" style={{ color: '#0A5569' }} />
                            <span className="text-xl font-bold" style={{ color: '#0A5569' }}>Cultural Context Analyzer</span>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => navigate('/login')}
                                className="px-4 py-2 rounded-lg font-medium transition-colors"
                                style={{ color: '#0A5569' }}
                            >
                                Sign In
                            </button>
                            <button
                                onClick={() => navigate('/register')}
                                className="px-6 py-2 rounded-lg font-medium text-white transition-all hover:shadow-lg"
                                style={{ backgroundColor: '#0A5569' }}
                            >
                                Get Started
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
                <div className="grid lg:grid-cols-2 gap-12 items-center">
                    <div>
                        <h1 className="text-5xl md:text-6xl font-bold mb-6" style={{ color: '#0A5569', lineHeight: '1.1' }}>
                            Unlock the Stories Behind Every Word
                        </h1>

                        <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                            Ever read a poem, a historical text, or a cultural reference and wondered about the deeper meaning?
                            We help you understand the rich cultural heritage and historical context behind literature from around the world.
                        </p>

                        <div className="flex flex-wrap gap-4 mb-8">
                            <button
                                onClick={() => navigate('/register')}
                                className="px-8 py-4 rounded-lg font-semibold text-white transition-all hover:shadow-xl flex items-center gap-2"
                                style={{ backgroundColor: '#0A5569' }}
                            >
                                Start Exploring
                                <ChevronRight className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => navigate('/login')}
                                className="px-8 py-4 rounded-lg font-semibold transition-all border-2"
                                style={{ borderColor: '#0A5569', color: '#0A5569' }}
                            >
                                Sign In
                            </button>
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-3 gap-6 pt-8 border-t border-gray-200">
                            <div>
                                <div className="text-3xl font-bold mb-1" style={{ color: '#0A5569' }}>12+</div>
                                <div className="text-sm text-gray-600">Languages</div>
                            </div>
                            <div>
                                <div className="text-3xl font-bold mb-1" style={{ color: '#0A5569' }}>5</div>
                                <div className="text-sm text-gray-600">Data Sources</div>
                            </div>
                            <div>
                                <div className="text-3xl font-bold mb-1" style={{ color: '#0A5569' }}>∞</div>
                                <div className="text-sm text-gray-600">Possibilities</div>
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="bg-white rounded-2xl shadow-2xl p-8 border" style={{ borderColor: '#b3dfe6' }}>
                            <div className="space-y-4">
                                <div className="flex items-start gap-3 p-4 rounded-lg" style={{ backgroundColor: '#e6f7f9' }}>
                                    <BookOpen className="w-6 h-6 flex-shrink-0 mt-1" style={{ color: '#0A5569' }} />
                                    <div>
                                        <h3 className="font-semibold mb-1" style={{ color: '#0A5569' }}>Cultural Origins</h3>
                                        <p className="text-sm text-gray-600">Discover where stories, poems, and texts come from</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3 p-4 rounded-lg bg-purple-50">
                                    <Globe className="w-6 h-6 flex-shrink-0 mt-1 text-purple-600" />
                                    <div>
                                        <h3 className="font-semibold text-purple-900 mb-1">Cross-Cultural Links</h3>
                                        <p className="text-sm text-purple-700">See how cultures connect and influence each other</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3 p-4 rounded-lg bg-green-50">
                                    <Lightbulb className="w-6 h-6 flex-shrink-0 mt-1 text-green-600" />
                                    <div>
                                        <h3 className="font-semibold text-green-900 mb-1">Modern Context</h3>
                                        <p className="text-sm text-green-700">Relate ancient wisdom to today's world</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* What Makes Us Different */}
            <section className="bg-white py-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold mb-4" style={{ color: '#0A5569' }}>
                            Why Students Love This Tool
                        </h2>
                        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                            Reading ancient texts shouldn't feel like solving a puzzle. We make cultural learning interactive,
                            visual, and actually fun.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                        <div className="text-center">
                            <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: '#e6f7f9' }}>
                                <Clock className="w-8 h-8" style={{ color: '#0A5569' }} />
                            </div>
                            <h3 className="text-lg font-semibold mb-2" style={{ color: '#0A5569' }}>Historical Timelines</h3>
                            <p className="text-gray-600 text-sm">
                                See events unfold chronologically. When did it happen? What came before and after?
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-4">
                                <Map className="w-8 h-8 text-purple-600" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2 text-purple-900">Interactive Maps</h3>
                            <p className="text-gray-600 text-sm">
                                Where did these stories take place? Explore locations on real maps with GPS coordinates.
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                                <Languages className="w-8 h-8 text-green-600" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2 text-green-900">Multilingual Support</h3>
                            <p className="text-gray-600 text-sm">
                                Get analysis in Hindi, Tamil, Spanish, Japanese, and 8+ other languages.
                            </p>
                        </div>

                        <div className="text-center">
                            <div className="w-16 h-16 rounded-full bg-pink-100 flex items-center justify-center mx-auto mb-4">
                                <Sparkles className="w-8 h-8 text-pink-600" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2 text-pink-900">Smart Explainers</h3>
                            <p className="text-gray-600 text-sm">
                                Click any cultural term to get instant pop-up explanations with modern parallels.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="py-20 bg-gradient-to-br from-blue-50 to-teal-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold mb-4" style={{ color: '#0A5569' }}>
                            Three Simple Steps
                        </h2>
                        <p className="text-xl text-gray-600">
                            From confusion to clarity in seconds
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="bg-white rounded-xl p-8 shadow-lg">
                            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-6 text-white text-xl font-bold" style={{ backgroundColor: '#0A5569' }}>
                                1
                            </div>
                            <h3 className="text-xl font-bold mb-3" style={{ color: '#0A5569' }}>Paste Your Text</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Copy any passage—a poem, a historical quote, a cultural reference. You can type it,
                                speak it using voice input, or even upload an image with text.
                            </p>
                        </div>

                        <div className="bg-white rounded-xl p-8 shadow-lg">
                            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-6 text-white text-xl font-bold" style={{ backgroundColor: '#0A5569' }}>
                                2
                            </div>
                            <h3 className="text-xl font-bold mb-3" style={{ color: '#0A5569' }}>AI Analyzes</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Our AI reads through millions of data points from Wikipedia, knowledge graphs, and verified
                                sources to understand the cultural context.
                            </p>
                        </div>

                        <div className="bg-white rounded-xl p-8 shadow-lg">
                            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-6 text-white text-xl font-bold" style={{ backgroundColor: '#0A5569' }}>
                                3
                            </div>
                            <h3 className="text-xl font-bold mb-3" style={{ color: '#0A5569' }}>Explore & Learn</h3>
                            <p className="text-gray-600 leading-relaxed">
                                Get timelines, maps, concept explainers, and modern analogies. Listen to explanations
                                in audio or read at your own pace.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Real Example */}
            <section className="bg-white py-20">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold mb-4" style={{ color: '#0A5569' }}>
                            See It In Action
                        </h2>
                        <p className="text-xl text-gray-600">
                            Here's what you get when you analyze a haiku
                        </p>
                    </div>

                    <div className="bg-gradient-to-br from-gray-50 to-blue-50 rounded-2xl p-8 border-2" style={{ borderColor: '#b3dfe6' }}>
                        <div className="mb-8">
                            <div className="text-sm font-semibold text-gray-500 mb-2">INPUT</div>
                            <div className="bg-white p-6 rounded-lg shadow-sm border" style={{ borderColor: '#b3dfe6' }}>
                                <p className="text-lg text-gray-800 italic font-serif">
                                    "An old silent pond<br />
                                    A frog jumps into the pond—<br />
                                    Splash! Silence again."
                                </p>
                                <p className="text-sm text-gray-500 mt-2">— Matsuo Bashō</p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="text-sm font-semibold text-gray-500 mb-3">YOU'LL GET</div>

                            <div className="bg-white p-4 rounded-lg shadow-sm flex items-start gap-3">
                                <Check className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#0A5569' }} />
                                <div>
                                    <span className="font-semibold" style={{ color: '#0A5569' }}>Cultural Origin:</span>
                                    <span className="text-gray-700"> Japanese Edo period poetry tradition (17th century)</span>
                                </div>
                            </div>

                            <div className="bg-white p-4 rounded-lg shadow-sm flex items-start gap-3">
                                <Check className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#0A5569' }} />
                                <div>
                                    <span className="font-semibold" style={{ color: '#0A5569' }}>Timeline:</span>
                                    <span className="text-gray-700"> Events from 1644 (Edo period begins) to 1694 (Bashō's death)</span>
                                </div>
                            </div>

                            <div className="bg-white p-4 rounded-lg shadow-sm flex items-start gap-3">
                                <Check className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#0A5569' }} />
                                <div>
                                    <span className="font-semibold" style={{ color: '#0A5569' }}>Map:</span>
                                    <span className="text-gray-700"> Location of Bashō's travels across Japan</span>
                                </div>
                            </div>

                            <div className="bg-white p-4 rounded-lg shadow-sm flex items-start gap-3">
                                <Check className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#0A5569' }} />
                                <div>
                                    <span className="font-semibold" style={{ color: '#0A5569' }}>Modern Analogy:</span>
                                    <span className="text-gray-700"> Like a mindfulness meditation app—finding peace in small moments</span>
                                </div>
                            </div>

                            <div className="bg-white p-4 rounded-lg shadow-sm flex items-start gap-3">
                                <Check className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#0A5569' }} />
                                <div>
                                    <span className="font-semibold" style={{ color: '#0A5569' }}>Key Concepts:</span>
                                    <span className="text-gray-700"> Zen Buddhism, wabi-sabi aesthetic, kireji (cutting words)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Breakdown */}
            <section className="py-20 bg-gradient-to-br from-blue-50 to-purple-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-bold mb-4" style={{ color: '#0A5569' }}>
                            Everything You Need to Learn
                        </h2>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="bg-white rounded-xl p-6 shadow-lg">
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: '#e6f7f9' }}>
                                    <BookOpen className="w-6 h-6" style={{ color: '#0A5569' }} />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg mb-2" style={{ color: '#0A5569' }}>Text & Image Input</h3>
                                    <p className="text-gray-600 text-sm">
                                        Type, paste, upload images with text, or use voice input. We extract and analyze text from any format.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl p-6 shadow-lg">
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                                    <Globe className="w-6 h-6 text-purple-600" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg mb-2 text-purple-900">Multi-Source Verification</h3>
                                    <p className="text-gray-600 text-sm">
                                        We cross-check facts across Wikipedia, Google Knowledge Graph, DBpedia, Wikidata, and OpenLibrary.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl p-6 shadow-lg">
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                                    <Languages className="w-6 h-6 text-green-600" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg mb-2 text-green-900">Audio Explanations</h3>
                                    <p className="text-gray-600 text-sm">
                                        Listen to explanations read aloud in your chosen language. Perfect for auditory learners.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl p-6 shadow-lg">
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 rounded-lg bg-pink-100 flex items-center justify-center flex-shrink-0">
                                    <Sparkles className="w-6 h-6 text-pink-600" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-lg mb-2 text-pink-900">Entity Highlighting</h3>
                                    <p className="text-gray-600 text-sm">
                                        Important cultural terms are highlighted. Hover to see instant Wikipedia definitions and context.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-gradient-to-r from-teal-600 to-blue-700 py-20">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        Ready to Unlock Cultural Wisdom?
                    </h2>
                    <p className="text-xl text-teal-100 mb-8">
                        Join students worldwide who are discovering the stories behind the words
                    </p>
                    <button
                        onClick={() => navigate('/register')}
                        className="px-10 py-5 bg-white rounded-xl font-bold text-xl transition-all hover:shadow-2xl hover:scale-105"
                        style={{ color: '#0A5569' }}
                    >
                        Start Exploring — It's Free
                    </button>
                    <p className="text-teal-100 mt-6 text-sm">
                        Already have an account?{' '}
                        <button
                            onClick={() => navigate('/login')}
                            className="underline font-semibold hover:text-white"
                        >
                            Sign in here
                        </button>
                    </p>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-gray-300 py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-4 gap-8 mb-8">
                        <div>
                            <div className="flex items-center gap-2 mb-4">
                                <BookOpen className="w-6 h-6 text-teal-400" />
                                <span className="font-bold text-white">CCA</span>
                            </div>
                            <p className="text-sm text-gray-400">
                                Making cultural learning accessible and engaging for students worldwide.
                            </p>
                        </div>

                        <div>
                            <h4 className="font-semibold text-white mb-3">Features</h4>
                            <ul className="space-y-2 text-sm">
                                <li>Text Analysis</li>
                                <li>Image OCR</li>
                                <li>Voice Input</li>
                                <li>Audio Output</li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="font-semibold text-white mb-3">Resources</h4>
                            <ul className="space-y-2 text-sm">
                                <li>Documentation</li>
                                <li>API Reference</li>
                                <li>Supported Languages</li>
                                <li>Data Sources</li>
                            </ul>
                        </div>

                        <div>
                            <h4 className="font-semibold text-white mb-3">Legal</h4>
                            <ul className="space-y-2 text-sm">
                                <li>Privacy Policy</li>
                                <li>Terms of Service</li>
                                <li>Cookie Policy</li>
                            </ul>
                        </div>
                    </div>

                    <div className="border-t border-gray-800 pt-8 text-center text-sm text-gray-400">
                        <p>By Team AKSha</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default LandingPage;
