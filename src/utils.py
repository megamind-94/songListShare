import os
import json
def isExist(filename, _make = False):
    if _make:
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
    return os.path.exists(filename)

def get_163music_p_k(params_dict):
    text = json.dumps(params_dict)
    pubKey = "010001"
    modulus = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    nonce = "0CoJUm6Qyw8W8jud"

    secKey = a(16)
    _params = aesEncrypt(aesEncrypt(text, nonce), secKey)
    _encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    return {
        'params': _params,
        'encSecKey': _encSecKey
    }


####################################################################################################################################
# 网易云音乐参数加密
def a(_a):
    _b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    _c = ""
    _d = 0
    while _a > _d:
        import random
        import math
        _e = math.floor(random.random() * len(_b))
        _c += _b[_e]
        _d += 1
    return _c

def aesEncrypt(text, secKey):
    from Crypto.Cipher import AES
    import base64
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext.decode()


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    from binascii import hexlify
    rs = int(hexlify(text.encode()), 16)**int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

