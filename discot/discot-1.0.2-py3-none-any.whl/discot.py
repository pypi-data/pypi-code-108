import discord
import asyncio
import argparse
import inspect
import shlex
import sys
import urllib.parse
from random import randint
from os import getcwd
from os.path import basename

client = discord.Client()

async def resolve(obj):
    if inspect.iscoroutine(obj):
        return await obj
    elif isinstance(obj, list) and all(inspect.iscoroutine(e) for e in obj):
        return [await e for e in obj]
    else:
        return obj

def make_discot_decorator(deco):
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
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'for {get_help_prompt()}'))

onmessage_events = []
def onmessage(fun):
    onmessage_events.append(fun)
    return fun

special_parameters_raw = ['message', 'content']
def special_parameters(f):
    def message(message, namespace):
        return message

    def content(message, namespace):
        all_params = inspect.signature(f).parameters.values()
        pos = list(filter(lambda param: param.name not in special_parameters_raw and param.kind in [inspect._POSITIONAL_ONLY, inspect._POSITIONAL_OR_KEYWORD] and param.default == inspect._empty, all_params))
        if len(pos) > 0:
            return ' '.join(str(getattr(namespace, param.name)) for param in pos)
        else:
            return ' '.join(getattr(namespace, 'content_raw', []))

    return {k: v for k, v in locals().items() if k in inspect.signature(f).parameters}

def get_normal_parameters(f):
    return {k: v for k, v in inspect.signature(f).parameters.items() if k not in special_parameters_raw}

parser = None
def get_parser():
    global parser
    if parser is None:
        parser = argparse.ArgumentParser(prog=get_help_prompt())
        subcommands = parser.add_subparsers()
        for fun_name, (fun, fun_details, unpacker) in available_commands.items():
            subparser = subcommands.add_parser(fun_name, help=fun_details['description'])
            for param in get_normal_parameters(fun).values():
                kwargs = {}
                if param.default is not inspect._empty:
                    if param.default is False:
                        kwargs['action'] = 'store_true'
                    else:
                        kwargs['default'] = param.default
                        if param.kind is not inspect._KEYWORD_ONLY:
                            kwargs['nargs'] = '?'
                if param.annotation is not inspect._empty:
                    kwargs['type'] = param.annotation
                if param.kind is inspect._VAR_POSITIONAL:
                    kwargs['nargs'] = '+'
                subparser.add_argument(('--' if param.kind is inspect._KEYWORD_ONLY or (param.kind is inspect._POSITIONAL_OR_KEYWORD and param.default is not inspect._empty) else '') + param.name, **kwargs)
            if len([p for p in get_normal_parameters(fun).values() if p.default == inspect._empty]) == 0:
                subparser.add_argument('content_raw', nargs='*', default='')

            subparser.set_defaults(func=unpacker)
    return parser

@client.event
async def on_message(msg):
    [await resolve(onmessage_event(msg)) for onmessage_event in onmessage_events]
    if msg.author.bot or msg.content == '': return

    if msg.content == get_help_prompt():
        await msg.channel.send('\n'.join([cmd_name + (f' - {cmd_details["description"]}' if cmd_details["description"] else '') for cmd_name, (_cmd, cmd_details, _unp) in available_commands.items()]) if len(available_commands) > 0 else 'No commands found. Spooky...')
        return

    cmd_name = next((commandname for commandname in available_commands.keys() if msg.content.startswith(commandname)), None)
    if cmd_name is None: return
    fun, cmd_details, _unp = available_commands[cmd_name]

    allowed_users, allowed_servers, allowed_channels = cmd_details['users'], cmd_details['servers'], cmd_details['channels']
    fails_check = lambda value, matches: matches != any and not value in matches
    if fails_check(f'{msg.author.name}#{msg.author.discriminator}', allowed_users): return
    if msg.guild and fails_check(msg.guild.name, allowed_servers): return
    if (str(msg.channel.type) == 'private' and allowed_channels != any) or (str(msg.channel.type) != 'private' and fails_check(msg.channel.name, allowed_channels)): return

    try:
        parser = get_parser()
        urispace = urllib.parse.quote(' ')
        parsed = parser.parse_args(shlex.split(msg.content[0] + urllib.parse.quote(msg.content[1:]).replace(urispace, ' ')))
    except:
        await msg.channel.send('invalid call!')
    else:
        for arg, arg_val in vars(parsed).items():
            if isinstance(arg_val, str):
                setattr(parsed, arg, urllib.parse.unquote(arg_val))
            elif isinstance(arg_val, list) and len(arg_val) > 0 and isinstance(arg_val[0], str):
                setattr(parsed, arg, list(map(urllib.parse.unquote, arg_val)))
        for spec_name, spec_f in special_parameters(fun).items():
            setattr(parsed, spec_name, await resolve(spec_f(msg, parsed)))
        result = await resolve(parsed.func(parsed))
        if isinstance(result, str):
            await msg.channel.send(result)

######################################################

@make_discot_decorator
def command(*args, prefix = '!', description = "", user = any, users = any, server = any, servers = any, channel = any, channels = any):
    fun, *_ = args

    def construct_list(singular, plurar):
        result_list = plurar
        if singular != any: 
            result_list = [singular] if plurar == any else [singular, *plurar]
        return result_list

    fun_details = {
        'description': description,
        'users': construct_list(user, users), 
        'servers': construct_list(server, servers), 
        'channels': construct_list(channel, channels)
    }

    def unpacker(namespace):
        positionals = [getattr(namespace, param.name) for param in inspect.signature(fun).parameters.values() if param.kind in [inspect._POSITIONAL_ONLY, inspect._POSITIONAL_OR_KEYWORD]]
        var_positionals = next((getattr(namespace, param.name) for param in inspect.signature(fun).parameters.values() if param.kind is inspect._VAR_POSITIONAL), [])
        keywords = {param.name: getattr(namespace, param.name) for param in inspect.signature(fun).parameters.values() if param.kind is inspect._KEYWORD_ONLY}
        return fun(*positionals, *var_positionals, **keywords)
        
    available_commands[f'{prefix}{fun.__name__}'] = (fun, fun_details, unpacker)
    print(f"Added command {prefix}{fun.__name__}")
    return fun

@make_discot_decorator
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
    return fun

######################################################

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

def get_help_prompt():
    return f'?{basename(getcwd())}'

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
    print('Initializing...')
    client.run(token)