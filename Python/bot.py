import cfg
import socket
import time
import re
import random
import argparse
from pythonosc import udp_client


class OSCBot:
    def __init__(self, oscaddr, oscport):
        self.CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
        self.oscclient = udp_client.SimpleUDPClient(oscaddr, oscport)
        self.twitchserver = socket.socket()

    def twitch_connect(self):
        """
        Connects to the twitch server
        """
        self.twitchserver.connect((cfg.HOST, cfg.PORT))
        self.twitchserver.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
        self.twitchserver.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
        self.twitchserver.send("JOIN #{}\r\n".format(cfg.CHAN).encode("utf-8"))

    def chat(self, msg):
        """
        Send a chat message to the twitch server.
        msg  -- the message to be sent
        """
        self.twitchserver.send("PRIVMSG #{} :{}".format(cfg.CHAN, msg))

    def work(self):
        """
        Handles all messages from the twitch server
        Filters the messages to the audio decider
        """
        while True:
            # get a communication from the twitch server
            string = self.twitchserver.recv(1024).decode("utf-8")

            # is it an irc ping
            if string == "PING :tmi.twitch.tv\r\n":
                self.twitchserver.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            # otherwise it's a chat message
            else:
                # split into useful parts
                username = re.search(r"\w+", string).group(0)  # return the entire match
                message = self.CHAT_MSG.sub("", string)

                # identify for OSC triggers
                # if random.random() < 0.15:
                #     self.oscclient.send_message("/twitch/trigger/volume/set", random.random())

                if random.random() < 0.25:
                    self.oscclient.send_message("/twitch/trigger/volume/on", "on")
                else:
                    self.oscclient.send_message("/twitch/trigger/volume/off", "off")

                # change note every message
                if cfg.CHAN in message or "dad" in message:
                    self.oscclient.send_message("/twitch/trigger/note", random.randint(0, 100))

                # log locally
                # print(username + ": " + message)

                # give the cpu a break
                time.sleep(1 / cfg.RATE)


if __name__ == '__main__':
    # grab arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=57120, help="The port the OSC server is listening on")
    args = parser.parse_args()

    bot = OSCBot(args.ip, args.port)
    bot.twitch_connect()
    bot.work()
