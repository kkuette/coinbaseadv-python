import unittest
from unittest.mock import patch, MagicMock
from cbadv.websocket_client import WebsocketClient

class TestWebsocketClient(unittest.TestCase):

    @patch('cbadv.websocket_client.create_connection')
    def setUp(self, mock_create_connection):
        self.api_key = 'test_api_key'
        self.api_secret = 'test_api_secret'
        self.client = WebsocketClient(api_key=self.api_key, api_secret=self.api_secret, channel='ticker')
        self.client.ws = MagicMock()

    @patch('cbadv.websocket_client.create_connection')
    def test_reconnect(self, mock_create_connection):
        self.client._reconnect()
        self.assertTrue(self.client.ws.close.called)
        self.assertTrue(mock_create_connection.called)

    @patch('cbadv.websocket_client.create_connection')
    def test_listen_reconnect_on_error(self, mock_create_connection):
        self.client.ws.recv.side_effect = Exception("Connection drop")
        with patch.object(self.client, '_reconnect') as mock_reconnect:
            self.client._listen()
            self.assertTrue(mock_reconnect.called)

    @patch('cbadv.websocket_client.create_connection')
    def test_on_close_reconnect(self, mock_create_connection):
        with patch.object(self.client, '_reconnect') as mock_reconnect:
            self.client.on_close()
            self.assertTrue(mock_reconnect.called)

    @patch('cbadv.websocket_client.create_connection')
    def test_simulate_connection_drop(self, mock_create_connection):
        self.client.ws.recv.side_effect = Exception("Connection drop")
        with patch.object(self.client, '_reconnect') as mock_reconnect:
            self.client._listen()
            self.assertTrue(mock_reconnect.called)

    @patch('cbadv.websocket_client.create_connection')
    def test_verify_reconnect_method(self, mock_create_connection):
        with patch.object(self.client, '_disconnect') as mock_disconnect:
            with patch.object(self.client, '_connect') as mock_connect:
                with patch('time.sleep', return_value=None):
                    self.client._reconnect()
                    self.assertTrue(mock_disconnect.called)
                    self.assertTrue(mock_connect.called)

if __name__ == '__main__':
    unittest.main()
