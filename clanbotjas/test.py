from discord_components import Button, Select, SelectOption, ComponentsBot, ButtonStyle

import settings
bot = ComponentsBot("!")
@bot.command()
async def button(ctx):
    await ctx.send("Buttons!", components=[Button(style=ButtonStyle.blue, label="Button", custom_id="button1")],)
    interaction = await bot.wait_for(
        "button_click", check=lambda inter: inter.custom_id == "button1"
    )
    await interaction.send(content="Button Clicked")

if __name__ == "__main__":
    bot.run(settings.DISCORD_TOKEN)
