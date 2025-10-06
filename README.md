# FL Music Bot

A Discord music bot built with **Python**, **discord.py**, and **yt-dlp**.  
It can play songs from YouTube, manage queues, and handle playlists.

---

## 🚀 Features
- Play or queue songs with `!play <song>`
- Pause, resume, skip, and leave via interactive buttons
- Playlist creation and playback using JSON storage
- Queue system for multiple songs
- Role-based restriction using `music ban`
- Modern embeds with cover art and control buttons

---

## ⚙️ Commands
| Command | Description |
|----------|--------------|
| `!play <song>` | Plays or queues a song from YouTube |
| `!playlistcreate <name> 1 <song> 2 <song> ...` | Creates a new playlist |
| `!playlist <name>` | Plays a saved playlist |
| `!leave` | Disconnects bot from voice channel |

**Buttons:**
- **Play** → Restart or resume the current song  
- **Stop** → Pause playback  
- **Next** → Play next song in queue  
- **Leave** → Disconnect the bot

---

## 🧱 Installation

1. Clone this repository or copy the bot files.
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

## 🧩 Usage

Start the bot:
```bash
python bot.py
```

In Discord:
```
!play Shape of You
!playlistcreate workout 1 Eminem - Lose Yourself 2 NF - The Search
!playlist workout
```

---

## 🔒 Permissions

Make sure the bot has these permissions:
- Connect
- Speak
- Read Messages
- Use Slash Commands (optional)

---

## ⚠️ Role Restriction

Users with the role **music ban** cannot use any bot command or buttons.

---

## 🗂️ File Structure
```
MusicBot/
├── bot.py
├── playlists.json
├── .env
├── venv/
└── README.md
```

---

## 🧠 Notes
- The bot uses `yt-dlp` for streaming YouTube audio.
- JSON is used for playlist storage.
- Each server has its own queue and playback state.

---

## 🛠️ Author
Developed by **Filip P.** with ❤️ for automation and music.

