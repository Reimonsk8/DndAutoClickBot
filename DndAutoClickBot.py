import discord
from discord.ext import commands
import pyautogui
import logging
import os
from dotenv import load_dotenv

load_dotenv()

global discord_username
discord_username = ''
global users_can_control_me
users_can_control_me = False
global run_code_its_me
run_code_its_me = False

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotAuthorized(Exception):
    pass

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('Bot is ready!')
    print(f'Connected to {len(bot.guilds)} guild(s):')
    
    # Get and print the bot's username
    bot_username = bot.user.name
    bot_discriminator = bot.user.discriminator
    full_bot_username = f"{bot_username}#{bot_discriminator}"
    
    print(f"My username is: {full_bot_username}")
    
    for guild in bot.guilds:
        print(f'- {guild.name}')

    # Ask for the username
    global discord_username
    discord_username = input("Please enter your Discord username (without the discriminator): ")
    print(f"Discord username set to: {discord_username}")

async def verify_discord_channel_user(ctx):
    #print(f'{ctx.author, " is in " ,allowed_users} has connected to Discord!')
    '''
    if str(ctx.author) not in allowed_users:
        raise NotAuthorized(f"{ctx.author} Only authorized users can use this command.")
    '''
    if ctx.author not in ctx.guild.members:
        raise NotAuthorized(f"You must be a member of {ctx.guild.name} to use this command.")


async def its_me(ctx):
    global discord_username
    global run_code_its_me
    if str(ctx.author) == discord_username:
        run_code_its_me = True
    else:
        run_code_its_me = False
        print(f"expected: {discord_username} to match -> {ctx.author}")

@bot.command(name="listusers")
async def list_allowed_users(ctx):
    try:
        await its_me(ctx)
        if not run_code_its_me: return
        
        guild = ctx.guild
        role = discord.utils.get(guild.roles, name="DnDAutoClickBotUser")  
        if role is None:
            await ctx.send("The role 'DnDAutoClickBotUser' does not exist in this server.", delete_after=10)
            return
        # Get all members with the role
        users_with_role = [member.name for member in guild.members if role in member.roles]
        # Create an embed with the list of users
        embed = discord.Embed(title=f"Users with '{role.name}' Role", description="\n".join(users_with_role), color=discord.Color.blue())
        # Add some additional fields to the embed
        embed.add_field(name="Total Users", value=str(len(users_with_role)), inline=False)
        embed.add_field(name="Role ID", value=str(role.id), inline=False)
        await ctx.send(embed=embed, delete_after=30)
    
    except NotAuthorized as e:
        await ctx.send(f"Sorry, you don't have permission to view the list of allowed users.\n\nError: {str(e)}", delete_after=10)

@bot.command(name="download")
async def download(ctx):
    try:
        await its_me(ctx)
        if not run_code_its_me: return
        await ctx.send('Download latest DND Ready Bot at https://www.reimondev.com/projects')
    except NotAuthorized as e:
        await ctx.send(f"Sorry, you don't have permission to download the client.\n\nError: {str(e)}", delete_after=10)

@bot.command(name="update")
async def update(ctx):
    try:
        await its_me(ctx)
        if not run_code_its_me: return
        await ctx.send('Download latest DND Ready Bot at https://www.reimondev.com/projects')
    except NotAuthorized as e:
        await ctx.send(f"Sorry, you don't have permission to download the client.\n\nError: {str(e)}", delete_after=10)

@bot.command(name="click")
@commands.has_any_role("DnDAutoClickBotUser","Admin")
async def click_command(ctx, x, y):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
    global users_can_control_me
    if not users_can_control_me:
        await its_me(ctx)
        if not run_code_its_me: return

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
@commands.has_any_role("DnDAutoClickBotUser","Admin")
async def move_mouse_command(ctx, x, y):
    global users_can_control_me
    if not users_can_control_me:
        await its_me(ctx)
        if not run_code_its_me: return
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
@commands.has_any_role("DnDAutoClickBotUser","Admin")
async def move_ready(ctx):
    global users_can_control_me
    if not users_can_control_me:
        await its_me(ctx)
        if not run_code_its_me: return
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
        await ctx.send(f"{discord_username} Ready for current Dungeon")
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
@commands.has_any_role("DnDAutoClickBotUser","Admin")
async def move_purchase_potions(ctx):
    global users_can_control_me
    if not users_can_control_me:
        await its_me(ctx)
        if not run_code_its_me: return
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

@bot.command(name="control")
@commands.has_any_role("DnDAutoClickBotUser","Admin")
async def control(ctx):
    await its_me(ctx)
    if run_code_its_me:
        global users_can_control_me
        await ctx.send(f"{ctx.author.name} users can control me ? {'yes' if users_can_control_me else 'no'}")

@bot.command(name="switch")
@commands.has_any_role("DnDAutoClickBotUser","Admin")
async def switch(ctx):
    await its_me(ctx)
    if run_code_its_me:
        global users_can_control_me
        users_can_control_me =  not users_can_control_me
        await ctx.send(f"{ctx.author.name} users can control me ? {'yes' if users_can_control_me else 'no'}")


@bot.command(name="info")
async def info(ctx):
    global run_code_its_me
    await its_me(ctx)
    if run_code_its_me:
        embed = discord.Embed(title="Info", description="Information about the bot:")
        embed.add_field(name="Command Prefix", value="!", inline=False)
        embed.add_field(name="!ready", value="set everybody ready for the dungeon", inline=False)
        embed.add_field(name="!meds", value="Purchases meds automatically.", inline=False)
        embed.add_field(name="!clear", value="Creates a button to delete all bot messages in the channel.", inline=True)
        embed.add_field(name="!switch", value="switch value of users controlling your computer", inline=False)
        embed.add_field(name="!control", value="show current value of users controlling your computer", inline=True)
        embed.add_field(name="!listusers", value="to display the current list of allowed users.", inline=False)
        embed.add_field(name="!download", value="Download install and run the client", inline=False)
        await ctx.send(embed=embed)
    

@bot.command()
@commands.has_any_role("DnDAutoClickBotUser","Admin")
async def clear(ctx):
    await its_me(ctx)
    if not run_code_its_me: return
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
        if msg.author == bot.user or msg.content.startswith("!"):
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
