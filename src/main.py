import json
from platform import *
from utils import *
import requests
import random

def print_playlist(_cdlist):
    print("\n"+"-"*30+"\n")
    print("请选出你想同步的歌单...\n")
    for _, _cd in enumerate(_cdlist):
        print("%s. %s" % (str(_+1), _cd['dissname']))
    print("\n"+"-"*30+"\n")

def print_platform(platforms, msg):
    print("\n" + "-" * 30 + "\n")
    print("请选择要%s的平台...\n"%(msg))
    for _, e in enumerate(platforms):
        print("%s. %s" % (str(_+1), e[0]))
    print("\n" + "-" * 30 + "\n")


if __name__ == '__main__':
    from all_platform import *
    share_pfs = {}
    ALL_PLATFORM = [('网易云', Music163Cls), ('QQ音乐', MusicqqCls)]

    print("\n" + "#"*50 + "\n")
    print("-"*15 +" 欢迎使用多平台歌单同步工具" + "-"*15 + "\n")
    print_platform(ALL_PLATFORM, "登录")
    while True:
        try:
            _ind = int(input("请输入序号: "))-1
            if _ind > len(ALL_PLATFORM) - 1:
                raise Exception
            break
        except:
            continue

    pf = ALL_PLATFORM[_ind][-1]()
    ALL_PLATFORM.remove(ALL_PLATFORM[_ind])
    _cdlist = pf.share()

    while len(_cdlist) > 0:
        print_playlist(_cdlist)
        try:
            _ind = int(input("请输入序号:")) - 1
            if _ind > len(_cdlist) - 1:
                raise Exception
        except:
            _ind = int(input("请输入正确序号:"))

        dissname = _cdlist[_ind]['dissname']
        songlist = pf.get_songlist_details(_cdlist[_ind].get('dissid'))

        print_platform(ALL_PLATFORM, "共享")
        while True:
            try:
                _ind = int(input("请输入序号: ")) - 1
                if _ind > len(ALL_PLATFORM)-1:
                    raise Exception
                break
            except:
                continue
        if not share_pfs.get(_ind, None):
            share_pfs[_ind] = ALL_PLATFORM[_ind][-1]()
        share_pfs[_ind].sync(dissname, songlist)

        if input('是否继续同步其他歌单(Y/y)').lower() != 'y':
            break


