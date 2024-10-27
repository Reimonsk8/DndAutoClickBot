import discord
from discord.ext import commands
import pyautogui
import logging
from dotenv import load_dotenv
import tkinter as tk
from tkinter import scrolledtext
from pynput import mouse
# from pynput import keyboard
# import pyperclip
import threading
import asyncio
import os

load_dotenv()

global discord_username
discord_username = ''

global run_code_its_me
run_code_its_me = False

global default_toggle
default_toggle = True

global switch_settings
switch_settings = {
    "lobby": default_toggle,
    "ready": default_toggle,
    "meds": default_toggle,
    "karma": default_toggle,
    "move": default_toggle,
    "click": default_toggle
}

global my_window
my_window = None

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotAuthorized(Exception):
    pass

def forward_log_to_main_window(message, level=logging.INFO):
    if my_window and hasattr(my_window, 'log'):
        my_window.log(message, level)
    else:
        print(f"Warning: Could not find MainWindow.log method. Message: {message}")

@bot.event
async def on_ready():
    required_roles = ["DnDAutoClickBotUser"]
    bot_username = bot.user.name
    bot_discriminator = bot.user.discriminator
    global full_bot_username
    full_bot_username = f"{bot_username}#{bot_discriminator}"
    forward_log_to_main_window(f"Bot is: {full_bot_username} ready!")
    forward_log_to_main_window(f'{bot.user} has connected to Discord to {len(bot.guilds)} guild(s):')
    for guild in bot.guilds:
        authorized_users = []
        for member in guild.members:
            if any(role.name in required_roles for role in member.roles):
                authorized_users.append(f'- {guild} {member} can use the bot')

        if authorized_users:
            for user in authorized_users:
                forward_log_to_main_window(user)
        else:
            forward_log_to_main_window(f'- {guild.name} no bot user online')

    # Now you can proceed with other bot operations
    await asyncio.sleep(1)  # Wait for 1 second before continuing
    forward_log_to_main_window("Bot is ready to receive commands.")

def requires_dnda_roles():
    def predicate(ctx):
        roles = ["DnDAutoClickBotUser", "Admin"]
        if any(role in [r.name for r in ctx.author.roles] for role in roles):
            return True
        raise commands.MissingAnyRole(roles)
    return commands.check(predicate)

async def verify_discord_channel_user(ctx):
    if ctx.author not in ctx.guild.members:
        raise NotAuthorized(f"You must be inside the {ctx.guild.name} channel to use this command.")
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send(f"Sorry, you don't have the required role to use this command. You need either 'DnDAutoClickBotUser' or 'Admin' role.")
    else:
        await ctx.send(f"An unexpected error occurred: {error}")


async def its_me(ctx):
    global discord_username
    global run_code_its_me
    if str(ctx.author) == discord_username:
        run_code_its_me = True
    else:
        run_code_its_me = False
        forward_log_to_main_window(f"{ctx.author} issued a command. The command will only run locally if it matches your username: {discord_username}")

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
@requires_dnda_roles()
async def click_command(ctx, x, y, target_user=None):
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
    global switch_settings
    if not switch_settings["click"]:
        await its_me(ctx)
        if not run_code_its_me: return

    # Check if target user is valid
    if not (target_user is None or target_user == discord_username):
        forward_log_to_main_window("Invalid target user", level=logging.ERROR)
        return

    try:
        x = int(x)
        y = int(y)
        forward_log_to_main_window(f"{ctx.author.name}Attempting to click at ({x}, {y})")
        pyautogui.click(x, y)
        await ctx.send(f"Clicked at ({x}, {y})")
    except ValueError:
        await ctx.send("Invalid coordinates. Please enter two numbers separated by a space.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="move")
@requires_dnda_roles()
async def move_mouse_command(ctx, x, y, target_user=None):
    global switch_settings
    if not switch_settings["move"]:
        await its_me(ctx)
        if not run_code_its_me: return
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
    # Check if target user is valid
    if not (target_user is None or target_user == discord_username):
        forward_log_to_main_window("Invalid target user")
        return
    
    try:
        x = int(x)
        y = int(y)
        forward_log_to_main_window(f"{ctx.author.name} Moving mouse to ({x}, {y})")
        pyautogui.moveTo(x, y)
        await ctx.send(f"{ctx.author.name} Mouse moved to ({x}, {y})")
    except ValueError:
        await ctx.send("Invalid coordinates. Please enter two numbers separated by a space.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="lobby")
@requires_dnda_roles()
async def move_play(ctx, target_user=None):
    global switch_settings
    if not switch_settings["lobby"]:
        await its_me(ctx)
        if not run_code_its_me: return
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))

    # Check if target user is valid
    if not (target_user is None or target_user == discord_username):
        forward_log_to_main_window("Invalid target user")
        return
    
    # Move and click play
    forward_log_to_main_window(f"{ctx.author.name} switch tab to play lobby")
    try:

        pyautogui.moveTo(250, 33)
        pyautogui.click(250, 33)
        await ctx.send(f"{discord_username} switched tab to play lobby")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")@bot.command(name='ready')

@bot.command(name="esc")
@requires_dnda_roles()
async def move_esc(ctx, target_user=None):
    global switch_settings
    if not switch_settings["lobby"]:
        await its_me(ctx)
        if not run_code_its_me: return
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))

    # Check if target user is valid
    if not (target_user is None or target_user == discord_username):
        forward_log_to_main_window("Invalid target user")
        return
    
    # Move and click play
    forward_log_to_main_window(f"{ctx.author.name} escape window")
    try:

        pyautogui.moveTo(80, 40)
        pyautogui.click(80, 40)
        await ctx.send(f"{discord_username} escape window")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")@bot.command(name='ready')

@bot.command(name='ready')
@requires_dnda_roles()
async def move_ready(ctx, target_user=None):
    global switch_settings
    
    # Check if ready switch is off
    if not switch_settings["ready"]:
        await its_me(ctx)
        if not run_code_its_me: return
    
    # Verify Discord channel user
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
    # Check if target user is valid
    if not (target_user is None or target_user == discord_username):
        forward_log_to_main_window("Invalid target user")
        return
    
    forward_log_to_main_window(f"{ctx.author.name} Dark and darker ready")
    try:
        # Move and click ready
        pyautogui.moveTo(100, 1000)
        pyautogui.click(100, 1000)
        # Move and click Confirm
        pyautogui.moveTo(830, 650)
        pyautogui.click(830, 650)
        await ctx.send(f"{discord_username} Ready for current Dungeon")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name='readyin')
@requires_dnda_roles()
async def move_readyin(ctx, mins=0, target_user=None):
    global switch_settings
    # Check if ready switch is off
    if not switch_settings["ready"]:
        await its_me(ctx)
        if not run_code_its_me: return
    
    # Verify Discord channel user
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
    # Check if target user is valid
    if not (target_user is None or target_user == discord_username):
        forward_log_to_main_window("Invalid target user")
        return
    
    # Try to convert mins to float
    try:
        mins = float(mins)
        if mins > 10: mins = 9

    except ValueError:
        return await ctx.send("Please provide a valid number for the minutes.")

    total_seconds = mins * 60
    while total_seconds > 0:
        if total_seconds >= 10:
            sleep_duration = 10
            time_unit = "minutes"
        else:
            sleep_duration = 1
            time_unit = "seconds"

        await asyncio.sleep(sleep_duration)
        total_seconds -= sleep_duration

        if time_unit == "minutes":
            remaining_minutes = int(total_seconds // 60)
            forward_log_to_main_window(f"{ctx.author.name} will be ready in {remaining_minutes} min {int(total_seconds % 60)} secs ")
        else:
            forward_log_to_main_window(f"{ctx.author.name} will click ready in {int(total_seconds)} {time_unit}")
    
    try:
        # Move and click ready
        pyautogui.moveTo(100, 1000)
        pyautogui.click(100, 1000)
        # Move and click Confirm
        pyautogui.moveTo(830, 650)
        pyautogui.click(830, 650)
        await ctx.send(f"{discord_username} Ready for current Dungeon")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name='karma')
@requires_dnda_roles()
async def move_karma(ctx, target_user=None):
    global switch_settings
    if not switch_settings["karma"]:
        await its_me(ctx)
        if not run_code_its_me: return
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    
        # Check if target user is valid
    if not (target_user is None or target_user == discord_username):
        forward_log_to_main_window("Invalid target user")
        return
    
    forward_log_to_main_window(f"{ctx.author.name} giving karma")
    try:
        # # Move and click ready
        pyautogui.moveTo(1700, 1000)
        pyautogui.click(1700, 1000)
        # # Move and click Confirm
        pyautogui.moveTo(460, 550)
        pyautogui.click(460, 550)
        await ctx.send(f"{discord_username} gived karma")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

def escape_current_screen():
    pyautogui.press('esc')
    pyautogui.moveTo(25, 25)
    pyautogui.click(25, 25)

def purchase_movements(times):
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
@requires_dnda_roles()
async def move_purchase_potions(ctx, repeat = 2):
    global switch_settings
    if not switch_settings["meds"]:
        await its_me(ctx)
        if not run_code_its_me: return
    try:
        await verify_discord_channel_user(ctx)
    except NotAuthorized as e:
        return await ctx.send(str(e))
    try:
        forward_log_to_main_window("Dark and darker ready")
        forward_log_to_main_window(f"{ctx.author.name} Purchasing Potions")

        # Move to merchants
        pyautogui.moveTo(1080, 35)
        pyautogui.click(1080, 35)
        
        # Move to alchemist
        pyautogui.moveTo(300, 500)
        pyautogui.click(300, 500)
        
        # Purchase health pots
        purchase_movements(repeat)
        
        # Move to surgeon
        pyautogui.moveTo(450, 800)
        pyautogui.click(450, 800)

        # Purchase bandages
        purchase_movements(repeat)

        # Move to stash
        pyautogui.moveTo(900, 35)
        pyautogui.click(900, 35)
        
        await ctx.send(f"{ctx.author.name} x{3*repeat} potions and bandages purchased")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command(name="switch")
@requires_dnda_roles()
async def switch(ctx, option=None):
    await its_me(ctx)
    if run_code_its_me:
        global switch_settings
        if option == None:
            embed = discord.Embed(title=f"{ctx.author.name} Current Switch Settings", description="Other users can control the following options", color=discord.Color.blue())
            for key, value in switch_settings.items():
                embed.add_field(name=key, value=f"{'On' if value else 'Off'}", inline=True)
            await ctx.send(embed=embed)
        elif option in switch_settings:
            # Toggle the switch
            switch_settings[option] = not switch_settings[option]
            await ctx.send(f"{option.capitalize()} is now {'On' if switch_settings[option] else 'Off'}")
        else:
            await ctx.send(f"Invalid option: {option}")

@bot.command(name="switchall")
@requires_dnda_roles()
async def switch(ctx):
    await its_me(ctx)
    if run_code_its_me:
        global switch_settings
        global default_toggle
        default_toggle = not default_toggle
        embed = discord.Embed(
            title=f"{ctx.author.name} switched all settings to {'On' if default_toggle else 'Off'}",
            description="Other users can control the following options",
            color=discord.Color.blue()
        )        
        for key, value in switch_settings.items():
            switch_settings[key] = default_toggle
            embed.add_field(name=key, value=f"{'Off' if value else 'On'}", inline=True)
        await ctx.send(embed=embed)

@bot.command(name="info")
async def info(ctx):
    global run_code_its_me
    await its_me(ctx)
    if run_code_its_me:
        embed = discord.Embed(title="GENERAL COMMANDS", description="Information about the bot:")
        embed.add_field(name="!listusers", value="to display the current list of allowed users.", inline=False)
        embed.add_field(name="!clear", value="Creates a button to delete all bot messages in the channel.", inline=True)
        embed.add_field(name="!update", value="Download install and run the lastest client version from website", inline=False)
        embed.add_field(name="!switchall", value="toggle all values On or Off for other users controlling commands", inline=False)
        embed.add_field(name="!switch [option]", value="switch value of single option that other users control", inline=False)

        embed.add_field(name="ACTION OPTIONS", value="", inline=False)
        embed.add_field(name="!lobby [user]", value="sets player on lobby tab (default user all)", inline=False)
        embed.add_field(name="!esc [user]", value="escapes current window (default user all)", inline=False)

        embed.add_field(name="!ready [user]", value="sets player ready for the dungeon (default user all)", inline=False)
        embed.add_field(name="!readyin [mins]", value="sets player ready in minute counter (default 0 mins)", inline=False)

        embed.add_field(name="!meds [2] [user]", value="Purchases (default meds x2 user all) automatically .", inline=False)
        embed.add_field(name="!karma [user]", value="gives good karma to top first player on screen (default user all)", inline=False)
        await ctx.send(embed=embed)
    
@bot.command()
@requires_dnda_roles()
async def clear(ctx, qty = 20):
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
        await delete_bot_messages(interaction, ctx.channel.id, ctx, qty)
    
    # Use a coroutine for the callback
    delete_button.callback = delete_callback
    
    view.add_item(delete_button)
    
    try:
        await ctx.send("Click the button below to delete all bot command messages", view=view)
    except Exception as e:
        forward_log_to_main_window(f"Error sending message: {e}")

async def delete_bot_messages(interaction, channel_id, ctx, qty):
    guild = interaction.guild
    channel = guild.get_channel(channel_id)
    
    async for msg in channel.history(limit=qty):
        if msg.author == bot.user or msg.content.startswith("!"):
            try:
                await msg.delete()
                forward_log_to_main_window(f"Deleted message {msg.id}")
            except Exception as e:
                forward_log_to_main_window(f"Error deleting message {msg.id}: {e}")
    
    try:
        global full_bot_username
        forward_log_to_main_window(f"{ctx.author.name} deleted all messages in relation to {full_bot_username} in {channel.name}")
        #await ctx.send(f"{ctx.author.name} All messages from {interaction.user} deleted from {channel.name}")
        #await interaction.followup.send(f"All messages from {interaction.user} deleted from {channel.name}", ephemeral=True)
    except Exception as e:
        forward_log_to_main_window(f"Error sending follow-up message: {e}")

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()# Remove title bar and borders
        self.root.title("DndAutoClickBot UI")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # self.logger = logging.getLogger('DndAutoClickBot')
        # self.logger.setLevel(logging.DEBUG)

        # Create a frame for the username entry
        self.username_frame = tk.ttk.Frame(self.root)
        self.username_frame.pack(padx=20, pady=20)

        # Create a label for the username input
        self.username_label = tk.ttk.Label(self.username_frame, text="Discord Username:")
        self.username_label.pack(side=tk.LEFT, padx=5)

        # Create an entry field for the username
        self.username_entry = tk.ttk.Entry(self.username_frame)
        self.username_entry.pack(side=tk.LEFT, padx=5)

        # Create a submit button
        self.submit_button = tk.ttk.Button(self.username_frame, text="Login", command=self.handle_submit)
        self.submit_button.pack(side=tk.LEFT, padx=5)

        # Create a label to display the cursor position
        self.label = tk.Label(self.root, text="Cursor Position:", font=('Helvetica', 12), fg='red')
        self.label.pack(pady=20)
        self.update_label()  # Call update_label once to set initial text
        self.listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()

        # Set up the update timer
        self.root.after(1000, self.update)  # Reduce update interval to 50ms

        # Create a scrolled text widget for logs
        self.log_text = scrolledtext.ScrolledText(self.root, height=20, width=60)
        self.log_text.pack(pady=10)

    def log(self, message, level=logging.INFO):
        self.log_text.insert(tk.END, message + "\n")

    def handle_submit(self):
        username = self.username_entry.get()
        if username:
            # Store the username or perform any necessary action
            forward_log_to_main_window(f"Submitted username: {username}")
            logging.info(f"Discord Username submitted: {username}")
            global discord_username
            discord_username = username
            if discord_username.strip():  # Check if the input is not empty
                forward_log_to_main_window(f"Discord username set to: {discord_username}")
            else:
                forward_log_to_main_window("No username submitted")

    def on_move(self, x, y):
        self.cursor_position = f"X: {x}, Y: {y}"
        self.root.after(0, self.update_label)

    def update_label(self):
        if self.root.winfo_exists():
            if hasattr(self, 'cursor_position'):
                self.label.config(text=f"{self.cursor_position}", fg='black')
            else:
                self.label.config(text="Waiting...", fg='red')

    def update(self):
        self.root.after(50, self.update)

    def run(self):
        self.root.mainloop()

    def on_closing(self):
        global root
        try:
            forward_log_to_main_window("Cleaning up...")
            # Close the mouse listener
            self.listener.stop()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(bot.close())
            except Exception as e:
                forward_log_to_main_window(f"Error closing Discord bot: {e}")
            finally:
                try:
                    # Close any open GUI windows
                    my_window.root.destroy()
                    # Clean up any other resources 
                    my_window.root.quit()
                except Exception as e:
                    print(f"Error quitting root window: {e}")
                print("Cleanup complete.")
        except Exception as e:
            print(f"An error occurred during cleanup: {str(e)}")

def main():
    global my_window
    my_window = MainWindow()
    #discord_thread = threading.Thread(target=lambda: bot.run(os.getenv('BOT_TOKEN')))
    # Start the Discord bot in a separate thread
    discord_thread = threading.Thread(target=lambda: asyncio.run(bot.run(os.getenv('BOT_TOKEN'))))
    discord_thread.daemon = True  # So that it stops when the main program exits
    discord_thread.start()

    my_window.run()
    discord_thread.join()

if __name__ == "__main__":
    main()