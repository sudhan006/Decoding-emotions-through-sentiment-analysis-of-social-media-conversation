# Import libraries
from googleapiclient.discovery import build
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
import re

# Download necessary nltk data
nltk.download('punkt')

# Your YouTube API Key
API_KEY = 'AIzaSyCnIxU9yDPMGsyelhNGOXNXvCx2Bzc8Xwc'

# Initialize YouTube API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Function to extract Video ID from URL
def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

# Function to get comments from a video
def get_comments(video_id, max_comments=100):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
    response = request.execute()

    while response and len(comments) < max_comments:
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
            if len(comments) >= max_comments:
                break
        if 'nextPageToken' in response:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                pageToken=response['nextPageToken'],
                maxResults=100,
                textFormat="plainText"
            )
            response = request.execute()
        else:
            break
    return comments

# Sentiment analysis function
def analyze_sentiment(comment):
    analysis = TextBlob(comment)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        return 'Positive'
    elif polarity == 0:
        return 'Neutral'
    else:
        return 'Negative'

# Main function
def main():
    # Ask for YouTube URL
    url = input("Enter YouTube Video URL: ")
    video_id = extract_video_id(url)

    if not video_id:
        print("Invalid YouTube URL. Please try again.")
        return

    max_comments = int(input("Enter number of comments to fetch: "))

    print("Fetching comments...")
    comments = get_comments(video_id, max_comments)

    print(f"Fetched {len(comments)} comments.")

    # Create DataFrame
    df = pd.DataFrame({'Comment': comments})
    # Analyze sentiment
    df['Sentiment'] = df['Comment'].apply(analyze_sentiment)

    # Save to CSV
    df.to_csv('youtube_comment_sentiment.csv', index=False)
    print("Results saved to 'youtube_comment_sentiment.csv'.")

    # Plot
    plt.figure(figsize=(8,6))
    sns.countplot(x='Sentiment', data=df, palette='Set3')
    plt.title('YouTube Comments Sentiment Analysis')
    plt.xlabel('Sentiment')
    plt.ylabel('Number of Comments')
    plt.savefig('youtube_sentiment_plot.png')
    plt.show()

# Run the script
if __name__ == "__main__":
    main()
