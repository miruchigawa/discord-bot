# Discord Bot Template
A kawaii-themed Discord bot featuring economy system, anime interactions, AI image generation, and administrative tools.

## Features
- Economy system with experience, levels, and currency
- Anime-themed interaction commands using waifu.it API
- AI image generation using Stable Diffusion
- Administrative tools for server management
- Detailed logging system
- MongoDB integration for data persistence
- Interactive games with rewards (TicTacToe)

## Setup
1. Create a new Discord bot and get the token
2. Create a new MongoDB database and get the connection string
3. Create a waifu.it account and get API token
4. Set up Stable Diffusion API endpoint
5. Copy `.env.example` to `.env` and modify the values:
   ```
   DISCORD_TOKEN=<your discord bot token>
   MONGO_URI=<your mongodb connection string>
   DB_NAME=<your database name>
   WAIFU_IT_TOKEN=<your waifu.it api token>
   STABLE_DIFFUSION_URL=<your stable diffusion api url> (comma separated for multiple servers)
   ```
6. Install dependencies
7. Run the bot with `python main.py`

## Project Structure
| Folder/File | Description |
| --- | --- |
| `cogs/` | Bot command modules (economy, anime, admin, games, wfx) |
| `utils/` | Utility classes (database, logger, helper) |
| `lib/` | External library wrappers (stablediffusion, waifuit, tickengine) |
| `main.py` | Main bot initialization |
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

### AI Image Generation Commands
- `wfx generate` - Generate anime-style images (costs 100 money)
  - Quality options: low, medium, high
  - Multiple aspect ratios: 1:1, 9:7, 7:9, etc.
  - Customizable steps and CFG scale
- `wfx models` - Show available Stable Diffusion models

### Games Commands
- `tictactoe [difficulty]` - Play TicTacToe against the computer
  - Difficulty options: easy, medium, hard
  - Rewards for winning:
    - Easy: 100 EXP, 50 Money
    - Medium: 250 EXP, 125 Money
    - Hard: 500 EXP, 250 Money

### Admin Commands
- `serverinfo` - Display detailed server information
- `sysinfo` - Show system resource usage
- `ban` - Ban a member from the server
- `unban` - Unban a user from the server
- `reload` - Reload specific cog (owner only)
- `shell` - Execute shell commands (owner only)
- `debug` - Evaluate Python code (owner only)
- `addmoney` - Add money to a user or my self

## Creating Cogs
Cogs help organize bot commands and listeners. Here's how to create a new cog:

1. Create a new file in the `cogs` folder (e.g. `mycog.py`)

2. Use this basic template:
   ```python
   import discord
   from discord.ext import commands
   from typing import Optional

   class MyCog(commands.Cog):
       """Description of your cog's purpose"""
       
       def __init__(self, bot: commands.Bot) -> None:
           self.bot = bot
           
       @commands.hybrid_command(
           name="mycommand",
           description="What this command does"
       )
       async def my_command(self, ctx: commands.Context) -> None:
           """Command description"""
           await ctx.send("(◕‿◕✿) Hello!")
           
   async def setup(bot: commands.Bot) -> None:
       await bot.add_cog(MyCog(bot))
   ```

3. The cog will be automatically loaded by the bot on startup

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
   - Follow the kawaii-themed message style
   - Implement proper permission checks

## License
This project is open-sourced under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please feel free to submit a pull request.

## Credits
- [waifu.it](https://waifu.it/) for anime images
- [Stable Diffusion Webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) for AI image generation interface
- [MongoDB](https://www.mongodb.com/) for data storage
- [Discord.py](https://discord.py.org/) for Discord API integration
- [Python](https://www.python.org/) for the programming language

## Contact
If you have any questions or suggestions, please feel free to contact me:

- [Discord](https://discord.gg/HXAwkFPK5d)
- [Twitter](https://x.com/miruchigawa)
- [Email](mailto:miruchigawa@outlook.jp)
