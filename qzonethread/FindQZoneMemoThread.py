from datetime import datetime

from bs4 import BeautifulSoup
from tqdm import trange, tqdm
import utils.ToolsUtil as Tools
import pandas as pd
import os
import re
import requests
import time
from PySide6.QtCore import QThread, Signal

from utils.ConfigUtil import ConfigUtil
from utils.QZoneClientUtil import QZoneClientUtil

from utils.QZoneExporter import *

class FindQZoneMemoThread(QThread):
    send_progress = Signal(int)
    send_login_status = Signal(str)
    send_message = Signal(str)
    send_result = Signal(str)

    def __init__(self):
        super().__init__()
        self.texts = []
        self.all_friends = []
        self.other_message = []
        self.user_message = []
        self.leave_message = []
        self.forward_message = []
        self.user_nickname = None
        self.qzone_client = None
        self.config = ConfigUtil()
        self.progress_bar = 0
        self.render_html_url = None
        self.exporter = None


    # def render_html(self, shuoshuo_path, zhuanfa_path):
    #     self.render_html_url = self.exporter.render_html(shuoshuo_path, zhuanfa_path)

    def save_data(self):
        user_save_path = self.config.result_path + self.qzone_client.uin + '/'
        pic_save_path = user_save_path + 'pic/'
        if not os.path.exists(user_save_path):
            os.makedirs(user_save_path)
        if not os.path.exists(pic_save_path):
            os.makedirs(pic_save_path)

        pd.DataFrame(self.texts, columns=['时间', '内容', '图片链接']).to_excel(
            user_save_path + self.qzone_client.uin + '_全部列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_全部列表.xlsx'}")
        pd.DataFrame(self.all_friends, columns=['昵称', 'QQ', '空间主页']).to_excel(
            user_save_path + self.qzone_client.uin + '_好友列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_好友列表.xlsx'}")
        for item in tqdm(self.texts, desc="处理消息列表", unit="item"):
            item_text = item[1]
            item_pic_link = item[2]
            if item_pic_link and 'http' in item_pic_link:
                pic_name = re.sub(r'[\\/:*?"<>|]', '_', item_text).replace(' ', '')
                if len(pic_name) > 40:
                    pic_name = pic_name[:40] + '.jpg'
                response = requests.get(item_pic_link)
                if response.status_code == 200:
                    with open(pic_save_path + pic_name, 'wb') as f:
                        f.write(response.content)
            if self.user_nickname in item_text:
                if '留言' in item_text:
                    self.leave_message.append(item)
                elif '转发' in item_text:
                    self.forward_message.append(item)
                else:
                    self.user_message.append(item)
            else:
                self.other_message.append(item)
        pd.DataFrame(self.user_message, columns=['时间', '内容', '图片链接']).to_excel(
            user_save_path + self.qzone_client.uin + '_说说列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_说说列表.xlsx'}")
        pd.DataFrame(self.forward_message, columns=['时间', '内容', '图片链接']).to_excel(
            user_save_path + self.qzone_client.uin + '_转发列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_转发列表.xlsx'}")
        pd.DataFrame(self.leave_message, columns=['时间', '内容', '图片链接']).to_excel(
            user_save_path + self.qzone_client.uin + '_留言列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_留言列表.xlsx'}")
        pd.DataFrame(self.other_message, columns=['时间', '内容', '图片链接']).to_excel(
            user_save_path + self.qzone_client.uin + '_其他列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_其他列表.xlsx'}")
        self.send_message.emit('导出成功，请查看 ' + user_save_path + self.qzone_client.uin + ' 文件夹内容')
        self.send_message.emit('共有 ' + str(len(self.texts)) + ' 条消息')
        self.send_message.emit('最早的一条说说发布在' + self.texts[self.texts.__len__() - 1][0])
        self.send_message.emit('好友列表共有 ' + str(len(self.all_friends)) + ' 个好友')
        self.send_message.emit('说说列表共有 ' + str(len(self.user_message)) + ' 条说说')
        self.send_message.emit('转发列表共有 ' + str(len(self.forward_message)) + ' 条转发')
        self.send_message.emit('留言列表共有 ' + str(len(self.leave_message)) + ' 条留言')
        self.send_message.emit('其他列表共有 ' + str(len(self.other_message)) + ' 条内容')
        self.send_message.emit('图片列表共有 ' + str(len(os.listdir(pic_save_path))) + ' 张图片')
        shuoshuo_path = user_save_path + self.qzone_client.uin + '_说说列表.xlsx'
        zhuanfa_path = user_save_path + self.qzone_client.uin + '_转发列表.xlsx'
        self.render_html(shuoshuo_path, zhuanfa_path)
        self.send_result.emit('已完成QQ空间历史数据回忆')

    def get_memo(self, count):
        self.send_message.emit("开 始 获 取 历 史 Q Q 空 间 动 态 详 情 ...")
        for i in trange(int(count / 100) + 1, desc='Progress', unit='100条'):
            try:
                message = self.qzone_client.get_message(i * 100, 100).content.decode('utf-8')
                time.sleep(0.2)
                html = Tools.process_old_html(message)
                if "li" not in html:
                    continue
                soup = BeautifulSoup(html, 'html.parser')
                for element in soup.find_all('li', class_='f-single f-s-s'):
                    self.process_element(element)
                self.send_progress.emit(float(i) / (count / 100.0) * 100.0)
            except Exception as err:
                print(f"Get Memo Err: {err}")
        self.send_progress.emit(100)

    def process_element(self, element):
        put_time = None
        text = None
        img = None
        friend_element = element.find('a', class_='f-name q_namecard')
        if friend_element:
            friend_name = friend_element.get_text()
            friend_qq = friend_element.get('link')[9:]
            friend_link = friend_element.get('href')
            if friend_qq not in [sublist[1] for sublist in self.all_friends]:
                self.all_friends.append([friend_name, friend_qq, friend_link])

        time_element = element.find('div', class_='info-detail')
        text_element = element.find('p', class_='txt-box-title ellipsis-one')
        img_element = element.find('a', class_='img-item')
        if time_element and text_element:
            put_time = time_element.get_text().replace('\xa0', ' ')
            text = text_element.get_text().replace('\xa0', ' ')
            if img_element:
                img = img_element.find('img').get('src')
            if text not in [sublist[1] for sublist in self.texts]:
                self.texts.append([put_time, text, img])

    def run(self):
        self.qzone_client = QZoneClientUtil()
        try:
            # 获取用户信息
            user_info = self.qzone_client.get_login_user_info()
            # 获取昵称
            self.user_nickname = user_info[self.qzone_client.uin][6]
            self.send_login_status.emit(f"用户<{self.qzone_client.uin}>: <{self.user_nickname}>登录成功")
            # 获取QQ空间消息总数
            count = self.get_message_count()
            self.send_message.emit("开 始 获 取 历 史 Q Q 空 间 动 态 总 数 ...")
            # 爬取历史空间消息数据render_html_url
            self.get_memo(count)
        except Exception as e:
            print(f"发生异常: {str(e)}")
        self.send_result.emit("获 取 历 史 Q Q 空 间 数 据 成 功!")
        # 保存数据
        if len(self.texts) > 0:
            self.exporter = QZoneExporter(
                qzone_client=self.qzone_client,
                config=self.config,
                texts=self.texts,
                all_friends=self.all_friends,
                user_nickname=self.user_nickname,
                send_message=self.send_message,  # 传递信号
                send_result=self.send_result  # 传递信号
            )
            self.render_html_url = self.exporter.save_data(read_only=False)

        else:
            self.send_message.emit("获 取 到 的 历 史 Q Q 空 间 数 据 为 空!")

    # 获取消息总数
    def get_message_count(self):
        # 初始的总量范围
        lower_bound = 0
        upper_bound = 100000  # 假设最大总量为100000
        total = upper_bound // 2  # 初始的总量为上下界的中间值
        count = 0
        with tqdm(desc="正在获取消息列表数量...") as pbar:
            while lower_bound <= upper_bound:
                response = self.qzone_client.get_message(total, 100)
                if response is None:
                    print("获取消息失败")
                    return None
                if "li" in response.text:
                    # 请求成功，总量应该在当前总量的右侧
                    lower_bound = total + 1
                else:
                    # 请求失败，总量应该在当前总量的左侧
                    upper_bound = total - 1
                total = (lower_bound + upper_bound) // 2  # 更新总量为新的中间值
                pbar.update(1)
                count += 1
                self.send_progress.emit(count)
        self.send_progress.emit(100)
        return total

if __name__ == '__main__':
    thread = FindQZoneMemoThread()
    thread.start()
