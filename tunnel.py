"""
Ngrok tunnel management for public URL generation
"""

from pyngrok import ngrok, conf
import config


class TunnelManager:
    """Manages ngrok tunnel creation and lifecycle"""

    def __init__(self, port):
        self.port = port
        self.tunnel = None
        self.public_url = None

        # Set ngrok auth token if available
        if config.NGROK_AUTH_TOKEN:
            conf.get_default().auth_token = config.NGROK_AUTH_TOKEN

    def start_tunnel(self):
        """Start ngrok tunnel and return public URL"""
        try:
            # Close any existing tunnels
            self.stop_tunnel()

            # Create new tunnel
            self.tunnel = ngrok.connect(self.port, bind_tls=True)
            self.public_url = self.tunnel.public_url

            print(f"Ngrok tunnel created: {self.public_url}")
            return self.public_url
        except Exception as e:
            print(f"Error creating ngrok tunnel: {e}")
            return None

    def stop_tunnel(self):
        """Stop the ngrok tunnel"""
        try:
            if self.tunnel:
                ngrok.disconnect(self.tunnel.public_url)
                self.tunnel = None
                self.public_url = None
                print("Ngrok tunnel closed")
        except Exception as e:
            print(f"Error stopping tunnel: {e}")

    def get_tunnel_info(self):
        """Get information about active tunnels"""
        try:
            tunnels = ngrok.get_tunnels()
            return tunnels
        except Exception as e:
            print(f"Error getting tunnel info: {e}")
            return []

    @staticmethod
    def kill_all_tunnels():
        """Kill all active ngrok tunnels"""
        try:
            ngrok.kill()
            print("All ngrok tunnels killed")
        except Exception as e:
            print(f"Error killing tunnels: {e}")
