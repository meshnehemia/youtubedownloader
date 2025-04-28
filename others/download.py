import yt_dlp

# Ask for the URL
url = input("Enter YouTube video URL: ")

# Setup
ydl_opts = {}

# Fetch video info
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)

# Display Title and Thumbnail
print(f"\n🎬 Video Title: {info['title']}")
print(f"🖼️  Cover Image Link: {info['thumbnail']}\n")

# Prepare available formats
formats = info.get('formats', [])
videos = []
audios = []

for f in formats:
    if f.get('vcodec') != 'none':  # It's a video (with or without audio)
        videos.append(f)
    elif f.get('acodec') != 'none':  # It's an audio
        audios.append(f)

# List Videos
print("📽️ Available Video Formats:")
for idx, v in enumerate(videos):
    filesize = v.get('filesize')
    filesize_str = f"{round(filesize/1024/1024, 2)}MB" if filesize else "Unknown size"
    print(f"[{idx}] {v.get('format_note', 'Unknown quality')} | {v.get('ext').upper()} | {filesize_str}")

# List Audios
print("\n🎵 Available Audio Formats:")
for idx, a in enumerate(audios):
    filesize = a.get('filesize')
    filesize_str = f"{round(filesize/1024/1024, 2)}MB" if filesize else "Unknown size"
    print(f"[{idx + len(videos)}] Audio only | {a.get('ext').upper()} | {filesize_str}")

# Ask the user
choice = input("\nEnter format number to download (or press Enter to get best quality): ")

# Download
ydl_opts = {}

if choice.strip() != "":
    choice = int(choice)
    if choice < len(videos):
        format_id = videos[choice]['format_id']
    else:
        format_id = audios[choice - len(videos)]['format_id']

    ydl_opts['format'] = format_id

print("\nDownloading... 🎬")

# Download the selected format
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
