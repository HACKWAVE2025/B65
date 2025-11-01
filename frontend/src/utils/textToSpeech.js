// Text-to-Speech utility using Web Speech API

// Map language codes to SpeechSynthesis language codes
const languageMap = {
  'en': 'en-US',
  'hi': 'hi-IN',
  'es': 'es-ES',
  'fr': 'fr-FR',
  'de': 'de-DE',
  'zh': 'zh-CN',
  'ja': 'ja-JP',
  'ar': 'ar-SA',
  'bn': 'bn-BD',
  'ta': 'ta-IN',
  'te': 'te-IN',
  'mr': 'mr-IN',
};

let currentUtterance = null;

/**
 * Convert markdown text to plain text for speech
 */
function markdownToPlainText(text) {
  if (!text) return '';
  
  // Remove markdown formatting
  return text
    .replace(/#{1,6}\s+/g, '') // Remove headers
    .replace(/\*\*(.+?)\*\*/g, '$1') // Remove bold
    .replace(/\*(.+?)\*/g, '$1') // Remove italic
    .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1') // Remove links, keep text
    .replace(/`([^`]+)`/g, '$1') // Remove code
    .replace(/\n+/g, ' ') // Replace newlines with spaces
    .trim();
}

/**
 * Speak text using the browser's SpeechSynthesis API
 */
export function speakText(text, language = 'en', onEnd = null) {
  // Stop any currently speaking text
  stopSpeaking();
  
  if (!text) {
    console.warn('No text provided for speech');
    return;
  }
  
  // Check if SpeechSynthesis is available
  if (!('speechSynthesis' in window)) {
    alert('Text-to-speech is not supported in your browser. Please use a modern browser like Chrome, Firefox, or Edge.');
    return;
  }
  
  // Convert markdown to plain text
  const plainText = markdownToPlainText(text);
  
  if (!plainText) {
    console.warn('No text to speak after conversion');
    return;
  }
  
  // Create utterance
  const utterance = new SpeechSynthesisUtterance(plainText);
  
  // Set language
  const langCode = languageMap[language] || 'en-US';
  utterance.lang = langCode;
  
  // Set voice properties
  utterance.rate = 0.9; // Slightly slower for clarity
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  
  // Set up event handlers
  if (onEnd) {
    utterance.onend = onEnd;
  }
  
  utterance.onerror = (event) => {
    console.error('Speech synthesis error:', event);
  };
  
  // Store current utterance
  currentUtterance = utterance;
  
  // Speak
  window.speechSynthesis.speak(utterance);
}

/**
 * Stop currently speaking text
 */
export function stopSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
  currentUtterance = null;
}

/**
 * Check if speech is currently active
 */
export function isSpeaking() {
  return window.speechSynthesis && window.speechSynthesis.speaking;
}

/**
 * Pause speech
 */
export function pauseSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.pause();
  }
}

/**
 * Resume paused speech
 */
export function resumeSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.resume();
  }
}

