import re
import requests
import json

from utils.ConfigUtil import ConfigUtil


class QZoneClientUtil:

    def __init__(self):
        # 登录获取cookies和g_tk
        self.config = ConfigUtil()
        self.cookies = self.config.get_local_user()
        self.g_tk = self.bkn(self.cookies.get('p_skey'))
        self.uin = re.sub(r'o0*', '', self.cookies.get('uin'))

        # 设置请求头
        self.headers = {
            'authority': 'user.qzone.qq.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        }

    # 获取历史消息列表
    def get_message(self, start, count):
        params = {
            'uin': self.uin,
            'begin_time': '0',
            'end_time': '0',
            'getappnotification': '1',
            'getnotifi': '1',
            'has_get_key': '0',
            'offset': start,
            'set': '0',
            'count': count,
            'useutf8': '1',
            'outputhtmlfeed': '1',
            'scope': '1',
            'format': 'jsonp',
            'g_tk': [
                self.g_tk,
                self.g_tk,
            ],
        }

        try:
            response = requests.get(
                'https://user.qzone.qq.com/proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds2_html_pav_all',
                params=params,
                cookies=self.cookies,
                headers=self.headers,
                timeout=(5, 10)  # 设置连接超时为5秒，读取超时为10秒
            )
            return response
        except requests.Timeout:
            print("请求超时")
            return None

    # 获取登录用户信息
    def get_login_user_info(self):
        response = requests.get(f'https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?g_tk={self.g_tk}&uins={self.uin}',
                                headers=self.headers, cookies=self.cookies)
        info = response.content.decode('GBK')
        info = info.strip().lstrip('portraitCallBack(').rstrip(');')
        info = json.loads(info)
        return info

    def bkn(self, pSkey):
        # 计算bkn
        t, n, o = 5381, 0, len(pSkey)

        while n < o:
            t += (t << 5) + ord(pSkey[n])
            n += 1

        return t & 2147483647


