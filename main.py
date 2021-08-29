from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
from discord.ext.commands import Bot
import discord
import asyncio

TOCKEN = 'ODgwOTExNzUxODUwMzgxMzIy.YSlLAA.5O8QQmwE6EhzZ1LKdHdLoVZvnYM'
PREFIX = '/'
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

loop = asyncio.get_event_loop()

client = discord.Client()

playlist = []
next_music_num = 0

voice = None
in_voice_channel = False
start_play = False
global_channel = None

bot = Bot(command_prefix='!')

@bot.command()
async def now_playing_func(ctx):
    title_text = f'Now playing [{get_name(playlist[next_music_num])}]({playlist[next_music_num]})'
    embed = discord.Embed(color=0x0000ff, description=title_text)
    await ctx.send(embed=embed)

async def next_music(e):
    global voice
    global playlist
    global start_play

    if next_music_num < len(playlist):
        await now_playing_func(global_channel)
        await play_music(voice, playlist[next_music_num])
        start_play = True
    else:
        start_play = False

async def play_music(vc, url):
    global next_music_num
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        next_music_num += 1
        
        vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: loop.create_task(next_music(1)))

def get_name(src):
    youtubeVideo = VideosSearch(src, limit = 1)
    name = youtubeVideo.result()['result'][0]['title']
    return name

@client.event
async def on_message(message):
    global in_voice_channel
    global voice
    global playlist
    global next_music_num
    global global_channel

    global_channel = message.channel
    if in_voice_channel == False:
        channel = client.get_channel(message.author.voice.channel.id)
        voice = await channel.connect()
        in_voice_channel = True

    if message.content.startswith(PREFIX + 'play'):
        search_text = ' '.join(message.content.split()[1:])
        youtubeVideo = VideosSearch(search_text, limit = 1)
        src = youtubeVideo.result()['result'][0]['link']

        playlist.append(src)

        title_text = f'Queded [{get_name(playlist[-1])}]({playlist[-1]})'
        embed = discord.Embed(color=0x0000ff, description=title_text)
        await message.channel.send(embed=embed)

        if start_play == False:
            await next_music(next_music_num)

    if message.content.startswith(PREFIX + 'pause'):
        voice.pause()

        embed = discord.Embed(color=0x0000ff, title="Pause")
        await message.channel.send(embed=embed)

    if message.content.startswith(PREFIX + 'stop'):
        voice.pause()
        playlist = []
        await next_music(next_music_num)
        next_music_num = 0

        embed = discord.Embed(color=0x0000ff, title="Stop")
        await message.channel.send(embed=embed)

    if message.content.startswith(PREFIX + 'next'):
        #If playlist have music
        if next_music_num + 1 < len(playlist) + 1:
            #Stop music
            voice.pause()
            #Play next music
            await next_music(next_music_num)
            #Play music
            voice.resume()

    if message.content.startswith(PREFIX + 'prev'):
        if next_music_num > 1:
            #Stop music
            voice.pause()
            #next_music_num - 2, before +1 in next_music_num -> play_music
            next_music_num -= 2
            await next_music(next_music_num)
            #Play music
            voice.resume()


    if message.content.startswith(PREFIX + 'resume') and len(playlist) > 0:
        #Play music
        voice.resume()
        #Send message in chat
        embed = discord.Embed(color=0x0000ff, title="Pause")
        await message.channel.send(embed=embed)

#discord.errors.ClientException: Already connected to a voice channel.
client.run(TOCKEN)