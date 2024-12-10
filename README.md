# Discord Bot Template
Modular Discord bot with economy, leveling, and more.

## Setup
1. Create a new Discord bot and get the token.
2. Create a new MongoDB database and get the connection string.
3. Copy `.env.example` to `.env` and modify the values:
   ```
   DISCORD_TOKEN=<your discord bot token>
   MONGO_URI=<your mongodb connection string>
   DB_NAME=<your database name>
   ```
4. Sync module with `uv sync`
5. Run the bot with `uv run main.py`

## Project Structure
| Folder | Description |
| --- | --- |
| `cogs/` | Cogs for the bot. |
| `utils/` | Utility functions and classes. |
| `main.py` | Main entry point for the bot. |
| `config.py` | Configuration settings. |
| `README.md` | This file. |


## Creating Cogs
Cogs are modules that help organize bot commands and listeners. Here's how to create a new cog:

1. Create a new file in the `cogs` folder (e.g. `mycog.py`)

2. Use this basic template:
   ```python
   import discord
   from discord.ext import commands

   class MyCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
           
       @commands.hybrid_command(name="mycommand")
       async def my_command(self, ctx):
           await ctx.send("Hello!")
           
   async def setup(bot):
       await bot.add_cog(MyCog(bot))
   ```

3. Register your cog in `main.py`:
   ```python
   await bot.load_extension("cogs.mycog")
   ```

4. Key components to know:
   - `commands.Cog` - Base class for all cogs
   - `@commands.hybrid_command()` - Creates slash + text commands
   - `@commands.Cog.listener()` - For event listeners
   - `async def setup()` - Required to load the cog

5. Best practices:
   - Keep related commands in the same cog
   - Add docstrings to your commands
   - Handle errors appropriately
   - Follow the existing code style

For more examples, check the existing cogs in the `cogs/` folder.

## License
This project is open-sourced under the Apache 2.0 License - see the [LICENSE] file for details.

## Contributing
Contributions are welcome! Please feel free to submit a pull request.

## Contact
For any questions or feedback, please contact the project maintainer at [miruchigawa@outlook.jp].
