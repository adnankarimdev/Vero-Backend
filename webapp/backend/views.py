from django.http import HttpResponse
import os
from dotenv import load_dotenv
import re
import json
import hashlib
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import pickle

# from langchain.vectorstores import FAISS
# from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from .serializers import (
    UserSerializer,
    UserDataSerializer,
    ReviewsToPostLaterSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from .models import UserData, CustomerReviewInfo, ReviewsToPostLater
import jwt
import secrets
import googlemaps
import requests
from django.conf import settings
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from token_count import TokenCount
from datetime import datetime
from backend.scheduler import scheduler
import pytz
from twilio.rest import Client

stop_words = [
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "s",
    "t",
    "can",
    "will",
    "just",
    "don",
    "should",
    "now",
]
load_dotenv()
os.environ["OPENAI_API_KEY"] = (
    "sk-proj-BkqMCfMCu8aJz0M19aj9T3BlbkFJCqFGN85AiM1NP2lJyrF1"
)
SENDGRID_API = "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"
MAILGUN_API = "f29f9a6ae5692803b6ff2d2795b4e1da-826eddfb-d93e3829"
faiss_index_path = "/Users/adnankarim/Desktop/DevTipsNotes/PersonalProjects/GoogleReviewDashboard/GoogleReviewDashboardBackend/scripts/faiss_index_p&s"
documents_path = "/Users/adnankarim/Desktop/DevTipsNotes/PersonalProjects/GoogleReviewDashboard/GoogleReviewDashboardBackend/scripts/faiss_documents_p&s.pkl"

ACCOUNT_SSID_TWILIO = "AC506ded0e4eedc8c96d4ef37cce931320"
AUTH_TOKEN_TWILIO = "461a27a99fc2c064264a70d9ebbb0582"
TWILIO_NUMBER = "+15873172396"
# embeddings = OpenAIEmbeddings()

SECRET_KEY = secrets.token_urlsafe(32)

google_email_app_password = "jmym xiii qzgc qnhc"
google_email_reviews_app_password = "jziu dafb uzex otqm"
google_email_concerns_app_password = "gcir oozn qkju ryzw"
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

tc = TokenCount(model_name="gpt-4o-mini")

prompt_review_score = """
You are to evaluate the helpfulness of a given review based on the following criteria:
	1.	Informative and Insightful (20%)
	•	High Score: The review is specific, relevant, and offers valuable insights about the place, describing what other visitors are likely to experience. It highlights what makes the place special and shares unique and new information.
	•	Moderate Score: The review provides some relevant details but lacks depth or fails to introduce something unique or new.
	•	Low Score: The review is vague, generic, or fails to provide specific information that would be helpful to other visitors.
	2.	Authenticity (20%)
	•	High Score: The review accurately reflects the reviewer’s own experience, including both positive and negative aspects. The reviewer is honest and specific about the service and the place.
	•	Moderate Score: The review is generally authentic but may lack specific details or balance between positive and negative aspects.
	•	Low Score: The review appears exaggerated, biased, or lacks honesty and specificity regarding the reviewer’s experience.
	3.	Respectfulness (20%)
	•	High Score: The review is constructive, even in criticism, and avoids profanity. The feedback is respectful and considerate of how business owners might use the information to improve their offerings.
	•	Moderate Score: The review is generally respectful but may contain mildly harsh language or criticism that is not fully constructive.
	•	Low Score: The review contains disrespectful language, harsh criticism, or profanity, making it unhelpful for business improvement.
	4.	Writing Style (20%)
	•	High Score: The review is well-written, with proper spelling and grammar. The reviewer avoids excessive capitalization and punctuation, and the length of the review is appropriate (e.g., a paragraph).
	•	Moderate Score: The review is understandable but may contain minor spelling or grammatical errors. The writing style is acceptable but could be improved for clarity or professionalism.
	•	Low Score: The review contains significant spelling or grammatical errors, excessive capitalization, or punctuation, making it difficult to read or less professional.
	5.	Privacy and Professionalism (10%)
	•	High Score: The review does not include personal or professional information, such as phone numbers or URLs of other businesses. The reviewer does not write reviews for places where they are currently or were formerly employed.
	•	Moderate Score: The review may slightly breach privacy or professionalism guidelines, but the issues are minor.
	•	Low Score: The review includes personal or professional information or violates the policy of not reviewing places of employment.
	6.	Focus on Experience (10%)
	•	High Score: The review focuses on the reviewer’s firsthand experience with the place, avoiding general commentary on social or political issues. It stays relevant to the location and does not engage in broader debates.
	•	Moderate Score: The review is mostly focused on the experience but may include minor general commentary or irrelevant information.
	•	Low Score: The review shifts focus away from the firsthand experience, including significant general commentary or unrelated topics.

    Instructions:

	•	Assess each review based on these criteria to determine its overall helpfulness, authenticity, and relevance.
	•	Combine the scores for a thoughtful and nuanced total score out of 100, taking into account the overall impact, balance, and importance of each criterion.
	•	Do not simply sum the scores; instead, weigh the overall quality of the review in determining the final score.
	•	Return only the total score, the number only.
	•	Do not include any other text, explanations, or output—only the total score.
"""

prompt = """
You are to analyze data for ALL locations you read unless otherwise specified and return graphs . Graphs must have relevant titles and data. Return ONLY the exact format specified below, with no additional text or explanations. Use react-chartjs-2 charts (BarChart, PieChart, LineChart, DoughnutChart, RadarChart, PolarAreaChart, BubbleChart, or ScatterChart). Fill out all data directly in the graph. Specify ALL details regarding location, rating, body, and date.
Output format:
<Card>
<CardHeader>
<CardTitle>[Title]</CardTitle>
<CardDescription>[Description]</CardDescription>
</CardHeader>
<CardContent>
<div className="space-y-4">
<div className="h-64">
<[ChartType] data={{
labels: [...],
datasets: [{
label: '...',
data: [...],
backgroundColor: [...],
borderColor: [...],
borderWidth: 1,
}]
}} options={{...}} />
</div>
</div>
</CardContent>
</Card>
Respond ONLY with this format, populated with relevant data based on the query. If a query cannot be graphed, create a closely related query that can be graphed and use that instead.

User Query: 
"""

prompt_review_adjuster = """
    Task: Transform the provided review into a polished Google review.
    
    Guidelines:

        •	Maintain the original tone and key message of the review—do not alter the point or criticism of the review.
        •	You can alter the text, but it must keep the same core point of the message.
        •	Your response should consist solely of the completed Google review.
        •   Be informative and insightful: Be specific and relevant to the place you’re reviewing, and describe what other visitors are likely to experience. Highlight what makes the place special, and try to share something unique and new. 
        •   Be authentic: Review your own experience, and explain what the place was like and the service you received. Try to be as accurate as possible, and include both the positive and negative aspects of your visit.
        •   Be respectful: Business owners often use feedback to improve their offerings. Even if you’re frustrated, make sure your criticism is constructive. Additionally, please avoid profanity.
        •   Write with style: Check your spelling and grammar, and avoid excessive capitalization and punctuation. In general, a paragraph is a great length for a review. 
        •   Avoid personal and professional information: Do not include the phone numbers or URLs of other businesses in your reviews. Additionally, do not write reviews for places where you are currently or formerly, an employee.
        •   Avoid general commentary: Certain locations may become the subject of larger public debate or conversation due to recent news coverage or current events. While we respect and value your opinion, Local Reviews are not meant for social or political commentary. Forums, like blogs or social networks, are much more appropriate for those types of conversations. Please write about your firsthand experience with the place and not general commentary on the place in relation to recent news.
        •   You are to ONLY return the review body you have generated. No stars, just the new review you have created.
    """
#  •	Where appropriate and natural, incorporate the following business keywords: [latte, best coffee shop, artisan].

# cant stuff keywords in, limit to only 2. Might have to remove outright. Search engines see keyword stuffing.
prompt_review_five_star_creator = """
Task: Transform the provided user badges selected for each section for a [review rating] review into a polished Google review. The buisness name will also be provided that you will be generating a review for. Finally, the keywords that are important to the buisness will be provided as well. You are to only put 2 keywords at a maximum if it goes in naturally.
    
You are to create a google review based on the following criteria:
	1.	Informative and Insightful (16%): Specific and valuable; unique insights.
	2.	Authenticity (16%): Honest, detailed reflection of the experience.
	3.	Integration of Keywords (10%): Relevant keywords used naturally.
	4.	Respectfulness (16%): Constructive, respectful, and avoids profanity.
	5.	Writing Style (16%): Well-written, correct grammar and spelling.
	6.	Privacy and Professionalism (10%): No personal or professional info; no conflict of interest.
	7.	Focus on Experience (10%): Focused on personal experience; avoids irrelevant commentary.

Instructions:
- Return only the review body.
- You can only put a MAXIMUM of 2 keywords in the review body.
- Make it first person. It should NOT sound generated. It should include first person language like 'I' and second person language like 'you'. Use it correctly where it makes sense.
- Do not include any emojis even if the badges have emojis.
- Do not include any other text, explanations, or output—only the review body.
- Vary the opening sentence for each review. Avoid always starting with "I recently visited..." Use a diverse range of opening structures.
- Aim for a high uniqueness score. Each review should have a distinct voice and structure.
- Vary the length of the review. Aim for between 50-150 words, but let it flow naturally.

Opening sentence examples (use these for inspiration, not verbatim):
- "What a pleasant surprise..."
- "If you're looking for..."
- "My experience at [Business Name] was..."
- "From the moment I walked in..."
- "I've been a regular at [Business Name] for..."
- "Let me tell you about my visit to..."

    """

prompt_address_email = """
You are a customer service representative for [Buisness Name]. You have received a negative review from a customer, and you want to craft a personalized response based on the details provided. Below is the review and the customer’s answers to specific questions you asked. Use this information to write a thoughtful and empathetic response.

Review:

[Insert the negative review text here and/or User Review Selected Badges.]

Customer’s Answers to Questions:

	1.	What specific issue did you experience?
[Insert customer’s answer here.]
	2.	How did this issue affect your visit?
[Insert customer’s answer here.]
	3.	Was there anything that you think could have improved your experience?
[Insert customer’s answer here.]
	4.	Do you have any suggestions for how we can avoid similar issues in the future?
[Insert customer’s answer here.]

Response Requirements:

	1.	Acknowledge the specific issue the customer experienced and show understanding of their frustration.
	2.	Apologize sincerely for the inconvenience caused.
	3.	Explain any actions you are taking to address the issue or improve.
	4.	Thank the customer for their feedback and invite them to provide more details if they wish.
	5.	Offer a resolution or compensation if specified in the input data. Give exactly what is specified.
    6.  If the answers to the questions are not specified, ask constructive questions for follow ups to try and get constructive feedback.

Input Format:
  Buisness Name: <buisness_name>
  Name: <name_of_customer_you_are_addressing>
  Negative Review Text: <review_body>
  User Review Selected Badges: <badges_selected_by_user>

Response Example:

“Dear [Customer’s Name],

Thank you for taking the time to share your feedback. We are genuinely sorry to hear about your recent experience at [Buisness Name]. We understand that [specific issue] was a significant inconvenience, and we deeply apologize for not meeting your expectations.

From your answers, we see that [specific issue] affected your visit by [how it affected their visit]. We appreciate your suggestion of [suggestion for improvement] and are taking steps to address this issue to prevent it from happening in the future.

Thank you for bringing this to our attention. Your feedback is invaluable in helping us improve our service. If you have any more details or further suggestions, please feel free to reach out to us directly. As a token of our appreciation and to make up for the inconvenience, we would like to offer you [mention any compensation or resolution].

We hope to have the opportunity to serve you better in the future.

Sincerely,
[Buisness Name]

Note:
NEVER SEND THE RESPONSE EXAMPLE!
"""

prompt_review_template_generator = """
Generate a Google review template based on the following data:

	•	Business Name: <name of business>
	•	User Rating: <rating out of 5>
	•	Questions Answered: <list of questions>

    The review template should allow the user to fill in specific parts of the text, such as “[write what you thought]” in places where the user’s personal experience should be described.
Instructions:

	1.	Tailor the review to reflect the specific business name provided.
	2.	Align the tone of the review with the rating:
	•	For a 1-star review: Provide constructive criticism that addresses the concerns while aiming for an overall positive tone.
	•	For a 5-star review: Highlight positive aspects and express satisfaction.
	3.	The review should always aim for a high score based on the following criteria:
	1.	Informative and Insightful (20%):
	•	The review should be specific, relevant, and offer valuable insights about the place, describing what other visitors are likely to experience. It should highlight what makes the place special and share unique and new information.
	2.	Authenticity (20%):
	•	The review must accurately reflect the reviewer’s own experience, including both positive and negative aspects. The reviewer should be honest and specific about the service and the place.
	3.	Respectfulness (20%):
	•	The review should be constructive, even in criticism, and avoid profanity. The feedback must be respectful and considerate of how business owners might use the information to improve their offerings.
	4.	Writing Style (20%):
	•	The review should be well-written, with proper spelling and grammar. Avoid excessive capitalization and punctuation, and keep the review length appropriate (e.g., a paragraph).
	5.	Privacy and Professionalism (10%):
	•	The review should not include personal or professional information, such as phone numbers or URLs of other businesses. The reviewer must not write reviews for places where they are currently or were formerly employed.
	6.	Focus on Experience (10%):
	•	The review should focus on the reviewer’s firsthand experience with the place, avoiding general commentary on social or political issues. It should stay relevant to the location and not engage in broader debates.

Important: Only return the review template BODY and nothing else.

Here is the data:
"""
prompt_review_question_generator = """

Before generating questions, perform an internet search using the location name to determine the industry or type of business. If an industry is identified, align the questions accordingly. If no specific location is provided, create focused questions that still meet the above criteria.
--------

Generate me 3 specific questions for someone who is about to leave a 1, 2, 3, or 4-star review. These questions should be aligned with their reasoning for the review, industry-relevant, and tailored to their experience. Make the questions extremely specific to avoid generality but do not mention the specific locations. 

Return it in this format where questions are a key in JSON:
questions: [ {id:1, questions:[]}, {id:2, questions:[]}, {id:3, questions:[]}, {id:4, questions:[]}]

NOTE: Just return the key with the values and nothing else.

Here is the data: which will give insight into what type of business it is and areas to focus on. If no specific area is provided, create your own relevant questions using the rules above:
"""

# Try to adjust query so its song names/lyrics for spotify platform. Will need to adjust accordingly, probs create a whole new prompt.
prompt_five_star_categories_generator = """
Generate EXACTLY 4 badges for each rating based on the overall rating of my business. To start, give me the top 3 most important factors for customers. Then, fill out badges relevant to the overall rating. No badges should have the same meaning.

For ratings:

	•	1 star: Badges should focus on collecting detailed feedback about severe issues or major concerns. Examples: “service was terrible 😡”, “product quality was unacceptable 😠”.
	•	2 stars: Badges should address significant issues and gather feedback on notably problematic aspects. Examples: “staff were unhelpful 😕”, “experience was disappointing 😞”.
	•	3 stars: Badges should gather feedback on areas of moderate concern or dissatisfaction. Examples: “ambiance could be improved 😐”, “service was slow ⏳”.
	•	4 stars: Badges should collect constructive feedback on minor issues or areas for improvement. Examples: “menu options could be better 🧐”, “cleanliness was lacking 🧹”.
	•	5 stars: Badges should celebrate positive feedback and gather information on what aspects were most satisfying. Examples: “excellent service 😊”, “great atmosphere 🌟”.

Badges should be short statements, not questions, and should include an emoji that represents the badge at the end of the sentence. Do not include any sentence enders. Make them as specific as possible.

Return it in this format where categories is a key in json. Don't include any random white spaces.:
{
  "categories": [
    {
      "name": "Your Rating",
    "badges": [
      { "rating": 1, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 2, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 3, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 4, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 5, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] }
    ]
    }
  ]
}

NOTE: Just return the key with the values and nothing else. 

Here is the data: which will give insight in terms of what buisness I am. Please search the internet for what buisness i am, if I don't exist, then find relevant buisnesses based on my buisness name to narrow down.

"""
prompt_five_star_multiple_categories_generator = """
Generate EXACTLY 4 badges for each name for my business. To start, give me the top 3 most important factors of my business for customers. Then, fill out badges relevant to that factor. No badges should have the same meaning. 

For ratings:

	•	1 star: Badges should focus on collecting detailed feedback about severe issues or major concerns. Examples: “service was terrible 😡”, “product quality was unacceptable 😠”.
	•	2 stars: Badges should address significant issues and gather feedback on notably problematic aspects. Examples: “staff were unhelpful 😕”, “experience was disappointing 😞”.
	•	3 stars: Badges should gather feedback on areas of moderate concern or dissatisfaction. Examples: “ambiance could be improved 😐”, “service was slow ⏳”.
	•	4 stars: Badges should collect constructive feedback on minor issues or areas for improvement. Examples: “menu options could be better 🧐”, “cleanliness was lacking 🧹”.
	•	5 stars: Badges should celebrate positive feedback and gather information on what aspects were most satisfying. Examples: “excellent service 😊”, “great atmosphere 🌟”.

Badges should be short statements, not questions, and should include an emoji that represents the badge at the end of the sentence. Do not include any sentence enders. Make them as specific as possible.

Return it in this format where categories is a key in json. Don't include any random white spaces.:
{
  "categories": [
    {
      "name": "<factor_1>",
    "badges": [
      { "rating": 1, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 2, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 3, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 4, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 5, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] }
    ]
    },
    {
      "name": "<factor_2>",
    "badges": [
      { "rating": 1, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 2, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 3, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 4, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 5, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] }
    ]
    },
    {
      "name": "<factor_3>",
    "badges": [
      { "rating": 1, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 2, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 3, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 4, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] },
      { "rating": 5, "badges": ["badge 1", "badge 2", "badge 3", "badge 4"] }
    ]
    }
  ]
}

NOTE: Just return the key with the values and nothing else. 

Here is the data: which will give insight in terms of what buisness I am. Please search the internet for what buisness i am, if I don't exist, then find relevant buisnesses based on my buisness name to narrow down.

"""

prompt_review_analyzer = """
 
You will receive a review body, the review rating (from 1 to 5), and the time it took to write the review (in seconds). Your task is to analyze the review and determine any improvements that the business could make. Your output should be the following structure:
{
  "score": [1-10],
  "reasoning": "[Detailed recommendations for business improvements based on the review criteria above]",
  "emotion": "[One word based on review body: happy, sad, angry, etc.]",
  "tone": "[One word based on review body: formal, casual, balanced, etc.]"
}
---

**Input Format**:
- Review body: [Text of the review]
- Rating: [1 to 5]

**Output Example**:

{
  "score": 8,
  "reasoning": "The review highlighted issues with slow service and unhelpful staff. The business could improve by training staff to be more responsive and efficient. Additionally, addressing the reviewer's concern about product quality could enhance overall customer satisfaction.",
  "emotion": "happy",
  "tone": "balanced"
}
Note: if the review lacks specific details, for the reasoning field, just write "Cannot provide suggestions due to lack of details provided by the customer.".

RETURN ONLY THE SPECIFIED OUTPUT MENTIONED.
---

"""

prompt_keyword_generator = """
 
You are an expert in search engine optimization (SEO) and keyword analysis. I need to find the top keywords related to a business's Google Maps presence. Please follow these instructions based on the information available:

1. **If a website URL is provided**, analyze the website and provide a list of the top keywords that are relevant for Google Maps searches.

   Website URL: [Insert Website URL Here]

2. **If no website URL is provided**, make educated guesses based on the business name and any tags associated with the business. Provide a list of the top keywords that would be relevant for Google Maps searches based on this information.

   Business Name: [Insert Business Name Here]
   Tags: [Insert Tags Here]

Keywords should not contain the buisness name. Instead, they should be general terms that users search. For example, "best coffee calgary" would be a vital keyword for a cofee shop. Also, add other keywords you feel would be extremely beneficial to the buisness for SEO. Provide your response as a list of keywords. Your output should be the following structure:

{
  "keywords": [keywords_you_found],
}


---

**Input Format**:
- Website URL: [Buisness website urls]
- Buisness Name: [Buisness Names]
- Tags: [Buisness Tags]

**Output Example**:

{
  "keywords": [
  "Coffee roasters Calgary",
  "Local coffee shop Calgary",
  "Phil & Sebastian coffee locations",
  "Specialty coffee Calgary",
  "Direct trade coffee Calgary",
  "Coffee subscriptions Calgary",
  "Calgary coffee delivery",
  "Espresso bar Calgary"
]
}

RETURN ONLY THE SPECIFIED OUTPUT MENTIONED.
---

"""

env_customer_url = os.environ.get("ENV_CUSTOMER_URL")


@csrf_exempt
def get_reviews_by_client_ids(request):
    client_ids = request.GET.getlist(
        "clientIds[]"
    )  # Get the list of client IDs from the query parameters
    if not client_ids:
        return JsonResponse({"error": "No client IDs provided"}, status=400)

    # Query the database
    reviews = CustomerReviewInfo.objects.filter(place_id_from_review__in=client_ids)

    # Serialize the data
    data = list(reviews.values())

    return JsonResponse(data, safe=False)


@csrf_exempt
def get_place_details(request, place_id):
    # Ensure you have your API key in your settings
    google_maps_api_key = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={google_maps_api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(data)


@csrf_exempt
def generate_categories(request):
    global prompt_five_star_categories_generator
    global prompt_five_star_multiple_categories_generator
    tokens = tc.num_tokens_from_string(prompt_five_star_categories_generator)
    print(f"GEN CATGORIES INPUT: Tokens in the string: {tokens}")

    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_query = data.get("context", "")
        user_radio_type = data.get("type", "")
        print(user_query)
        print(user_radio_type)

        # Messages for the LLM
        if user_radio_type == "overall":
            prompt_to_use = prompt_five_star_categories_generator
        else:
            prompt_to_use = prompt_five_star_multiple_categories_generator

        messages = [
            ("system", prompt_to_use),
            ("human", user_query),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(f"GEN CATGORIES OUTPUT: Tokens in the string: {tokens}")
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def generate_five_star_review(request):
    global prompt_review_five_star_creator
    tokens = tc.num_tokens_from_string(prompt_review_five_star_creator)
    print(f"GEN 5 STAR REVIEW INPUT: Tokens in the string: {tokens}")
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        print("review data", data)
        user_query = data.get("context", "")
        print(user_query)

        # Messages for the LLM
        messages = [
            ("system", prompt_review_five_star_creator),
            ("human", user_query),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(f"GEN 5 STAR REVIEW OUTPUT: Tokens in the string: {tokens}")
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def generate_review_questions(request):
    global prompt_review_question_generator
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_query = data.get("context", "")
        print(user_query)

        # Messages for the LLM
        messages = [
            ("system", prompt_review_question_generator),
            ("human", user_query),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def generate_review_template(request):
    global prompt_review_template_generator
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_query = data.get("context", "")
        print(user_query)

        # Messages for the LLM
        messages = [
            ("system", prompt_review_template_generator),
            ("human", user_query),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def get_place_id_by_email(request, email):
    if request.method == "GET":
        try:
            settings = UserData.objects.get(user_email=email)
            place_ids_as_array = (
                json.loads(settings.place_ids) if settings.place_ids else []
            )
            website_urls_as_array = (
                json.loads(settings.website_urls) if settings.website_urls else []
            )
            in_location_urls_as_array = (
                json.loads(settings.in_location_urls)
                if settings.in_location_urls
                else []
            )
            data = {
                "placeIds": place_ids_as_array,
                "places": settings.places_information,
                "websiteUrls": website_urls_as_array,
                "locationUrls": in_location_urls_as_array,
            }
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse(
                {"error": "Settings not found for the specified placeId."}, status=404
            )
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


@csrf_exempt
def get_review_questions(request, place_id):
    place_ids_list = place_id.split(",")  # Convert place_id to a JSON-encoded string
    if request.method == "GET":
        try:
            all_user_data = UserData.objects.all()
            matching_settings = [
                user_data
                for user_data in all_user_data
                if any(pid in json.loads(user_data.place_ids) for pid in place_ids_list)
            ]
            settings = settings = matching_settings[0]
            data = {
                "emailIntro": settings.email_intro,
                "emailSignature": settings.email_signature,
                "emailBody": settings.email_body,
                "emailAppPassword": settings.email_app_password,
                "clientEmail": settings.client_email,
                "worryRating": settings.worry_rating,
                "showWorryDialog": settings.show_worry_dialog,
                "placeIds": settings.place_ids,
                "showComplimentaryItem": settings.show_complimentary_item,
                "complimentaryItem": settings.complimentary_item,
                "questions": settings.questions,
                "dialogBody": settings.worry_dialog_body,
                "dialogTitle": settings.worry_dialog_title,
                "websiteUrls": settings.website_urls,
                "places": settings.places_information,
                "keywords": settings.company_keywords,
                "useBubblePlatform": settings.bubble_rating_platform,
                "emailDelay": settings.email_delay,
            }
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse(
                {"error": "Settings not found for the specified placeId."}, status=404
            )
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


@csrf_exempt
def get_review_settings(request, place_ids):
    place_ids_list = place_ids.split(",")
    if request.method == "GET":
        try:
            all_user_data = UserData.objects.all()

            # Filter results by checking if any place_id from place_ids_list exists in each entry's place_ids
            matching_settings = [
                user_data
                for user_data in all_user_data
                if any(pid in json.loads(user_data.place_ids) for pid in place_ids_list)
            ]
            settings = matching_settings[0]
            data = {
                "emailIntro": settings.email_intro,
                "emailSignature": settings.email_signature,
                "emailBody": settings.email_body,
                "emailAppPassword": settings.email_app_password,
                "clientEmail": settings.client_email,
                "worryRating": settings.worry_rating,
                "showWorryDialog": settings.show_worry_dialog,
                "placeIds": settings.place_ids,
                "showComplimentaryItem": settings.show_complimentary_item,
                "complimentaryItem": settings.complimentary_item,
                "questions": settings.questions,
                "dialogBody": settings.worry_dialog_body,
                "dialogTitle": settings.worry_dialog_title,
                "websiteUrls": settings.website_urls,
                "locationUrls": settings.in_location_urls,
                "places": settings.places_information,
                "userEmail": settings.user_email,
                "keywords": settings.company_keywords,
                "companyUrls": settings.company_website_urls,
                "useBubblePlatform": settings.bubble_rating_platform,
                "emailDelay": settings.email_delay,
                "categories": settings.categories,
            }
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse(
                {"error": "Settings not found for the specified placeId."}, status=404
            )
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


def extract_words(keywords):
    """
    Extract individual words from a list of keywords, removing special characters.

    :param keywords: List of keywords to split into words.
    :return: List of all extracted words.
    """
    all_words = []

    for keyword in keywords:
        # Use regular expressions to split by non-word characters and ignore empty strings
        words = re.findall(r"\b\w+\b", keyword)
        all_words.extend(words)

    return all_words


@csrf_exempt
def set_place_ids(request):
    global stop_words
    global env_customer_url
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Extract place_id from the data
        print(data)
        place_ids = [place["place_id"] for place in data.get("places", [])]
        buisness_names = [place["name"] for place in data.get("places", [])]
        buisness_tags = [
            item for sublist in data.get("googleTypes", []) for item in sublist
        ]
        company_website_urls = [place["websiteUrl"] for place in data.get("places", [])]
        unique_website_urls = list(set(company_website_urls))
        if env_customer_url == "LOCAL":
            base_url = "http://localhost:4100/clientreviews/"
            in_location_url = "http://localhost:4100/instorereviews/"
        else:
            base_url = "https://vero-reviews.vercel.app/clientreviews/"
            in_location_url = "https://vero-reviews.vercel.app/instorereviews/"
        default_worry_dialog = "We’re truly sorry to hear that your experience didn’t meet your expectations, and we greatly appreciate your feedback. Please give us the chance to make it up to you!"
        default_worry_title = "We are sorry 😔"

        website_urls = [f"{base_url}{place_id}" for place_id in place_ids]
        in_location_urls = [f"{in_location_url}{place_id}" for place_id in place_ids]
        print(place_ids)

        # extract company websites, make it unique
        # if no company website, just use buisness name and its types
        # generate keywords based on company website via gpt prompt
        keywords = generate_keywords(website_urls, buisness_names, buisness_tags)
        # sub_keywords = extract_words(keywords["keywords"])
        final_keywords = list(set(keywords["keywords"]))
        filtered_keywords = [
            word for word in final_keywords if word.lower() not in stop_words
        ]

        if place_ids:
            # Use update_or_create to either update an existing entry or create a new one
            user_data, created = UserData.objects.update_or_create(
                place_ids=place_ids,
                defaults={
                    "questions": data.get("questions", []),
                    "email_intro": data.get("emailIntro", ""),
                    "email_signature": data.get("emailSignature", ""),
                    "email_body": data.get("emailBody", ""),
                    "email_app_password": data.get("emailAppPassword", ""),
                    "client_email": data.get("userEmail", ""),
                    "worry_rating": data.get("worryRating", 4),
                    "show_worry_dialog": data.get("showWorryDialog", True),
                    "place_ids": json.dumps(place_ids),
                    "show_complimentary_item": data.get("showComplimentaryItem", False),
                    "complimentary_item": data.get("complimentaryItem", ""),
                    "worry_dialog_body": default_worry_dialog,
                    "worry_dialog_title": default_worry_title,
                    "website_urls": json.dumps(website_urls),
                    "in_location_urls": json.dumps(in_location_urls),
                    "user_email": data.get("userEmail", ""),
                    "places_information": data.get("places", []),
                    "company_website_urls": unique_website_urls,
                    "company_keywords": filtered_keywords,
                    "email_delay": data.get("emailDelay", 60),
                    "categories": data.get("categories", []),
                },
            )

            serializer = UserDataSerializer(user_data)
            status_code = status.HTTP_200_OK if not created else status.HTTP_201_CREATED
            return JsonResponse(serializer.data, status=status_code)
        else:
            return JsonResponse(
                {"error": "placeIds is required"}, status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


def analyze_review(rating, ratingBody, timeTaken):
    global prompt_review_analyzer
    analyzed_data = (
        "Rating: \n"
        + str(rating)
        + "\n"
        + "Rating Body: \n"
        + ratingBody
        + "\n"
        + "Time taken: \n"
        + str(timeTaken)
    )
    tokens = tc.num_tokens_from_string(prompt_review_analyzer)
    print(f"ANALYZE REVIEW INPUT: Tokens in the string: {tokens}")
    messages = [
        ("system", prompt_review_analyzer),
        ("human", analyzed_data),
    ]

    ai_msg = llm.invoke(messages)
    tokens = tc.num_tokens_from_string(ai_msg.content)
    print(f"ANALYZE REVIEW OUTPUT: Tokens in the string: {tokens}")
    data = json.loads(ai_msg.content)
    return data


def generate_keywords(business_urls, buisness_names, buisness_tags):
    global prompt_keyword_generator
    analyzed_data = (
        "Website URL: \n"
        + "\n".join(business_urls)
        + "\n"
        + "Buisness Names: \n"
        + "\n".join(buisness_names)
        + "\n"
        + "Tags: \n"
        + "\n".join(buisness_tags)
    )
    messages = [
        ("system", prompt_keyword_generator),
        ("human", analyzed_data),
    ]

    ai_msg = llm.invoke(messages)
    print(ai_msg.content)
    data = json.loads(ai_msg.content)
    return data


@csrf_exempt
def save_customer_review(request):
    if request.method == "POST":

        try:
            body = json.loads(request.body)
            # print(body)
            data = body["data"]
            location = data.get("location")
            rating = data.get("rating")
            badges = json.dumps(data.get("badges", []))
            posted_to_google_review = data.get("postedToGoogleReview", False)
            generated_review_body = data.get("generatedReviewBody", "")
            final_review_body = data.get("finalReviewBody")
            email_sent_to_company = data.get("emailSentToCompany", False)
            place_id_from_review = data.get("placeIdFromReview")
            time_taken_to_write_review_in_seconds = data.get("timeTakenToWriteReview")
            review_date = data.get("reviewDate")
            posted_with_bubble_rating_platform = data.get(
                "postedWithBubbleRatingPlatform", False
            )
            posted_with_in_store_mode = data.get("postedWithInStoreMode", False)
            review_uuid = data.get("reviewUuid", "")
            pending_google_review = data.get("pendingGoogleReview", False)
            text_sent_for_review = data.get("textSentForReview", False)

            print("TIME TAKEN: ", time_taken_to_write_review_in_seconds)
            print("location", location)
            print("rating", rating)  # cant be 0?
            print("place id", place_id_from_review)

            if not all([location, rating, place_id_from_review]):
                print("DIIED HERE 1")
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # do gpt call to analyze reviews; only for free forms.
            # low ratings with bubble will imply suggestions based on badges selected.
            if (
                final_review_body.strip() != ""
                and not posted_with_bubble_rating_platform
            ):
                print("DIIED HERE 2")
                analyzed_review = analyze_review(
                    rating, final_review_body, time_taken_to_write_review_in_seconds
                )
                print("ANALYZED REVEIEW ", analyzed_review)
            else:
                print("DIIED HERE 3")
                analyzed_review = {}
                print("ANALYZED REVEIEW ", analyzed_review)

            # Create and save the CustomerReview instance
            review = CustomerReviewInfo(
                location=location,
                rating=rating,
                badges=badges,
                posted_to_google_review=posted_to_google_review,
                generated_review_body=generated_review_body,
                final_review_body=final_review_body,
                email_sent_to_company=email_sent_to_company,
                text_sent_for_review=text_sent_for_review,
                place_id_from_review=place_id_from_review,
                analyzed_review_details=analyzed_review,
                time_taken_to_write_review_in_seconds=time_taken_to_write_review_in_seconds,
                review_date=review_date,
                posted_with_bubble_rating_platform=posted_with_bubble_rating_platform,
                posted_with_in_store_mode=posted_with_in_store_mode,
                review_uuid=review_uuid,
                pending_google_review=pending_google_review,
            )
            review.save()
            print("REVIEWS SAVED")

            return JsonResponse({"message": "Review saved successfully"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


@csrf_exempt
def save_user_review_question_settings(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Extract place_id from the data
        user_email = data.get("userEmail")
        print(data)

        if user_email:
            # Use update_or_create to either update an existing entry or create a new one
            user_data, created = UserData.objects.update_or_create(
                user_email=user_email,
                defaults={
                    "questions": data.get("questions", []),
                    "email_intro": data.get("emailIntro", ""),
                    "email_signature": data.get("emailSignature", ""),
                    "email_body": data.get("emailBody", ""),
                    "email_app_password": data.get("emailAppPassword", ""),
                    "client_email": data.get("clientEmail", ""),
                    "worry_rating": data.get("worryRating", 3),
                    "show_worry_dialog": data.get("showWorryDialog", True),
                    "place_ids": json.dumps(data.get("placeIds", "")),
                    "show_complimentary_item": data.get("showComplimentaryItem", False),
                    "complimentary_item": data.get("complimentaryItem", ""),
                    "worry_dialog_body": data.get("dialogBody", ""),
                    "worry_dialog_title": data.get("dialogTitle", ""),
                    "bubble_rating_platform": data.get("useBubblePlatform", False),
                    "email_delay": data.get("emailDelay", 60),
                    "categories": data.get("categories", []),
                    "company_keywords": data.get("keywords", []),
                    # 'website_url': "https://vero-reviews.vercel.app/clientreviews/" + data.get('placeIds', ''),
                    # 'user_email': data.get('userEmail', '')
                },
            )

            serializer = UserDataSerializer(user_data)
            status_code = status.HTTP_200_OK if not created else status.HTTP_201_CREATED
            return JsonResponse(serializer.data, status=status_code)
        else:
            return JsonResponse(
                {"error": "placeIds is required"}, status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def log_in_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required"}, status=400
            )

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Generate a token (if using JWT)
            token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")

            return JsonResponse(
                {
                    "message": "Logged in successfully",
                    "token": token,
                    "user": {"id": user.id, "email": user.email},
                },
                status=200,
            )
        else:
            return JsonResponse(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


@csrf_exempt
def sign_up_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


# def load_data_for_llm():
#     global llm
#     print("in ere")
#     with open(documents_path, "rb") as f:
#         documents = pickle.load(f)

#     vectorstore = FAISS.load_local(
#         faiss_index_path, embeddings, allow_dangerous_deserialization=True
#     )
#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,  # Or use another model if you have one
#         chain_type="stuff",
#         retriever=vectorstore.as_retriever(),
#     )
#     return qa_chain


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@csrf_exempt
def update_review_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        review_uuid = data.get("reviewUuid")
        final_review_body = data.get("finalReviewBody")

        review_to_update = CustomerReviewInfo.objects.get(review_uuid=review_uuid)
        emailed_review_to_update = ReviewsToPostLater.objects.get(
            review_uuid=review_uuid
        )

        review_to_update.posted_to_google_review = True
        review_to_update.final_review_body = final_review_body
        review_to_update.posted_to_google_after_email_sent = True
        review_to_update.pending_google_review = False
        review_to_update.save()

        emailed_review_to_update.posted_to_google = True
        emailed_review_to_update.save()
        response_data = {"message": "Successfully updated existing review!"}
        return JsonResponse(response_data, status=status.HTTP_200_OK)

        # first, update customerReviewInfo by UUID; turn posted to google to true.

        # then, delete reviewtopostlater entry by UUID. I don't see any reason to keep the entry.. or is there a reason?
        # maybe keep it,


@csrf_exempt
def get_review_by_uuid(request, review_uuid):
    if request.method == "GET":
        try:
            review = ReviewsToPostLater.objects.get(review_uuid=review_uuid)
            serializer = ReviewsToPostLaterSerializer(review)
            return JsonResponse(serializer.data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse({"error": "Review UUID not found."}, status=404)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


def create_calendar_invite(
    event_summary: str,
    event_description: str,
    event_location: str,
    start_time: datetime,
    duration_minutes: int = 1,
) -> bytes:
    """
    Creates a calendar invite (.ics) for an event.

    :param event_summary: The title of the event.
    :param event_description: A detailed description of the event.
    :param event_location: The location or URL of the event.
    :param start_time: The starting datetime of the event.
    :param duration_minutes: The duration of the event in minutes (default is 1 minute).
    :return: The .ics file as bytes.
    """
    cal = Calendar()
    event = Event()
    event.add("summary", event_summary)
    event.add("dtstart", start_time)
    event.add(
        "dtend", start_time + timedelta(minutes=duration_minutes)
    )  # Event lasts for the specified duration in minutes
    event.add("dtstamp", datetime.now())
    event.add("location", event_location)
    event.add("description", event_description)

    # Add the event to the calendar
    cal.add_component(event)

    # Return the calendar invite as a byte string
    return cal.to_ical()


def send_text(message_body, to_phone_number):
    client = Client(ACCOUNT_SSID_TWILIO, AUTH_TOKEN_TWILIO)
    message = client.messages.create(
        body=message_body, from_=TWILIO_NUMBER, to=to_phone_number
    )

    # Return the SID of the sent message
    return message.sid


@csrf_exempt
def send_email_to_post_later(request):
    global prompt_review_five_star_creator
    global env_customer_url
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            to_email = data.get("userEmailToSend", "")
            name = data.get("userNameToSend", "")
            googleReviewUrl = data.get("googleReviewUrl", "")
            user_query = data.get("context", "")
            review_uuid = data.get("reviewUuid", "")
            date = data.get("date", "")
            time = data.get("time", "")
            send_now = data.get("sendEmailNow", False)
            phone_number = data.get("phoneNumber", "")
            tone = data.get("tone", "")
            subject = "Your 5 star review ✨"
            business_name = data.get("buisnessName", "")
            badges = json.dumps(data.get("badges", []))

            # Combine date and time to form a datetime object
            date_part = date[:10]
            combined_datetime = datetime.strptime(
                f"{date_part} {time}", "%Y-%m-%d %I:%M %p"
            )
            print("Naive Datetime:", combined_datetime)

            # Convert to UTC # also gotta figure out different time zone handling. What if somone is in eastern time.
            local_tz = pytz.timezone("America/Denver")
            localized_datetime = local_tz.localize(combined_datetime)

            # Convert to UTC
            utc_datetime = localized_datetime.astimezone(pytz.UTC)
            print("UTC:", utc_datetime)

            messages = [
                ("system", prompt_review_five_star_creator),
                ("human", user_query),
            ]

            # Invoke the LLM with the messages
            ai_msg = llm.invoke(messages)

            # Store the review data
            if env_customer_url == "LOCAL":
                customer_url = f"http://localhost:4100/customer/{review_uuid}"
            else:
                customer_url = f"https://vero-reviews.vercel.app/customer/{review_uuid}"
            # mobile url
            # customer_url = "http://192.168.1.92:4100/customer/" + f"{review_uuid}"
            dataToStore = {
                "email": to_email,
                "phone_number": phone_number,
                "name": name,
                "google_review_url": googleReviewUrl,
                "review_uuid": review_uuid,
                "review_body": ai_msg.content,
                "customer_url": customer_url,
                "posted_to_google": False,
                "tone": tone,
                "badges": badges,
            }
            serializer = ReviewsToPostLaterSerializer(data=dataToStore)
            if serializer.is_valid():
                serializer.save()
            else:
                # Print or log the validation errors
                print("Serializer errors:", serializer.errors)

            # Create the calendar invite
            # ugh, 4 segments for this message.
            twilio_body = f"Hey {name}! Your 30 second review is ready for {business_name}: {customer_url}. Thank you for being so awesome. 🤗"
            body = f"Hey {name}! \nHere's your five star review! Just go ahead and open the link provided below. It'll take less than a minute! (We aren't even kidding) \n{customer_url} \nWant to do it later? We also sent you a calendar invite so you won't miss a beat! 🗓️\n Thank you for being so awesome. 🤗"
            event_summary = f"Follow up on your 5-star review for {business_name}"
            event_description = f"Reminder to post your 5-star review for {business_name} on Google. Here’s your custom link: {googleReviewUrl}"
            start_time = datetime.now() + timedelta(days=1)  # Set to 1 day from now
            ics_file = create_calendar_invite(
                event_summary, event_description, googleReviewUrl, start_time
            )
            from_email = "reviews@vero-io.com"
            from_password = google_email_reviews_app_password

            # Schedule the email to be sent once at the specified date and time
            # Divert here, if phone number then go to twilio
            if phone_number:
                if send_now:
                    send_text(twilio_body, phone_number)
                else:
                    phone_args = (twilio_body, phone_number)
                    scheduler.add_job(
                        send_text, "date", run_date=utc_datetime, args=phone_args
                    )

            else:
                email_args = (
                    subject,
                    body,
                    ics_file,
                    from_email,
                    to_email,
                    from_password,
                )
                if send_now:
                    send_sceduled_email(
                        subject, body, ics_file, from_email, to_email, from_password
                    )
                else:
                    scheduler.add_job(
                        send_sceduled_email,
                        "date",
                        run_date=utc_datetime,
                        args=email_args,
                    )

            return JsonResponse({"content": "Success"})

        except Exception as e:
            # Handle any exceptions that occur
            print("Error:", str(e))
            return JsonResponse({"error": "An error occurred"}, status=500)
    #   # Create the email message
    #   msg = MIMEMultipart()
    #   msg['From'] = from_email
    #   msg['To'] = to_email
    #   msg['Subject'] = subject

    #   # Attach the body text
    #   msg.attach(MIMEText(body, 'plain'))

    #   # Attach the calendar invite
    #   part = MIMEApplication(ics_file, Name="invite.ics")
    #   part['Content-Disposition'] = 'attachment; filename="invite.ics"'
    #   msg.attach(part)

    #   try:
    #       # Connect to the Gmail SMTP server
    #       server = smtplib.SMTP('smtp.gmail.com', 587)
    #       server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection

    #       # Login to the server
    #       server.login(from_email, from_password)

    #       # Send the email
    #       server.sendmail(from_email, to_email, msg.as_string())
    #       print('Email sent successfully.')
    #       return JsonResponse({"content": "Success"})

    #   except Exception as e:
    #     error_message = str(e)
    #     return JsonResponse({
    #         "success": False,
    #         "error": {
    #             "message": error_message
    #         }
    #     }, status=500)

    #   finally:
    #       # Close the connection to the server
    #       server.quit()


def send_sceduled_email(subject, body, ics_file, from_email, to_email, from_password):
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the body text
    msg.attach(MIMEText(body, "plain"))

    # Attach the calendar invite
    part = MIMEApplication(ics_file, Name="invite.ics")
    part["Content-Disposition"] = 'attachment; filename="invite.ics"'
    msg.attach(part)

    try:
        # Connect to the Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection

        # Login to the server
        server.login(from_email, from_password)

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully.")
        return JsonResponse({"content": "Success"})

    except Exception as e:
        error_message = str(e)
        return JsonResponse(
            {"success": False, "error": {"message": error_message}}, status=500
        )

    finally:
        # Close the connection to the server
        server.quit()


def send_scheduled_concern_email(
    subject, body, from_email, to_email, from_password, cc_email
):
    from_email = "concerns@vero-io.com"
    from_password = google_email_concerns_app_password
    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Cc"] = cc_email

    # Attach the body text
    msg.attach(MIMEText(body, "plain"))
    recipients = [to_email]
    recipients.append(cc_email)

    try:
        # Connect to the Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection

        # Login to the server
        server.login(from_email, from_password)

        # Send the email
        server.sendmail(from_email, recipients, msg.as_string())
        print("Email sent successfully.")
        return JsonResponse({"content": "Success"})

    except Exception as e:
        error_message = str(e)
        return JsonResponse(
            {"success": False, "error": {"message": error_message}}, status=500
        )

    finally:
        # Close the connection to the server
        server.quit()


@csrf_exempt
def get_client_catgories(
    request, place_id
):  # Convert place_id to a JSON-encoded string
    if request.method == "GET":
        try:
            all_user_data = UserData.objects.all()
            matching_settings = [
                user_data
                for user_data in all_user_data
                if place_id
                in json.loads(
                    user_data.place_ids
                )  # Check if place_id exists in the place_ids list
            ]
            settings = matching_settings[0]
            data = {"categories": settings.categories}
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse(
                {"error": "Settings not found for the specified placeId."}, status=404
            )
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


@csrf_exempt
def send_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        to_email = data.get("userEmailToSend", "")
        name = data.get("userNameToSend", "")
        review_body = data.get("userReviewToSend", "")
        buisness_name = data.get("buisnessName", "")
        place_id = data.get("placeId", "")
        all_user_data = UserData.objects.all()
        # Filter results by checking if any place_id from place_ids_list exists in each entry's place_ids
        matching_settings = [
            user_data
            for user_data in all_user_data
            if place_id
            in json.loads(
                user_data.place_ids
            )  # Check if place_id exists in the place_ids list
        ]
        settings = matching_settings[0]
        if settings.show_complimentary_item == True:
            gpt_body = f"""
            Buisness Name: {buisness_name}
             Name: {name}
             Complimentary Item: {settings.complimentary_item}
             {review_body}
        """
        else:
            gpt_body = f"""
            Buisness Name: {buisness_name}
             Name: {name}
             Complimentary Item: No discount or Complimentary Item
             {review_body}
            """

        subject = "Your concerns"
        messages = [
            ("system", prompt_address_email),
            ("human", gpt_body),
        ]

        # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)

        # Return the AI-generated content as a JSON response
        print(ai_msg.content)
        # here, we will schedule the new email.

        body = ai_msg.content
        from_email = "concerns@vero-io.com"
        from_password = google_email_concerns_app_password
        cc_email = settings.client_email
        email_args = (subject, body, from_email, to_email, from_password, cc_email)

        utc_datetime = datetime.now(pytz.UTC)

        # Add 5 minutes to the current UTC time
        # time will be client adjusted.
        send_date_time = utc_datetime + timedelta(minutes=settings.email_delay)
        scheduler.add_job(
            send_scheduled_concern_email,
            "date",
            run_date=send_date_time,
            args=email_args,
        )
        return JsonResponse({"content": "Success"})


@csrf_exempt
def create_review_score(request):
    global prompt_review_score
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_review = data.get("userReview", "")

        # Messages for the LLM
        messages = [
            ("system", prompt_review_score),
            ("human", user_review),
        ]

        # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)

        # Return the AI-generated content as a JSON response
        print(ai_msg.content)
        return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def create_charts(request):
    global prompt
    global internalLLM
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        search_query = data.get("query", "")

        # Messages for the LLM
        messages = [
            ("system", prompt),
            ("human", search_query),
        ]

        # # Invoke the LLM with the messages
        # ai_msg = llm.invoke(messages)
        ai_msg = internalLLM({"query": prompt + search_query})
        # ai_msg = agent.invoke(prompt + search_query)
        # print(ai_msg.keys())
        # print(type(ai_msg))
        # Return the AI-generated content as a JSON response
        return JsonResponse({"content": ai_msg["result"]})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def create_review(request):
    global prompt_review_adjuster
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        all_reviews = data.get("allReviewsToSend", "")

        # Messages for the LLM
        messages = [
            ("system", prompt_review_adjuster),
            ("human", all_reviews),
        ]

        # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)

        # Return the AI-generated content as a JSON response
        return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)
