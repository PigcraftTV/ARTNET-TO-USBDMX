import socket
import ctypes
from datetime import datetime
import time


# You might want to change these Settings:
SERIAL_NUMBER = b"00000000"
ARTNET_UNIVERSE_OUT = 0
ARTNET_UNIVERSE_IN = 1
ARTNET_TARGET_IP = "255.255.255.255"
dll_path = "/home/admin/usbdmx.so"

_usbdmx = ctypes.CDLL(dll_path)
_usbdmx.OpenLink.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
_usbdmx.OpenLink.restype = ctypes.c_int
_usbdmx.SetInterfaceMode.argtypes = [ctypes.c_char_p, ctypes.c_int]
_usbdmx.SetInterfaceMode.restype = ctypes.c_int
_usbdmx.CloseLink.argtypes = [ctypes.c_char_p]
_usbdmx.CloseLink.restype = None

class FX5Interface:
    def __init__(self, serial: bytes):
        self.serial = serial
        self.dmx_in = ctypes.create_string_buffer(512)
        self.dmx_out = ctypes.create_string_buffer(512)

    def open(self):
        if _usbdmx.OpenLink(self.serial, self.dmx_out, self.dmx_in) == 0:
            raise IOError("Unable to open interface")
        _usbdmx.SetInterfaceMode(self.serial, 6)

    def close(self):
        _usbdmx.CloseLink(self.serial)

    def set_channels(self, channel_values: dict):
        """channel_values = {channel_index: value}"""
        for ch, val in channel_values.items():
            assert 0 <= ch <= 511
            assert 0 <= val <= 255
            self.dmx_out[ch] = val.to_bytes(1, "little")

fx5 = FX5Interface(SERIAL_NUMBER)
fx5.open()
letters = {
    "A": ["  A  ",
          " A A ",
          "AAAAA",
          "A   A",
          "A   A"],
    "R": ["RRRR ",
          "R   R",
          "RRRR ",
          "R R  ",
          "R  RR"],
    "T": ["TTTTT",
          "  T  ",
          "  T  ",
          "  T  ",
          "  T  "],
    "N": ["N   N",
          "NN  N",
          "N N N",
          "N  NN",
          "N   N"],
    "E": ["EEEEE",
          "E    ",
          "EEE  ",
          "E    ",
          "EEEEE"],
    "U": ["U   U",
          "U   U",
          "U   U",
          "U   U",
          " UUU "],
    "S": [" SSS ",
          "S    ",
          " SSS ",
          "    S",
          "SSSS "],
    "D": ["DDDD ",
          "D   D",
          "D   D",
          "D   D",
          "DDDD "],
    "M": ["M   M",
          "MM MM",
          "M M M",
          "M   M",
          "M   M"],
    "X": ["X   X",
          " X X ",
          "  X  ",
          " X X ",
          "X   X"],
    "<": ["  <  ",
          " <   ",
          "<    ",
          " <   ",
          "  <  "],
    ">": ["  >  ",
          "   > ",
          "    >",
          "   > ",
          "  >  "],
    "-": ["     ",
          "-----",
          "     ",
          "     ",
          "     "],
    " ": ["     ",
          "     ",
          "     ",
          "     ",
          "     "],
    "/": ["    /",
          "   / ",
          "  /  ",
          " /   ",
          "/    "],
    "B": [
          "BBBB ",
          "B   B",
          "BBBB ",
          "B   B",
          "BBBB "]

    
}

text = "ARTNET <-> USBDMX"

for i in range(5):
    line = ""
    for char in text:
        line += letters.get(char.upper(), ["     "]*5)[i] + "  "
    print(line)

print("Artnet <-> USBDMX by PigcraftTV")
print(f"[{datetime.now()}] Interface {SERIAL_NUMBER.decode()} opened, DMX-Out ready")

UDP_IP = ""
UDP_PORT = 6454
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind((UDP_IP, UDP_PORT))
print(f"[{datetime.now()}] Art-Net listener started on UDP port {UDP_PORT}")

def send_artnet(universe: int, dmx_data: bytes):
    packet = bytearray()
    packet.extend(b"Art-Net\x00")
    packet.extend((0x5000).to_bytes(2, "little"))
    packet.extend((14).to_bytes(2, "little"))
    packet.extend((0).to_bytes(1, "big"))
    packet.extend((0).to_bytes(1, "big"))
    packet.extend(universe.to_bytes(2, "little"))
    packet.extend(len(dmx_data).to_bytes(2, "big")) 
    packet.extend(dmx_data)

    sock.sendto(packet, (ARTNET_TARGET_IP, UDP_PORT))

last_in_state = bytes(512)

while True:

    sock.settimeout(0.01)
    try:
        data, addr = sock.recvfrom(1024)
    except socket.timeout:
        data = None

    if data and data[:8] == b"Art-Net\x00":
        opcode = int.from_bytes(data[8:10], "little")
        if opcode == 0x5000:  # OpDmx
            universe = int.from_bytes(data[14:16], "little")
            if universe == ARTNET_UNIVERSE_OUT:
                length = int.from_bytes(data[16:18], "big")
                dmx_data = data[18:18+length]

                changed_channels = {}
                for i, val in enumerate(dmx_data):
                    if fx5.dmx_out[i] != val.to_bytes(1, "little"):
                        fx5.dmx_out[i] = val.to_bytes(1, "little")
                        changed_channels[i+1] = val

                if changed_channels:
                    _usbdmx.SetInterfaceMode(fx5.serial, 6)
                    print(f"[{datetime.now()}] Artnet -> DMX, {len(changed_channels)} channels updated")

    dmx_in_bytes = bytes(fx5.dmx_in.raw)
    if dmx_in_bytes != last_in_state:
        last_in_state = dmx_in_bytes
        send_artnet(ARTNET_UNIVERSE_IN, dmx_in_bytes)
        print(f"[{datetime.now()}] DMX In -> Artnet sent ({len(dmx_in_bytes)} channels)")

    time.sleep(0.01)
#Code with Copyright by PigcraftTV 2025



