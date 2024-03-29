from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# Function to get completion using OpenAI's Chat API
def get_completion(prompt, model="gpt-3.5-turbo"):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt},
        ],
        model=model,
    )
    return chat_completion.choices[0].message.content


# Function to download content from a given URL
def download_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        return response.text  # Assuming the content is text-based, you can access it using response.text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the URL: {e}")
        return None


# Function to extract visible text from HTML content
def extract_visible_text(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        visible_text = soup.get_text()  # Get the visible text content using .get_text() method of BeautifulSoup
        return visible_text

    except Exception as e:
        print(f"An error occurred while extracting text: {e}")
        return None


# Function to summarize content from a given URL
def summarize_from_url(url):
    html_text = download_url(url)
    text = extract_visible_text(html_text)
    prompt = f"""
    Summarize the following text in 3 to 5 sentences using simple language that anyone can understand in English:
    {text}
    """
    response = get_completion(prompt)
    return response


# Function to get visible text from a given URL
def get_article_text(url):
    html_text = download_url(url)
    if html_text:
        content = extract_visible_text(html_text)
        return content
    else:
        return None  # Handle case where download or extraction fails


# Function to display PDF content from a given URL
def display_pdf_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        pdf_content = response.content
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        num_pages = pdf_document.page_count
        full_text = ""

        for page_num in range(num_pages):
            page = pdf_document.load_page(page_num)
            page_text = page.get_text("text")
            full_text += page_text

        pdf_document.close()
        return full_text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading the PDF: {e}")


# Function to summarize content from a given PDF URL
def summarize_from_pdf(url):
    pdf_text = display_pdf_content(url)
    prompt = f"""
    Summarize the following text in 3 to 5 sentences using simple language that anyone can understand in English:
    {pdf_text}
    """
    response = get_completion(prompt)
    return response


# Function to convert conversation history into a string
def convert_history(conversation_history):
    history_string = ""
    for message in conversation_history:
        history_string += f"{message['role']}: {message['message']}\n"

    return history_string


# Function to generate an answer using conversation history, article text, and a given question
def generate_answer(question, article_text, conversation_history):
    conversation_history = convert_history(conversation_history)
    prompt = f"""
    Conversation history: {conversation_history}
    Answer the question using the conversation history, given article, and your common knowledge.
    Given article: {article_text}
    Question: {question}
    Answer:
    """
    response = get_completion(prompt)
    return response.strip()
