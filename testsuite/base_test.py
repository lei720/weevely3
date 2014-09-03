from unittest import TestCase
from core.commons import randstr
from testsuite.config import script_folder, script_folder_url
from generate import generate, save_generated
import hashlib
import os

class BaseTest(TestCase):

    @classmethod
    def _randomize_bd(cls):
        cls.password = randstr(10)
        password_hash = hashlib.md5(cls.password).hexdigest().lower()
        filename = '%s_%s_%s.php' % (
            __name__, password_hash[:4], password_hash[4:8])
        cls.url = os.path.join(script_folder_url, filename)
        cls.path = os.path.join(script_folder, filename)

    @classmethod
    def setUpClass(cls):

        cls._randomize_bd()

        obfuscated = generate(cls.password)
        save_generated(obfuscated, cls.path)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.path)