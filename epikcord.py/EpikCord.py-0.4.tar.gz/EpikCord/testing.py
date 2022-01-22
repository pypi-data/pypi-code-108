from EpikCord import *


client = Client("ODk4MjY4MjI3MjE2NTA2OTQw.YWhveg.PeQ0IZhJKEwNeoh8wWJ4PcK5TVQ", 513)

@client.event
async def interaction(interaction: dict):
    interaction = BaseInteraction(client, interaction)
    await interaction.reply({"content": "Hello World"})
    
client.login()