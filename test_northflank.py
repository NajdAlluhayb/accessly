import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
import api

class NorthflankRoutes(unittest.TestCase):
    def test_aliases_use_existing_handlers_and_protect_visitor_data(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(api, "visitor_directory", return_value=Path(directory)), patch.object(api, "PUBLIC", True):
            client = TestClient(api.app)
            headers = {"Authorization": "Bearer " + "a" * 64}
            self.assertEqual(client.get("/health").json(), {"status": "ok"})
            for route in ("/profile", "/requests", "/api/profile", "/api/requests", "/jobs/missing"):
                self.assertEqual(client.get(route).status_code, 401)
            self.assertEqual(client.post("/chat", json={}).status_code, 401)
            with patch.object(api, "visitor_busy", return_value=False):
                self.assertEqual(client.post("/profile", headers=headers, json={"needs": ["Captions"]}).status_code, 200)
            self.assertEqual(client.get("/api/profile", headers=headers).json()["needs"], ["Captions"])
            self.assertEqual(client.get("/requests", headers=headers).json(), [])
            with patch.object(api, "analyze", return_value={"id":"job"}) as analyze:
                self.assertEqual(client.post("/chat", headers=headers, json={"url":"https://example.org/event"}).status_code, 202)
                self.assertEqual(str(analyze.call_args.args[0].url), "https://example.org/event")
            with patch.object(api, "message", return_value={"id":"job"}) as message:
                self.assertEqual(client.post("/chat", headers=headers, json={"session_id":"session", "message":"Draft only"}).status_code, 202)
                self.assertEqual(message.call_args.args[0], "session")
            self.assertEqual(client.post("/chat", headers=headers, json={}).status_code, 422)
            self.assertEqual(client.post("/requests/missing/check", headers=headers).status_code, 404)

if __name__ == "__main__": unittest.main()
