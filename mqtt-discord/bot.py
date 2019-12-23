import asyncio
import discord
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.session import ApplicationMessage
from hbmqtt.mqtt.constants import QOS_1, QOS_2, QOS_0
import re
import yaml

async def run_mqtt(mqttClient: MQTTClient, discordClient: discord.Client):
    await mqttClient.connect(CONFIG['mqtt']['uri'])

    await mqttClient.subscribe([
            ('frigate/+/snapshot', QOS_0),
         ])

    try:
        while True:
            message = await mqttClient.deliver_message()
            await handle_snapshot_message(message)
    finally:
        await mqttClient.unsubscribe(['frigate/+/snapshot'])
        await mqttClient.disconnect()


async def handle_snapshot_message(message: ApplicationMessage):
    message_topic = message.topic
    camera_id_match = re.search('frigate/(.+?)/snapshot', message_topic)
    if camera_id_match:
        camera_id = camera_id_match.group(1)
    else:
        print("could not parse topic ", message_topic)
        return
    print("snapshot found: ", camera_id)
    snapshot_data = message.data


async def run_discord(discordClient: discord.Client):
    print ("starting Discord")
    await discordClient.start(CONFIG['discord']['token'])

class DiscordClient(discord.Client):
   async def on_ready(self):
       print('Logged on as {0}!'.format(self.user))

   async def on_message(self, message):
       print('Message from {0.author}: {0.content}'.format(message))

CONFIG = yaml.safe_load(open("config.yml"))

async def main():
    discordClient = DiscordClient()
    mqttClient = MQTTClient()
    await asyncio.wait({run_mqtt(mqttClient, discordClient), run_discord(discordClient)}, return_when=asyncio.FIRST_EXCEPTION)

if __name__ == '__main__':
    asyncio.run(main())