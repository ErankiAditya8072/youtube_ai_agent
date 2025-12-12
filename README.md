# YouTube AI Note-Taker

A powerful AI agent that turns YouTube videos into detailed, time-stamped study notes. 

Built with **Streamlit** and **Groq (Llama 3)**, this tool extracts transcripts, processes them using a sophisticated prompt to remove fluff, and generates a structured Markdown summary.

##Features

* **Automated Note-Taking**: Converts video audio into high-quality, objective technical notes.
* **Smart Timestamps**: Automatically adds timestamps to section headers so you can jump to specific parts of the video.
* **No Fluff**: The AI is prompted to remove meta-talk (e.g., "The speaker says...") and focus purely on the concepts.
* **Local History**: Saves your summaries automatically to a JSON file so you don't have to re-generate them.
* **Telegram Integration**: Optionally sends the summary directly to your Telegram chat.
* **Dual View**: Switch between a beautiful rendered view and raw Markdown code.

## Tech Stack

* **Python 3.8+**
* **Streamlit** (Frontend UI)
* **Groq Cloud API** (LLM Power / Llama 3-70b)
* **YouTube Transcript API** (Data extraction)

## Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/youtube-ai-agent.git](https://github.com/YOUR_USERNAME/youtube-ai-agent.git)
    cd youtube-ai-agent
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Keys**
    Open `backend.py` and find the configuration section at the top. Paste your API keys inside the quotes:
    
    ```python
    # backend.py
    GROQ_API_KEY = "gsk_..."        # Get from console.groq.com
    TELEGRAM_BOT_TOKEN = "..."      # Get from BotFather (Optional)
    TELEGRAM_CHAT_ID = "..."        # Your Chat ID
    ```.

## How to Run

Run the Streamlit app from your terminal:

```bash
streamlit run app.py
