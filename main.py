import discord
from discord.ext import commands
import os
import psutil
import asyncio
import platform
import aioconsole
import sys
from dotenv import load_dotenv
from utils.logger import Logger
from utils.helper import Help
from typing import Dict, Callable, Awaitable, Optional, List, Any
import signal
from utils.database import Database

class DiscordBot:
    """A Discord bot class that handles events, commands, and CLI operations.
    
    Attributes:
        token (str): The Discord bot token from environment variables
        bot (commands.Bot): The main Discord bot instance
        logger (Logger): Custom logger instance for bot operations
        running (bool): Flag to control the CLI shell loop
    """
    
    def __init__(self) -> None:
        self._setup_env()
        self._setup_bot()
        self._setup_signal_handlers()
        self.bot.db = None
        
    def _setup_env(self) -> None:
        """Set up environment variables"""
        load_dotenv()
        self.token: str = os.getenv('DISCORD_TOKEN')
        if not self.token:
            raise ValueError("⚠️ Bot token not found in .env file!")

    def _setup_bot(self) -> None:
        """Set up bot instance and configurations"""
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True 
        intents.members = True

        self.bot: commands.Bot = commands.Bot(
            command_prefix='!', 
            intents=intents,
            help_command=Help()
        )
        self.logger: Logger = Logger()
        self.running: bool = True
        self.setup_events()

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown"""
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle system signals for graceful shutdown"""
        self.running = False
        asyncio.create_task(self._shutdown())

    def setup_events(self) -> None:
        """Set up bot event handlers for error handling and ready state."""
        @self.bot.event
        async def on_command_error(ctx: commands.Context, error: Exception) -> None:
            error_messages: Dict[type, str] = {
                commands.CommandNotFound: "(｡•́︿•̀｡) Oopsie! Command not found. Try checking available commands~",
                commands.MissingPermissions: "(｡T ω T｡) Gomen ne~ You don't have permission to use this command!",
                commands.MissingRequiredArgument: "(◕︿◕✿) Ah! You're missing something important. Please check the command usage~"
            }
            message: str = error_messages.get(type(error), f"(╥﹏╥) Oh no! Something went wrong: {str(error)}")
            await ctx.send(message)

        @self.bot.event
        async def on_ready() -> None:
            self.logger.info(f'✨ Logged in as {self.bot.user.name}')
            self.logger.info('🚀 Bot is ready')
            await self._initialize_bot()

    async def _initialize_bot(self) -> None:
        """Initialize bot components"""
        self.bot.db = Database()
        await self.bot.db.connect()
        self.logger.info('✨ Successfully connected to MongoDB')

        await self.load_cogs()
        await self.sync_commands()
        self.bot.loop.create_task(self.cli_shell())

    async def sync_commands(self) -> None:
        """Sync slash commands globally."""
        try:
            synced = await self.bot.tree.sync()
            self.logger.info(f'✨ Successfully synced {len(synced)} slash commands')
        except Exception as e:
            self.logger.error(f'❌ Failed to sync slash commands: {str(e)}')

    async def _manage_extension(self, extension: str, action: str) -> bool:
        """Manage cog extension loading/unloading
        
        Args:
            extension (str): The extension name
            action (str): Either 'load' or 'unload'
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if action == 'load':
                await self.bot.load_extension(extension)
            else:  # unload
                await self.bot.unload_extension(extension)
            self.logger.info(f'✨ Successfully {action}ed cog: {extension}')
            return True
        except Exception as e:
            self.logger.error(f'❌ Failed to {action} cog {extension}: {str(e)}')
            return False

    async def load_cogs(self) -> None:
        """Load all cog extensions from the cogs directory.""" 
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                extension = f'cogs.{filename[:-3]}'
                await self._manage_extension(extension, 'load')

    async def unload_cogs(self) -> None:
        """Unload all currently loaded cog extensions."""
        for extension in list(self.bot.extensions):
            await self._manage_extension(extension, 'unload')
            
    async def cli_shell(self) -> None:
        """Start an interactive CLI shell for bot management."""
        commands: Dict[str, Callable[[], Awaitable[None]]] = {
            "quit": self._shutdown,
            "exit": self._shutdown,
            "reload": self.handle_reload,
            "status": self.handle_status,
            "metrics": self.handle_metrics,
            "help": self.handle_help,
            "clear": self.handle_clear
        }

        while self.running:
            try:
                command: str = await aioconsole.ainput("🐚 > ")
                cmd: str = command.lower().strip()
                
                if not cmd:
                    continue
                    
                handler: Optional[Callable[[], Awaitable[None]]] = commands.get(cmd)
                if handler:
                    await handler()
                else:
                    self.logger.warning("❓ Unknown command")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error executing command: {str(e)}")

    async def _shutdown(self) -> None:
        """Gracefully shutdown the bot and cleanup resources"""
        if not self.running:  # Prevent multiple shutdown attempts
            return
            
        self.running = False
        self.logger.info("🛑 Shutting down bot...")
        
        try:
            await self.bot.close()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
        finally:
            await asyncio.sleep(0.5)  # Brief pause for cleanup
            sys.exit(0)

    async def handle_reload(self) -> None:
        """Reload bot cogs and sync commands"""
        self.logger.info("🔄 Reloading cogs...")
        await self.unload_cogs()
        await self.load_cogs()
        await self.sync_commands()

    async def handle_status(self) -> None:
        """Display bot status information"""
        status_info: str = f'🤖 {self.bot.user.name if self.bot.user else "Not Connected"} | ⚡ {round(self.bot.latency * 1000)}ms | 🌐 {len(self.bot.guilds)}'
        self.logger.info(status_info)

    async def handle_metrics(self) -> None:
        """Display system metrics"""
        cpu_usage: float = psutil.cpu_percent()
        memory: Any = psutil.virtual_memory()
        disk: Any = psutil.disk_usage('/')
        metrics_info: str = f'📊 {cpu_usage}% | 💻 {memory.percent}% | 💾 {disk.percent}%'
        self.logger.info(metrics_info)

    async def handle_help(self) -> None:
        """Display available CLI commands and their descriptions."""
        help_text: str = """
        Available Commands:
        - help    : Show this help message
        - status  : Show bot status (name, latency, guilds)
        - metrics : Show system metrics (CPU, RAM, disk usage)
        - reload  : Reload all cogs
        - clear   : Clear the console screen
        - quit    : Shutdown the bot
        - exit    : Alias for quit
        """
        self.logger.info(help_text)

    async def handle_clear(self) -> None:
        """Clear the console screen."""
        os.system('cls' if platform.system() == 'Windows' else 'clear')

    def run(self) -> None:
        """Start the Discord bot."""
        self.bot.run(self.token)

def main() -> None:
    """Main entry point for the Discord bot application."""
    bot: DiscordBot = DiscordBot()
    bot.run()

if __name__ == "__main__":
    main()