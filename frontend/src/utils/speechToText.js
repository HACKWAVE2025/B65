/**
 * Speech-to-Text utility using Web Speech API
 * Provides browser-based speech recognition functionality
 */

class SpeechToText {
    constructor() {
        // Check if browser supports speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('Speech recognition not supported in this browser');
            this.recognition = null;
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true; // Keep listening until stopped
        this.recognition.interimResults = true; // Get real-time results
        this.isListening = false;

        // Callbacks
        this.onResult = null;
        this.onError = null;
        this.onEnd = null;
    }

    /**
     * Check if speech recognition is supported
     */
    isSupported() {
        return this.recognition !== null;
    }

    /**
     * Start listening for speech
     * @param {string} language - Language code (e.g., 'en-US', 'hi-IN')
     * @param {function} onResult - Callback when speech is recognized
     * @param {function} onError - Callback on error
     * @param {function} onEnd - Callback when recognition ends
     */
    start(language = 'en-US', onResult, onError, onEnd) {
        if (!this.recognition) {
            if (onError) {
                onError(new Error('Speech recognition not supported'));
            }
            return;
        }

        if (this.isListening) {
            console.warn('Already listening');
            return;
        }

        // Set language
        this.recognition.lang = language;

        // Store callbacks
        this.onResult = onResult;
        this.onError = onError;
        this.onEnd = onEnd;

        // Set up event handlers
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }

            if (this.onResult) {
                this.onResult({
                    finalTranscript: finalTranscript.trim(),
                    interimTranscript: interimTranscript.trim(),
                    isFinal: finalTranscript.length > 0
                });
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (this.onError) {
                this.onError(event.error);
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            if (this.onEnd) {
                this.onEnd();
            }
        };

        // Start recognition
        try {
            this.recognition.start();
            this.isListening = true;
        } catch (error) {
            console.error('Failed to start speech recognition:', error);
            if (this.onError) {
                this.onError(error);
            }
        }
    }

    /**
     * Stop listening
     */
    stop() {
        if (!this.recognition || !this.isListening) {
            return;
        }

        try {
            this.recognition.stop();
            this.isListening = false;
        } catch (error) {
            console.error('Failed to stop speech recognition:', error);
        }
    }

    /**
     * Check if currently listening
     */
    getIsListening() {
        return this.isListening;
    }
}

// Create singleton instance
const speechToText = new SpeechToText();

export default speechToText;

/**
 * Language code mappings for speech recognition
 * Maps our app's language codes to speech recognition language codes
 */
export const getSpeechLanguageCode = (languageCode) => {
    const languageMap = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'es': 'es-ES',
        'fr': 'fr-FR',
        'de': 'de-DE',
        'zh': 'zh-CN',
        'ja': 'ja-JP',
        'ar': 'ar-SA',
        'bn': 'bn-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'mr': 'mr-IN'
    };

    return languageMap[languageCode] || 'en-US';
};
