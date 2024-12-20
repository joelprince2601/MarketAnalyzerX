import requests
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob

NEWS_API_KEY = '3ee0afaff900479f882f5a6686d48e82'
BASE_URL = 'https://newsapi.org/v2/everything'

def get_company_news(company_name, days=7):
    """
    Fetch news articles for a specific company from NewsAPI
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    params = {
        'q': company_name,
        'from': start_date.strftime('%Y-%m-%d'),
        'to': end_date.strftime('%Y-%m-%d'),
        'sortBy': 'relevancy',
        'language': 'en',
        'apiKey': NEWS_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        news_data = response.json()
        
        if news_data['status'] == 'ok':
            articles = news_data['articles']
            return process_news_articles(articles)
        else:
            return None, None, []
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return None, None, []

def analyze_sentiment(text):
    """
    Analyze sentiment of text using TextBlob
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity

def process_news_articles(articles):
    """
    Process and analyze news articles
    """
    if not articles:
        return None, None, []
    
    # Create a list to store processed articles
    processed_articles = []
    sentiment_scores = []
    
    for article in articles[:10]:  # Process top 10 articles
        title = article.get('title', '')
        description = article.get('description', '')
        
        # Calculate sentiment
        combined_text = f"{title} {description}"
        sentiment = analyze_sentiment(combined_text)
        sentiment_scores.append(sentiment)
        
        processed_articles.append({
            'title': title,
            'description': description,
            'url': article.get('url', ''),
            'published_at': article.get('publishedAt', ''),
            'source': article.get('source', {}).get('name', ''),
            'sentiment': sentiment
        })
    
    # Calculate average sentiment
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Create news summary
    news_summary = create_news_summary(processed_articles)
    
    return avg_sentiment, news_summary, processed_articles

def create_news_summary(articles):
    """
    Create a summary of news sentiment and key points
    """
    if not articles:
        return "No recent news available."
    
    positive_news = [a for a in articles if a['sentiment'] > 0.1]
    negative_news = [a for a in articles if a['sentiment'] < -0.1]
    neutral_news = [a for a in articles if -0.1 <= a['sentiment'] <= 0.1]
    
    summary = []
    
    if positive_news:
        summary.append(f"Positive News ({len(positive_news)}): {positive_news[0]['title']}")
    
    if negative_news:
        summary.append(f"Negative News ({len(negative_news)}): {negative_news[0]['title']}")
    
    if neutral_news:
        summary.append(f"Neutral News ({len(neutral_news)}): {neutral_news[0]['title']}")
    
    return "\n".join(summary)

def get_market_news():
    """
    Get general market news and trends
    """
    params = {
        'q': 'stock market OR financial markets',
        'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        'sortBy': 'relevancy',
        'language': 'en',
        'apiKey': NEWS_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        news_data = response.json()
        
        if news_data['status'] == 'ok':
            articles = news_data['articles'][:5]  # Get top 5 market news
            return [{
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', '')
            } for article in articles]
        return []
    except Exception as e:
        print(f"Error fetching market news: {str(e)}")
        return []

def get_news_analysis(company_name):
    """
    Main function to get comprehensive news analysis
    """
    # Get company-specific news
    sentiment, summary, articles = get_company_news(company_name)
    
    # Get general market news
    market_news = get_market_news()
    
    return {
        'company_sentiment': sentiment,
        'news_summary': summary,
        'recent_articles': articles,
        'market_news': market_news
    } 
