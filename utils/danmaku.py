import threading
import zlib

from ws4py.client.threadedclient import WebSocketClient
import urllib
import urllib.request
import urllib.parse
import json
import time


class CG_Client(WebSocketClient):
    def __init__(self, url, back, header, roomId):
        WebSocketClient.__init__(self, url, headers=header)
        self.back = back
        self.roomId = roomId

    def init_connect(self, token):
        req = bytearray(('{"uid":0,"roomid":' + self.roomId + ',"protover":2,"platform":"web","clientver":"1.10.6","type":2,"key":"' + token + '"}').encode())

        header = bytearray()
        header.extend((len(req) + 16).to_bytes(4, byteorder='big'))
        header += bytearray(b'\x00\x10\x00\x01\x00\x00\x00\x07\x00\x00\x00\x01')
        header += req
        self.send(header)

    def opened(self):
        pass

    def closed(self, code, reason=None):
        print("Closed down:", code, reason)

    def received_message(self, resp):
        msg = resp.data
        if byte2int(msg[11:12]) == 5:
            msg_header_length = byte2int(msg[4:6])
            msg = msg[msg_header_length:]
            is_def, msg = deflate(msg)
            if is_def:
                while msg != b'':
                    msg_s_length = byte2int(msg[0:4])
                    handle_mes(msg[16:msg_s_length], self.back)
                    msg = msg[msg_s_length:]


class Heartbeat(threading.Thread):
    def __init__(self, was, interval):
        threading.Thread.__init__(self)
        self.was = was
        self.interval = interval

    def run(self):
        while True:
            self.was.send(bytearray(b'\x00\x00\x00\x1f\x00\x10\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01' + 
                                    b'\x5b\x6f\x62\x6a\x65\x63\x74\x20\x4f\x62\x6a\x65\x63\x74\x5d'))
            time.sleep(self.interval)


def get_server_list(roomId):
    header = {
        'Referer': 'https://live.bilibili.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    request = urllib.request.Request("https://api.live.bilibili.com/room/v1/Danmu/getConf?room_id=" + roomId + "&platform=pc&player=web",
                                     headers=header, method='GET')
    response = urllib.request.urlopen(request)
    result = json.loads(response.read().decode('utf-8'))["data"]
    return result["host_server_list"][0]["host"], result["token"]


def handle_mes(message, back):
    try:
        back(message.decode('UTF-8'))
    except UnicodeDecodeError:
        back(message)


def byte2int(data):
    return int().from_bytes(data, byteorder='big', signed=True)


def deflate(data):
    try:
        try:
            return True, zlib.decompress(data, -zlib.MAX_WBITS)
        except zlib.error:
            return True, zlib.decompress(data)
    except Exception:
        return False, data


def back(text):
    print(text)
    pass


if __name__ == '__main__':
    roomId = "123456"
    host, token = get_server_list(roomId)
    headers = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"),
               ("Origin", "https://live.bilibili.com"),
               ("Sec-WebSocket-Extensions", "permessage-deflate; client_max_window_bits")]
    ws = None
    try:
        ws = CG_Client('wss://' + host + '/sub', back, headers, roomId)
        ws.connect()
        ws.init_connect(token)
        Heartbeat(ws, 30).start()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
