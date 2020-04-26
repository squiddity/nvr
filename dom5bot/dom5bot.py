import asyncio
import aiofiles
import discord
from pathlib import Path
import sys
import os
import re

class Dom5Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.ready_event = asyncio.Event()
        self.dom5sh = Path.home() / '.steam' / 'steam' / 'steamapps' / 'common' / 'Dominions5' / 'dom5.sh'

    async def on_ready(self):
        print('Logged on as {0.user}!'.format(self))
        # double check dom5.sh exists, otherwise shut down
        if (not self.dom5sh.exists()):
            print ("could not find dom5.sh at {0}".format(self.dom5sh))
            self.close()
            return

        # set up listen server
        await asyncio.start_server(self.on_ping_connected, '127.0.0.1', os.environ.get('PORT'))
        self.ready_event.set()


    async def send_game_update(self, gamename):
        channelname = os.environ.get('CHANNEL')
        channel = discord.utils.get(self.get_all_channels(), name=channelname)
        if (not channel):
            print ('could not find channel: {0}'.format(channelname))
            return
        turn = await self.get_turn(gamename)
        if (turn):
            message = 'Time flows onwards in world {0} to turn {1}.'
            message = message.format(gamename, turn)
            print ('message to {0}: {1}'.format(channelname, message))
            #await channel.send(message)
        else:
            print ('turn could not be found for {0}'.format(gamename))

    async def on_ping_connected(self, reader, writer):
        print ("client connected")
        data = await reader.read(1024)
        writer.close()
        gamename = data.decode("utf-8")
        print ('game: {0}'.format(gamename))
        await self.send_game_update(gamename)
        

    async def get_turn(self, gamename):
        savedgamedir = Path(os.environ.get('DOM5DIR')) / 'savedgames' / gamename
        if (not savedgamedir.exists()):
            print ('saved game could not be found at: {0}'.format(savedgamedir))
            return None
        dom5process = await asyncio.create_subprocess_shell(
            '{0} --nosteam --verify {1}'.format(str(self.dom5sh), gamename))
        await dom5process.wait()
        chkfilelist = list(savedgamedir.glob('*.chk'))
        #print (len(chkfilelist))
        chkfile = chkfilelist[0]
        #print (chkfile)
        #print (chkfile.exists())
        async with aiofiles.open(str(chkfile), mode='r') as f:
            contents = await f.read()
            pattern = re.compile('turnnbr (\d+)')
            match = pattern.search(contents)
            # print(match.group(1))
            print ('turn is {0}'.format(match.group(1)))
            return match.group(1)
        
async def main():
    dom5Bot = Dom5Bot()
    print ('starting with token: {0}'.format(os.environ.get('DISCORD')))
    await asyncio.wait({dom5Bot.start(os.environ.get('DISCORD'))}, return_when=asyncio.FIRST_EXCEPTION)

if __name__ == '__main__':
    asyncio.run(main())
