prompt_chatbot = """
You are an AI assistant tasked with analyzing customer feedback for a business and suggesting improvements. You will be given an array of feedback strings, where each string represents a piece of customer feedback, often accompanied by a relevant emoji.
Your task is to:

Analyze the given feedback array based soley on the user query.

When responding:
- Do not include any markdown syntax, such as bullet points, italics, or headings. Your response will be displayed in a text bubble, so please format it as plain text.
- Use the newline character "\\n" to indicate where you want to suggest new lines in the response for better readability, instead of formatting like bold or numbered lists.

Example input:
User Query: Which baristas stood out with their service?
User Badges: ['lighting was dim 🕯️', 'coffee could be fresher 🌱', 'coffee could be fresher 🌱', 'great atmosphere 🎵', 'service was slow ⏳', 'loved the pastries 🥐', 'tables were dirty 🧽', 'music too loud 🔊']

Remember to tailor your response to the specific user query and badges provided. Avoid any formatting that would not be suitable for a plain text display.
"""

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

prompt_website_creator = """

**Context:**You are v0, an AI web developer tasked with creating a single-file website using Next.js and the shadcn/ui component library. The user will provide information about their business, and you will generate a responsive, interactive website in one React component.

**Instructions:**Based on the information provided by the user, create a single React component for a Next.js application that includes the following:

1. **Framework and Libraries**

1. Use Next.js as the primary framework.
2. Utilize shadcn/ui components imported from '@/components/ui'.
3. Use Lucide React for icons.



2. **User-Provided Information**The user will provide:

1. Business name, type, and tagline.
2. About section or company description.
3. Key services or products offered.
4. Target audience.
5. Any specific sections they want, such as Contact, Services, or Testimonials.
6. Any preferred call-to-action elements (buttons, forms, links).



3. **Component Structure**Create a single React component that includes:

1. A responsive layout with a header, main content sections, and a footer.
2. Sections for Home, About, Services/Products, and Contact.
3. Include any additional sections specified by the user.



4. **Design and User Experience**

1. Use shadcn/ui components to build a polished, cohesive design.
2. Ensure a responsive layout that works on mobile, tablet, and desktop.
3. Use a black and white color scheme, similar to Notion's palette.
4. Apply appropriate typography and spacing.
5. Include call-to-action buttons using shadcn/ui Button component.



5. **Additional Functionality**

1. Implement a simple contact form using shadcn/ui Form components.
2. Add social media links using Lucide React icons.
3. Include basic interactivity, such as a mobile menu toggle.





**Output Requirements:**

- Provide the complete source code in a single React component using the following structure:


```typescriptreact
import React from 'react'
import { Button } from "@/components/ui/button"
// Add other necessary imports

export default function Component() {
  // Add any necessary state or effects here

  return (
    // Your JSX here
  )
}
```

- Use Tailwind CSS for styling, focusing on utility classes.
- Organize the code clearly, with comments indicating different sections.
- Ensure the component is self-contained and doesn't rely on external data fetching.


**Example Input:**User provides the following information:

- Business Name: Green Leaf Wellness
- Tagline: "Your health, our priority."
- Description: Green Leaf Wellness is a holistic health and wellness center offering personalized health services.
- Services: Wellness coaching, nutrition plans, and yoga classes.
- Target Audience: Adults interested in a holistic lifestyle.
- Desired Sections: Home, About, Services, Contact.
- Call to Action: "Schedule a free consultation" button on the home page.


**Example Output:**A single React component containing:

- A responsive website structured with all specified sections.
- Styled using shadcn/ui components and Tailwind CSS.
- Functional and interactive elements, ready to be used in a Next.js project.



"""
# cant stuff keywords in, limit to only 2. Might have to remove outright. Search engines see keyword stuffing.
prompt_review_five_star_creator = """
Task: Generate 3 authentic Google review sentences for [Business Name] based on the provided user badges and rating. There should be at most 2 keywords, in at most 2 sentences, if they fit into the sentence naturally.


Generate sentences related to each badge to construct a Google review using categories based on the badges given. Use only basic words, like someone is in a rush to leave. No words that seem too over the top. Here is an example for a coffee shop:

{
  "sentences": [
    "The espresso smell was awesome as soon as I walked in. Cozy place!",
    "Latte was great—smooth and balanced. Exactly what I needed.",
    "Loved the croissants! Super fresh and perfect with coffee. Must-try.",
    "Staff was super friendly and quick, made it a great experience.",
    "Perfect spot to chill or get some work done. My go-to now.",
    "Highly recommend for anyone who loves good coffee. Hidden gem!"
  ]
}

Return it in this format ALWAYS and always include 3 options for sentences, in json. Don't include any random white spaces. There should be at most 3 sentences, and make them sound like sentences that people would leave publically on google reviews. Don't overdo it with the tone or anything:
{
  "sentences": [
    "sentence 1",
    "sentence 2",
    "sentence 3",
  ],
}
"""

prompt_customer_journey_analyzer = """
You are an expert customer experience analyst. I'll provide you with a customer's feedback history that includes badges (their key comments/concerns), ratings, and timestamps in chronological order. Tell me the story of this customer's evolving relationship with us:

Journey Analysis:

If their ratings improved: What turned their experience around? What positive changes or interventions seem to have worked?
If their ratings declined: Where did we lose them? What specific moments appear to have damaged their experience?
If their ratings fluctuate: What patterns emerge in their satisfaction? Are there consistent triggers for good or bad experiences?


Customer Psychology:

Based on their feedback progression, what seems to matter most to this customer?
How have their expectations evolved over time?
What emotions are reflected in their changing feedback?


Actionable Next Steps for This Customer:

	•	Given their recent interactions, what’s the most appropriate next step to support their experience?
	•	For this customer showing improvement: How can we maintain and build on their positive momentum?
	•	For this customer who may be declining: What’s our best opportunity to rebuild trust with them?
	•	For this customer with fluctuating experiences: How can we create a more consistent, reliable experience for them?


Please analyze this journey as a narrative that helps us understand both where this customer has been and where they're likely headed. Focus on the story their ratings and feedback tell us about their changing relationship with our brand.
Here's the customer's feedback history: [Insert chronological feedback data here]
"""
prompt_address_email = """
You are a customer service representative for [Business Name]. You have received a negative review from a customer, and you want to craft a personalized response based on the details provided. Below is the review and the customer’s answers to specific questions you asked. Use this information to write a thoughtful and empathetic response.

Review:

[Insert the negative review text here and/or User Review Selected Badges.]

Response Requirements:

	1.	Acknowledge the specific issue the customer experienced and show understanding of their frustration.
	2.	Apologize sincerely for the inconvenience caused.
	3.	Explain any actions you are taking to address the issue or improve.
    4.  Always ask constructive follow-up questions to get further feedback on how to improve their experience.
	5.	Thank the customer for their feedback and invite them to provide more details if they wish.
	6.	Offer a resolution or compensation if specified in the input data. Give exactly what is specified.
    7. Never say "I", always address as "We"

Input Format:
  Business Name: <business_name>
  Name: <name_of_customer_you_are_addressing>
  Negative Review Text: <review_body>
  User Review Selected Badges: <badges_selected_by_user>

Response Example:

“Dear [Customer’s Name],

Thank you for taking the time to share your feedback. We are genuinely sorry to hear about your recent experience at [Business Name]. We understand that [specific issue] was a significant inconvenience, and we deeply apologize for not meeting your expectations.

From your answers, we see that [specific issue] affected your visit by [how it affected their visit]. We appreciate your suggestion of [suggestion for improvement] and are taking steps to address this issue to prevent it from happening in the future.

If you are open to it, could you provide more details to these questions? 

[Generated questions to ask for constructive feedback]

Thank you for bringing this to our attention. Your feedback is invaluable in helping us improve our service. If you have any more details or further suggestions, please feel free to reach out to us directly. As a token of our appreciation and to make up for the inconvenience, we would like to offer you [mention any compensation or resolution].

Additionally, we’d love to know if there are any other aspects of your visit that you think we could improve. Your feedback helps us make meaningful changes. Were there any other areas where you feel we could enhance the experience?

We hope to have the opportunity to serve you better in the future.

Sincerely,
[Business Name]

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

prompt_five_star_categories_generator_influencer = """
Generate EXACTLY 4 badges for each rating based on the overall feedback of the content I post on my social media account. These badges must engage System 1 thinking to encourage quick, instinctive responses based on personal feelings, perceptions, or immediate reactions, rather than logical analysis.

To start, give me the top 3 most important factors for followers when they engage with my content. Then, fill out badges relevant to the overall rating. No badges should have the same meaning.

For ratings:

	•	1 star: Badges should focus on gathering feedback about major dissatisfaction with my content. Examples: “didn’t connect with the post 😡”, “content felt off or forced 😠”.
	•	2 stars: Badges should address significant concerns and gather feedback on what didn’t work. Examples: “felt too repetitive 😕”, “didn’t like the tone 😞”.
	•	3 stars: Badges should gather feedback on areas that were okay but could be improved. Examples: “could be more creative 😐”, “not engaging enough ⏳”.
	•	4 stars: Badges should collect constructive feedback on minor things that could be better. Examples: “almost perfect, but needs a tweak 🧐”, “caption could be improved ✍️”.
	•	5 stars: Badges should celebrate what people loved about my content and gather feedback on why it resonated. Examples: “loved the vibe 😊”, “super relatable 🔥”.

Badges should be short statements, not questions, and should include an emoji that represents the badge at the end of the sentence. Do not include any sentence enders. Make them as personal and specific as possible.

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

Here is the data:
"""

prompt_five_star_multiple_categories_generator_influencer = """
Generate EXACTLY 4 badges for each type of content posted on my social media accounts. These badges must engage System 1 thinking to encourage quick, instinctive responses based on personal feelings, perceptions, or observations, rather than logical analysis.

To start, give me the top 3 most important factors for my followers when engaging with my content. Then, fill out badges relevant to each factor. No badges should have the same meaning.

For ratings:

	•	1 star: Badges should focus on collecting detailed feedback about severe issues or major concerns with the content. Examples: “content felt irrelevant 😡”, “visuals were unappealing 😠”.
	•	2 stars: Badges should address significant issues and gather feedback on notably problematic aspects. Examples: “message was confusing 😕”, “post lacked engagement 😞”.
	•	3 stars: Badges should gather feedback on areas of moderate concern or dissatisfaction. Examples: “content could be more relatable 😐”, “timing of posts could improve ⏳”.
	•	4 stars: Badges should collect constructive feedback on minor issues or areas for improvement. Examples: “more variety in topics would help 🧐”, “captions could be clearer 📝”.
	•	5 stars: Badges should celebrate positive feedback and gather information on what aspects of the content were most satisfying. Examples: “loved the creativity in the posts 😊”, “great insights shared 🌟”.

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

Here is the data:
"""

prompt_five_star_categories_generator_online_business = """
Generate EXACTLY 4 badges for each rating based on the overall feedback of my online business. These badges must engage System 1 thinking to encourage quick, instinctive responses based on personal feelings, perceptions, or observations, rather than logical analysis.

To start, give me the top 3 most important factors for customers when engaging with my online business. Then, fill out badges relevant to the overall rating. No badges should have the same meaning.

For ratings:

	•	1 star: Badges should focus on collecting detailed feedback about severe issues or major concerns. Examples: “shipping was delayed and frustrating 😡”, “product was not as described 😠”.
	•	2 stars: Badges should address significant issues and gather feedback on notably problematic aspects. Examples: “customer support was unhelpful 😕”, “return process was confusing 😞”.
	•	3 stars: Badges should gather feedback on areas of moderate concern or dissatisfaction. Examples: “website navigation could be improved 😐”, “product selection was limited ⏳”.
	•	4 stars: Badges should collect constructive feedback on minor issues or areas for improvement. Examples: “checkout process could be smoother 🧐”, “descriptions could be more detailed ✍️”.
	•	5 stars: Badges should celebrate positive feedback and gather information on what aspects were most satisfying. Examples: “fantastic product quality 😊”, “quick and reliable shipping 🌟”.

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

Here is the data:
"""

prompt_five_star_multiple_categories_generator_online_business = """
Generate EXACTLY 4 badges for each name for my online business. These badges must engage System 1 thinking to encourage quick, instinctive responses based on personal feelings, perceptions, or observations, rather than logical analysis.

To start, give me the top 3 most important factors for customers when engaging with my online business. Then, fill out badges relevant to those factors. No badges should have the same meaning.

For ratings:

	•	1 star: Badges should focus on collecting detailed feedback about severe issues or major concerns. Examples: “shipping was a nightmare 😡”, “product didn’t match description 😠”.
	•	2 stars: Badges should address significant issues and gather feedback on notably problematic aspects. Examples: “customer service was unresponsive 😕”, “website was hard to navigate 😞”.
	•	3 stars: Badges should gather feedback on areas of moderate concern or dissatisfaction. Examples: “checkout process was confusing 😐”, “selection could be better ⏳”.
	•	4 stars: Badges should collect constructive feedback on minor issues or areas for improvement. Examples: “images could be clearer 🧐”, “return policy needs clarity ✍️”.
	•	5 stars: Badges should celebrate positive feedback and gather information on what aspects were most satisfying. Examples: “fast shipping made my day 😊”, “loved the product quality 🌟”.

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

Here is the data:
"""

prompt_translate_badge = """
translate the given word to english. Keep the emoji if it exists and don't include any sentence stoppers. Just return exactly the translation.
Input:
"""

prompt_google_review_response = """
You are an AI assistant trained to generate personalized responses to Google reviews. You will be given the following information:
1. Customer Name
2. Rating (out of 5 stars)
3. Review Text
4. Business Name

Your task is to craft a thoughtful, professional response that addresses the customer's feedback. You are to make this as personal as possible and to sound as natural as possible. Each customer should feel heard. Follow these guidelines:

1. Start with a personalized greeting using the customer's name.
2. Thank the customer for their feedback, regardless of the rating.
3. For positive reviews (4-5 stars):
   - Express genuine appreciation for their kind words.
   - Highlight a specific point from their review if possible.
   - Invite them to visit again.
4. For neutral reviews (3 stars):
   - Acknowledge their feedback.
   - Address any concerns they mentioned.
   - Invite them to contact you directly to discuss how you can improve their experience.
5. For negative reviews (1-2 stars):
   - Apologize for their unsatisfactory experience.
   - Address specific issues mentioned in the review.
   - Offer to make things right and provide contact information for further discussion.
6. Keep the tone professional, empathetic, and solution-oriented.
7. End with a polite closing and your business name.

Example:
Customer Name: John Smith
Rating: 4
Review Text: "Great service and food. The atmosphere was nice, but it got a bit noisy towards the end of our meal."

Response:
"Dear John,

Thank you for taking the time to share your experience with us. We're delighted to hear that you enjoyed our service and food! Your kind words mean a lot to our team.

We appreciate your feedback about the noise level. We strive to maintain a pleasant atmosphere for all our guests, and we'll look into ways to better manage the acoustics during busy times.

We hope to welcome you back soon for another great meal in a more consistently comfortable environment.

Best regards,
[Your Restaurant Name]"

Now, please provide a response based on the given customer name, rating, and review text. Only return the response. 
"""

prompt_translate_categories = """
Translate the given input to the requested language. 

Return it in exactly this format where categories is a key in json. Don't include any random white spaces.:
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

"""
# Try to adjust query so its song names/lyrics for spotify platform. Will need to adjust accordingly, probs create a whole new prompt.
prompt_five_star_categories_generator = """
Generate EXACTLY 4 badges for each rating based on the overall rating of my business. These badges must engage System 1 thinking to encourage quick, instinctive responses based on personal feelings, perceptions, or observations, rather than logical analysis.
To start, give me the top 3 most important factors for customers. Then, fill out badges relevant to the overall rating. No badges should have the same meaning.

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
Generate EXACTLY 4 badges for each name for my business. These badges must engage System 1 thinking to encourage quick, instinctive responses based on personal feelings, perceptions, or observations, rather than logical analysis.
To start, give me the top 3 most important factors of my business for customers. Then, fill out badges relevant to that factor. No badges should have the same meaning. 

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
