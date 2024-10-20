import discord
from discord.ext import commands
import pyautogui
import json
import logging
import sys
from dotenv import load_dotenv
load_dotenv()

import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotAuthorized(Exception):
    pass

allowed_users = []

def load_allowed_users():
    global allowed_users
    try:
        with open('allowed_users.txt', 'r') as f:
            allowed_users = json.load(f)
    except FileNotFoundError:
        logger.info("Allowed users file not found. Using default.")
        allowed_users = ['reimonsk8', 'tolec21', 'Admin', 'bazanator']
    except json.JSONDecodeError:
        logger.error("Failed to decode allowed users file. Using default.")
        allowed_users = ['reimonsk8', 'bazanator', 'tolec21', 'Admin']
    except Exception as e:
        logger.error(f"An error occurred while loading allowed users: {e}")
        raise

def save_allowed_users():
    global allowed_users
    try:
        with open('allowed_users.txt', 'w') as f:
            json.dump(allowed_users, f)
    except IOError as e:
        logger.error(f"Failed to save allowed users: {e}")

try:
    load_allowed_users()
except FileNotFoundError:
    print("Warning: allowed_users.txt file not found. Using default values.")
    allowed_users = ['reimonsk8', 'bazanator', 'tolec21', 'Admin']
except Exception as e:
    print(f"Error loading allowed users: {str(e)}")
    # You might want to stop the bot here or take some other action
    sys.exit(1)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Bot is ready!')
    print(f'Connected to {len(bot.guilds)} guild(s):')
    
    for guild in bot.guilds:
        print(f'- {guild.name}')

async def verify_discord_channel_user(ctx):
    #print(f'{ctx.author, " is in " ,allowed_users} has connected to Discord!')
    if str(ctx.author) not in allowed_users:
        raise NotAuthorized(f"{ctx.author} Only authorized users can use this command.")
    if ctx.author not in ctx.guild.members:
        raise NotAuthorized(f"You must be a member of {ctx.guild.name} to use this command.")

@bot.command(name="manageusers")
@commands.has_permissions(administrator=True)
async def manage_allowed_users(ctx):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e), delete_after=10)

    view = ManageUsersView(ctx)
    await ctx.send("Manage Allowed Users", view=view)

class ManageUsersView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.allowed_users = allowed_users.copy()

    @discord.ui.button(label="Add User", style=discord.ButtonStyle.green)
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddUserModal(self.ctx))

    @discord.ui.button(label="Remove User", style=discord.ButtonStyle.red)
    async def remove_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RemoveUserModal(self.ctx, self.allowed_users))

class AddUserModal(discord.ui.Modal):
    def __init__(self, ctx):
        super().__init__(title="Add User")
        self.add_item(discord.ui.TextInput(label="Username", placeholder="Enter username", min_length=1, max_length=32))
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        username = self.children[0].value.strip().lower()
        global allowed_users
        
        if len(username) > 32:
            return await interaction.response.send_message("Username too long. Maximum length is 32 characters.", ephemeral=True)
        
        if username not in allowed_users:
            allowed_users.append(username)
            save_allowed_users()
            
            embed = discord.Embed(title="Success!", description=f"{username} added to allowed users.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.ctx.send(f"{username} has been added to the allowed users list.", delete_after=10)
        else:
            embed = discord.Embed(title="Error", description=f"{username} is already in the allowed users list.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

class RemoveUserModal(discord.ui.Modal):
    def __init__(self, ctx, allowed_users):
        super().__init__(title="Remove User")
        self.add_item(discord.ui.TextInput(label="Username", placeholder="Enter username", min_length=1, max_length=32))
        self.ctx = ctx
        self.allowed_users = allowed_users

    async def callback(self, interaction: discord.Interaction):
        username = self.children[0].value.strip().lower()
        global allowed_users
        
        if len(username) > 32:
            return await interaction.response.send_message("Username too long. Maximum length is 32 characters.", ephemeral=True)
        
        if username in allowed_users:
            allowed_users.remove(username)
            save_allowed_users()
            
            embed = discord.Embed(title="Success!", description=f"{username} removed from allowed users.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.ctx.send(f"{username} has been removed from the allowed users list.", delete_after=10)
        else:
            embed = discord.Embed(title="Error", description=f"{username} is not in the allowed users list.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="listusers")
async def list_allowed_users(ctx):
    embed = discord.Embed(title="Allowed Users", description="\n".join(allowed_users), color=discord.Color.blue())
    await ctx.send(embed=embed, delete_after=30)

def save_allowed_users():
    with open('allowed_users.txt', 'w') as f:
        json.dump(allowed_users, f)

@bot.event
async def on_member_join(member):
    rules_channel = discord.utils.get(member.guild.channels, name='rules')
    
    if rules_channel:
        embed = discord.Embed(title="Welcome to Our Server!", description=f"Hello {member.name}!")
        embed.add_field(name="Available Commands:", value="""
        !download - Download, install and run the client
        !ready - Set everybody ready for the dungeon
        !meds - Automatically purchases meds.
        !clear - Creates a button to delete all bot messages in the channel.
        """, inline=False)
        embed.add_field(name="For More Details:", value="Type !info for more information!", inline=False)
        
        await rules_channel.send(embed=embed)
    else:
        print(f"No channel named 'rules' found in {member.guild.name}")

@bot.command(name="download")
async def hello_download(ctx):
    await ctx.send('Download latest DND Ready Bot at https://www.reimondev.com/projects')

@bot.command(name="update")
async def hello_update(ctx):
    await ctx.send('Download latest DND Ready Bot at https://www.reimondev.com/projects')

@bot.command(name="click")
async def click_command(ctx, x, y):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    try:
        x = int(x)
        y = int(y)
        print("f{ctx.author.name}Attempting to click at ({x}, {y})")
        pyautogui.click(x, y)
        await ctx.send(f"Clicked at ({x}, {y})")
    except ValueError:
        await ctx.send("Invalid coordinates. Please enter two numbers separated by a space.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="move")
async def move_mouse_command(ctx, x, y):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
    try:
        x = int(x)
        y = int(y)
        print(f"{ctx.author.name} Moving mouse to ({x}, {y})")
        pyautogui.moveTo(x, y)
        await ctx.send(f"{ctx.author.name} Mouse moved to ({x}, {y})")
    except ValueError:
        await ctx.send("Invalid coordinates. Please enter two numbers separated by a space.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name='ready')
async def move_ready(ctx):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    print(f"{ctx.author.name} Dark and darker ready")
    try:
        # Move and click play
        pyautogui.moveTo(250, 33)
        pyautogui.click(250, 33)
        # Move and click ready
        pyautogui.moveTo(100, 1000)
        pyautogui.click(100, 1000)
        # Move and click Confirm
        pyautogui.moveTo(830, 650)
        pyautogui.click(830, 650)
        await ctx.send(f"{ctx.author.name} Ready for current Dungeon")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

def escape_current_screen():
    pyautogui.press('esc')
    pyautogui.moveTo(25, 25)
    pyautogui.click(25, 25)

def purchase_movements(times = 2):
    for _ in range(times):
        pyautogui.moveTo(200, 300)
        pyautogui.click(200, 300)
        
        # Fill stash and buy
        pyautogui.moveTo(1000, 920)
        pyautogui.click(1000, 920)
        pyautogui.moveTo(1000, 1000)
        pyautogui.click(1000, 1000)
    # Escaped from merchant screen
    escape_current_screen()

@bot.command(name="meds")
async def move_purchase_potions(ctx):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    try:
        print("Dark and darker ready")
        print(f"{ctx.author.name} Purchasing Potions")

        # Move to merchants
        pyautogui.moveTo(1080, 35)
        pyautogui.click(1080, 35)
        
        # Move to alchemist
        pyautogui.moveTo(300, 500)
        pyautogui.click(300, 500)
        
        # Purchase health pots
        purchase_movements()
        
        # Move to surgeon
        pyautogui.moveTo(300, 950)
        pyautogui.click(300, 950)

        # Purchase bandages
        purchase_movements()

        # Move to stash
        pyautogui.moveTo(900, 35)
        pyautogui.click(900, 35)
        
        await ctx.send(f"{ctx.author.name} x6 potions and bandages purchased")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="info")
async def info(ctx):
    embed = discord.Embed(title="Info", description="Information about the bot:")
    #embed.add_field(name="Command Prefix", value="!", inline=False)
    embed.add_field(name="!download", value="Download install and run the client", inline=False)
    embed.add_field(name="!ready", value="set everybody ready for the dungeon", inline=False)
    embed.add_field(name="!meds", value="Purchases meds automatically.", inline=False)
    embed.add_field(name="!clear", value="Creates a button to delete all bot messages in the channel.", inline=True)
    embed.add_field(name="!listusers", value="to display the current list of allowed users.", inline=False)
    embed.add_field(name="!manageusers ", value="command to administrators only.", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def clear(ctx):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
    view = discord.ui.View(timeout=300)
    delete_button = discord.ui.Button(label="Delete Messages", style=discord.ButtonStyle.primary)
    # Define the callback as a coroutine
    async def delete_callback(interaction):
        await delete_bot_messages(interaction, ctx.channel.id, ctx)
    
    # Use a coroutine for the callback
    delete_button.callback = delete_callback
    
    view.add_item(delete_button)
    
    try:
        await ctx.send("Click the button below to delete all messages from this user.", view=view)
    except Exception as e:
        print(f"Error sending message: {e}")

async def delete_bot_messages(interaction, channel_id, ctx):
    guild = interaction.guild
    channel = guild.get_channel(channel_id)
    
    async for msg in channel.history(limit=20):
        if msg.author == bot.user or msg.author == interaction.user:
            try:
                await msg.delete()
                print(f"Deleted message {msg.id}")
            except Exception as e:
                print(f"Error deleting message {msg.id}: {e}")
    
    try:
        print(f"{ctx.author.name} All messages from {interaction.user} deleted from {channel.name}")
        #await ctx.send(f"{ctx.author.name} All messages from {interaction.user} deleted from {channel.name}")
        #await interaction.followup.send(f"All messages from {interaction.user} deleted from {channel.name}", ephemeral=True)
    except Exception as e:
        print(f"Error sending follow-up message: {e}")

bot.run(os.getenv('BOT_TOKEN'))