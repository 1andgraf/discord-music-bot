# Discord Music Bot

A music bot built with **Python**, **discord.py**, and **yt-dlp**.  
It can play songs, manage queues and playlists.

## ⚙️ Commands
| Command | Description |
|----------|--------------|
| `!play <song>` | Plays or queues a song from YouTube |
| `!playlistcreate <playlistname> 1 <song> 2 <song> 3...` | Creates a new playlist |
| `!playlist <name>` | Plays a saved playlist |
| `!leave` | Disconnects bot from voice channel |

Users with the role **music ban** cannot make any bot interactions.

## 🧱 Installation

1. Clone this repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -U discord.py[voice] yt-dlp ffmpeg-python python-dotenv pynacl
   ```
4. Install **FFmpeg** (required for audio).
5. Create a `.env` file in your project directory:
   ```env
   TOKEN=YOUR_DISCORD_BOT_TOKEN
   ```
---

The bot needs these permissions to work on the servers:
- Connect
- Speak
- Read Messages
