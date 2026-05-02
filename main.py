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
# EMOJIS
# =====================
HAMMER = "<:hammer:1475639604513345747>"
GREEN = "<:green:1475267542086975558>"
CROSS = "<:cross:1303102536194064476>"
CLEAR = "<:clear:1265166157959401503>"
MUTE = "<:mute:1305204045195116606>"
UNMUTE = "<:unmute:1305204037343383584>"
TICKET = "<:ticket:1163792671475769364>"

# =====================
# READY
# =====================
@bot.event
async def on_ready():
    print(f"✅ Connecté : {bot.user}")

# =====================
# CLEAR
# =====================
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{CLEAR} {amount} messages supprimés", delete_after=3)

# =====================
# BAN
# =====================
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member):
    await member.ban()
    await ctx.send(f"{HAMMER} {member} a été banni")

# =====================
# KICK
# =====================
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member):
    await member.kick()
    await ctx.send(f"👢 {member} kick")

# =====================
# UNBAN
# =====================
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
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")

    if not role:
        role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False)

    await member.add_roles(role)
    await ctx.send(f"{MUTE} {member} mute")

@bot.command()
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.remove_roles(role)
    await ctx.send(f"{UNMUTE} {member} unmute")

# =====================
# TOS 1
# =====================
@bot.command()
async def tos(ctx):
    embed = discord.Embed(title="📋 TOS #1", color=discord.Color.green())
    embed.description = f"{GREEN} FnF\n{GREEN} No note\n{GREEN} Screenshot payment\n\n{CROSS} No refund"
    embed.add_field(name="PayPal", value="extazlemeilleur@gmail.com", inline=False)
    embed.add_field(name="LTC", value="LTqhLYyzRAqzAyfJU8PykBPwJjXmKUdC8Z", inline=False)
    await ctx.send(embed=embed)

# =====================
# TOS 2
# =====================
@bot.command()
async def tos2(ctx):
    embed = discord.Embed(title="📋 TOS #2", color=discord.Color.blue())
    embed.description = f"{GREEN} FnF\n{GREEN} No note\n{GREEN} Screenshot payment\n\n{CROSS} No refund"
    embed.add_field(name="PayPal", value="haythemchl93380@gmail.com", inline=False)
    embed.add_field(name="LTC", value="LLn2rAf7jzttyabPKe38PjSrCnV5AKk8Kx", inline=False)
    await ctx.send(embed=embed)

# =====================
# VOUCH
# =====================
@bot.command()
async def vouch(ctx):
    await ctx.send("https://discord.com/channels/1496985489482190891/1497024400007106601\nVouch <@1002539242204971058> and <@1499834951150080198>")

# =====================
# LOCK / UNLOCK
# =====================
@bot.command()
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔒 Locked")

@bot.command()
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("🔓 Unlocked")

# =====================
# 🎟 TICKET FIX
# =====================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choisis une option",
        options=[
            discord.SelectOption(label="Support", emoji="❓"),
            discord.SelectOption(label="Buy", emoji="🛒"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):

        await interaction.response.defer(ephemeral=True)

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

        await channel.send(f"{TICKET} Ticket ouvert par {user.mention}")
        await interaction.followup.send(f"✅ Ticket créé : {channel.mention}", ephemeral=True)

@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title=f"{TICKET} Support",
        description="Choisis une catégorie",
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
    await ctx.send("🔒 Fermeture...")

    await asyncio.sleep(2)
    await ctx.channel.delete()

# =====================
# RENAME
# =====================
@bot.command()
async def rename(ctx, *, name):
    if not ctx.channel.name.startswith("ticket-"):
        return await ctx.send("❌ Pas un ticket")

    await ctx.channel.edit(name=f"ticket-{name}")
    await ctx.send("✏️ Renommé")

# =====================
# GIVEAWAY
# =====================
@bot.command()
async def gcreate(ctx, duration: int, winners: int, *, prize: str):
    embed = discord.Embed(title="🎉 GIVEAWAY", description=prize, color=discord.Color.gold())
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
    await ctx.send(f"🎉 Winner: {winner.mention}")

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
    await ctx.send(f"🎉 New winner: {winner.mention}")

# =====================
# RUN
# =====================
bot.run(os.getenv("TOKEN"))
