import discord
from discord.ext import commands
import asyncio
import os
import random
from io import BytesIO

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)

# =====================
# READY
# =====================
@bot.event
async def on_ready():
    print(f"✅ Connecté : {bot.user}")

# =====================
# ERROR HANDLER
# =====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Tu n'as pas la permission.")
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
# CLEAR
# =====================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages supprimés", delete_after=3)

# =====================
# VOUCH
# =====================
@bot.command()
async def vouch(ctx):
    await ctx.send("Vouch <@1002539242204971058> and <@1499834951150080198>")

# =====================
# TOS #1
# =====================
@bot.command()
async def tos(ctx):
    embed = discord.Embed(
        title="📋 TOS #1",
        description="🟢 FnF\n🟢 No note\n🟢 Screenshot payment\n\n❌ No respect = No refund",
        color=discord.Color.green()
    )
    embed.add_field(name="💳 PayPal", value="extazlemeilleur@gmail.com", inline=False)
    embed.add_field(name="💰 LTC", value="LTqhLYyzRAqzAyfJU8PykBPwJjXmKUdC8Z", inline=False)
    await ctx.send(embed=embed)

# =====================
# TOS #2
# =====================
@bot.command()
async def tos2(ctx):
    embed = discord.Embed(
        title="📋 TOS #2",
        description="🟢 FnF\n🟢 No note\n🟢 Screenshot payment\n\n❌ No respect = No refund",
        color=discord.Color.blue()
    )
    embed.add_field(name="💳 PayPal", value="haythemchl93380@gmail.com", inline=False)
    embed.add_field(name="💰 LTC", value="LLn2rAf7jzttyabPKe38PjSrCnV5AKk8Kx", inline=False)
    await ctx.send(embed=embed)

# =====================
# BAN / UNBAN / KICK
# =====================
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"🔨 {member} banni")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = await bot.fetch_user(user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"🔓 {user} débanni")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"👢 {member} kick")

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
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Salon verrouillé")

@bot.command()
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Salon déverrouillé")

# =====================
# 🎟 TICKET MENU
# =====================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🎟 Choisis une catégorie",
        options=[
            discord.SelectOption(label="Support", emoji="❓"),
            discord.SelectOption(label="Buy", emoji="🛒"),
            discord.SelectOption(label="Autre", emoji="📩"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        guild = interaction.guild
        user = interaction.user

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites
        )

        await channel.send(f"🎟 Ticket ouvert par {user.mention}")
        await interaction.response.send_message(f"✅ Ticket créé : {channel.mention}", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    embed = discord.Embed(
        title="🎟 Support 24/7",
        description="Choisis une option pour ouvrir un ticket",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=TicketView())

# =====================
# CLOSE + TRANSCRIPT
# =====================
@bot.command()
async def close(ctx):
    if "ticket-" not in ctx.channel.name:
        return await ctx.send("❌ Pas un ticket")

    messages = []
    async for msg in ctx.channel.history(limit=200):
        messages.append(f"{msg.author}: {msg.content}")

    file = discord.File(BytesIO("\n".join(messages).encode()), "transcript.txt")

    await ctx.author.send(file=file)
    await ctx.send("🔒 Ticket fermé")

    await asyncio.sleep(2)
    await ctx.channel.delete()

# =====================
# RENAME
# =====================
@bot.command()
@commands.has_permissions(manage_channels=True)
async def rename(ctx, *, new_name):
    if not ctx.channel.name.startswith("ticket-"):
        return await ctx.send("❌ Utilisable uniquement dans un ticket.")

    await ctx.channel.edit(name=f"ticket-{new_name}")
    await ctx.send(f"✏️ Renommé en ticket-{new_name}")

# =====================
# GIVEAWAY
# =====================
@bot.command()
async def gcreate(ctx, duration: int, winners: int, *, prize: str):

    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"🎁 {prize}\n👑 Winners: {winners}\n⏱ {duration}s\n\nRéagis 🎉",
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

    winner = random.choice(users)
    await ctx.send(f"🎉 Gagnant: {winner.mention}")

# =====================
# REROLL
# =====================
@bot.command()
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
    await ctx.send(f"🎉 Nouveau gagnant: {winner.mention}")

# =====================
# RUN
# =====================
bot.run(os.getenv("TOKEN"))
