# Convoq — System Design Document

---

## 1. Design Philosophy

Every class, interface, and module in Convoq follows three pillars:

- **OOP Pillars**: Encapsulation, Inheritance, Abstraction, Polymorphism
- **SOLID Principles**: SRP, OCP, LSP, ISP, DIP
- **Design Patterns**: Applied where they solve real problems, not for ceremony

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Convoq App                         │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Hotkey   │  │  App Adapter │  │  AI Engine        │  │
│  │ Manager  │→ │  (Context +  │→ │  (Groq/Streaming) │  │
│  │          │  │   Replace)   │  │                   │  │
│  └──────────┘  └──────────────┘  └───────────────────┘  │
│       ↑              ↑                    ↓              │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Config   │  │  Clipboard   │  │  Overlay UI       │  │
│  │ Manager  │  │  Manager     │  │  (PyQt6)          │  │
│  └──────────┘  └──────────────┘  └───────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              System Tray Manager                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 3. OOP Pillars — Applied

### 3.1 Encapsulation

Each component hides its internal state and exposes only what's necessary.

| Component | Hidden Internals | Public Interface |
|-----------|-----------------|------------------|
| ClipboardManager | Lock state, backup buffer | `copy()`, `paste()`, `backup()`, `restore()` |
| AIClient | API key, connection, token buffer | `refine(prompt) → AsyncIterator[str]` |
| ContextExtractor | UI tree traversal, selectors | `extract() → ConversationContext` |
| HotkeyManager | Listener thread, key state | `register(combo, callback)`, `start()`, `stop()` |

### 3.2 Inheritance

Used sparingly and only where "is-a" relationships genuinely exist:

```
AppAdapter (ABC)
  ├── WhatsAppAdapter
  ├── SlackAdapter        (future)
  └── TeamsAdapter        (future)

ContextExtractor (ABC)
  ├── UIAutomationExtractor   (pywinauto)
  ├── AccessibilityExtractor  (future)
  └── OCRExtractor            (future fallback)
```

### 3.3 Abstraction

Users of each subsystem interact through abstract interfaces, never concrete implementations:

- `Refiner` — the pipeline doesn't know if AI is Groq, OpenAI, or local
- `AppAdapter` — the pipeline doesn't know if the target is WhatsApp or Slack
- `ContextExtractor` — the pipeline doesn't know if context comes from UI automation or OCR

### 3.4 Polymorphism

The refinement pipeline treats all adapters and extractors identically:

```python
def handle_hotkey(tone: Tone, adapter: AppAdapter, refiner: Refiner):
    context = adapter.extract_context()      # polymorphic — any app
    draft = adapter.get_draft()              # polymorphic — any app
    refined = refiner.refine(draft, context, tone)  # polymorphic — any AI
    adapter.replace_text(refined)            # polymorphic — any app
```

---

## 4. SOLID Principles — Applied

### 4.1 Single Responsibility Principle (SRP)

Every class has exactly one reason to change:

| Class | Single Responsibility |
|-------|----------------------|
| `HotkeyManager` | Listening for and dispatching global hotkeys |
| `ContextExtractor` | Extracting conversation history from a UI |
| `ClipboardManager` | Safe clipboard read/write with locking |
| `AIClient` | Communicating with the AI provider |
| `PromptBuilder` | Constructing the refinement prompt |
| `TextReplacer` | Injecting refined text back into the target app |
| `OverlayUI` | Displaying loading/streaming feedback |
| `TrayManager` | System tray lifecycle and menu |
| `ConfigManager` | Loading, validating, and persisting settings |
| `RefinementPipeline` | Orchestrating the full refine flow |

### 4.2 Open/Closed Principle (OCP)

The system is open for extension, closed for modification:

- **New app?** → Implement `AppAdapter`. No existing code changes.
- **New tone?** → Add to `Tone` enum. Prompt template handles it automatically.
- **New AI provider?** → Implement `Refiner`. Pipeline doesn't change.
- **New extraction method?** → Implement `ContextExtractor`. Fallback chain picks it up.

### 4.3 Liskov Substitution Principle (LSP)

Any subclass can replace its parent without breaking behavior:

- `WhatsAppAdapter` can be swapped with `SlackAdapter` — the pipeline works identically
- `UIAutomationExtractor` can be swapped with `OCRExtractor` — same `extract()` contract
- `GroqRefiner` can be swapped with `LocalModelRefiner` — same streaming interface

### 4.4 Interface Segregation Principle (ISP)

Clients depend only on the interfaces they use. No fat interfaces:

```python
class ContextExtractable(Protocol):
    """Only for components that need to read context"""
    def extract_context(self) -> ConversationContext: ...

class TextReplaceable(Protocol):
    """Only for components that need to write text back"""
    def get_draft(self) -> str: ...
    def replace_text(self, text: str) -> None: ...

class Refinable(Protocol):
    """Only for components that need AI refinement"""
    def refine(self, draft: str, context: ConversationContext, tone: Tone) -> AsyncIterator[str]: ...
```

`AppAdapter` composes `ContextExtractable + TextReplaceable` — but a component that only needs context extraction depends only on `ContextExtractable`.

### 4.5 Dependency Inversion Principle (DIP)

High-level modules depend on abstractions, not concretions:

```
RefinementPipeline
    depends on → AppAdapter (abstract)      NOT WhatsAppAdapter
    depends on → Refiner (abstract)         NOT GroqRefiner
    depends on → ContextExtractor (abstract) NOT UIAutomationExtractor
    depends on → ClipboardPort (abstract)    NOT Win32Clipboard
```

All concrete implementations are injected via the DI container at startup.

---

## 5. Design Patterns — Applied

### 5.1 Creational Patterns

#### Factory Method — `AppAdapterFactory`

Creates the correct adapter based on the active foreground window:

```python
class AppAdapterFactory:
    _registry: dict[str, type[AppAdapter]] = {}

    @classmethod
    def register(cls, app_name: str, adapter_cls: type[AppAdapter]):
        cls._registry[app_name] = adapter_cls

    @classmethod
    def create(cls, window_title: str) -> AppAdapter:
        for app_name, adapter_cls in cls._registry.items():
            if app_name.lower() in window_title.lower():
                return adapter_cls()
        raise UnsupportedAppError(window_title)
```

**Why**: New apps register themselves without modifying factory code (OCP).

#### Singleton — `ConfigManager`

One global config instance, loaded once:

```python
class ConfigManager:
    _instance: ConfigManager | None = None

    def __new__(cls) -> ConfigManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
```

**Why**: Config must be consistent across all components. Thread-safe lazy init.

#### Builder — `PromptBuilder`

Constructs complex prompts step by step:

```python
prompt = (
    PromptBuilder()
    .with_system_instructions()
    .with_context(conversation_context)
    .with_draft(user_draft)
    .with_tone(tone)
    .with_constraints()
    .build()
)
```

**Why**: Prompt structure varies by context (reply vs new, short vs long, group vs 1-on-1). Builder keeps construction logic readable and extensible.

---

### 5.2 Structural Patterns

#### Adapter — `AppAdapter` hierarchy

Wraps each messaging app's unique UI automation behind a uniform interface:

```python
class WhatsAppAdapter(AppAdapter):
    """Adapts WhatsApp Desktop's UI tree to our AppAdapter interface"""

    def extract_context(self) -> ConversationContext:
        # pywinauto-specific WhatsApp selectors
        ...

    def get_draft(self) -> str:
        # WhatsApp input box specific logic
        ...

    def replace_text(self, text: str) -> None:
        # WhatsApp-specific text injection
        ...
```

**Why**: Each app has radically different UI internals. Adapter isolates that complexity.

#### Facade — `ConvoqEngine`

Single entry point that hides the entire subsystem:

```python
class ConvoqEngine:
    """Facade — the only class the tray/UI layer touches"""

    def __init__(self, config: ConfigManager):
        self._pipeline = RefinementPipeline(...)
        self._hotkeys = HotkeyManager(...)
        self._tray = TrayManager(...)
        self._overlay = OverlayUI(...)

    def start(self):
        self._hotkeys.start()
        self._tray.start()

    def stop(self):
        self._hotkeys.stop()
        self._tray.stop()
```

**Why**: `main.py` calls `ConvoqEngine.start()` — it doesn't need to know about 10 subsystems.

#### Proxy — `ClipboardManager`

Controls access to the system clipboard with locking and backup:

```python
class ClipboardManager:
    """Proxy around raw clipboard — adds locking, backup/restore"""

    def __init__(self):
        self._lock = threading.Lock()
        self._backup: str | None = None

    def safe_paste(self, text: str) -> None:
        with self._lock:
            self._backup = self._read_raw()
            self._write_raw(text)
            self._simulate_paste()
            time.sleep(0.05)
            self._restore_backup()
```

**Why**: Raw clipboard access has race conditions. Proxy adds safety without changing the interface.

---

### 5.3 Behavioral Patterns

#### Chain of Responsibility — `ExtractionChain`

Fallback chain for context extraction:

```python
class ExtractionChain:
    def __init__(self, extractors: list[ContextExtractor]):
        self._extractors = extractors  # ordered by priority

    def extract(self, window) -> ConversationContext:
        for extractor in self._extractors:
            try:
                result = extractor.extract(window)
                if result.is_valid():
                    return result
            except ExtractionError:
                continue
        return ConversationContext.empty()
```

Chain order: `UIAutomationExtractor → AccessibilityExtractor → OCRExtractor → empty fallback`

**Why**: PRD recommendation #4 — graceful degradation through a fallback chain.

#### Observer — `EventBus`

Decouples components via events:

```python
class EventBus:
    _listeners: dict[str, list[Callable]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event: str, callback: Callable):
        cls._listeners[event].append(callback)

    @classmethod
    def emit(cls, event: str, data: Any = None):
        for callback in cls._listeners[event]:
            callback(data)
```

Events:
| Event | Emitted By | Consumed By |
|-------|-----------|-------------|
| `hotkey.triggered` | HotkeyManager | RefinementPipeline |
| `refinement.started` | RefinementPipeline | OverlayUI |
| `refinement.token` | AIClient | OverlayUI (streaming) |
| `refinement.completed` | RefinementPipeline | OverlayUI, TextReplacer |
| `refinement.failed` | RefinementPipeline | OverlayUI (error state) |
| `app.detected` | AppDetector | AppAdapterFactory |

**Why**: Overlay UI shouldn't import AIClient. Observer keeps them decoupled.

#### Strategy — `Tone` as strategy

Each tone is a strategy that modifies prompt construction:

```python
class Tone(Enum):
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    DIRECT = "direct"
    APOLOGETIC = "apologetic"

    @property
    def instruction(self) -> str:
        return TONE_INSTRUCTIONS[self]
```

**Why**: Adding a new tone = adding an enum value + instruction string. No if/else chains.

#### Command — `UndoManager`

Stores refinement history for undo (PRD recommendation #5):

```python
@dataclass
class RefinementCommand:
    original: str
    refined: str
    timestamp: float
    adapter: AppAdapter

    def undo(self):
        self.adapter.replace_text(self.original)

class UndoManager:
    _history: deque[RefinementCommand]  # bounded

    def record(self, command: RefinementCommand):
        self._history.append(command)

    def undo_last(self) -> bool:
        if self._history:
            self._history.pop().undo()
            return True
        return False
```

**Why**: Undo requires storing the inverse operation. Command pattern is the textbook fit.

#### State — `OverlayUI` states

```
┌─────────┐  hotkey   ┌───────────┐  first token  ┌────────────┐  done   ┌──────────┐
│  Hidden  │────────→ │  Loading  │──────────────→│ Streaming  │───────→│ Fading   │
└─────────┘          └───────────┘               └────────────┘        └──────────┘
     ↑                     │                          │                     │
     │                     │ error                    │ error               │
     │                     ▼                          ▼                     │
     │               ┌───────────┐                                         │
     └───────────────│   Error   │←────────────────────────────────────────┘
                     └───────────┘                    timeout
```

**Why**: Overlay behavior differs dramatically per state. State pattern prevents spaghetti conditionals.

---

## 6. Module Structure

```
convoq/
├── main.py                     # Entry point
├── config/
│   ├── __init__.py
│   ├── config_manager.py       # Singleton config
│   └── default_config.yaml     # Default settings
├── core/
│   ├── __init__.py
│   ├── engine.py               # ConvoqEngine facade
│   ├── pipeline.py             # RefinementPipeline orchestrator
│   ├── event_bus.py            # Observer event system
│   └── undo_manager.py         # Command pattern undo
├── adapters/
│   ├── __init__.py
│   ├── base.py                 # AppAdapter ABC + protocols
│   ├── factory.py              # AppAdapterFactory
│   ├── whatsapp.py             # WhatsAppAdapter
│   └── detection.py            # Active window detection
├── extractors/
│   ├── __init__.py
│   ├── base.py                 # ContextExtractor ABC
│   ├── chain.py                # ExtractionChain (CoR)
│   ├── ui_automation.py        # UIAutomationExtractor
│   └── ocr.py                  # OCRExtractor fallback
├── ai/
│   ├── __init__.py
│   ├── base.py                 # Refiner ABC
│   ├── groq_refiner.py         # GroqRefiner (streaming)
│   ├── prompt_builder.py       # Builder pattern
│   └── tone.py                 # Tone enum/strategy
├── clipboard/
│   ├── __init__.py
│   └── manager.py              # ClipboardManager proxy
├── ui/
│   ├── __init__.py
│   ├── overlay.py              # OverlayUI (state pattern)
│   ├── states.py               # Overlay state classes
│   └── tray.py                 # TrayManager
├── hotkeys/
│   ├── __init__.py
│   └── manager.py              # HotkeyManager
└── models/
    ├── __init__.py
    └── context.py              # ConversationContext, Message dataclasses
```

---

## 7. Data Models

```python
@dataclass(frozen=True)
class Message:
    text: str
    sender: str          # "self" or contact name
    timestamp: str | None

@dataclass(frozen=True)
class ConversationContext:
    messages: tuple[Message, ...]
    app_name: str
    is_group: bool = False

    def is_valid(self) -> bool:
        return len(self.messages) > 0

    @classmethod
    def empty(cls) -> ConversationContext:
        return cls(messages=(), app_name="unknown")

@dataclass
class RefinementRequest:
    draft: str
    context: ConversationContext
    tone: Tone

@dataclass
class RefinementResult:
    original: str
    refined: str
    tone: Tone
    latency_ms: float
```

---

## 8. Dependency Graph

```
main.py
  → ConvoqEngine (facade)
      → ConfigManager (singleton)
      → HotkeyManager
          → EventBus (observer)
      → RefinementPipeline
          → AppAdapterFactory (factory method)
              → WhatsAppAdapter (adapter)
                  → ExtractionChain (chain of responsibility)
                      → UIAutomationExtractor
                      → OCRExtractor
          → Refiner (abstract)
              → GroqRefiner (concrete)
                  → PromptBuilder (builder)
                  → Tone (strategy)
          → ClipboardManager (proxy)
          → UndoManager (command)
      → OverlayUI (state pattern)
      → TrayManager
```

All arrows point from high-level → abstraction. No high-level module imports a concrete low-level class directly (DIP).

---

## 9. Pattern Summary

| Pattern | Category | Where | Why |
|---------|----------|-------|-----|
| Factory Method | Creational | `AppAdapterFactory` | Create adapters without knowing concretions |
| Singleton | Creational | `ConfigManager` | One config instance, consistent state |
| Builder | Creational | `PromptBuilder` | Complex prompt construction, step by step |
| Adapter | Structural | `WhatsAppAdapter`, etc. | Uniform interface over different app UIs |
| Facade | Structural | `ConvoqEngine` | Hide subsystem complexity from entry point |
| Proxy | Structural | `ClipboardManager` | Safe clipboard access with locking/backup |
| Chain of Responsibility | Behavioral | `ExtractionChain` | Fallback chain for context extraction |
| Observer | Behavioral | `EventBus` | Decouple hotkeys, AI, and UI |
| Strategy | Behavioral | `Tone` | Swap tone behavior without conditionals |
| Command | Behavioral | `UndoManager` | Reversible refinement operations |
| State | Behavioral | `OverlayUI` states | Clean overlay state transitions |

---

## 10. Key Design Decisions

1. **Protocols over ABCs where possible** — Python's structural typing (Protocol) keeps things Pythonic and avoids deep inheritance trees
2. **Async streaming throughout** — AIClient yields tokens via `AsyncIterator`, overlay consumes them reactively
3. **Event-driven decoupling** — Components communicate through EventBus, not direct references
4. **Bounded undo history** — `deque(maxlen=10)` prevents memory growth
5. **Config as YAML** — Human-editable, no database needed for a desktop app
6. **Frozen dataclasses for models** — Immutable data prevents accidental mutation across threads
