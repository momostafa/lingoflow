from sqlalchemy.orm import Session
from .models import PhraseGroup, PhraseTranslation

def compute_mastery_badge(score: int, play_count: int) -> str:
    """
    Determines the visual badge designation string state cleanly on the backend.
    """
    if play_count == 0:
        return "Not practiced"
    if score >= 9:
        return "Mastered"
    if score >= 6:
        return "Proficient"
    return "Learning"

def get_unified_practice_matrix(db: Session, languages: list[str] = None, category: str = None, skip: int = 0, limit: int = 10):
    """
    Fetches Master Rows and maps requested target column translations 
    along with tracking scores, play metrics, and practice note buffers.
    """
    query = db.query(PhraseGroup)
    
    if category and category != "all":
        query = query.filter(PhraseGroup.category == category)
        
    total_records = query.count()
    groups = query.offset(skip).limit(limit).all()
    
    matrix_response = []
    for group in groups:
        row = {
            "id": group.id,
            "master_phrase": group.master_text,
            "category": group.category,
            
            # --- Personal Analytics Buffers ---
            "play_count": group.play_count,
            "score": group.score,
            "mastery_badge": compute_mastery_badge(group.score, group.play_count),
            "practice_notes": group.practice_notes or "",
            
            "translations": {}
        }
        
        for t in group.translations:
            if languages and t.language_code not in languages:
                continue
            row["translations"][t.language_code] = {
                "translation_id": t.id,
                "text": t.translated_text,
                "audio_path": t.audio_path
            }
            
        matrix_response.append(row)
        
    return {
        "total": total_records,
        "data": matrix_response
    }

def update_phrase_tracking(db: Session, group_id: int, score: int = None, play_count_increment: bool = False, notes: str = None):
    """
    Updates the tracking metrics or custom notes of a master phrase.
    """
    group = db.query(PhraseGroup).filter(PhraseGroup.id == group_id).first()
    if not group:
        return None
        
    if play_count_increment:
        group.play_count += 1
    if score is not None:
        group.score = max(0, min(10, score))  # Safe bounds constraint (0-10)
    if notes is not None:
        group.practice_notes = notes
        
    db.commit()
    db.refresh(group)
    return group
