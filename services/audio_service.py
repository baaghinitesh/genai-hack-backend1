import asyncio
import base64
import io
import tempfile
import os
import httpx
import json
from typing import List, Optional
from google.cloud import aiplatform
from google.auth import default
from google.cloud import texttospeech
from loguru import logger
from config.settings import settings
from services.storage_service import storage_service


class AudioService:
    def __init__(self):
        # Hardcoded configuration - SDK uses GOOGLE_APPLICATION_CREDENTIALS automatically
        self.project_id = settings.vertex_ai_project_id
        self.lyria_model = settings.lyria_model
        self.location = "us-central1"
        self.prediction_client = None
        self.tts_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Lyria (Vertex AI Prediction) and TTS clients."""
        try:
            # Initialize Vertex AI for Lyria using PredictionServiceClient (correct approach)
            aiplatform.init(project=self.project_id, location=self.location)
            self.prediction_client = aiplatform.gapic.PredictionServiceClient()
            
            # Initialize Text-to-Speech client  
            self.tts_client = texttospeech.TextToSpeechClient()
            
            logger.info(f"Audio service initialized - Lyria: {self.lyria_model}, TTS: Chirp 3: HD (with Google Cloud TTS fallback)")
            
        except Exception as e:
            logger.error(f"Failed to initialize audio service: {e}")
            raise
    
    async def generate_background_music(self, prompt: str, panel_number: int) -> bytes:
        """Generate background music using Lyria-002 REST API."""
        try:
            logger.info(f"Generating background music for panel {panel_number}")
            logger.info(f"Music prompt: {prompt[:100]}...")
            
            # Enhanced prompt based on Lyria best practices:
            # Specify genre, mood, instrumentation, tempo
            enhanced_prompt = f"Instrumental ambient music, {prompt}, gentle emotional soundtrack, soft strings, peaceful mood, medium tempo"
            
            # Prepare the Lyria API request based on documentation
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.lyria_model}"
            
            # Create instance following the documented format
            instance = {
                "prompt": enhanced_prompt,
                "negative_prompt": "vocals, singing, drums, loud instruments",  # Exclude vocals, keep it ambient
                "seed": settings.imagen_seed  # Use same seed for consistency across panels
            }
            
            logger.info(f"Calling Lyria API with enhanced prompt")
            
            # Make the prediction using the PredictionServiceClient
            response = await asyncio.to_thread(
                self.prediction_client.predict,
                endpoint=endpoint,
                instances=[instance],
                parameters={}
            )
            
            logger.info(f"Lyria response received: {type(response)}")
            
            # Extract the audio data from response
            if response.predictions and len(response.predictions) > 0:
                prediction = response.predictions[0]
                logger.info(f"Prediction type: {type(prediction)}")
                logger.info(f"Prediction keys: {prediction.keys() if hasattr(prediction, 'keys') else 'No keys'}")
                
                # The response should contain base64 encoded audio (WAV format, 48kHz, 30s)
                if 'bytesBase64Encoded' in prediction:
                    audio_data = base64.b64decode(prediction['bytesBase64Encoded'])
                    logger.info(f"Background music generated successfully for panel {panel_number} - {len(audio_data)} bytes (WAV)")
                    return audio_data
                elif 'bytes_base64_encoded' in prediction:
                    audio_data = base64.b64decode(prediction['bytes_base64_encoded'])
                    logger.info(f"Background music generated successfully for panel {panel_number} - {len(audio_data)} bytes (WAV)")
                    return audio_data
                else:
                    logger.error(f"No audio data found in prediction. Available keys: {list(prediction.keys()) if hasattr(prediction, 'keys') else 'N/A'}")
                    raise Exception("No audio data in Lyria response")
            else:
                logger.error("No predictions in Lyria response")
                raise Exception("No predictions in Lyria response")
                
        except Exception as e:
            logger.error(f"Failed to generate background music for panel {panel_number}: {e}")
            # For hackathon: fall back to a simple placeholder
            logger.warning("Falling back to placeholder audio for hackathon")
            return self._generate_placeholder_audio()
    
    def _generate_placeholder_audio(self) -> bytes:
        """Generate placeholder audio for when Lyria fails."""
        try:
            import numpy as np
            sample_rate = 48000
            duration = 20  # 20 seconds for each panel
            
            # Generate a simple ambient tone (multiple frequencies for richness)
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            # Create a chord with multiple frequencies (ambient sound)
            frequencies = [220, 330, 440]  # A3, E4, A4
            audio_data = np.zeros_like(t)
            
            for freq in frequencies:
                audio_data += np.sin(freq * 2 * np.pi * t) * 0.05  # Very low volume
            
            # Add some gentle fade in/out
            fade_samples = int(sample_rate * 2)  # 2 second fade
            audio_data[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit PCM WAV format (as expected by Lyria)
            audio_data_int16 = (audio_data * 32767).astype(np.int16)
            
            # Create WAV header and data
            import wave
            import io
            
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)  # 48kHz
                wav_file.writeframes(audio_data_int16.tobytes())
            
            wav_data = wav_buffer.getvalue()
            logger.info(f"Generated placeholder audio - {len(wav_data)} bytes (WAV)")
            return wav_data
            
        except Exception as e:
            logger.error(f"Failed to generate placeholder audio: {e}")
            # Return minimal WAV file
            return b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00\x00\x00\x00\x00\x00'
    
    def _select_voice_for_user(self, age: int, gender: str) -> dict:
        """Select appropriate Chirp 3: HD voice based on user gender."""

        # Voice mapping based on gender - using specific Chirp 3: HD voices
        voice_map = {
            "male": {
                "name": "en-IN-Chirp3-HD-Fenrir",  # Male voice
                "language_code": "en-IN"
            },
            "female": {
                "name": "en-IN-Chirp3-HD-Kore",  # Female voice
                "language_code": "en-IN"
            },
            "non-binary": {
                "name": "en-IN-Chirp3-HD-Gacrux",  # Non-binary voice
                "language_code": "en-IN"
            },
            "prefer_not_to_say": {
                "name": "en-IN-Chirp3-HD-Charon",  # Default neutral voice
                "language_code": "en-IN"
            }
        }

        # Normalize gender input
        gender_normalized = gender.lower().strip()
        if gender_normalized not in voice_map:
            if gender_normalized in ["male", "female", "non-binary"]:
                # Use exact match
                pass
            else:
                # Default to prefer not to say for any unrecognized gender
                gender_normalized = "prefer_not_to_say"

        # Get the appropriate voice
        selected_voice = voice_map[gender_normalized]

        logger.info(f"Selected Chirp 3: HD voice for gender {gender}: {selected_voice['name']}")

        return selected_voice

    async def _make_chirp_request(self, request_data: dict) -> bytes:
        """Make API request to Chirp 3: HD for speech synthesis."""
        try:
            # Chirp 3: HD API endpoint (you'll need to replace with actual endpoint)
            chirp_api_url = "https://api.chirp.ai/v1/speech/synthesize"  # Placeholder URL
            
            # Headers for Chirp 3: HD API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.chirp_api_key}",  # You'll need to add this to settings
                "Accept": "audio/mpeg"  # For MP3 output
            }
            
            # Make the API request
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    chirp_api_url,
                    json=request_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    # Return the audio data
                    audio_data = response.content
                    logger.info(f"Chirp 3: HD API request successful - {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.error(f"Chirp 3: HD API request failed: {response.status_code} - {response.text}")
                    raise Exception(f"Chirp 3: HD API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to make Chirp 3: HD request: {e}")
            raise

    async def generate_tts_audio(self, text: str, panel_number: int, user_age: int = 16, user_gender: str = "non-binary") -> bytes:
        """Generate TTS audio using Chirp 3: HD with gender-based voice selection."""
        try:
            logger.info(f"Generating TTS audio for panel {panel_number}")
            logger.info(f"User gender: {user_gender}")
            logger.info(f"TTS text: {text[:100]}...")

            # Select appropriate voice based on gender only
            selected_voice = self._select_voice_for_user(user_age, user_gender)

            # Use Google Cloud Text-to-Speech directly for Chirp 3: HD voices
            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=selected_voice["language_code"],
                name=selected_voice["name"]
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,  # Standard speaking rate for all users
                pitch=0.0,
                volume_gain_db=0.0
            )

            response = await asyncio.to_thread(
                self.tts_client.synthesize_speech,
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            # Return the audio data
            audio_data = response.audio_content
            logger.info(f"TTS audio generated successfully for panel {panel_number} - {len(audio_data)} bytes")
            logger.info(f"Used Chirp 3: HD voice: {selected_voice['name']}")
            return audio_data

        except Exception as e:
            logger.error(f"Failed to generate TTS audio for panel {panel_number}: {e}")
            raise
    
    async def generate_all_audio(self, panels: List[dict], story_id: str, user_age: int = 16, user_gender: str = "non-binary") -> tuple[List[str], List[str]]:
        """Generate background music and TTS for all panels with personalized voice."""
        try:
            logger.info(f"Generating audio for user: {user_age} years old, {user_gender}")
            
            async def generate_single_panel_audio(panel: dict, panel_num: int) -> tuple[str, str]:
                """Generate audio for a single panel (music + TTS)."""
                logger.info(f"Generating audio for panel {panel_num}")
                
                # Generate background music and TTS in parallel for this panel
                music_prompt = panel.get('music_prompt', f"Emotional ambient music for panel {panel_num}")
                dialogue_text = panel.get('dialogue_text', f"Panel {panel_num} narration")
                
                music_task = self.generate_background_music(music_prompt, panel_num)
                tts_task = self.generate_tts_audio(dialogue_text, panel_num, user_age, user_gender)
                
                background_data, tts_data = await asyncio.gather(music_task, tts_task)
                
                # Upload both audio files in parallel
                background_upload_task = storage_service.upload_background_music(background_data, story_id, panel_num)
                tts_upload_task = storage_service.upload_tts_audio(tts_data, story_id, panel_num)
                
                background_url, tts_url = await asyncio.gather(background_upload_task, tts_upload_task)
                
                logger.info(f"Panel {panel_num} audio generated and uploaded")
                return background_url, tts_url
            
            # Generate audio for all panels in parallel
            tasks = [generate_single_panel_audio(panel, i) for i, panel in enumerate(panels, 1)]
            results = await asyncio.gather(*tasks)
            
            # Separate background and TTS URLs
            background_urls = [result[0] for result in results]
            tts_urls = [result[1] for result in results]
            
            logger.info(f"All audio generated for {len(panels)} panels")
            return background_urls, tts_urls
            
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            raise
    

    

    
    async def create_audio_prompt(self, panel_data: dict, emotional_tone: str) -> str:
        """Create optimized music generation prompt."""
        character = panel_data.get('character_sheet', {})
        props = panel_data.get('prop_sheet', {})
        
        prompt = f"""
        Generate a {emotional_tone}-toned ambient track for a manga panel.
        Character: {character.get('name', 'Character')}
        Setting: {props.get('environment', '')}
        Mood elements: {', '.join(props.get('mood_elements', []))}
        Duration: 15-20 seconds
        Style: Emotional and atmospheric background music
        """
        
        return prompt.strip()


# Global audio service instance
audio_service = AudioService()
