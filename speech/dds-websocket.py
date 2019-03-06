#!/usr/bin/env python
import json
import time
import hmac
import asyncio
#import ssl
import websockets
from hashlib import sha1
from uuid import uuid4

alias = "test"
productId = "278579015"
deviceName = "2b6b3f8c9f02ba57f7608cea9a082b40"
audioFile = "8k.wav"
deviceSecret = 'fd6d715e975dd68fa75baec688d7a5cb'

def signature(sig_factors):
    keys = list(sig_factors.keys())
    keys.sort()
    tmp = ""
    for key in keys:
        tmp += sig_factors[key]

    print(tmp)
    hashed = hmac.new(bytes(deviceSecret, encoding = "utf-8"), bytes(tmp, encoding = "utf-8"), sha1)
    return hashed.hexdigest()
    

async def triggerIntent(ws): 
    content = {
        'topic' : 'dm.input.intent',
        'recordId' : uuid4().hex,
        'skillId' : '2018091000000010',
        'intent': '天气',
        'slots' : { 'key' : "苏州"}
    }
    try:
        await ws.send(json.dumps(content))
        resp = await ws.recv()
        print(resp)
    except websockets.exceptions.ConnectionClosed as exp:
        print(exp)

async def textRequest(ws):
    content = {
        "topic" : 'nlu.input.text',
        "recordId" : uuid4().hex,
        "refText" : "苏州的天气"
    }
    try:
        await ws.send(json.dumps(content))
        resp = await ws.recv()
        print(resp)
    except websockets.exceptions.ConnectionClosed as exp:
        print(exp)


async def audioRequest(ws):
    content = {
        "topic": "recorder.stream.start",
        "recordId": uuid4().hex,
        "audio": {
            "audioType": "wav",
            "sampleRate": 8000,
            "channel": 1,
            "sampleBytes": 2
        }
    }
    try:
        await ws.send(json.dumps(content))
        with open(audioFile, 'rb') as f:
            while True:
                chunk = f.read(3200)
                if not chunk:
                    await ws.send(bytes("", encoding = "utf-8"))
                    break
                await ws.send(chunk)
        async for message in ws:
            print(message)
            resp = json.loads(message)
            if 'dm' in resp:
                break 
    except websockets.exceptions.ConnectionClosed as exp:
        print(exp)
        ws.close()


async def dds_demo():
    nonce = uuid4().hex
    timestamp = int(time.time())
    nonce = uuid4().hex
    factors = {
        "productId" : productId,
        "deviceName": deviceName,
        "timestamp" : str(timestamp),
        "nonce" : nonce
    }
    sig = signature(factors)
    url = ("wss://dds.dui.ai/dds/v2/%s?productId=%s&deviceName=%s&nonce=%s&timestamp=%s&sig=%s&serviceType=websocket") % (alias, productId, deviceName, nonce, timestamp,sig )
    print(url)
    async with websockets.connect(url) as websocket:
        await textRequest(websocket)
        #await triggerIntent(websocket)
        #await audioRequest(websocket)


asyncio.get_event_loop().run_until_complete(dds_demo()) 