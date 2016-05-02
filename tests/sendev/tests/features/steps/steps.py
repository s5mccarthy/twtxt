from behave import *
import unittest
import logging
import os
import sys
import textwrap
#import click


@given('creating new profile (using quickstart)')
def step_impl(context):
    return True

@when('create new twtxt file in a non-existent directory')
def step_impl(context):
    twtfile_dir = os.path.dirname(twtfile)
    return True

@then('the specified directory is created')
def step_impl(context):
    os.makedirs(twtfile_dir)
    return True

#@given('creating new profile (using quickstart)')
#def step_impl(context):
  #  return True

@when('create a new config file in a non-existent directory')
def step_impl(context):
    cfgfile = os.path.join(Config.config_dir, Config.config_name)
    return True

@then('create the specified directory and place config there')
def step_impl(context):
    conf = Config.create_config2(cfgfile, nick, twtfile, twturl, disclose_identity, add_news)
    return True


	
#@given('creating a new profile (using quickstart)')
#def step_impl(context):
 #   return True

@when('new config file created in default or user-given location')
def step_impl(context):
    cfgfile = os.path.join(Config.config_dir, Config.config_name)
    return True

@then('detect any existing config before creating new config')
def step_impl(context):
    cfgfile = determineCF(cfgfile)
    return True
