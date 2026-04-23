# 🧠 Convoq — Context-Aware Messaging Assistant (Windows) — PRD

---

## 1. 📌 Overview

### Product Name

**Convoq**

### Tagline

*Smarter replies. Better tone. Zero effort.*

### Description

Convoq is a Windows-based AI assistant that enhances real-time messaging by:

* Automatically extracting conversation context
* Refining user-written messages
* Applying tone intelligently
* Delivering ultra-fast responses via streaming AI

It integrates seamlessly with apps like WhatsApp Desktop without requiring copy-paste.

---

## 2. 🎯 Objectives

* Eliminate grammar mistakes in chat communication
* Enable context-aware, human-like responses
* Provide real-time refinement with minimal friction
* Deliver sub-second AI response using streaming

---

## 3. 👤 Target Users

* Developers and professionals
* Non-native English speakers
* Frequent chat users (WhatsApp, Slack, Teams)
* Anyone who values fast, polished communication

---

## 4. 🚀 Core Features

---

### 4.1 🎹 Hotkey-Based Interaction

Single hotkey opens a tone picker popup:

| Hotkey   | Action                        |
| -------- | ----------------------------- |
| Ctrl + R | Open tone picker, then refine |

Tone picker (appears near cursor, click or press key):

| Key | Tone         |
| --- | ------------ |
| 1   | Casual       |
| 2   | Professional |
| 3   | Friendly     |
| 4   | Direct       |
| 5   | Apologetic   |

---

### 4.2 🧠 Context-Aware Message Refinement

* Automatically extracts last 3–5 messages
* Detects:

  * Reply vs new message
* Ensures contextual coherence

---

### 4.3 🎛️ Tone Engine

Supported tones:

* Casual
* Professional
* Friendly
* Direct
* Apologetic

Future:

* Adaptive tone (auto-detect from conversation)

---

### 4.4 ⚡ Streaming AI Response (Core Differentiator)

Powered by Groq

* Token-by-token streaming response
* Ultra-low latency (~sub-second perceived speed)
* Enables real-time UI feedback

---

### 4.5 🔄 Automatic Text Replacement

* Captures input field
* Replaces text instantly
* Maintains cursor focus
* No manual copy-paste required

---

### 4.6 ⏳ Loading & Streaming UI Overlay

* Lightweight PyQt overlay near cursor
* Displays:

  * “Refining…” state
  * Optional live streaming text
* Non-blocking and disappears automatically

---

### 4.7 🧩 Background System Tray App

* Runs silently in background
* Tray features:

  * Enable/Disable Convoq
  * Exit application
  * Future: tone presets

---

## 5. 🧠 Functional Flow

1. User types message in WhatsApp
2. Presses hotkey (e.g., Ctrl + 2)
3. Convoq:

   * Extracts context (last messages)
   * Captures draft input
4. Displays loader overlay
5. Sends request to Groq (streaming mode)
6. Streams response (optional UI preview)
7. Replaces input text with refined output
8. Overlay disappears

---

## 6. 🏗️ Technical Architecture

---

### 6.1 Desktop Layer (Python)

| Component          | Tech      |
| ------------------ | --------- |
| UI                 | PyQt6     |
| Hotkeys            | pynput    |
| Context Extraction | pywinauto |
| Input Automation   | pyautogui |
| Clipboard          | pyperclip |
| Background Tray    | pystray   |

---

### 6.2 AI Layer

* Provider: Groq
* Model: `llama-3.1-8b-instant`
* Mode: Streaming (`stream=True`)

---

### 6.3 Architecture Diagram

```
User Input
   ↓
Hotkey Trigger
   ↓
Context Extractor (pywinauto)
   ↓
Input Capture
   ↓
AI Client (Groq Streaming)
   ↓
Streaming Response
   ↓
Text Replacement
   ↓
Overlay UI Feedback
```

---

## 7. 🧩 Core Components

---

### 7.1 Hotkey Manager

* Global listener using pynput
* Maps tone to processing pipeline

---

### 7.2 Context Extractor

* Connects to WhatsApp UI
* Extracts visible chat messages
* Filters last 3–5 relevant messages

---

### 7.3 Streaming AI Client

* Sends structured prompt
* Receives token stream
* Builds final output incrementally

---

### 7.4 Text Replacer

* Uses clipboard injection
* Ensures seamless overwrite

---

### 7.5 Loader & Streaming UI

* PyQt overlay window
* Shows:

  * Loading state
  * Optional live output

---

### 7.6 System Tray Manager

* Background lifecycle control
* Minimal user interaction

---

## 8. 🧪 Prompt Design

```
You are an AI message assistant.

INPUT:
- Previous conversation (last messages)
- Draft message
- Tone

TASK:
1. Determine if the message is a reply or new
2. Rewrite with:
   - Correct grammar
   - Context awareness
   - Tone applied properly

RULES:
- Keep it natural
- Keep it concise
- Do not over-formalize

OUTPUT:
Return only the refined message.
```

---

## 9. ⚡ Streaming Behavior Design

### Mode 1 (MVP)

* Show loader
* Wait for full response
* Replace text

---

### Mode 2 (Advanced)

* Display streaming text in overlay
* Replace text after completion

---

### Future Mode

* Real-time typing replacement (progressive insertion)

---

## 10. ⚠️ Constraints & Risks

---

### Technical Risks

* WhatsApp UI changes → break selectors
* OCR fallback may be inaccurate
* Clipboard timing issues

---

### Platform Limitations

* No official WhatsApp API access
* Must rely on UI automation

---

## 11. 📈 Success Metrics

* Response latency < 1 second (perceived)
* ≥ 90% grammar improvement accuracy
* ≤ 1 user action (hotkey) per refinement
* Minimal UI disruption

---

## 12. 🛣️ Roadmap

---

### Phase 1 (MVP)

* Hotkeys
* Tone refinement
* Text replacement
* Groq streaming integration

---

### Phase 2

* Context extraction
* Loader UI

---

### Phase 3

* System tray app
* Stability improvements

---

### Phase 4 (Advanced)

* Adaptive tone detection
* Multi-language support
* Context compression

---

## 13. 🔐 Privacy & Security

* No message storage
* No conversation logging
* API calls only for active refinement
* Future: local model support

---

## 14. 📦 Deployment

* Packaged via PyInstaller
* Runs as Windows background app
* Optional auto-start on boot

---

## 15. 💡 Future Enhancements

* Cross-platform (Mac support)
* Slack / Teams integration
* Voice-to-text refinement
* Smart reply suggestions
* Personalized tone learning

---

## 16. 📋 Recommendations

1. **Build an app adapter interface** early so adding Slack/Teams isn't a rewrite
2. **Add a "passthrough" threshold** — don't refine messages under N characters or that are already clean
3. **Move system tray and error handling to Phase 1** — these are table stakes for a background app
4. **Define a fallback chain**: pywinauto → accessibility API → OCR → graceful failure with notification
5. **Add hotkey for undo** — let users revert to their original text instantly
6. **Consider `win32clipboard` with locking** instead of pyperclip for more reliable clipboard ops

---

## 17. 🧠 Key Insight

Convoq is not just a grammar tool.

👉 It is a **real-time communication intelligence layer**
that understands context, tone, and intent—instantly.

---
