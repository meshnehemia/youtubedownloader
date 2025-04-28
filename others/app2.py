from flask import Flask, request, send_file, render_template_string
from pytube import YouTube
import os

app = Flask(__name__)

# HTML templates
INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <title>YouTube Video Downloader</title>
    <style>
      body { font-family: Arial; margin: 50px; text-align: center; }
      input, button, select { padding: 10px; margin: 10px; width: 300px; }
      .stream-info { margin: 20px auto; max-width: 600px; text-align: left; }
      .thumbnail { max-width: 200px; margin: 10px 0; }
    </style>
  </head>
  <body>
    <h1>Download YouTube Video</h1>
    <form action="/streams" method="post">
      <input type="text" name="url" placeholder="Enter YouTube URL" required/>
      <br>
      <button type="submit">Show Available Streams</button>
    </form>
  </body>
</html>
"""

STREAMS_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <title>Available Streams</title>
    <style>
      body { font-family: Arial; margin: 50px; text-align: center; }
      .stream-info { margin: 20px auto; max-width: 600px; text-align: left; }
      .thumbnail { max-width: 200px; margin: 10px 0; }
      button { padding: 10px; margin: 10px; }
    </style>
  </head>
  <body>
    <h1>{{ title }}</h1>
    <img class="thumbnail" src="{{ thumbnail_url }}" alt="Video thumbnail">
    
    <h2>Available Streams:</h2>
    <form action="/download" method="post">
      <input type="hidden" name="url" value="{{ url }}">
      {% for stream in streams %}
        <div class="stream-info">
          <input type="radio" name="itag" value="{{ stream.itag }}" id="{{ stream.itag }}" required>
          <label for="{{ stream.itag }}">
            {{ stream.mime_type }} - {{ stream.resolution or stream.abr }} - {{ stream.filesize_approx|round(2) }}MB
          </label>
        </div>
      {% endfor %}
      <button type="submit">Download Selected Stream</button>
    </form>
    <br>
    <a href="/">Back to Home</a>
  </body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(INDEX_HTML)

@app.route('/streams', methods=['POST'])
def show_streams():
    url = request.form['url']
    try:
        yt = YouTube(url)
        # Filter streams to show progressive (video+audio) and audio-only streams
        streams = yt.streams.filter(progressive=True).order_by('resolution').desc() + \
                 yt.streams.filter(only_audio=True).order_by('abr').desc()
        
        return render_template_string(
            STREAMS_HTML,
            title=yt.title,
            thumbnail_url=yt.thumbnail_url,
            url=url,
            streams=streams
        )
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    itag = request.form['itag']
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        filepath = stream.download()

        # Clean up filename
        filename = f"{yt.title.replace(' ', '_')}.{stream.subtype}"
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype=stream.mime_type
        )
    except Exception as e:
        return f"Error: {str(e)}", 400
    finally:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)