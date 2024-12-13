import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re
import praw
import os

# Helper function to clean text
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z ]', '', text)
    return text.strip().lower()

# Sentiment Analysis using VADER and TextBlob
def analyze_sentiment(text):
    cleaned_text = clean_text(text)

    # VADER Sentiment Analysis
    analyzer = SentimentIntensityAnalyzer()
    vader_score = analyzer.polarity_scores(cleaned_text)['compound']

    textblob_score = TextBlob(cleaned_text).sentiment.polarity
    
    combined_score = (vader_score + textblob_score) / 2

    # Normalize to 1-100 scale
    sentiment_score = int((combined_score + 1) * 50)
    return sentiment_score

# Function to classify sentiment
def classify_sentiment(score):
    if score <= 40:
        return "Strong Sell"
    elif 41 <= score < 60:
        return "Neutral"
    elif score >= 60:
        return "Strong Buy"

def fetch_market_sentiment(market_type="global", country="US", num_articles=5):
    api_key = 'bc6a8428bd6143798ea88348297f44ec'

    # Based on the market type, decide the query
    if market_type == "global":
        query = "stock market"
    elif market_type == "country":
        query = f"stock market {country}"
    else:
        print("Invalid market type. Please choose 'global' or 'country'.")
        return []

    url = f'https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={api_key}'
    scores = []
    news_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        articles = data.get('articles', [])

        for article in articles[:num_articles]:
            title = article.get('title', '')
            description = article.get('description', '')

            if title and description and "[Removed]" not in title and "[Removed]" not in description:
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)
                scores.append(sentiment_score)

                news_data.append({
                    "headline": title,
                    "relevant_prediction": sentiment_score
                })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")

    return {"scores": scores, "news": news_data}

def fetch_news_sentiment(stock_symbol, num_articles=5):
    api_key = 'bc6a8428bd6143798ea88348297f44ec'
    url = f'https://newsapi.org/v2/everything?q={stock_symbol}&language=en&apiKey={api_key}'
    scores = []
    news_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        articles = data.get('articles', [])

        for article in articles[:num_articles]:
            title = article.get('title', '')
            description = article.get('description', '')

            if title and description and "[Removed]" not in title and "[Removed]" not in description:
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)
                scores.append(sentiment_score)

                news_data.append({
                    "headline": title,
                    "relevant_prediction": sentiment_score
                })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")

    return {"scores": scores, "news": news_data}

def fetch_reddit_sentiment(stock_symbol, num_posts=5):
    reddit = praw.Reddit(
        client_id='dh-pJ2g7bmp5H55tgsth3w',
        client_secret='L2tiTgDrdwwb9DWtrX19CdbZqYAGsg',
        user_agent='AI-lluminati',
        username='AccomplishedMonk3736',
        password='garlandidya57'
    )
    scores = []
    reddit_data = []

    subreddit = reddit.subreddit('all')
    posts = subreddit.search(stock_symbol, limit=num_posts)

    for post in posts:
        text = post.title + " " + post.selftext
        sentiment_score = analyze_sentiment(text)
        scores.append(sentiment_score)

        reddit_data.append({
            "headline": post.title,
            "relevant_prediction": sentiment_score
        })

    return {"scores": scores, "news": reddit_data}

def fetch_and_analyze_stock_sentiment(stock_symbol, num_posts=10):
    news_result = fetch_news_sentiment(stock_symbol, num_articles=num_posts // 2)
    reddit_result = fetch_reddit_sentiment(stock_symbol, num_posts=num_posts // 2)

    combined_scores = news_result["scores"] + reddit_result["scores"]
    combined_data = news_result["news"] + reddit_result["news"]

    if combined_scores:
        overall_score = sum(combined_scores) / len(combined_scores)
        return {
            "overall_prediction": overall_score,
            "news": combined_data
        }
    else:
        print("No data available to analyze sentiment.")
        return {
            "overall_prediction": None,
            "news": []
        }


#TRENDING NEWS

# Fetch News Articles for Stock Market (Global or Country-Specific)
def fetch_market_sentiment(market_type="global", country="US", num_articles=5):
    api_key = 'bc6a8428bd6143798ea88348297f44ec'

    # Based on the market type, decide the query
    if market_type == "global":
        query = "stock market"
    elif market_type == "country":
        query = f"stock market {country}"
    else:
        print("Invalid market type. Please choose 'global' or 'country'.")
        return []

    url = f'https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={api_key}'
    scores = []
    news_data = []

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        articles = data.get('articles', [])

        for article in articles[:num_articles]:
            title = article.get('title', '')
            description = article.get('description', '')

            if title and description and "[Removed]" not in title and "[Removed]" not in description:
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)
                scores.append(sentiment_score)

                news_data.append({
                    "headline": title,
                    "relevant_prediction": sentiment_score
                })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")

    if scores:
        overall_score = sum(scores) / len(scores)
        overall_classification = overall_score

        return {
            "overall_prediction": overall_classification,
            "news": news_data
        }
    else:
        print("No data available to analyze sentiment.")
        return {
            "overall_prediction": "No Data",
            "news": []
        }

# Example usage
#fetch_and_analyze_stock_sentiment('Zomato', num_posts=10)
#fetch_market_sentiment(market_type="country", country="Canada", num_articles=5)
#fetch_market_sentiment(market_type="global", num_articles=5)


# Main entry point for execution
if __name__ == "__main__":  
    # Example usage
    print("Fetching and analyzing sentiment for Zomato stock...")
    print(fetch_and_analyze_stock_sentiment('Zomato', num_posts=7))

    #print("Fetching and analyzing sentiment for global stock market...")
    #fetch_market_sentiment(market_type="global", num_articles=5)

    print("Fetching and analyzing sentiment for stock market in India...")
    print(fetch_market_sentiment(market_type="country", country="India", num_articles=5))