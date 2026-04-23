# Convoq

**Smarter replies. Better tone. Zero effort.**

Convoq is a Windows desktop AI assistant that refines your chat messages in real-time. Type your message in WhatsApp, press `Ctrl+R`, pick a tone, and your message is instantly rewritten with proper grammar, context, and tone — no copy-paste needed.

---

## How It Works

```
Type message → Ctrl+R → Pick tone → AI refines → Text replaced
```

1. Type your message in WhatsApp Desktop
2. Press **Ctrl+R** — a tone picker popup appears
3. Click a tone or press **1-6** on your keyboard
4. Convoq reads your draft, sends it to Groq's AI, and replaces your text instantly

---

## Tone Options

| Key | Tone           | Description                                      |
|-----|----------------|--------------------------------------------------|
| 1   | Casual         | Relaxed, like texting a friend                   |
| 2   | Professional   | Polished, business-appropriate                   |
| 3   | Friendly       | Warm and approachable                            |
| 4   | Direct         | Concise, no filler                               |
| 5   | Apologetic     | Sincere, empathetic                              |
| 6   | Tanglish       | Tamil + English mix (WhatsApp style)             |

---

## Setup

### Prerequisites

- Python 3.10+
- Windows 10/11
- [Groq API key](https://console.groq.com/keys)

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/convoq.git
cd convoq

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Or set it as an environment variable:

```bash
set GROQ_API_KEY=your_groq_api_key_here
```

### Run

```bash
python main.py
```

Convoq starts in the background with a system tray icon. Open WhatsApp Desktop, type a message, and press `Ctrl+R`.

---

## Project Structure

```
convoq/
├── main.py                        # Entry point
├── requirements.txt               # Dependencies
├── .env                           # API key (not committed)
├── convoq/
│   ├── config/
│   │   ├── config_manager.py      # Singleton config loader
│   │   └── default_config.yaml    # Default settings
│   ├── core/
│   │   ├── engine.py              # Facade — app entry point
│   │   ├── event_bus.py           # Observer — event system
│   │   ├── pipeline.py            # Refinement orchestrator
│   │   └── undo_manager.py        # Command — undo support
│   ├── adapters/
│   │   ├── base.py                # Abstract AppAdapter
│   │   ├── factory.py             # Factory — adapter creation
│   │   ├── detection.py           # Window detection (Win32)
│   │   └── whatsapp.py            # WhatsApp adapter
│   ├── extractors/
│   │   ├── base.py                # Abstract ContextExtractor
│   │   ├── chain.py               # Chain of Responsibility — fallback
│   │   ├── ui_automation.py       # pywinauto extractor
│   │   └── ocr.py                 # OCR fallback (placeholder)
│   ├── ai/
│   │   ├── base.py                # Abstract Refiner
│   │   ├── groq_refiner.py        # Groq streaming client
│   │   ├── prompt_builder.py      # Builder — prompt construction
│   │   └── tone.py                # Strategy — tone definitions
│   ├── clipboard/
│   │   └── manager.py             # Proxy — safe clipboard ops
│   ├── ui/
│   │   ├── overlay.py             # Status overlay (State pattern)
│   │   ├── states.py              # Overlay state classes
│   │   ├── tone_picker.py         # Tone selection popup
│   │   └── tray.py                # System tray manager
│   ├── hotkeys/
│   │   └── manager.py             # Global hotkey listener
│   └── models/
│       └── context.py             # Data models
├── Convoq-PRD.md                  # Product requirements
└── DESIGN.md                      # Architecture & design doc
```

---

## Architecture

Built with **OOP**, **SOLID principles**, and **11 design patterns**:

| Pattern                  | Where                | Purpose                              |
|--------------------------|----------------------|--------------------------------------|
| Singleton                | ConfigManager        | One config instance                  |
| Factory Method           | AppAdapterFactory    | Create adapter by active window      |
| Builder                  | PromptBuilder        | Step-by-step prompt construction     |
| Adapter                  | WhatsAppAdapter      | Uniform interface over app UIs       |
| Facade                   | ConvoqEngine         | Single entry point for subsystems    |
| Proxy                    | ClipboardManager     | Safe clipboard with locking          |
| Chain of Responsibility  | ExtractionChain      | Extractor fallback chain             |
| Observer                 | EventBus             | Decoupled component communication    |
| Strategy                 | Tone                 | Swappable tone instructions          |
| Command                  | UndoManager          | Reversible refinements               |
| State                    | OverlayUI            | Overlay state machine                |

---

## Tech Stack

| Component          | Technology                |
|--------------------|---------------------------|
| Language           | Python 3.10+              |
| AI Provider        | Groq (llama-3.1-8b-instant) |
| UI Framework       | PyQt6                     |
| Global Hotkeys     | pynput                    |
| UI Automation      | pywinauto                 |
| Clipboard          | pyperclip + Win32 API     |
| Input Simulation   | pyautogui                 |
| System Tray        | pystray + Pillow          |
| Config             | PyYAML                    |
| Env Variables      | python-dotenv             |

---

## Custom Configuration

Create `~/.convoq/config.yaml` to override defaults:

```yaml
ai:
  model: llama-3.1-8b-instant
  max_tokens: 256
  temperature: 0.7

context:
  max_messages: 5
  passthrough_min_chars: 3

overlay:
  fade_timeout_ms: 1500

undo:
  max_history: 10
```

---

## Adding New Apps

Convoq is built with an adapter pattern. To add support for a new messaging app:

1. Create `convoq/adapters/slack.py`
2. Implement the `AppAdapter` abstract class
3. Self-register at the bottom of the file:

```python
AppAdapterFactory.register("slack", SlackAdapter)
```

No existing code needs to change (Open/Closed Principle).

---

## Privacy

- No messages are stored or logged
- API calls only happen when you press Ctrl+R
- All processing is ephemeral
- Your Groq API key stays local in `.env`

---

## Roadmap

- [x] Hotkey-triggered refinement
- [x] Tone selection UI
- [x] Groq streaming integration
- [x] Text replacement via clipboard
- [x] System tray background app
- [x] Tanglish support
- [ ] Context extraction from chat history
- [ ] Undo support (Ctrl+Z)
- [ ] Slack / Teams adapters
- [ ] Adaptive tone detection
- [ ] Multi-language support
- [ ] Local model support (offline mode)

---

## License

MIT
