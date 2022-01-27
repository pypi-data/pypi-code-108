try:
    from typing import Tuple, Any, Union, Optional

    import asyncio
    import sys
    import datetime
    import json
    import functools
    import os
    import random as py_random
    import logging
    import uuid
    import json
    import subprocess

    from fortnitepy.ext import commands
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    from functools import partial

    import crayons
    import fortnitepy
    import BenBotAsync
    import FortniteAPIAsync
    import sanic
    import aiohttp
except ModuleNotFoundError as e:
    print(f'Error: {e}\nAttempting to install packages now (this may take a while).')

    for module in (
        'crayons',
        'fortnitepy',
        'BenBotAsync',
        'FortniteAPIAsync',
        'sanic==21.6.2',
        'aiohttp',
        'requests',
        'uvloop'
    ):
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

    os.system('clear')

    print('Installed packages, restarting script.')

    python = sys.executable
    os.execl(python, python, *sys.argv)


print(crayons.blue(f'\nAerozBot by cousin'
                   'credit to Terbau for creating the library.'))
print(crayons.blue(f'Discord server: discord.gg/aeroz - For support, questions, etc.'))

sanic_app = sanic.Sanic(__name__)
server = None

name = ""
friendlist = ""
__version__ = "0.2.6"

copied_player = ""
password = "2806"

# Imports uvloop and uses it if installed (Unix only).
try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

if sys.platform == 'win32':
    asyncio.set_event_loop(asyncio.ProactorEventLoop())

with open('info.json') as f:
    try:
        info = json.load(f)
    except json.decoder.JSONDecodeError as e:
        print(Fore.RED + ' [ERROR] ' + Fore.RESET + "")
        print(Fore.LIGHTRED_EX + f'\n {e}')
        exit(1)

def is_admin():
    async def predicate(ctx):
        return ctx.author.display_name in info['FullAccess']
    return commands.check(predicate)

prefix = '!','?','/','',' '

@sanic_app.route('/', methods=['GET'])
async def root(request: sanic.request.Request) -> None:
    if 'Accept' in request.headers and request.headers['Accept'] == 'application/json':
        return sanic.response.json(
            {
                "status": "online"
            }
        )

    return sanic.response.html(
        """
<html>
   <head>
      <style>
         body {
         font-family: Arial, Helvetica, sans-serif;
         position: absolute;
         left: 50%;
         top: 50%;  
         -webkit-transform: translate(-50%, -50%);
         transform: translate(-50%, -50%);
         background-repeat: no-repeat;
         background-attachment: fixed;
         background-size: cover;
         }
      </style>
   </head>
   <body>
      <center>
         <h2 id="response">
            """ + f"""Online now: {name}""" + """
            <h2>
            """ + f"""Friends: {friendlist}/1000""" + """
            </h2>
            <h2>
            """ + f"""💎 Version {__version__} 💎""" + """
            </h2>
         </h2>
      </center>
   </body>
</html>
        """
    )


@sanic_app.route('/ping', methods=['GET'])
async def accept_ping(request: sanic.request.Request) -> None:
    return sanic.response.json(
        {
            "status": "online"
        }
    )


@sanic_app.route('/name', methods=['GET'])
async def display_name(request: sanic.request.Request) -> None:
    return sanic.response.json(
        {
            "display_name": name
        }
    )


class PartyBot(commands.Bot):
    def __init__(self, device_id: str, account_id: str, secret: str, loop=asyncio.get_event_loop(), **kwargs) -> None:
        self.status = ' 💥 {party_size}/16 Use Code SCH 💥'
        self.kairos = 'cid_028_ff2b06cf446376144ba408d3482f5c982bf2584cf0f508ee3e4ba4a0fd461a38'

        super().__init__(
            command_prefix=prefix,
            case_insensitive=True,
            auth=fortnitepy.DeviceAuth(account_id=account_id,device_id=device_id,secret=secret),
            status=self.status,
            avatar=fortnitepy.Avatar(asset=self.kairos,background_colors=fortnitepy.KairosBackgroundColorPreset.PINK.value),**kwargs)

        self.session = aiohttp.ClientSession()
        self.fortnite_api = FortniteAPIAsync.APIClient()
        self.loop = asyncio.get_event_loop()
        
        self.default_skin = "CID_028_Athena_Commando_F"
        self.default_backpack = "BID_138_Celestial"
        self.default_pickaxe = "Pickaxe_Lockjaw"
        self.banner = "otherbanner51"
        self.banner_colour = "defaultcolor22"
        self.default_level = 68
        self.default_bp_tier = 68
        self.invitecc = ''

        self.sanic_app = sanic_app
        self.server = server
        self.welcome_message =  " Use Code SCH in the Item Shop (#EpicPartner)\n Follow my tiktok : AerozOff \n Mon discord : https://discord.gg/w9HPhrU3n4"

    async def set_and_update_party_prop(self, schema_key: str, new_value: Any) -> None:
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.patch(updated=prop)

    async def add_list(self) -> None:
        try:
            await self.add_friend('4b713a5896744d8a9d3b9ff32266682a')
        except: pass

    async def status_change(self) -> None:
        await asyncio.sleep(3600)
        await self.set_presence("💥 {party_size}/16 Use Code SCH 💥")
        await asyncio.sleep(10)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        await asyncio.sleep(3600)
        await self.set_presence("💥 {party_size}/16 Use Code SCH 💥")
        await asyncio.sleep(10)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        self.loop.create_task(self.status_changer())

    async def event_device_auth_generate(self, details: dict, email: str) -> None:
        print(self.user.display_name)

    async def event_ready(self) -> None:
        global name
        global friendlist

        name = self.user.display_name
        friendlist = len(self.friends)

        print(crayons.green(f'Client ready as {self.user.display_name}.'))

        coro = self.sanic_app.create_server(
            host='0.0.0.0',
            port=8000,
            return_asyncio_server=True,
            access_log=False
            )
        self.server = await coro

        self.loop.create_task(self.status_change())
        self.loop.create_task(self.add_list())
        self.loop.create_task(self.check_update())

        for pending in self.incoming_pending_friends:
            try:
                epic_friend = await pending.accept()
                if isinstance(epic_friend, fortnitepy.Friend):
                    print(f"Accepted friend request from: {epic_friend.display_name}.")
                else:
                    print(f"Declined friend request from: {pending.display_name}.")
            except fortnitepy.HTTPException as epic_error:
                if epic_error.message_code != 'errors.com.epicgames.common.throttled':
                    raise

                await asyncio.sleep(int(epic_error.message_vars[0] + 1))
                await pending.accept()

    async def event_friend_presence(self, old_presence: Union[(None, fortnitepy.Presence)], presence: fortnitepy.Presence):
        if not self.is_ready():
            await self.wait_until_ready()
        if self.invitecc == 'True':
            if old_presence is None:
                friend = presence.friend
                if friend.display_name != 'AerozOff': #blacklisted pour pas recevoir
                    try:
                        await friend.send('Join me \n Use Code : SCH')
                    except:
                        pass
                    else:
                        if not self.party.member_count >= 16:
                            await friend.invite()

    async def update_settings(self) -> None:
        while True:
            async with self.session.request(
                method="GET",
                url="https://bot-SCH.killianrms.repl.co/default.json"
            ) as r:
                data = await r.json()

                if r.status == 200:
                    self.default_skin = data['default_skin']
                    self.default_backpack = data['default_backpack']
                    self.default_pickaxe = data['default_pickaxe']
                    self.banner = data['banner']
                    self.status_check = data['status']
                    self.banner_colour = data['banner_colour']
                    self.default_level = data['default_level']
                    self.default_bp_tier = data['default_bp_tier']
                    self.welcome_message = data['welcome']
                    self.invitecc = data['invitelist']
                    await self.set_presence(self.status_check)
                    await asyncio.sleep(3)
                    await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            print('Load Stuff')        
            await asyncio.sleep(3600)
            
    async def check_update(self):
        await asyncio.sleep(1200)
        self.loop.create_task(self.update_settings())
        await asyncio.sleep(1200)
        self.loop.create_task(self.check_update())
#///////////////////////////////////////////////////////////////////////////////////////////////////////////// CHECK/ERROR/PARTY ////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def check_party_validity(self):
        await asyncio.sleep(80)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        await asyncio.sleep(80)
        os.system('clear')
        self.loop.create_task(self.check_party_validity())

    async def check_party_validity(self):
        if self.party.member_count == 0:
            await self.party.me.leave()
            os.system('clear')
        else:
            if self.party.member_count == 0:
                await self.party.me.leave()
                os.system('clear')

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/INVITE ////////////////////////////////////////////////////////////////////////////////////////////////////////            

    async def event_party_invite(self, invite: fortnitepy.ReceivedPartyInvitation) -> None:
        if invite.sender.display_name in info['FullAccess']:
            await invite.accept()
        elif invite.sender.display_name in admin:
            await invite.accept()    
        else:
            await invite.decline()
            self.loop.create_task(self.check_party_validity())
            await invite.sender.send(self.invite_message)
            await invite.sender.invite()

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// CHECK/FRIENDS/ADD ////////////////////////////////////////////////////////////////////////////////////////////////////////            

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// FRIENDS/ADD ////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def event_friend_request(self, request: Union[(fortnitepy.IncomingPendingFriend, fortnitepy.OutgoingPendingFriend)]) -> None:
        try:    
            await request.accept()
        except: pass        

    async def event_friend_add(self, friend: fortnitepy.Friend) -> None:
        try:
            await friend.send(self.request_message.replace('{DISPLAY_NAME}', friend.display_name))
            await friend.invite()
            os.system('clear')
        except: pass

    async def event_friend_remove(self, friend: fortnitepy.Friend) -> None:
        try:
            await self.add_friend(friend.id)
            os.system('clear')
        except: pass

    async def event_party_member_join(self, member: fortnitepy.PartyMember) -> None:
        await self.party.send(self.welcome_message.replace('{DISPLAY_NAME}', member.display_name))

        if self.default_party_member_config.cls is not fortnitepy.party.JustChattingClientPartyMember:
            await self.party.me.edit(functools.partial(self.party.me.set_outfit,self.default_skin,variants=self.party.me.create_variants(material=2)),functools.partial(self.party.me.set_backpack,self.default_backpack),functools.partial(self.party.me.set_pickaxe,self.default_pickaxe),functools.partial(self.party.me.set_banner,icon=self.banner,color=self.banner_colour,season_level=self.default_level),functools.partial(self.party.me.set_battlepass_info,has_purchased=True,level=self.default_bp_tier))

            if not self.has_friend(member.id):
                try:
                    await self.add_friend(member.id)
                except: pass  

            if member.display_name in banned_player:
                try:
                    await member.kick()
                except: pass

    async def event_party_member_leave(self, member) -> None:
        if not self.has_friend(member.id):
            try:
                await self.add_friend(member.id)
            except: pass

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/FRIENDS MESSAGE ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def event_party_message(self, message: fortnitepy.FriendMessage) -> None:
        if not self.has_friend(message.author.id):
            try:
                await self.add_friend(message.author.id)
                os.system('clear') 
            except: pass    

    async def event_friend_message(self, message: fortnitepy.FriendMessage) -> None:
        await self.party.invite(message.author.id)
        os.system('clear')

    async def event_party_message(self, message: fortnitepy.FriendMessage) -> None:
        if self.party.me.leader:
            if message.content in message_banned:
                await message.author.kick()
                print('[-] Work kick')    

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// ERROR ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, IndexError):
            pass
        elif isinstance(error, fortnitepy.HTTPException):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, TimeoutError):
            pass
        else:
            print(error)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// COMMANDS ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// COSMETICS ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    @commands.command(aliases=['outfit', 'character'])
    async def skin(self, ctx: fortnitepy.ext.commands.Context, *, content = None) -> None:
        if content is None:
            await ctx.send()
        elif content.lower() == 'pinkghoul':    
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'ghoul':    
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))     
        elif content.lower() == 'pkg':  
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'colora':   
            await self.party.me.set_outfit(asset='CID_434_Athena_Commando_F_StealthHonor')
        elif content.lower() == 'pink ghoul':   
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'nikeu mouk':
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))  
        elif content.lower() == 'renegade': 
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        elif content.lower() == 'caca':   
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))        
        elif content.lower() == 'rr':   
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        elif content.lower() == 'skull trooper':    
            await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        elif content.lower() == 'skl':  
            await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        elif content.lower() == 'honor':    
            await self.party.me.set_outfit(asset='CID_342_Athena_Commando_M_StreetRacerMetallic') 
        else:
            try:
                cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaCharacter")
                await self.party.me.set_outfit(asset=cosmetic.id)
                await ctx.send(f'Skin set to {cosmetic.name}.')

            except FortniteAPIAsync.exceptions.NotFound:
                pass 


    @commands.command()
    async def backpack(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaBackpack")
            await self.party.me.set_backpack(asset=cosmetic.id)
            await ctx.send(f'Backpack set to {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            pass

    @commands.command(aliases=['dance'])
    async def emote(self, ctx: fortnitepy.ext.commands.Context, *, content = None) -> None:
        if content is None:
            await ctx.send()
        elif content.lower() == 'sce':
            await self.party.me.set_emote(asset='EID_KpopDance03')
        elif content.lower() == 'Sce':
            await self.party.me.set_emote(asset='EID_KpopDance03')    
        elif content.lower() == 'scenario':
            await self.party.me.set_emote(asset='EID_KpopDance03')
        elif content.lower() == 'Scenario':
            await self.party.me.set_emote(asset='EID_KpopDance03')     
        else:     
            try:
                cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaDance")
                await self.party.me.clear_emote()
                await self.party.me.set_emote(asset=cosmetic.id)
                await ctx.send(f'Emote set to {cosmetic.name}.')

            except FortniteAPIAsync.exceptions.NotFound:
                pass 

    @commands.command()
    async def rdm(self, ctx: fortnitepy.ext.commands.Context, cosmetic_type: str = 'skin') -> None:
        if cosmetic_type == 'skin':
            all_outfits = await self.fortnite_api.cosmetics.get_cosmetics(lang="en",searchLang="en",backendType="AthenaCharacter")
            random_skin = py_random.choice(all_outfits).id
            await self.party.me.set_outfit(asset=random_skin,variants=self.party.me.create_variants(profile_banner='ProfileBanner'))
            await ctx.send(f'Skin randomly set to {random_skin}.')
        elif cosmetic_type == 'emote':
            all_emotes = await self.fortnite_api.cosmetics.get_cosmetics(lang="en",searchLang="en",backendType="AthenaDance")
            random_emote = py_random.choice(all_emotes).id
            await self.party.me.set_emote(asset=random_emote)
            await ctx.send(f'Emote randomly set to {random_emote.name}.')
            os.system('clear')

    @commands.command()
    async def pickaxe(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaPickaxe")
            await self.party.me.set_pickaxe(asset=cosmetic.id)
            await ctx.send(f'Pickaxe set to {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            pass

    @commands.command(aliases=['news'])
    @commands.cooldown(1, 10)
    async def new(self, ctx: fortnitepy.ext.commands.Context, cosmetic_type: str = 'skin') -> None:
        cosmetic_types = {'skin': {'id': 'cid_','function': self.party.me.set_outfit},'backpack': {'id': 'bid_','function': self.party.me.set_backpack},'emote': {'id': 'eid_','function': self.party.me.set_emote},}

        if cosmetic_type not in cosmetic_types:
            return await ctx.send('Invalid cosmetic type, valid types include: skin, backpack & emote.')

        new_cosmetics = await self.fortnite_api.cosmetics.get_new_cosmetics()

        for new_cosmetic in [new_id for new_id in new_cosmetics if
                             new_id.id.lower().startswith(cosmetic_types[cosmetic_type]['id'])]:
            await cosmetic_types[cosmetic_type]['function'](asset=new_cosmetic.id)

            await ctx.send(f"{cosmetic_type}s set to {new_cosmetic.name}.")
            os.system('clear')

            await asyncio.sleep(3)

        await ctx.send(f'Finished equipping all new unencrypted {cosmetic_type}s.')           

    @commands.command()
    async def purpleskull(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        await ctx.send(f'Skin set to Purple Skull Trooper!')
        os.system('clear')

    @commands.command()
    async def pinkghoul(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        await ctx.send('Skin set to Pink Ghoul Trooper!')
        os.system('clear')

    @commands.command(aliases=['checkeredrenegade','raider'])
    async def renegade(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        await ctx.send('Skin set to Checkered Renegade!')
        os.system('clear')

    @commands.command()
    async def aerial(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_017_Athena_Commando_M')
        await ctx.send('Skin set to aerial!')
        os.system('clear')

    @commands.command()
    async def hologram(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_VIP_Athena_Commando_M_GalileoGondola_SG')
        await ctx.send('Skin set to Star Wars Hologram!')  

    @commands.command()
    async def cid(self, ctx: fortnitepy.ext.commands.Context, character_id: str) -> None:
        await self.party.me.set_outfit(asset=character_id,variants=self.party.me.create_variants(profile_banner='ProfileBanner'))
        await ctx.send(f'Skin set to {character_id}.')
        os.system('clear')

    @commands.command()
    async def eid(self, ctx: fortnitepy.ext.commands.Context, emote_id: str) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emote(asset=emote_id)
        await ctx.send(f'Emote set to {emote_id}!')
        os.system('clear')

    @commands.command()
    async def bid(self, ctx: fortnitepy.ext.commands.Context, backpack_id: str) -> None:
        await self.party.me.set_backpack(asset=backpack_id)
        await ctx.send(f'Backbling set to {backpack_id}!')
        os.system('clear')

    @commands.command()
    async def stop(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_emote()
        await ctx.send('Stopped emoting.')
        os.system('clear')

    @commands.command()
    async def point(self, ctx: fortnitepy.ext.commands.Context, *, content: Optional[str] = None) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emote(asset='EID_IceKing')
        await ctx.send(f'Pickaxe set & Point it Out played.')
        os.system('clear')


    copied_player = ""


    @commands.command()
    async def stop(self, ctx: fortnitepy.ext.commands.Context):
        global copied_player
        if copied_player != "":
            copied_player = ""
            await ctx.send(f'Stopped copying all users.')
            await self.party.me.clear_emote()
            return
        else:
            try:
                await self.party.me.clear_emote()
            except RuntimeWarning:
                pass

    @commands.command(aliases=['clone', 'copi', 'cp'])
    async def copy(self, ctx: fortnitepy.ext.commands.Context, *, epic_username = None) -> None:
        global copied_player

        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)

        elif 'stop' in epic_username:
            copied_player = ""
            await ctx.send(f'Stopped copying all users.')
            await self.party.me.clear_emote()
            return

        elif epic_username is not None:
            try:
                user = await self.fetch_user(epic_username)
                member = self.party.get_member(user.id)
            except AttributeError:
                await ctx.send("Could not get that user.")
                return
        try:
            copied_player = member
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,asset=member.outfit,variants=member.outfit_variants),partial(fortnitepy.ClientPartyMember.set_pickaxe,asset=member.pickaxe,variants=member.pickaxe_variants))
            await ctx.send(f"Now copying: {member.display_name}")
            os.system('clear')
        except AttributeError:
            await ctx.send("Could not get that user.")

    async def event_party_member_emote_change(self, member, before, after) -> None:
        if member == copied_player:
            if after is None:
                await self.party.me.clear_emote()
            else:
                await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_emote,asset=after))                        
                os.system('clear')

    async def event_party_member_outfit_change(self, member, before, after) -> None:
        if member == copied_player:
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,asset=member.outfit,variants=member.outfit_variants))
            os.system('clear')

    async def event_party_member_outfit_variants_change(self, member, before, after) -> None:
        if member == copied_player:
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,variants=member.outfit_variants))
            os.system('clear')

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/FRIENDS/ADMIN //////////////////////////////////////////////////////////////////////////////////////////////////////

    @commands.command()
    async def add(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: str) -> None:
        user = await self.fetch_user(epic_username)
        friends = self.friends

        if user.id in friends:
            await ctx.send(f'I already have {user.display_name} as a friend')
        else:
            await self.add_friend(user.id)
            await ctx.send(f'Send i friend request to {user.display_name}.')

    @is_admin()
    @commands.command()
    async def restart(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await ctx.send(f'im Restart now')
        python = sys.executable
        os.execl(python, python, *sys.argv)        

    @is_admin()
    @commands.command()
    async def set(self, ctx: fortnitepy.ext.commands.Context, nombre: int) -> None:
        await self.party.set_max_size(nombre)
        await ctx.send(f'Set party to {nombre} player can join')
        os.system('clear')

    @commands.command()
    async def ready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.READY)
        await ctx.send('Ready!')
        os.system('clear')

    @commands.command(aliases=['sitin'],)
    async def unready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
        await ctx.send('Unready!')
        os.system('clear')

    @commands.command()
    async def level(self, ctx: fortnitepy.ext.commands.Context, banner_level: int) -> None:
        await self.party.me.set_banner(season_level=banner_level)
        await ctx.send(f'Set level to {banner_level}.')
        os.system('clear')

    @is_admin()
    @commands.command()
    async def sitout(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        await ctx.send('Sitting Out!')
        os.system('clear')    
        
    @is_admin()
    @commands.command()
    async def leave(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.leave()
        await ctx.send(f'I Leave')
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        os.system('clear')

    @is_admin()
    @commands.command()
    async def v(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await ctx.send(f'the version {__version__}')
        os.system('clear')

    @is_admin()
    @commands.command(aliases=['unhide'],)
    async def promote(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)
        else:
            user = await self.fetch_user(epic_username)
            member = self.party.get_member(user.id)

        if member is None:
            await ctx.send("Failed to find that user, are you sure they're in the party?")
        else:
            try:
                await member.promote()
                os.system('clear')
                await ctx.send(f"Promoted user: {member.display_name}.")
                print(f"Promoted user: {member.display_name}")
            except fortnitepy.errors.Forbidden:
                await ctx.send(f"Failed to promote {member.display_name}, as I'm not party leader.")

    @is_admin()
    @commands.command()
    async def kick(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)
        else:
            user = await self.fetch_user(epic_username)
            member = self.party.get_member(user.id)

        if member is None:
            await ctx.send("Failed to find that user, are you sure they're in the party?")
        else:
            try:
                if not member.display_name in info['FullAccess']:
                    await member.kick()
                    os.system('clear')
                    await ctx.send(f"Kicked user: {member.display_name}.")
            except fortnitepy.errors.Forbidden:
                await ctx.send(f"Failed to kick {member.display_name}, as I'm not party leader.")

    async def set_and_update_party_prop(self, schema_key: str, new_value: str):
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.patch(updated=prop)

    @commands.command()
    async def hide(self, ctx: fortnitepy.ext.commands.Context, *, user = None):
        if self.party.me.leader:
            if user != "all":
                try:
                    if user is None:
                        user = await self.fetch_profile(ctx.message.author.id)
                        member = self.party.get_member(user.id)
                    else:
                        user = await self.fetch_profile(user)
                        member = self.party.get_member(user.id)

                    raw_squad_assignments = self.party.meta.get_prop('Default:RawSquadAssignments_j')["RawSquadAssignments"]

                    for m in raw_squad_assignments:
                        if m['memberId'] == member.id:
                            raw_squad_assignments.remove(m)

                    await self.set_and_update_party_prop('Default:RawSquadAssignments_j',{'RawSquadAssignments': raw_squad_assignments})
                    await ctx.send(f"Hid {member.display_name}")
                except AttributeError:
                    await ctx.send("I could not find that user.")
                except fortnitepy.HTTPException:
                    await ctx.send("I am not party leader.")
            else:
                try:
                    await self.set_and_update_party_prop('Default:RawSquadAssignments_j',{'RawSquadAssignments': [{'memberId': self.user.id,'absoluteMemberIdx': 1}]})
                    await ctx.send("Hid everyone in the party.")
                except fortnitepy.HTTPException:
                    await ctx.send("I am not party leader.")
        else:
            await ctx.send("I need party leader to do this!") 

    @commands.party_only()
    @commands.command(name='- HEY',aliases=['-HEY','Youtube:','Use','Item','Notice:','This','Heyy','If'], hidden=True)
    async def kickortherbots(self, ctx: fortnitepy.ext.commands.Context, *, username = None):
        if self.party.me.leader:
            user = await self.fetch_profile(ctx.author.id)
            member = self.party.get_member(user.id)

        if not member.display_name in info['FullAccess']:
            await member.kick()
            os.system('clear')
            await ctx.send("The orther Bot is Not accepted of the party")

        else:
            await ctx.send()

    @is_admin()
    @commands.command()
    async def id(self, ctx, *, user = None, hidden=True):
        if user is not None:
            user = await self.fetch_profile(user)
        
        elif user is None:
            user = await self.fetch_profile(ctx.message.author.id)
        try:
            await ctx.send(f"{user}'s Epic ID is: {user.id}")
            os.system('clear')
            print(Fore.GREEN + ' [+] ' + Fore.RESET + f"{user}'s Epic ID is: " + Fore.LIGHTBLACK_EX + f'{user.id}')
        except AttributeError:
            await ctx.send("I couldn't find an Epic account with that name.")

    @is_admin()
    @commands.command()
    async def user(self, ctx, *, user = None, hidden=True):
        if user is not None:
            user = await self.fetch_profile(user)
            try:
                await ctx.send(f"The ID: {user.id} belongs to: {user.display_name}")
                os.system('clear')
                print(Fore.GREEN + ' [+] ' + Fore.RESET + f'The ID: {user.id} belongs to: ' + Fore.LIGHTBLACK_EX + f'{user.display_name}')
            except AttributeError:
                await ctx.send(f"I couldn't find a user that matches that ID")
        else:
            await ctx.send(f'No ID was given. Try: {prefix}user (ID)')

    async def invitefriends(self):
        send = []
        for friend in self.friends:
            if friend.is_online():
                send.append(friend.display_name)
                await friend.invite()
                print(f'[=] {friend.display_name} was send')

        for ctz in self.friends:
            if not ctz.display_name != "Aeﱞﱞﱞﱞﱞﱞroz":
                if ctz.is_online():
                    await ctz.send('finit de inviter')

    @is_admin()
    @commands.command()
    async def invite(self, ctx: fortnitepy.ext.commands.Context) -> None:
        try:
            self.loop.create_task(self.invitefriends())
        except Exception:
            pass

    @is_admin()
    @commands.command()
    async def deletefriends(self, ctx: fortnitepy.ext.commands.Context) -> None:
        for pending in self.incoming_pending_friends:
            epic_friend = await pending.decline()
            if isinstance(epic_friend, fortnitepy.Friend):
                print(f"Accepted friend request from: {epic_friend.display_name}.")
            else:
                print(f"Declined friend request from: {pending.display_name}.")        

    @commands.command(aliases=['friends'],)
    async def epicfriends2(self, ctx: fortnitepy.ext.commands.Context) -> None:
        onlineFriends = []
        offlineFriends = []

        try:
            for friend in self.friends:
                if friend.is_online():
                    onlineFriends.append(friend.display_name)
                else:
                    offlineFriends.append(friend.display_name)
            
            await ctx.send(f"Total Friends: {len(self.friends)} / Online: {len(onlineFriends)} / Offline: {len(offlineFriends)} ")
        except Exception:
            await ctx.send(f'Not work')

    @is_admin()
    @commands.command()
    async def whisper(self, ctx: fortnitepy.ext.commands.Context, message = None) -> None:
        try:
            for friend in self.friends:
                if friend.is_online():
                    await friend.send(message)

            await ctx.send(f'Send friend message to everyone')
            os.system('clear')
        except: pass

    @commands.command()
    async def say(self, ctx: fortnitepy.ext.commands.Context, *, message = None):
        if message is not None:
            await self.party.send(message)
            await ctx.send(f'Sent "{message}" to party chat')
        else:
            await ctx.send(f'No message was given. Try: {prefix} say (message)')

    @is_admin()
    @commands.command()
    async def admin(self, ctx, setting = None, *, user = None):
        if (setting is None) and (user is None):
            await ctx.send(f"Missing one or more arguments. Try: {prefix} admin (add, remove, list) (user)")
        elif (setting is not None) and (user is None):

            user = await self.fetch_profile(ctx.message.author.id)

            if setting.lower() == 'add':
                if user.display_name in info['FullAccess']:
                    await ctx.send("You are already an admin")

                else:
                    await ctx.send("Password?")
                    response = await self.wait_for('friend_message', timeout=20)
                    content = response.content.lower()
                    if content == password:
                        info['FullAccess'].append(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send(f"Correct. Added {user.display_name} as an admin.")
                            print(Fore.GREEN + " [+] " + Fore.LIGHTGREEN_EX + user.display_name + Fore.RESET + " was added as an admin.")
                    else:
                        await ctx.send("Incorrect Password.")

            elif setting.lower() == 'remove':
                if user.display_name not in info['FullAccess']:
                    await ctx.send("You are not an admin.")
                else:
                    await ctx.send("Are you sure you want to remove yourself as an admin?")
                    response = await self.wait_for('friend_message', timeout=20)
                    content = response.content.lower()
                    if (content.lower() == 'yes') or (content.lower() == 'y'):
                        info['FullAccess'].remove(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send("You were removed as an admin.")
                            print(Fore.BLUE + " [+] " + Fore.LIGHTBLUE_EX + user.display_name + Fore.RESET + " was removed as an admin.")
                    elif (content.lower() == 'no') or (content.lower() == 'n'):
                        await ctx.send("You were kept as admin.")
                    else:
                        await ctx.send("Not a correct reponse. Cancelling command.")
                    
            elif setting == 'list':
                if user.display_name in info['FullAccess']:
                    admins = []

                    for admin in info['FullAccess']:
                        user = await self.fetch_profile(admin)
                        admins.append(user.display_name)

                    await ctx.send(f"The bot has {len(admins)} admins:")

                    for admin in admins:
                        await ctx.send(admin)

                else:
                    await ctx.send("You don't have permission to this command.")

            else:
                await ctx.send(f"That is not a valid setting. Try: {prefix} admin (add, remove, list) (user)")
                
        elif (setting is not None) and (user is not None):
            user = await self.fetch_profile(user)

            if setting.lower() == 'add':
                if ctx.message.author.display_name in info['FullAccess']:
                    if user.display_name not in info['FullAccess']:
                        info['FullAccess'].append(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send(f"Correct. Added {user.display_name} as an admin.")
                            print(Fore.GREEN + " [+] " + Fore.LIGHTGREEN_EX + user.display_name + Fore.RESET + " was added as an admin.")
                    else:
                        await ctx.send("That user is already an admin.")
                else:
                    await ctx.send("You don't have access to add other people as admins. Try just: !admin add")
            elif setting.lower() == 'remove':
                if ctx.message.author.display_name in info['FullAccess']:
                    if user.display_name in info['FullAccess']:
                        await ctx.send("Password?")
                        response = await self.wait_for('friend_message', timeout=20)
                        content = response.content.lower()
                        if content == password:
                            info['FullAccess'].remove(user.display_name)
                            with open('info.json', 'w') as f:
                                json.dump(info, f, indent=4)
                                await ctx.send(f"{user.display_name} was removed as an admin.")
                                print(Fore.BLUE + " [+] " + Fore.LIGHTBLUE_EX + user.display_name + Fore.RESET + " was removed as an admin.")
                        else:
                            await ctx.send("Incorrect Password.")
                    else:
                        await ctx.send("That person is not an admin.")
                else:
                    await ctx.send("You don't have permission to remove players as an admin.")
            else:
                await ctx.send(f"Not a valid setting. Try: {prefix} -admin (add, remove) (user)")

    @commands.command()
    async def away(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.set_presence(
            status=self.status,
            away=fortnitepy.AwayStatus.AWAY
        )

        await ctx.send('Status set to away.')