import openai
import json
import discord

openai.api_key = ""
discord_key = ""
character = ""
memory_size = 10
allowed_users = []

description = []
conversation = []

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def main():
	load_character(character)
	load_conversation()
	client.run(discord_key)
	save_conversation()


@client.event
async def on_message(message):
	if message.author.id not in allowed_users:
		return
	
	if not message.content.startswith("!"):
		return
	
	if message.content == "!save":
		save_conversation()
		return
	
	if is_flagged(message.content):
		return
	
	conversation.append({"role": "user", "content": message.content})

	prompt_resp = openai.ChatCompletion.create(
		model = "gpt-3.5-turbo",
		max_tokens = 128,
		temperature = 1,
		top_p = 0.9,
		messages = description + conversation
	)

	text_resp = prompt_resp["choices"][0]["message"]["content"]
	conversation.append({"role": "assistant", "content": text_resp})

	trim_conversation()
	
	await message.channel.send(text_resp)


def is_flagged(text):
	mod_resp = openai.Moderation.create(input=text)
	return mod_resp["results"][0]["flagged"]


def load_character(name):
	character = ""
	with open(name, "r") as file:
		character = file.read()
	description.append({"role": "user", "content": character})
	description.append({"role": "system", "content": "Below is the conversation history."})


def load_conversation():
	with open("conversation.json", "r") as file:
		data = json.load(file)
		for message in data:
			conversation.append(message)


def save_conversation():
	with open("conversation.json", "w") as file:
		json.dump(conversation, file, indent=4)


def trim_conversation():
	if (len(conversation) > memory_size):
		conversation.pop(0)
		conversation.pop(0)


if __name__ == "__main__":
   main()