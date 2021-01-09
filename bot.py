import pickle
from chatterbot import ChatBot
import discord
import json
import random
from discord.ext import commands, tasks
import os
import profanity_filter
import traceback

pf = profanity_filter.ProfanityFilter()

client = commands.Bot(command_prefix='%')


chatbot = ChatBot('Villager')

# train ML
from chatterbot.trainers import ChatterBotCorpusTrainer

trainer = ChatterBotCorpusTrainer(chatbot)
from chatterbot.trainers import ListTrainer

trainer.train(
    "chatterbot.corpus.english.botprofile",
    "chatterbot.corpus.english.conversations",
    "chatterbot.corpus.english.humor"
)
listtrainer = ListTrainer(chatbot)
# make it so
convo = ["hello there", "hi"]

guilds = None

# with open("convo.pkl", "wb") as fp:   #Pickling
# pickle.dump(convo, fp)

try:
    with open('convo.pkl', 'rb') as fp:  # Unpickling
        convo = pickle.load(fp)
except Exception:
    with open("convo.pkl", "wb") as fp:  # Pickling
        pickle.dump(convo, fp)

silenceMode = False
silenceChannels = []


try:
    with open('channel_blacklist.pkl', 'rb') as fp:  # Unpickling
        silenceChannels = pickle.load(fp)
except Exception:
    with open("channel_blacklist.pkl", "wb") as fp:  # Pickling
        pickle.dump(silenceChannels, fp)




@client.event
async def on_ready():
    print('We have logged in as {0.user} (chatbot mode)'.format(client))
    guilds__ = len(client.guilds)
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(f"Talking with {guilds__} Servers"))



@client.event
async def on_message(message):
    if message.author == client.user:
        return

    await client.process_commands(message)
    if '%' in message.content:  # change to bot prefix
        return

    if "http" in message.content:
        return

    contnt = message.content
    if message.channel.id in silenceChannels:
        shouldRespond = random.randint(1, 5)
        if shouldRespond == 1:
            return
        response = chatbot.get_response(contnt)
        print(response)
        await message.channel.send(response)

    else:
        shouldRespond = random.randint(1, 20)
        if shouldRespond == 1:
            response = chatbot.get_response(contnt)
            print(response)
            await message.channel.send(response)


    if message.author.bot:
        return
    elif pf.is_clean(message.content):
        convo.append(message.content)
    else:
        print('message censored')

@client.command()
@commands.check(commands.is_owner())
async def learn(ctx):
    print("re-learning...")
    trainer.train(
        "chatterbot.corpus.english.botprofile",
        "chatterbot.corpus.english.conversations",
        "chatterbot.corpus.english.humor"
    )
    listtrainer.train(
        convo
    )
    with open("convo.pkl", "wb") as fp:  # Pickling
        pickle.dump(convo, fp)
    print("recalibrated AI")
    await ctx.send("re-learned")

@client.command()
@commands.check_any(commands.is_owner(), commands.is_guild_owner())
async def allowChannel(ctx):
    try:
        silenceChannels.append(ctx.message.channel.id)
    except Exception:
        await ctx.send('could not add this channel')
        return
    else:
        await ctx.send("added this channel. I will talk alot more here...")




@tasks.loop(minutes=500)
async def learn_auto():
    print("auto-re-learning...")
    trainer.train(
        "chatterbot.corpus.english.botprofile",
        "chatterbot.corpus.english.conversations",
        "chatterbot.corpus.english.humor"
    )
    listtrainer.train(
        convo
    )
    with open("convo.pkl", "wb") as fp:  # Pickling
        pickle.dump(convo, fp)
    print("recalibrated AI")


token = os.environ['TOKEN']
client.run(token)
