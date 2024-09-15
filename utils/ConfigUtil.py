import os
import yaml

CONFIG_PATH = 'config/config.yaml'


class ConfigUtil:
    def __init__(self, config_path=CONFIG_PATH):
        # 初始化配置文件
        self.config = self.read_yaml(config_path)

        # 获取路径配置
        self.temp_path = self.config['temp']
        self.user_path = self.config['user']
        self.result_path = self.config['result']
        self.fetch_all_path = self.config['fetch-all']
        # 初始化文件夹
        self.init_folders()

    # 读取 YAML 文件
    def read_yaml(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config

    def init_folders(self):
        # 初始化temp文件夹
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)
            print(f"Created directory: {self.temp_path}")

        # 初始化user文件夹
        if not os.path.exists(self.user_path):
            os.makedirs(self.user_path)
            print(f"Created directory: {self.user_path}")

        # 初始化result文件夹
        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)
            print(f"Created directory: {self.result_path}")

        # 初始化fetch-all文件夹
        if not os.path.exists(self.fetch_all_path):
            os.makedirs(self.fetch_all_path)
            print(f"Created directory: {self.fetch_all_path}")

    def save_user(self, cookies):
        # 保存用户的cookies
        with open(os.path.join(self.user_path, cookies.get('uin')), 'w') as f:
            f.write(str(cookies))

    def get_local_user(self):
        # 获取本地已登录用户
        files = os.listdir(self.user_path)
        if not files or len(files) == 0:
            return None
        file_path = os.path.join(self.user_path, files[0])
        with open(file_path, 'r') as file:
            content = file.read()
        return eval(content)
