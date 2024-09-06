import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the prompt for summarization
summary_prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

# Define the prompt for Q&A
qa_prompt = """You are a YouTube video transcript question answerer. Based on the provided transcript, answer the following question: """

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        st.error("Error extracting transcript. Please check the video URL.")
        return None

# Function to generate content using Google Gemini Pro
def generate_gemini_content(prompt, text):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + text)
    return response.text

# Streamlit app layout
st.title("YouTube Transcript to Detailed Notes Converter")

youtube_link = st.text_input("Enter YouTube Video Link:")
if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(summary_prompt, transcript_text)
        st.markdown("## Detailed Notes:")
        st.write(summary)

question = st.text_input("Enter your question:")
if st.button("Ask a Question"):
    if youtube_link and question:
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            # Combine the question with the transcript for context
            combined_prompt = f"{qa_prompt} {question}\nTranscript:\n{transcript_text}"
            answer = generate_gemini_content(combined_prompt, transcript_text)
            st.markdown("## Answer:")
            st.write(answer)
