import unittest
from concurrent.futures import ThreadPoolExecutor

from ai_studio.runtime import Runtime, USERS


class RuntimeTests(unittest.TestCase):
    def test_completed_task_asset_and_accounting(self):
        runtime = Runtime(delay=0)
        user = USERS["local-member-key"]
        run = runtime.create(user, "image", "local-poster", "<script>hello</script>")
        runtime.executor.shutdown(wait=True)
        result = runtime.get(user, run["id"])
        self.assertEqual(result["state"], "completed")
        content = runtime.asset(user, result["asset_id"])
        self.assertNotIn(b"<script>", content)
        self.assertEqual([e["state"] for e in result["events"]], ["queued", "running", "completed"])
        self.assertEqual(runtime.profile(user)["credits"], {"available": 98, "reserved": 0, "spent": 2})
        runtime.close()

    def test_cancel_refunds_once(self):
        runtime = Runtime(delay=10)
        self.addCleanup(runtime.close)
        user = USERS["local-member-key"]
        run = runtime.create(user, "image", "local-poster", "hello")
        self.assertEqual(runtime.profile(user)["credits"]["reserved"], 2)
        runtime.cancel(user, run["id"])
        with self.assertRaises(ValueError):
            runtime.cancel(user, run["id"])
        self.assertEqual(runtime.profile(user)["credits"], {"available": 100, "reserved": 0, "spent": 0})

    def test_model_and_task_permissions(self):
        runtime = Runtime(delay=10)
        self.addCleanup(runtime.close)
        member, admin = USERS["local-member-key"], USERS["local-admin-key"]
        with self.assertRaises(PermissionError):
            runtime.create(member, "image", "local-badge", "hello")
        run = runtime.create(admin, "image", "local-badge", "hello")
        with self.assertRaises(PermissionError):
            runtime.get(member, run["id"])
        self.assertEqual(runtime.list_runs(member), [])

    def test_tool_and_provider_failure(self):
        runtime = Runtime(delay=0)
        user = USERS["local-member-key"]
        run = runtime.create(user, "tool", "text.uppercase", "hello")
        runtime.executor.shutdown(wait=True)
        self.assertEqual(runtime.get(user, run["id"])["result"], {"text": "HELLO"})
        runtime.close()
        runtime = Runtime(delay=0)
        runtime.provider.render = lambda *_: (_ for _ in ()).throw(ValueError("failed"))
        run = runtime.create(user, "image", "local-poster", "hello")
        runtime.executor.shutdown(wait=True)
        self.assertEqual(runtime.get(user, run["id"])["state"], "failed")
        self.assertEqual(runtime.profile(user)["credits"]["available"], 100)
        runtime.close()

    def test_concurrent_reservation_cannot_overspend(self):
        runtime = Runtime(delay=10)
        self.addCleanup(runtime.close)
        user = USERS["local-member-key"]
        def submit(_):
            try:
                runtime.create(user, "image", "local-poster", "hello")
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            accepted = sum(pool.map(submit, range(60)))
        self.assertEqual(accepted, 50)
        self.assertEqual(runtime.profile(user)["credits"]["available"], 0)


if __name__ == "__main__":
    unittest.main()
