from django.http import HttpResponse
import os
from dotenv import load_dotenv
from collections import defaultdict
import time
import re
import json
import hashlib
import stripe
from collections import Counter
from django.db.models import Q
from django.utils import timezone
from django.forms.models import model_to_dict
from django.core import serializers
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from backend.prompts import (
    # Review-related prompts
    prompt_review_adjuster,
    prompt_review_analyzer,
    prompt_review_five_star_creator,
    prompt_review_score,
    prompt_review_template_generator,
    prompt_google_review_response,
    # Category generation
    prompt_five_star_categories_generator,
    prompt_five_star_multiple_categories_generator,
    prompt_five_star_categories_generator_influencer,
    prompt_five_star_multiple_categories_generator_influencer,
    prompt_five_star_categories_generator_online_business,
    prompt_five_star_multiple_categories_generator_online_business,
    # Keyword and question generation
    prompt_keyword_generator,
    prompt_review_question_generator,
    # Chatbot and email prompts
    prompt_chatbot,
    prompt_address_email,
    # Other
    prompt_translate_categories,
    prompt_translate_badge,
    prompt_customer_journey_analyzer,
)
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
    CustomerSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from .models import (
    UserData,
    CustomerReviewInfo,
    ReviewsToPostLater,
    ScheduledJob,
    CustomUser,
    CustomerUser,
)
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


llm_chat = ChatOpenAI(
    model="gpt-4o",
    temperature=1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

tc = TokenCount(model_name="gpt-4o-mini")


env_customer_url = os.environ.get("ENV_CUSTOMER_URL")


@csrf_exempt
def customer_journey_analysis(request):
    global prompt_customer_journey_analyzer
    tokens = tc.num_tokens_from_string(prompt_customer_journey_analyzer)
    print(f"journey analysis with badges INPUT: Tokens in the string: {tokens}")

    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_query = data.get("chartData", "")

        print(user_query)

        messages = [
            ("system", prompt_customer_journey_analyzer),
            ("human", json.dumps(user_query)),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(ai_msg.content)
        print(f"journey analysis OUTPUT: Tokens in the string: {tokens}")
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def get_place_information(request):
    if request.method == "GET":
        places = list(UserData.objects.values_list("places_information", flat=True))
        return JsonResponse(places, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


@csrf_exempt
def get_review_data_customer(request):
    if request.method == "GET":
        reviews = CustomerReviewInfo.objects.all()
        serialized_data = serializers.serialize("json", reviews)
        data = json.loads(serialized_data)

        # Update location_data to include total rating and review count for average calculation
        location_data = defaultdict(
            lambda: {
                "total_rating": 0,
                "review_count": 0,
                "place_id": "",
                "ratings_data": defaultdict(lambda: {"badges": [], "reviews": []}),
            }
        )

        # Process the reviews
        for review in data:
            fields = review["fields"]
            location = fields["location"]
            place_id = fields["place_id_from_review"]
            rating = fields["rating"]
            badges = json.loads(fields["badges"])  # convert badges string to list
            final_review_body = fields["final_review_body"]  # get the review body

            # Update location data with rating-specific entries
            location_data[location]["ratings_data"][rating]["badges"].extend(badges)

            # Only add the review body if it is not empty
            if final_review_body:
                location_data[location]["ratings_data"][rating]["reviews"].append(
                    final_review_body
                )

            # Update total rating and review count for average rating calculation
            location_data[location]["total_rating"] += rating
            location_data[location]["review_count"] += 1
            location_data[location]["place_id"] = place_id

        # Create the final result structure
        result = []
        for location, location_info in location_data.items():
            ratings_summary = []
            for rating, data in location_info["ratings_data"].items():
                # Count badge appearances
                badge_counts = Counter(data["badges"])
                # Get the top 3 badges
                top_badges = badge_counts.most_common(3)

                ratings_summary.append(
                    {
                        "rating": rating,
                        "badges": [badge for badge, count in top_badges],
                        "reviews": data["reviews"],
                    }
                )

            # Sort the ratings_summary by rating in descending order
            ratings_summary.sort(key=lambda x: x["rating"], reverse=True)
            # Calculate average rating
            average_rating = (
                location_info["total_rating"] / location_info["review_count"]
            )

            result.append(
                {
                    "location": location,
                    "place_id": location_info["place_id"],
                    "total_reviews": location_info["review_count"],
                    "average_rating": average_rating,  # Include the average rating
                    "ratings_summary": ratings_summary,
                }
            )

        # Return the serialized data as a JSON response
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


@csrf_exempt
def product_page(request):
    # Set your Stripe secret key
    stripe.api_key = settings.STRIPE_TEST_KEY

    if request.method == "POST":
        data = json.loads(request.body)
        # Get the product ID and quantity from the request (you could pass this from the front-end)
        product_id = data.get("product_id", "")
        quantity = int(data.get("quantity", 1))  # Default to 1 if not provided
        email = data.get("email", "")

        try:
            # Fetch the product price from Stripe
            product = stripe.Product.retrieve(product_id)
            price_data = stripe.Price.list(
                product=product_id, limit=1
            )  # Get the price for the product

            if not price_data or not price_data["data"]:
                return JsonResponse(
                    {"error": "No price found for the product"}, status=400
                )

            price_id = price_data["data"][0]["id"]  # Get the first price ID

            # Create a Stripe Checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=email,
                billing_address_collection="required",
                line_items=[
                    {
                        "price": price_id,  # Dynamically pass the price ID
                        "quantity": quantity,
                    },
                ],
                mode="subscription",
                # customer_creation='always',  # Automatically create a customer for each session
                success_url=settings.REDIRECT_STRIPE_SUCCESS_URL
                + "/paymentsuccessful/{CHECKOUT_SESSION_ID}",
                cancel_url=settings.REDIRECT_STRIPE_SUCCESS_URL
                + "/paymentfail/{CHECKOUT_SESSION_ID}",
            )

            # customer_creation = 'always',
            # success_url = settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
            # cancel_url = settings.REDIRECT_DOMAIN + '/payment_cancelled',
            # Redirect to Stripe Checkout page
            return JsonResponse({"url": checkout_session.url}, status=303)

        except stripe.error.StripeError as e:
            # Handle Stripe API errors
            return JsonResponse({"error": str(e)}, status=400)


## use Stripe dummy card: 4242 4242 4242 4242
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_TEST_KEY
    payload = request.body
    signature_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        session_id = session.get("id", None)
        session_customer_email = session.get("customer_email", "")
        invoice_id = session.get("invoice", None)
        print("my session details", session)
        user_account = CustomUser.objects.get(email=session_customer_email)
        user_account.account_subscription = "premium"
        user_account.save()
        # Fetch the invoice and send it via email
        if invoice_id:
            send_invoice_email(invoice_id, session_customer_email)
    return HttpResponse(status=200)


def send_invoice_email(invoice_id, to_email):
    from_email = "reviews@vero-io.com"
    from_password = google_email_reviews_app_password  # Your app password here
    subject = "Your Invoice from Vero"
    body = "Thank you for your payment! Please find your invoice attached in the pdf link below: \n"

    try:
        # Retrieve the invoice from Stripe
        invoice = stripe.Invoice.retrieve(invoice_id)
        print(invoice)
        hosted_invoice_url = invoice.get(
            "hosted_invoice_url", None
        )  # Get the PDF URL for the invoice
        print("invoice url ", hosted_invoice_url)

        # Prepare the email
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        body = body + hosted_invoice_url

        # Attach the body text
        msg.attach(MIMEText(body, "plain"))

        # Attach the invoice PDF
        # Attaching as pdf is a little buggy. need to investigate.
        # if invoice_pdf_url:
        #     pdf_response = requests.get(invoice_pdf_url)
        #     if pdf_response.status_code == 200:
        #         msg.attach(MIMEText(pdf_response.content, "application/pdf"))
        #     else:
        #         print(f"Failed to retrieve PDF from Stripe: {pdf_response.status_code}")

        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(from_email, from_password)
            server.sendmail(from_email, [to_email], msg.as_string())

        print(f"Invoice sent to {to_email}")

    except Exception as e:
        print(f"Failed to send invoice email: {e}")


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
def get_personal_reviews(request, email):
    customer_reviews = CustomerReviewInfo.objects.filter(customer_email=email)
    data = list(customer_reviews.values())
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
def get_customer_svgs(request):
    emails = request.GET.getlist(
        "emails[]"
    )  # Get the list of client IDs from the query parameters
    if not emails:
        return JsonResponse({"error": "No client IDs provided"}, status=400)

    # Query the database
    customer_data = CustomerUser.objects.filter(email__in=emails).values(
        "email", "avatar_svg"
    )

    # Serialize the data
    data = list(customer_data)

    return JsonResponse(data, safe=False)


@csrf_exempt
def save_user_avatar(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_email = data.get("email", "")
            user_svg_string = data.get("svg", "")

            customer = CustomerUser.objects.get(email=user_email)
            if customer.avatar_svg != user_svg_string:
                customer.avatar_svg = user_svg_string
                customer.save()

            return JsonResponse(
                {"status": "success", "message": "Avatar saved successfully"}
            )

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def chat_with_badges(request):
    global prompt_chatbot
    tokens = tc.num_tokens_from_string(prompt_chatbot)
    print(f"Chat with badges INPUT: Tokens in the string: {tokens}")

    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_input = data.get("inputMessage", "")
        user_query = (
            "User Query: "
            + user_input
            + "\n"
            + "User Badges: "
            + json.dumps(data.get("context", ""))
        )
        print(user_query)

        messages = [
            ("system", prompt_chatbot),
            ("human", json.dumps(user_query)),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(ai_msg.content)
        print(f"Chat with badges  OUTPUT: Tokens in the string: {tokens}")
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def get_user_data(request, email):
    if request.method == "GET":
        try:
            user_data = CustomUser.objects.get(username=email)
            data = {
                "account_type": user_data.account_type,
                "business_name": user_data.business_name,
            }
            return JsonResponse(data, status=200)
        except UserData.DoesNotExist:
            return JsonResponse({"error": "User not found."}, status=404)
    else:
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)


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
        user_account_type = data.get("accountType", "")
        print(user_query)
        print(user_radio_type)
        print(user_account_type)

        # Messages for the LLM
        if user_account_type == "google-business":
            if user_radio_type == "overall":
                prompt_to_use = prompt_five_star_categories_generator
            else:
                prompt_to_use = prompt_five_star_multiple_categories_generator

        elif user_account_type == "influencer":
            if user_radio_type == "overall":
                prompt_to_use = prompt_five_star_categories_generator_influencer
            else:
                prompt_to_use = (
                    prompt_five_star_multiple_categories_generator_influencer
                )

        elif user_account_type == "online-business":
            if user_radio_type == "overall":
                prompt_to_use = prompt_five_star_categories_generator_online_business
            else:
                prompt_to_use = (
                    prompt_five_star_multiple_categories_generator_online_business
                )
        else:
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
def translate_badge(request):
    global prompt_translate_badge
    tokens = tc.num_tokens_from_string(prompt_translate_badge)
    print(f"TRANSLATE BADGE INPUT: Tokens in the string: {tokens}")
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_badge = data.get("badge", "")
        finalQuery = user_badge

        # Messages for the LLM
        messages = [
            ("system", prompt_translate_badge),
            ("human", finalQuery),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(f"TRANSLATE OUTPUT: Tokens in the string: {tokens}")
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def translate_language(request):
    global prompt_translate_categories
    tokens = tc.num_tokens_from_string(prompt_translate_categories)
    print(f"TRANSLATE INPUT: Tokens in the string: {tokens}")
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        user_query = data.get("context", "")
        user_requested_language = data.get("language", "english")
        print(user_query)
        finalQuery = (
            "Context: "
            + "\n"
            + json.dumps(user_query)
            + "\n"
            + "Requested Language:"
            + user_requested_language
        )

        # Messages for the LLM
        messages = [
            ("system", prompt_translate_categories),
            ("human", finalQuery),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(f"TRANSLATE OUTPUT: Tokens in the string: {tokens}")
        return JsonResponse({"content": ai_msg.content})
        # return JsonResponse({"content": ai_msg.content})

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def generate_google_review_response(request):
    global prompt_google_review_response
    tokens = tc.num_tokens_from_string(prompt_google_review_response)
    print(f"GEN 5 STAR REVIEW RESPONSE INPUT: Tokens in the string: {tokens}")
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        review_name = data.get("name", "")
        review_rating = data.get("rating", "")
        review_body = data.get("body", "")
        business_name = data.get("businessName", "")
        final_query = (
            "Customer Name: "
            + review_name
            + "\n Customer Rating: "
            + review_rating
            + "\n Customer Review Body: "
            + review_body
            + "\n Business Name: "
            + business_name
        )

        # Messages for the LLM
        messages = [
            ("system", prompt_google_review_response),
            ("human", final_query),
        ]

        # # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        # ai_msg = agent.invoke(prompt + search_query)
        tokens = tc.num_tokens_from_string(ai_msg.content)
        print(f"GEN 5 STAR REVIEW RESPONSE OUTPUT: Tokens in the string: {tokens}")
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
                "dialogBody": settings.worry_dialog_body,
                "dialogTitle": settings.worry_dialog_title,
                "websiteUrls": settings.website_urls,
                "places": settings.places_information,
                "keywords": settings.company_keywords,
                "useBubblePlatform": settings.bubble_rating_platform,
                "emailDelay": settings.email_delay,
                "card_description": settings.card_description,
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
                "card_description": settings.card_description,
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
        formatted_address = [
            place["formatted_address"] for place in data.get("places", [])
        ]

        # Only insta businesses will have this
        # Always the same for local and prod
        if "online_place" in formatted_address:
            if env_customer_url == "LOCAL":
                base_url = "http://localhost:4100/social-business/"
                in_location_url = "http://localhost:4100/social-business/"
            else:
                base_url = "https://vero-reviews.vercel.app/social-business/"
                in_location_url = "https://vero-reviews.vercel.app/social-business/"

        elif "influencer_place" in formatted_address:
            if env_customer_url == "LOCAL":
                base_url = "http://localhost:4100/social-icon/"
                in_location_url = "http://localhost:4100/social-icon/"
            else:
                base_url = "https://vero-reviews.vercel.app/social-icon/"
                in_location_url = "https://vero-reviews.vercel.app/social-icon/"
        elif env_customer_url == "LOCAL":
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
                    "card_description": data.get(
                        "cardDescription", "How did we do? 🤔"
                    ),
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
def get_customer_reviewed_places(request, email):
    customer = CustomerUser.objects.filter(email=email).first()
    customer_reviewed_locations = customer.places_reviewed
    return JsonResponse(
        {
            "data": customer_reviewed_locations,
        },
        status=200,
    )


@csrf_exempt
def get_customer_score(request, email):
    customer = CustomerUser.objects.filter(email=email).first()
    customer_score = customer.user_score
    return JsonResponse(
        {
            "data": customer_score,
        },
        status=200,
    )

@csrf_exempt
def get_customer_information(request, email):
    try:
        customer = CustomerUser.objects.get(email=email)
        customer_dict = model_to_dict(customer)
        return JsonResponse({"data": customer_dict}, status=200)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=404)


@csrf_exempt
def already_posted_to_google(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parsing the JSON payload
            customer_email = data.get("customerEmail")
            place_id_from_review = data.get("placeId")

            # Check if customer exists
            customer = CustomerUser.objects.filter(email=customer_email).first()
            if not customer:
                return JsonResponse(
                    {"data": False, "message": "Customer not found"}, status=404
                )

            # Check if place_id is in google_reviewed_places
            if place_id_from_review in customer.google_reviewed_places:
                print("You've already posted a Google review for this location")
                return JsonResponse(
                    {"data": True, "message": "Google Review already posted"},
                    status=200,
                )
            else:
                return JsonResponse(
                    {"data": False, "message": "No review found for this location"},
                    status=200,
                )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "POST request required"}, status=405)


def update_customer_score(
    customer_email,
    posted_to_google_review,
    place_id_from_review,
    review_date,
    pending_google_review,
):
    if pending_google_review:
        return 0.0
    score_received = 0.0
    no_score = False
    customer = CustomerUser.objects.filter(email=customer_email).first()

    if not customer:
        return None, "Customer not found"

    if isinstance(review_date, str):
        try:
            review_date = datetime.strptime(review_date, "%B %d, %Y at %I:%M:%S %p")
        except ValueError:
            return None, "Invalid date format"

    # Ensure the datetime is timezone-aware
    if timezone.is_naive(review_date):
        review_date = timezone.make_aware(review_date)
    else:
        review_date = timezone.localtime(review_date)

    # Check if the customer has already reviewed this place
    if place_id_from_review in customer.places_reviewed:
        last_review_date = customer.place_review_dates.get(place_id_from_review)
        if last_review_date:
            last_review_date = datetime.fromisoformat(last_review_date)
            if timezone.is_naive(last_review_date):
                last_review_date = timezone.make_aware(last_review_date)
            else:
                last_review_date = timezone.localtime(last_review_date)

        if posted_to_google_review:
            if place_id_from_review in customer.google_reviewed_places:
                no_score = True
                print("You've already posted a Google review for this location")
        else:
            # Check for cooldown period (1 week) for non-Google reviews
            # this also means if they posted to google, gotta wait 7 days
            if last_review_date and (review_date - last_review_date).days < 7:
                no_score = True
                print(
                    "Please wait a week before posting another review for this location"
                )

    # Update score and review counts
    if posted_to_google_review and not no_score:
        if place_id_from_review not in customer.google_reviewed_places:
            customer.user_score += 1
            customer.user_google_reviews += 1
            customer.google_reviewed_places.append(place_id_from_review)
            score_received = 1.0
    else:
        if not no_score:
            customer.user_score += 0.5
            customer.user_regular_reviews += 1
            score_received = 0.5

    # Add the place_id to places_reviewed if it's not already there
    if place_id_from_review not in customer.places_reviewed:
        customer.places_reviewed.append(place_id_from_review)

    # Update the review date for this place
    customer.place_review_dates[place_id_from_review] = review_date.isoformat()

    customer.save()
    return score_received


@csrf_exempt
def save_customer_review(request):
    score_received = 0.0
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
            customer_email = data.get("customerEmail", "")

            # if customer email comes from the review data,
            # that means they submitted a review logged in.
            # hence, update score.
            if customer_email and customer_email != "":
                score_received = update_customer_score(
                    customer_email,
                    posted_to_google_review,
                    place_id_from_review,
                    review_date,
                    pending_google_review,
                )

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
                customer_email=customer_email,
                score_received=score_received,
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
            print("size of request load: ", len(request.body))
            data = json.loads(request.body)  # Parse the JSON body of the request
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Extract place_id from the data
        user_email = data.get("userEmail")
        print(data.get("cardDescription"))

        if user_email:
            # Use update_or_create to either update an existing entry or create a new one
            user_data, created = UserData.objects.update_or_create(
                user_email=user_email,
                defaults={
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
                    "card_description": data.get(
                        "cardDescription", "How did we do? 🤔"
                    ),
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
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "account_type": user.account_type,
                    },
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
def log_in_customer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse(
                {"error": "Email and password are required"}, status=400
            )

        try:
            user = CustomerUser.objects.get(email=email)
        except CustomerUser.DoesNotExist:
            return JsonResponse({"error": "Invalid email or password"}, status=401)

        if user.check_password(password):
            login(request, user)

            # Generate a token (if using JWT)
            token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")

            return JsonResponse(
                {
                    "message": "Logged in successfully",
                    "token": token,
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    },
                },
                status=200,
            )
        else:
            return JsonResponse({"error": "Invalid email or password"}, status=401)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


@csrf_exempt
def sign_up_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
            data["account_subscription"] = "free-trial"
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


@csrf_exempt
def sign_up_customer(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse the JSON body of the request
            print(data)
            data["user_score"] = 0
            data["user_reviews"] = {}
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CustomerSerializer(data=data)
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

        if not review_to_update.customer_email:
            review_to_update.customer_email = emailed_review_to_update.email
        review_to_update.posted_to_google_review = True
        review_to_update.score_received = 1.0
        review_to_update.final_review_body = final_review_body
        review_to_update.posted_to_google_after_email_sent = True
        review_to_update.pending_google_review = False
        update_customer_score(
            customer_email=(
                review_to_update.customer_email
                if review_to_update.customer_email
                else emailed_review_to_update.email
            ),
            posted_to_google_review=True,
            place_id_from_review=review_to_update.place_id_from_review,
            review_date=review_to_update.review_date,
            pending_google_review=False,
        )
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


def already_posted_to_google_email(customer_email, place_id_from_review):
    try:
        # Check if customer exists
        customer = CustomerUser.objects.filter(email=customer_email).first()
        if not customer:
            return False

        # Check if place_id is in google_reviewed_places
        if place_id_from_review in customer.google_reviewed_places:
            print("You've already posted a Google review for this location")
            return True
        else:
            return False

    except:
        return False


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
            business_name = data.get("buisnessName", "")
            badges = json.dumps(data.get("badges", []))
            place_id_from_review = data.get("placeIdFromReview", "")

            already_posted_to_google_before = already_posted_to_google_email(
                to_email, place_id_from_review
            )

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

            # save in db if first time posting to google
            if not already_posted_to_google_before:
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

            from_email = "reviews@vero-io.com"
            from_password = google_email_reviews_app_password
            # ugh, 4 segments for this message.
            if not already_posted_to_google_before:
                twilio_body = f"Hey {name}! Your 30 second review is ready for {business_name}: {customer_url}. Thank you for being so awesome. 🤗"
                body = f"Hey {name}! \nHere's your five star review! Just go ahead and open the link provided below. It'll take less than a minute! (We aren't even kidding) \n{customer_url} \nThank you for being so awesome. 🤗"
                subject = "Your 5 star review ✨"
            else:
                twilio_body = f"Hey {name}! You've already posted a google review for {business_name}! Thank you for being so awesome. :)"
                body = f"Hey {name}! You've already posted a google review for {business_name}! Thank you for being so awesome. 🤗"
                subject = "You're too Amazing 🥳"

            # Schedule the email to be sent once at the specified date and time
            # Divert here, if phone number then go to twilio
            if phone_number:
                if send_now:
                    send_text(twilio_body, phone_number)
                else:
                    phone_args = (twilio_body, phone_number)
                    job = scheduler.add_job(
                        send_text, "date", run_date=utc_datetime, args=phone_args
                    )
                    ScheduledJob.objects.create(
                        job_id=job.id,  # Store the job ID from APScheduler
                        job_name="send_text",
                        run_date=utc_datetime,
                        args=json.dumps(phone_args),  # Store args as JSON string
                    )

            else:
                email_args = (
                    subject,
                    body,
                    from_email,
                    to_email,
                    from_password,
                )
                if send_now:
                    send_sceduled_email(
                        subject, body, from_email, to_email, from_password
                    )
                else:
                    job = scheduler.add_job(
                        send_sceduled_email,
                        "date",
                        run_date=utc_datetime,
                        args=email_args,
                    )
                    # Store the job in the database
                    ScheduledJob.objects.create(
                        job_id=job.id,  # Store the job ID from APScheduler
                        job_name="send_scheduled_email",
                        run_date=utc_datetime,
                        args=json.dumps(email_args),  # Store args as JSON string
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


def send_sceduled_email(subject, body, from_email, to_email, from_password):
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the body text
    msg.attach(MIMEText(body, "plain"))

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
            data = {
                "categories": settings.categories,
                "card_description": settings.card_description,
            }
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
        job = scheduler.add_job(
            send_scheduled_concern_email,
            "date",
            run_date=send_date_time,
            args=email_args,
        )
        # Store the job in the database
        ScheduledJob.objects.create(
            job_id=job.id,  # Store the job ID from APScheduler
            job_name="send_scheduled_concern_email",
            run_date=send_date_time,
            args=json.dumps(email_args),  # Store args as JSON string
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
