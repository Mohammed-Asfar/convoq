"""Tone strategy — each tone carries its own prompt instruction."""

from enum import Enum


class Tone(Enum):
    """Supported message tones. Each value maps to a prompt instruction."""

    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    DIRECT = "direct"
    APOLOGETIC = "apologetic"
    TANGLISH = "tanglish"

    @property
    def instruction(self) -> str:
        return _TONE_INSTRUCTIONS[self]

    @property
    def label(self) -> str:
        return self.value.capitalize()


_TONE_INSTRUCTIONS: dict[Tone, str] = {
    Tone.CASUAL: (
        "Use a relaxed, conversational tone. Keep it natural like texting a friend. "
        "Use contractions, simple words, and short sentences."
    ),
    Tone.PROFESSIONAL: (
        "Use a polished, professional tone. Be clear and respectful. "
        "Avoid slang, use complete sentences, and maintain a business-appropriate register."
    ),
    Tone.FRIENDLY: (
        "Use a warm, approachable tone. Be enthusiastic but not over the top. "
        "Show genuine interest and positivity."
    ),
    Tone.DIRECT: (
        "Be concise and to the point. No filler words, no unnecessary pleasantries. "
        "State things clearly and efficiently."
    ),
    Tone.APOLOGETIC: (
        "Use a sincere, empathetic tone. Acknowledge the issue, express genuine regret, "
        "and convey a willingness to make things right."
    ),
    Tone.TANGLISH: (
        "Rewrite the message in Tanglish — the way young Tamil people ACTUALLY text on WhatsApp. "
        "This means MOSTLY English words with a FEW Tamil words sprinkled in naturally. "
        "NOT full Tamil written in English letters. "
        "The base language should be ENGLISH with Tamil flavor words mixed in.\n\n"
        "GOOD examples:\n"
        "- 'no worries da, team leader will take care'\n"
        "- 'bro nee correct dhan, let's do it'\n"
        "- 'ok macha, I'll handle this one'\n"
        "- 'dei wait panna, I'm coming'\n"
        "- 'project deadline pakka ready, don't worry'\n\n"
        "BAD examples (too much Tamil, hard to read):\n"
        "- 'team leader ku theriyum, avanga paathukuvanga' — TOO MUCH Tamil\n"
        "- 'Oru sol ena, therinuku solla kollala' — this is just Tamil in English letters, NOT Tanglish\n\n"
        "Rules: Keep 70-80% English, 20-30% Tamil words. Use Tamil only for common words like "
        "da, bro, macha, dei, dhan, panna, vaanga, sollu, pakka, podu. "
        "The message MUST be easily readable by someone who knows basic Tamil words."
    ),
}
