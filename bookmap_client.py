import zmq
import threading
import json

class BookmapDataClient:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.thread = None
        self.socket = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._stream_from_zmq, daemon=True)
        self.thread.start()

    def _stream_from_zmq(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://127.0.0.1:5556")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

        print("[ZMQ] Subscribed to tcp://127.0.0.1:5556")

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        while self.running:
            socks = dict(poller.poll(100))
            if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                try:
                    raw = self.socket.recv_string()
                    print("[ZMQ] Raw received:", raw)  # DEBUG
                    data = json.loads(raw)
                    formatted = self._parse_data(data)
                    print("[ZMQ] Parsed:", formatted)  # DEBUG
                    self.callback(formatted)
                except Exception as e:
                    print("[ZMQ] Error:", e)

        self.socket.close()
        context.term()


    def _parse_data(self, raw):
        return {
            "symbol": raw.get("symbol", "Unknown"),
            "bid": raw.get("bestBidPrice"),
            "ask": raw.get("bestAskPrice"),
            "volume": raw.get("volume", 0)
        }

    def stop(self):
        self.running = False

