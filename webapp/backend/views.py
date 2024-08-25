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
        "body": "I’ve been to every P&S location over the years and I love this one the most because of the wonderful staff! Especially the girl with the cool outfits.\n\nCoffee is always great and the atmosphere is always friendly, 6/5 stars.",
        "date": "a year ago"
    },
    {
        "location": "Phil & Sebastion - Stephen Ave",
        "rating": "5",
        "body": "This is one of my favorite Phil & Sebastian's to go to. The two Duo that have been working together lately are the best. Coffee is always great. Thank you guys for making my days better.",
        "date": "a year ago"
    },
    ...
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