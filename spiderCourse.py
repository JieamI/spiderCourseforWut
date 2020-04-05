import requests
import execjs
from bs4 import BeautifulSoup

class SpiderCourse():
    # 初始化
    def __init__(self, usr, pwd):
        self.url = 'http://202.114.50.129/Certification/login.do'
        self.datas = {'userName1': execjs.compile(open(r"md5.js").read()).call('hex_md5', usr),
                      'password1': execjs.compile(open(r"sha1.js").read()).call('hex_sha1', usr + pwd),
                      'webfinger': 'ec198773ef514e44ed8cbf9ef7a114e7',
                      'type': 'xs',     #身份认证为学生
                      'userName': usr,
                      'password': pwd
                    } 
                                      
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    # 网页解析
    def SoupParse(self):
        # 由浏览器指纹获取code
        fp = requests.post(url = "http://sso.jwc.whut.edu.cn/Certification/getCode.do", data = {'webfinger': self.datas['webfinger']})
        self.datas['code'] = fp.content.decode('utf-8') 
        html = requests.post(self.url, data = self.datas,headers = self.header)
        soup = BeautifulSoup(html.content, "lxml")
        course = soup.select_one(".table-class-even")
        self.res=[[],[],[],[],[]]
        index = 0
        for each in course.find_all('tr',recursive=False):
            for child in each.find_all('td',{'style':'text-align: center'},recursive=False,limit=7):
                temp_blue = child.find('div',{'style':'margin-top: 2px; font-size: 10px; color: blue'})
                temp_red = child.find('div',{'style':'margin-top: 2px; font-size: 10px; color: red'}) 
                if temp_blue or temp_red:
                    if temp_blue:
                        self.res[index].append(temp_blue.get_text().strip().replace('\t','').replace('\r', '').replace('\n', ''))
                    else:
                        self.res[index].append(temp_red.get_text().strip().replace('\t','').replace('\r', '').replace('\n', ''))
                else:
                    self.res[index].append("")
            index = index+1