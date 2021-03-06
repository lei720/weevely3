from testsuite.base_test import BaseTest
from testfixtures import log_capture
from core import modules
from core.sessions import SessionURL
from core import messages
from testsuite import config
import unittest
import os

@unittest.skipIf(not
                    (config.sql_dbms == 'mysql'
                    and config.sql_db
                    and config.sql_user
                    and config.sql_passwd
                    ),
                "Mysql console test is not properly configured"
                )
class MySQLConsole(BaseTest):

    def setUp(self):
        self.session = SessionURL(self.url, self.password, volatile = True)
        modules.load_modules(self.session)

        self.run_argv = modules.loaded['sql_console'].run_argv
        self.run_cmdline = modules.loaded['sql_console'].run_cmdline

    @unittest.skipIf(not config.sql_autologin,
                    "Autologin is not set")

    def test_autologin(self):
        self.assertEqual(self.run_argv(['-query', "select 'A';"]), [["A"]])
        self.assertTrue(self.run_argv(['-query', 'select @@hostname;']))
        self.assertTrue(self.run_argv(['-query', 'show databases;']))

    @log_capture()
    def test_wrongcommand(self, log_captured):
        # Wrong command
        self.assertIsNone(self.run_cmdline('-query bogus'))

        # Checking if the error message start about the missing comma is ok
        self.assertEqual(messages.module_sql_console.missing_sql_trailer_s[:60],
                         log_captured.records[-2].msg[:60])
        # Check also other error messages
        self.assertEqual('%s %s' % (messages.module_sql_console.no_data,
                                    messages.module_sql_console.check_credentials),
                         log_captured.records[-1].msg)


    @log_capture()
    def test_wronglogin(self, log_captured):

        wrong_login = '-user bogus -passwd bogus -query "select \'A\';"'

        # Using run_cmdline to test the outputs
        self.assertIsNone(self.run_cmdline(wrong_login))
        self.assertEqual('%s %s' % (messages.module_sql_console.no_data,
                                    messages.module_sql_console.check_credentials),
                         log_captured.records[-1].msg)

    def test_login(self):

        login = ['-user', config.sql_user, '-passwd', config.sql_passwd ]

        self.assertEqual(self.run_argv(login + [ '-query', "select 'A';"]), [["A"]])
        self.assertTrue(self.run_argv(login + ['-query', 'select @@hostname;']))
        self.assertTrue(self.run_argv(login + ['-query', 'show databases;']))

        # The user is returned in the form `[[ user@host ]]`
        self.assertEqual(
            self.run_argv(login + ['-query', 'SELECT USER();'])[0][0][:len(config.sql_user)],
            config.sql_user
        )
        self.assertEqual(
            self.run_argv(login + ['-query', 'SELECT CURRENT_USER();'])[0][0][:len(config.sql_user)],
            config.sql_user
        )
