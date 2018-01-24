#!/usr/bin/python

import pcap
import sys
import string
import time
import socket
import struct
import paho.mqtt.client as mqtt
import json
import time
import binascii

host = '192.168.56.14' # Specify your edge id
port = '1883'
topic = 'python' #Make sure topic match to your FogHorn Edge sensor config

def publish(data):
    try:
        client.publish(topic, json.dumps(data))
    except Exception as e:
        print 'publish error'
        print e

def decode_ip_packet(s):
    header_len = ord(s[0]) & 0x0f
    d = s[4 * header_len:]
    d = d[32:]
    return d

def print_packet(pktlen, data, timestamp):
    if not data:
        return

    if data[12:14]=='\x08\x00':
        payload = binascii.hexlify(decode_ip_packet(data[14:]))
        if len(payload) > 1:
            publish(payload)
            print payload

if __name__=='__main__':

    if len(sys.argv) < 3:
        print 'usage: packet_to_mqtt.py <interface> <expr>'
        sys.exit(0)

    client = mqtt.Client(protocol=mqtt.MQTTv311)

    try:
        client.connect(host, port=port, keepalive=60)
    except Exception as e:
        print 'MQTT connection error'
        sys.exit(0)

    p = pcap.pcapObject()
    dev = sys.argv[1]
    net, mask = pcap.lookupnet(dev)

    # note:  to_ms does nothing on linux
    p.open_live(dev, 1600, 0, 100)
    p.setfilter(string.join(sys.argv[2:],' '), 0, 0)

    # try-except block to catch keyboard interrupt.  Failure to shut
    # down cleanly can result in the interface not being taken out of promisc.
    # mode
    # p.setnonblock(1)
    try:
        while 1:
            p.dispatch(1, print_packet)

    except KeyboardInterrupt:
        print '%s' % sys.exc_type
        print 'shutting down'
        print '%d packets received, %d packets dropped, %d packets dropped by interface' % p.stats()
