"""
    twtxt.cli
    ~~~~~~~~~
    This module implements the command-line interface of twtxt.
    :copyright: (c) 2016 by buckket.
    :license: MIT, see LICENSE for more details.
"""

import logging
import os
import sys
import textwrap

import click

from twtxt.cache import Cache
from twtxt.config import Config
from twtxt.helper import run_pre_tweet_hook, run_post_tweet_hook
from twtxt.helper import sort_and_truncate_tweets
from twtxt.helper import style_timeline, style_source, style_source_with_status
from twtxt.helper import validate_created_at, validate_text
from twtxt.helper import get_new_tweets
from twtxt.log import init_logging
from twtxt.mentions import expand_mentions
from twtxt.models import Tweet, Source
from twtxt.twfile import get_local_tweets, add_local_tweet
from twtxt.twhttp import get_remote_tweets, get_remote_status

logger = logging.getLogger(__name__)


@click.group()
@click.option("--config", "-c",
              type=click.Path(exists=True, file_okay=True, readable=True, writable=True, resolve_path=True),
              help="Specify a custom config file location.")
@click.option("--verbose", "-v",
              is_flag=True, default=False,
              help="Enable verbose output for debugging purposes.")
@click.version_option()
@click.pass_context
def cli(ctx, config, verbose):
    """Decentralised, minimalist microblogging service for hackers."""
    init_logging(debug=verbose)

    if ctx.invoked_subcommand == "quickstart":
        return

    try:
        if config:
            conf = Config.from_file(config)
        else:
            conf = Config.discover()
    except ValueError:
        click.echo("✗ Config file not found or not readable. You may want to run twtxt quickstart.")
        sys.exit()

    ctx.default_map = conf.build_default_map()
    ctx.obj = {'conf': conf}


@cli.command()
@click.option("--created-at",
              callback=validate_created_at,
              help="ISO 8601 formatted datetime string to use in Tweet, instead of current time.")
@click.option("--twtfile", "-f",
              type=click.Path(file_okay=True, writable=True, resolve_path=True),
              help="Location of your twtxt file. (Default: twtxt.txt)")
@click.argument("text", callback=validate_text, nargs=-1)
@click.pass_context
def tweet(ctx, created_at, twtfile, text):
    """Append a new tweet to your twtxt file."""
    text = expand_mentions(text)
    tweet = Tweet(text, created_at) if created_at else Tweet(text)

    pre_tweet_hook = ctx.obj["conf"].pre_tweet_hook
    if pre_tweet_hook:
        if not run_pre_tweet_hook(pre_tweet_hook, ctx.obj["conf"].options):
            click.echo("✗ pre_tweet_hook returned non-zero")
            raise click.Abort

    if not add_local_tweet(tweet, twtfile):
        click.echo("✗ Couldn’t write to file.")
    else:
        post_tweet_hook = ctx.obj["conf"].post_tweet_hook
        if post_tweet_hook:
            if not run_post_tweet_hook(post_tweet_hook, ctx.obj["conf"].options):
                click.echo("✗ post_tweet_hook returned non-zero")


@cli.command()
@click.option("--pager/--no-pager",
              is_flag=True,
              help="Use a pager to display content. (Default: False)")
@click.option("--limit", "-l",
              type=click.INT,
              help="Limit total number of shown tweets. (Default: 20)")
@click.option("--twtfile", "-f",
              type=click.Path(exists=True, file_okay=True, readable=True, resolve_path=True),
              help="Location of your twtxt file. (Default: twtxt.txt")
@click.option("--ascending", "sorting", flag_value="ascending",
              help="Sort timeline in ascending order.")
@click.option("--descending", "sorting", flag_value="descending",
              help="Sort timeline in descending order. (Default)")
@click.option("--timeout", type=click.FLOAT,
              help="Maximum time requests are allowed to take. (Default: 5.0)")
@click.option("--porcelain", is_flag=True,
              help="Style output in an easy-to-parse format. (Default: False)")
@click.option("--source", "-s",
              help="Only show feed of the given source. (Can be nick or URL)")
@click.option("--cache/--no-cache",
              is_flag=True,
              help="Cache remote twtxt files locally. (Default: True)")
# comp490 -begin
@click.option("--newtweets", "-nt",
              is_flag=True,
              help="Only shows tweets that have not been viewed yet.")
# comp490 -end
@click.pass_context
def timeline(ctx, pager, limit, twtfile, sorting, timeout, porcelain, source, cache, newtweets):
    """Retrieve your personal timeline."""
    if source:
        source_obj = ctx.obj["conf"].get_source_by_nick(source)
        if not source_obj:
            logger.debug("Not following {0}, trying as URL".format(source))
            source_obj = Source(source, source)
        sources = [source_obj]
    else:
        sources = ctx.obj["conf"].following

    tweets = get_remote_tweets(sources, limit, timeout, cache)

    if twtfile and not source:
        source = Source(ctx.obj["conf"].nick, ctx.obj["conf"].twturl, file=twtfile)
        tweets.extend(get_local_tweets(source, limit))

    tweets = sort_and_truncate_tweets(tweets, sorting, limit)

    if not tweets:
        return

    if pager:
        click.echo_via_pager(style_timeline(tweets, porcelain))
        updateLastViewed = ctx.obj["conf"].update_last_viewed()
    # comp490 begin
    elif newtweets:
        lastViewed = ctx.obj["conf"].get_last_viewed()
        tweets = get_new_tweets(tweets, lastViewed)
        click.echo(tweets)
        ctx.obj["conf"].update_last_viewed()
    # comp490 end
    else:
        click.echo(style_timeline(tweets, porcelain))
        updateLastViewed = ctx.obj["conf"].update_last_viewed()


@cli.command()
@click.option("--pager/--no-pager",
              is_flag=True,
              help="Use a pager to display content. (Default: False)")
@click.option("--limit", "-l",
              type=click.INT,
              help="Limit total number of shown tweets. (Default: 20)")
@click.option("--ascending", "sorting", flag_value="ascending",
              help="Sort timeline in ascending order.")
@click.option("--descending", "sorting", flag_value="descending",
              help="Sort timeline in descending order. (Default)")
@click.option("--timeout", type=click.FLOAT,
              help="Maximum time requests are allowed to take. (Default: 5.0)")
@click.option("--porcelain", is_flag=True,
              help="Style output in an easy-to-parse format. (Default: False)")
@click.option("--cache/--no-cache",
              is_flag=True,
              help="Cache remote twtxt files locally. (Default: True)")
# comp490 -begin
# @click.option("--new", "-n",
#              help="Only shows tweets that have not been viewed yet.")
# comp490 -end
@click.argument("source")
@click.pass_context
def view(ctx, **kwargs):
    """Show feed of given source."""
    ctx.forward(timeline)


@cli.command()
@click.option("--check/--no-check",
              is_flag=True,
              help="Check if source URL is valid and readable. (Default: True)")
@click.option("--timeout", type=click.FLOAT,
              help="Maximum time requests are allowed to take. (Default: 5.0)")
@click.option("--porcelain", is_flag=True,
              help="Style output in an easy-to-parse format. (Default: False)")
@click.option("--lastmodified", "-lm",
              help="Shows the last modified date of your followings")
@click.pass_context
def following(ctx, check, timeout, porcelain, lastmodified):
    """Return the list of sources you’re following."""
    sources = ctx.obj['conf'].following

    if check:
        sources = get_remote_status(sources, timeout)
        for (source, status) in sources:
            click.echo(style_source_with_status(source, status, porcelain))
    else:
        sources = sorted(sources, key=lambda source: source.nick)
        for source in sources:
            click.echo(style_source(source, porcelain))


@cli.command()
@click.argument("nick")
@click.argument("url")
@click.option("--force", "-f", flag_value=True,
              help="Force adding and overwriting nick")
@click.pass_context
def follow(ctx, nick, url, force):
    """Add a new source to your followings."""
    source = Source(nick, url)
    sources = ctx.obj['conf'].following

    if not force:
        if source.nick in (source.nick for source in sources):
            click.confirm("➤ You’re already following {0}. Overwrite?".format(
                click.style(source.nick, bold=True)), default=False, abort=True)

        _, status = get_remote_status([source])[0]
        if status != 200:
            click.confirm("➤ The feed of {0} at {1} is not available. Follow anyway?".format(
                click.style(source.nick, bold=True),
                click.style(source.url, bold=True)), default=False, abort=True)

    ctx.obj['conf'].add_source(source)
    click.echo("✓ You’re now following {0}.".format(
        click.style(source.nick, bold=True)))


@cli.command()
@click.argument("nick")
@click.pass_context
def unfollow(ctx, nick):
    """Remove an existing source from your followings."""
    source = ctx.obj['conf'].get_source_by_nick(nick)

    try:
        with Cache.discover() as cache:
            cache.remove_tweets(source.url)
    except OSError as e:
        logger.debug(e)

    ret_val = ctx.obj['conf'].remove_source_by_nick(nick)
    if ret_val:
        click.echo("✓ You’ve unfollowed {0}.".format(
            click.style(source.nick, bold=True)))
    else:
        click.echo("✗ You’re not following {0}.".format(
            click.style(nick, bold=True)))


@cli.command()
def quickstart():
    """Quickstart wizard for setting up twtxt."""
    width = click.get_terminal_size()[0]
    width = width if width <= 79 else 79

    click.secho("twtxt - quickstart", fg="cyan")
    click.secho("==================", fg="cyan")
    click.echo()
    # change to old version
    help_text = "This wizard will generate a basic configuration file for twtxt with all mandatory options set. " \
                "Have a look at the README.rst to get information about the other available options and their meaning."
    click.echo(textwrap.fill(help_text, width))

    click.echo()
    nick = click.prompt("➤ Please enter your desired nick", default=os.environ.get("USER", ""))

    # COMP490 FROM HERE------------------ (overwrite_check is from twtxt's latest update from buckket, however is  heavily modified because it didn't do what specifications required)
    def overwrite_check(path):

        if os.path.isfile(path):
            if click.confirm("➤ '{0}' already exists. Overwrite?".format(path)):
                print("file will be overwritten")
            else:
                cfgfile = click.prompt("➤ Please enter the desired location for your config file",
                                       os.path.join(Config.config_dir, Config.config_name),
                                       type=click.Path(readable=True, writable=True, file_okay=True))

    
    def user_preference(path):
        if click.confirm("➤ '{0}' already exists. Overwrite?".format(path)):
            return True
        else:
            return False

    def g(): #best function ever.
        return True


    def determineCF(path):  # comp490
        if os.path.isfile(path):
            if user_preference(path):
                print("file will be overwritten")
                return path
            else:
                cfgfile = click.prompt("➤ Please enter the desired location for your config file",
                                       os.path.join(Config.config_dir, Config.config_name),
                                       type=click.Path(readable=True, writable=True, file_okay=True))
                return cfgfile

    # cfgfile = os.path.expanduser(cfgfile)
    cfgfile = os.path.join(Config.config_dir, Config.config_name)  # comp490
    cfgfile = determineCF(cfgfile)  # comp490


    twtfile = click.prompt("➤ Please enter the desired location for your twtxt file",
                           os.path.expanduser("~/twtxt.txt"),
                           type=click.Path(readable=True, writable=True, file_okay=True))
    twtfile_dir = os.path.dirname(twtfile)
    if not os.path.exists(twtfile_dir):
        os.makedirs(twtfile_dir)
    #twtfile = os.path.expanduser(twtfile)
    #twtfile = determineCF(twtfile)
    overwrite_check(twtfile)
#COMP490 TO HERE------------------
    twturl = click.prompt("➤ Please enter the URL your twtxt file will be accessible from",
                          default="https://example.org/twtxt.txt")

    disclose_identity = click.confirm("➤ Do you want to disclose your identity? Your nick and URL will be shared when "
                                      "making HTTP requests", default=False)

    click.echo()
    add_news = click.confirm("➤ Do you want to follow the twtxt news feed?", default=True)

    conf = Config.create_config2(cfgfile, nick, twtfile, twturl, disclose_identity, add_news)
    open(os.path.expanduser(twtfile), "a").close()

    twtfile_dir = os.path.dirname(twtfile)
    if not os.path.exists(twtfile_dir):
        os.makedirs(twtfile_dir)
    open(twtfile, "a").close()

    click.echo()
    click.echo("✓ Created config file at '{0}'.".format(click.format_filename(conf.config_file)))
    click.echo("✓ Created twtxt file at '{0}'.".format(click.format_filename(twtfile)))


main = cli
