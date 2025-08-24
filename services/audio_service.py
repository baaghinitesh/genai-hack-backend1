import asyncio
import base64
import io
import tempfile
import os
from typing import List, Optional
from pydub import AudioSegment
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
            
            logger.info(f"Audio service initialized - Lyria: {self.lyria_model}, TTS: Cloud Text-to-Speech")
            
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
        """Select appropriate voice based on user age and gender."""
        
        # Voice mapping based on Google Cloud TTS available voices
        voice_map = {
            # Young voices (10-17 years)
            "young": {
                "male": {
                    "name": "en-US-Neural2-J",  # Young male voice
                    "gender": texttospeech.SsmlVoiceGender.MALE
                },
                "female": {
                    "name": "en-US-Neural2-F",  # Young female voice  
                    "gender": texttospeech.SsmlVoiceGender.FEMALE
                },
                "non-binary": {
                    "name": "en-US-Neural2-F",  # Neutral young voice
                    "gender": texttospeech.SsmlVoiceGender.FEMALE
                }
            },
            # Teen voices (13-19 years)
            "teen": {
                "male": {
                    "name": "en-US-Standard-D",  # Teen male voice
                    "gender": texttospeech.SsmlVoiceGender.MALE
                },
                "female": {
                    "name": "en-US-Standard-E",  # Teen female voice
                    "gender": texttospeech.SsmlVoiceGender.FEMALE
                },
                "non-binary": {
                    "name": "en-US-Standard-H",  # Neutral teen voice
                    "gender": texttospeech.SsmlVoiceGender.FEMALE
                }
            },
            # Adult voices (20+ years)
            "adult": {
                "male": {
                    "name": "en-US-Neural2-A",  # Adult male voice
                    "gender": texttospeech.SsmlVoiceGender.MALE
                },
                "female": {
                    "name": "en-US-Neural2-C",  # Adult female voice
                    "gender": texttospeech.SsmlVoiceGender.FEMALE
                },
                "non-binary": {
                    "name": "en-US-Neural2-F",  # Neutral adult voice
                    "gender": texttospeech.SsmlVoiceGender.FEMALE
                }
            }
        }
        
        # Determine age category
        if age <= 12:
            age_category = "young"
        elif age <= 19:
            age_category = "teen"
        else:
            age_category = "adult"
        
        # Normalize gender input
        gender_normalized = gender.lower()
        if gender_normalized not in ["male", "female", "non-binary"]:
            gender_normalized = "non-binary"  # Default fallback
        
        # Get the appropriate voice
        selected_voice = voice_map[age_category][gender_normalized]
        
        logger.info(f"Selected voice for age {age}, gender {gender}: {selected_voice['name']} ({age_category})")
        
        return selected_voice

    async def generate_tts_audio(self, text: str, panel_number: int, user_age: int = 16, user_gender: str = "non-binary") -> bytes:
        """Generate TTS audio using Google Cloud Text-to-Speech with dynamic voice selection."""
        try:
            logger.info(f"Generating TTS audio for panel {panel_number}")
            logger.info(f"User: {user_age} years old, {user_gender}")
            logger.info(f"TTS text: {text[:100]}...")
            
            # Select appropriate voice based on user demographics
            selected_voice = self._select_voice_for_user(user_age, user_gender)
            
            # Prepare the TTS request using Google Cloud Text-to-Speech API
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice based on user demographics
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name=selected_voice["name"],
                ssml_gender=selected_voice["gender"]
            )
            
            # Configure audio format with age-appropriate settings
            speaking_rate = 0.9 if user_age <= 12 else 1.0  # Slightly slower for young users
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate,
                pitch=0.0,
                volume_gain_db=0.0
            )
            
            # Generate TTS audio
            response = await asyncio.to_thread(
                self.tts_client.synthesize_speech,
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Return the audio data
            audio_data = response.audio_content
            logger.info(f"TTS audio generated successfully for panel {panel_number} - {len(audio_data)} bytes")
            logger.info(f"Used voice: {selected_voice['name']}")
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
    
    async def synchronize_audio(self, background_urls: List[str], tts_urls: List[str], story_id: str) -> str:
        """Synchronize background music and TTS into a single audio track."""
        try:
            # Create a combined audio track
            combined_audio = AudioSegment.empty()
            
            for i, (bg_url, tts_url) in enumerate(zip(background_urls, tts_urls)):
                logger.info(f"Synchronizing audio for panel {i + 1}")
                
                # Load background music
                bg_audio = AudioSegment.from_mp3(io.BytesIO(await self._download_audio(bg_url)))
                
                # Load TTS audio
                tts_audio = AudioSegment.from_mp3(io.BytesIO(await self._download_audio(tts_url)))
                
                # Ensure background music is 20 seconds
                if len(bg_audio) > 20000:  # 20 seconds in milliseconds
                    bg_audio = bg_audio[:20000]
                elif len(bg_audio) < 20000:
                    # Extend with silence if too short
                    silence_needed = 20000 - len(bg_audio)
                    silence_audio = AudioSegment.silent(duration=silence_needed)
                    bg_audio = bg_audio + silence_audio
                
                # Overlay TTS on background music
                panel_audio = bg_audio.overlay(tts_audio)
                
                # Add to combined audio
                combined_audio += panel_audio
                
                # Add 2-second silence between panels (except after the last one)
                if i < len(background_urls) - 1:
                    silence_audio = AudioSegment.silent(duration=2000)  # 2 seconds
                    combined_audio += silence_audio
            
            # Export as MP3
            audio_buffer = io.BytesIO()
            combined_audio.export(audio_buffer, format="mp3")
            audio_data = audio_buffer.getvalue()
            
            # Upload to GCS
            final_audio_url = await storage_service.upload_audio(audio_data, story_id, "final")
            
            logger.info(f"Audio synchronization completed: {final_audio_url}")
            return final_audio_url
            
        except Exception as e:
            logger.error(f"Failed to synchronize audio: {e}")
            raise
    
    async def _download_audio(self, url: str) -> bytes:
        """Download audio file from GCS using client instead of HTTP."""
        try:
            from google.cloud import storage
            
            # Extract bucket and blob path from GCS URL
            # URL format: https://storage.googleapis.com/bucket-name/path/file.ext
            url_parts = url.replace('https://storage.googleapis.com/', '').split('/', 1)
            bucket_name = url_parts[0]
            blob_path = url_parts[1]
            
            # Use GCS client to download
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_path)
            return blob.download_as_bytes()
                
        except Exception as e:
            logger.error(f"Failed to download audio from {url}: {e}")
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
