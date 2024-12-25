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
    elif 41 <= score < 45:
        return "Sell"
    elif 45 <= score < 48:
        return "Weak Sell"
    elif 48 <= score < 52:
        return "Neutral"
    elif 52 <= score < 55:
        return "Weak Buy"
    elif 55 <= score < 60:
        return "Buy"
    else:
        return "Strong Buy"

def fetch_market_sentiment(market_type="global", country="US", num_articles=5):
    api_key = '0564634ade774fc287c6d22abc99bdde'

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
            url = article.get('url', '')

            if title and description and "[Removed]" not in title and "[Removed]" not in description:
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)
                scores.append(sentiment_score)

                # Truncate description if it's too long
                if len(description) > 200:
                    description = description[:197] + '...'

                news_data.append({
                    "headline": title,
                    "url": url,
                    "description": description,
                    "relevant_prediction": sentiment_score,
                    "sentiment_classification": classify_sentiment(sentiment_score)
                })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")

    if scores:
        overall_score = sum(scores) / len(scores)
        return {
            "overall_prediction": overall_score,
            "overall_sentiment": classify_sentiment(overall_score),
            "news": news_data
        }
    else:
        return {
            "overall_prediction": None,
            "overall_sentiment": "Unknown",
            "news": []
        }

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
            url = article.get('url', '')

            if title and description and "[Removed]" not in title and "[Removed]" not in description:
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)
                scores.append(sentiment_score)

                # Truncate description if it's too long
                if len(description) > 200:
                    description = description[:197] + '...'

                news_data.append({
                    "headline": title,
                    "url": url,
                    "description": description,
                    "relevant_prediction": sentiment_score,
                    "sentiment_classification": classify_sentiment(sentiment_score)
                })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")

    if scores:
        overall_score = sum(scores) / len(scores)
        return {
            "overall_prediction": overall_score,
            "overall_sentiment": classify_sentiment(overall_score),
            "news": news_data
        }
    else:
        return {
            "overall_prediction": None,
            "overall_sentiment": "Unknown",
            "news": []
        }

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
            "relevant_prediction": sentiment_score,
            "sentiment_classification": classify_sentiment(sentiment_score)
        })

    if scores:
        overall_score = sum(scores) / len(scores)
        return {
            "overall_prediction": overall_score,
            "overall_sentiment": classify_sentiment(overall_score),
            "news": reddit_data
        }
    else:
        return {
            "overall_prediction": None,
            "overall_sentiment": "Unknown",
            "news": []
        }

def fetch_enhanced_news_sentiment(stock_symbol, num_display=5):
    api_key = 'bc6a8428bd6143798ea88348297f44ec'
    url = f'https://newsapi.org/v2/everything?q={stock_symbol}&language=en&sortBy=relevancy&pageSize=25&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        articles = data.get('articles', [])

        # Filter and process articles
        news_data = []
        for article in articles:
            # Only include articles with description and URL
            if (article.get('description') and 
                article.get('url') and 
                "[Removed]" not in article.get('title', '') and 
                "[Removed]" not in article.get('description', '')):
                
                title = article.get('title', '')
                description = article.get('description', '')
                url = article.get('url', '')
                publisher = article.get('source', {}).get('name', 'Unknown')
                published_at = article.get('publishedAt', '')

                # Analyze sentiment
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)

                # Truncate description if needed
                if len(description) > 200:
                    description = description[:197] + '...'

                news_data.append({
                    "headline": title,
                    "url": url,
                    "description": description,
                    "publisher": publisher,
                    "published_at": published_at,
                    "relevant_prediction": sentiment_score,
                    "sentiment_classification": classify_sentiment(sentiment_score)
                })

                # Stop if we have 5 articles
                if len(news_data) == num_display:
                    break

        # If less than 5 articles found, return what we have
        if news_data:
            # Calculate overall sentiment
            scores = [article['relevant_prediction'] for article in news_data]
            overall_score = sum(scores) / len(scores)
            
            return {
                "overall_prediction": overall_score,
                "overall_sentiment": classify_sentiment(overall_score),
                "news": news_data
            }
        else:
            return {
                "overall_prediction": None,
                "overall_sentiment": "Unknown",
                "news": []
            }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return {
            "overall_prediction": None,
            "overall_sentiment": "Unknown",
            "news": []
        }

# Update the main sentiment analysis function to use the new method
def fetch_and_analyze_stock_sentiment(stock_symbol, num_posts=5):
    news_result = fetch_enhanced_news_sentiment(stock_symbol, num_display=5)
    reddit_result = fetch_reddit_sentiment(stock_symbol, num_posts=num_posts)

    combined_data = news_result.get('news', []) + reddit_result.get('news', [])
    
    # Combine scores
    combined_scores = [
        *(news_result.get('news', [])[0].get('relevant_prediction', 0) for _ in range(len(news_result.get('news', [])))),
        *(reddit_result.get('news', [])[0].get('relevant_prediction', 0) for _ in range(len(reddit_result.get('news', []))))
    ]

    if combined_scores:
        overall_score = sum(combined_scores) / len(combined_scores)
        return {
            "overall_prediction": overall_score,
            "overall_sentiment": classify_sentiment(overall_score),
            "news": combined_data[:5]  # Limit to 5 total news items
        }
    else:
        return {
            "overall_prediction": None,
            "overall_sentiment": "Unknown",
            "news": []
        }
    
if __name__ == "__main__":
    # Example usage
    print("Fetching and analyzing sentiment for Zomato stock...")
    result = fetch_and_analyze_stock_sentiment('Zomato', num_posts=7)
    print(f"Overall Score: {result['overall_prediction']}")
    print(f"Overall Sentiment: {result['overall_sentiment']}")
    print("\nNews Items:")
    for item in result['news']:
        print(f"- {item['headline']} (Score: {item['relevant_prediction']}, {item['sentiment_classification']})")