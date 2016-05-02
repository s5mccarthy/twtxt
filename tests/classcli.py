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


class Cliclass:
    def user_preference(path):
        if click.confirm("➤ '{0}' already exists. Overwrite?".format(path)):
            return True
        else:
            return False

    def g():
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
