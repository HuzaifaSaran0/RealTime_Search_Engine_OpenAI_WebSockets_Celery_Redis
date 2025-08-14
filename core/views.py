import os
import requests
from django.shortcuts import render
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
import json

# Openai setup
import re
import json
from .tasks import fetch_openai_results_task
from django.contrib.auth.decorators import login_required
from .models import SearchResult

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_URL = "https://api.tavily.com/search"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# login sign up views
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        return redirect("")

    return render(request, "core/signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("/") # this empty string means the user will be redirected to the homepage
        else:
            messages.error(request, "Invalid credentials")
            return redirect("login")
    return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# login sign up end

DEFAULT_QUERIES = [
    "SpaceX Starship launch",
]

def fetch_results(query):
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": 2
    }
    try:
        response = requests.post(TAVILY_URL, json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"query": query, "results": data.get("results", [])}
    except Exception as e:
        print(f"Error fetching {query}:", e)
    return {"query": query, "results": []}

def index(request):
    # Get queries from POST form, or default if first visit
    if request.method == "POST":
        queries = request.POST.getlist("queries")
        queries = [q.strip() for q in queries if q.strip()]
    else:
        queries = DEFAULT_QUERIES

    all_results = []
    if request.method == "POST":
        with ThreadPoolExecutor(max_workers=10) as executor:
            all_results = list(executor.map(fetch_results, queries))

    return render(request, "core/index.html", {
        "queries": queries,
        "all_results": all_results
    })


@login_required
def openai_index(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.method == "POST":
        queries = request.POST.getlist("queries")
        queries = [q.strip() for q in queries if q.strip()]  # Remove empty queries by stripping whitespace
        queries = queries[:1]  # limit for cost
        for query in queries:
            fetch_openai_results_task.delay( # here delay is used to offload the task to a background worker which means the request will be processed asynchronously
                query=query,
                user_id=request.user.id
            )
    else:
        queries = DEFAULT_QUERIES

    all_results = SearchResult.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "core/openai_index.html", {
        "queries": queries,
        "message": "Search started! You will see results shortly.",
        "user_id": request.user.id,
        "all_results": all_results,
    })