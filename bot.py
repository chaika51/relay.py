import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import re
import os

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("❌ Переменная окружения TOKEN не найдена")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== ВРЕМЯ ====================
def parse_time(time_str: str):
    match = re.fullmatch(r"(\d+)([smhdсмчд])", time_str.lower())
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    mapping = {
        "s": timedelta(seconds=value),
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
        "с": timedelta(seconds=value),
        "м": timedelta(minutes=value),
        "ч": timedelta(hours=value),
        "д": timedelta(days=value)
    }
    return mapping[unit]

# ==================== ПРАВА ====================
def has_access(ctx):
    return ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.moderate_members

# ==================== EMBED ====================
def build_mute_embed(member, time, reason, author):
    embed = discord.Embed(color=0x9b59b6)
    embed.description = (
        "<a:7870redflyingheart:1459453296422027469> **Squad 875 Team** <a:7870redflyingheart:1459453296422027469>\n\n"
        f"1. Вы были наказаны Персоналом <:378490ban:1459454963334910148>\n"
        f"2. Тип наказания **Тайм-Аут** <a:88094loading:1459453760190550058>\n"
        f"3. Длительность **{time}** <a:689495aec:1459453590333558848>\n"
        f"4. Причина **{reason}** <a:655233greensparklies:1459449234955964499>\n"
        f"5. Кто выдал **{author}** <:378490ban:1459454963334910148>"
    )
    return embed

def build_unmute_embed(member, reason, author):
    if not reason:
        reason = "Без причины"
    embed = discord.Embed(color=0x1abc9c)
    embed.description = (
        "<a:7870redflyingheart:1459453296422027469> **Squad 875 Team** <a:7870redflyingheart:1459453296422027469>\n\n"
        f"1. Вы были размьючены Персоналом <:378490ban:1459454963334910148>\n"
        f"2. Тип наказания **Тайм-Аут был снят** <a:88094loading:1459453760190550058>\n"
        f"3. Длительность **Снят** <a:689495aec:1459453590333558848>\n"
        f"4. Причина **{reason}** <a:655233greensparklies:1459449234955964499>\n"
        f"5. Кто снял **{author}** <:378490ban:1459454963334910148>"
    )
    return embed

# ==================== МЬЮТ ====================
@bot.command(name="мьют")
async def mute(ctx, *args):
    if not has_access(ctx):
        await ctx.reply("❌ У тебя нет прав для выдачи тайм-аута")
        return

    member = None
    time_str = None
    reason = "Не указана"

    # Пинг
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
        if len(args) >= 2:
            time_str = args[1]
            reason = " ".join(args[2:]) if len(args) > 2 else reason
    # Ответ
    elif ctx.message.reference:
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = msg.author
        if len(args) >= 1:
            time_str = args[0]
            reason = " ".join(args[1:]) if len(args) > 1 else reason

    if not member or not time_str:
        await ctx.reply("❌ Использование: `!мьют @пинг 10s причина` или ответом `!мьют 10s причина`")
        return

    if member == ctx.author or member == ctx.guild.me or (member.top_role >= ctx.author.top_role and not ctx.author.guild_permissions.administrator):
        await ctx.reply("❌ Нельзя замьютить этого пользователя")
        return

    duration = parse_time(time_str)
    if not duration:
        await ctx.reply("❌ Неверный формат времени (`s/m/h/d` или `с/м/ч/д`)")
        return

    try:
        await member.timeout(duration, reason=reason)
    except discord.Forbidden:
        await ctx.reply("❌ Недостаточно прав")
        return

    embed = build_mute_embed(member, time_str, reason, ctx.author)
    try:
        await member.send(embed=embed)
    except:
        pass

    await ctx.reply(f"✅ {member.mention} получил тайм-аут на **{time_str}**")

# ==================== РАЗМЬЮТ ====================
@bot.command(name="размьют")
async def unmute(ctx, *args):
    if not has_access(ctx):
        await ctx.reply("❌ У тебя нет прав для снятия тайм-аута")
        return

    member = None
    reason = ""

    # Пинг
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
        if len(args) >= 1:
            reason = " ".join(args[1:]) if len(args) > 1 else ""
    # Ответ
    elif ctx.message.reference:
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = msg.author
        if len(args) >= 1:
            reason = " ".join(args) if len(args) > 0 else ""

    if not member:
        await ctx.reply("❌ Использование: `!размьют @пинг причина (необязательно)` или ответом")
        return

    if member == ctx.guild.me:
        await ctx.reply("❌ Я не могу снять тайм-аут себе")
        return

    try:
        await member.edit(timed_out_until=None)
    except discord.Forbidden:
        await ctx.reply("❌ Недостаточно прав")
        return

    embed = build_unmute_embed(member, reason, ctx.author)
    try:
        await member.send(embed=embed)
    except:
        pass

    await ctx.reply(f"✅ {member.mention} тайм-аут снят")

bot.run(TOKEN)
