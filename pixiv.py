# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import json
import threading
import re
import time
import os
import requests
import sys


def makedir(path):
    path = path.strip()
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        print(path + " has created")
        return True
    else:
        print(path + " has exists")
        return False


class Pixiv(threading.Thread):
    def __init__(self, pixiv_id, password):

        self.mainpage = 'http://www.pixiv.net'
        self.bookmark = 'http://www.pixiv.net/bookmark_new_illust.php'
        self.session = requests.Session()
        self.fail_link = []
        self.fail_link_id = []
        self.pixiv_id = pixiv_id
        self.password = password
        self.path = 'D:\\downloader_pixiv'
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": """Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3076.0 Safari/537.36"""
        }

    def login_main_page(self):
        loginpage = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'

        login_page_html = self.session.get(loginpage)
        self.logindata = dict(captcha="", g_recaptcha_response="", source="pc", ref="wwwtop_accounts_index")
        self.logindata["pixiv_id"] = self.pixiv_id
        self.logindata["password"] = self.password

        # 得到post_key,并设置到form data
        soup = BeautifulSoup(login_page_html.text, "lxml")
        init_config_tag = soup.find_all("input", id="init-config")[0]
        postKey = json.loads(init_config_tag.get("value"))["pixivAccount.postKey"]
        self.logindata["post_key"] = postKey

        # 登陆
        res1 = self.session.post(loginpage, self.logindata, headers=self.headers)

        file = open("pixiv-1.html", 'wb')
        file.write(res1.text.encode())
        file.close()

    def get_pic_type(self, real_url):  # 区分图片格式
        p_type = re.search(re.compile('png', re.S), real_url)
        if p_type == None:
            self.pic_type = 'jpg'
            return self.pic_type
        else:
            self.pic_type = 'png'

    def get_pic_list(self, index):
        url = self.bookmark + '?p=' + str(index)
        pic_ls_page = self.session.get(url)

        soup = BeautifulSoup(pic_ls_page.text, "lxml")
        pic_element_ls = soup.find_all("li", class_="image-item")
        pic_url_ls = []
        pic_id_ls = []
        for element in pic_element_ls:
            pic_id = re.findall('.*?id=(\d+)', element.contents[0]["href"])[0]
            append_url = self.mainpage + element.contents[0]["href"]
            pic_url_ls.append(append_url)
            pic_id_ls.append(pic_id)
        result = [pic_url_ls, pic_id_ls]
        return result

    def get_bookmark_pic(self, index):
        targets = self.get_pic_list(index)

        pic_num = len(targets[0])
        makedir(self.path)
        for i in range(0, pic_num - 1):
            url = targets[0][i]
            pic_id = targets[1][i]
            # filename = self.path + '\\'+ id
            print(url, "  ", i + 1)
            self.download_pic(url, pic_id)

    def download_pic(self, url, pic_id):
        headers = self.headers
        headers["Referer"] = url
        try:
            page = self.session.get(url, headers=headers)
        except:
            self.fail_link.append(url)
            self.fail_link_id.append(pic_id)
            print("打开图片页面失败！！！！！！！！")
            return False
        soup = BeautifulSoup(page.text, "lxml")
        artest = soup.find_all("h1", class_="user")[0].get_text()
        file_path = self.path + '\\' + artest
        makedir(file_path)

        realURL = soup.find("img", attrs={"class", "original-image"})
        if realURL:
            headers["Referer"] = realURL["data-src"]
            try:
                pictrue = self.session.get(realURL["data-src"], headers=headers)
            except:
                print("打开下载连接失败")
                return False
            self.get_pic_type(realURL["data-src"])
            title = realURL["alt"]
            filename = file_path + "\\" + title + pic_id + "." + self.pic_type
            try:
                f = open(filename, "wb")
                f.write(pictrue.content)
                f.close()
                print("下载成功：", realURL["data-src"])
                return True
            except:
                print("下载失败")
                return False
        else:
            print("不是单图")
            return True

    def download_fail_pic(self):
        for i in range(0, len(self.fail_link) - 1):
            url = self.fail_link[i]
            pic_id = self.fail_link_id[i]
            try:
                self.download_pic(url, pic_id)
                self.fail_link.remove(self.fail_link[i])
                self.fail_link_id.remove(self.fail_link_id[i])
            except:
                print("下载失败")

page_begin = int(sys.argv[1])
page_end = int(sys.argv[2])
# print(page_begin)
# print(type(int(page_begin)))
pixiv = Pixiv("your account", "your password")
pixiv.login_main_page()
# pixiv.get_bookmark_pic(6)
for i in range(page_begin, page_end):
    pixiv.get_bookmark_pic(i)
    time.sleep(30)
while pixiv.fail_link:
    pixiv.download_fail_pic()
    time.sleep(30)


