import asyncio
import discord
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.session import ApplicationMessage
from hbmqtt.mqtt.constants import QOS_1, QOS_2, QOS_0
import re
import yaml

async def run_mqtt():
    mqttClient = MQTTClient()
    await mqttClient.connect(CONFIG['mqtt']['uri'])

    await mqttClient.subscribe([
 #           ('$SYS/broker/uptime', QOS_1),
 #           ('$SYS/broker/load/#', QOS_2),
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


class DiscordClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

CONFIG = yaml.safe_load(open("config.yml"))
discordClient = DiscordClient()

asyncio.run(asyncio.wait({run_mqtt()}, return_when=asyncio.FIRST_EXCEPTION))
#asyncio.run(asyncio.wait({discordClient.start(CONFIG['discord']['token'])}, return_when=asyncio.FIRST_EXCEPTION))
#asyncio.run(asyncio.wait({run_mqtt(), discordClient.start(CONFIG['discord']['token'])}, return_when=asyncio.FIRST_EXCEPTION))

#if __name__ == '__main__':