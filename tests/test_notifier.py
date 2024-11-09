import unittest
from src.notifier import Notifier

class TestNotifier(unittest.TestCase):
    def setUp(self):
        self.settings = {'enabled': True}
        self.notifier = Notifier(self.settings)

    def test_notify(self):
        # 由于notify方法目前是空实现，我们只测试它不会抛出异常
        try:
            self.notifier.notify("Test report")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"notify() raised {type(e).__name__} unexpectedly!") 