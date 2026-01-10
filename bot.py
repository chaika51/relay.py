import discord
from discord.ext import commands
from datetime import timedelta
import re
import os

# TOKEN берётся из переменных окружения
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("❌ Переменная окружения TOKEN не найдена")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Парсер времени s/m/h/d
def parse_time(time_str: str):
    match = re.fullmatch(r"(\d+)(s|m|h|d)", time_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    return {
        "s": timedelta(seconds=value),
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value)
    }[unit]

# Проверка прав: админ или модератор
def has_access(ctx):
    return ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.moderate_members

@bot.event
async def on_ready():
    print(f"✅ Бот запущен: {bot.user}")

@bot.command(name="мьют")
async def mute(ctx, member: discord.Member = None, time: str = None, *, reason: str = "Не указана"):

    # Проверка доступа
    if not has_access(ctx):
        await ctx.reply("❌ У тебя нет прав для выдачи тайм-аута (Админ или Moderate Members)")
        return

    # Если команда ответом на сообщение
    if ctx.message.reference and not member:
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = msg.author

    if not member or not time:
        await ctx.reply("❌ Использование: `!мьют @пользователь 10s причина`")
        return

    # Проверки
    if member == ctx.author:
        await ctx.reply("❌ Нельзя замьютить себя")
        return
    if member == ctx.guild.me:
        await ctx.reply("❌ Я не могу замьютить себя")
        return
    if member.top_role >= ctx.author.top_role and not ctx.author.guild_permissions.administrator:
        await ctx.reply("❌ У пользователя роль выше или равна вашей")
        return

    duration = parse_time(time)
    if not duration:
        await ctx.reply("❌ Неверный формат времени (`s/m/h/d`)")
        return

    try:
        await member.timeout(duration, reason=reason)
    except discord.Forbidden:
        await ctx.reply("❌ Недостаточно прав")
        return

    # Embed уведомление с твоими эмодзи (если бот в том же сервере)
    embed = discord.Embed(color=0x9b59b6)
    embed.description = (
        "<a:7870redflyingheart:1459453296422027469> **Squad 875 Team** <a:7870redflyingheart:1459453296422027469>\n\n"
        "1. Вы были наказаны Персоналом <:378490ban:1459454963334910148>\n"
        "2. Тип наказания **Тайм-Аут** <a:88094loading:1459453760190550058>\n"
        f"3. Длительность **{time}** <a:689495aec:1459453590333558848>\n"
        f"4. Причина **{reason}** <a:655233greensparklies:1459449234955964499>\n"
        f"5. Кто выдал **{ctx.author}** <:378490ban:1459454963334910148>"
    )

    # Отправка в ЛС
    try:
        await member.send(embed=embed)
    except:
        pass

    await ctx.reply(f"✅ {member.mention} получил тайм-аут на **{time}**")

# Обработка ошибок
@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ У тебя нет прав для выдачи тайм-аута")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply("❌ У бота нет прав для выдачи тайм-аута")

bot.run(TOKEN)
