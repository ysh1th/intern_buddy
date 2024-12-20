import requests
from dotenv import load_dotenv
import os

maxtokens = 100

load_dotenv()  # Loads environment variables from .env file
PERPLEX_API = os.getenv("PERPLEX_API")
if not PERPLEX_API:
    raise ValueError("API key is missing!")

def generate_behavioral_questions(user_skills, job_requirements, job_title):
    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {PERPLEX_API}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"The user has the following skills: {', '.join(user_skills)}.\n"
        # f"the internship job title is this: {job_title}\n"
        f"The internship job requires: {', '.join(job_requirements)}.\n"
        f"Create a concise behavioral interview question based on this information.\n"
        f"You can choose from different types of questions such as situational, experience-based, or skill-based.\n"
        f"Be creative and vary the style of the question each time.\n"
        f"Only respond with question\n"
        f"ensure it is relevant and engaging."
    )
    
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "system", "content": "Be precise and concise."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": maxtokens,
        "temperature": 0.5,
        "top_p": 0.9,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }

    
    response = requests.post(url, headers=headers, json=payload)
    

    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0].get("message", {}).get("content", "No content found")
    else:
        print(f"Error at behavior q: {response.status_code}, {response.text}\n")
        return None
    

# Function to analyze response and generate a follow-up question
def generate_follow_up_question(user_response, initial_question):
    url = "https://api.perplexity.ai/chat/completions"
    
    # Combine the user's response and the initial question into a prompt
    prompt = (
        f"Analyze the following response to the question: {initial_question}\n"
        f"User's response: {user_response}\n"
        f"Based on the analysis, create one follow-up question to probe further.\n"
        f"only respond with the question."
    )

    headers = {
        "Authorization": f"Bearer {PERPLEX_API}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "system", "content": "Be analytical, constructive and precise."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": maxtokens,
        "temperature": 0.6,
        "top_p": 0.9,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }
    

    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0].get("message", {}).get("content", "No content found")
    else:
        print(f"Error at behavior q: {response.status_code}, {response.text}\n")
        return None

def response_analysis(
        job_requirements,
        first_question,
        first_response,
        follow_up_question,
        follow_up_response
    ):

    url = "https://api.perplexity.ai/chat/completions"
    
    # Combine the user's response and the initial question into a prompt
    prompt = (
        f"You are an interview evaluator analyzing behavioral responses. The user has answered:\n"
        f"1. An initial question.\n"
        f"2. A follow-up question based on their first response.\n"

        f"Evaluate the user's performance using these criteria:\n"
        f"- Clarity: Was the response clear and well-structured?\n"
        f"- Relevance: Did it address the question and align with the job requirements?\n"
        f"- Depth: Were specific examples and details provided?\n"
        f"- Skills Demonstrated: What skills were evident in the response?\n"
        f"- Suggestions: Offer actionable feedback for improvement.\n"

        f"Details:\n"
        f"- Job Requirements: {job_requirements}\n"
        f"- Initial Question: {first_question}\n"
        f"- User's Response: {first_response}\n"
        f"- Follow-Up Question: {follow_up_question}\n"
        f"- Follow-Up Response: {follow_up_response}\n"

        f"Respond very concisely in the above:"

    )

    headers = {
        "Authorization": f"Bearer {PERPLEX_API}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {"role": "system", "content": "Be analytical, constructive and precise."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0.6,
        "top_p": 0.9,
        "search_domain_filter": ["perplexity.ai"],
        "return_images": False,
        "return_related_questions": False,
        "search_recency_filter": "month",
        "top_k": 0,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1
    }
    

    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0].get("message", {}).get("content", "No content found")
    else:
        print(f"Error at behavior q: {response.status_code}, {response.text}\n")
        return None
# Example usage
# Retrieve from database
# user_response = "I managed a team of 5 to develop a web application within a tight deadline."
# initial_question = "Can you share an experience where you demonstrated leadership skills?"

# follow_up_question = generate_follow_up_question(user_response, initial_question)
# print(f"Follow-up question: {follow_up_question}")
