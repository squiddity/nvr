import asyncio
import aiofiles
import discord
from pathlib import Path
import sys
import os
import re

FTHERLND = 'ftherlnd'

class Dom5Bot(discord.Client):
    def __init__(self):
        super().__init__()
        self.ready_event = asyncio.Event()
        self.dom5sh = Path(os.environ.get('DOM5GAMEDIR')) / 'dom5.sh'
        self.games = set()

        
    async def on_ready(self):
        print('Logged on as {0.user}!'.format(self))
        # double check dom5.sh exists, otherwise shut down
        if (not self.dom5sh.exists()):
            print ("could not find dom5.sh at {0}".format(self.dom5sh))
            self.close()
            return

        # set up listen server
        port = os.environ.get('PORT')
        await asyncio.start_server(self.on_ping_connected, port=port)
        print ('listening at: {0}'.format(port))
        self.ready_event.set()

        
    async def on_ping_connected(self, reader, writer):
        print ("client connected")
        data = await reader.read(1024)
        writer.write("OK\n".encode())
        writer.close()
        gamename = data.decode("utf-8")
        if (len(gamename) > 0):
            print ('game: {0}'.format(gamename))
            self.games.add(gamename)
            await self.send_postcheck_update(gamename)
        else:
            print ('empty gamename')        


    async def on_message(self, message):
        if (message.content.startswith('?s')):
            print ("team status")
            channel = message.channel
            await self.send_team_status(self.games, channel)
        
            
    async def send_postcheck_update(self, gamename):
        channelname = os.environ.get('CHANNEL')
        channel = discord.utils.get(self.get_all_channels(), name=channelname)
        if (not channel):
            print ('could not find channel: {0}'.format(channelname))
            return
        self.games.add(gamename)
        turns = await self.get_turns(gamename)
        if (FTHERLND in turns):            
            turn = turns[FTHERLND]
        else:
            print("couldn't find ftherlnd, using first available")
            turn = list(turns.values())[0]

        if (turn):
            message = 'Time flows onwards in world {0} to turn {1}.'
            message = message.format(gamename, turn)
            print ('message to {0}: {1}'.format(channelname, message))
            await channel.send(message)
        else:
            print ('turn could not be found for {0}'.format(gamename))

            
    async def send_team_status(self, games, channel):
        for game in games:
            turns = await self.get_turns(game)
            done = set()
            doing = set()
            if FTHERLND in turns:
                master_turn = turns.pop(FTHERLND)
                for nation in turns.keys():
                    nation_turn = turns[nation]
                    if (nation_turn == master_turn):
                        done.add(nation)
                    elif (nation_turn == master_turn - 1):
                        doing.add(nation)
                    else:
                       print("error: game turn is {0} but nation {1} turn is {2}".format(
                            master_turn, nation, nation_turn))
                await channel.send("The age in world {0} has reached {1} turns.".format(game, master_turn))
                if (len(done) > 0):
                    await channel.send("The nations of {0} have cast their lots.".format(', '.join(done)))
                if (len(doing) > 0):
                    await channel.send("The nations of {0} have yet to follow.".format(', '.join(doing)))
            else:
                for nation in turns.keys():
                    nation_turn = turns[nation]
                    await channel.send("{0} nation {1} is at turn {2}.".format(game, nation, nation_turn))
    
    async def get_turns(self, gamename):
        userdir = Path(os.environ.get('DOM5USERDIR'))
        savedgamedir =  userdir / 'savedgames' / gamename
        if (not savedgamedir.exists()):
            print ('saved game could not be found at: {0}'.format(savedgamedir))
            return None
        dom5process = await asyncio.create_subprocess_shell(
            'DOM5_CONF={2} {0} --nosteam --verify {1}'.format(
                str(self.dom5sh), gamename, str(userdir)))
        retcode = await dom5process.wait()
        # todo: doesn't seem to be working, error still returns status 0
        if (retcode != 0):
            print ('{0} returned error code: {1}'.format(self.dom5sh, retcode))
            return None
        chkfilelist = list(savedgamedir.glob('*.chk'))
        #print (len(chkfilelist))
        turns = {}
        for chkfile in chkfilelist:
            chkfile = savedgamedir / chkfile
            print("checking: {0}".format(str(chkfile)))
            #chkfile = savedgamedir / "ftherlnd.chk"
            if (not chkfile.exists()):
                print ("{0} does not exist".format(chkfile))
            nation = chkfile.stem
            underscore = nation.find('_')
            if (underscore > -1):
                nation = nation[underscore+1:]
            print("reading {0}".format(nation))
            async with aiofiles.open(str(chkfile), mode='r') as f:
                contents = await f.read()
                turn_pattern = re.compile('turnnbr (\d+)')
                turn_match = turn_pattern.search(contents)
                # print(match.group(1))
                #print ('turn is {0}'.format(turn_match.group(1)))
                turns[nation] = int(turn_match.group(1))
        return turns
 
async def main():
    dom5Bot = Dom5Bot()
    print ('starting with token: {0}'.format(os.environ.get('DISCORD')))
    await asyncio.wait(
        {dom5Bot.start(os.environ.get('DISCORD'))},
        return_when=asyncio.FIRST_EXCEPTION)

if __name__ == '__main__':
    asyncio.run(main())
