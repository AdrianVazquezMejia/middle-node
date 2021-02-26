import time
import unittest

from src.watchdog import Watchdog

delay_time = 0


def test_handler():
    global delay_time
    delay_time = time.time() - start_time


class TestWDT(unittest.TestCase):
    def test_timeout(self):
        """
        Test that wdt timeouts 
        """
        global start_time
        start_time = time.time()
        wtd = Watchdog(2, test_handler)
        time.sleep(2)
        self.assertAlmostEqual(delay_time, 2.0, 1, "Must be almost equal")

    def test_reset(self):
        global start_time
        start_time = time.time()
        wdt = Watchdog(2, test_handler)
        time.sleep(1)
        wdt.reset()
        time.sleep(1)
        self.assertAlmostEqual(delay_time, 0.0, 1, "Must be almost equal")
        wdt.stop()

    def test_stop(self):
        global start_time
        start_time = time.time()
        wdt = Watchdog(2, test_handler)
        wdt.stop()
        time.sleep(2)
        self.assertAlmostEqual(delay_time, 0.0, 1, "Must be almost equal")
        wdt.stop()


if __name__ == '__main__':

    unittest.main()
