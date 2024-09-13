import os

import streamlit as st
from guard.clients import GroqClient
from streamlit_ace import st_ace
from streamlit_theme import st_theme

st.set_page_config(
    layout="wide",
    page_icon="🔍",
    page_title="Vulnerability Explorer",
    menu_items={
        "Get Help": "https://github.com/codeguardai/explorer/issues",
        "Report a bug": "https://github.com/codeguardai/explorer/issues",
    },
)
st.title("Vulnerability Explorer")

# Ensure the Groq API key is set
if not os.environ.get("GROQ_API_KEY"):
    st.error(
        "Groq API key not found. Please set the 'GROQ_API_KEY' environment variable."
    )
    st.stop()

# Initialize the AI client using GroqClient from guard
ai_client = GroqClient("llama3-8b-8192")

LANGUAGE_DISPLAY_MAP = {
    "C": "c_cpp",
    "C++": "c_cpp",
    "C#": "csharp",
    "Go": "golang",
    "Python": "python",
    "JavaScript": "javascript",
    "Java": "java",
    "Ruby": "ruby",
    "PHP": "php",
    "Swift": "swift",
    "Kotlin": "kotlin",
    "HTML": "html",
    "CSS": "css",
    "TypeScript": "typescript",
    "JSON": "json",
    "Markdown": "markdown",
    "Elixir": "elixir",
    "Rust": "rust",
    "Erlang": "erlang",
}
available_languages = sorted(LANGUAGE_DISPLAY_MAP.keys())

# Set the Ace editor theme based on the base theme
theme = st_theme()
base_theme = (
    theme.get("base")
    if theme and isinstance(theme, dict) and "base" in theme
    else "dark"
)
ace_theme = "twilight" if base_theme == "dark" else "chrome"

# Initialize session state for the result if not already initialized
if "result" not in st.session_state:
    st.session_state["result"] = "Results will appear here."

# Default Python code snippet
default_python_code = """import os

def read_file(filepath):
    return open(filepath).read()

def login(user, pwd):
    if user == "admin" and pwd == "password123":
        print("Welcome!")
    else:
        print("Access denied!")

filepath = input("File path: ")
print(read_file(filepath))

user = input("Username: ")
pwd = input("Password: ")
login(user, pwd)
"""

# Define layout columns for input and results
input_column, result_column = st.columns(2)

with input_column:
    st.header("📝 Input Code")

    display_language = st.selectbox(
        "Choose Language:",
        available_languages,
        index=available_languages.index("Python"),
    )
    ace_language = LANGUAGE_DISPLAY_MAP[display_language]

    # Code editor with syntax highlighting using st_ace
    code_input = st_ace(
        value=default_python_code if display_language == "Python" else "",
        placeholder="Enter your code here...",
        language=ace_language,
        theme=ace_theme,
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        show_gutter=True,
        wrap=False,
        auto_update=True,
        min_lines=20,
        key="ace_editor",
    )

    evaluate = st.button("Evaluate")

st.markdown(
    """
    <style>
    .scrollable-container {
        max-height: 100vh;
        overflow-y: auto;
        padding: 1em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with result_column:
    st.header("🔍 Analysis")

    if evaluate:
        if code_input.strip() == "":
            st.warning("Please enter some code before evaluating.")
        else:
            with st.spinner("Analyzing code..."):
                try:
                    code_with_language = f"Language: {display_language}\n{code_input}"
                    result = ai_client.scan_code(code_with_language)
                    st.session_state["result"] = result
                except Exception as e:
                    st.session_state["result"] = f"An error occurred: {e}"

    st.markdown(
        f'<div class="scrollable-container">{st.session_state["result"]}</div>',
        unsafe_allow_html=True,
    )
