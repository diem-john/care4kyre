import streamlit as st
import os
from src.question_engine import QuestionBank
from src.models import QuizSession
from src.database import DatabaseManager
from src.score_manager import ScoreManager

# --- CONFIGURATION ---
st.set_page_config(
    page_title="PNLE Reviewer Pro",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="expanded"
)


# Load CSS
def load_css():
    css_path = "assets/styles.css"
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


load_css()


# --- INITIALIZATION ---
@st.cache_resource
def get_managers():
    db = DatabaseManager()
    return db, ScoreManager(db), QuestionBank()


db, score_manager, question_bank = get_managers()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🩺 PNLE Reviewer")
    available_sets = question_bank.get_available_sets()

    if not available_sets:
        st.error("Question bank is empty or missing.")
        st.stop()

    selected_set = st.selectbox("Choose PNLE Set", available_sets)

    st.markdown("---")
    st.page_link("pages/dashboard.py", label="📊 View Analytics", icon="📈")

# --- MAIN UI LOGIC ---
parts = question_bank.get_parts_for_set(selected_set)
if not parts:
    st.warning("No parts found for this set.")
    st.stop()

# Generate Tabs dynamically
tabs = st.tabs(parts)

for i, part_name in enumerate(parts):
    with tabs[i]:
        session_key = f"session_{selected_set}_{part_name}"

        # Initialize Session State for this specific Set+Part
        if session_key not in st.session_state:
            questions = question_bank.get_shuffled_questions(selected_set, part_name)
            st.session_state[session_key] = QuizSession(
                set_name=selected_set,
                part_name=part_name,
                questions=questions
            )
            st.session_state[f"show_rationale_{session_key}"] = False

        session: QuizSession = st.session_state[session_key]

        # Completion View
        if session.completed:
            st.success("🎉 You have completed this part!")
            st.metric("Final Score", f"{session.score} / {len(session.questions)}")

            # Historical Comparison
            prev_score = score_manager.get_previous_score(selected_set, part_name)
            if prev_score:
                current_pct = (session.score / len(session.questions)) * 100
                diff = current_pct - prev_score['percentage']

                st.write("### Performance Trend")
                col1, col2 = st.columns(2)
                col1.metric("Previous Score", f"{prev_score['score']}/{prev_score['total_questions']}",
                            f"{prev_score['percentage']:.1f}%")
                col2.metric("Current Score", f"{session.score}/{len(session.questions)}", f"{diff:+.1f}%")

            if st.button("Retry Part", key=f"retry_{session_key}"):
                del st.session_state[session_key]
                st.rerun()

            continue

        # Single Question Flow
        if not session.questions:
            st.info("No questions available in this section.")
            continue

        q = session.questions[session.current_index]

        # Progress UI
        progress = (session.current_index) / len(session.questions)
        st.progress(progress)
        st.caption(f"Question {session.current_index + 1} of {len(session.questions)}")

        # Question Display
        st.markdown(f"### {q.question_text}")

        # Choices Form
        with st.form(key=f"form_{session_key}_{session.current_index}"):
            options = [f"{k}: {v}" for k, v in q.choices.items()]
            user_choice = st.radio("Select your answer:", options, index=None)
            submitted = st.form_submit_button("Submit Answer")

            if submitted:
                if user_choice:
                    selected_key = user_choice.split(":")[0]
                    session.user_answers[session.current_index] = selected_key
                    st.session_state[f"show_rationale_{session_key}"] = True
                else:
                    st.warning("Please select an answer.")

        # Rationale View
        if st.session_state.get(f"show_rationale_{session_key}"):
            selected_key = session.user_answers[session.current_index]
            is_correct = selected_key == q.correct_answer

            if is_correct:
                st.success(f"**Correct!** The answer is {q.correct_answer}")
                # Increment score only once per question
                if f"scored_{session_key}_{session.current_index}" not in st.session_state:
                    session.score += 1
                    st.session_state[f"scored_{session_key}_{session.current_index}"] = True
            else:
                st.error(f"**Incorrect.** You chose {selected_key}. The correct answer is {q.correct_answer}.")

            with st.expander("Show Rationale", expanded=True):
                st.write(q.rationale)

            if st.button("Next Question", key=f"next_{session_key}"):
                st.session_state[f"show_rationale_{session_key}"] = False
                session.current_index += 1

                if session.current_index >= len(session.questions):
                    session.completed = True
                    score_manager.save_score(selected_set, part_name, session.score, len(session.questions))

                st.rerun()