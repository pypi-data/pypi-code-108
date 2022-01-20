# Cog Stuff
from discord.ext import commands
from discord.embeds import Embed
from discord.colour import Color

# AA Contexts
from aadiscordbot.app_settings import get_site_url
from allianceauth.services.modules.discord.models import DiscordUser

# OPCALENDAR
import operator
from opcalendar.models import Event, IngameEvents, EventHost
from django.db.models import Q, F
from itertools import chain
from app_utils.urls import static_file_absolute_url
from datetime import datetime
import os

import logging

from opcalendar.app_settings import (
    OPCALENDAR_DISCORD_OPS_DISPLAY_EXTERNAL,
)

logger = logging.getLogger(__name__)

# i dont want to do this, but the below object get wont work without it, investigate.
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class Ops(commands.Cog):
    """
    A Collection of Authentication Tools for Alliance Auth
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ops(self, ctx):
        """
        Sends a direct message about the upcoming events visible for the user
        """
        await ctx.trigger_typing()

        # Get authod ID
        id = ctx.message.author.id

        url = get_site_url()

        today = datetime.today()

        user_argument = ctx.message.content[5:]

        if not user_argument:
            host = "all hosts"

        else:
            host = user_argument

        # Get user if discord service is active
        try:
            discord_user = DiscordUser.objects.get(uid=id)

            user = discord_user.user

            discord_active = True

        except Exception:
            logger.error("Discord service is not active for user")

            embed = Embed(title="Command failed")
            embed.colour = Color.red()
            embed.set_thumbnail(
                url=static_file_absolute_url("opcalendar/terminate.png")
            )
            embed.description = "Activate the [discord service]({}/services) to access this command.".format(
                url
            )
            discord_active = False

            await ctx.reply(embed=embed)

        if discord_active:
            # Get normal events
            # Filter by groups and states
            events = (
                Event.objects.filter(
                    Q(event_visibility__restricted_to_group__in=user.groups.all())
                    | Q(event_visibility__restricted_to_group__isnull=True),
                )
                .filter(
                    Q(event_visibility__restricted_to_state=user.profile.state)
                    | Q(event_visibility__restricted_to_state__isnull=True),
                )
                .filter(start_time__gte=today)
            )
            if user_argument:
                events = events.filter(host__community=host)

            # Get ingame events
            # Filter by groups and states
            ingame_events = (
                IngameEvents.objects.annotate(
                    start_time=F("event_start_date"),
                    end_time=F("event_end_date"),
                )
                .filter(
                    Q(
                        owner__event_visibility__restricted_to_group__in=user.groups.all()
                    )
                    | Q(owner__event_visibility__restricted_to_group__isnull=True),
                )
                .filter(
                    Q(owner__event_visibility__restricted_to_state=user.profile.state)
                    | Q(owner__event_visibility__restricted_to_state__isnull=True),
                )
                .filter(start_time__gte=today)
            )

            hosts = EventHost.objects.all()

            if not OPCALENDAR_DISCORD_OPS_DISPLAY_EXTERNAL:
                hosts = hosts.filter(external=False)

            hosts = _hosts(hosts)

            if user_argument:
                ingame_events = ingame_events.filter(host__community=host)

            # Combine events, limit to 20 events
            all_events = sorted(
                chain(events, ingame_events),
                key=operator.attrgetter("start_time"),
            )[:20]

            embed = Embed(title="Scheduled Opcalendar Events")

            embed.set_thumbnail(url=static_file_absolute_url("opcalendar/calendar.png"))

            embed.colour = Color.blue()

            embed.description = "List view of the next 20 upcoming operations for {}. A calendar view is located in [here]({}/opcalendar).\n\nFiltering: To filter events for a specific host add the name after the command ie. `!ops my coalition`\n\nAvailable hosts: *{}*".format(
                host, url, hosts
            )

            # Format all events and ingame events
            for event in all_events:
                if type(event) == Event:
                    embed.add_field(
                        name="Event: {0} {1}".format(
                            event.title, event.operation_type.ticker
                        ),
                        value="Host: {0}\nFC: {1}\nDoctrine: {2}\nLocation: {3}\nTime: {4}\n[Details]({5}/opcalendar/event/{6}/details/)\n".format(
                            event.host,
                            event.fc,
                            event.doctrine,
                            event.formup_system,
                            event.start_time,
                            url,
                            event.id,
                        ),
                        inline=False,
                    )
                if type(event) == IngameEvents:
                    embed.add_field(
                        name="Ingame Event: {0}".format(event.title),
                        value="Host: {0}\n Time:{1}\n[Details]({2}/opcalendar/ingame/event/{3}/details/)".format(
                            event.owner_name,
                            event.start_time,
                            url,
                            event.event_id,
                        ),
                        inline=False,
                    )

            await ctx.author.send(embed=embed)

            embed = Embed(title="Events sent")
            embed.colour = Color.green()
            embed.description = (
                "I have sent you a direct message about upcoming events."
            )
            discord_active = False

            await ctx.reply(embed=embed)


def _hosts(hosts):
    hosts = [x.community for x in hosts]

    if hosts:
        return ", ".join(hosts)
    else:
        return None


def setup(bot):
    bot.add_cog(Ops(bot))
