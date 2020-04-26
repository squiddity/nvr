import asyncio
import aiofiles
import discord
from pathlib import Path
import sys
import re

class Dom5Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.ready_event = asyncio.Event()

    async def on_ready(self):
        print('Logged on as {0.user}!'.format(self))
        channel = discord.utils.get(self.get_all_channels(), name='general')
        print ("sending message")
        turn = await get_turn()
        message = 'Time flows onwards in world {0} to turn {1}.'.format(sys.argv[2], turn)
        print (message)
        #await channel.send(message)
        await self.close()

async def get_turn():
    dom5sh = Path.home() / '.steam' / 'steam' / 'steamapps' / 'common' / 'Dominions5' / 'dom5.sh'
    #print(dom5sh)
    #print(dom5sh.exists())
    savedgamedir = Path.home() / '.dominions5' / 'savedgames' / sys.argv[2]
    #print(savedgamedir)
    #print (savedgamedir.exists())
    dom5process = await asyncio.create_subprocess_shell(
        '{0} --nosteam --verify {1}'.format(str(dom5sh), sys.argv[2]))
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
    print (sys.argv[1])
    await asyncio.wait({dom5Bot.start(sys.argv[1])}, return_when=asyncio.FIRST_EXCEPTION)

if __name__ == '__main__':
    asyncio.run(main())
