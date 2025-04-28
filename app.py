from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify,session
import yt_dlp
import os
import threading
import re
from werkzeug.utils import secure_filename
from datetime import timedelta
import secrets
from business_login import download_history, loggin,new_user,new_history

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
app.config['DOWNLOAD_FOLDER'] = os.path.abspath(DOWNLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 * 1024  # 4GB max download size
download_progress = {
    'status': 'idle',
    'percentage': '0%',
    'speed': '',
    'eta': '',
    'filename': '',
    'error': None
}

@app.route('/')
def home():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('home.html', first_name=session['first_name'], last_name=session['last_name'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login-email']
        password = request.form['login-password']
        user_login = loggin.UserLogin()
        success, result = user_login.login_user(email, password)
        if success:
            session['id'] = result['id']
            session['first_name'] = result['first_name']
            session['last_name'] = result['last_name']
            session['email'] = result['email']
            return jsonify({'success': True, 'redirect': url_for('home')}) ,200
        else:
            return jsonify({'success':False, 'error': result}), 200
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    user_registration = new_user.UserRegistration()
    if user_registration.connect():
        success,message = user_registration.register_user(first_name, last_name, email, password, confirm_password)
        user_registration.close()
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})
    else:
        return jsonify({'success': False, 'message': 'Database connection failed'})
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def is_authenticated():
    if 'id' in session:
        return True 
    return False

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    return filename.strip()

@app.route('/information/url', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = info.get('formats', [])
            videos = []
            audios = []

            for f in formats:
                if f.get('vcodec') != 'none':
                    videos.append(f)
                elif f.get('acodec') != 'none':
                    audios.append(f)
            
            # Sort videos by resolution and file size
            videos.sort(key=lambda x: (
                -1 * int(x.get('height', 0)) if x.get('height') else 0,
                x.get('filesize') or 0
            ))
            
            # Sort audio by bitrate and file size
            audios.sort(key=lambda x: (
                -1 * int(x.get('abr', 0)) if x.get('abr') else 0,
                x.get('filesize') or 0
            ))

            return {
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'videos': videos[:20],  # Limit to top 20 formats
                'audios': audios[:10],    # Limit to top 10 audio formats
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'original_url': url
            }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None

def download_video(url, format_id):
    global download_progress
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            download_progress['status'] = 'downloading'
            download_progress['percentage'] = d.get('_percent_str', '0%')
            download_progress['speed'] = d.get('_speed_str', '')
            download_progress['eta'] = d.get('_eta_str', '')
        elif d['status'] == 'finished':
            download_progress['status'] = 'finished'
            download_progress['filename'] = d.get('filename', '')
    
    try:
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
            'quiet': True,
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'restrictfilenames': True,  # This helps with filename issues
            'merge_output_format': 'mp4'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Get the actual filename that will be used
            temp_filename = ydl.prepare_filename(info)
            download_progress['filename'] = os.path.basename(temp_filename)
            ydl.download([url])
            
    except Exception as e:
        download_progress['status'] = 'error'
        download_progress['error'] = str(e)
        print(f"Error during download: {e}")

@app.route('/media_check', methods=['GET', 'POST'])
def Media_check():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return jsonify({'success': False, 'error': 'Please enter a YouTube URL'}), 302
        if 'youtube.com' not in url and 'youtu.be' not in url:
            return({'success':False,'error':'Please enter a valid Youtube URL'}),302
        video_info = get_video_info(url)
        if not video_info:
            return jsonify({'success': False, 'error': 'Failed to retrieve video information'}), 302
        return jsonify({'success': True, 'video_info': video_info, 'url': url}), 200
        
@app.route('/download', methods=['POST'])
def download():
    global download_progress
    
    url = request.form.get('url')
    format_id = request.form.get('format_id')
    
    if not url or not format_id:
        flash('Invalid request parameters', 'error')
        return redirect(url_for('index'))
    
    download_progress = {
        'status': 'starting',
        'percentage': '0%',
        'speed': '',
        'eta': '',
        'filename': '',
        'error': None
    }
    
    thread = threading.Thread(target=download_video, args=(url, format_id))
    thread.start()
    
    return render_template('download_progress.html', url=url)

@app.route('/progress')
def progress():
    global download_progress
    return jsonify(download_progress)

@app.route('/download_complete')
def download_complete():
    global download_progress
    if download_progress['status'] == 'finished':
        filename = os.path.basename(download_progress['filename'])
        return render_template('complete.html', filename=filename)
    else:
        flash('Download not complete or failed', 'error')
        return redirect(url_for('index'))

@app.route('/download_file/<path:filename>')
def download_file(filename):
    # First try with the original filename (path included for safety)
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    
    # If not found, try with secure_filename version
    if not os.path.exists(file_path):
        safe_filename = secure_filename(filename)
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], safe_filename)
    
    # If still not found, try replacing %20 with spaces
    if not os.path.exists(file_path):
        decoded_filename = filename.replace('%20', ' ')
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], decoded_filename)
    
    if not os.path.exists(file_path):
        flash('File not found. It may have expired or been deleted.', 'error')
        return redirect(url_for('index'))
    
    # Get the proper filename for download
    download_name = os.path.basename(file_path)
    
    # Send file with original filename but sanitized for safety
    response = send_file(
        file_path,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/octet-stream'
    )
    
    # Cleanup after download
    @response.call_on_close
    def cleanup():
        try:
            os.remove(file_path)
        except Exception as e:
            app.logger.error(f"Error deleting file: {e}")
    
    return response
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/register_download_history', methods=['POST'])
def register_download_history():
    # Get the data from the request (JSON)
    data = request.get_json()

    # Extract data from the request body
    video_title = data.get('video_title')
    downloaded_by = session['id']
    duration = data.get('duration')
    video_link = data.get('video_link')
    resolution = data.get('resolution')
    file_size = data.get('file_size')
    file_type = data.get('file_type')

    # Create a UserLogin instance
    user_login = new_history.Userhistory()

    # Call the register_download_history method from the class
    status, message = user_login.register_download_history(
        video_title, downloaded_by, duration, video_link, resolution, file_size, file_type
    )

    # Return a JSON response with the status and message
    return jsonify({"status": status, "message": message})

@app.route('/get_download_history', methods=['GET'])
def get_download_history():
    """ API endpoint to get download history for a user """
    user_id = session['id']  # Get user_id from the query parameters
    if not user_id:
        return jsonify({"status": False, "message": "❌ User ID is required."})

    # Instantiate UserHistory and get download history
    user_history =download_history.UserHistory()
    status, result = user_history.get_download_history(user_id)

    if status:
        return jsonify({"status": True, "history": result})
    else:
        return jsonify({"status": False, "message": result})


if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'production':
        print("Starting production server...")
        app.run(host='0.0.0.0', port=5000)
    else:
        print("""
        ⚠️ WARNING ⚠️
        This is a development server. For production use:
        1. Install gunicorn: pip install gunicorn
        2. Run: gunicorn -w 4 -b 0.0.0.0:5000 app:app
        """)
        app.run(debug=True)