# language_practice/src/audio_engine.py - Complete structural file update pass

import os
import sys
import subprocess
from pathlib import Path
from .config import settings
from .models import PhraseTranslation, SystemSetting
from .database import SessionLocal

# Update the filename block inside generate_translation_audio in language_practice/src/audio_engine.py
def generate_translation_audio(translation: PhraseTranslation, force: bool = False) -> str:
    """
    Compiles localized text sentences safely into offline MP3 voice assets.
    """
    # Force clean filename formatting extraction by splitting off any directory tags safely
    if translation.audio_path:
        filename = translation.audio_path.split("/")[-1]
    else:
        filename = f"{translation.language_code}_{translation.group_id}.mp3"

    file_path = settings.AUDIO_DIR / filename
    relative_path = f"audio/{filename}"

    # Force re-write paths cleanly to database memory columns
    translation.audio_path = relative_path

    if file_path.exists() and not force:
        return relative_path
        
    try:
        text_to_speak = translation.translated_text
        lang = translation.language_code
        
        # Update the platform conditional slice inside language_practice/src/audio_engine.py
        if sys.platform == "darwin":
            temp_aiff = settings.AUDIO_DIR / filename.replace(".mp3", ".aiff")

            db = SessionLocal()
            try:
                setting_key = f"voice_{lang}"
                voice_row = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
                voice_name = voice_row.value if voice_row else "Thomas"  # default fallback
            finally:
                db.close()
                            
            subprocess.run(["say", "-v", voice_name, "-o", str(temp_aiff), text_to_speak], check=True)
    
            ffmpeg_path = "/opt/homebrew/bin/ffmpeg"
            if os.path.exists(ffmpeg_path):
                subprocess.run([
                    ffmpeg_path, "-i", str(temp_aiff), 
                    "-y", "-acodec", "libmp3lame", "-aq", "4", 
                    str(file_path)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                
                if temp_aiff.exists():
                    os.remove(temp_aiff)
            else:
                os.rename(temp_aiff, file_path)
        else:
            with open(file_path, "wb") as f:
                f.write(b"")
                
        return relative_path
        
    except Exception as e:
        print(f" ! Offline Audio Engine processing failure: {str(e)}")
        return ""
