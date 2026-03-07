import time

class TokenBuffer:
    def __init__(self, expected_tds):
        self.expected_tds = expected_tds  # Tokens per second
        self.buffer = []
        self.last_delivery_time = time.time()

    def add_token(self, token):
        """Adds a token to the buffer."""
        self.buffer.append(token)

    def deliver_tokens(self):
        """Delivers tokens from the buffer at the expected rate."""
        now = time.time()
        time_elapsed = now - self.last_delivery_time
        tokens_to_deliver = int(time_elapsed * self.expected_tds)

        delivered_tokens = []
        for _ in range(min(tokens_to_deliver, len(self.buffer))):
            delivered_tokens.append(self.buffer.pop(0))

        if delivered_tokens:
            self.last_delivery_time = time.time()
        return delivered_tokens