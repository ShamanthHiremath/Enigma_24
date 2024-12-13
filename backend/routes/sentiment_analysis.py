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

def fetch_news_sentiment(stock_symbol, num_articles=5):
    api_key = 'bc6a8428bd6143798ea88348297f44ec'
    # Added language=en to fetch only English articles
#    url = f'https://newsapi.org/v2/everything?q={stock_symbol}&sortBy=publishedAt&language=en&apiKey={api_key}'
    url = f'https://newsapi.org/v2/everything?q={stock_symbol}&language=en&apiKey={api_key}'
    scores = []

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        articles = data.get('articles', [])
        
        print(f"\nAnalyzing {num_articles} News Articles for {stock_symbol} (sorted by newest)...\n")
        
        for article in articles[:num_articles]:
            title = article.get('title', '')
            description = article.get('description', '')

            # Ensure valid title and description
            if title and description and "[Removed]" not in title and "[Removed]" not in description:
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)
                scores.append(sentiment_score)
                print(f"Title: {title}\nPublished At: {article.get('publishedAt', '')}\nSentiment Score: {sentiment_score}\n")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
    
    return scores



# Fetch Reddit Posts (Reddit API using PRAW)
def fetch_reddit_sentiment(stock_symbol, num_posts=5):
    reddit = praw.Reddit(
            client_id='dh-pJ2g7bmp5H55tgsth3w',
            client_secret='L2tiTgDrdwwb9DWtrX19CdbZqYAGsg',
            user_agent='AI-lluminati',
            username='AccomplishedMonk3736',
            password='garlandidya57'
            )
    scores = []
    
    subreddit = reddit.subreddit('all')
    #posts = subreddit.search(stock_symbol, limit=num_posts, sort='new')
    posts = subreddit.search(stock_symbol, limit=num_posts)

    print(f"\nAnalyzing {num_posts} Reddit Posts for {stock_symbol}...\n")
    
    for post in posts:
        text = post.title + " " + post.selftext
        sentiment_score = analyze_sentiment(text)
        scores.append(sentiment_score)
        print(f"Title: {post.title}\nSentiment Score: {sentiment_score}\n")
    
    return scores

# Main function to fetch and aggregate sentiment
def fetch_and_analyze_stock_sentiment(stock_symbol, num_posts=10):
    # Fetch sentiments from different platforms
    news_scores = fetch_news_sentiment(stock_symbol, num_articles=num_posts)
    reddit_scores = fetch_reddit_sentiment(stock_symbol, num_posts=num_posts)

    all_scores = news_scores + reddit_scores
    if all_scores:
        overall_score = sum(all_scores) / len(all_scores)
        overall_classification = classify_sentiment(overall_score)

        print(f"\nOverall Sentiment for {stock_symbol}: {overall_classification} ({overall_score:.2f})")
        if overall_classification == "Strong Buy": return 1
        if overall_classification == "Neutral": return 0
        if overall_classification == "Strong Sell": return -1 
        
    else:
        print(f"\nNo data available to analyze sentiment for {stock_symbol}.")



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

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        articles = data.get('articles', [])
        
        if market_type == "country":
            print(f"\nAnalyzing {num_articles} News Articles for {market_type} Stock Market ({country})\n")
        else:
            print(f"\nAnalyzing {num_articles} News Articles for {market_type} Stock Market\n")

        for article in articles[:num_articles]:
            title = article.get('title', '')
            description = article.get('description', '')
            published_at = article.get('publishedAt', '')

            print(f"Title: {title}")
            print(f"Description: {description}")
            print(f"Published At: {published_at}")
            print("-" * 80)

            if title and description and "[Removed]" not in title and "[Removed]" not in description:
                text = title + " " + description
                sentiment_score = analyze_sentiment(text)
                scores.append(sentiment_score)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
    
    return scores

# Example usage
#fetch_and_analyze_stock_sentiment('Zomato', num_posts=10)
#fetch_and_analyze_market_sentiment(market_type="country", country="Canada", num_articles=5)
#fetch_and_analyze_market_sentiment(market_type="global", num_articles=5)


# Main entry point for execution
if __name__ == "__main__":
    # Example usage
    print("Fetching and analyzing sentiment for Zomato stock...")
    fetch_and_analyze_stock_sentiment('Zomato', num_posts=10)

    print("Fetching and analyzing sentiment for global stock market...")
    fetch_market_sentiment(market_type="global", num_articles=5)

    print("Fetching and analyzing sentiment for stock market in India...")
    fetch_market_sentiment(market_type="country", country="India", num_articles=5)