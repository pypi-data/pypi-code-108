import json
import uuid
import discord
import asyncio
from inspect import signature, Parameter, iscoroutine
from random import randint
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from aiohttp import web
from os import mkdir, getcwd
from os.path import join, exists

class any_available: pass

class State:
    def __init__(self, json_path):
        if not exists(json_path):
            json.dump({}, open(json_path, 'w'), indent = 4)
        self.__dict__['path'] = json_path
        self.__dict__['obj'] = json.load(open(self.path, 'r'))
        json.dump(self.obj, open(self.path, 'w'), indent = 4)
    
    def __getattr__(self, name):
        return self.obj[name] if name in self.obj else self.__getattribute__(name)

    def __setattr__(self, name, value):
        self.obj[name] = value
        json.dump(self.obj, open(self.path, 'w'), indent = 4)

state = State('state.info')

templates_dir = 'templates'
if not exists(templates_dir):
    mkdir(templates_dir)

help_prompt = f"?{getcwd().split('/')[-1]}"
client = discord.Client()

print('Initializing...')

_ = uuid.uuid1()

async def resolve(obj):
    if iscoroutine(obj):
        await obj
    elif isinstance(obj, list) and all(iscoroutine(e) for e in obj):
        [await e for e in obj]
    else:
        pass

class webhook_resolver(object):
    def __init__(self, schema):
        self.schema = schema
        self.aggregate = type('', (), {})()

    def test(self, obj):
        return self.adhers_to_schema(obj, self.schema)

    def adhers_to_schema(self, obj, schema_element):
        try:
            if schema_element != _:

                if isinstance(schema_element, list):
                    for a, b in zip(obj, schema_element):
                        if not self.adhers_to_schema(a, b):
                            return False

                elif isinstance(schema_element, dict):
                    for k, v in schema_element.items():
                        if not k in obj or not self.adhers_to_schema(obj[k], v):
                            return False
                        else:
                            self.aggregate.__dict__[k] = obj[k]

                else:
                    if obj != schema_element:
                        return False

            return True
        except KeyError as e:
            print("error:", e)
            return False

available_webhooks = []

async def find_webhook(request):
    body_encoded = await request.read()
    body = body_encoded.decode()
    shape = json.loads(body)

    for schema, fun in available_webhooks:
        resolver = webhook_resolver(schema)
        if resolver.test(shape):
            await resolve(fun(resolver.aggregate, body))
            with open(join(templates_dir, fun.__name__), 'w') as output_file:
                output_file.write(body)
            break

    return web.Response()

http_server = None

async def start_server():
    await web._run_app(http_server, port=5000)

def webhook(*, schema):
    global http_server
    if http_server == None:
        http_server = web.Application()
        http_server.add_routes([
            web.post('/', find_webhook)
        ])
        client.loop.create_task(start_server())

    def decorator(fun):
        available_webhooks.append((schema, fun))
    return decorator


def make_discord_interface_decorator(deco):
    def inner(f = None, **kwargs):
        if f != None and (kwargs != {} or not hasattr(f, '__call__') or not hasattr(f, '__name__') or f.__name__ == '<lambda>' or f.__name__ in globals()):
            raise TypeError("An interface decorator can only receive keyword arguments")
        return deco(f) if f else lambda lf: deco(lf, **kwargs)
    return inner

######################################################
available_commands = dict()

@client.event
async def on_ready():
    if len(available_commands) > 0:
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'for {help_prompt}'))

@make_discord_interface_decorator
def command(*args, prefix = '!', description = "", user = any_available, users = any_available, server = any_available, servers = any_available, channel = any_available, channels = any_available):
    fun, *_ = args

    def construct_list(singular, plurar):
        result_list = plurar
        if singular != any_available: 
            result_list = [singular] if plurar == any_available else [singular, *plurar]
        return result_list

    fun_details = {
        'description': description,
        'users': construct_list(user, users), 
        'servers': construct_list(server, servers), 
        'channels': construct_list(channel, channels)
    }
        
    available_commands[f'{prefix}{fun.__name__}'] = (fun, fun_details)
    print(f"Added command {prefix}{fun.__name__}")

onmessage_events = []
def onmessage(fun):
    onmessage_events.append(fun)

@client.event
async def on_message(msg):
    [await resolve(onmessage_event(msg)) for onmessage_event in onmessage_events]
    if msg.author.bot: return

    if msg.content == help_prompt:
        await msg.channel.send('\n'.join([cmd_name + (f' - {cmd_details["description"]}' if cmd_details["description"] else '') for cmd_name, (_cmd, cmd_details) in available_commands.items()]) if len(available_commands) > 0 else 'No commands found. Spooky...')
        return

    cmd_name, *args = list(filter(lambda s: s, msg.content.split(' ')))
    if cmd_name not in available_commands: return
    cmd, cmd_details = available_commands[cmd_name]

    allowed_users, allowed_servers, allowed_channels = cmd_details['users'], cmd_details['servers'], cmd_details['channels']
    fails_check = lambda value, matches: matches != any_available and not value in matches
    if fails_check(f'{msg.author.name}#{msg.author.discriminator}', allowed_users): return
    if msg.guild and fails_check(msg.guild.name, allowed_servers): return
    if (str(msg.channel.type) == 'private' and allowed_channels != any_available) or (str(msg.channel.type) != 'private' and fails_check(msg.channel.name, allowed_channels)): return

    fun_params = signature(cmd).parameters
    fun_param_names = [param_name for param_name in fun_params.keys() if  param_name != 'message']
    fun_params_default_count = len([param_name for param_name, param in fun_params.items() if param_name != 'message' and param.default != Parameter.empty])

    if (abs(len(fun_param_names) - len(args)) <= fun_params_default_count) or any(param.kind == Parameter.VAR_POSITIONAL for param in fun_params.values()):
        kwargs = {'message': msg} if 'message' in fun_params else {}
        reply = cmd(*args, **kwargs)
        if isinstance(reply, str):
            await msg.channel.send(reply)
        else:
            await resolve(reply)
    else:
        reply = f"Error, expected {len(fun_param_names)} arguments (got {len(args)})"
        if len(fun_param_names) > 0:
            reply += '\nExpected arguments: '
            reply += ', '.join([f'{arg_name}' + (f' (default: {fun_params.get(arg_name).default})' if fun_params.get(arg_name).default != Parameter.empty else '') for arg_name in fun_param_names])
        await msg.channel.send(reply)


######################################################

@make_discord_interface_decorator
def loop(*args, seconds = 0, minutes = 0, hours = 0, between = None):
    fun, *_ = args
    async def loop_task():
        await client.wait_until_ready()
        while not client.is_closed():
            await resolve(fun())
            sleep_time = randint(between[0], between[1]) if between else (seconds + minutes * 60 + hours * 60 * 60)
            await asyncio.sleep(sleep_time)
    client.loop.create_task(loop_task())
    print(f"Added task {fun.__name__}")

def ensure_channel(server_name, channel_name):
    try:
        server = next(guild for guild in client.guilds if guild.name == server_name)
        return next(channel for channel in server.channels if channel.name == channel_name)
    except:
        raise ValueError('Channel not found!')

def ensure_emoji(server_name, emoji_name):
    try:
        server = next(guild for guild in client.guilds if guild.name == server_name)
        return next(emoji for emoji in server.emojis if emoji.name == emoji_name)
    except:
        raise ValueError('Emoji not found!')

class colours:
    success = 2664261
    failure = 14431557
    calming = 31743
    
def make_embed(*, fields = [], **kwargs):
    embed = discord.Embed(**kwargs)
    for name, value in fields:
        embed.add_field(name = name, value = value, inline = False)
    return embed

def run(token):
    client.run(token)