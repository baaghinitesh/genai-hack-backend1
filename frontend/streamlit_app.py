import streamlit as st
import requests
import json
import time
import asyncio
from typing import Dict, List
import base64
from io import BytesIO
from PIL import Image
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="🎌 Manga Mental Wellness",
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

.status-success {
    background: #D4F5D4;
    padding: 10px;
    border-radius: 5px;
    border-left: 4px solid #28A745;
}

.status-error {
    background: #F8D7DA;
    padding: 10px;
    border-radius: 5px;
    border-left: 4px solid #DC3545;
}

.slideshow-container {
    max-width: 800px;
    margin: auto;
    position: relative;
    background: #f9f9f9;
    border-radius: 15px;
    padding: 20px;
}

.panel-slide {
    display: none;
    text-align: center;
    animation: fadeIn 0.5s;
}

.panel-slide.active {
    display: block;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

.controls {
    text-align: center;
    margin-top: 20px;
}

.progress-bar {
    width: 100%;
    height: 20px;
    background: #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
    margin: 20px 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #FF6B9D, #C7A2FF);
    transition: width 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎌 Manga Mental Wellness - Your Story Ready!</h1>
        <p>✅ Complete 6-panel manga story with background music and TTS</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show the existing complete story directly
    st.markdown("---")
    
    # Story selector
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🎬 Your Completed Stories")
        story_id = st.selectbox(
            "Select a story to view:",
            ["story_884416", "story_885418"],
            index=0,
            help="Choose from your generated stories"
        )
    
    with col2:
        st.markdown("### 🎮 Quick Actions")
        if st.button("🔄 Refresh Story", use_container_width=True):
            st.rerun()
        if st.button("🎵 Play Audio Only", use_container_width=True):
            audio_url = f"https://storage.googleapis.com/calmira-backend/stories/{story_id}/final_audio.mp3"
            st.audio(audio_url)
    
    # Display the complete story immediately
    display_complete_story(story_id)
    
    # Show additional story information
    st.markdown("---")
    show_story_info()


def display_complete_story(story_id: str):
    """Display the complete manga story with assets from GCS directly."""
    
    try:
        # Build story data directly from known assets
        base_url = f"https://storage.googleapis.com/calmira-backend/stories/{story_id}/"
        
        # Create mock story data
        story_data = {
            "story_id": story_id,
            "panels": [
                {"panel_number": 1, "dialogue_text": "Every day, I wake up with one goal: to be a good human being, kind to everyone I meet..."},
                {"panel_number": 2, "dialogue_text": "But the world isn't always easy. Sometimes, it feels like an endless fight… to keep that kindness alive..."},
                {"panel_number": 3, "dialogue_text": "Is this 'fight' truly external? Or is it a battle within myself? To master my own reactions, my own choices..."},
                {"panel_number": 4, "dialogue_text": "My hobby, fighting, taught me discipline. Not to strike down, but to stand firm. To control my own choices..."},
                {"panel_number": 5, "dialogue_text": "True strength isn't about winning arguments or overpowering others. It's about choosing compassion..."},
                {"panel_number": 6, "dialogue_text": "And as I choose kindness, day by day, I find my inner peace. My journey continues, stronger and more..."}
            ],
            "image_urls": [f"{base_url}panel_{i:02d}.png" for i in range(1, 7)],
            "audio_url": f"{base_url}final_audio.mp3",
            "status": "completed"
        }
        
        st.success(f"✅ Displaying completed story: {story_id}")
        
        # Display the slideshow
        display_manga_slideshow(story_data)
        
    except Exception as e:
        st.error(f"❌ Error loading story: {str(e)}")
        # Show debug info
        st.expander("Debug Info").write(f"Story ID: {story_id}, Error: {e}")


def display_manga_slideshow(story: Dict):
    """Display the manga story as an interactive slideshow."""
    
    panels = story.get("panels", [])
    image_urls = story.get("image_urls", [])
    audio_url = story.get("audio_url", "")
    
    st.markdown("---")
    
    # Main audio player - prominent position
    if audio_url:
        st.markdown("### 🎵 Complete Story Audio (Background Music + Voice)")
        st.markdown(f"**🔗 Audio URL:** `{audio_url}`")
        
        try:
            st.audio(audio_url, format="audio/mp3")
            st.info("▶️ **Play the audio above and navigate through panels below for the complete manga experience!**")
        except Exception as e:
            st.error(f"❌ Could not load audio: {e}")
            
            # Test audio URL
            try:
                import requests
                response = requests.head(audio_url, timeout=5)
                st.write(f"Audio HTTP Status: {response.status_code}")
            except Exception as req_error:
                st.write(f"Audio URL Test Error: {req_error}")
    
    # Full slideshow display
    if panels and image_urls:
        
        # Navigation controls
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
                options=list(range(1, len(image_urls) + 1)),
                index=st.session_state.current_panel - 1,
                format_func=lambda x: f"Panel {x}: {get_panel_title(x)}",
                key="panel_selector"
            )
            st.session_state.current_panel = current_panel
        
        with col3:
            if st.button("➡️ Next", use_container_width=True):
                st.session_state.current_panel = min(len(image_urls), st.session_state.current_panel + 1)
        
        # Display current panel large
        st.markdown("---")
        display_panel_large(panels[current_panel - 1], image_urls[current_panel - 1], current_panel)
        
        # Show all panels in grid
        st.markdown("---")
        st.subheader("📚 All 6 Panels Overview")
        
        # Display in 2x3 grid
        for row in range(3):
            cols = st.columns(2)
            for col_idx, col in enumerate(cols):
                panel_idx = row * 2 + col_idx
                if panel_idx < len(image_urls):
                    with col:
                        panel_num = panel_idx + 1
                        st.markdown(f"**Panel {panel_num}: {get_panel_title(panel_num)}**")
                        try:
                            st.image(image_urls[panel_idx], caption=f"Panel {panel_num}", width=None)
                            st.write(f"*{panels[panel_idx].get('dialogue_text', '')[:100]}...*")
                        except Exception as e:
                            st.error(f"Could not load Panel {panel_num}: {e}")
                            st.code(f"URL: {image_urls[panel_idx]}")
                            
                            # Test if URL is accessible
                            try:
                                import requests
                                response = requests.head(image_urls[panel_idx], timeout=3)
                                st.write(f"Status: {response.status_code}")
                            except:
                                st.write("❌ URL not accessible")
    
    else:
        st.warning("⚠️ No panels or images available.")
        st.json(story)


def display_panel_large(panel: Dict, image_url: str, panel_number: int):
    """Display a single manga panel in large format."""
    
    st.markdown(f"""
    <div class="panel-container">
        <div class="panel-header">Panel {panel_number}: {get_panel_title(panel_number)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Full width image display with debugging
    st.markdown(f"**🔗 Image URL:** `{image_url}`")
    
    try:
        st.image(image_url, caption=f"Panel {panel_number} - Rohit's Mental Wellness Journey", width=None)
    except Exception as e:
        st.error(f"❌ Could not load Panel {panel_number} image")
        st.code(f"Image URL: {image_url}")
        st.write(f"Error: {e}")
        
        # Test URL accessibility
        try:
            import requests
            response = requests.head(image_url, timeout=5)
            st.write(f"HTTP Status: {response.status_code}")
            st.write(f"Headers: {dict(response.headers)}")
        except Exception as req_error:
            st.write(f"URL Test Error: {req_error}")
    
    # Display dialogue prominently
    dialogue_text = panel.get("dialogue_text", "")
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


def display_panel_summary(panel: Dict, image_url: str, panel_number: int):
    """Display a summary view of a panel."""
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        try:
            st.image(image_url, width=200)
        except:
            st.text("Image unavailable")
    
    with col2:
        dialogue_text = panel.get("dialogue_text", "")
        st.write(f"**Dialogue:** {dialogue_text[:100]}{'...' if len(dialogue_text) > 100 else ''}")
        
        music_prompt = panel.get("music_prompt", "")
        st.write(f"**Music:** {music_prompt}")


def get_panel_title(panel_number: int) -> str:
    """Get descriptive title for each panel based on story structure."""
    titles = {
        1: "Introduction",
        2: "Challenge", 
        3: "Reflection",
        4: "Discovery",
        5: "Transformation",
        6: "Resolution"
    }
    return titles.get(panel_number, f"Panel {panel_number}")


def show_story_info():
    """Show information about the completed stories."""
    
    st.markdown("## 🎌 Your Completed Manga Stories")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📖 Story_884416 - "Rohit's Journey"
        **Character:** Rohit (24-year-old male)  
        **Theme:** Inner strength through martial arts  
        **Style:** Demon Slayer manga aesthetic  
        **Status:** ✅ Complete with audio  
        
        **Story Arc:**
        1. **Introduction** - Daily pursuit of kindness
        2. **Challenge** - World's difficulties
        3. **Reflection** - Internal vs external battles
        4. **Discovery** - Discipline through fighting
        5. **Transformation** - True strength definition
        6. **Resolution** - Finding inner peace
        """)
    
    with col2:
        st.markdown("""
        ### 🎵 Audio Components Generated
        **Background Music:** Lyria-002 compositions  
        **Voice Narration:** Male adult voice (en-US-Neural2-A)  
        **Final Audio:** Separate background music and TTS files  
        
        **Technical Details:**
        - **Image Model:** Imagen 4.0 with typography
        - **TTS Model:** Google Cloud Text-to-Speech
        - **Music Model:** Lyria-002 via Vertex AI
        - **Storage:** Google Cloud Storage
        - **Total Duration:** ~2-3 minutes
        """)
    
    st.markdown("---")
    st.info("🎯 **Ready to Experience:** Your complete manga story with background music and TTS is ready above!")


def check_backend_health():
    """Check if the backend is running and healthy."""
    
    st.markdown("## 🔍 Backend Status")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            
            st.markdown("""
            <div class="status-success">
                ✅ Backend is healthy and ready!
            </div>
            """, unsafe_allow_html=True)
            
            # Show service status
            services = health_data.get("services", {})
            if services:
                st.markdown("**Service Status:**")
                for service, status in services.items():
                    status_icon = "✅" if "healthy" in status else "⚠️"
                    st.write(f"{status_icon} **{service.replace('_', ' ').title()}:** {status}")
        
        else:
            st.markdown("""
            <div class="status-error">
                ❌ Backend is not responding properly
            </div>
            """, unsafe_allow_html=True)
    
    except requests.exceptions.ConnectionError:
        st.markdown("""
        <div class="status-error">
            🔌 Backend is not running. Please start the server with:<br>
            <code>python start_backend.py</code>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.markdown(f"""
        <div class="status-error">
            ❌ Error checking backend: {str(e)}
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()