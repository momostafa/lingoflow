# language_practice/src/main.py
import httpx
import csv
import io
import subprocess
import re
from fastapi import FastAPI, Depends, Query, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import UploadFile, File
from openai import AsyncOpenAI

from .database import get_db, engine, Base
from .config import settings  # Import our absolute path settings container
from . import crud
from .audio_engine import generate_translation_audio
from .models import PhraseTranslation, PhraseGroup, SystemSetting

app = FastAPI(title="LingoFlow")

# Fix 404: Resolve folders absolutely relative to our true application roots
app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(settings.BASE_DIR / "language_practice" / "templates"))

# Practice page
@app.get("/practice", response_class=HTMLResponse)
async def read_practice_grid(
    request: Request,
    db: Session = Depends(get_db),
    languages: Optional[List[str]] = Query(None, alias="lang"),
    category: Optional[str] = Query("all"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1)
):
    skip = (page - 1) * limit
    matrix_data = crud.get_unified_practice_matrix(
        db, languages=languages, category=category, skip=skip, limit=limit
    )
    
    # --- AUTOMATIC AUDIO CACHE VERIFICATION ROUTINE ---
    for row in matrix_data["data"]:
        group_id = row["id"]
        db_translations = db.query(PhraseTranslation).filter(PhraseTranslation.group_id == group_id).all()
        
        for trans in db_translations:
            if not trans.audio_path or not (settings.STATIC_DIR / trans.audio_path).exists():
                new_path = generate_translation_audio(trans)
                if new_path:
                    trans.audio_path = new_path
                    db.commit()
                    
    available_languages = ["fr", "ru", "ua", "no", "it", "es", "ar"]
    
    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "phrases": matrix_data["data"],
            "total_records": matrix_data["total"],
            "current_page": page,
            "limit": limit,
            "selected_languages": languages or ["fr", "ru", "it", "ua", "no", "es", "ar"],
            "available_languages": available_languages,
            "selected_category": category
        }
    )

@app.post("/api/practice/{group_id}/track")
async def update_phrase_analytics(
    group_id: int,
    score: Optional[int] = Query(None, ge=0, le=10),
    increment_play: Optional[bool] = Query(False),
    notes: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    updated_group = crud.update_phrase_tracking(
        db,
        group_id=group_id,
        score=score,
        play_count_increment=increment_play,
        notes=notes
    )
    if not updated_group:
        raise HTTPException(status_code=404, detail="Master phrase group not found")
        
    return {
        "status": "success",
        "group_id": updated_group.id,
        "play_count": updated_group.play_count,
        "score": updated_group.score,
        "notes": updated_group.practice_notes
    }


@app.post("/api/practice/regenerate-audio")
async def bulk_regenerate_missing_audio(db: Session = Depends(get_db)):
    translations = db.query(PhraseTranslation).all()
    rebuilt_count = 0
    
    for trans in translations:
        file_missing = not trans.audio_path or not (settings.STATIC_DIR / trans.audio_path).exists()
        if file_missing:
            new_path = generate_translation_audio(trans)
            if new_path:
                trans.audio_path = new_path
                rebuilt_count += 1
                
    if rebuilt_count > 0:
        db.commit()
        
    return {
        "status": "success",
        "message": f"Scan finished. Successfully compiled {rebuilt_count} audio files.",
        "rebuilt_files_count": rebuilt_count
    }


@app.post("/api/practice/{phrase_id}/score")
async def update_phrase_self_score(phrase_id: int, score: int = Query(..., ge=0, le=10), db: Session = Depends(get_db)):
    phrase = db.query(PhraseGroup).filter(PhraseGroup.id == phrase_id).first()
    if not phrase:
        return {"status": "error", "message": "Target record not found."}
        
    phrase.score = score
    if score >= 8:
        phrase.mastery_status = "Mastered"
    elif score >= 4:
        phrase.mastery_status = "Learning"
    else:
        phrase.mastery_status = "Needs Practice"
        
    db.commit()
    
    return {
        "status": "success",
        "score": phrase.score,
        "mastery_badge": f"• {phrase.mastery_status}",
        "phrase_id": phrase_id
    }


# ─── UPGRADED LOCAL INFERENCE ROUTE VIA REFACTORED OPENAI ENGINE ───
@app.post("/api/practice/{phrase_id}/ai")
async def trigger_local_ai_inference(phrase_id: int, payload: dict = None, db: Session = Depends(get_db)):
    """
    Connects to the active local LLM backend using the official openai SDK client wrapper.
    Provides conversational AI assistance for language practice.
    """
    payload = payload or {}
    custom_command = payload.get("command", "").strip()
    active_languages = payload.get("languages", ["fr", "ru", "it"])

    cfg = {row.key: row.value for row in db.query(SystemSetting).all()}

    endpoint = cfg.get("llm_endpoint", "http://127.0.0.1:8080").rstrip("/")
    model_name = cfg.get("llm_model", "unsloth/gemma-4-E2B-it-GGUF:Q4_K_XL")
    persona = cfg.get("ai_persona", "negotiator")

    phrase = db.query(PhraseGroup).filter(PhraseGroup.id == phrase_id).first()
    if not phrase:
        return {"status": "error", "message": "Target practice row record not found."}

    # Simplified conversational system prompt
    system_prompt = (
        "You are a helpful language learning assistant. "
        "Provide concise, practical assistance for language practice. "
        "Keep responses under 5 sentences unless the user requests more detail."
    )

    # Initial conversational greeting
    if not custom_command:
        user_prompt = f"Hello, how can I help you practice: '{phrase.master_text}'?\n"
        user_prompt += f"Category: {phrase.category}\n"
        user_prompt += f"Notes: {phrase.practice_notes}\n"
        user_prompt += "\nYou can help the user by:\n"
        user_prompt += "- Explaining the phrase meaning and usage\n"
        user_prompt += "- Suggesting alternative phrasings (more formal, more casual, more complex, etc.)\n"
        user_prompt += "- Providing grammar tips\n"
        user_prompt += "- Offering cultural context\n"
    else:
        user_prompt = f"Current phrase: '{phrase.master_text}'\n"
        user_prompt += f"Category: {phrase.category}\n"
        user_prompt += f"Notes: {phrase.practice_notes}\n\n"
        user_prompt += f"User request: {custom_command}"

    try:
        # Initialize the official SDK Client pointing directly to our system setting parameters
        ai_client = AsyncOpenAI(base_url=f"{endpoint}/v1", api_key="local-dev-bypass")

        # Dispatch the standard structural payload request
        completion = await ai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1024  # Security cap to protect against looping timeouts
        )

        # Access the underlying string payload using object attributes natively
        ai_response = completion.choices[0].message.content

    except Exception as e:
        return {"status": "error", "message": f"SDK communication link failure with current server: {str(e)}"}

    # Strip out literal quotes if your underlying LLM output returned them explicitly wrapped
    clean_response = ai_response.strip()
    if clean_response.startswith('"') and clean_response.endswith('"'):
        clean_response = clean_response[1:-1].strip()

    return {
        "status": "success",
        "ai_analysis": clean_response,
        "translations_patched": False
    }


@app.post("/api/practice/{phrase_id}/generate-translations")
async def generate_missing_translations(phrase_id: int, payload: dict = None, db: Session = Depends(get_db)):
    """
    Manually generate translations for missing languages using the configured LLM.
    User can trigger this on-demand from the AI modal.
    """
    payload = payload or {}
    active_languages = payload.get("languages", ["fr", "ru", "it"])

    cfg = {row.key: row.value for row in db.query(SystemSetting).all()}
    endpoint = cfg.get("llm_endpoint", "http://127.0.0.1:8080").rstrip("/")
    model_name = cfg.get("llm_model", "unsloth/gemma-4-E2B-it-GGUF:Q4_K_XL")

    phrase = db.query(PhraseGroup).filter(PhraseGroup.id == phrase_id).first()
    if not phrase:
        return {"status": "error", "message": "Target practice row record not found."}

    existing_langs = [t.language_code for t in phrase.translations]
    missing_langs = [l for l in active_languages if l not in existing_langs]

    if not missing_langs:
        return {"status": "success", "message": "All translations already exist.", "generated_count": 0}

    # Generate translations using LLM
    system_prompt = (
        "You are a professional translator. "
        "Translate the given phrase into the specified languages accurately and naturally. "
        "Format your response with each translation on a new line, prefixed with the language code in brackets: [code]: translation"
    )

    user_prompt = f"Translate this phrase into {missing_langs}: '{phrase.master_text}'\n"
    user_prompt += f"Context: {phrase.category} - {phrase.practice_notes}\n"
    user_prompt += f"Format exactly like this:\n"
    for lang in missing_langs:
        user_prompt += f"[{lang}]: translated phrase\n"

    try:
        ai_client = AsyncOpenAI(base_url=f"{endpoint}/v1", api_key="local-dev-bypass")
        completion = await ai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=512
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        return {"status": "error", "message": f"Translation generation failed: {str(e)}"}

    # Parse and create translations
    generated_count = 0
    for line in ai_response.split("\n"):
        clean_line = line.strip()
        for lang in missing_langs:
            prefix_match = f"[{lang}]:"
            if clean_line.lower().startswith(prefix_match.lower()):
                clean_text = clean_line[len(prefix_match):].strip().replace('"', '')
                if clean_text:
                    new_trans = PhraseTranslation(
                        group_id=phrase.id,
                        language_code=lang,
                        translated_text=clean_text,
                        audio_path=f"audio/{lang}_{phrase.id}.mp3"
                    )
                    db.add(new_trans)
                    db.flush()
                    generate_translation_audio(new_trans, force=True)
                    generated_count += 1

    if generated_count > 0:
        db.commit()

    return {
        "status": "success",
        "message": f"Successfully generated {generated_count} translations.",
        "generated_count": generated_count
    }


@app.post("/api/practice/{phrase_id}/update-master")
async def update_master_text(phrase_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    Update the master text, regenerate translations, and generate audio files.
    Called after user confirms AI's proposed changes.
    """
    new_master_text = payload.get("new_master_text", "").strip()
    active_languages = payload.get("languages", ["fr", "ru", "it"])

    if not new_master_text:
        return {"status": "error", "message": "New master text cannot be empty."}

    phrase = db.query(PhraseGroup).filter(PhraseGroup.id == phrase_id).first()
    if not phrase:
        return {"status": "error", "message": "Target practice row record not found."}

    # Update master text
    phrase.master_text = new_master_text

    # Delete existing translations (they'll be regenerated)
    db.query(PhraseTranslation).filter(PhraseTranslation.group_id == phrase_id).delete()

    # Generate new translations using LLM
    cfg = {row.key: row.value for row in db.query(SystemSetting).all()}
    endpoint = cfg.get("llm_endpoint", "http://127.0.0.1:8080").rstrip("/")
    model_name = cfg.get("llm_model", "unsloth/gemma-4-E2B-it-GGUF:Q4_K_XL")

    target_langs = active_languages
    system_prompt = (
        "You are a professional translator. "
        "Translate the given phrase into the specified languages accurately and naturally. "
        "Format your response with each translation on a new line, prefixed with the language code in brackets: [code]: translation"
    )

    user_prompt = f"Translate this phrase into {target_langs}: '{new_master_text}'\n"
    user_prompt += f"Context: {phrase.category} - {phrase.practice_notes}\n"
    user_prompt += f"Format exactly like this:\n"
    for lang in target_langs:
        user_prompt += f"[{lang}]: translated phrase\n"

    try:
        ai_client = AsyncOpenAI(base_url=f"{endpoint}/v1", api_key="local-dev-bypass")
        completion = await ai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=512
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        # Commit the master text update even if translation fails
        db.commit()
        return {"status": "partial", "message": f"Master text updated but translation failed: {str(e)}"}

    # Parse and create translations
    generated_count = 0
    for line in ai_response.split("\n"):
        clean_line = line.strip()
        for lang in target_langs:
            prefix_match = f"[{lang}]:"
            if clean_line.lower().startswith(prefix_match.lower()):
                clean_text = clean_line[len(prefix_match):].strip().replace('"', '')
                if clean_text:
                    new_trans = PhraseTranslation(
                        group_id=phrase.id,
                        language_code=lang,
                        translated_text=clean_text,
                        audio_path=f"audio/{lang}_{phrase.id}.mp3"
                    )
                    db.add(new_trans)
                    db.flush()
                    generate_translation_audio(new_trans, force=True)
                    generated_count += 1

    db.commit()

    return {
        "status": "success",
        "message": f"Master text updated and {generated_count} translations generated with audio.",
        "generated_count": generated_count
    }


@app.get("/api/settings")
async def get_system_settings(db: Session = Depends(get_db)):
    settings_rows = db.query(SystemSetting).all()
    return {row.key: row.value for row in settings_rows}


@app.post("/api/settings/save")
async def save_system_settings(payload: dict, db: Session = Depends(get_db)):
    for key, value in payload.items():
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting:
            setting.value = str(value)
        else:
            db.add(SystemSetting(key=key, value=str(value)))
    db.commit()
    return {"status": "success", "message": "Configuration saved successfully."}


@app.post("/api/settings/fetch-voices")
async def fetch_system_voices(db: Session = Depends(get_db)):
    """
    Fetch available macOS voices using say command and save to database.
    Maps locale suffixes to language codes.  
    """
    try:
        # Run say command to list all voices
        result = subprocess.run(
            ["say", "-v", "?"],
            capture_output=True,
            text=True,
            check=True
        )
            
        # Map locale to language code
        lang_mapping = {
        'us': 'en',
        'gb': 'en',
        'fr': 'fr',
        'es': 'es',
        'it': 'it',
        'no': 'no',
        'ar': 'ar',
        'ru': 'ru',
        'ua': 'ua'
        }

        # Regex Breakdown:
        # ^\s*          -> Match any leading whitespace
        # ([A-Za-z0-9\-]+) -> Capture group 1: The voice name (letters, numbers, hyphens)
        # \s+           -> Match the spaces between the name and the locale
        # ([a-z]{2}_[A-Z]{2}) -> Capture group 2: The locale string (e.g., en_US, it_IT, ru_RU)
        # ru was not matched say returns > Milena (Russian (Russia)) ru_RU    # Здравствуйте! Меня зовут Милена.
        # ar was not matched say returns > Majed               ar_001   # مرحبًا! اسمي ماجد.
        # es was not captured say returns > Rocko (Spanish (Spain)) es_ES    # ¡Hola! Me llamo Rocko. Sandy (Spanish (Spain)) es_ES    # ¡Hola! Me llamo Sandy.
        # voice_pattern = re.compile(r"^\s*([A-Za-z0-9\-]+)\s+([a-z]{2}_[A-Z]{2})") #partially working
        # voice_pattern = re.compile(r"^\s*([A-Za-z0-9\-]+)\s+([a-z]{2}_[A-Z]{2})\s+#") # caputred 5 out of 8 voices: missing ru, ar, es "voices":{"en":"Albert","fr":"Jacques","ua":"Lesya","es":"Montse","no":"Nora"}}

        # voice_pattern = re.compile(r"^\s*([A-Za-z0-9\-]+)\s+([a-z]{2}_[A-Z]{2})\s+\(.*?\) #")
        
        # Updated regex pattern with Unicode flag
        voice_pattern = re.compile(r"^\s*([A-Za-z0-9\-]+)\s+([^#]*)\s*((?:[a-z]{2}_[A-Z]{2})|(?:[a-z]{2}))\s*")

        voices = {}
        for line in result.stdout.split('\n'):
            match = voice_pattern.match(line)
            if match:
                voice_name = match.group(1)      # e.g., "Alice"
                full_locale = match.group(3)     # e.g., "it_IT"
            
            # Extract the country suffix (e.g., "it" from "it_IT")
            country_suffix = full_locale.split('_')[-1].lower() 
            
            if country_suffix in lang_mapping:
                target_lang = lang_mapping[country_suffix]
                # Keep the first high-quality match found for this language
                if target_lang not in voices:
                    voices[target_lang] = voice_name
                    

        # Save to database
        saved_count = 0
        db.flush()
        for lang, voice_name in voices.items():
            setting_key = f"voice_{lang}"
            setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
            if setting:
                setting.value = voice_name
            else:
                db.add(SystemSetting(key=setting_key, value=voice_name))
            saved_count += 1

        db.commit()

        # actual return {"status":"success","message":"Successfully fetched and saved 5 voice settings.","voices":{"en":"Albert","fr":"Jacques","ua":"Lesya","es":"Montse","no":"Nora"}}
        return {
            "status": "success",
            "message": f"Successfully fetched and saved {saved_count} voice settings.",
            "voices": voices
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch voices: {str(e)}"}

## ─── UPGRADED SETTINGS CONNECTIVITY TEST VIA REFACTORED OPENAI ENGINE ───
@app.post("/api/settings/test-llm")
async def test_local_llm_connection(payload: dict, db: Session = Depends(get_db)):
    """
    Validates loopback connectivity using the standardized library wrapper.
    Harvests all models and pushes them back directly into our frontend views.
    """
    endpoint = payload.get("endpoint", "http://127.0.0.1:8080").rstrip("/")
    try:
        # Utilize a clean temporary client container instance
        test_client = AsyncOpenAI(base_url=f"{endpoint}/v1", api_key="local-dev-bypass")
        # Fetch available models through the client layer directly
        models_data = await test_client.models.list()
        # Build out our target ID list array
        model_list = [m.id for m in models_data.data]

        return {
            "status": "connected",
            "message": f"Online! Discovered {len(model_list)} local models.",
            "models": model_list
        }

    except Exception as e:
        return {"status": "failed", "message": f"Unreachable endpoint link! Ensure your server is active. Error: {str(e)}"}

@app.post("/api/phrases/add")
async def add_single_phrase(payload: dict, db: Session = Depends(get_db)):
    master_text = payload.get("master_text", "").strip()
    category = payload.get("category", "General").strip()
    practice_notes = payload.get("practice_notes", "").strip()
    translations_dict = payload.get("translations", {})
    if not master_text:
        return {"status": "error", "message": "Master phrase cannot be empty."}
    
    new_group = PhraseGroup(
        master_text=master_text,
        category=category,
        play_count=0,
        score=0,
        practice_notes=practice_notes
    )

    db.add(new_group)
    db.flush()

    for lang, text in translations_dict.items():
        if text.strip():
            db.add(PhraseTranslation(
                group_id=new_group.id,
                language_code=lang,
                translated_text=text.strip(),
                audio_path=f"audio/{lang}_{new_group.id}.mp3"
            ))
    db.commit()
    return {"status": "success", "message": f"Phrase #{new_group.id} created successfully."}

@app.delete("/api/phrases/{phrase_id}")
async def delete_phrase_group(phrase_id: int, db: Session = Depends(get_db)):
    phrase = db.query(PhraseGroup).filter(PhraseGroup.id == phrase_id).first()

    if not phrase:
        return {"status": "error", "message": "Record not found."}
    db.delete(phrase)
    db.commit()
    return {"status": "success", "message": f"Phrase #{phrase_id} removed cleanly."}

@app.post("/api/phrases/import-csv")
async def import_phrases_from_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded_content = content.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    csv_file = io.StringIO(decoded_content)
    reader = csv.DictReader(csv_file, skipinitialspace=True)
    imported_count = 0

    for row in reader:
        clean_row = {k.strip(): v.strip() if v else "" for k, v in row.items() if k}
        m_text = clean_row.get("master_text", "")
        if not m_text:
            continue

        group = PhraseGroup(
            master_text=m_text,
            category=clean_row.get("category", "Imported"),
            play_count=0,
            score=0,
            practice_notes=clean_row.get("notes", "")
        )

        db.add(group)
        db.flush()

        for lang in ["fr", "ru", "it"]:
            trans_text = clean_row.get(f"{lang}text", "")
            if trans_text:
                db.add(PhraseTranslation(
                    group_id=group.id,
                    language_code=lang,
                    translated_text=trans_text,
                    audio_path=f"audio/{lang}{group.id}.mp3"
                ))
            imported_count += 1
    db.commit()
    return {"status": "success", "message": f"Successfully parsed and imported {imported_count} phrases."}
