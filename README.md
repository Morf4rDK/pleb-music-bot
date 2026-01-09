# Pleb Discord Music Bot 🎵

A Discord bot that plays music from YouTube and SoundCloud using Docker.

## Features

- 🎵 Play music from YouTube and SoundCloud
- 📝 Queue management
- ⏸️ Pause/Resume playback
- ⏭️ Skip tracks
- 🔁 Loop current song
- 🐳 Docker support

## Commands

- `!play <song/url>` or `!p <song/url>` - Play a song
- `!skip` or `!s` - Skip current song
- `!pause` - Pause playback
- `!resume` - Resume playback
- `!stop` - Stop and clear queue
- `!queue` or `!q` - Show current queue
- `!loop` - Toggle loop for current song
- `!leave` or `!dc` - Disconnect from voice channel

## Setup

### Prerequisites

- Docker and Docker Compose installed
- A Discord bot token ([Create one here](https://discord.com/developers/applications))

### Installation

1. **Clone or create the project directory:**
   ```bash
   mkdir discord-music-bot
   cd discord-music-bot
   ```

2. **Create the required files:**
   - `bot.py` - Main bot code
   - `Dockerfile` - Docker configuration
   - `docker-compose.yml` - Docker Compose configuration
   - `requirements.txt` - Python dependencies
   - `.env` - Environment variables

3. **Set up your Discord bot token:**
   ```bash
   cp .env.example .env
   # Edit .env and add your Discord token
   ```

4. **Build and run with Docker:**
   ```bash
   docker-compose up -d
   ```

### Bot Permissions

When inviting your bot to a server, make sure it has these permissions:
- Read Messages/View Channels
- Send Messages
- Connect
- Speak
- Use Voice Activity

**Invite URL format:**
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=3148800&scope=bot
```

## Usage

1. Join a voice channel in your Discord server
2. Use `!play <song name or URL>` to start playing music
3. The bot will join your voice channel and start playing

**Examples:**
```
!play never gonna give you up
!play https://www.youtube.com/watch?v=dQw4w9WgcXQ
!play https://soundcloud.com/artist/track
```

## Docker Commands

**Start the bot:**
```bash
docker-compose up -d
```

**Stop the bot:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Rebuild after code changes:**
```bash
docker-compose up -d --build
```

## Troubleshooting

**Bot not responding:**
- Check logs: `docker-compose logs -f`
- Verify your bot token in `.env`
- Ensure the bot has proper permissions

**Audio issues:**
- Make sure ffmpeg is installed in the container (it's included in the Dockerfile)
- Check if the bot has "Speak" permission in the voice channel

**Can't play certain videos:**
- Some videos may be region-locked or have other restrictions
- Try updating yt-dlp: modify `requirements.txt` to use the latest version

## Notes

- The bot will automatically disconnect after 5 minutes of inactivity
- YouTube and SoundCloud links are both supported
- Search queries automatically search YouTube

## License

MIT License - Feel free to modify and use as needed!