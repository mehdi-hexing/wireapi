from flask import Flask, request
import requests
import json
import os
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519

app = Flask(__name__)

def byte_to_base64(myb):
    return base64.b64encode(myb).decode('utf-8')
   
def generate_public_key(key_bytes):
    private_key = x25519.X25519PrivateKey.from_private_bytes(key_bytes)
    public_key = private_key.public_key()
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )  
    return public_key_bytes

def generate_private_key():
    key = os.urandom(32)  
    key = list(key)
    key[0] &= 248
    key[31] &= 127
    key[31] |= 64  
    return bytes(key)

def register_key_on_CF(pub_key):
    url = 'https://api.cloudflareclient.com/v0a4005/reg'

    body = {
        "key": pub_key,
        "install_id": "",
        "fcm_token": "",
        "warp_enabled": True,
        "tos": datetime.datetime.now().isoformat()[:-3] + "+07:00",
        "type": "Android",
        "model": "PC",
        "locale": "en_US"
    }

    bodyString = json.dumps(body)

    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'api.cloudflareclient.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.12.1',
        "CF-Client-Version": "a-6.30-3596"
    }

    r = requests.post(url, data=bodyString, headers=headers, timeout=10)
    return r

def bind_keys():
    priv_bytes = generate_private_key()
    priv_string = byte_to_base64(priv_bytes)

    pub_bytes = generate_public_key(priv_bytes)
    pub_string = byte_to_base64(pub_bytes)

    result = register_key_on_CF(pub_string)

    z = json.loads(result.content)
    client_id = z['config']["client_id"]   
    cid_byte = base64.b64decode(client_id)
    
    # حذف بخش reserved
    return f"private_key: {priv_string}\npublic_key: {pub_string}\n"

def get_key():
    data = bind_keys()
    return data

@app.route("/arshiacomplus/api/wirekey")
def replace1():
    return get_key()

@app.route("/")
def replace():
    return get_key()
