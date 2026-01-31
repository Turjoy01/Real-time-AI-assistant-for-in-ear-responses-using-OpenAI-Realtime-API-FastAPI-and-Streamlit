import streamlit as st
import asyncio
import websockets
import json
from datetime import datetime
import requests
import base64
from audio_recorder_streamlit import audio_recorder

# Page config
st.set_page_config(
    page_title="AI Earbud Assistant - Passive Mode",
    page_icon="🎧",
    layout="wide"
)

# Backend configuration
BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'is_listening' not in st.session_state:
    st.session_state.is_listening = False
if 'client_id' not in st.session_state:
    import uuid
    st.session_state.client_id = str(uuid.uuid4())
if 'last_transcription' not in st.session_state:
    st.session_state.last_transcription = ""
if 'question_detected' not in st.session_state:
    st.session_state.question_detected = False

# Custom CSS
st.markdown("""
<style>
.passive-mode {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}
.silent-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #95a5a6;
    margin-right: 8px;
    animation: pulse 2s infinite;
}
.question-detected {
    background: #27ae60 !important;
    animation: pulse-fast 0.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
@keyframes pulse-fast {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.conversation-bubble {
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
}
.user-bubble {
    background: #ecf0f1;
    color: #2c3e50;
    margin-left: 20%;
}
.ai-bubble {
    background: #3498db;
    color: white;
    margin-right: 20%;
}
</style>
""", unsafe_allow_html=True)

# Title and mode indicator
st.markdown("""
<div class="passive-mode">
    <h1>🎧 AI Earbud Assistant</h1>
    <p><strong>PASSIVE LISTENING MODE</strong></p>
    <p>AI is silent and monitoring. It will only speak when a question is detected.</p>
</div>
""", unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎙️ Live Audio")
    
    # Status indicator
    status_col1, status_col2 = st.columns([1, 3])
    with status_col1:
        if st.session_state.question_detected:
            st.markdown('<span class="silent-indicator question-detected"></span> Question Detected!', unsafe_allow_html=True)
        else:
            st.markdown('<span class="silent-indicator"></span> Listening Silently...', unsafe_allow_html=True)
    
    # Audio recorder
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e74c3c",
        neutral_color="#95a5a6",
        icon_name="microphone",
        icon_size="3x",
        pause_threshold=2.0
    )
    
    if audio_bytes:
        # Send audio to backend
        with st.spinner("👂 AI is analyzing your voice..."):
            files = {'file': ('audio.wav', audio_bytes, 'audio/wav')}
            response = requests.post(f"{BACKEND_URL}/api/voice", files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'question_detected':
                    st.session_state.question_detected = True
                    st.success(f"🤖 AI Answer: **{data['answer']}**")
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        'type': 'question',
                        'text': data['transcription'],
                        'timestamp': datetime.now()
                    })
                    st.session_state.conversation_history.append({
                        'type': 'answer',
                        'text': data['answer'],
                        'timestamp': datetime.now()
                    })
                    
                    # Store last transcription for visual feedback
                    st.session_state.last_transcription = data['transcription']
                elif 'transcription' in data:
                    st.info(f"📝 Heard: \"{data['transcription']}\" (Not a question)")
                    st.session_state.question_detected = False
                else:
                    st.warning("⚠️ No clear speech detected.")
            else:
                st.error("❌ Error processing voice.")

    # Manual text input (for testing)
    st.markdown("---")
    st.subheader("💬 Or Type to Test")
    user_input = st.text_input(
        "Type a sentence (AI will detect if it's a question):",
        key="text_input",
        placeholder="e.g., What is the capital of France?"
    )
    
    if user_input:
        # Show transcription
        st.markdown(f"**Transcription:** {user_input}")
        st.session_state.last_transcription = user_input
        
        # Send to backend
        with st.spinner("Processing..."):
            response = requests.post(
                f"{BACKEND_URL}/api/question",
                params={"question": user_input}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data['answer'] != "Not a question":
                    st.session_state.question_detected = True
                    st.success(f"🤖 AI Response: **{data['answer']}**")
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({
                        'type': 'question',
                        'text': user_input,
                        'timestamp': datetime.now()
                    })
                    st.session_state.conversation_history.append({
                        'type': 'answer',
                        'text': data['answer'],
                        'timestamp': datetime.now()
                    })
                    
                    # Trigger TTS (simulated)
                    st.audio(f"data:audio/mp3;base64,{base64.b64encode(b'').decode()}")
                else:
                    st.info("ℹ️ Not a question - AI remains silent")
                    st.session_state.question_detected = False

with col2:
    st.header("📊 Conversation Log")
    
    # Display conversation history
    if st.session_state.conversation_history:
        for entry in reversed(st.session_state.conversation_history[-10:]):
            if entry['type'] == 'question':
                st.markdown(
                    f'<div class="conversation-bubble user-bubble">'
                    f'<strong>Q:</strong> {entry["text"]}<br>'
                    f'<small>{entry["timestamp"].strftime("%H:%M:%S")}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="conversation-bubble ai-bubble">'
                    f'<strong>A:</strong> {entry["text"]}<br>'
                    f'<small>{entry["timestamp"].strftime("%H:%M:%S")}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("👂 AI is listening silently... Ask a question to see it respond!")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Context upload
    st.subheader("📄 Upload Context")
    st.write("Provide context to help AI give better answers")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'md', 'json'],
        help="Upload documents with relevant information"
    )
    
    if uploaded_file:
        files = {'file': uploaded_file}
        response = requests.post(f"{BACKEND_URL}/api/context", files=files)
        if response.status_code == 200:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
    
    # Statistics
    st.subheader("📊 Statistics")
    if st.session_state.conversation_history:
        questions = [e for e in st.session_state.conversation_history if e['type'] == 'question']
        st.metric("Questions Detected", len(questions))
        st.metric("AI Responses", len(questions))
    else:
        st.metric("Questions Detected", 0)
    
    # Controls
    st.subheader("🗑️ Controls")
    if st.button("Clear History", use_container_width=True):
        requests.delete(f"{BACKEND_URL}/api/history")
        st.session_state.conversation_history = []
        st.success("✅ History cleared!")
    
    if st.button("Clear Context", use_container_width=True):
        requests.delete(f"{BACKEND_URL}/api/context")
        st.success("✅ Context cleared!")

# Footer
st.markdown("---")
st.markdown("""
### 💡 How It Works
1. **AI listens passively** - No response to regular conversation
2. **Detects questions automatically** - Uses NLP to identify when someone asks a question
3. **Whispers short answers** - Provides concise responses (1-15 words)
4. **Silent by default** - Won't interrupt or respond unless necessary

**Example:**
- "The weather is nice today" → ❌ No response (statement)
- "What time is it?" → ✅ AI responds: "3:45 PM"
""")
# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")# st.markdown("© 2024 AI Earbud Assistant")
# st.markdown("Developed by OpenAI")