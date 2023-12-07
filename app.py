# app.py

from flask import Flask, render_template, request
from Senti import extract_video_id,analyze_sentiment,generate_bar_chart,generate_pie_chart
from YoutubeCommentScrapper import (save_video_comments_to_csv,
                                    get_channel_info,
                                    youtube,
                                    get_channel_id,
                                    get_video_stats                              
)
import os




app = Flask(__name__)

def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))


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
            bar_chart_image = generate_bar_chart(results)
            pie_chart_image = generate_pie_chart(results)
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
