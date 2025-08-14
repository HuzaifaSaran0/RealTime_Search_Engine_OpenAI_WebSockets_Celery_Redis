# core/tasks.py
import os
import re
import json
from celery import shared_task
from .models import SearchResult
# core/tasks.py
from .custom_signals import search_completed
from openai import OpenAI
# client = OpenAI(api_key=settings.OPENAI_API_KEY) 
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

@shared_task
def fetch_openai_results_task(query, user_id=None):
    try:
        # STEP 1 — Search
        search_response = client.responses.create( # this line is for initiating a search request which means it will send the query to the OpenAI API
            model="o4-mini",
            tools=[{
                "type": "web_search_preview",
                "user_location": { # to change the user location to the actual user's location, you can pass the user's location data here
                    "type": "approximate",
                    "country": "PK",
                    "city": "Islamabad",
                    "region": "Islamabad"
                }
            }],
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a search engine. Search the live internet for the given query "
                        "and return exactly 2 most relevant results as a valid JSON array like this:\n"
                        "[{\"title\": \"Title here\", \"url\": \"https://...\", \"content\": \"short summary here\"}]"
                        "No extra text, no markdown."
                    )
                },
                {"role": "user", "content": query}
            ]
        )

        raw_search_content = search_response.output_text # this line is for getting the raw search content which means it will extract the output text from the search response

        # STEP 2 — Extract JSON if wrapped
        match = re.search(r'\[.*\]', raw_search_content, re.S) # this line is for matching the JSON array in the raw search content
        if match:
            raw_search_content = match.group() # this line is for getting the matched group which means it will extract the matched text from the raw search content so the result will be a valid JSON array

        try:
            results = json.loads(raw_search_content) # this line is for parsing the JSON array from the raw search content
        except json.JSONDecodeError:
            results = [{
                "title": "Error parsing results",
                "url": "",
                "content": raw_search_content
            }]

        # Save to DB
        search_result = SearchResult.objects.create(
            query=query,
            results=results,
            user_id=user_id
        ) # this line is for creating a new SearchResult object and saving it to the database
        search_completed.send( # this line is for sending a signal when the search is completed, this send() method will trigger the function in signals.py under this search_completed signal
            sender=fetch_openai_results_task, # sender is send for identifying the source of the signal
            search_result=search_result # this line is for passing the search_result object to the signal
        )

        return {"query": query, "results": results} # this return is only because celery always expects a return value, these values could be used later but in current setup, it is not being used anywhere

    except Exception as e:
        print(f"Error fetching {query}:", e)
        return {"query": query, "results": []}


# schedule code
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task
def run_scheduled_searches():
    # Loop through all users
    for user in User.objects.all():
        # Get their last search queries
        latest_results = (
            SearchResult.objects.filter(user_id=user.id)
            .order_by("-created_at")
            .values_list("query", flat=True)[:1]  # Get the latest query
        )

        for query in latest_results:
            fetch_openai_results_task.delay(query, user.id)
