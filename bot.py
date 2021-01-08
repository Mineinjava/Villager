import pickle
from chatterbot import ChatBot
import discord
import json
import random
from discord.ext import commands
import os

client = commands.Bot(command_prefix='%')
# note: I never use the commands 

chatbot = ChatBot('Warden')

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

# with open("convo.pkl", "wb") as fp:   #Pickling
# pickle.dump(convo, fp)

try:
    with open('convo.pkl', 'rb') as fp:  # Unpicklingdir
        convo = pickle.load(fp)
except Exception:
    with open("convo.pkl", "wb") as fp:  # Pickling
        pickle.dump(convo, fp)

silenceMode = False


@client.event
async def on_ready():
    print('We have logged in as {0.user} (chatbot mode)'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '%' in message.content:  # change to bot prefix
        return

    if "http" in message.content:
        return

    contnt = message.content
    if silenceMode == False:
        shouldRespond = random.randint(1, 5)
        if shouldRespond == 1:
            return
        response = chatbot.get_response(contnt)
        print(response)
        await message.channel.send(response)

    if message.author.bot:
        return
    else:
        convo.append(message.content)


@client.command()
async def learn(ctx):
    await ctx.send("re-learning...")
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
    await ctx.send("recalibrated AI")


token = os.environ['TOKEN']
client.run(token)
