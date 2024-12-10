# Discord Bot Template
A modular Discord bot featuring economy system, anime interactions, and administrative tools.

## Features
- Economy system with experience, levels, and currency
- Anime-themed interaction commands using waifu.it API
- Administrative tools for server management
- Interactive CLI interface for bot management
- Detailed logging system
- MongoDB integration for data persistence

## Setup
1. Create a new Discord bot and get the token
2. Create a new MongoDB database and get the connection string
3. Create a waifu.it account and get API token
4. Copy `.env.example` to `.env` and modify the values:
   ```
   DISCORD_TOKEN=<your discord bot token>
   MONGO_URI=<your mongodb connection string>
   DB_NAME=<your database name>
   WAIFU_IT_TOKEN=<your waifu.it api token>
   ```
5. Sync module with `uv sync`
6. Run the bot with `uv run main.py`

## Project Structure
| Folder/File | Description |
| --- | --- |
| `cogs/` | Bot command modules (economy, anime, admin) |
| `utils/` | Utility classes (database, logger, helper) |
| `lib/` | External library wrappers |
| `main.py` | Main bot initialization and CLI interface |
| `config.py` | Centralized configuration management |

## Available Commands

### Economy Commands
- `profile` - View user level, exp and balance
- `leaderboard` - Server rankings by exp
- `daily` - Claim daily rewards (exp or money)
- `give` - Transfer money to other users

### Anime Commands
- `hug` - Send hugging anime GIF
- `pat` - Send headpatting anime GIF
- `kiss` - Send kissing anime GIF
- `cry` - Send crying anime GIF
- `neko` - Send random neko image

### Admin Commands
- `serverinfo` - Display detailed server information
- `ban` - Ban a member from the server
- `unban` - Unban a user from the server

## Creating Cogs
Cogs help organize bot commands and listeners. Here's how to create a new cog:

1. Create a new file in the `cogs` folder (e.g. `mycog.py`)

2. Use this basic template:
   ```python
   import discord
   from discord.ext import commands

   class MyCog(commands.Cog):
       """Description of your cog's purpose"""
       
       def __init__(self, bot: commands.Bot) -> None:
           self.bot = bot
           
       @commands.hybrid_command(name="mycommand")
       async def my_command(self, ctx: commands.Context) -> None:
           """Command description"""
           await ctx.send("Hello!")
           
   async def setup(bot: commands.Bot) -> None:
       await bot.add_cog(MyCog(bot))
   ```

3. The cog will be automatically loaded by the bot as it scans the `cogs/` directory on startup. No manual registration needed.

4. Key components:
   - `commands.Cog` - Base class for all cogs
   - `@commands.hybrid_command()` - Creates slash + text commands
   - `@commands.Cog.listener()` - For event listeners
   - `async def setup()` - Required to load the cog
   - Type hints for better code clarity

5. Best practices:
   - Keep related commands in the same cog
   - Add docstrings to your commands and classes
   - Handle errors appropriately
   - Use type hints consistently
   - Follow the existing code style

6. Reloading cogs:
   - Use the CLI command `reload` to reload all cogs
   - This will unload existing cogs and load them again
   - Useful during development

## CLI Commands
- `help` - Show available CLI commands
- `status` - Show bot status (name, latency, guilds)
- `metrics` - Show system metrics (CPU, RAM, disk)
- `reload` - Reload all cogs
- `clear` - Clear console screen
- `quit/exit` - Shutdown bot

## License
This project is open-sourced under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please feel free to submit a pull request.

## Contact
For questions or feedback, please contact the project maintainer at [miruchigawa@outlook.jp](mailto:miruchigawa@outlook.jp).