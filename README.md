# QZoneMemo
## 介绍

***QZoneMemo*** : 获取QQ空间发布的历史说说/动态/转发/好友评论 (包括已删除的动态)

![QzoneMemo-Screen](assests\qzonememo_screen.png)

## 准备工作 

### 1. 创建虚拟环境

创建内置Python 3.9的conda虚拟环境, 然后激活该环境.

```shell
conda create -n qzonememo python=3.9
conda activate qzonememo
```

### 2. 安装依赖包

切换到QZoneMemo程序所在的路径

```shell
cd {QZoneMemo程序所在的路径}
```

安装程序所需要的依赖包

```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 运行程序

``` python
python main.py
```

## 框架

[![Python](https://img.shields.io/badge/python-3776ab?style=for-the-badge&logo=python&logoColor=ffd343)](https://www.python.org/)[![Static Badge](https://img.shields.io/badge/Pyside6-test?style=for-the-badge&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html)

## 参考

[GetQzonehistory](https://github.com/LibraHp/GetQzonehistory)

[PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)

