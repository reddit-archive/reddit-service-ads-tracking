from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from pyramid.httpexceptions import HTTPMovedPermanently
from pyramid.request import Request

from ... import (
    mock,
    patch_service,
)

from reddit_service_ads_tracking.lib import (
    useragent,
)


class UserAgentTests(unittest.TestCase):
    def test_user_agent_chrome_osx(self):
        chrome_osx = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/50.0.2661.102 Safari/537.36"
        )

        parsed = useragent.parse(chrome_osx)

        self.assertFalse(parsed["bot"])

        self.assertEqual(parsed["browser_name"], "Chrome")
        self.assertEqual(parsed["browser_version"], "50.0.2661.102")

        self.assertEqual(parsed["os_name"], "Macintosh")

        self.assertEqual(parsed["platform_name"], "Mac OS")
        self.assertEqual(parsed["platform_version"], "X 10.9.5")

    def test_user_agent_firefox_osx(self):
        firefox_osx = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0)"
            " Gecko/20100101 Firefox/33.0"
        )

        parsed = useragent.parse(firefox_osx)

        self.assertFalse(parsed["bot"])

        self.assertEqual(parsed["browser_name"], "Firefox")
        self.assertEqual(parsed["browser_version"], "33.0")

        self.assertEqual(parsed["os_name"], "Macintosh")

        self.assertEqual(parsed["platform_name"], "Mac OS")
        self.assertEqual(parsed["platform_version"], "X 10.10")

    def test_user_agent_firefox_windows(self):
        firefox_osx = (
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
            " Gecko/20100101 Firefox/40.1"
        )

        parsed = useragent.parse(firefox_osx)

        self.assertFalse(parsed["bot"])

        self.assertEqual(parsed["browser_name"], "Firefox")
        self.assertEqual(parsed["browser_version"], "40.1")

        self.assertEqual(parsed["os_name"], "Windows")

        self.assertEqual(parsed["platform_name"], "Windows")
        self.assertEqual(parsed["platform_version"], "7")

    def test_user_agent_ios_safari(self):
        safari_ios = (
            "Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X)"
            " AppleWebKit/537.51.1 (KHTML, like Gecko)"
            " Version/7.0 Mobile/11A465 Safari/9537.53"
        )

        parsed = useragent.parse(safari_ios)

        self.assertFalse(parsed["bot"])

        self.assertEqual(parsed["browser_name"], "Safari")
        self.assertEqual(parsed["browser_version"], "7.0")

        self.assertEqual(parsed["os_name"], "iOS")

        self.assertEqual(parsed["platform_name"], "iOS")
        self.assertEqual(parsed["platform_version"], "7.0")
        self.assertEqual(parsed["sub-platform"], "IPad")

    def test_google_crawler(self):
        google_bot = (
            "Mozilla/5.0 ("
            "compatible; Googlebot/2.1;"
            " +http://www.google.com/bot.html)"
        )

        parsed = useragent.parse(google_bot)

        self.assertTrue(parsed["bot"])

        self.assertEqual(parsed["browser_name"], "GoogleBot")
        self.assertEqual(parsed["browser_version"], "2.1")

        self.assertEqual(parsed["platform_name"], None)
        self.assertEqual(parsed["platform_version"], None)
