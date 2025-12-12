import os
import json
import re
from dotenv import load_dotenv
import requests
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # 🔴 PASTE YOUR GROQ API KEY HERE
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # From BotFather
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HISTORY_FILE = "summary_history.json"

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ==========================================
# 💾 HISTORY
# ==========================================
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_to_history(video_id, url, title, summary_text):
    history = load_history()
    history = [item for item in history if item['video_id'] != video_id]
    
    data = {
        "video_id": video_id,
        "url": url,
        "title": title,
        "summary": summary_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    history.insert(0, data)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def delete_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# ==========================================
# 📹 YOUTUBE LOGIC
# ==========================================
def extract_video_id(url):
    patterns = [r'(?:v=|\/)([0-9A-Za-z_-]{11}).*']
    match = re.search(patterns[0], url)
    return match.group(1) if match else None

def get_video_title(video_url):
    try:
        oembed = f"https://www.youtube.com/oembed?url={video_url}&format=json"
        return requests.get(oembed).json().get('title', 'Unknown Video')
    except:
        return "Unknown Video"

def format_timestamp(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ✅ YOUR REQUESTED CODE (With Timestamps Added)
def get_transcript(video_id):
    """Fetches transcript using multiple fallback methods."""
    try:
        ytt_api = YouTubeTranscriptApi()
        # 1. Try standard languages
        try:
            fetched_transcript = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB', 'hi'])
        except NoTranscriptFound:
            # 2. Fallback logic
            transcript_list = ytt_api.list(video_id)
            try:
                # Try manual
                transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB', 'hi'])
            except NoTranscriptFound:
                try:
                    # Try auto-generated
                    transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB', 'hi'])
                except NoTranscriptFound:
                    # Translate first available
                    for t in transcript_list:
                        if t.is_translatable:
                            transcript = t.translate('en')
                            break
                    else:
                        return None
            fetched_transcript = transcript.fetch()

        # 3. Process the transcript (Handle both Dicts and Objects)
        # ⚠️ I updated this part to INCLUDE TIMESTAMPS so your AI prompt works.
        formatted_list = []
        for entry in fetched_transcript:
            if isinstance(entry, dict):
                text = entry['text']
                start = entry['start']
            else:
                text = entry.text
                start = entry.start
            
            # Format: [00:00:00] Text here...
            time_str = format_timestamp(start)
            formatted_list.append(f"[{time_str}] {text}")

        return "\n".join(formatted_list)

    except Exception as e:
        print(f"Transcript Error: {e}")
        return None

# ==========================================
# 🧠 AI SUMMARY
# ==========================================

def clean_markdown_spacing(text):
    text = re.sub(r'(?<!\n)\n(#{1,3} )', r'\n\n\1', text)
    text = re.sub(r'(?<!\n)\n(- )', r'\n\n\1', text)
    text = re.sub(r'(?<!\n)\n(\[)', r'\n\n\1', text)
    return text

def generate_summary(text):
    if not client: return "Error: Groq Key Missing"
    
    truncated_text = text[:35000]

    # 🔥 YOUR EXACT PROMPT
    prompt = f"""
    You are an expert technical editor. Your goal is to convert the raw transcript below into clean, objective, and highly structured notes along with a good explanation.

    STRICT RULES:
    1. **NO META-TALK**: Do NOT use words like "The speaker says", "The interviewer asks", "He mentions", "She explains". 
       - BAD: "The speaker explains that AI is evolving."
       - GOOD: "AI is evolving rapidly due to new algorithms."
       - Write directly about the subject matter in the active or passive voice.
    
    2. **TIMESTAMPS**: Do NOT put a timestamp on every line. 
       - ONLY put a timestamp at the start of a Header (H2).
       - Example: ## [00:02:15] Section Title

    3. **FORMATTING**:
       - Use H2 (##) for Main Sections.
       - Use Bullet Points (-) for details.
       - Use **Bold** for key terms.
       - Leave a BLANK LINE between every bullet point.

    4. **CONTENT**:
       - Capture every technical detail, formula, and argument.
       - If a specific tool/resource is mentioned, list it.
     
    5. Definitions & Jargon: Explain technical terms clearly.
    6. Examples & Analogies: Record every example/analogy.
    8. Important Quotes: Write verbatim inside quotes.
    8. Summary Section at the End:
       - 1-paragraph summary
       - Key Takeaways list
       - Glossary.

    STRUCTURE EXAMPLE:
    ## [00:00:00] Overview of Intelligence
    - The optimal size of the cognitive core is measured in bits.
    
    - Historically, the field prioritized larger models, but efficiency is now increasing.

    ## [00:01:30] Problems with Training Data
    - Internet data is often unreliable, necessitating filtering mechanisms.
    
    - High-quality data curation reduces the need for massive parameter counts.

    TRANSCRIPT DATA:
    {truncated_text}
    """

    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        raw_text = chat.choices[0].message.content
        return clean_markdown_spacing(raw_text)
    except Exception as e:
        return f"Groq Error: {e}"

# ==========================================
# ✈️ TELEGRAM
# ==========================================
def send_telegram_message(msg):
    if not TELEGRAM_BOT_TOKEN: return False, "No Token"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    clean = msg.replace("#", "").replace("**", "").replace("`", "")
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": clean})
    return True, "Sent"