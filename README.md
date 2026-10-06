# 🌊 LingoFlow

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)

**A high-performance, self-contained local language acquisition matrix and interactive AI copilot pipeline**

LingoFlow enables conversational rehearsal, automated local voice track generation, and dynamic, context-aware linguistic advice powered completely by open-weight LLMs running locally on your hardware.

[⭐ Star this repo](https://github.com/yourusername/lingoflow) • [🐛 Report Issue](https://github.com/yourusername/lingoflow/issues) • [📖 Documentation](https://github.com/yourusername/lingoflow/wiki)

</div>

---

## ✨ Features

- **🎛️ Unified Practice Matrix** - Compare phrase translations across multiple target languages simultaneously in an intuitive grid layout
- **🔊 Self-Compiling Audio Ecosystem** - Automatically generates MP3 audio files using macOS native TTS when assets are missing
- **⚡ Interactive AI Copilot** - Context-aware AI assistant providing linguistic tips, phrase variations, and translation assistance
- **🤖 Local LLM Integration** - Powered by local models (llama-server or LM Studio) with full privacy and zero API costs
- **📈 Performance Tracking** - Dynamic mastery badges (Needs Practice, Learning, Mastered) based on self-scoring
- **📥 Bulk CSV Import** - Easily import vocabulary spreadsheets with automatic translation and audio generation
- **🎚️ Multi-Language Support** - Supports 8 languages: English, French, Russian, Ukrainian, Italian, Spanish, Norwegian, Arabic
- **⚙️ Dynamic Voice Selection** - Automatically fetches and uses available macOS voices for each language

---

## 🏗️ Architecture

```text
  [ Web Browser UI ]
           │
           ▼ (HTTP/JSON)
  [ FastAPI Backend ]
   ├── SQLAlchemy / SQLite
   ├── macOS TTS Audio Engine
   └── OpenAI SDK (Local LLM)
           │
           ▼ (Local Port)
  [ llama-server ] or [ LM Studio ]
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- macOS (for native TTS audio generation)
- Local LLM backend (llama-server or LM Studio)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/lingoflow.git
cd lingoflow
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start your local LLM backend**

**Using llama-server:**
```bash
llama-server -m /path/to/your/model.gguf -c 4096 --host 127.0.0.1 --port 8080 -np 1
```

**Using LM Studio:**
1. Open LM Studio
2. Select your model and start the server
3. Note the port (default: 1234)

4. **Configure the application**
- Open `http://127.0.0.1:8000/practice`
- Go to ⚙️ Settings Panel
- Set your LLM endpoint and model name
- Click "Fetch Available Voices" to auto-configure TTS voices

5. **Run the application**
```bash
uvicorn src.main:app --reload
```

6. **Open your browser**
Navigate to `http://127.0.0.1:8000`

---

## � Usage

### Adding Phrases

1. Go to 📝 Phrase Management tab
2. Fill in the master phrase, category, and translations
3. Click "➕ Save Phrase Row"

### Bulk Import

Prepare a CSV file with the following format:
```csv
master_text,category,notes,fr_text,ru_text,it_text,es_text
"How much does this cost?","Bargaining","Target high margins","C'est combien?","Сколько это стоит?","Quanto costa?","¿Cuánto cuesta?"
```

Import it via the Phrase Management tab.

### Using the AI Copilot

1. Click "⚡ Ask AI" on any phrase
2. Interact with the AI assistant:
   - Ask for phrase variations (more formal, casual, complex)
   - Request grammar explanations
   - Get contextual usage tips
3. If AI proposes changes, click "✓ Yes, Update" to apply them

### Audio Playback

- Click "🔊 Play" on any translation to hear the native pronunciation
- Use the speed slider in the control panel to adjust playback rate (0.5x - 2.0x)

---

## 🛠️ Development

### Project Structure

```
lingoflow/
├── src/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── crud.py              # Database operations
│   ├── audio_engine.py      # TTS audio generation
│   └── config.py            # Configuration
├── templates/
│   ├── base.html            # Base template
│   └── index.html           # Main application UI
├── static/
│   ├── css/                 # Stylesheets
│   └── audio/               # Generated audio files
├── data/
│   └── practice.db          # SQLite database
├── scripts/
│   └── populate_db.py       # Database initialization
└── requirements.txt         # Python dependencies
```

### Running Tests

```bash
pytest
```

### Code Style

This project follows PEP 8 guidelines. Consider using:
```bash
black src/
isort src/
flake8 src/
```

---

## � Configuration

### LLM Settings

- **Endpoint**: Your local LLM server URL (e.g., `http://127.0.0.1:8080`)
- **Model**: The model name as configured in your LLM server
- **Persona**: Choose between "Bazaar Negotiator" or "Linguistic Tutor"

### Voice Settings

The application automatically fetches available macOS voices. Supported language codes:
- `en` - English
- `fr` - French
- `ru` - Russian
- `ua` - Ukrainian
- `it` - Italian
- `es` - Spanish
- `no` - Norwegian
- `ar` - Arabic

---

## 🗺️ Future Roadmap

Planned features and enhancements for upcoming releases:

### Short-Term Goals

- **🎯 Topic-Based Phrase Generation**
  - Ask AI to generate sets of phrases/translations by specific topics
  - Example: "Generate 5 short sales lines related to Egyptian Papyrus"
  - Category-based organization and bulk import

- **🌐 Cross-Platform TTS Support**
  - Add voice engine compatibility for Windows (using SAPI or Microsoft Speech Platform)
  - Add voice engine compatibility for Linux (using eSpeak-ng, Festival, or Mozilla TTS)
  - Unified audio generation API with platform detection

### Medium-Term Goals

- **📊 Advanced Analytics Dashboard**
  - Learning progress visualization with charts
  - Session tracking and study time metrics
  - Weakness identification and targeted practice recommendations

- **🎮 Gamification Features**
  - Achievement badges and milestones
  - Daily streak tracking
  - Spaced repetition scheduling

- **📚 Content Library**
  - Pre-built phrase packs for common scenarios (travel, business, medical)
  - Community-shared phrase collections
  - Import/export of custom phrase libraries

### Long-Term Goals

- **🤖 Enhanced AI Capabilities**
  - Context-aware conversation practice mode
  - Grammar error detection and correction
  - Pronunciation analysis using audio input

- **🔗 Multi-Device Sync**
  - Cloud synchronization (self-hosted options)
  - Mobile app companion
  - Offline-first architecture with online backup

- **🌍 Extended Language Support**
  - Add more languages (German, Japanese, Chinese, etc.)
  - Regional dialect support
  - Custom language pack loading

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI integration via [OpenAI Python SDK](https://github.com/openai/openai-python)
- Local inference powered by [llama.cpp](https://github.com/ggerganov/llama.cpp)
- Database management with [SQLAlchemy](https://www.sqlalchemy.org/)
