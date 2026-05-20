# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import yt_dlp
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True
}

def search_youtube(query):
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        if not query.startswith("http"):
            query = f"ytsearch:{query}"
        info = ydl.extract_info(query, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["url"], info["title"]

@bot.command(name="دخل")
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("لازم تكون في قناة صوتية أول!")
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"✅ انتقلت إلى: **{channel.name}**")
    else:
        await channel.connect()
        await ctx.send(f"✅ دخلت: **{channel.name}**")

@bot.command(name="شغل")
async def play(ctx, *, query):
    if not ctx.author.voice:
        await ctx.send("لازم تكون في قناة صوتية!")
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)
    await ctx.send(f"🔍 جاري البحث عن: **{query}**")
    audio_url, title = search_youtube(query)
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    ctx.voice_client.play(
        discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS)
    )
    await ctx.send(f"🎵 يشتغل الآن: **{title}**")

@bot.command(name="وقف")
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ تم الإيقاف")
    else:
        await ctx.send("مافيه شي يشتغل!")

@bot.command(name="استراحة")
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ تم الإيقاف المؤقت")

@bot.command(name="كمل")
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ تم الاستمرار")

@bot.command(name="اطلع")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 وداعاً!")

@bot.event
async def on_ready():
    print(f"البوت شغال: {bot.user}")

bot.run(os.environ["TOKEN"])
