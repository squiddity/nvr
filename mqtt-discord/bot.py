import paho.mqtt.client as mqtt
import discord
import yaml

class DiscordClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

class MqttClient(mqtt.Client):
    def on_connect(self, client, userdata, rc):
        topic_sub = "frigate"
        print("Connected with result code " + str(rc) + " to topic " + topic_sub)
        client.subscribe(topic_sub)

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        message = "Melding fra MQTT med topic: " + msg.topic + " er  mottatt:\n" + msg.payload

CONFIG = yaml.safe_load(open("config.yml"))

discordClient = DiscordClient()
discordClient.run(CONFIG['discord']['token'])

mqttClient = MqttClient()
mqttClient.connect(CONFIG['mqtt']['host'], CONFIG['mqtt']['host'])
mqttClient.loop_forever()
