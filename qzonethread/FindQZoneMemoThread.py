import json
from datetime import datetime
from bs4 import BeautifulSoup
import utils.ToolsUtil as Tools
import pandas as pd
import os
import re
import requests
import time
from PySide6.QtCore import QThread, Signal

from utils.ConfigUtil import ConfigUtil
from utils.QZoneClientUtil import QZoneClientUtil


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
        self.WORKDIR = "./config/fetch-all/"
        self.USER_QZONE_INFO = 'user_qzone_info.json'
        self.QZONE_MOMENTS_ALL = 'qzone_moments_all.json'

    def render_html(self, shuoshuo_path, zhuanfa_path):
        # 读取 Excel 文件内容
        shuoshuo_df = pd.read_excel(shuoshuo_path)
        zhuanfa_df = pd.read_excel(zhuanfa_path)
        # 头像
        avatar_url = f"https://q.qlogo.cn/headimg_dl?dst_uin={self.qzone_client.uin}&spec=640&img_type=jpg"
        # 提取说说列表中的数据
        shuoshuo_data = shuoshuo_df[['时间', '内容', '图片链接', '评论']].values.tolist()
        # 提取转发列表中的数据
        zhuanfa_data = zhuanfa_df[['时间', '内容', '图片链接', '评论']].values.tolist()
        # 合并所有数据
        all_data = shuoshuo_data + zhuanfa_data
        # 按时间排序
        all_data.sort(key=lambda x: Tools.safe_strptime(x[0]) or datetime.min, reverse=True)
        html_template, post_template, comment_template = Tools.get_html_template()
        # 构建动态内容
        post_html = ""
        for entry in all_data:
            try:
                time, content, img_urls, comments = entry
                img_url_lst = str(img_urls).split(",")
                content_lst = content.split("：")
                if len(content_lst) == 1:
                    continue
                nickname = content_lst[0]
                message = content_lst[1]
                image_html = '<div class="image">'
                for img_url in img_url_lst:
                    if img_url and img_url.startswith('http'):
                        # 将图片替换为高清图
                        img_url = str(img_url).replace("/m&ek=1&kp=1", "/s&ek=1&kp=1")
                        img_url = str(img_url).replace(r"!/m/", "!/s/")
                        image_html += f'<img src="{img_url}" alt="图片">\n'
                image_html += "</div>"
                comment_html = ""
                # 获取评论数据
                if str(comments) != "nan":
                    comments = eval(comments)
                    for comment in comments:
                        comment_create_time, comment_content, comment_nickname, comment_uin = comment
                        comment_avatar_url = f"https://q.qlogo.cn/headimg_dl?dst_uin={comment_uin}&spec=640&img_type=jpg"
                        comment_html += comment_template.format(
                            avatar_url=comment_avatar_url,
                            nickname=comment_nickname,
                            time=comment_create_time,
                            message=comment_content
                        )
                # 生成每个动态的HTML块
                post_html += post_template.format(
                    avatar_url=avatar_url,
                    nickname=nickname,
                    time=time,
                    message=message,
                    image=image_html,
                    comments=comment_html
                )
            except Exception as err:
                print(err)

        # 生成完整的HTML
        final_html = html_template.format(posts=post_html)
        user_save_path = self.config.result_path + self.qzone_client.uin + '/'
        # 将HTML写入文件
        output_file = os.path.join(os.getcwd(), user_save_path, self.qzone_client.uin + "_回忆说说网页版.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_html)
        self.render_html_url = output_file
        self.send_message.emit('复刻QQ空间说说记录成功!')

    def save_data(self):
        user_save_path = self.config.result_path + self.qzone_client.uin + '/'
        pic_save_path = user_save_path + 'pic/'
        if not os.path.exists(user_save_path):
            os.makedirs(user_save_path)
        if not os.path.exists(pic_save_path):
            os.makedirs(pic_save_path)

        pd.DataFrame(self.texts, columns=['时间', '内容', '图片链接', '评论']).to_excel(
            user_save_path + self.qzone_client.uin + '_全部列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_全部列表.xlsx'}")
        pd.DataFrame(self.all_friends, columns=['昵称', 'QQ', '空间主页']).to_excel(
            user_save_path + self.qzone_client.uin + '_好友列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_好友列表.xlsx'}")
        for item in self.texts:
            item_text = item[1]
            # 可见说说中可能存在多张图片
            item_pic_links = str(item[2]).split(",")
            for item_pic_link in item_pic_links:
                if item_pic_link and len(item_pic_link) > 0 and 'http' in item_pic_link:
                    pic_name = re.sub(r'[\\/:*?"<>|]', '_', item_text).replace(' ', '')
                    if len(pic_name) > 40:
                        pic_name = pic_name[:40] + '.jpg'
                    response = requests.get(item_pic_link)
                    if response.status_code == 200:
                        # 防止图片重名
                        if os.path.exists(pic_save_path + pic_name):
                            pic_name = pic_name.split('.')[0] + "_" + str(int(time.time())) + '.jpg'
                        with open(pic_save_path + pic_name, 'wb') as f:
                            f.write(response.content)
            if self.user_nickname in item_text:
                if '留言' in item_text:
                    self.leave_message.append(item[:-1])
                elif '转发' in item_text:
                    self.forward_message.append(item)
                else:
                    self.user_message.append(item)
            else:
                self.other_message.append(item[:-1])
        pd.DataFrame(self.user_message, columns=['时间', '内容', '图片链接', '评论']).to_excel(
            user_save_path + self.qzone_client.uin + '_说说列表.xlsx', index=False)
        self.send_message.emit(f"已成功导出: {self.qzone_client.uin + '_说说列表.xlsx'}")
        pd.DataFrame(self.forward_message, columns=['时间', '内容', '图片链接', '评论']).to_excel(
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
        for i in range(int(count / 100) + 1):
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
            # 爬取历史空间消息数据
            self.get_memo(count)
        except Exception as e:
            print(f"获取QQ空间互动消息发生异常: {str(e)}")
        self.texts = [t + [""] for t in self.texts]  # 确保texts是四列, 防止后续保存结果出现问题
        self.send_result.emit("获 取 历 史 Q Q 空 间 数 据 成 功!")
        try:
            self.send_message.emit("开 始 获 取 未 删 除 Q Q 空 间 说 说 ...")
            user_moments = self.get_visible_moments_list()
            if user_moments and len(user_moments) > 0:
                # 如果可见说说的内容是从消息列表恢复的说说内容子集，则不添加到消息列表中
                self.texts = [t for t in self.texts if
                              not any(Tools.get_content_from_split(u[1]) in Tools.get_content_from_split(t[1]) for u in
                                      user_moments)]
                self.texts.extend(user_moments)
        except Exception as err:
            print(f"获取未删除QQ空间记录发生异常: {str(err)}")

        # 保存数据
        if len(self.texts) > 0:
            self.save_data()
        else:
            self.send_message.emit("获 取 到 的 历 史 Q Q 空 间 数 据 为 空!")

    # 获取消息总数
    def get_message_count(self):
        # 初始的总量范围
        lower_bound = 0
        upper_bound = 10000000  # 假设最大总量为10000000
        total = upper_bound // 2  # 初始的总量为上下界的中间值
        count = 0
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
            count += 1
            self.send_progress.emit(count)
        self.send_progress.emit(100)
        return total

    # 获取所有可见的未删除的说说+高清图片（包含2014年之前）
    def get_visible_moments_list(self):
        # 1. 获取说说总条数
        user_qzone_info = Tools.read_txt_file(self.WORKDIR, self.USER_QZONE_INFO)
        if not user_qzone_info:
            # 样本缓存未找到，开始请求获取样本
            qq_userinfo_response = self.get_user_qzone_info(1)
            Tools.write_txt_file(self.WORKDIR, self.USER_QZONE_INFO, qq_userinfo_response)
            user_qzone_info = Tools.read_txt_file(self.WORKDIR, self.USER_QZONE_INFO)
        if not Tools.is_valid_json(user_qzone_info):
            print("获取QQ空间信息失败")
            return None
        json_dict = json.loads(user_qzone_info)
        totalMomentsCount = json_dict['total']
        self.send_message.emit(f'你的未删除说说总条数{totalMomentsCount}')

        # 当前未删除说说总数为0, 直接返回
        if totalMomentsCount == 0:
            return None

        # 2. 获取所有说说数据
        # print("开始获取所有未删除说说")
        qzone_moments_all = Tools.read_txt_file(self.WORKDIR, self.QZONE_MOMENTS_ALL)
        if not qzone_moments_all:
            # 缓存未找到，开始请求获取所有未删除说说
            qq_userinfo_response = self.get_user_qzone_info(totalMomentsCount)
            Tools.write_txt_file(self.WORKDIR, self.QZONE_MOMENTS_ALL, qq_userinfo_response)
            qzone_moments_all = Tools.read_txt_file(self.WORKDIR, self.QZONE_MOMENTS_ALL)

        if not Tools.is_valid_json(qzone_moments_all):
            print("获取QQ空间说说失败")
            return None
        json_dict = json.loads(qzone_moments_all)
        qzone_moments_list = json_dict['msglist']
        self.send_message.emit(f'已获取到数据的说说总条数{len(qzone_moments_list)}')

        # 3. 添加说说列表
        texts = []
        for index, item in enumerate(qzone_moments_list):
            content = item['content'] if item['content'] else ""
            nickname = item['name']
            create_time = Tools.format_timestamp(item['created_time'])
            pictures = ""
            # 如果有图片
            if 'pic' in item:
                for index, picture in enumerate(item['pic']):
                    pictures += picture['url1'] + ","
            # 去除最后一个逗号
            pictures = pictures[:-1] if pictures != "" else pictures
            comments = []
            if 'commentlist' in item:
                for index, commentToMe in enumerate(item['commentlist']):
                    comment_content = commentToMe['content']
                    comment_create_time = commentToMe['createTime2']
                    comment_nickname = commentToMe['name']
                    comment_uin = commentToMe['uin']
                    # 时间，内容，昵称，QQ号
                    comments.append([comment_create_time, comment_content, comment_nickname, comment_uin])
            # 格式：时间、内容、图片链接、转发内容、评论内容
            texts.append([create_time, f"{nickname} ：{content}", pictures, comments])
            self.send_progress.emit(int(float(index) / len(qzone_moments_list) * 100.0))
        self.send_progress.emit(100)
        return texts

    # 获取用户QQ空间相关信息
    def get_user_qzone_info(self, num):
        url = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6'
        cookies = self.qzone_client.cookies
        g_tk = self.qzone_client.bkn(cookies.get('p_skey'))
        qq_number = re.sub(r'o0*', '', cookies.get('uin'))
        skey = cookies.get('skey')
        p_uin = cookies.get('p_uin')
        pt4_token = cookies.get('pt4_token')
        p_skey = cookies.get('p_skey')
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': f'uin={p_uin};skey={skey};p_uin={p_uin};pt4_token={pt4_token};p_skey={p_skey}',
            'priority': 'u=1, i',
            'referer': f'https://user.qzone.qq.com/{qq_number}/main',
            'sec-ch-ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }

        params = {
            'uin': f'{qq_number}',
            'ftype': '0',
            'sort': '0',
            'pos': '0',
            'num': f'{num}',
            'replynum': '100',
            'g_tk': f'{g_tk}',
            'callback': '_preloadCallback',
            'code_version': '1',
            'format': 'jsonp',
            'need_private_comment': '1'
        }
        try:
            response = requests.get(url, headers=headers, params=params)
        except Exception as e:
            print(e)
        raw_response = response.text
        # 使用正则表达式去掉 _preloadCallback()，并提取其中的 JSON 数据
        raw_txt = re.sub(r'^_preloadCallback\((.*)\);?$', r'\1', raw_response, flags=re.S)
        # 再转一次是为了去掉响应值本身自带的转义符http:\/\/ 
        json_dict = json.loads(raw_txt)
        if json_dict['code'] != 0:
            print(f"错误 {json_dict['message']}")
            return None
        return json.dumps(json_dict, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    thread = FindQZoneMemoThread()
    thread.start()
