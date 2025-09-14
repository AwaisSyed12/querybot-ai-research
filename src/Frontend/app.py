import requests
from bs4 import BeautifulSoup
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Retrieve the Google API key securely
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Google API key not found. Please create a .env file with GOOGLE_API_KEY=your_key_here")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

extracted_filename = "extracted_data.txt"

def create_vector_db(urls):
    with open(extracted_filename, "w", encoding="utf-8") as file:
        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                extracted_text = soup.get_text().replace('\n', ' ').replace('\t', ' ')
                file.write(extracted_text + " ")
            except Exception as e:
                st.sidebar.error(f"Failed to process {url}: {e}")
    st.sidebar.success(f"Data extracted and saved to '{extracted_filename}'.")

def get_answer(query):
    try:
        with open(extracted_filename, "r", encoding="utf-8") as file:
            data = file.read()

        prompt = f"""
        Based on the following context, please provide a detailed answer to the question posed. Use information only from the context provided and do not include any external knowledge or assumptions.

        CONTEXT:
        {data}

        QUESTION:
        {query}

        Answer:
        """

        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except FileNotFoundError:
        return "Error: The extracted data file does not exist. Please process the URLs first."
    except Exception as e:
        return f"An error occurred: {str(e)}"

st.set_page_config(page_title="QueryBot: AI Research", page_icon=":bar_chart:", layout="wide")
st.title("QueryBot: AI Research 📈")
st.markdown("Automated AI-powered tool for extracting, analyzing, and summarizing insights from web articles.")

with st.sidebar:
    st.header("⚡ Article URLs")
    test_urls = [
        "https://www.moneycontrol.com/news/business/markets/wall-street-rises-as-tesla-soars-on-ai-optimism-11351111.html",
        "https://github.com/resources/articles/ai/what-are-ai-agents"
    ]
    url1 = st.text_input("URL 1", value=test_urls[0])
    url2 = st.text_input("URL 2", value=test_urls[1])
    process_url_clicked = st.button("Process URLs")
    if process_url_clicked:
        with st.spinner("Extracting and processing URLs..."):
            create_vector_db([url1, url2])

st.markdown("---")
st.subheader("🔎 Ask a Question")
query = st.text_input("Enter your query:", placeholder="e.g. What are AI agents?")
get_answer_clicked = st.button("Get Answer")

if get_answer_clicked:
    if query:
        with st.spinner("Generating AI answer..."):
            answer = get_answer(query)
        st.markdown("#### 📄 **Answer:**")
        st.write(answer)
    else:
        st.warning("⚠️ Please enter a query to get an answer.")