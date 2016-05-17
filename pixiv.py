#-*- coding: UTF-8 -*-

import urllib2
import urllib
import cookielib
import re



class PIXIV:
    def __init__(self):
        self.filename = 'cookie.txt'
        self.mainpage = 'http://www.pixiv.net'
        self.piclist = 'http://www.pixiv.net/bookmark_new_illust.php'

    def Cookie_Login(self):  # 读取之前登陆生成的cookie
        cookie_login = cookielib.MozillaCookieJar()
        cookie_login.load('cookie.txt', ignore_discard=True, ignore_expires=True)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_login))
        return opener

    def login_main_page(self):
        loginpage = 'https://www.pixiv.net/login.php'

        p_id = raw_input('pixiv_id:')
        password = raw_input('pawwword:')

        self.logindata = {
            'mode': 'login',
            'return_to': '/',
            'pixiv_id': '',#p站用户名
            'pass': '',#p站密码
            'skip': 1
        }
        self.logindata['pixiv_id']=p_id
        self.logindata['pass']=password
        self.p_login_data=urllib.urlencode(self.logindata)
        self.p_login_header = {  # 头信息
            'accept-language': 'zh-CN,zh;q=0.8',
            'origin':'http://www.pixiv.net',
            'referer': 'http://www.pixiv.net/',
            'upgrade - insecure - requests': 1,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/50.0.2661.102 Safari/537.36'
        }
        login = urllib2.Request(
            url=loginpage,
            data=self.p_login_data,
            headers=self.p_login_header
        )
        try:
            self.cookies = cookielib.MozillaCookieJar(self.filename)
            self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
            self.opener.open(login)
            self.cookies.save(ignore_discard=True, ignore_expires=True)

        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print '登录失败？？？',e.reason

    def get_pic_list(self, index):
        url = self.piclist + '?p='+str(index)
        request = urllib2.Request(url)
        response = self.opener.open(request)
        page = response.read()
        pic_ls = re.findall('<li class="image-item"><a href="(.*?)".*?></a>.*?<a.*?>.*?</a></li>', page)
        pic_url_ls = []
        for picurl in pic_ls:
            pic_url = self.mainpage + picurl
            pic_url_ls.append(pic_url)
            #print pic_url
        return pic_url_ls

    def get_pic(self,index):
        page_ls = self.get_pic_list(index)
        num = 1
        for p in page_ls:
            id=re.findall('h.*?id=(\d+)',p)
            page = self.opener.open(p).read()
            pic = re.findall('<div class="wrapper">.*?<img.*?data-src="(.*?)".*?>.*?</div>',page)
            path = 'D:\\downloader_p\\'
            filename = path + id[0] + '_' + str(num)+'.jpg'
            print filename
            if pic:
                self.saveImage(filename, pic[0],p)
            num+=1

    def saveImage(self,filename,imageurl,page):

        f = open(filename, 'wb')
        f.write(self.downLoadPic(page ,imageurl))
        f.close()

    def downLoadPic(self, make_url, real_url):
        head = {
            'Referer': '',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/50.0.2661.102 Safari/537.36',
            'accept-language': 'zh-CN,zh;q=0.8',
        }
        head['Referer'] = make_url

        request = urllib2.Request(
            url=real_url,
            headers=head
        )
        decode_url = self.opener.open(request)
        return decode_url.read()





pixiv = PIXIV()
pixiv.login_main_page()
pixiv.get_pic(2)

#<li.*?><a href="(.*?)".*?></a>.*?<a.*?>.*?</a></li>