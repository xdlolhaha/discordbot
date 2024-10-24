import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests


TOKEN = ''

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix=",", intents=intents)

# status
status_list = [
    discord.Game(name="status"),
    discord.Streaming(name="Streaming Now!", url="https://twitch.tv/streamer"),
    discord.Activity(type=discord.ActivityType.listening, name="status"),
    discord.Activity(type=discord.ActivityType.watching, name="status")
]

current_status_index = 0

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    
    change_status.start()

@tasks.loop(minutes=2)  # Change status every 2 minutes
async def change_status():
    global current_status_index
    status = status_list[current_status_index]
    await bot.change_presence(activity=status)
    print(f"Status updated to: {status.name}")  
    current_status_index = (current_status_index + 1) % len(status_list)


@bot.tree.command(name="avatar", description="Get the avatar of a specified user")
@app_commands.describe(user="The user to get the avatar of")
async def avatar(interaction: discord.Interaction, user: discord.User = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.name}'s Avatar", color=0x1E90FF)
    embed.set_image(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cat", description="Get a random picture of a cat")
async def cat(interaction: discord.Interaction):
    response = requests.get("https://api.thecatapi.com/v1/images/search")
    if response.status_code == 200:
        data = response.json()
        if data:
            cat_image_url = data[0]['url']
            embed = discord.Embed(title="Here's a Random Cat Picture", color=0x1E90FF)
            embed.set_image(url=cat_image_url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No cat picture found.", ephemeral=True)
    else:
        await interaction.response.send_message("Error fetching cat picture.", ephemeral=True)


@bot.tree.command(name="ip_lookup", description="Look up information for an IP address")
@app_commands.describe(ip="The IP address to look up")
async def ip_lookup(interaction: discord.Interaction, ip: str):
    url = f"https://ipapi.co/{ip}/json/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if "error" not in data:
            embed = discord.Embed(title=f"IP Lookup for {ip}", color=0x1E90FF)
            embed.add_field(name="IP", value=data.get("ip", "N/A"), inline=False)
            embed.add_field(name="City", value=data.get("city", "N/A"), inline=False)
            embed.add_field(name="Region", value=data.get("region", "N/A"), inline=False)
            embed.add_field(name="Country", value=data.get("country_name", "N/A"), inline=False)
            embed.add_field(name="Postal Code", value=data.get("postal", "N/A"), inline=False)
            embed.add_field(name="Latitude", value=data.get("latitude", "N/A"), inline=False)
            embed.add_field(name="Longitude", value=data.get("longitude", "N/A"), inline=False)
            embed.add_field(name="ISP", value=data.get("org", "N/A"), inline=False)
            embed.add_field(name="Timezone", value=data.get("timezone", "N/A"), inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"Error: {data['reason']}", ephemeral=True)
    else:
        await interaction.response.send_message("Error fetching data from the IP lookup service.", ephemeral=True)


@bot.tree.command(name="dm_role", description="DM all members with a specific role")
@app_commands.describe(role="The role to send a message to", message="The message to send")
async def dm_role(interaction: discord.Interaction, role: discord.Role, message: str):
    members = [member for member in interaction.guild.members if role in member.roles]
    
    if not members:
        await interaction.response.send_message(f"No members found with the role '{role.name}'.", ephemeral=True)
        return

    await interaction.response.send_message(f"Sending message to {len(members)} members with the role '{role.name}'...", ephemeral=True)

    for member in members:
        try:
            await member.send(message)
        except discord.Forbidden:
            await interaction.followup.send(f"Could not send message to {member.display_name} (DMs may be closed).", ephemeral=True)
    
    await interaction.followup.send("Finished sending DMs.", ephemeral=True)


@bot.tree.command(name="help", description="Shows all available commands")
async def help_command(interaction: discord.Interaction):
    commands = [
        {"name": "avatar", "description": "Get the avatar of a specified user"},
        {"name": "cat", "description": "Get a random picture of a cat"},
        {"name": "ip_lookup", "description": "Look up information for an IP address"},
        {"name": "dm_role", "description": "DM all members with a specific role"}
    ]
    
    embed = discord.Embed(title="Help - Available Commands", color=0x1E90FF)
    for command in commands:
        embed.add_field(name=f"/{command['name']}", value=command['description'], inline=False)
    
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
