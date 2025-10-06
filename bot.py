import discord
from discord.ext import commands
from discord.ui import View, Button
import yt_dlp
from dotenv import load_dotenv
import os
import asyncio
import json

PLAYLIST_FILE = "playlists.json"

def load_playlists():
    if not os.path.exists(PLAYLIST_FILE):
        return {}
    with open(PLAYLIST_FILE, "r") as f:
        return json.load(f)

def save_playlists(data):
    with open(PLAYLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

queues = {}

last_bot_message = {}

current_song = {}

paused = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.check
async def check_music_ban(ctx):
    if any(role.name.lower() == "music ban" for role in ctx.author.roles):
        return False
    return True

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return
    raise error

class MusicControls(View):
    def __init__(self, voice_client, guild_id, text_channel):
        super().__init__(timeout=None)
        self.voice_client = voice_client
        self.guild_id = guild_id
        self.text_channel = text_channel

    async def play_next_song(self):
        queue = queues.get(self.guild_id, [])
        if queue:
            next_song = queue.pop(0)
            queues[self.guild_id] = queue
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.stop()
            msg = last_bot_message.get(self.guild_id)
            if msg:
                try:
                    await msg.delete()
                except:
                    pass
            await play_song(self.voice_client, next_song, self.guild_id, self.text_channel)

    @discord.ui.button(label="Play", style=discord.ButtonStyle.green)
    async def play_button(self, interaction: discord.Interaction, button: Button):
        if any(role.name.lower() == "music ban" for role in interaction.user.roles):
            await interaction.response.send_message("You are banned from using music commands.", ephemeral=True)
            return
        if self.voice_client:
            song_info = current_song.get(self.guild_id)
            if song_info:
                if self.voice_client.is_paused():
                    self.voice_client.resume()
                    paused[self.guild_id] = False
                    await interaction.response.defer()
                else:
                    if self.voice_client.is_playing():
                        self.voice_client.stop()
                    msg = last_bot_message.get(self.guild_id)
                    if msg:
                        try:
                            await msg.delete()
                        except:
                            pass
                    await play_song(self.voice_client, song_info, self.guild_id, self.text_channel)
                    await interaction.response.defer()
            else:
                await interaction.response.send_message("No song to play.", ephemeral=True)
        else:
            await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        if any(role.name.lower() == "music ban" for role in interaction.user.roles):
            await interaction.response.send_message("You are banned from using music commands.", ephemeral=True)
            return
        if self.voice_client:
            if self.voice_client.is_playing():
                self.voice_client.pause()
                paused[self.guild_id] = True
                await interaction.response.defer()
            elif self.voice_client.is_paused():
                await interaction.response.send_message("Already paused.", ephemeral=True)
            else:
                await interaction.response.send_message("Nothing to pause.", ephemeral=True)
        else:
            await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if any(role.name.lower() == "music ban" for role in interaction.user.roles):
            await interaction.response.send_message("You are banned from using music commands.", ephemeral=True)
            return
        queue = queues.get(self.guild_id, [])
        if not queue:
            await interaction.response.send_message("Nothing in queue", ephemeral=True)
            return
        msg = last_bot_message.get(self.guild_id)
        if msg:
            try:
                await msg.delete()
            except:
                pass
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        else:
            await self.play_next_song()
        await interaction.response.defer()

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.grey)
    async def leave_button(self, interaction: discord.Interaction, button: Button):
        if any(role.name.lower() == "music ban" for role in interaction.user.roles):
            await interaction.response.send_message("You are banned from using music commands.", ephemeral=True)
            return
        msg = last_bot_message.get(self.guild_id)
        if msg:
            try:
                await msg.delete()
            except:
                pass
        if self.voice_client:
            await self.voice_client.disconnect()

async def play_song(voice_client, song_info, guild_id, text_channel):
    url = song_info["url"]
    title = song_info["title"]
    author = song_info["author"]
    thumbnail = song_info.get("thumbnail")

    source = await discord.FFmpegOpusAudio.from_probe(url, method="fallback")
    voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(voice_client, guild_id, text_channel), bot.loop))

    current_song[guild_id] = song_info
    paused[guild_id] = False

    embed = discord.Embed(title=title, description=f"By {author}", color=0x1DB954)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text="MusicBot")

    view = MusicControls(voice_client, guild_id, text_channel)
    message = await text_channel.send(embed=embed, view=view)
    last_bot_message[guild_id] = message

async def play_next(voice_client, guild_id, text_channel):
    queue = queues.get(guild_id, [])
    if queue:
        next_song = queue.pop(0)
        queues[guild_id] = queue
        await play_song(voice_client, next_song, guild_id, text_channel)
        
@bot.command(name="playlistcreate")
async def playlistcreate(ctx, playlist_name: str, *, songs: str):
    playlists = load_playlists()
    parts = songs.split()
    playlist = []
    current_song = []
    for part in parts:
        if part.isdigit():
            if current_song:
                playlist.append(" ".join(current_song))
                current_song = []
        else:
            current_song.append(part)
    if current_song:
        playlist.append(" ".join(current_song))

    if not playlist:
        await ctx.send("No valid songs provided.")
        return

    playlists[playlist_name] = playlist
    save_playlists(playlists)
    await ctx.send(f"Playlist **{playlist_name}** saved with {len(playlist)} songs.")

@bot.command(name="playlist")
async def playlist(ctx, playlist_name: str):
    playlists = load_playlists()
    if playlist_name not in playlists:
        await ctx.send("Playlist not found.")
        return

    playlist_songs = playlists[playlist_name]
    await ctx.send(f"Loading playlist **{playlist_name}** ({len(playlist_songs)} songs)")

    guild_id = ctx.guild.id
    voice_client = ctx.voice_client
    if not voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            voice_client = ctx.voice_client
        else:
            await ctx.send("Join a voice channel first.")
            return

    first_song = playlist_songs[0]
    remaining = playlist_songs[1:]
    ydl_opts = {"format": "bestaudio", "noplaylist": True}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{first_song}", download=False)["entries"][0]
        song_info = {
            "url": info["url"],
            "title": info["title"],
            "author": info.get("uploader", "Unknown"),
            "thumbnail": info.get("thumbnail", None),
        }

    await play_song(voice_client, song_info, guild_id, ctx.channel)

    for song in remaining:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song}", download=False)["entries"][0]
            queued = {
                "url": info["url"],
                "title": info["title"],
                "author": info.get("uploader", "Unknown"),
                "thumbnail": info.get("thumbnail", None),
            }
        queue = queues.get(guild_id, [])
        queue.append(queued)
        queues[guild_id] = queue

@bot.command()
async def play(ctx, *, query):
    guild_id = ctx.guild.id
    voice_client = ctx.voice_client
    if not voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            voice_client = ctx.voice_client
        else:
            await ctx.send("Join a voice channel first.")
            return

    ydl_opts = {"format": "bestaudio", "noplaylist": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
        url = info["url"]
        title = info["title"]
        author = info.get("uploader", "Unknown")
        thumbnail = info.get("thumbnail", None)

    song_info = {"url": url, "title": title, "author": author, "thumbnail": thumbnail}

    if voice_client.is_playing():
        queue = queues.get(guild_id, [])
        queue.append(song_info)
        queues[guild_id] = queue
        await ctx.send(f"Added **{title}** to the queue.")
    else:
        await play_song(voice_client, song_info, guild_id, ctx.channel)

@bot.command()
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
    else:
        await ctx.send("I'm not connected to any voice channel.")

bot.run(TOKEN)