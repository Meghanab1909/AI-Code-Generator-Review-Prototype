import streamlit as st
import os
import tempfile
import pdfplumber
import litellm

litellm_params = {
    "model": "ollama/mistral",
    "api_base":"http://localhost:11434"
}

st.set_page_config(page_title="Test Model")
st.title("Code Generation Prototype")
st.write("Upload project-related documents for generating code.")

file = st.file_uploader("Choose a file 📂\n\n(Only one file can be uploaded at a time)", accept_multiple_files = False, type = ["pdf", ".docx"])

language = st.selectbox("Pick a language:", ["C", "C++", "Python", "Java"])

generate = st.button("🔄 Generate code")

def extract_text_from_pdf(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete = False, suffix = ".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        text = ""
        
        with pdfplumber.open(tmp_file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        os.remove(tmp_file_path)
        
        if not text:
            raise ValueError("No text could be extracted")
        
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""
    
def build_prompt(language: str, document_text: str) -> str:
    return f"""You are an expert {language} developer.

The following is a document that describes what the program should do:

\"\"\"
{document_text[:2000]}
\"\"\"

Based on this, write a complete {language} script that implements the described functionality.
- Do not include any explanation.
- Only return valid {language} code.
- The code must follow OPEN-SOURCE CODING STANDARDS.
- Do not use markdown or formatting.
- Assume the user wants working code based only on the document.
"""

def generate_code(prompt: str):
    try:
        response = litellm.completion(
            model = litellm_params["model"],
            base_url = litellm_params["api_base"],
            messages = [{"role": "user", "content": prompt}]
        )
        
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating code: {str(e)}"

if file and generate:
    if file.type == "application/pdf":
        document_text = extract_text_from_pdf(file)
    else:
        document_text = file.read().decode("utf-8")
    
    if not document_text.strip():
        st.error("No readable text found in the document")
    else:
        prompt = build_prompt(language, document_text)
        
        with st.spinner("Generating code . . ."):
            generated_code = generate_code(prompt)
        
        st.code(generated_code, language = "c")
