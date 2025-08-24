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

# Configure Streamlit page
st.set_page_config(
    page_title="🎌 Manga Mental Wellness - GCS Direct",
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

def display_panel_with_gcs(story_id: str, panel_number: int, dialogue_text: str):
    """Display a panel by loading directly from GCS."""
    
    bucket_name = "calmira-backend"
    image_blob_path = f"stories/{story_id}/panel_{panel_number:02d}.png"
    
    st.markdown(f"""
    <div class="panel-container">
        <div class="panel-header">Panel {panel_number}: {get_panel_title(panel_number)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Load and display image
    image_data = load_image_from_gcs(bucket_name, image_blob_path)
    
    if image_data:
        st.image(image_data, caption=f"Panel {panel_number} - Rohit's Mental Wellness Journey")
        st.success(f"✅ Panel {panel_number} loaded successfully from GCS")
    else:
        st.error(f"❌ Could not load Panel {panel_number} from GCS path: {image_blob_path}")
    
    # Display dialogue
    if dialogue_text:
        st.markdown(f"""
        <div class="dialogue-text">
            <strong>💭 Narration:</strong><br>
            <em>"{dialogue_text}"</em>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress indicator
    progress = panel_number / 6
    st.progress(progress)
    st.caption(f"Panel {panel_number} of 6 • {progress*100:.0f}% Complete")

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

def main():
    """Main Streamlit application with direct GCS access."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎌 Manga Mental Wellness - Direct GCS Access</h1>
        <p>✅ Loading content directly from Google Cloud Storage</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Story data
    story_id = "story_884416"
    panels_data = [
        {"panel_number": 1, "dialogue_text": "Every day, I wake up with one goal: to be a good human being, kind to everyone I meet..."},
        {"panel_number": 2, "dialogue_text": "But the world isn't always easy. Sometimes, it feels like an endless fight… to keep that kindness alive..."},
        {"panel_number": 3, "dialogue_text": "Is this 'fight' truly external? Or is it a battle within myself? To master my own reactions, my own choices..."},
        {"panel_number": 4, "dialogue_text": "My hobby, fighting, taught me discipline. Not to strike down, but to stand firm. To control my own choices..."},
        {"panel_number": 5, "dialogue_text": "True strength isn't about winning arguments or overpowering others. It's about choosing compassion..."},
        {"panel_number": 6, "dialogue_text": "And as I choose kindness, day by day, I find my inner peace. My journey continues, stronger and more..."}
    ]
    
    # Load and display audio
    st.markdown("### 🎵 Complete Story Audio (Background Music + Voice)")
    
    bucket_name = "calmira-backend"
    audio_blob_path = f"stories/{story_id}/final_audio.mp3"
    
    audio_data = load_audio_from_gcs(bucket_name, audio_blob_path)
    
    if audio_data:
        st.audio(audio_data, format="audio/mp3")
        st.success("✅ Audio loaded successfully from GCS")
        st.info("▶️ **Play the audio above and navigate through panels below for the synchronized manga experience!**")
    else:
        st.error(f"❌ Could not load audio from GCS path: {audio_blob_path}")
    
    st.markdown("---")
    
    # Panel navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Previous", use_container_width=True):
            if "current_panel" not in st.session_state:
                st.session_state.current_panel = 1
            st.session_state.current_panel = max(1, st.session_state.current_panel - 1)
    
    with col2:
        if "current_panel" not in st.session_state:
            st.session_state.current_panel = 1
        
        current_panel = st.selectbox(
            "📖 Panel Navigation",
            options=list(range(1, 7)),
            index=st.session_state.current_panel - 1,
            format_func=lambda x: f"Panel {x}: {get_panel_title(x)}",
            key="panel_selector"
        )
        st.session_state.current_panel = current_panel
    
    with col3:
        if st.button("➡️ Next", use_container_width=True):
            st.session_state.current_panel = min(6, st.session_state.current_panel + 1)
    
    # Display current panel
    st.markdown("---")
    panel_data = panels_data[current_panel - 1]
    display_panel_with_gcs(story_id, current_panel, panel_data["dialogue_text"])
    
    # Show all panels overview
    st.markdown("---")
    st.subheader("📚 All 6 Panels Overview (Direct GCS Loading)")
    
    # Display in 2x3 grid
    for row in range(3):
        cols = st.columns(2)
        for col_idx, col in enumerate(cols):
            panel_idx = row * 2 + col_idx
            if panel_idx < 6:
                with col:
                    panel_num = panel_idx + 1
                    panel_data = panels_data[panel_idx]
                    
                    st.markdown(f"**Panel {panel_num}: {get_panel_title(panel_num)}**")
                    
                    # Load image from GCS
                    image_blob_path = f"stories/{story_id}/panel_{panel_num:02d}.png"
                    image_data = load_image_from_gcs(bucket_name, image_blob_path)
                    
                    if image_data:
                        st.image(image_data, caption=f"Panel {panel_num}")
                        st.write(f"*{panel_data['dialogue_text'][:100]}...*")
                    else:
                        st.error(f"❌ Panel {panel_num} not found")
                        st.code(f"Path: {image_blob_path}")

if __name__ == "__main__":
    main()
