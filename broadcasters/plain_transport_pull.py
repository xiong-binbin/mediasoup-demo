# coding=UTF-8
from __future__ import print_function
import os
import json
import requests


verify = True
room_id = "gjopbvp4"
broadcaster_id = "Ty3kTxlh0CU9xvCYac25K95tjFOk"
url = "https://xiongbinbin.club:4443/rooms/"
head = {'Content-Type': 'application/json'}

audio_pt = 100
video_pt = 105
audio_ssrc = 1111
video_ssrc = 2222
audio_consumer_port = 28962
video_consumer_port = 45698
audio_consumer_rtcp_port = 28963
video_consumer_rtcp_port = 45699
audio_consumer_ip = '127.0.0.1'
video_consumer_ip = '127.0.0.1'

audio_producer_id = "87a54493-78c6-4f1c-8e45-d744bc7d69ae"
video_producer_id = "e2dc02cd-8647-4c2b-8282-ea0f965db2b4"

#判断房间号是否存在
response = requests.get(url + room_id, verify=verify)
if response.status_code != 200:
    print(response.text)
    exit()

#创建audio PlainTransport
body = json.dumps({'type': 'plain', 'comedia': False, 'rtcpMux': False})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports", data=body, headers=head, verify=verify)
text = json.loads(response.text)
audio_transport_id = text['id']
audio_transport_ip = text['ip']
audio_transport_port = text['port']
audio_transport_rtcp_port = text['rtcpPort']

#创建video PlainTransport
body = json.dumps({'type': 'plain', 'comedia': False, 'rtcpMux': False})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports", data=body, headers=head, verify=verify)
text = json.loads(response.text)
video_transport_id = text['id']
video_transport_ip = text['ip']
video_transport_port = text['port']
video_transport_rtcp_port = text['rtcpPort']

#连接audio PlainTransport
body = json.dumps({'ip': audio_consumer_ip, 'port': audio_consumer_port, 'rtcpPort': audio_consumer_rtcp_port})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/plainTransports/" + audio_transport_id + "/connect", data=body, headers=head, verify=verify)
print("connect audio PlainTransport:" + response.text)

#连接video PlainTransport
body = json.dumps({'ip': video_consumer_ip, 'port': video_consumer_port, 'rtcpPort': video_consumer_rtcp_port})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/plainTransports/" + video_transport_id + "/connect", data=body, headers=head, verify=verify)
print("connect video PlainTransport:" + response.text)

#创建audio Consumer
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports/" + audio_transport_id + "/consume?producerId=" + audio_producer_id, verify=verify)
print("audio Consumer:" + response.text)

#创建video Consumer
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports/" + video_transport_id + "/consume?producerId=" + video_producer_id, verify=verify)
print("video Consumer:" + response.text)


'''
h264.sdp文件内容如下：

v=0
o=- 0 0 IN IP4 127.0.0.1
s=-
c=IN IP4 127.0.0.1
t=0 0
m=audio 28962 RTP/AVPF 100
a=rtcp:28963
a=rtpmap:100 opus/48000/2
a=fmtp:100 sprop-stereo=1
m=video 45698 RTP/AVPF 105
a=rtcp:45699
a=rtpmap:105 H264/90000
a=fmtp:105 level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=4d0032

FFmpeg拉流命令：
ffmpeg -loglevel debug -protocol_whitelist file,rtp,udp -i h264.sdp -vcodec copy -acodec aac out.mp4

'''
