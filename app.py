import streamlit as st
from utils.transcript import get_transcript_from_url, extract_article_text, extract_text_from_pdf, extract_text_from_docx
from utils.llama_api import generate_flashcards_with_ollama
from utils.database import save_flashcards, get_saved_flashcards
from utils.download import flashcards_to_csv, flashcards_to_pdf, flashcards_to_tsv
import fitz  

# Initialize session state variable
if 'cleared_old_flashcards' not in st.session_state:
    st.session_state.cleared_old_flashcards = False

# Set page configuration
st.set_page_config(page_title="NexLearn-AI", layout="centered")

# Inject custom CSS and JS for styling and flip effect
st.markdown("""
    <style>
        
        body {
            /* Use Streamlit's theme variables. The fallbacks should match your config.toml light theme. */
            background-color: var(--streamlit-theme-backgroundColor, #F0F2F6); 
            color: var(--streamlit-theme-textColor, #1f2937);            
            font-family: 'Segoe UI', sans-serif; 
        }

        /* Navigation Buttons (About & Export) Container & Styling */
        .header-nav-buttons-container { 
            display: flex;
            justify-content: flex-end; 
            align-items: center; 
            /* gap: 10px; 
            padding-top: 5px; 
            padding-bottom: 10px; 
        }

        .header-nav-buttons-container div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button {
            background-color: var(--streamlit-theme-primaryColor, #2563eb) !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 8px 18px !important; 
            font-weight: 500 !important;
            font-size: 0.95em !important; 
            width: 100% !important; 
            text-align: center !important;
            line-height: 1.3 !important;
            transition: background-color 0.2s ease-in-out;
            cursor: pointer !important;
        }

        .header-nav-buttons-container div[data-testid="stVerticalBlock"] div[data-testid="stButton"] > button:hover {
            background-color: #1d4ed8 !important;
        }
        
        div[data-testid="stHorizontalBlock"]:first-child { 
            padding-top: 15px; 
            padding-bottom: 15px; 
            align-items: center; 
        }
            
        .input-area-container {
            background-color: var(--streamlit-theme-secondaryBackgroundColor, #FFFFFF);
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-top: 20px;
            margin-bottom: 30px;
        }
            
        .input-area-container .stButton>button {
            width: 100% !important; 
            background-color: var(--streamlit-theme-primaryColor, #2563eb) !important; 
            color: white !important; 
            border: none !important; 
            padding-top: 10px !important; 
            padding-bottom: 10px !important; 
            border-radius: 6px !important; 
            font-weight: 500 !important; 
        }

        .input-area-container .stButton>button:hover {
            background-color: #1d4ed8 !important; 
            /* color: white !important; /* Ensuring white text on hover is good too */
        }
        
        div[data-testid="stDownloadButton"] > button {
            width: 100% !important; 
            background-color: var(--streamlit-theme-secondaryBackgroundColor, #F8F9FA) !important; 
            color: var(--streamlit-theme-textColor, #1f2937) !important; 
            border: 1px solid #D3D6DA !important; 
            font-weight: 500 !important;
        }
        div[data-testid="stDownloadButton"] > button:hover {
            background-color: #E9ECEF !important; 
            border-color: #B groupBy0C4 !important;
        }
                    
        .nav-buttons {
            display: flex;
            gap: 10px;
        }

        .flashcard-container {
            perspective: 1000px;
            margin: 20px 0;
        }

        .flashcard {
            width: 100%;
            max-width: 600px;
            min-height: 150px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            transform-style: preserve-3d;
            transition: transform 0.6s;
            margin: auto;
            position: relative;
            user-select: none;
            padding: 25px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.3em;
            color: #111827;
        }

        .flashcard.flipped {
            transform: rotateY(180deg);
        }

        .flashcard-front, .flashcard-back {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 12px;
            backface-visibility: hidden;
            padding: 25px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .flashcard-front {
            color: #111827;
            font-weight: bold;
            font-size: 1.3em;
        }
        .flashcard-back {
            background: #e0f2fe;
            color: #1e3a8a;
            border-left: 10px solid #2563eb;
            transform: rotateY(180deg);
            font-size: 1em;
            padding: 25px; 
            height: 100%; 
            box-sizing: border-box; 
            display: flex;
            align-items: center; 
            justify-content: center; 
            text-align: center; 
            overflow-wrap: break-word; 
            word-wrap: break-word;
            white-space: normal; 
            overflow-y: auto;
        }
            
        .nav-flashcard-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
        }
        .nav-flashcard-buttons button {
            background-color: #2563eb;
            border: none;
            color: white;
            padding: 8px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
        }
        .nav-flashcard-buttons button:disabled {
            background-color: #a5b4fc;
            cursor: not-allowed;
        }
            
        .flip-btn {
            background-color: #2563eb;
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
            
        .saved-view-flashcard .flashcard-container {
            margin: 25px auto; 
        }
        .saved-view-flashcard .flashcard {
            max-width: 750px !important; 
            min-height: 200px !important; 
        }
        .saved-view-flashcard .flashcard-front { 
            /* font-size: 1.4em !important; */
        }
        .saved-view-flashcard .flashcard-back { 
            /* font-size: 1.2em !important; */ /* For Answer on back */
        }

    </style>
""", unsafe_allow_html=True)

# Initialize session state variables if not present
if "view" not in st.session_state:
    st.session_state.view = "home"
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "flipped" not in st.session_state:
    st.session_state.flipped = False
if "saved_flipped_states" not in st.session_state:
    st.session_state.saved_flipped_states = []

# App Header with navigation buttons

# if st.button("NexLearn-AI", key="home_btn", use_container_width=False):
#     st.session_state.view = "home"
#     st.session_state.flipped = False

# with st.container(): # Use a Streamlit container
#     st.markdown("<div id='nexlearn-title-container'>", unsafe_allow_html=True) # Custom ID for CSS
#     if st.button("🏠 NexLearn", key="home_btn_title_main", use_container_width=False):
#         st.session_state.view = "home"
#         st.session_state.flipped = False
#     st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"""
    <a href="?view=home&rerun={st.session_state.get('rerun_count', 0) + 1}" target="_self" style="text-decoration: none; display: block; text-align: center;">
        <h1 style="color: var(--streamlit-theme-primaryColor, #2563eb); font-size: 3.5em; font-weight: bold; margin-bottom: 5px; margin-top: 10px;">
             NexLearn-AI
        </h1>
    </a>
""", unsafe_allow_html=True)

query_params = st.query_params 
if "view" in query_params and query_params["view"] == "home":
    if 'navigated_home' not in st.session_state or not st.session_state.navigated_home:
         st.session_state.view = "home" 
         st.session_state.flipped = False
         st.session_state.navigated_home = True 
else:
    st.session_state.navigated_home = False

st.markdown("<div class='header-nav-buttons-container'>", unsafe_allow_html=True)
nav_button_cols = st.columns([1,1])
with nav_button_cols[0]:
    if st.button("About", key="about_nav_btn", use_container_width=True, type="primary"):
        st.session_state.view = "about"
        st.session_state.flipped = False
with nav_button_cols[1]:
    if st.button("Export", key="saved_nav_btn", use_container_width=True, type="primary"):
        st.session_state.view = "saved"
        st.session_state.flipped = False
st.markdown("</div>", unsafe_allow_html=True)


# st.markdown("<div class='header-nav-buttons-container'>", unsafe_allow_html=True)
# nav_button_cols = st.columns([1,1]) 
# with nav_button_cols[0]:
#     if st.button("About", key="about_nav_btn", use_container_width=True, type = 'primary'):
#         st.session_state.view = "about"
#         st.session_state.flipped = False
# with nav_button_cols[1]:
#     if st.button("Export", key="saved_nav_btn", use_container_width=True, type = 'primary'):
#         st.session_state.view = "saved"
#         st.session_state.flipped = False
# st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# Function to generate flashcards and save
def generate_and_save(url, count):
    try:
        transcript = get_transcript_from_url(url)
        flashcards = generate_flashcards_with_ollama(transcript, num_flashcards=count)[:count]
        st.session_state.flashcards = flashcards
        st.session_state.current_index = 0
        st.session_state.flipped = False
        save_flashcards(flashcards)
        st.success("✅ Flashcards generated and saved!")
    except Exception as e:
        st.error(f"Error: {e}")

def generate_flashcards_from_article(url, count):
    article_text = extract_article_text(url)
    if not article_text:
        raise ValueError("Could not extract content from the article.")
    flashcards = generate_flashcards_with_ollama(article_text, num_flashcards=count)[:count]
    st.session_state.flashcards = flashcards
    st.session_state.current_index = 0
    st.session_state.flipped = False
    save_flashcards(flashcards)
    st.success("Flashcards generated from article!")
    #return flashcards
    

# Flashcard display with flip effect
def show_flashcard(index):
    flashcard = st.session_state.flashcards[index]

    card_html = f"""
    <div class="flashcard-container">
        <div class="flashcard {'flipped' if st.session_state.flipped else ''}">
            <div class="flashcard-front">
                Q: {flashcard['question']}
            </div>
            <div class="flashcard-back">
                {flashcard['answer']}
            </div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# Button callback functions for navigation and flip
def flip_flashcard():
    st.session_state.flipped = not st.session_state.flipped

def next_flashcard():
    if st.session_state.current_index < len(st.session_state.flashcards) - 1:
        st.session_state.current_index += 1
        st.session_state.flipped = False

def prev_flashcard():
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
        st.session_state.flipped = False

# Views logic
if st.session_state.view == "home":

    st.markdown("### Generate AI Flashcards from Multiple Inputs")

    st.info(
            "✨ **Tips for Great Flashcards!**\n\n"
    "Our AI is ready to help you learn smarter. Here's how to get the best results:\n"
    "- **Content is Key:** For the sharpest flashcards, focus on specific topics. Texts under about **6,000 words** (or ~24,000 characters) often work great.\n"
    "- **Combine Your Sources:** Feel free to mix and match! You can generate flashcards by combining a YouTube video with your uploaded notes (PDF/Word) or pasted text.\n"
    "- **Longer Materials?** If you have extensive content, consider breaking it into a few smaller sections for separate flashcard batches. This can improve focus and quality."
    )
    st.markdown("---")

    # Let user select multiple input types
    input_options = st.multiselect("Select Input Types to Include:", 
                                   ["YouTube URL", "Web Article", "Document Upload", "Paste Text"])

    count = st.number_input("🔢 Number of flashcards to generate", min_value=1, max_value=50, value=5)

    combined_text = ""

    # Inputs storage to display inputs if needed
    youtube_url = ""
    article_url = ""
    uploaded_file = None
    pasted_text = ""

    if "YouTube URL" in input_options:
        youtube_url = st.text_input("Enter YouTube URL")

    if "Web Article" in input_options:
        article_url = st.text_input("Enter Web Article URL")

    if "Document Upload" in input_options:
        uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "doc", "docx"])

    if "Paste Text" in input_options:
        pasted_text = st.text_area("Paste your notes or text here")

    generate_disabled = False
    error_msgs = []

    # Validate inputs to enable Generate button only if any input has data
    has_any_input = any([
        (youtube_url and "YouTube URL" in input_options),
        (article_url and "Web Article" in input_options),
        (uploaded_file and "Document Upload" in input_options),
        (pasted_text.strip() and "Paste Text" in input_options)
    ])

    if not has_any_input:
        generate_disabled = True
        error_msgs.append("Please provide input data for at least one selected input type.")

    
    if st.button("Generate Flashcards", disabled=generate_disabled, key="generate_btn_home"):
        with st.spinner(" Generating your flashcards... Hang tight!"):
            try:
                # Get transcript from YouTube
                if youtube_url:
                    combined_text += get_transcript_from_url(youtube_url) + "\n\n"

                # Extract article text
                if article_url:
                    article_text = extract_article_text(article_url)
                    if not article_text:
                        st.warning("Could not extract content from the article URL.")
                    else:
                        combined_text += article_text + "\n\n"

                # Extract from uploaded doc/pdf
                if uploaded_file:
                    if uploaded_file.name.endswith(".pdf"):
                        combined_text += extract_text_from_pdf(uploaded_file) + "\n\n"
                    else:
                        combined_text += extract_text_from_docx(uploaded_file) + "\n\n"

                # Add pasted text
                min_chars = 50  # minimum number of characters required in pasted text
                min_words = 50  # minimum number of words required in pasted text

                pasted_text_stripped = pasted_text.strip()

                # Check length and word count only for pasted text
                if "Paste Text" in input_options:
                    text_length_ok = len(pasted_text_stripped) >= min_chars
                    word_count_ok = len(pasted_text_stripped.split()) >= min_words
                    can_generate_pasted_text = text_length_ok and word_count_ok

                    if not can_generate_pasted_text:
                        error_msgs.append(
                            f"Pasted text must have at least {min_chars} characters and {min_words} words."
                        )

                    if can_generate_pasted_text:
                        combined_text += pasted_text_stripped + "\n\n"
                else:
                    # If paste text is not selected, no check needed
                    can_generate_pasted_text = True

                if not combined_text.strip():
                    st.error("No valid content extracted from the selected inputs.")
                else:
                    max_chars = 24000  # LLaMA 3 safe limit
                    if len(combined_text) > max_chars:
                        st.warning(
                            f"⚠️ Your input is {len(combined_text):,} characters. "
                            f"This exceeds the recommended limit of {max_chars:,} characters. "
                            "Flashcard quality may degrade or be truncated."
                        )
                        # Optional: Uncomment to automatically truncate
                        # combined_text = combined_text[:max_chars]

                    # Generate flashcards from combined text
                    flashcards = generate_flashcards_with_ollama(combined_text, num_flashcards=count)[:count]
                    st.session_state.flashcards = flashcards
                    st.session_state.current_index = 0
                    st.session_state.flipped = False
                    save_flashcards(flashcards)
                    st.success("Flashcards generated from combined inputs!")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if st.session_state.flashcards:
        show_flashcard(st.session_state.current_index)

        #st.markdown("<div class='nav-flashcard-buttons'>", unsafe_allow_html=True)
        colA, colB, colC = st.columns(3)
        with colA:
            prev_disabled = st.session_state.current_index <= 0
            st.button("⬅️ Previous", disabled=prev_disabled, on_click=prev_flashcard, key="prev_btn", use_container_width=True, type="primary")       
        with colB:
            st.button("🔄 Flip", on_click=flip_flashcard, key="flip_btn_home", use_container_width=True, type="primary")
        with colC:
            next_disabled = st.session_state.current_index >= len(st.session_state.flashcards) - 1
            st.button("➡️ Next", disabled=next_disabled, on_click=next_flashcard, key="next_btn_home", use_container_width=True, type="primary")
        #st.markdown("</div>", unsafe_allow_html=True)


elif st.session_state.view == "about":
    st.markdown("<div class='about-page-container'>", unsafe_allow_html=True) # Optional container for styling

    st.markdown("# About NexLearn-AI ")
    st.markdown("---") 

    st.markdown(
        "NexLearn-AI is your intelligent study companion, designed to accelerate your learning "
        "and boost knowledge retention by transforming diverse content into interactive flashcards."
    )
    st.markdown("")

    st.markdown("### What is NexLearn-AI?")
    st.markdown(
        "In a world overflowing with information, NexLearn-AI helps you cut through the noise. "
        "We leverage the power of cutting-edge AI to automatically generate concise, effective Q&A flashcards "
        "from various sources like YouTube videos, web articles, uploaded documents (PDFs, Word files), or even your own pasted notes. "
        "Stop passively consuming content and start actively engaging with it!"
    )
    st.markdown("")

    st.markdown("### Why Was NexLearn-AI Built?")
    st.markdown(
        "NexLear-AIn was born from the idea that learning should be efficient, engaging, and accessible. "
        "Traditional note-taking and content review can be time-consuming. We aim to streamline this process by: "
        "\n- **Saving Time:** Automating the creation of study materials."
        "\n- **Enhancing Recall:** Utilizing the proven effectiveness of active recall and spaced repetition facilitated by flashcards."
        "\n- **Promoting Microlearning:** Breaking down complex information into digestible Q&A pairs."
        "\n- **Supporting Diverse Learners:** Catering to students, professionals, lifelong learners, and educators who want to maximize their understanding of any given material."
    )
    st.markdown("")

    st.markdown("### Key Features We Offer:")
    st.markdown(
        "- **Multi-Source Input:** Generate flashcards from:"
        "\n\n  - YouTube Video URLs"
        "\n\n  - Web Article Links"
        "\n\n  - Uploaded Documents (PDF, DOCX, DOC)"
        "\n\n  - Pasted Text or Notes"
        "\n\n  - Generate User Defined Flashcards"
        "\n\n  - Combine multiple sources into one set of flashcards!"
        "\n- **AI-Powered Generation:** Smart Q&A pairs created using advanced Large Language Models (LLMs)."
        "\n- **Interactive Flashcard UI:** Engaging flip-card interface for active review."
        "\n- **Local Storage:** Your generated flashcards are saved for the current session, allowing you to review and revisit them."
        "\n- **Multiple Export Options:** Download your flashcards as:"
        "\n\n  - CSV (Comma-Separated Values) - for spreadsheets or other tools."
        "\n\n  - TSV (Tab-Separated Values) - ideal for importing into Anki and other spaced repetition software."
        "\n\n  - PDF - for easy printing and offline review."
        "\n- **Adjustable Flashcard Count:** You decide how many flashcards you want from your content."
    )
    st.markdown("")

    st.markdown("### Future Vision & Potential Next Steps:")
    st.markdown(
        "- **User Accounts & Persistent Storage:** Allowing users to save flashcard sets across sessions."
        "\n- **Advanced Customization:** More control over flashcard generation (e.g., type of questions, difficulty)."
        "\n- **Spaced Repetition System (SRS) Integration:** Direct integration or smarter export for SRS tools."
        "\n- **Image Support:** Generating flashcards from content with images, or allowing image-based answers."
        "\n- **Wider Range of LLMs:** Support for more local and cloud-based LLMs."
        "\n- **Collaboration Features:** Sharing flashcard sets with others."
        "\n- **Browser Extension:** For even easier content capture from the web."
    )
    st.markdown("")

    st.markdown(
        "**NexLearn-AI - Learn Faster. Remember Longer.**"
    )
    st.markdown("</div>", unsafe_allow_html=True)


# elif st.session_state.view == "about":
#     st.markdown("##  About NexLearn-AI")
#     st.markdown("""
#         NexLearn-AI is an AI-powered platform that transforms long-form educational videos into concise flashcards.
        
#          **What it does:**
#         - Extracts transcript from YouTube videos
#         - Uses LLaMA 3 to generate smart Q&A flashcards
#         - Saves flashcards for future review
#         - Ideal for microlearning, students, lifelong learners, and educators

#         ⚙️ Built with:
#         - Python + Streamlit
#         - Ollama + LLaMA 3
#         - YouTube Transcript API
#         - SQLite backend for saving flashcards

#         Learn faster. Remember longer. ✨
#     """)

elif st.session_state.view == "saved":
    st.markdown("## 💾 Saved Flashcards")
    saved_flashcards = get_saved_flashcards()

    # Initialize flip states for saved cards if not matching
    if len(st.session_state.saved_flipped_states) != len(saved_flashcards):
        st.session_state.saved_flipped_states = [False] * len(saved_flashcards)

    if saved_flashcards:

        st.markdown("### Export Your Flashcards")
        
        col_csv, col_tsv, col_pdf = st.columns(3)
        with col_csv:
            csv_data = flashcards_to_csv(saved_flashcards)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="nexlearn_flashcards.csv",
                help="Click to download the cards in CSV format",
                mime="text/csv",
                use_container_width=True
            )
        with col_tsv:
            tsv_data = flashcards_to_tsv(saved_flashcards)
            st.download_button(
                label="Download TSV (Anki)",
                data=tsv_data,
                file_name="nexlearn_flashcards.tsv",
                help="Click to download the cards in TSV format",
                mime="text/tab-separated-values",
                use_container_width=True
            )
        with col_pdf:
            pdf_bytes_io = flashcards_to_pdf(saved_flashcards)
            st.download_button(
                label="Download PDF",
                data=pdf_bytes_io,
                file_name="flashcards.pdf",
                help="Click to download the cards in PDF format",
                mime="application/pdf",
                use_container_width=True
            )
        st.markdown("---")

        st.markdown("### Review Your Flashcards")

        for i, card_data in enumerate(saved_flashcards):
            #flip_button = st.button(f"Flip Card {i+1}", key=f"flip_saved_{i}", help="Click to flip card")
            #if flip_button:
                # Toggle flip state for this card only
             #   st.session_state.saved_flipped_states[i] = not st.session_state.saved_flipped_states[i]

            flipped_class = "flipped" if st.session_state.saved_flipped_states[i] else ""

            card_html = f"""
            <div class="saved-view-flashcard">
                <div class="flashcard-container" style="margin-bottom: 5px;"> 
                    <div class="flashcard {'flipped' if st.session_state.saved_flipped_states[i] else ''}" id="saved-card-{i}">
                        <div class="flashcard-front">
                            Q: {card_data['question']}
                        </div>
                        <div class="flashcard-back">
                            {card_data['answer']}
                        </div>
                    </div>
                </div>
             </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # if st.button(f"🔄 Flip Card {i+1}", key=f"flip_saved_btn_{i}", use_container_width=True, help="Click to flip this card"):
            #     st.session_state.saved_flipped_states[i] = not st.session_state.saved_flipped_states[i]
            #     st.rerun() # Rerun to reflect the flip immediately

            # Modified for narrower, centered button:
            button_cols = st.columns([1, 2, 1]) # Ratio: 1 part empty, 2 parts button, 1 part empty
                                                # Adjust ratio e.g. [1,1,1] for smaller, [2,1,2] for wider empty space
            with button_cols[1]: # Place button in the middle column
                if st.button(
                    f" Flip Card {i+1}", 
                    key=f"flip_saved_btn_{i}", 
                    use_container_width=True, # KEEP True so it fills the MIDDLE column
                    help="Click to flip this card", 
                    type="primary" # Keep as secondary or change to primary if desired
                ):
                    st.session_state.saved_flipped_states[i] = not st.session_state.saved_flipped_states[i]
                    st.rerun()

            st.markdown("---")

    else:
        st.info("Looks like you haven't saved any flashcards yet. Go to the Home page to generate some!")

else:
    st.info("Looks like you haven't saved any flashcards yet. Go to the Home page to generate some!")
