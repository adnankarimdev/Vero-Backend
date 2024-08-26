from django.http import HttpResponse
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI


os.environ['OPENAI_API_KEY'] = 'sk-proj-BkqMCfMCu8aJz0M19aj9T3BlbkFJCqFGN85AiM1NP2lJyrF1'

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

prompt = """
You are to return graphs for me in this format: 
                <Card>
            <CardHeader>
              <CardTitle>Rating Distribution</CardTitle>
              <CardDescription>Distribution of ratings across all reviews</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="h-64">
                  <Bar data={barData} />
                </div>
                <div className="h-64">
                  <Pie data={pieData} />
                </div>
              </div>
            </CardContent>
          </Card>
with relevant titles, data, and so forth. return it as code and nothing else because it will be dynamically updated. i will ask natural questions, you respond with graphs. if the question cannot be turned into a graph, then reply with null. You are to fill out the data yourself and plug it in directly into the graph. You cannot create an external variable for the data. 

here's the data:
[
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "I\u2019ve been to every P&S location over the years and I love this one the most because of the wonderful staff! Especially the girl with the cool outfits.\n\nCoffee is always great and the atmosphere is always friendly, 6/5 stars.",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "This is one of my favorite Phil & Sebastian's to go to. The two Duo that have been working together lately are the best. Coffee is always great. Thank you guys for making my days better.",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "The girls here are always so sweet, I go a couple times a week and I\u2019ve never had a bad experience. The service is also super quick which is nice :) I love the vanilla bean latte so much!",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "Great little cafe spot for grabbing a coffee and donut! The 2 baristas are so friendly and helpful! \ud83d\ude0d\n\nI would suggest that you try the R3 brewed coffee and the leche flan donut.",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "Great service. Only started coming here recently and the girl that works most mornings knows my order. Thank you !",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "Best coffee in town. Love going to P&S and glad that they have a very convenient downtown location.",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "Amazing coffee. Especially the pink bourbon. Staff always friendly and the prices are reasonable.",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "Fast service and great coffee",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "1",
        "body": "I ordered a large London fog, half sweet, with oat milk that ended up being $8. What I got was a weak, watery, over sweet \u201ctea\u201d that did not have steamed milk. Barista should\u2019ve left the tea bags in but seemed to pour hot water over and then removed the bag. Waste of money. Do not get a tea latte, they don\u2019t know how to make it.",
        "date": "2024-08"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "1",
        "body": "Went here with my family for the comic expo parade and had an awful experience. First off, I spent 26 dollars on a coffee and three hot chocolates. They Gave me a the coffee and ONE of the hot chocolates. Not one person was smiling and we waited 15 minutes for 2 more hot chocolates.....and the parade has started.\nThe coffee wasn't life changing, and the hot chocolate...nothing better than what you could make yourself. Again, not life changing.\nDid I also mention that it appears they did serve food at one time?? but I don't think they actually serve food there anymore. Lots of blacked out places on the menu....who knows?\nBut it's ok. We leave and the parade has started. My two older son is with my husband and my toddler starts getting crabby. I take him BACK into the store just to sit and it's also a bit chilly out. There was no one there.  Everyone was outside watching the parade. Only employees...maybe two? At the front\nAnyhow, since there is NO ONE THERE besides them myself, and my daughter.\nI already got my sub-par beverages and my 18 month old son fussing. Well I checked his diaper! OH MAN. he barely had a pee in there, but we had a long walk back, so I just whip zip put on another...lol I'm sure they have cameras. LITERALLY  2 seconds.\nThen a tap on my shoulder \"um ew can you not\" and I had earplugs in, so I just maybe I didn't react quick enough? Whatever the case may be...he came up and didn't like that I did that and because I chose to put the diaper on....again maybe I wasn't acknowledging Mr man quick enough, but he called me RUDE! And says something to the effect of I could get the place shut down if the health inspector sees me...a lady with a baby in a place with no obvious bathrooms, and then rudely wiped the seat we were at, like it was SUCH A BIG DEAL. Just unnecessary. Like, I am human.\nI get it. A hundo. That was not an ideal place but we were on stephen Ave, our car is SOSOSOSO far away, the parade was blocking eVErYTHing....and the coffee shop was EMPTY. Where was I to go? Lol the staff was so frosty\nAnd this gut just shames me. He never even OFFERED to show me the bathroom. I TIPPED THAT BUTTHEAD.\nAfter giving me several dirty looks, he stares into my soul (again, why this level of aggression?\"\n\"Just ask next time\"\n\nUmmmmm NO there will be no next time. Y'all don't even have food!!!!!\n\nAnd for Pete's sake. Water those poor pothos plants! They are starting to look as sad as the staff.\n\nIt's just not a family friendly place, and that is the truth all day long.\n\nKeep them pothos in your thoughts and prayers",
        "date": "2024-05"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "I'm from Edmonton, I was on work in calgary, best latte I have ever had , I love latte and I have lots of local places but Phil & S\u00e9bastien is the best , I wish you would open in Edmonton too.",
        "date": "2024-05"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "Filled cronut",
        "date": "2024-02"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "",
        "date": "2024-02"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "1",
        "body": "Very poor customer service and won\u2019t ever be returning",
        "date": "2023-09"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "1",
        "body": "Not only the hot drinks at this location are unpalatable but also the staff is rude, love the other locations but won't be returning to this one",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "Donuts here are legit",
        "date": "2022-08"
    }
    
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Always super delightful to stop in here. The young gentlemen that work here are super great. Hoopla donuts are always a great treat too!",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Awesome Coffee",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Smooth cappuccino.\nDonuts are a treat.\nPleasant service to the table.  Water available, self serve.",
        "date": "2024-03"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Great downtown meeting spot with ample seating options.",
        "date": "2024-02"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "First cafe ever that actually uses vanilla bean for vanilla latte!!",
        "date": "2024-02"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "A touch pricey but you get what you pay for, best coffee in Calgary that we've experienced.\nSmall selection of doughnuts that you can tell are made fresh each day. Their options available change every day.",
        "date": "2023-11"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Great atmosphere and amazing coffee",
        "date": "2023-11"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "4",
        "body": "Very good doughnuts, great people working. Very friendly and welcoming.",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "The BEST customer service! Everytime I come to this location they are super sweet and happy to see me. Great food and baked goodies! Coffee is fresh and delicious! Thanks for being amazing! \u2764\ufe0f",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "The guy who works at this location is awesome and the donuts are the best in the city, especially the Earl Grey \ud83e\udd24 \u2026",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Best coffee and delicious donuts !",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Best coffee and treats!",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Best coffee in Alberta",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "3",
        "body": "I like the chair I was sitting in",
        "date": "2022-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "hands down one of the best coffee spots in town!",
        "date": "2021-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Had the the London Fog hoopla donut and it was delicious!",
        "date": "2021-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Best coffee in Calgary.",
        "date": "2021-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "I do not like paying very much for things that are available everywhere. Downtown there is an abundance of coffee shops to choose from. Phil and Sebastian\u2019s though... NEVER disappoints. I get my usual plain latte and enjoy the next 15 minutes. No need to add flavour shots - in my opinion it just detracts from the deliciousness of a properly made espresso drink. It tastes as creamy as ever and the flavour of the bean is superb. \ud83d\udc4d\ud83c\udffc\ud83d\udc4d\ud83c\udffc",
        "date": "2020-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "4",
        "body": "The coffee is excellent.  The donuts are fantastic but buy early as they sell out of the good ones really early.  Donuts are a bit crazy expensive hopefully they will lower the price. Also avoid the hot chocolate, it\u2019s made from good ingredients but done so poorly that it\u2019s shameful.",
        "date": "2019-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "2",
        "body": "The coffee is good, but Hoopla donuts is a major disappointment for me. Over $3 dollars for a small donut that is barely better than Tim Hortons (How is that even possible?).",
        "date": "2019-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Love their maple glazed donuts. Hard to find the plain glazed ones in Calgary.",
        "date": "2019-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "3",
        "body": "Just ok coffee....not worth the premium pricing",
        "date": "2019-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "The best coffee in Canada, bar none.",
        "date": "2019-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "Good coffee, great doughnuts.",
        "date": "2019-08"
    },
    {
        "location": "Phil & Sebastion - Calgary Place",
        "rating": "5",
        "body": "love it",
        "date": "2019-08"
    }

]

you are to ONLY make charts that are from react-chartjs-2, you can assume i have all of it imported. I have wrappers. So 
	•	If Bar then BarChart
	•	If Pie then PieChart
	•	If Line then LineChart
	•	If Doughnut then DoughnutChart
	•	If Radar then RadarChart
	•	If PolarArea then PolarAreaChart
	•	If Bubble then BubbleChart
	•	If Scatter then ScatterChart
got it?
"""


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@csrf_exempt
def create_charts(request):
    global prompt
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        search_query = data.get("query", "")
        
        # Messages for the LLM
        messages = [
            ("system", prompt),
            ("human", search_query),
        ]
        
        # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        
        # Return the AI-generated content as a JSON response
        return JsonResponse({"content": ai_msg.content})
    
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def create_review(request):
    prompt = """
    You are to transform a given review into a complete google review. 
    Do not ALTER the tone, or the point of the review. 
    If you can, try to include my buisness key words if possible, 
    only if it makes sense with the review: [latte, best coffee shop, artisan]. 
    You are to ONLY return the completed google review. 
"""
    if request.method == "POST":
        # Parse the JSON data sent from the frontend
        data = json.loads(request.body)
        all_reviews = data.get("allReviewsToSend", "")
        
        # Messages for the LLM
        messages = [
            ("system", prompt),
            ("human", all_reviews),
        ]
        
        # Invoke the LLM with the messages
        ai_msg = llm.invoke(messages)
        
        # Return the AI-generated content as a JSON response
        return JsonResponse({"content": ai_msg.content})
    
    return JsonResponse({"error": "Invalid request method"}, status=400)