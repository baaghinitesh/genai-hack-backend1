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

# Configure Streamlit page
st.set_page_config(
    page_title="🎌 Manga Mental Wellness - Realistic Slideshow",
    page_icon="🎌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #FF6B9D, #C7A2FF);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
    color: white;
}

.current-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
}

.dialogue-text {
    background: #F0F8FF;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #4A90E2;
    font-style: italic;
    margin: 15px 0;
    font-size: 1.1em;
    line-height: 1.5;
}

.instruction-box {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 10px;
    padding: 20px;
    margin: 15px 0;
}

.slideshow-active {
    background: #d4edda;
    border: 2px solid #28a745;
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
    text-align: center;
}

.limitation-notice {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
}

.timer-display {
    background: #e2e3e5;
    border: 2px solid #6c757d;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    text-align: center;
    font-size: 1.2em;
    font-weight: bold;
}

.audio-section {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
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
        
        # Resize image to reduce size (max 600px width)
        image = Image.open(io.BytesIO(image_data))
        if image.width > 600:
            ratio = 600 / image.width
            new_height = int(image.height * ratio)
            image = image.resize((600, new_height), Image.Resampling.LANCZOS)
        
        # Convert back to bytes
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='PNG', optimize=True, quality=85)
        return output_buffer.getvalue()
        
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
        1: "Introduction - The Daily Goal",
        2: "Challenge - The Struggle", 
        3: "Reflection - Inner Questions",
        4: "Discovery - Learning from Fighting",
        5: "Transformation - True Strength",
        6: "Resolution - Finding Peace"
    }
    return titles.get(panel_number, f"Panel {panel_number}")

def estimate_tts_duration(text: str) -> int:
    """Estimate TTS duration in seconds."""
    words = len(text.split())
    # Assume 2.5 words per second (slower than normal speech for TTS)
    duration = max(int(words / 2.5), 5)  # Minimum 5 seconds
    return duration

def main():
    """Main application with realistic slideshow functionality."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎌 Manga Mental Wellness</h1>
        <p>🎵 Realistic Slideshow with Manual Audio Control</p>
        <small>⚠️ Auto-play limitations: Browser security requires manual audio interaction</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Story configuration
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
    if "slideshow_mode" not in st.session_state:
        st.session_state.slideshow_mode = False
    if "timer_active" not in st.session_state:
        st.session_state.timer_active = False
    if "timer_start" not in st.session_state:
        st.session_state.timer_start = None
    if "estimated_duration" not in st.session_state:
        st.session_state.estimated_duration = 0
    
    # Important limitation notice
    st.markdown("""
    <div class="limitation-notice">
        <strong>⚠️ Important:</strong> Due to browser security policies, this slideshow requires manual interaction:
        <ul>
            <li>🎤 Click "Play" on TTS audio manually</li>
            <li>🎵 Click "Play" on background music manually (optional)</li>
            <li>⏱️ Use timer to know when to advance panels</li>
            <li>⏭️ Click "Next Panel" to advance when ready</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Control buttons
    st.markdown("### 🎮 Slideshow Controls")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🎬 Start Slideshow", use_container_width=True):
            st.session_state.slideshow_mode = True
            st.session_state.current_panel = 1
            st.session_state.timer_active = False
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop Slideshow", use_container_width=True):
            st.session_state.slideshow_mode = False
            st.session_state.timer_active = False
            st.session_state.current_panel = 1
            st.rerun()
    
    with col3:
        if st.button("⏮️ Previous", use_container_width=True):
            if st.session_state.current_panel > 1:
                st.session_state.current_panel -= 1
                st.session_state.timer_active = False
                st.rerun()
    
    with col4:
        if st.button("⏭️ Next Panel", use_container_width=True):
            if st.session_state.current_panel < 6:
                st.session_state.current_panel += 1
                st.session_state.timer_active = False
                st.rerun()
            elif st.session_state.current_panel == 6:
                st.balloons()
                st.success("🎉 Slideshow completed!")
                st.session_state.slideshow_mode = False
    
    with col5:
        # Manual panel selector (when not in slideshow mode)
        if not st.session_state.slideshow_mode:
            selected = st.selectbox(
                "Jump to:",
                options=list(range(1, 7)),
                index=st.session_state.current_panel - 1,
                format_func=lambda x: f"Panel {x}"
            )
            if selected != st.session_state.current_panel:
                st.session_state.current_panel = selected
                st.session_state.timer_active = False
                st.rerun()
    
    # Slideshow status
    if st.session_state.slideshow_mode:
        st.markdown(f"""
        <div class="slideshow-active">
            <h3>🎬 Slideshow Mode Active</h3>
            <p>Currently showing Panel {st.session_state.current_panel}/6</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Current panel display
    st.markdown("---")
    
    current_panel_num = st.session_state.current_panel
    panel_data = panels_data[current_panel_num - 1]
    
    # Panel header
    st.markdown(f"""
    <div class="current-panel">
        <h2>🎌 Panel {current_panel_num}: {get_panel_title(current_panel_num)}</h2>
        <p>Progress: {current_panel_num}/6 • {current_panel_num/6*100:.0f}% Complete</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content layout
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Panel image
        st.markdown("#### 🖼️ Panel Image")
        
        image_blob_path = f"stories/{story_id}/panel_{current_panel_num:02d}.png"
        image_data = load_image_from_gcs(bucket_name, image_blob_path)
        
        if image_data:
            st.image(
                image_data, 
                caption=f"Panel {current_panel_num} - Mental Wellness Journey",
                width=550
            )
        else:
            st.error(f"❌ Could not load Panel {current_panel_num} image")
            st.image(
                "https://via.placeholder.com/550x350/cccccc/666666?text=Panel+Image+Not+Found", 
                caption=f"Panel {current_panel_num} - Image Not Found"
            )
        
        # Dialogue text
        dialogue_text = panel_data["dialogue_text"]
        st.markdown(f"""
        <div class="dialogue-text">
            <strong>💭 Panel Narration:</strong><br>
            <em>"{dialogue_text}"</em>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        # Audio controls
        st.markdown("#### 🎵 Audio Controls")
        
        # Load audio files
        tts_blob_path = f"stories/{story_id}/tts_panel_{current_panel_num:02d}.mp3"
        music_blob_path = f"stories/{story_id}/music_panel_{current_panel_num:02d}.mp3"
        
        tts_data = load_audio_from_gcs(bucket_name, tts_blob_path)
        music_data = load_audio_from_gcs(bucket_name, music_blob_path)
        
        # TTS Audio section
        st.markdown('<div class="audio-section">', unsafe_allow_html=True)
        st.markdown("**🎤 Voice Narration (TTS)**")
        if tts_data:
            st.audio(tts_data, format="audio/mp3")
            st.success("✅ TTS audio loaded")
        else:
            st.error("❌ TTS audio not found")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Background Music section
        st.markdown('<div class="audio-section">', unsafe_allow_html=True)
        st.markdown("**🎵 Background Music**")
        if music_data:
            st.audio(music_data, format="audio/mp3")
            st.success("✅ Background music loaded")
        else:
            st.error("❌ Background music not found")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Timer controls (for slideshow mode)
        if st.session_state.slideshow_mode:
            st.markdown("---")
            st.markdown("#### ⏱️ Panel Timer")
            
            estimated_duration = estimate_tts_duration(dialogue_text)
            
            col_timer1, col_timer2 = st.columns(2)
            
            with col_timer1:
                if st.button("🎬 Start Panel Timer", use_container_width=True):
                    st.session_state.timer_active = True
                    st.session_state.timer_start = time.time()
                    st.session_state.estimated_duration = estimated_duration
                    st.info(f"⏱️ Timer started! Panel duration: ~{estimated_duration}s")
                    st.rerun()
            
            with col_timer2:
                if st.button("⏹️ Stop Timer", use_container_width=True):
                    st.session_state.timer_active = False
                    st.rerun()
            
            # Display timer
            if st.session_state.timer_active and st.session_state.timer_start:
                elapsed = int(time.time() - st.session_state.timer_start)
                remaining = max(0, st.session_state.estimated_duration - elapsed)
                
                if remaining > 0:
                    st.markdown(f"""
                    <div class="timer-display">
                        ⏱️ Time remaining: {remaining}s<br>
                        <small>Elapsed: {elapsed}s / {st.session_state.estimated_duration}s</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Auto-refresh every second
                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="timer-display" style="background: #d4edda; border-color: #28a745;">
                        ✅ Panel Complete!<br>
                        <small>Ready to advance to next panel</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("⏭️ Auto-Advance to Next", use_container_width=True):
                        if current_panel_num < 6:
                            st.session_state.current_panel += 1
                            st.session_state.timer_active = False
                            st.success(f"✅ Advanced to Panel {st.session_state.current_panel}")
                            st.rerun()
                        else:
                            st.balloons()
                            st.success("🎉 Slideshow completed!")
                            st.session_state.slideshow_mode = False
                            st.rerun()
    
    # Progress bar
    st.markdown("---")
    progress = current_panel_num / 6
    st.progress(progress)
    st.markdown(f"**Overall Progress:** {current_panel_num}/6 panels ({progress*100:.0f}% complete)")
    
    # Instructions
    if st.session_state.slideshow_mode:
        st.markdown("""
        <div class="instruction-box">
            <h4>🎯 How to Use the Slideshow:</h4>
            <ol>
                <li><strong>🎤 Play TTS:</strong> Click play on the "Voice Narration" audio player above</li>
                <li><strong>🎵 Play Music:</strong> (Optional) Click play on the "Background Music" for ambiance</li>
                <li><strong>⏱️ Start Timer:</strong> Click "Start Panel Timer" to track the panel duration</li>
                <li><strong>👂 Listen:</strong> Enjoy the narration while viewing the panel image</li>
                <li><strong>⏭️ Advance:</strong> When timer shows "Panel Complete", click "Auto-Advance to Next"</li>
                <li><strong>🔄 Repeat:</strong> Continue for all 6 panels</li>
            </ol>
            <p><strong>💡 Pro Tip:</strong> You can play both TTS and background music simultaneously for the full experience!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="instruction-box">
            <h4>📖 Browse Mode Active</h4>
            <p>Use the controls above to start the slideshow or browse panels manually.</p>
            <p><strong>🎬 Ready to start?</strong> Click "Start Slideshow" for the full guided experience!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Panel overview (collapsed during slideshow)
    if not st.session_state.slideshow_mode:
        with st.expander("📚 View All Panels", expanded=False):
            for i, panel in enumerate(panels_data, 1):
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    st.write(f"**Panel {i}**")
                    if st.button(f"Go to {i}"):
                        st.session_state.current_panel = i
                        st.rerun()
                
                with col2:
                    st.write(f"**{get_panel_title(i)}**")
                    st.write(f"*{panel['dialogue_text'][:80]}...*")
                
                with col3:
                    # Check asset availability
                    panel_tts = f"stories/{story_id}/tts_panel_{i:02d}.mp3"
                    panel_music = f"stories/{story_id}/music_panel_{i:02d}.mp3"
                    
                    tts_ok = load_audio_from_gcs(bucket_name, panel_tts) is not None
                    music_ok = load_audio_from_gcs(bucket_name, panel_music) is not None
                    
                    st.write(f"🎤 {'✅' if tts_ok else '❌'}")
                    st.write(f"🎵 {'✅' if music_ok else '❌'}")
                
                if i < len(panels_data):
                    st.markdown("---")

if __name__ == "__main__":
    main()