import discord
from discord.ext import commands
import asyncio
import os
import random
from io import BytesIO

# =====================
# INTENTS (OBLIGATOIRE)
# =====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)

giveaways = {}

# =====================
# READY
# =====================
@bot.event
async def on_ready():
    print(f"✅ Connecté : {bot.user}")

# =====================
# ERROR HANDLER (IMPORTANT)
# =====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas les permissions.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Argument manquant.")
    else:
        print(error)

# =====================
# TEST
# =====================
@bot.command()
async def test(ctx):
    await ctx.send("✅ BOT OK")

# =====================
# CLEAR (FIX IMPORTANT)
# =====================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages supprimés", delete_after=3)

# =====================
# TOS
# =====================
@bot.command()
async def tos(ctx):
    embed = discord.Embed(
        title="📋 TOS",
        description="🟢 FnF\n🟢 No note\n🟢 Screenshot payment\n\nNo refund = No respect",
        color=discord.Color.green()
    )

    embed.add_field(
        name="PayPal",
        value="extazlemeilleur@gmail.com\nhaythemchl93380@gmail.com",
        inline=False
    )

    embed.add_field(
        name="LTC",
        value="LLn2rAf7jzttyabPKe38PjSrCnV5AKk8Kx",
        inline=False
    )

    await ctx.send(embed=embed)

# =====================
# BAN / UNBAN
# =====================
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} ban")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"🔓 {user} unban")

# =====================
# MUTE / UNMUTE
# =====================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"🔇 {member} mute")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if role in member.roles:
        await member.remove_roles(role)

    await ctx.send(f"🔊 {member} unmute")

# =====================
# LOCK / UNLOCK
# =====================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Channel locked")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Channel unlocked")

# =====================
# TICKET SIMPLE
# =====================
@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    channel = await ctx.guild.create_text_channel(f"ticket-{ctx.author.name}")
    await channel.send(f"🎟 Ticket de {ctx.author.mention}")
    await ctx.send(f"✅ Ticket créé : {channel.mention}")

# =====================
# CLOSE + TRANSCRIPT
# =====================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx):

    if "ticket-" not in ctx.channel.name:
        return await ctx.send("❌ Pas un ticket")

    messages = []
    async for msg in ctx.channel.history(limit=200):
        messages.append(f"{msg.author}: {msg.content}")

    transcript = "\n".join(messages)

    file = discord.File(BytesIO(transcript.encode()), "transcript.txt")

    await ctx.author.send(file=file)
    await ctx.send("🔒 Ticket fermé")

    await asyncio.sleep(2)
    await ctx.channel.delete()

# =====================
# GIVEAWAY
# =====================
@bot.command()
@commands.has_permissions(administrator=True)
async def gcreate(ctx, duration: int, winners: int, *, prize: str):

    embed = discord.Embed(
        title="🎉 GIVEAWAY",
        description=f"Prize: **{prize}**\nWinners: **{winners}**\nReact 🎉",
        color=discord.Color.gold()
    )

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")

    await asyncio.sleep(duration)

    msg = await ctx.channel.fetch_message(msg.id)

    users = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if user != bot.user:
                    users.append(user)

    if not users:
        return await ctx.send("❌ Aucun participant")

    winners_list = random.sample(users, min(winners, len(users)))

    await ctx.send("🎉 Winner(s): " + ", ".join(w.mention for w in winners_list))

# =====================
# REROLL
# =====================
@bot.command()
@commands.has_permissions(administrator=True)
async def reroll(ctx, message_id: int):

    msg = await ctx.channel.fetch_message(message_id)

    users = []
    for reaction in msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if user != bot.user:
                    users.append(user)

    if not users:
        return await ctx.send("❌ Aucun participant")

    winner = random.choice(users)

    await ctx.send(f"🎉 New winner: {winner.mention}")

# =====================
# RUN BOT
# =====================
bot.run(os.getenv("TOKEN"))
