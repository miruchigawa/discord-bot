import discord
from discord.ext import commands
from lib.tickengine import TicTacToeEngine, Difficulty
from typing import Dict, Optional, Tuple

class TicTacToeView(discord.ui.View):
    """View class for TicTacToe game interface"""
    def __init__(self, game: TicTacToeEngine, player_id: int, cog):
        super().__init__(timeout=60)
        self.game = game
        self.player_id = player_id
        self.cog = cog
        self._update_buttons()

    def _update_buttons(self):
        """Update button labels and styles based on current game state"""
        board = self.game.get_board_state()
        for i in range(3):
            for j in range(3):
                button = discord.ui.Button(
                    label='⬜' if board[i][j] == ' ' else board[i][j],
                    style=discord.ButtonStyle.secondary if board[i][j] == ' ' else 
                          discord.ButtonStyle.success if board[i][j] == 'X' else 
                          discord.ButtonStyle.danger,
                    row=i,
                    custom_id=f"ttt_{i}_{j}"
                )
                button.callback = self.button_callback
                self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        """
        Handle button click interactions for the game
        
        Parameters
        ----------
        interaction: The interaction event from the button click
        """
        if interaction.user.id != self.player_id:
            await interaction.response.send_message(
                "(｡T ω T｡) This is not your game!", 
                ephemeral=True
            )
            return

        if self.game.is_game_over():
            await interaction.response.send_message(
                "(｡T ω T｡) Game is already over!", 
                ephemeral=True
            )
            return

        custom_id = interaction.data["custom_id"]
        _, row, col = custom_id.split('_')
        row, col = int(row), int(col)

        if self.game.make_move(row, col):
            self.clear_items()
            self._update_buttons()

            if self.game.is_game_over():
                winner = self.game.get_winner()
                if winner:
                    if winner == 'X':
                        rewards = await self.cog._handle_game_rewards(
                            interaction.user.id,
                            interaction.guild_id,
                            self.game.difficulty.value
                        )
                        content = (
                            f"(◕‿◕✿) You won! Here's your reward:\n" + \
                            f"✨ +{rewards['exp']} EXP\n" + \
                            f"💰 +{rewards['money']} Money"
                        )
                    else:
                        content = "(｡•́︿•̀｡) Computer won!"
                else:
                    content = "(｡◕‿◕｡) It's a draw!"
                
                for child in self.children:
                    child.disabled = True
                    
                if self.player_id in Games.active_games:
                    del Games.active_games[self.player_id]
            else:
                content = "(◕ᴗ◕✿) Your turn!"

            await interaction.response.edit_message(
                content=content,
                view=self
            )
        else:
            await interaction.response.send_message(
                "(｡•́︿•̀｡) Invalid move!", 
                ephemeral=True
            )

class Games(commands.Cog):
    """Cog containing fun games to play with the bot"""
    
    active_games: Dict[int, Tuple[TicTacToeEngine, TicTacToeView]] = {}

    DIFFICULTY_REWARDS = {
        "easy": {"exp": 100, "money": 50},
        "medium": {"exp": 250, "money": 125},
        "hard": {"exp": 500, "money": 250}
    }

    def __init__(self, bot: commands.Bot):
        """
        Initialize Games cog
        
        Parameters
        ----------
        bot: The bot instance
        """
        self.bot = bot

    @commands.hybrid_command(
        name="tictactoe",
        description="Play TicTacToe against the computer and earn rewards!"
    )
    async def tictactoe(
        self, 
        ctx: commands.Context, 
        difficulty: str = "medium"
    ):
        """
        Start a TicTacToe game against the computer
        
        Parameters
        ----------
        ctx: The command context
        difficulty: The game difficulty level (easy/medium/hard)
            easy: Win to earn 100 EXP and 50 Money
            medium: Win to earn 250 EXP and 125 Money
            hard: Win to earn 500 EXP and 250 Money
        """
        if ctx.author.id in self.active_games:
            return await ctx.send(
                "(｡•́︿•̀｡) You already have an active game! " + \
                "Finish it first or wait for it to expire~"
            )

        try:
            diff = Difficulty(difficulty.lower())
            rewards = self.DIFFICULTY_REWARDS[difficulty.lower()]
        except (ValueError, KeyError):
            return await ctx.send(
                "(｡T ω T｡) Invalid difficulty! Choose: easy, medium, or hard"
            )

        game = TicTacToeEngine(difficulty=diff)
        view = TicTacToeView(game, ctx.author.id, self)
        self.active_games[ctx.author.id] = (game, view)

        await ctx.send(
            f"(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ TicTacToe Game Started! Difficulty: {difficulty}\n" + \
            f"Win to earn: ✨ {rewards['exp']} EXP and 💰 {rewards['money']} Money\n" + \
            "(◕‿◕✿) You are X, I am O. Your turn!",
            view=view
        )

        await view.wait()
        if ctx.author.id in self.active_games:
            del self.active_games[ctx.author.id]
            if not game.is_game_over():
                await ctx.send("(｡•́︿•̀｡) Game expired due to inactivity!")

    async def _handle_game_rewards(self, user_id: int, guild_id: int, difficulty: str) -> Dict[str, int]:
        """Handle rewards for winning a game
        
        Parameters
        ----------
        user_id: int
            The user ID to reward
        guild_id: int
            The guild ID where the game was played
        difficulty: str
            The game difficulty level
            
        Returns
        -------
        Dict[str, int]
            The rewards given (exp and money)
        """
        rewards = self.DIFFICULTY_REWARDS.get(difficulty.lower(), self.DIFFICULTY_REWARDS["easy"])
        
        await self.bot.db.add_money(user_id, guild_id, rewards["money"])
        
        user_data = await self.bot.db.get_user(user_id, guild_id)
        current_exp = user_data['exp'] + rewards["exp"]
        await self.bot.db.update_exp(user_id, guild_id, current_exp)
        
        return rewards

async def setup(bot: commands.Bot):
    """Setup function to add Games cog to bot"""
    await bot.add_cog(Games(bot))