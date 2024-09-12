import re


# 提取两个字符串之间的内容
def extract_string_between(source_string, start_string, end_string):
    start_index = source_string.find(start_string) + len(start_string)
    end_index = source_string.find(end_string)
    extracted_string = source_string[start_index:-37]
    return extracted_string


# 去除多余的空格
def replace_multiple_spaces(string):
    pattern = r'\s+'
    replaced_string = re.sub(pattern, ' ', string)
    return replaced_string


# 替换十六进制编码
def process_old_html(message):
    def replace_hex(match):
        hex_value = match.group(0)
        byte_value = bytes(hex_value, 'utf-8').decode('unicode_escape')
        return byte_value

    new_text = re.sub(r'\\x[0-9a-fA-F]{2}', replace_hex, message)
    start_string = "html:'"
    end_string = "',opuin"
    new_text = extract_string_between(new_text, start_string, end_string)
    new_text = replace_multiple_spaces(new_text).replace('\\', '')
    return new_text


def get_html_template():
    # HTML模板
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QQ空间动态</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
            }}
            .post {{
                background-color: #333;
                color: #fff;
                padding: 20px;
                margin: 20px;
                border-radius: 10px;
            }}
            .avatar {{
                float: left;
                margin-right: 20px;
            }}
            .content {{
                overflow: hidden;
            }}
            .avatar img {{
                width: 50px;
                height: 50px;
                border-radius: 50%;
            }}
            .nickname {{
                font-size: 1.2em;
                font-weight: bold;
            }}
            .time {{
                color: #999;
                font-size: 0.9em;
            }}
            .message {{
                margin-top: 10px;
                font-size: 1.1em;
            }}
            .image {{
                margin-top: 10px;
            }}
            .image img {{
                max-width: 100%;
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        {posts}
    </body>
    </html>
    """

    # 生成每个动态的HTML内容
    post_template = """
    <div class="post">
        <div class="avatar">
            <img src="{avatar_url}" alt="头像">
        </div>
        <div class="content">
            <div class="nickname">{nickname}</div>
            <div class="time">{time}</div>
            <div class="message">{message}</div>
            {image}
        </div>
    </div>
    """

    return html_template, post_template
