import websocket
import threading
import re
from constants import BOT_USERNAME, OAUTH_TOKEN, CHANNEL


# Function to extract username and message using regex
# def extract_username_and_message(message):
#     regex_pattern = r"^@[^;]*display-name=([^;]+).*PRIVMSG[^:]+:(.*)$"
#     matches = re.match(regex_pattern, message)
#
#     if matches:
#         username, message_content = matches.groups()
#         return username, message_content.strip()
#
#     return None, None


def extract_username_and_message(message):
    remainder, content = message.split(f'PRIVMSG #{CHANNEL} :', 1)
    user = {key: value for key, value in [key_value_pair.split('=') for key_value_pair in remainder.split(';')]}['display-name']

    if user and content:
        return user, content
    return None, None


def on_message(ws, message):
    # This function will be called when a new message is received from the WebSocket
    if "PING" in message:
        # Respond to the PING message to keep the connection alive
        ws.send("PONG\n")
    elif "PRIVMSG" in message:
        # Parse the message from the Twitch IRC response
        user, content = extract_username_and_message(message)
        print(f"{user}: {content}")


def on_error(ws, error):
    print("Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("Closed:", close_status_code, close_msg)


def on_open(ws):
    # This function will be called when the WebSocket connection is opened
    print("Connected to WebSocket.")
    # Join the channel
    ws.send('CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands')
    ws.send(f"PASS {OAUTH_TOKEN}")
    ws.send(f"NICK {BOT_USERNAME}")
    ws.send(f"JOIN #{CHANNEL}")
    send_message(ws, "Hello from scoliosisbot")


def send_message(ws, message):
    # Send a message to the channel
    ws.send(f"PRIVMSG #{CHANNEL} :{message}")


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "wss://irc-ws.chat.twitch.tv:443",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.on_open = on_open

    # Start a separate thread to run the WebSocket
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    ws_thread.join()

    # You can add custom bot logic here or do other tasks in the main thread.
    # For example, you can use a while loop to keep the main thread running while the WebSocket runs in the background.
