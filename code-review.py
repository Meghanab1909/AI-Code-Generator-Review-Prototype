import streamlit as st
import os
import tempfile
import pdfplumber
import litellm
from pathlib import Path
import difflib

litellm_params = {
    "model": "ollama/mistral",
    "api_base":"http://localhost:11434"
}

st.set_page_config(page_title="Test Model")
st.title("Code Review Prototype")

SUPPORTED_EXTENSIONS = ['.py', '.java', 'c', 'cpp']

root = st.text_input("Enter root directory path:","")

review = st.button("🚀 Review")

file_codes = {}

def extract_codes(root):
    if root:
        root_dir = Path(root)
        
        if root_dir.exists() and root_dir.is_dir():
            st.success(f"Scanning directory {root_dir}")
            
            code_files = [i for i in root_dir.rglob("*") if i.suffix in SUPPORTED_EXTENSIONS]
            
            st.write(f"🔍 Found {len(code_files)} code files")
            
            for i in code_files:
                try:
                    with open(i, "r", encoding = "utf-8") as f:
                        file_codes[i] = f.read()
                except Exception as e:
                    st.warning(f"Could not read {i}: {e}")
                    
def build_prompt(codes: dict) -> str:
    combined_code = "\n\n".join(
        f"--- File: {filename} ---\n{content}" for filename, content in codes.items()
    )
    
    print(combined_code)
    
    return f"""You are an expert software engineer and code reviewer.

Your task is to carefully review the following code files and provide a detailed but concise and simple analysis in a easy to understand manner.

Analyze the code based on the following:
- Functional similarities or duplicate logic across files. Mention the function names where the similarities or duplicate logic is observed. 

Do **not** modify the code. Just return a well-structured conclusion summarizing your observations, insights and optimization techniques IN A SIMPLE AND EASY TO UNDERSTAND MANNER. 

Here are the code files:

\"\"\"
{combined_code}
\"\"\"
"""

def review_code(prompt: str):
    try:
        response = litellm.completion(
            model = litellm_params["model"],
            base_url = litellm_params["api_base"],
            messages = [{"role": "user", "content": prompt}]
        )
        
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating code: {str(e)}"

if root and review:
    extract_codes(root)
    
    prompt = build_prompt(file_codes)
        
    with st.spinner("Analyzing . . ."):
        analysis = review_code(prompt)
        
    st.markdown(analysis)
