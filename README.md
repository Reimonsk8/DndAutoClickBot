# DndAutoClickBot

This bot allows you to automate some helpful DarknDarker Actions:

## Features

- Automatic build.bat file to create a single executable file
- Easy setup with a .env file and server role creation
- User verification system for secure command execution

## Setup Instructions

1. Create a `.env` file adding your BOT_TOKEN="yourbottokenhere"
2. Create a role named "DndAutoClickBotUser" in your server settings
3. Add desired users to this role
4. When running the .exe, enter your exact Discord username in the terminal
5. Verify the list of allowed users using the `!listusers` command

## Available Commands

### General Commands

- `!help`: See all available commands
- `!info`: View detailed instructions
- `!listusers`: Display the current list of allowed users
- `!clear`: Create a button to delete all bot messages in the channel
- `!update`: Download and install the latest client version from our website
- `!switchall`: Toggle all values On or Off for other users controlling commands
- `!switch [option]`: Switch the value of a single option controlled by other users

### Action Options

- `!lobby [user]`: Set player on lobby tab (default applies to all)
- `!ready [user]`: Set player ready for the dungeon (default applies to all)
- `!meds [2] [user]`: Purchase meds (2 sets default) automatically
- `!karma [user]`: Give good karma to the top first player on screen (default applies to all)

## Usage Notes

- Ensure you have the necessary permissions ("DnDAutoClickBotUser" or "Admin" role)
- Some commands require verification before execution
- Always double-check coordinates when using click/move commands

For more detailed information and troubleshooting, please refer to the project's documentation or contact the developers.