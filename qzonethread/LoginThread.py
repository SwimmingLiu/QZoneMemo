import sys

import cv2
import numpy as np
import requests
from PIL import Image
import qrcode
import platform
import time
import re
from PySide6.QtCore import QThread, Signal

from utils.ConfigUtil import ConfigUtil

try:
    from pyzbar.pyzbar import decode
except Exception as e:
    print("无法找到 zbar 共享库。请确保安装了 zbar。")
    if platform.system() == "Linux":
        print("对于基于 RPM 的系统（如 Fedora), 您可以运行以下命令:")
        print("sudo dnf install -y zbar")
    elif platform.system() == "Darwin":
        print("MacOS 安装 zbar 请参考:")
        print("https://github.com/LibraHp/GetQzonehistory/issues/23#issuecomment-2349269027")
    print("有关更多安装指南，请参考 zbar 的官方文档或您的发行版文档。")
    sys.exit(1)


class QQLoginThread(QThread):
    send_cookies = Signal(dict)  # cookies
    send_qrcode_result = Signal(str)  # qrcode message
    send_qrcode = Signal(np.ndarray)  # qrcode image

    def __init__(self):
        super().__init__()
        self.config = ConfigUtil()
        self.qrsig = None
        self.cookies = None

    def run(self):
        self.qrsig = self.get_qr_code()
        if self.qrsig:
            self.cookies = self.get_login_info()
        if self.cookies:
            self.send_cookies.emit(self.cookies)
        # 获取cookies之后退出当前线程
        self.quit()

    def get_cookie(self, req):
        try:
            cookies = requests.utils.dict_from_cookiejar(req.cookies)
            uin = requests.utils.dict_from_cookiejar(req.cookies).get('uin')
            regex = re.compile(r'ptsigx=(.*?)&')
            sigx = re.findall(regex, req.text)[0]
            url = ('https://ptlogin2.qzone.qq.com/check_sig?pttype=1&uin=' + uin +
                   '&service=ptqrlogin&nodirect=0&ptsigx=' + sigx +
                   '&s_url=https%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara%3Dizone&f_url=&ptlang' +
                   '=2052&ptredirect=100&aid=549000912&daid=5&j_later=0&low_login_hour=0&regmaster=0&pt_login_type' +
                   '=3&pt_aid=0&pt_aaid=16&pt_light=0&pt_3rd_aid=0')
            r = requests.get(url, cookies=cookies, allow_redirects=False)
            target_cookies = requests.utils.dict_from_cookiejar(r.cookies)
            self.config.save_user(target_cookies)
            return target_cookies
        except Exception as err:
            print(f"Get Cookies Err: {err}")
            return None

    def get_login_info(self):
        ptqrtoken = self.ptqrToken(self.qrsig)
        confirm_status = False
        cancel_status = False
        while True:
            url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=https%3A%2F%2Fqzs.qq.com%2Fqzone%2Fv5%2Floginsucc.html%3Fpara' \
                  '%3Dizone&ptqrtoken=' + str(ptqrtoken) + '&ptredirect=0&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-' \
                  + str(time.time()) + '&js_ver=20032614&js_type=1&login_sig=&pt_uistyle=40&aid=549000912&daid=5&'
            cookies = {'qrsig': self.qrsig}
            try:
                req = requests.get(url, cookies=cookies)
                if '二维码未失效' in req.text:
                    pass
                elif '二维码认证中' in req.text:
                    if not confirm_status:
                        self.send_qrcode_result.emit('二维码认证中')
                        confirm_status = True
                elif '二维码已失效' in req.text:
                    self.send_qrcode_result.emit('二维码已失效')
                    break
                elif '登录成功' in req.text:
                    self.send_qrcode_result.emit('登录成功')
                    return self.get_cookie(req)
                else:
                    if not cancel_status:
                        self.send_qrcode_result.emit('取消登录')
                        cancel_status = True
            except Exception as err:
                print(f"Get Login Info Err: {err}")
            time.sleep(2)
        return None

    # 获取QRCode
    def get_qr_code(self):
        url = 'https://ssl.ptlogin2.qq.com/ptqrshow?appid=549000912&e=4&l=Q&s=8&d=1000&v=3&t=0.8692955245720428&daid=5&pt_3rd_aid=0'
        try:
            resp = requests.get(url)
            qrsig = requests.utils.dict_from_cookiejar(resp.cookies).get('qrsig')

            with open(self.config.temp_path + 'QR.png', 'wb') as f:
                f.write(resp.content)

            im = Image.open(self.config.temp_path + 'QR.png')
            qrcode_img_cv2 = cv2.imdecode(np.fromfile(self.config.temp_path + 'QR.png', dtype=np.uint8), -1)
            self.send_qrcode.emit(qrcode_img_cv2)
            im = im.resize((350, 350))
            # 解码二维码
            decoded_objects = decode(im)
            for obj in decoded_objects:
                qr = qrcode.QRCode()
                qr.add_data(obj.data.decode('utf-8'))
                # qr.print_ascii(invert=True)
            return qrsig

        except Exception as err:
            print(f"Get QRCode Err: {err}")

    def ptqrToken(self, qrsig):
        n, i, e = len(qrsig), 0, 0
        while n > i:
            e += (e << 5) + ord(qrsig[i])
            i += 1
        return 2147483647 & e


if __name__ == '__main__':
    cookie_thread = QQLoginThread()

    cookie_thread.cookies_signal.connect(lambda cookies: print("Cookies:", cookies))
    cookie_thread.start()
