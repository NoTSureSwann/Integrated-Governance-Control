import unittest
import asyncio
import json
import websockets
from services.event_bus import EventBus, NexusEvent
from services.websocket_server import WebSocketServer

class TestWebSocketEngine(unittest.TestCase):
    """
    Test Case untuk memverifikasi fungsionalitas WebSocket Server & Client.
    """
    @classmethod
    def setUpClass(cls):
        # Definisikan port test khusus agar tidak bertabrakan dengan port runtime (8765)
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        
        cls.server = WebSocketServer(host="127.0.0.1", port=8766)
        cls.loop.run_until_complete(cls.server.start())

    @classmethod
    def tearDownClass(cls):
        # Hentikan server setelah seluruh pengujian selesai
        if cls.server:
            cls.loop.run_until_complete(cls.server.stop())
        cls.loop.close()

    def test_websocket_broadcast(self):
        """Menguji apakah event di EventBus berhasil ter-broadcast ke klien WebSocket."""
        received_messages = []

        async def client_receive():
            uri = "ws://127.0.0.1:8766/ws"
            async with websockets.connect(uri) as ws:
                # Trigger Event di EventBus sesaat setelah client connect
                event = NexusEvent(
                    event_type="Logs",
                    payload={"message": "WS Connection Success"},
                    agent="TestAgent"
                )
                # Berikan sedikit waktu agar handshake websocket selesai
                await asyncio.sleep(0.1)
                EventBus().publish(event)
                
                # Terima pesan dari websocket
                msg = await ws.recv()
                received_messages.append(json.loads(msg))

        self.loop.run_until_complete(client_receive())
        
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0]["event_type"], "Logs")
        self.assertEqual(received_messages[0]["payload"]["message"], "WS Connection Success")
        self.assertEqual(received_messages[0]["agent"], "TestAgent")

if __name__ == "__main__":
    unittest.main()
