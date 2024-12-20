import streamlit as st
import openai
import markdown
import google.generativeai as genai
from transformers import pipeline
from PyPDF2 import PdfReader
from docx import Document

st.set_page_config(page_title="Markitdown Lib")

st.title("Markdown Conversion")

project_id = st.sidebar.text_input("Enter Project ID", type="default")
location = st.sidebar.text_input("Enter Location", type="default")
api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
gemini_api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")
meta_model_path = st.sidebar.text_input("Enter Meta AI (LLaMA) Model Path", type="default")

uploaded_file = st.file_uploader("Choose a File", type=["txt", "pdf", "docx"])

if st.button("Process File"):
    if not uploaded_file:
        st.error("Error: No file uploaded!")
    else:
        with st.spinner("Processing File..."):
            file_extension = uploaded_file.name.split(".")[-1]
            if file_extension == "txt":
                file_content = uploaded_file.read().decode("utf-8")
            elif file_extension == "pdf":
                pdf_reader = PdfReader(uploaded_file)
                file_content = " "
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        file_content += text
            elif file_extension == "docx":
                doc = Document(uploaded_file)
                file_content = " "
                for paragraph in doc.paragraphs:
                    file_content += paragraph.text
                
            else:
                st.error("Unsupported file type!")
                st.stop()

            st.subheader("Original Content:")
            st.text_area("Original File Content:", file_content, height=200)

            st.subheader("Markdown Content:")
            markdown_content = markdown.markdown(file_content)
            st.text_area("Markdown Converted Content:", markdown_content, height=200)

            llm_option = st.selectbox("Select any LLM:", ["OpenAI (GPT)", "Gemini", "Meta AI (LLaMA)"])

            if llm_option == "OpenAI (GPT)":
                if not api_key:
                    st.error("Missing OpenAI API Key")
                elif st.button("Summarize with OpenAI GPT"):
                    openai.api_key = api_key
                    try:
                        result = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "Summarize the content."},
                                {"role": "user", "content": markdown_content},
                            ],
                            max_tokens=200,
                            temperature=0.7,
                        )
                        summary = result.choices[0].message.content.strip()
                        st.subheader("SUMMARY")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"Error with OpenAI GPT: {e}")

            elif llm_option == "Gemini":
                if not gemini_api_key:
                    st.error("Missing Gemini API Key")
                elif st.button("Summarize with Gemini"):
                    genai.configure(api_key=gemini_api_key)
                    model = genai.GenerativeModel("gemini-v1")
                    try:
                        response = model.generate_content(f"Summarize the content:\n\n{markdown_content}")
                        summary = response.text.strip()
                        st.subheader("SUMMARY")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"Error with Gemini: {e}")

            elif llm_option == "Meta AI (LLaMA)":
                if not meta_model_path:
                    st.error("Missing Meta AI (LLaMA) model path")
                elif st.button("Summarize with Meta AI (LLaMA)"):
                    try:
                        summarizer = pipeline("summarization", model=meta_model_path)
                        result = summarizer(markdown_content, max_length=200, min_length=30, do_sample=False)
                        summary = result[0]['summary_text']
                        st.subheader("SUMMARY")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"Error with Meta AI (LLaMA): {e}")

savess