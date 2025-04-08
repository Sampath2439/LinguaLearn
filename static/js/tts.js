// tts.js - Text-to-speech functionality using the Web Speech API

// Check if browser supports Web Speech API (as a fallback option)
const speechSynthesisSupported = 'speechSynthesis' in window;

// Set of language codes for Web Speech API
const languageCodeMap = {
    "English": "en-US",
    "Spanish": "es-ES",
    "French": "fr-FR",
    "German": "de-DE",
    "Italian": "it-IT",
    "Portuguese": "pt-PT",
    "Chinese": "zh-CN",
    "Japanese": "ja-JP",
    "Korean": "ko-KR",
    "Russian": "ru-RU",
    "Arabic": "ar-SA",
    "Hindi": "hi-IN",
    "Dutch": "nl-NL",
    "Swedish": "sv-SE",
    "Polish": "pl-PL",
    "Turkish": "tr-TR"
};

/**
 * Speak text using the Web Speech API (client-side fallback)
 * 
 * Note: This is a fallback if the server-side TTS fails
 * The primary TTS functionality is implemented in the backend
 * 
 * @param {string} text - The text to speak
 * @param {string} languageName - The language name
 */
function speakTextFallback(text, languageName) {
    if (!speechSynthesisSupported) {
        console.error('Speech synthesis not supported in this browser');
        return;
    }
    
    // Stop any current speech
    window.speechSynthesis.cancel();
    
    // Create speech synthesis utterance
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Set language
    const langCode = languageCodeMap[languageName] || 'en-US';
    utterance.lang = langCode;
    
    // Speak the text
    window.speechSynthesis.speak(utterance);
}

/**
 * Get available voices for a specific language
 * @param {string} languageName - The language name
 * @returns {Array} - Array of available voices for the language
 */
function getVoicesForLanguage(languageName) {
    if (!speechSynthesisSupported) {
        return [];
    }
    
    const langCode = languageCodeMap[languageName] || 'en-US';
    const voices = window.speechSynthesis.getVoices();
    
    // Filter voices by language
    return voices.filter(voice => voice.lang.startsWith(langCode.split('-')[0]));
}

// Event listener for the speechSynthesis.onvoiceschanged event
if (speechSynthesisSupported) {
    window.speechSynthesis.onvoiceschanged = function() {
        // This ensures voices are loaded before trying to use them
        console.log('Voices loaded for Web Speech API');
    };
}
