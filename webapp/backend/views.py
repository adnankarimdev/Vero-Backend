from django.http import HttpResponse
import os
import json
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import pickle
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .serializers import UserSerializer, UserDataSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import UserData 
import jwt
import secrets
import googlemaps

os.environ['OPENAI_API_KEY'] = 'sk-proj-BkqMCfMCu8aJz0M19aj9T3BlbkFJCqFGN85AiM1NP2lJyrF1'
faiss_index_path = '/Users/adnankarim/Desktop/DevTipsNotes/PersonalProjects/GoogleReviewDashboard/GoogleReviewDashboardBackend/scripts/faiss_index_p&s'
documents_path = '/Users/adnankarim/Desktop/DevTipsNotes/PersonalProjects/GoogleReviewDashboard/GoogleReviewDashboardBackend/scripts/faiss_documents_p&s.pkl'

embeddings = OpenAIEmbeddings()

SECRET_KEY = secrets.token_urlsafe(32)

google_email_app_password = "jmym xiii qzgc qnhc"
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

agent = create_csv_agent(
    llm,
    "/Users/adnankarim/Desktop/DevTipsNotes/PersonalProjects/reviews.csv",
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    allow_dangerous_code=True,
    handle_parsing_errors=True
)

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

prompt_address_email = """
You are a customer service representative for a coffee shop. You have received a negative review from a customer, and you want to craft a personalized response based on the details provided. Below is the review and the customer’s answers to specific questions you asked. Use this information to write a thoughtful and empathetic response.

Review:

[Insert the negative review text here.]

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
	5.	Offer a resolution or compensation if appropriate, such as a discount or free item on their next visit.

Response Example:

“Dear [Customer’s Name],

Thank you for taking the time to share your feedback. We are genuinely sorry to hear about your recent experience at [Coffee Shop Name]. We understand that [specific issue] was a significant inconvenience, and we deeply apologize for not meeting your expectations.

From your answers, we see that [specific issue] affected your visit by [how it affected their visit]. We appreciate your suggestion of [suggestion for improvement] and are taking steps to address this issue to prevent it from happening in the future.

Thank you for bringing this to our attention. Your feedback is invaluable in helping us improve our service. If you have any more details or further suggestions, please feel free to reach out to us directly. As a token of our appreciation and to make up for the inconvenience, we would like to offer you [mention any compensation or resolution].

We hope to have the opportunity to serve you better in the future.

Sincerely,
P&S
"""

@csrf_exempt 
def get_place_id_by_email(request, email):
    if request.method == 'GET':
        try:
            settings = UserData.objects.get(user_email=email)
            place_ids_as_array = json.loads(settings.place_ids) if settings.place_ids else []
            website_urls_as_array = json.loads(settings.website_urls) if settings.website_urls else []
            data = {
                "placeIds": place_ids_as_array,
                "places": settings.places_information,
                "websiteUrls": website_urls_as_array
            }
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse({"error": "Settings not found for the specified placeId."}, status=404)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)
        
@csrf_exempt 
def get_review_questions(request, place_id):
    place_ids_list = place_id.split(',') # Convert place_id to a JSON-encoded string
    if request.method == 'GET':
        try:
            all_user_data = UserData.objects.all()
            matching_settings = [
                user_data for user_data in all_user_data
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
                "websiteUrls" : settings.website_urls,
                "places" : settings.places_information
            }
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse({"error": "Settings not found for the specified placeId."}, status=404)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)
    
@csrf_exempt 
def get_review_settings(request, place_ids):
    place_ids_list = place_ids.split(',')
    if request.method == 'GET':
        try:
            all_user_data = UserData.objects.all()

            # Filter results by checking if any place_id from place_ids_list exists in each entry's place_ids
            matching_settings = [
                user_data for user_data in all_user_data
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
                "websiteUrls" : settings.website_urls,
                "places" : settings.places_information,
                "userEmail" : settings.user_email
            }
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse({"error": "Settings not found for the specified placeId."}, status=404)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)
    

@csrf_exempt  
def set_place_ids(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract place_id from the data
        
        place_ids = [place['place_id'] for place in data.get('places', [])]
        base_url = "http://localhost:4100/clientreviews/"

        website_urls = [f"{base_url}{place_id}" for place_id in place_ids]
        print(place_ids)

        if place_ids:
            # Use update_or_create to either update an existing entry or create a new one
            user_data, created = UserData.objects.update_or_create(
                place_ids=place_ids,
                defaults={
                    'questions': data.get('questions', []),
                    'email_intro': data.get('emailIntro', ''),
                    'email_signature': data.get('emailSignature', ''),
                    'email_body': data.get('emailBody', ''),
                    'email_app_password': data.get('emailAppPassword', ''),
                    'client_email': data.get('clientEmail', ''),
                    'worry_rating': data.get('worryRating', 3),
                    'show_worry_dialog': data.get('showWorryDialog', True),
                    'place_ids': json.dumps(place_ids),
                    'show_complimentary_item': data.get('showComplimentaryItem', False),
                    'complimentary_item': data.get('complimentaryItem', ''),
                    'worry_dialog_body': data.get('dialogBody', ''),
                    'worry_dialog_title': data.get('dialogTitle', ''),
                    'website_urls': json.dumps(website_urls),
                    'user_email': data.get('userEmail', ''),
                    'places_information': data.get('places', [])
                }
            )

            serializer = UserDataSerializer(user_data)
            status_code = status.HTTP_200_OK if not created else status.HTTP_201_CREATED
            return JsonResponse(serializer.data, status=status_code)
        else:
            return JsonResponse({"error": "placeIds is required"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@csrf_exempt  
def save_user_review_question_settings(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract place_id from the data
        user_email = data.get('userEmail')
        print(data)

        if user_email:
            # Use update_or_create to either update an existing entry or create a new one
            user_data, created = UserData.objects.update_or_create(
                user_email=user_email,
                defaults={
                    'questions': data.get('questions', []),
                    'email_intro': data.get('emailIntro', ''),
                    'email_signature': data.get('emailSignature', ''),
                    'email_body': data.get('emailBody', ''),
                    'email_app_password': data.get('emailAppPassword', ''),
                    'client_email': data.get('clientEmail', ''),
                    'worry_rating': data.get('worryRating', 3),
                    'show_worry_dialog': data.get('showWorryDialog', True),
                    'place_ids': json.dumps(data.get('placeIds', '')),
                    'show_complimentary_item': data.get('showComplimentaryItem', False),
                    'complimentary_item': data.get('complimentaryItem', ''),
                    'worry_dialog_body': data.get('dialogBody', ''),
                    'worry_dialog_title': data.get('dialogTitle', ''),
                    # 'website_url': "http://localhost:4100/clientreviews/" + data.get('placeIds', ''),
                    # 'user_email': data.get('userEmail', '')
                }
            )

            serializer = UserDataSerializer(user_data)
            status_code = status.HTTP_200_OK if not created else status.HTTP_201_CREATED
            return JsonResponse(serializer.data, status=status_code)
        else:
            return JsonResponse({"error": "placeIds is required"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@csrf_exempt
def log_in_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Generate a token (if using JWT)
            token = jwt.encode({'user_id': user.id}, SECRET_KEY, algorithm='HS256')

            return JsonResponse({
                "message": "Logged in successfully",
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email
                }
            }, status=200)
        else:
            return JsonResponse({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@csrf_exempt
def sign_up_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
def load_data_for_llm():
    global llm
    print("in ere")
    with open(documents_path, 'rb') as f:
      documents = pickle.load(f)

    vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)
    qa_chain = RetrievalQA.from_chain_type(
    llm=llm, # Or use another model if you have one
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
    )
    return qa_chain
  

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def send_email(request):
    if request.method == "POST":
      data = json.loads(request.body)
      to_email = data.get("userEmailToSend", "")
      name = data.get("userNameToSend", "")
      review_body = data.get("userReviewToSend", "")
      subject = "Your concerns"
      gpt_body = f'''
  Name: {name}
  {review_body}
'''
      messages = [
    ("system", prompt_address_email),
    ("human", gpt_body),
    ]
      
      # Invoke the LLM with the messages
      ai_msg = llm.invoke(messages)
      
      # Return the AI-generated content as a JSON response
      print(ai_msg.content)
      body = ai_msg.content
      from_email = "adnan.karim.dev@gmail.com"
      from_password = google_email_app_password
      # Create the email message
      msg = MIMEMultipart()
      msg['From'] = from_email
      msg['To'] = to_email
      msg['Subject'] = subject

      # Attach the body text
      msg.attach(MIMEText(body, 'plain'))

      try:
          # Connect to the Gmail SMTP server
          server = smtplib.SMTP('smtp.gmail.com', 587)
          server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection

          # Login to the server
          server.login(from_email, from_password)

          # Send the email
          server.sendmail(from_email, to_email, msg.as_string())
          print('Email sent successfully.')
          return JsonResponse({"content": "Success"})

      except Exception as e:
        error_message = str(e) 
        return JsonResponse({
            "success": False,
            "error": {
                "message": error_message
            }
        }, status=500) 

      finally:
          # Close the connection to the server
          server.quit()

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
        return JsonResponse({"content": ai_msg['result']})
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

internalLLM = load_data_for_llm()