from transformers import pipeline

# Sentiment analysis 모델 로드
sentiment_analyzer = pipeline('sentiment-analysis')

def analyze_message(message):
    result = sentiment_analyzer(message)
    return result
