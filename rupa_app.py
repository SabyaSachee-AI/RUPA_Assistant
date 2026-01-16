import streamlit as st
import os
import json
import asyncio
import edge_tts
import pygame
import uuid
from rupa_brain import RupaAssistant
from streamlit_mic_recorder import speech_to_text

# --- Page Config ---
st.set_page_config(page_title="RUPA AI", page_icon="❤️", layout="centered")

# --- Persistent Memory Management ---
MEMORY_FILE = "chat_history.json"
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# --- Initialize Session States ---
if "assistant" not in st.session_state:
    st.session_state.assistant = RupaAssistant()
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()
if "voice_on" not in st.session_state:
    st.session_state.voice_on = True
if "last_spoken_id" not in st.session_state:
    st.session_state.last_spoken_id = ""

if not pygame.mixer.get_init():
    pygame.mixer.init()

assistant = st.session_state.assistant

# --- PYTHON NEURAL VOICE ENGINE ---
async def rupa_speak_python(text, lang):
    """Generates natural female voice via edge-tts"""
    voice = "bn-BD-NabanitaNeural" if lang == "Bengali" else "en-US-AriaNeural"
    unique_filename = f"voice_{uuid.uuid4().hex}.mp3"
    
    # Soft and pleasant tuning
    communicate = edge_tts.Communicate(text, voice, rate="-10%", pitch="+2Hz")
    await communicate.save(unique_filename)
    
    pygame.mixer.music.load(unique_filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    try:
        os.remove(unique_filename)
    except:
        pass

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("rupa.png"):
        st.image("rupa.png", use_container_width=True)
    st.write(f"**Relationship Mode: Mojib & Rupa**")
    st.divider()

    language = st.radio("Language:", ("English", "Bengali"))
    
    st.write(f"🎤 **Talk to Rupa:**")
    spoken_text = speech_to_text(language='bn-BD' if language == "Bengali" else 'en-US', start_prompt="Record", key='voice_input')

    with st.expander("🛠️ Advanced Settings"):
        role = st.selectbox("Role:", list(assistant.roles.keys()))
        st.session_state.voice_on = st.toggle("Voice Active", value=st.session_state.voice_on)

    if st.button("🗑️ Clear Memory"):
        st.session_state.messages = []
        if os.path.exists(MEMORY_FILE): os.remove(MEMORY_FILE)
        st.rerun()

# --- GREETING ---
if "greeted" not in st.session_state and not st.session_state.messages:
    g = assistant.get_greeting(language)
    st.session_state.messages.append({"role": "model", "content": g}) # Changed role to 'model'
    st.session_state.greeted = True
    if st.session_state.voice_on:
        asyncio.run(rupa_speak_python(g, language))

# --- CHAT DISPLAY ---
st.title(f"RUPA AI: {role}")



for msg in st.session_state.messages:
    is_u = msg["role"] == "user"
    av = "mojib.png" if is_u else "rupa.png"
    nm = "Mojib" if is_u else "Rupa ❤️"
    with st.chat_message(msg["role"], avatar=av if os.path.exists(av) else None):
        st.markdown(f"**{nm}**")
        st.markdown(msg["content"])

# --- INPUT HANDLING ---
prompt = spoken_text if spoken_text else st.chat_input("Talk to Rupa...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="mojib.png" if os.path.exists("mojib.png") else None):
        st.markdown("**Mojib**")
        st.markdown(prompt)

    with st.chat_message("model", avatar="rupa.png" if os.path.exists("rupa.png") else None):
        st.markdown("**Rupa ❤️**")
        ph, full = st.empty(), ""
        # Provide history turns
        stream = assistant.get_response(prompt, role, st.session_state.messages[-15:], language)
        for chunk in stream:
            full += chunk.text
            ph.markdown(full + "▌")
        ph.markdown(full)
        
        m_id = f"{len(st.session_state.messages)}_{hash(full)}"
        if st.session_state.voice_on and st.session_state.last_spoken_id != m_id:
            asyncio.run(rupa_speak_python(full, language))
            st.session_state.last_spoken_id = m_id

    st.session_state.messages.append({"role": "model", "content": full})
    save_memory(st.session_state.messages)
    if spoken_text: st.rerun()