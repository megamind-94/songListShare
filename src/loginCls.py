import os
import requests
import sys
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse
import re
from requests.cookies import RequestsCookieJar
import json

class WechatLoginCls():

    def __init__(self, url):
        self._headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"}
        self._session = requests.Session()
        self._url = url
        self._redict_url = ""
        self._uuid = ""
        self._appid = ""
        self._checkToken = ""
        self._state = ""
        self._scope = ""
        self.QRImgPath = os.path.join(os.path.dirname(__file__), ".tmp", "tmp-wechat.png")
        self._uuid = ""
        self._code = ""
        self._uid = ""
        self._cookies = RequestsCookieJar()
        if not os.path.exists(os.path.dirname(self.QRImgPath)) or not os.path.isdir(os.path.dirname(self.QRImgPath)):
            os.makedirs(os.path.dirname(self.QRImgPath))

        # 初始化参数
        self._get_init_args()

    def _get_init_args(self):
        # _response = requests.get(self._url)
        _response = self._session.get(self._url, verify=False, hooks=dict(response=self._hook))
        if _response.status_code != 200:
            sys.exit("\n请输入正确的url地址\n")
        _soup = BS(_response.content, 'html.parser')
        _img_sel = _soup.select('img.qrcode.lightBorder')
        if len(_img_sel) < 1:
            sys.exit("\n没有找到二维码，请输入确认输入的url是跳转至微信授权登录\n")
        else:
            _img_sel = _img_sel[0]

        self._uuid = _img_sel.attrs['src'].split("/")[-1]
        _redict_url = re.findall(r'[&]?redirect_uri=([^&#]+)', urlparse(_response.url).query)
        if len(_redict_url) > 0:
            self._redict_url = _redict_url[0]
        _state = re.findall(r'[&]?state=([^&#]+)', urlparse(_response.url).query)
        if len(_state) > 0:
            self._state = _state[0]

        urlbase = urlparse(_response.url)
        # imghtml = requests.get(urlbase.scheme + "://" + urlbase.netloc + _img_sel.attrs['src'])
        imghtml = self._session.get(urlbase.scheme + "://" + urlbase.netloc + _img_sel.attrs['src'], verify=False, hooks=dict(response=self._hook))
        with open(self.QRImgPath, 'wb') as f:
            f.write(imghtml.content)
            f.flush()
        self.showQRImg()

    def login(self):
        pass

    def _get_login_chk(self):
        import time
        _chk_url = "https://long.open.weixin.qq.com/connect/l/qrconnect?uuid={uuid}&_={_}".format(
            uuid=self._uuid,
            _=int(time.time())
        )
        # _response = requests.get(_chk_url)
        _response = self._session.get(_chk_url, verify=False)

        if _response.status_code == 200:
            _code = re.findall(r'wx_errcode=([0-9]+)', _response.content.decode("utf8"))
            if len(_code) > 0:
                if _code[0] == '405':
                    print("\n微信登录成功\n")
                    self._code = re.findall(r'wx_code=\'(.+)\';', _response.content.decode("utf8"))[0]
                    return True
                elif _code[0] == '408':
                    print("\n等待微信授权...\n")
                elif _code[0] == '402':
                    print("\n微信二维码已过期，重新请求二维码...\n")
                    self._get_init_args()
        return False

    def showQRImg(self):
        from PIL import Image
        im = Image.open(self.QRImgPath)
        im.show()
        print("\n请扫描二维码...\n")

    # 因为登录链接有重定向行为，cookies在请求返回(新地址)中不存在，所以需要用hook监控请求过程（直接请求&重定向）
    def _hook(self, rsp, **kwargs):
        from requests.sessions import merge_cookies
        self._cookies = merge_cookies(rsp.cookies, self._cookies)

    def test_hook(self, rsp, **kwargs):
        import pdb;pdb.set_trace();

if __name__ == '__main__':
    wechatlogin = WechatLoginCls('https://music.163.com/api/sns/authorize?snsType=10&clientType=web2&callbackType=Login&forcelogin=true')
    wechatlogin.login()
