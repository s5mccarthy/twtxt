import unittest
# from unittest import *
from unittest.mock import patch
import click
from click.testing import CliRunner
import twtxt.models
import twtxt.twhttp
import twtxt.config
import twtxt.cli
import twtxt.cache
import os
from twtxt.config import Config
from twtxt.cli import cli
import classcli
from classcli import Cliclass


class myTestClass(unittest.TestCase):


    def test_overwrites_config_ask(self):
         cfgfile = os.path.join(Config.config_dir, Config.config_name)
         self.assertEqual(Cliclass.determineCF(cfgfile), cfgfile)

    #
    @property
    def test_creates_configpath_successfully(self):
        test=False
        path = os.path.join(Config.config_dir, Config.config_name)
        if os.path.isfile(path):
           test = True
        self.assertEqual(test, True)

    @property
    def test_creates_twtxtdir_successfully(self):
        return False


    def test_overwrite_twtxtdir_successfully(self):
        twtfile_dir = os.path.dirname(twtfile)
        self.assertTrue(Cliclass.overwrite_check(twtfile), True)


if __name__ == '__main__':
    unittest.main()
