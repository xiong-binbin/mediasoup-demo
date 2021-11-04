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

fd = open('debug.txt', 'w+')

#判断房间号是否存在
response = requests.get(url + room_id, verify=verify)
if response.status_code != 200:
    print(response.text)
    exit()

#创建Broadcaster
rtpCapabilities = {
    "codecs":[
        {
            "mimeType": "audio/opus",
            "kind": "audio",
            "preferredPayloadType": 100,
            "clockRate": 48000,
            "channels": 2,
            "parameters": {
                "sprop-stereo": 1
            },
            "rtcpFeedback": []
        },
        {
            "mimeType": "video/H264",
            "kind": "video",
            "preferredPayloadType": 105,
            "clockRate": 90000,
            "parameters": {
                "packetization-mode": 1,
                "level-asymmetry-allowed": 1,
                "profile-level-id": "4d0032",
                "x-google-start-bitrate": 1000
            },
            "rtcpFeedback": []
        }
    ],

    "headerExtensions": [
        {
            "kind": "audio",
            "uri": "urn:ietf:params:rtp-hdrext:sdes:mid",
            "preferredId": 1,
            "preferredEncrypt": False,
            "direction": "sendrecv"
        },
        {
            "kind": "video",
            "uri": "urn:ietf:params:rtp-hdrext:sdes:mid",
            "preferredId": 1,
            "preferredEncrypt": False,
            "direction": "sendrecv"
        }
    ]
}
body = json.dumps({'id': broadcaster_id, 'displayName': 'Broadcaster', 'device': {'name': 'FFmpeg'}, 'rtpCapabilities': rtpCapabilities})
response = requests.post(url + room_id + "/broadcasters", data=body, headers=head, verify=verify)
if response.status_code != 200:
    print(response.text)

#创建audio PlainTransport
body = json.dumps({'type': 'plain', 'comedia': True, 'rtcpMux': False})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports", data=body, headers=head, verify=verify)
text = json.loads(response.text)
audio_transport_id = text['id']
audio_transport_ip = text['ip']
audio_transport_port = text['port']
audio_transport_rtcp_port = text['rtcpPort']

#创建video PlainTransport
body = json.dumps({'type': 'plain', 'comedia': True, 'rtcpMux': False})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports", data=body, headers=head, verify=verify)
text = json.loads(response.text)
video_transport_id = text['id']
video_transport_ip = text['ip']
video_transport_port = text['port']
video_transport_rtcp_port = text['rtcpPort']

#创建audio Producer
body = json.dumps({"kind": "audio", "rtpParameters": {"codecs": [{"mimeType": "audio/opus", "payloadType": audio_pt, "clockRate": 48000, "channels": 2, "parameters": {"sprop-stereo": 1}}], "encodings": [{"ssrc": audio_ssrc}]}})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports/" + audio_transport_id + "/producers", data=body, headers=head, verify=verify)
fd.writelines('audio_producer_id = "' + json.loads(response.text)['id'] + '"\n')

#创建video Producer
body = json.dumps({"kind": "video", "rtpParameters": {"codecs": [{"mimeType": "video/H264", "payloadType": video_pt, "clockRate": 90000, "parameters": {"packetization-mode": 1, "level-asymmetry-allowed": 1, "profile-level-id": "4d0032", "x-google-start-bitrate": 1000}}], "encodings": [{"ssrc": video_ssrc}]}})
response = requests.post(url + room_id + "/broadcasters/" + broadcaster_id + "/transports/" + video_transport_id + "/producers", data=body, headers=head, verify=verify)
fd.writelines('video_producer_id = "' + json.loads(response.text)['id'] + '"\n')
fd.close()

#启动FFmpeg
cmd  = 'ffmpeg '
cmd += '-re '
cmd += '-v info '
cmd += '-stream_loop -1 '
cmd += '-i test.mp4 '
cmd += '-map 0:a:0 '
cmd += '-acodec libopus -ab 128k -ac 2 -ar 48000 '
cmd += '-map 0:v:0 '
cmd += '-pix_fmt yuv420p -c:v libx264 -b:v 1000k -profile:v baseline -deadline realtime -cpu-used 4 '
cmd += '-f tee '
cmd += '"[select=a:f=rtp:ssrc={audio_ssrc}:payload_type={audio_pt}]rtp://{audio_transport_ip}:{audio_transport_port}?rtcpport={audio_transport_rtcp_port}|\
        [select=v:f=rtp:ssrc={video_ssrc}:payload_type={video_pt}]rtp://{video_transport_ip}:{video_transport_port}?rtcpport={video_transport_rtcp_port}"'\
        .format(audio_ssrc=audio_ssrc, audio_pt=audio_pt, audio_transport_ip=audio_transport_ip, audio_transport_port=audio_transport_port, audio_transport_rtcp_port=audio_transport_rtcp_port, \
            video_ssrc=video_ssrc, video_pt=video_pt, video_transport_ip=video_transport_ip, video_transport_port=video_transport_port, video_transport_rtcp_port=video_transport_rtcp_port)

os.system(cmd)

#删除Broadcaster
response = requests.delete(url + room_id + "/broadcasters/" + broadcaster_id, verify=verify)
if response.status_code != 200:
    print(response.text)
    exit()

