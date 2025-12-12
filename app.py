import streamlit as st
import backend

st.set_page_config(page_title="Expert Notes", page_icon="📝", layout="wide")

st.title("📝 Expert Video Notes")

# Session State
if 'selected_summary' not in st.session_state:
    st.session_state['selected_summary'] = None
if 'selected_title' not in st.session_state:
    st.session_state['selected_title'] = None

# --- SIDEBAR ---
st.sidebar.header("📚 History")
if st.sidebar.button("🗑️ Clear All History"):
    backend.delete_history()
    st.session_state['selected_summary'] = None
    st.rerun()

history = backend.load_history()

if not history:
    st.sidebar.info("No notes yet.")
else:
    for item in history:
        title = item.get('title', 'Unknown')
        if len(title) > 35: title = title[:35] + "..."
        if st.sidebar.button(f"📄 {title}", key=item['timestamp']):
            st.session_state['selected_summary'] = item['summary']
            st.session_state['selected_title'] = item['title']
            st.session_state['selected_url'] = item['url']
            st.rerun()

# --- MAIN PAGE ---
if st.session_state['selected_summary']:
    # Navigation
    if st.button("⬅️ New Video"):
        st.session_state['selected_summary'] = None
        st.rerun()
    
    st.divider()
    
    # Header
    st.header(st.session_state.get('selected_title', 'Notes'))
    st.markdown(f"🔗 [Watch Original Video]({st.session_state.get('selected_url', '#')})")
    
    st.markdown("---")

    # 📑 TABS: Rendered vs Raw
    tab1, tab2 = st.tabs(["📖 Reading View", "💻 Raw Markdown"])
    
    with tab1:
        # This renders the Markdown beautifully
        st.markdown(st.session_state['selected_summary'])
    
    with tab2:
        # This shows the code if you need to copy it
        st.text_area("Raw Markdown", value=st.session_state['selected_summary'], height=600)

else:
    # --- SEARCH INPUT ---
    st.markdown("### Generate expert-level notes with timestamps.")
    
    col1, col2 = st.columns([5, 1])
    with col1:
        url = st.text_input("YouTube URL", placeholder="https://youtube.com/...")
    with col2:
        tg = st.checkbox("Telegram", value=True)
        st.write("")
    
    if st.button("🚀 Process Video", type="primary"):
        if url:
            vid_id = backend.extract_video_id(url)
            if vid_id:
                with st.spinner("⏳ Fetching Transcript..."):
                    text = backend.get_transcript(vid_id)
                
                if text:
                    with st.spinner("🧠 Generating Notes..."):
                        title = backend.get_video_title(url)
                        summary = backend.generate_summary(text)
                        
                        backend.save_to_history(vid_id, url, title, summary)
                        
                        st.session_state['selected_summary'] = summary
                        st.session_state['selected_title'] = title
                        st.session_state['selected_url'] = url
                        
                        if tg:
                            backend.send_telegram_message(f"📝 {title}\n\n{summary}")
                        
                        st.rerun()
                else:
                    st.error("No transcript found.")