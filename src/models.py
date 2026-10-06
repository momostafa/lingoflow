# language_practice/src/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class PhraseGroup(Base):
    """
    Acts as the 'Master Row' Anchor.
    Tracks core meaning, custom user notes, and personal mastery statistics.
    """
    __tablename__ = "phrase_groups"

    id = Column(Integer, primary_key=True, index=True)
    master_text = Column(String, nullable=False)  # Anchor phrase (English)
    category = Column(String, index=True, default="General")
    
    # --- Practice Tracker Properties ---
    play_count = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)  # Integer bounded 0 - 10
    mastery_status = Column(String, default="Not practiced", nullable=False)  # "Not practiced", "Learning", "Mastered"
    practice_notes = Column(String, nullable=True)  # Dynamic space for synonyms / custom notes
    
    created_at = Column(DateTime, server_default=func.now())

    # Relational mapping to individual translation target cells
    translations = relationship(
        "PhraseTranslation", 
        back_populates="group", 
        cascade="all, delete-orphan",
        lazy="joined"
    )

class PhraseTranslation(Base):
    """
    Stores individual language translations tied back to the Master Concept Group.
    Tracks distinct accent attributes and voice properties for high-fidelity practice.
    """
    __tablename__ = "phrase_translations"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("phrase_groups.id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(5), nullable=False, index=True)  # 'fr', 'ru', 'it', etc.
    translated_text = Column(String, nullable=False)
    audio_path = Column(String, nullable=True)  # Safe cached disk audio tracker file
    
    # --- High Fidelity Voice Variant Properties ---
    voice_gender = Column(String(10), default="Female", nullable=False)  # "Male" or "Female"
    voice_accent = Column(String(30), default="Standard", nullable=False)  # "Standard", "Parisian", etc.

    group = relationship("PhraseGroup", back_populates="translations")

# 🌟 ENFORCE FIX: Ensure this class is declared down at the very bottom line!
class SystemSetting(Base):
    """
    Persists local configuration parameters, voice mappings, and local LLM endpoints.
    Allows the app to remain flexible without hardcoded configuration scripts.
    """
    __tablename__ = "system_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
