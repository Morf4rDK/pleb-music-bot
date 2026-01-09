import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Queue for each guild
queues = {}

ytdl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)

class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.loop = False

    def add(self, item):
        self.queue.append(item)

    def next(self):
        if self.loop and self.current:
            return self.current
        if self.queue:
            self.current = self.queue.popleft()
            return self.current
        self.current = None
        return None

    def clear(self):
        self.queue.clear()
        self.current = None

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = MusicQueue()
    return queues[guild_id]

async def play_next(ctx):
    guild_id = ctx.guild.id
    queue = get_queue(guild_id)
    
    if ctx.voice_client is None:
        return

    item = queue.next()
    if item is None:
        await asyncio.sleep(300)  # Wait 5 min then disconnect
        if ctx.voice_client and not ctx.voice_client.is_playing():
            await ctx.voice_client.disconnect()
        return

    try:
        data = await asyncio.get_event_loop().run_in_executor(
            None, lambda: ytdl.extract_info(item['url'], download=False)
        )
        
        if 'entries' in data:
            data = data['entries'][0]

        url = data['url']
        source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
        
        ctx.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )
        
        await ctx.send(f"🎵 Now playing: **{data.get('title', 'Unknown')}**")
    except Exception as e:
        await ctx.send(f"❌ Error playing track: {str(e)}")
        await play_next(ctx)

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')

@bot.command(name='play', aliases=['p'])
async def play(ctx, *, query):
    """Play a song from YouTube or SoundCloud"""
    if ctx.author.voice is None:
        await ctx.send("❌ You need to be in a voice channel!")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    elif ctx.voice_client.channel != ctx.author.voice.channel:
        await ctx.voice_client.move_to(ctx.author.voice.channel)

    queue = get_queue(ctx.guild.id)
    
    await ctx.send(f"🔍 Searching for: **{query}**")
    
    try:
        data = await asyncio.get_event_loop().run_in_executor(
            None, lambda: ytdl.extract_info(f"ytsearch:{query}", download=False)
        )
        
        if 'entries' in data:
            data = data['entries'][0]
        
        queue.add({'url': data['webpage_url'], 'title': data.get('title', 'Unknown')})
        
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
        else:
            await ctx.send(f"➕ Added to queue: **{data.get('title', 'Unknown')}**")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    """Skip the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped!")

@bot.command(name='stop')
async def stop(ctx):
    """Stop playing and clear the queue"""
    queue = get_queue(ctx.guild.id)
    queue.clear()
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped and cleared queue!")

@bot.command(name='pause')
async def pause(ctx):
    """Pause the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused!")

@bot.command(name='resume')
async def resume(ctx):
    """Resume the paused song"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed!")

@bot.command(name='queue', aliases=['q'])
async def show_queue(ctx):
    """Show the current queue"""
    queue = get_queue(ctx.guild.id)
    if queue.current is None and not queue.queue:
        await ctx.send("📭 Queue is empty!")
        return
    
    msg = "**Current Queue:**\n"
    if queue.current:
        msg += f"🎵 Now: {queue.current['title']}\n\n"
    
    if queue.queue:
        msg += "**Up Next:**\n"
        for i, item in enumerate(list(queue.queue)[:10], 1):
            msg += f"{i}. {item['title']}\n"
    
    await ctx.send(msg)

@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def leave(ctx):
    """Make the bot leave the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left voice channel!")

@bot.command(name='loop')
async def loop(ctx):
    """Toggle loop for current song"""
    queue = get_queue(ctx.guild.id)
    queue.loop = not queue.loop
    status = "enabled" if queue.loop else "disabled"
    await ctx.send(f"🔁 Loop {status}!")

if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable not set")
    bot.run(TOKEN)