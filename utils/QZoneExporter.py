import os
from datetime import datetime

import pandas as pd
import re
import requests
from tqdm import tqdm
import utils.ToolsUtil as Tools

class QZoneExporter:
    def __init__(self, qzone_client, config, texts, all_friends, user_nickname, send_message, send_result):
        self.qzone_client = qzone_client
        self.config = config
        self.texts = texts
        self.all_friends = all_friends
        self.user_nickname = user_nickname
        self.send_message = send_message
        self.send_result = send_result
        self.user_message = []
        self.forward_message = []
        self.leave_message = []
        self.other_message = []
        self.render_html_url = None

    def save_data(self, read_only=False):
        user_save_path = self._create_directory_structure()
        self._export_data(user_save_path, read_only)
        self._process_texts(user_save_path)
        self._export_message_lists(user_save_path, read_only)
        self._final_summary(user_save_path)
        return self.render_html_url

    def _create_directory_structure(self):
        user_save_path = self.config.result_path + self.qzone_client.uin + '/'
        pic_save_path = user_save_path + 'pic/'
        os.makedirs(user_save_path, exist_ok=True)
        os.makedirs(pic_save_path, exist_ok=True)
        return user_save_path

    def _export_data(self, user_save_path, read_only):
        # 导出全部列表和好友列表，并支持只读推荐
        self._export_excel_with_read_only(user_save_path + self.qzone_client.uin + '_全部列表.xlsx',
                                          self.texts,
                                          ['时间', '内容', '图片链接'],
                                          read_only)
        self._export_excel_with_read_only(user_save_path + self.qzone_client.uin + '_好友列表.xlsx',
                                          self.all_friends,
                                          ['昵称', 'QQ', '空间主页'],
                                          read_only)

    def _export_excel_with_read_only(self, file_path, data, columns, read_only):
        df = pd.DataFrame(data, columns=columns)
        writer = pd.ExcelWriter(file_path, engine="xlsxwriter")
        df.to_excel(writer, index=False)
        if read_only:
            writer.book.read_only_recommended()  # 设置为只读推荐
        writer.close()
        self.send_message.emit(f"已成功导出: {os.path.basename(file_path)}")

    def _process_texts(self, user_save_path):
        pic_save_path = user_save_path + 'pic/'
        for item in tqdm(self.texts, desc="处理消息列表", unit="item"):
            self._download_images(item, pic_save_path)
            self._categorize_messages(item)

    def _download_images(self, item, pic_save_path):
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

    def _categorize_messages(self, item):
        item_text = item[1]
        if self.user_nickname in item_text:
            if '留言' in item_text:
                self.leave_message.append(item)
            elif '转发' in item_text:
                self.forward_message.append(item)
            else:
                self.user_message.append(item)
        else:
            self.other_message.append(item)

    def _export_message_lists(self, user_save_path, read_only):
        # 导出分类的消息列表
        self._export_excel_with_read_only(user_save_path + self.qzone_client.uin + '_说说列表.xlsx',
                                          self.user_message,
                                          ['时间', '内容', '图片链接'],
                                          read_only)
        self._export_excel_with_read_only(user_save_path + self.qzone_client.uin + '_转发列表.xlsx',
                                          self.forward_message,
                                          ['时间', '内容', '图片链接'],
                                          read_only)
        self._export_excel_with_read_only(user_save_path + self.qzone_client.uin + '_留言列表.xlsx',
                                          self.leave_message,
                                          ['时间', '内容', '图片链接'],
                                          read_only)
        self._export_excel_with_read_only(user_save_path + self.qzone_client.uin + '_其他列表.xlsx',
                                          self.other_message,
                                          ['时间', '内容', '图片链接'],
                                          read_only)

    def render_html(self, shuoshuo_path, zhuanfa_path):
        # 读取 Excel 文件内容
        shuoshuo_df = pd.read_excel(shuoshuo_path)
        zhuanfa_df = pd.read_excel(zhuanfa_path)
        # 头像
        avatar_url = f"https://q.qlogo.cn/headimg_dl?dst_uin={self.qzone_client.uin}&spec=640&img_type=jpg"
        # 提取说说列表中的数据
        shuoshuo_data = shuoshuo_df[['时间', '内容', '图片链接']].values.tolist()
        # 提取转发列表中的数据
        zhuanfa_data = zhuanfa_df[['时间', '内容', '图片链接']].values.tolist()
        # 合并所有数据
        all_data = shuoshuo_data + zhuanfa_data
        # 按时间排序
        all_data.sort(key=lambda x: datetime.strptime(x[0], "%Y年%m月%d日 %H:%M"), reverse=True)
        html_template, post_template = Tools.get_html_template()
        # 构建动态内容
        post_html = ""
        for entry in all_data:
            try:
                time, content, img_url = entry
                img_url = str(img_url)
                content_lst = content.split("：")
                if len(content_lst) == 1:
                    continue
                nickname = content_lst[0]
                message = content_lst[1]

                image_html = f'<div class="image"><img src="{img_url}" alt="图片"></div>' if img_url and img_url.startswith(
                    'http') else ''

                # 生成每个动态的HTML块
                post_html += post_template.format(
                    avatar_url=avatar_url,
                    nickname=nickname,
                    time=time,
                    message=message,
                    image=image_html
                )
            except Exception as err:
                print(err)

        # 生成完整的HTML
        final_html = html_template.format(posts=post_html)
        user_save_path = self.config.result_path + self.qzone_client.uin + '/'
        # 将HTML写入文件
        output_file = os.path.join(os.getcwd(), user_save_path, "qzone_posts.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_html)
        self.render_html_url = output_file
        self.send_message.emit('复刻QQ空间说说记录成功!')

    def _final_summary(self, user_save_path):
        pic_save_path = user_save_path + 'pic/'
        self.send_message.emit('导出成功，请查看 ' + user_save_path + self.qzone_client.uin + ' 文件夹内容')
        self.send_message.emit(f"共有 {len(self.texts)} 条消息")
        self.send_message.emit(f"最早的一条说说发布在 {self.texts[-1][0]}")
        self.send_message.emit(f"好友列表共有 {len(self.all_friends)} 个好友")
        self.send_message.emit(f"说说列表共有 {len(self.user_message)} 条说说")
        self.send_message.emit(f"转发列表共有 {len(self.forward_message)} 条转发")
        self.send_message.emit(f"留言列表共有 {len(self.leave_message)} 条留言")
        self.send_message.emit(f"其他列表共有 {len(self.other_message)} 条内容")
        self.send_message.emit(f"图片列表共有 {len(os.listdir(pic_save_path))} 张图片")
        shuoshuo_path = user_save_path + self.qzone_client.uin + '_说说列表.xlsx'
        zhuanfa_path = user_save_path + self.qzone_client.uin + '_转发列表.xlsx'
        self.render_html(shuoshuo_path, zhuanfa_path)
        self.send_result.emit('已完成QQ空间历史数据回忆')