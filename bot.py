import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")

@bot.command()
async def тест(ctx):
    await ctx.send("✅ Бот работает! Хостинг ок.")

token = os.getenv("TOKEN")

if not token:
    raise RuntimeError("TOKEN не найден")

bot.run(token)

