# language_practice/scripts/populate_db.py
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from language_practice.src.database import SessionLocal, init_db
from language_practice.src.models import PhraseGroup, PhraseTranslation

def seed_bazaar_data():
    """
    Populates relational tables using a clean, synchronized, error-free 
    naming convention for localized audio tracking cells.
    """
    init_db()
    db = SessionLocal()
    
    try:
        if db.query(PhraseGroup).count() > 0:
            print("Database already contains data rows. Seeding sequence aborted.")
            return

        print("--- Initiating Bug-Free Relational Database Seeding Loop ---")

        # --- DATA RECORD 1: WELCOMING GREETINGS ---
        g1_text = "Hello! Welcome to my shop. How can I help you today, my friend?"
        group_1 = PhraseGroup(
            master_text=g1_text,
            category="El Kawther Bazaar",
            play_count=0,
            score=0,
            practice_notes="Standard warm greeting for customers walking past your bazaar stall."
        )
        db.add(group_1)
        db.flush()  # Extract the group_1.id anchor baseline instantly from SQLite

        t1_fr = "Bonjour ! Bienvenue dans ma boutique. Comment puis-je vous aider aujourd'hui, mon ami ?"
        t1_ru = "Здравствуйте! Добро пожаловать в мой магазин. Как я могу помочь вам сегодня, мой друг?"
        t1_it = "Ciao! Benvenuto nel mio negozio. Come posso aiutarti oggi, amico mio?"

        db.add_all([
            PhraseTranslation(group_id=group_1.id, language_code="fr", translated_text=t1_fr, voice_gender="Female", voice_accent="Standard", audio_path=f"audio/fr_{group_1.id}.mp3"),
            PhraseTranslation(group_id=group_1.id, language_code="ru", translated_text=t1_ru, voice_gender="Male", voice_accent="Standard", audio_path=f"audio/ru_{group_1.id}.mp3"),
            PhraseTranslation(group_id=group_1.id, language_code="it", translated_text=t1_it, voice_gender="Female", voice_accent="Standard", audio_path=f"audio/it_{group_1.id}.mp3")
        ])

        # --- DATA RECORD 2: PREMIUM EGYPTIAN COTTON ---
        g2_text = "This is handmade Egyptian cotton, absolute premium quality. Touch it, it is soft."
        group_2 = PhraseGroup(
            master_text=g2_text,
            category="El Kawther Bazaar",
            play_count=0,
            score=0,
            practice_notes="Product highlight phrase. Emphasize the tactile quality of the cotton fabric."
        )
        db.add(group_2)
        db.flush()  # Extract group_2.id baseline anchor dynamically

        t2_fr = "C'est du coton égyptien fait à la main, d'une qualité absolue. Touchez-le, c'est très doux."
        t2_ru = "Это египетский хлопок ручной работы, абсолютное премиальное качество. Потрогайте, он очень мягкий."
        t2_it = "Questo è cotone egiziano fatto a mano, qualità premium assoluta. Toccalo, è morbidissimo."

        db.add_all([
            PhraseTranslation(group_id=group_2.id, language_code="fr", translated_text=t2_fr, voice_gender="Female", voice_accent="Standard", audio_path=f"audio/fr_{group_2.id}.mp3"),
            PhraseTranslation(group_id=group_2.id, language_code="ru", translated_text=t2_ru, voice_gender="Male", voice_accent="Standard", audio_path=f"audio/ru_{group_2.id}.mp3"),
            PhraseTranslation(group_id=group_2.id, language_code="it", translated_text=t2_it, voice_gender="Female", voice_accent="Standard", audio_path=f"audio/it_{group_2.id}.mp3")
        ])

        db.commit()
        print("\n--- Seeding Successfully Completed! Audio path keys are locked to group parents. ---")

    except Exception as e:
        db.rollback()
        print(f"Critical error during database seeding: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_bazaar_data()
