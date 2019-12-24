import asyncio
import discord
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.session import ApplicationMessage
from hbmqtt.mqtt.constants import QOS_0
from io import BytesIO
import os
import re
import time

CHANNEL_LASTSENT = {}

async def run_mqtt(mqttClient: MQTTClient, discordClient: discord.Client):
    print ("starting MQTT")
    await mqttClient.connect(os.environ.get('MQTT'))

    await mqttClient.subscribe([('frigate/+/snapshot', QOS_0)])

    try:
        while True:
            message = await mqttClient.deliver_message()
            await handle_snapshot_message(message, discordClient)
    finally:
        await mqttClient.unsubscribe(['frigate/+/snapshot'])
        await mqttClient.disconnect()


async def handle_snapshot_message(message: ApplicationMessage, discordClient: discord.Client):
    message_topic = message.topic
    camera_id_match = re.search('frigate/(.+?)/snapshot', message_topic)
    if camera_id_match:
        camera_id = camera_id_match.group(1)
    else:
        print("could not parse topic ", message_topic)
        return
    print("snapshot received: ", camera_id)

    elapsed_time  = time.time() - CHANNEL_LASTSENT.get(camera_id, 0)
    if elapsed_time < 10:
        print("throttling and discarding snapshot for", camera_id, elapsed_time)
        return
    else:
        print("new snapshot throttle set for", camera_id)
        CHANNEL_LASTSENT[camera_id] = time.time()

    snapshot_data = message.data
    snapshot_file = discord.File(BytesIO(snapshot_data), filename="snapshot.jpg")

    channel = discord.utils.get(discordClient.get_all_channels(), name=camera_id)
    if channel:
        print("sending snapshot to", channel.name)
        await channel.send(file=snapshot_file)
    else:
        print("could not find channel", camera_id)

async def run_discord(discordClient: discord.Client):
    print ("starting Discord")
    await discordClient.start(os.environ.get('DISCORD'))

class DiscordClient(discord.Client):
   async def on_ready(self):
       print('Logged on as {0}!'.format(self.user))

async def main():
    discordClient = DiscordClient()
    mqttClient = MQTTClient()
    await asyncio.wait({run_mqtt(mqttClient, discordClient), run_discord(discordClient)}, return_when=asyncio.FIRST_EXCEPTION)

if __name__ == '__main__':
    asyncio.run(main())
