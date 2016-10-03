#-*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import json
import threading
import re
import time
import os
import requests


def makedir(path):
    path = path.strip()
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False

class PIXIV(threading.Thread):
    def __init__(self):
        self.mainpage = 'http://www.pixiv.net'
        self.bookmark = 'http://www.pixiv.net/bookmark_new_illust.php'
        self.session = requests.Session()
        self.fail_link = []
        self.path = 'D:\\downloader_pixiv'
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36",
        }

    def get_pic_type(self, real_url):  # 区分图片格式
        p_type = re.search(re.compile('png', re.S), real_url)
        if p_type == None:
            self.pic_type = 'jpg'
            return self.pic_type
        else:
            self.pic_type = 'png'

    def login_main_page(self):
        loginpage = 'http://accounts.pixiv.net/login'

        #p_id = raw_input('pixiv_id:')
        #password = raw_input('pawwword:')
        login_page_html = self.session.get(loginpage)

        self.logindata = {
            "pixiv_id": "1337939247@qq.com",
            "password": "13777gattag",
            "captcha": "",
            "g_recaptcha_response": "",
            "source": "source",
            'skip': '1',
            'mode': 'login',
        }

        #得到post_key,并设置到form data
        soup = BeautifulSoup(login_page_html.text, "lxml")
        init_config_tag = soup.find_all("input", id="init-config")[0]
        postKey = json.loads(init_config_tag.get("value"))["pixivAccount.postKey"]
        self.logindata["post_key"] =postKey

        #登陆
        res1 = self.session.post(loginpage,self.logindata,headers=self.headers)

    def get_pic_list(self, index):
        url = self.bookmark + '?p='+str(index)
        pic_ls_page =self.session.get(url)

        soup = BeautifulSoup(pic_ls_page.text,"lxml")
        pic_ls = soup.find_all("li",class_="image-item")
        pic_url_ls = []
        for url in pic_ls:
            id = re.findall('.*?id=(\d+)', url.contents[0]["href"])[0]
            append_url = self.mainpage + url.contents[0]["href"]
            pic_url_ls.append(append_url)
            pic_url_ls.append(id)
        return pic_url_ls

    def get_bookmark_pic(self,index):
        page_ls = self.get_pic_list(index)


        makedir(self.path)
        for i in range(0,len(page_ls)-1,2):
            url = page_ls[i]
            id = page_ls[i+1]
            filename = self.path + '\\'+id
            print(url,"   ",i+1)
            self.download_pic(url,id,filename)

    def download_pic(self, url, id, filename):
        headers = self.headers
        headers["Referer"] = url
        try:
            page = self.session.get(url, headers=headers)
        except:
            self.fail_link.append(url)
            self.fail_link.append(id)
            print("打开图片页面失败！！！！！！！！")
            return False
        soup = BeautifulSoup(page.text, "lxml")
        realURL = soup.find("img", attrs={"class", "original-image"})

        if(realURL):
            headers["Referer"] = realURL["data-src"]
            try:
                pictrue = self.session.get(realURL["data-src"], headers=headers)
            except:
                print("打开下载连接失败")
                return False
            self.get_pic_type(realURL["data-src"])
            filename = filename + "." + self.pic_type
            try:
                f = open(filename, "wb")
                f.write(pictrue.content)
                f.close()
                print("下载成功：",realURL["data-src"])
                return True
            except:
                print("下载失败")
                return False
        else:
            print("不是单图")
            return True

    def download_fail_pic(self):
        failLink = self.fail_link[:]
        for i in range(0, len(failLink) - 1, 2):
            url = failLink[i]
            id = failLink[i + 1]
            filename = self.path + '\\' + id
            print(url, "   ", i + 1)
            try:
                if(self.download_pic(url, id, filename)):
                    self.fail_link.remove(url)
                    self.fail_link.remove(id)
                else:
                    print("下载失败")
            except:
                print("下载失败")

pixiv = PIXIV()
pixiv.login_main_page()
for i in range(5):
    pixiv.get_bookmark_pic(i)
    time.sleep(30)
while(pixiv.fail_link):
    pixiv.download_fail_pic()
    time.sleep(30)

#<li.*?><a href="(.*?)".*?></a>.*?<a.*?>.*?</a></li>