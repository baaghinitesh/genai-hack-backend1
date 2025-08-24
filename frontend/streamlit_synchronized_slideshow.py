import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from google.cloud import storage
import io
import base64
from PIL import Image
import tempfile
import os
import time
import threading

# Configure Streamlit page
st.set_page_config(
    page_title="🎌 Manga Mental Wellness - Synchronized Slideshow",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for manga styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #FF6B9D, #C7A2FF);
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 2rem;
}

.panel-container {
    border: 3px solid #333;
    border-radius: 15px;
    padding: 15px;
    margin: 10px 0;
    background: white;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.panel-header {
    font-weight: bold;
    font-size: 1.2em;
    color: #333;
    margin-bottom: 10px;
    border-bottom: 2px solid #FF6B9D;
    padding-bottom: 5px;
}

.dialogue-text {
    background: #F0F8FF;
    padding: 10px;
    border-radius: 8px;
    border-left: 4px solid #4A90E2;
    font-style: italic;
    margin: 10px 0;
}

.audio-controls {
    background: #f0f0f0;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

.current-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_image_from_gcs(bucket_name: str, blob_path: str):
    """Load image from GCS and return as bytes."""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            return None
            
        image_data = blob.download_as_bytes()
        return image_data
    except Exception as e:
        st.error(f"Error loading {blob_path}: {e}")
        return None

@st.cache_data
def load_audio_from_gcs(bucket_name: str, blob_path: str):
    """Load audio from GCS and return as bytes."""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        if not blob.exists():
            return None
            
        audio_data = blob.download_as_bytes()
        return audio_data
    except Exception as e:
        st.error(f"Error loading {blob_path}: {e}")
        return None

def get_panel_title(panel_number: int) -> str:
    """Get descriptive title for each panel."""
    titles = {
        1: "Introduction",
        2: "Challenge", 
        3: "Reflection",
        4: "Discovery",
        5: "Transformation",
        6: "Resolution"
    }
    return titles.get(panel_number, f"Panel {panel_number}")

def create_synchronized_audio(tts_data, music_data):
    """Create synchronized audio by mixing TTS and background music."""
    try:
        from pydub import AudioSegment
        from pydub.playback import play
        import io
        
        # Load TTS and music
        tts_audio = AudioSegment.from_mp3(io.BytesIO(tts_data))
        music_audio = AudioSegment.from_mp3(io.BytesIO(music_data))
        
        # Extend music to match TTS duration if needed
        if len(music_audio) < len(tts_audio):
            # Loop music to match TTS length
            loops_needed = (len(tts_audio) // len(music_audio)) + 1
            music_audio = music_audio * loops_needed
        
        # Trim music to match TTS duration
        music_audio = music_audio[:len(tts_audio)]
        
        # Lower music volume (background)
        music_audio = music_audio - 20  # Reduce by 20dB
        
        # Mix TTS and music
        synchronized_audio = tts_audio.overlay(music_audio)
        
        # Export as bytes
        output = io.BytesIO()
        synchronized_audio.export(output, format="mp3")
        return output.getvalue()
        
    except Exception as e:
        st.error(f"Error creating synchronized audio: {e}")
        return None

def main():
    """Main Streamlit application with panel-by-panel synchronization."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎌 Manga Mental Wellness - Panel-by-Panel Synchronized Slideshow</h1>
        <p>🎵 Each panel: Image + TTS + Background Music → Auto-advance when audio finishes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Story data
    story_id = "story_884416"
    bucket_name = "calmira-backend"
    
    panels_data = [
        {"panel_number": 1, "dialogue_text": "Every day, I wake up with one goal: to be a good human being, kind to everyone I meet..."},
        {"panel_number": 2, "dialogue_text": "But the world isn't always easy. Sometimes, it feels like an endless fight… to keep that kindness alive..."},
        {"panel_number": 3, "dialogue_text": "Is this 'fight' truly external? Or is it a battle within myself? To master my own reactions, my own choices..."},
        {"panel_number": 4, "dialogue_text": "My hobby, fighting, taught me discipline. Not to strike down, but to stand firm. To control my own choices..."},
        {"panel_number": 5, "dialogue_text": "True strength isn't about winning arguments or overpowering others. It's about choosing compassion..."},
        {"panel_number": 6, "dialogue_text": "And as I choose kindness, day by day, I find my inner peace. My journey continues, stronger and more..."}
    ]
    
    # Initialize session state
    if "current_panel" not in st.session_state:
        st.session_state.current_panel = 1
    if "is_playing" not in st.session_state:
        st.session_state.is_playing = False
    if "auto_advance" not in st.session_state:
        st.session_state.auto_advance = True
    
    # Control panel
    st.markdown("### 🎮 Slideshow Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎬 Start Slideshow", use_container_width=True):
            st.session_state.current_panel = 1
            st.session_state.is_playing = True
            st.rerun()
    
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.is_playing = False
            st.rerun()
    
    with col3:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.current_panel = 1
            st.session_state.is_playing = False
            st.rerun()
    
    with col4:
        st.session_state.auto_advance = st.checkbox("🔄 Auto-advance", value=True)
    
    # Manual navigation
    st.markdown("### 📖 Manual Navigation")
    manual_panel = st.selectbox(
        "Select Panel:",
        options=list(range(1, 7)),
        index=st.session_state.current_panel - 1,
        format_func=lambda x: f"Panel {x}: {get_panel_title(x)}"
    )
    
    if manual_panel != st.session_state.current_panel:
        st.session_state.current_panel = manual_panel
        st.rerun()
    
    # Display current panel
    st.markdown("---")
    
    current_panel_num = st.session_state.current_panel
    panel_data = panels_data[current_panel_num - 1]
    
    # Current panel header
    st.markdown(f"""
    <div class="current-panel">
        <h2>🎌 Panel {current_panel_num}: {get_panel_title(current_panel_num)}</h2>
        <p>Progress: {current_panel_num}/6 • {current_panel_num/6*100:.0f}% Complete</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load panel assets
    image_blob_path = f"stories/{story_id}/panel_{current_panel_num:02d}.png"
    tts_blob_path = f"stories/{story_id}/tts_panel_{current_panel_num:02d}.mp3"
    music_blob_path = f"stories/{story_id}/music_panel_{current_panel_num:02d}.mp3"
    
    # Load image
    image_data = load_image_from_gcs(bucket_name, image_blob_path)
    
    if image_data:
        st.image(image_data, caption=f"Panel {current_panel_num} - Rohit's Mental Wellness Journey", width=None)
        st.success(f"✅ Panel {current_panel_num} image loaded")
    else:
        st.error(f"❌ Could not load Panel {current_panel_num} image")
    
    # Display dialogue
    dialogue_text = panel_data["dialogue_text"]
    st.markdown(f"""
    <div class="dialogue-text">
        <strong>💭 Narration:</strong><br>
        <em>"{dialogue_text}"</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Audio controls
    st.markdown("### 🎵 Panel Audio Components")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎤 TTS (Voice Narration)**")
        tts_data = load_audio_from_gcs(bucket_name, tts_blob_path)
        if tts_data:
            st.audio(tts_data, format="audio/mp3")
            st.success("✅ TTS loaded")
        else:
            st.error("❌ TTS not found")
    
    with col2:
        st.markdown("**🎵 Background Music**")
        music_data = load_audio_from_gcs(bucket_name, music_blob_path)
        if music_data:
            st.audio(music_data, format="audio/mp3")
            st.success("✅ Music loaded")
        else:
            st.error("❌ Music not found")
    
    with col3:
        st.markdown("**🎼 Synchronized (TTS + Music)**")
        if tts_data and music_data:
            synchronized_audio = create_synchronized_audio(tts_data, music_data)
            if synchronized_audio:
                st.audio(synchronized_audio, format="audio/mp3")
                st.success("✅ Synchronized audio created")
                
                # Auto-advance logic
                if st.session_state.auto_advance and st.session_state.is_playing:
                    st.info("⏭️ Auto-advancing to next panel when audio finishes...")
                    # In a real implementation, you'd use JavaScript to detect audio end
                    # For now, we'll use a simple timer
                    time.sleep(2)  # Simulate audio duration
                    if current_panel_num < 6:
                        st.session_state.current_panel = current_panel_num + 1
                        st.rerun()
            else:
                st.error("❌ Could not create synchronized audio")
        else:
            st.warning("⚠️ Need both TTS and music for synchronization")
    
    # Progress bar
    progress = current_panel_num / 6
    st.progress(progress)
    
    # Panel overview
    st.markdown("---")
    st.subheader("📚 All Panels Overview")
    
    for i, panel in enumerate(panels_data, 1):
        with st.expander(f"Panel {i}: {get_panel_title(i)}", expanded=(i == current_panel_num)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Load panel image
                panel_image_blob = f"stories/{story_id}/panel_{i:02d}.png"
                panel_image_data = load_image_from_gcs(bucket_name, panel_image_blob)
                
                if panel_image_data:
                    st.image(panel_image_data, caption=f"Panel {i}", width=200)
                else:
                    st.error(f"Panel {i} image not found")
            
            with col2:
                st.write(f"**Dialogue:** {panel['dialogue_text'][:100]}...")
                
                # Load panel audio components
                panel_tts_blob = f"stories/{story_id}/tts_panel_{i:02d}.mp3"
                panel_music_blob = f"stories/{story_id}/music_panel_{i:02d}.mp3"
                
                tts_available = load_audio_from_gcs(bucket_name, panel_tts_blob) is not None
                music_available = load_audio_from_gcs(bucket_name, panel_music_blob) is not None
                
                st.write(f"🎤 TTS: {'✅' if tts_available else '❌'}")
                st.write(f"🎵 Music: {'✅' if music_available else '❌'}")
                st.write(f"🎼 Sync: {'✅' if tts_available and music_available else '❌'}")

if __name__ == "__main__":
    main()
