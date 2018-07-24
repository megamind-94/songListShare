from loginCls import WechatLoginCls
import re
from tqdm import tqdm
import random
from utils import *

# 网易云音乐
class Music163Cls(WechatLoginCls):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    }

    def __init__(self):
        url = 'https://open.weixin.qq.com/connect/qrconnect?appid=wxe280063f5fb2528a&response_type=code&redirect_uri=https://music.163.com/back/weichat&forcelogin=true&scope=snsapi_login&state=YGMoimgMhm&checkToken=9ca17ae2e6ffcda170e2e6eea9ee399aeb83d2f54ea6b8bdd7b12598eca499c1609ae8fb9bc44983e79accc62af0feaec3b92af7b79e8faa3caa90a3a8bb4b969c9aafcb809690e1adaa428a8aabaab64ea18deecda180e2e6eea9d43cf6b7a582bc5aed9d9db3c639aa8b85a6cb6193e3f3c300&lang=zh_CN'
        super(Music163Cls, self).__init__(url)

        self._csrf = None
        self._cookies_dict = None
        self._share_list = []
        self._user_playlist = []
        self._pid = None

        self._login()


    def _login(self):
        while not self._get_login_chk():
            continue
        if self._redict_url != '' and self._code != '' and self._state != '':
            _response = self._session.get(self._redict_url, params={'code': self._code, 'state': self._state}, headers=self._headers, verify=False, hooks=dict(response=self._hook))
            if _response.status_code == 200 and len(self._cookies) > 0:
                try:
                    _data = json.loads(_response.content.decode('utf8'))
                except:
                    _data = {}
                self._uid = _data.get("account", dict()).get("id", "")
                self._cookies_dict = self._cookies.get_dict()
                self._csrf = self._cookies_dict.get('__csrf')
                self._get_user_createdlist()

        else:
            print('\n初始化失败\n')


    def _get_favorlist(self):
        params_dict = {
            'csrf_token': self._csrf,
            'limit': '1001',
            'offset': '0',
            'uid': self._uid
        }
        p_k_dict = get_163music_p_k(params_dict)
        _rsp = self._session.post("https://music.163.com/weapi/user/playlist?csrf_token=%s" % (self._csrf), data=p_k_dict,
                             headers=Music163Cls.HEADERS)

        content = json.loads(_rsp.content.decode())
        if content.get('code', -1) == 200 or len(content.get('playlist', [])) > 0:
            for _, _cd in enumerate(content.get('playlist')):
                if _cd.get('userId') != self._uid:
                    self._share_list.append({
                        'dissid': _cd.get('id'),
                        'dissname': _cd.get('name'),
                        'logo': _cd.get('coverImgUrl')
                    })
        else:
            print('\n没能获取到用户收藏的歌单...\n')

    def _get_user_createdlist(self):
        params_dict = {
            'csrf_token': self._csrf,
            'limit': '1001',
            'offset': '0',
            'uid': self._uid
        }
        p_k_dict = get_163music_p_k(params_dict)
        _rsp = self._session.post("https://music.163.com/weapi/user/playlist?csrf_token=%s" % (self._csrf),
                                  data=p_k_dict,
                                  headers=Music163Cls.HEADERS)

        content = json.loads(_rsp.content.decode())
        if content.get('code', -1) == 200 or len(content.get('playlist', [])) > 0:
            for _, _cd in enumerate(content.get('playlist')):
                if _cd.get('userId') == self._uid:
                    self._user_playlist.append({
                        'dissid': _cd.get('id'),
                        'dissname': _cd.get('name'),
                        'logo': _cd.get('coverImgUrl')
                    })
        else:
            print('\n没能获取到用户个人歌单...\n')


    def get_songlist_details(self, music_id):
        params_dict = {
            'csrf_token': self._csrf,
            'id': music_id,
            'limit': '1000',
            'n': '1000',
            'offset': '0',
            'total': 'true'
        }
        p_k_dict = get_163music_p_k(params_dict)
        _rsp = self._session.post("https://music.163.com/weapi/v3/playlist/detail?csrf_token=%s" % (self._csrf),
                             data=p_k_dict,
                             headers=Music163Cls.HEADERS)

        content = json.loads(_rsp.content.decode())
        if content['code'] == 200:
            songlist = []
            for _, songinfo in enumerate(content['playlist']['tracks']):
                songlist.append(
                    {
                        'songname': songinfo['name'],
                        'singer': " ".join([_i['name'] for _i in songinfo['ar']])
                    }
                )
            return songlist
        else:
            return []


    def _create_playlist(self, name):
        params_dict = {
            'csrf_token': self._csrf,
            'name': name
        }
        p_k_dict = get_163music_p_k(params_dict)
        _rsp = self._session.post("https://music.163.com/weapi/playlist/create?csrf_token=%s" % (self._csrf), data=p_k_dict,
                             headers=Music163Cls.HEADERS, cookies=self._cookies_dict)
        content = json.loads(_rsp.content.decode())
        if content['code'] == 200:
            return content['id']
        else:
            return False

    def _song_search(self, s):
        # params_dict = {
        #     's': s,
        #     'csrf_token': self._csrf
        # }
        params_dict = {
            'csrf_token': self._csrf,
            'hlposttag': "</span>",
            'hlpretag': "<span class='s - fc7'>",
            'id':"1370259035",
            'limit':"30",
            'offset':"0",
            's': s,
            'total': "true",
            'type':"1"
        }
        p_k_dict = get_163music_p_k(params_dict)
        _rsp = self._session.post("https://music.163.com/weapi/cloudsearch/get/web?csrf_token=%s" % (self._csrf),
                             data=p_k_dict,
                             headers=Music163Cls.HEADERS)

        content = json.loads(_rsp.content.decode())
        if content['code'] == 200 and len(content['result']) > 0:
            return content['result']['songs'][0]['id']
        else:
            print("![关键字 - %s 搜不到结果]")
            return None

    def _add_song2createdlist(self, song_id, pid):
        params_dict = {
            'csrf_token': self._csrf,
            'op': "add",
            'pid': pid,
            'trackIds': "[%s]" % (song_id),
            'tracks': "[object Object]"
        }
        p_k_dict = get_163music_p_k(params_dict)
        _rsp = self._session.post("https://music.163.com/weapi/playlist/manipulate/tracks?csrf_token=%s" % (self._csrf),
                             data=p_k_dict,
                             headers=Music163Cls.HEADERS)

        content = json.loads(_rsp.content.decode())
        if content.get('code', -1) == 200:
            return True
        else:
            return False

    def share(self):

        if len(self._share_list) == 0:
            self._get_favorlist()

        if len(self._share_list) == 0:
            print('\n您没有收藏任何歌单...\n')
        else:
            return self._share_list

    def sync(self, dissname, songlist):
        count = 0
        if dissname not in self._user_playlist:
            dirid =  self._create_playlist(dissname)
            if not dirid:
                print("\n" + "#" * 50 + "\n无法创建歌单-%s\n" % (dissname) + "#" * 50 + "\n")
                return
            for songinfo in tqdm(songlist):
                if self._add_song2createdlist(dirid, self._song_search(songinfo['songname'][:10] + " " + songinfo['singer'])):
                    count += 1
            print("歌单[%s]已同步完成，共添加了%s首歌..."%(dissname, str(count)))
        else:
            print("\n歌单[%s]已存在...\n"%(dissname))


class MusicqqCls(WechatLoginCls):

    HEADERS = {
        "referer": "https://y.qq.com/portal/profile.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    }
    
    def __init__(self):
        from urllib.parse import unquote
        _url = unquote(
            'https://open.weixin.qq.com/connect/qrconnect?appid=wx48db31d50e334801&redirect_uri=https%3A%2F%2Fy.qq.com%2Fportal%2Fwx_redirect.html%3Flogin_type%3D2%26surl%3Dhttps%3A%2F%2Fy.qq.com%2F&response_type=code&scope=snsapi_login&state=STATE&href=https%3A%2F%2Fy.gtimg.cn%2Fmediastyle%2Fyqq%2Fpopup_wechat.css'
        )
        super(MusicqqCls, self).__init__(_url)

        self._cookies_dict = None
        self._uin = None
        self._share_list = []
        self._user_playlist = []

        self._login()

    def _login(self):
        import random
        while not self._get_login_chk():
            continue
        if self._redict_url != '' and self._code != '' and self._state != '':
            self._headers['referer'] = self._redict_url + "&surl=https://y.qq.com/"
            _rsp = self._session.get('https://c.y.qq.com/base/fcgi-bin/h5_login_wx_get_musickey.fcg?wxcode=' + self._code + '&appid=wx48db31d50e334801&jsonpCallback=' + str(random.random()).replace('0.', ''),
                                     headers=self._headers)
            # content = json.loads(re.findall(r'\(([^\)]+)',_rsp.content.decode())[0])

            self._cookies_dict = _rsp.cookies.get_dict()
            self._uin = self._cookies_dict.get("wxuin", "").replace("o", "")
            if self._uin != "":
                self._cookies_dict.update(dict(login_type="2"))
                self._get_user_createdlist()

    def _create_playlist(self, name):
        params = {
            "loginUin": self._uin,
            "HostUin": "0",
            "format": "fs",
            "inCharset": "GB2312",
            "outCharset": "utf8",
            "notice": "0",
            "platform": "yqq",
            "needNewCode": "0",
            "g_tk": "5381",
            "uin": self._uin,
            "name": name,
            "description": "",
            "show": "1",
            "pic_url": "",
            "tags": "",
            "tagids": "",
            "formsender": "1",
            "utf8": "1",
            "qzrefererrer": "https://y.qq.com/portal/profile.html#sub=other&tab=create&"
        }

        _rsp = self._session.post("https://c.y.qq.com/splcloud/fcgi-bin/create_playlist.fcg?g_tk=5381", data=params,
                             headers=MusicqqCls.HEADERS, cookies=self._cookies_dict)

        result = json.loads(re.findall(r'back\(([^\);]+)', _rsp.content.decode())[0].replace('code:','"code":').replace('msg','"msg"').replace('dirid', '"dirid"').replace('\'','"'))
        if result['code'] == 0:
            self._user_playlist.append(name)
            return result['dirid']
        else:
            return False

    def _get_favorlist(self):
        _rsp = self._session.get(
            "https://c.y.qq.com/fav/fcgi-bin/fcg_get_profile_order_asset.fcg?g_tk=5381&jsonpCallback={jsonpcallback}&loginUin={loginUin}&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&ct=20&cid=205360956&userid={userid}&reqtype=3&sin=0&ein=200".format(
                jsonpcallback="MusicJsonCallback" + str(random.random()).replace('0.', '')[:16],
                # jsonpcallback='5284310121355209',
                loginUin=self._uin,
                userid=self._uin
            ),
            headers=MusicqqCls.HEADERS
        )
        content = json.loads(re.findall(r'\(([^\)]+)', _rsp.content.decode())[0])
        if content.get('code', -1) == 0 or len(content.get('data', {})) > 0:
            for _, _cd in enumerate(content.get('data').get('cdlist', [])):
                self._share_list.append({
                    'dissid': _cd.get('dissid'),
                    'dissname': _cd.get('dissname'),
                    'logo': _cd.get('logo')
                })
        else:
            print('\n没能获取到用户收藏的歌单...\n')

    def _get_user_createdlist(self):
        import time
        _rsp = self._session.get(
            "https://c.y.qq.com/rsc/fcgi-bin/fcg_user_created_diss?hostuin={hostuin}&sin=0&size=32&r={r}&g_tk=5381&jsonpCallback=MusicJsonCallback{jsoncallback}&loginUin={loginUin}&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0".format(
                hostuin=self._uin,
                r=str(int(time.time() * 1000)),
                jsoncallback="MusicJsonCallback" + str(random.random()).replace('0.', ''),
                loginUin=self._uin
            ),
            headers=MusicqqCls.HEADERS
        )
        content = json.loads(re.findall(r'\(([^\)]+)', _rsp.content.decode())[0])
        if content.get('code', -1) == 0 or len(content.get('data', {})) > 0:
            for diss in content.get('data').get('disslist', []):
                self._user_playlist.append(diss.get('diss_name'))
        else:
            print('\n没能获取到用户个人歌单...\n')


    def _add_song2createdlist(self, dirid, mid):
        params = {
            "loginUin": self._uin,
            "hostUin": "0",
            "format": "json",
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "notice": "0",
            "platform": "yqq.post",
            "needNewCode": "0",
            "uin": self._uin,
            "midlist": mid,
            "typelist": "13",
            "dirid": dirid,
            "addtype": "",
            "formsender": "4",
            "source": "153",
            "r2": "0",
            "r3": "1",
            "utf8": "1",
            "g_tk": "5381"

        }
        _rsp = self._session.post("https://c.y.qq.com/splcloud/fcgi-bin/fcg_music_add2songdir.fcg?g_tk=5381", data=params,
                             headers=MusicqqCls.HEADERS, cookies=self._cookies_dict)
        try:
            content = json.loads(_rsp.text)
            _code = content.get('code', -1)
        except:
            _code = -1
        if _code == 0:
            return True
        else:
            return False

    def _song_search(self, k):
        jsoncallback = "MusicJsonCallback%s" % (str(random.random()).replace('0.', ''))
        _rsp = self._session.get(
            "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.center&searchid=52351807424062653&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n={limit}&w={k}&g_tk=5381&jsonpCallback={jsonpcallback}&loginUin={loginUin}&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0".format(
                k=k,
                jsonpcallback=jsoncallback,
                loginUin=self._uin,
                limit='100'
            ),
            headers=MusicqqCls.HEADERS
        )
        try:
            content = json.loads(_rsp.content.decode().replace(jsoncallback+'(', '').rsplit(')', maxsplit=1)[0])
            return content['data']['song']['list'][0]['mid']
        except:
            return None


    def get_songlist_details(self, dissid):
        _rsp = self._session.get(
            'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&disstid={disstid}&format=jsonp&g_tk=5381&jsonpCallback=playlistinfoCallback&loginUin={loginUin}&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(
                disstid=dissid,
                loginUin=self._uin
            ),
            headers=MusicqqCls.HEADERS
        )
        result = json.loads(_rsp.content.decode().rsplit(')', maxsplit=1)[0].replace('playlistinfoCallback(', ''))
        if result['code'] == 0:
            songlist = []
            for _, songinfo in enumerate(result['cdlist'][0]['songlist']):
                songlist.append(
                    {
                        'songname': songinfo['songname'],
                        'singer': " ".join([_i['name'] for _i in songinfo['singer']])
                    }
                )
            return songlist
        else:
            return []


    def share(self):

        if len(self._share_list) == 0:
            self._get_favorlist()

        if len(self._share_list) == 0:
            print('\n您没有收藏任何歌单...\n')
        else:
            return self._share_list


    def sync(self, dissname, songlist):
        count = 0
        if dissname not in self._user_playlist:
            dirid = self._create_playlist(dissname)
            if not dirid:
                print("\n" + "#" * 50 + "\n无法创建歌单-%s\n" % (dissname) + "#" * 50 + "\n")
                return
            for songinfo in tqdm(songlist):
                if self._add_song2createdlist(dirid, self._song_search(songinfo['songname'][:10] + ' ' + songinfo['singer'])):
                    count += 1
            print("歌单[%s]已同步完成，共添加了%s首歌..."%(dissname, str(count)))
        else:
            print("\n歌单[%s]已存在...\n"%(dissname))




