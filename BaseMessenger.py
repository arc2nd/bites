#!/usr/bin/env python

import os
import sys
import json
import time
import datetime
import subprocess
import traceback
from optparse import OptionParser

import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe


def parse_args(all_args):
    parser = OptionParser(version = '%prog 1.0')
    parser.add_option('-l', '--listen', action='store_true', help='enter listen mode')

    options, args = parser.parse_args(all_args)
    return options, args


class BaseMessenger(object):
    def __init__(self, path):
        # self.conn = self.get_conn()
        self.connected = False
        self.creds = self.get_creds(path)
        return

    def get_conn(self, broker_addr):
        client = None
        try:
            #client = mqtt.Client('BaseBitesClient')
            client = mqtt.Client()
            client.on_connect = self.on_connect 
            client.on_message = self.on_message
            if len(self.creds['PASS']):
                client.username_pw_set(self.creds['USER'], password=self.creds['PASS'])
            client.connect(broker_addr, keepalive=60)
            self.connected = True
        except:
            print('couldn\'t connect to broker')
        return client

    def get_creds(self, path):
        j = None
        cmd = "openssl des3 -salt -d -in %s -pass pass:%s" % (path, os.path.basename(path))
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        if (output):
            try:
                j = json.loads(output)
            except:
                j = None
        return j

    def send_message(self, client, topic, msg):
        client.publish(topic, msg)
        print(' [x] Sent: "{}"'.format(msg))

    def close_conn(self, client):
        client.disconnect()

    def talk(self, client, topic, msg):
        self.send_message(client, topic, msg)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(" [+] Connected to broker")
            self.connected = True                #Signal connection 
        else:
            print(" [-] Connection failed")

    def on_message(self, client, userdata, msg):
        print(' [x] Received: {}'.format(msg.payload.decode('utf-8')))

    def listen(self, client, topic):
        while self.connected != True:    #Wait for connection
            time.sleep(0.1)
        client.subscribe(topic)
        client.loop_start()
        # time.sleep(0.1)
        print(' [*] Waiting for messages, CTRL+C to exit')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "exiting"
            client.disconnect()
            client.loop_stop()


if __name__ == '__main__':
    options, args = parse_args(sys.argv[1:])
    my_msgr = BaseMessenger('/home/james/scripts/bites/envs.crypt')
    my_conn = my_msgr.get_conn(my_msgr.creds['SERVER'])
    if options.listen:
        my_msgr.listen(my_conn, 'test_topic')
    else:
        # print(' [->] sending: {}'.format('hello'))
        my_msgr.send_message(my_conn, 'test_topic', 'Base at {}'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')))
    my_msgr.close_conn(my_conn)



