# app.py

from flask import Flask, render_template, request
from Senti import extract_video_id,analyze_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv,get_channel_info,youtube,get_channel_id,get_video_stats

import os
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO



app = Flask(__name__)

def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

def generate_chart(results, chart_type):
    num_neutral = results.get('num_neutral', 0)
    num_positive = results.get('num_positive', 0)
    num_negative = results.get('num_negative', 0)

    if chart_type == 'bar':
        df = pd.DataFrame({
            'Sentiment': ['Positive', 'Negative', 'Neutral'],
            'Number of Comments': [num_positive, num_negative, num_neutral]
        })

        fig = px.bar(
            df, x='Sentiment', y='Number of Comments',
            color='Sentiment', color_discrete_sequence=['#87CEFA', '#FFA07A', '#D3D3D3'],
            title='Sentiment Analysis Results'
        )
    elif chart_type == 'pie':
        labels = ['Neutral', 'Positive', 'Negative']
        values = [num_neutral, num_positive, num_negative]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                     marker=dict(colors=['yellow', 'green', 'red']))])
    else:
        return None

    # Save the chart to a BytesIO object
    image_stream = BytesIO()
    fig.write_image(image_stream, format="png")
    image_stream.seek(0)

    # Convert the image to base64 for embedding in HTML
    encoded_image = base64.b64encode(image_stream.read()).decode("utf-8")

    return f"data:image/png;base64,{encoded_image}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_link = request.form['youtube_link']
        video_id = extract_video_id(youtube_link)
        channel_id = get_channel_id(video_id)

        if video_id:
            # Define directory_path here
            directory_path = os.getcwd()  # You may want to specify a different path

            csv_file = save_video_comments_to_csv(video_id)
            delete_non_matching_csv_files(directory_path, video_id)

            channel_info = get_channel_info(youtube, channel_id)
            stats = get_video_stats(video_id)
            results = analyze_sentiment(csv_file)
        

            # Generate HTML strings for charts
            bar_chart_image = generate_chart(results, 'bar')
            pie_chart_image = generate_chart(results, 'pie')
            return render_template('index.html',
                                    video_id = video_id,
                                   channel_info=channel_info,
                                   stats=stats,
                                   results=results,
                                   bar_chart_image=bar_chart_image,  # Correct variable name
                                   pie_chart_image=pie_chart_image)  # Correct variable name
        else:
            return render_template('index.html', error="Invalid YouTube link")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
