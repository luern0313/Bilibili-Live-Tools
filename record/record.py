import json
import threading
import time
import urllib
import urllib.request
import urllib.parse
import ssl
import sys
import re
import os
import string
import configparser

import pymysql

sys.path.append(os.path.abspath('../bilibili-tool/'))
import danmaku

ssl._create_default_https_context = ssl._create_unverified_context

SQL_DEFAULT = "INSERT INTO `{}` (`mid`, `name`, `cmd`, `info`) VALUES (%s, %s, %s, %s)"
SQL_DANMAKU = "INSERT INTO `{}` (`mid`, `name`, `cmd`, `danmaku`, `info`) VALUES (%s, %s, %s, %s, %s)"
SQL_INTERACT = "INSERT INTO `{}` (`mid`, `name`, `cmd`, `interact_num`, `info`) VALUES (%s, %s, %s, %s, %s)"
SQL_GIFT = "INSERT INTO `{}` (`mid`, `name`, `cmd`, `gift_name`, `gift_price`, `info`) VALUES (%s, %s, %s, " \
           "%s, %s, %s) "
SQL_SC = "INSERT INTO `{}` (`mid`, `name`, `cmd`, `danmaku`, `gift_name`, `gift_price`, `info`) VALUES (%s, %s, " \
         "%s, %s, 'SUPER_CHAT', %s, %s) "
SQL_POPULARITY = "INSERT INTO `{}` (`mid`, `name`, `cmd`, `popularity`, `info`) VALUES (%s, %s, %s, %s, %s)"

PATTERN_ENTRY = re.compile(r"欢迎.+%(.+)%")

room_id = ""
sheet_name = ""
c = ""
headers = ""
host = ""
token = ""
enterSourceName = ''

DANMAKU_THREAD_NAME = "danmaku"
THREAD_RESTART_TIME = [0, 1, 3, 5, 10, 60, 60, 60, 180, 180,
                       600, 600, 1800, 3600, 3600, 7200, 43200, 86400]
thread_restart_time_index = -1


def check_thread():
    global thread_restart_time_index
    while True:
        if DANMAKU_THREAD_NAME not in [t.name for t in threading.enumerate()]:
            print("线程 " + DANMAKU_THREAD_NAME + " 停止，重启中")
            danmaku_thread = DanmakuThread()
            danmaku_thread.setName(DANMAKU_THREAD_NAME)
            danmaku_thread.start()
        thread_restart_time_index += 1
        if thread_restart_time_index < len(THREAD_RESTART_TIME):
            time.sleep(THREAD_RESTART_TIME[thread_restart_time_index])
        else:
            print("重试次数超过上限")
            input()


class DanmakuThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.fp_time = 0
        self.wh_time = 0

    def run(self):
        global ws
        try:
            print("弹幕ws开启")
            ws = danmaku.CG_Client('wss://' + host + '/sub', han_danmaku, headers, room_id)
            ws.connect()
            ws.init_connect(token)
            danmaku.Heartbeat(ws, 30).start()
            ws.run_forever()
        except KeyboardInterrupt:
            ws.close()


def get_server_list():
    header = {
        'Referer': 'https://live.bilibili.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    request = urllib.request.Request(
        "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id=" + room_id + "",
        headers=header, method='GET')
    response = urllib.request.urlopen(request)
    result = json.loads(response.read().decode('utf-8'))["data"]
    return result["host_list"][0]["host"] + ":" + str(result["host_list"][0]["wss_port"]), result["token"]


def han_danmaku(text: string):
    global thread_restart_time_index
    try:
        danmaku_json = json.loads(text)
        text = text.replace("'", "''")
        mid = ""
        name = ""
        interact_num = -1
        sql = ""
        values = None
        cmd = danmaku_json["cmd"]

        thread_restart_time_index = -1

        if cmd == "DANMU_MSG":
            mid = str(danmaku_json["info"][2][0])
            name = danmaku_json["info"][2][1]
            dan = danmaku_json["info"][1]
            dan = dan.replace("'", "''")

            sql = SQL_DANMAKU.format(sheet_name)
            values = (mid, name, cmd, dan, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + ")  danmaku: " + danmaku_json["info"][1])
        elif cmd == "INTERACT_WORD":
            enter = danmaku_json["data"]
            mid = enter["uid"]
            name = enter["uname"]
            interact_num = enter["msg_type"]

            sql = SQL_INTERACT.format(sheet_name)
            values = (mid, name, cmd, interact_num, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + ")  interact_num: " + str(interact_num))
        elif cmd == "ENTRY_EFFECT":
            data = danmaku_json["data"]
            mid = data["uid"]
            writing = data["copy_writing"]
            name = PATTERN_ENTRY.match(writing).group(1)
            interact_num = 1

            sql = SQL_INTERACT.format(sheet_name)
            values = (mid, name, cmd, interact_num, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + ")  interact_num: " + str(interact_num))
        elif cmd == "SEND_GIFT":
            gift = danmaku_json["data"]
            mid = gift["uid"]
            name = gift["uname"]
            gift_name = gift["giftName"]
            gift_price = (gift["total_coin"] / 10) if gift["coin_type"] == "gold" else 0

            sql = SQL_GIFT.format(sheet_name)
            values = (mid, name, cmd, gift_name, gift_price, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + "): " + gift_name + "  " + str(gift_price / 100) + "元")
        elif cmd == "COMBO_SEND":
            gift = danmaku_json["data"]
            mid = gift["uid"]
            name = gift["uname"]
            gift_name = gift["gift_name"]
            gift_price = (gift["combo_total_coin"] / 10)

            sql = SQL_GIFT.format(sheet_name)
            values = (mid, name, cmd, gift_name, gift_price, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + "): " + gift_name + "  " + str(gift_price / 100) + "元")
        elif cmd == "SUPER_CHAT_MESSAGE":
            data = danmaku_json["data"]
            mid = data["uid"]
            name = data["user_info"]["uname"]
            danmaku = data["message"]
            price = data["price"] * 100

            sql = SQL_SC.format(sheet_name)
            values = (mid, name, cmd, danmaku, price, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + ")  danmaku: " + danmaku + "  price: " + str(price))
        elif cmd == "GUARD_BUY":
            data = danmaku_json["data"]
            mid = data["uid"]
            name = data["username"]
            gift_name = data["gift_name"]
            gift_price = data["price"] / 10

            sql = SQL_GIFT.format(sheet_name)
            values = (mid, name, cmd, gift_name, gift_price, text)
        elif cmd == "WATCHED_CHANGE":
            data = danmaku_json["data"]
            num = data["num"]

            sql = SQL_POPULARITY.format(sheet_name)
            values = (mid, name, cmd, num, text)
        elif cmd == "LIVE":
            cursor.execute("ALTER TABLE `" + sheet_name + "` CHANGE `is_live` `is_live` TINYINT(1) NOT NULL DEFAULT '1';")
            connection.commit()

            sql = SQL_DEFAULT.format(sheet_name)
            values = (mid, name, cmd, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + ")")
        elif cmd == "PREPARING":
            cursor.execute("ALTER TABLE `" + sheet_name + "` CHANGE `is_live` `is_live` TINYINT(1) NOT NULL DEFAULT '0';")
            connection.commit()

            sql = SQL_DEFAULT.format(sheet_name)
            values = (mid, name, cmd, text)
            # tool_print_log(cmd + "  " + name + "(" + str(mid) + ")")
        else:
            if is_all:
                sql = SQL_DEFAULT.format(sheet_name)
                values = ("", "", cmd, text)
            else:
                return

        cursor.execute(sql, values)

        connection.commit()
    except Exception as e:
        tool_print_log(text)
        tool_print_log("ERR:" + str(e))
        tool_print_log("")


def handler_reply(text):
    return re.sub("{face:\d+?}", "", text).replace("\\", "\\\\").replace("/", "//")


def tool_print_log(text):
    time_now = time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime())
    print(time_now + text)


def main():
    global is_all
    global room_id
    global sheet_name
    global c
    global headers
    global host
    global token
    global connection
    global cursor

    room_id = input("输入直播间id")
    is_all = input("是否收集全部信息(y/N)") == "y"
    sheet_name = room_id if not is_all else room_id + "-all"
    sheet_name += time.strftime("-%y%m%d", time.localtime())
    host, token = get_server_list()

    conf = configparser.ConfigParser()
    conf.read("../utils/config.ini", encoding="utf-8")
    connection = pymysql.Connection(host=conf["sql_config"]["host"], port=int(conf["sql_config"]["port"]),
                                    user=conf["sql_config"]["user"], password=conf["sql_config"]["password"],
                                    db=conf["sql_config"]["db"])
    cursor = connection.cursor()

    headers = [("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"),
               ("Origin", "https://live.bilibili.com")]

    check = threading.Thread(target=check_thread)
    check.setName('Thread:check')
    check.start()


if __name__ == '__main__':
    main()
