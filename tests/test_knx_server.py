#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import threading
from random import randint
from knxnet import *

__author__ = "Adrien Lescourt"
__copyright__ = "HES-SO 2015, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.0"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


class Knxserver(threading.Thread):

    udp_port = 3671

    def __init__(self):
        super().__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_running = True
        self.addr = None
        self.channel_id = randint(0, 255)
        self.status = 0
        self.control_endpoint = ('0.0.0.0', 0)
        self.data_endpoint = ('0.0.0.0', 0)

    def run(self):
        try:
            self.socket.bind(('', self.udp_port))
            while self.server_running:
                frame, self.addr = self.socket.recvfrom(1024)
                if frame:
                    if len(frame) > len(b'exit'):

                        print('Frame received:' + str([hex(h) for h in frame]))
                        decoded_frame = knxnet.decode_frame(frame)

                        # CONNECTION REQUEST
                        if decoded_frame.header.service_type_descriptor ==\
                                knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST:
                            print('= Connection request:\n' + str(decoded_frame))
                            conn_resp = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_RESPONSE,
                                                            self.channel_id,
                                                            self.status,
                                                            self.data_endpoint)
                            self.send(conn_resp.frame)
                            print('Frame sent:' + repr(conn_resp))
                            print('= Connection response:\n' + str(conn_resp))

                        # CONNECTION STATE REQUEST
                        elif decoded_frame.header.service_type_descriptor ==\
                                knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST:
                            print('= Connection state request:\n' + str(decoded_frame))
                            conn_state_rep = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_RESPONSE,
                                                                 self.channel_id,
                                                                 self.status)
                            self.send(conn_state_rep.frame)
                            print('Frame sent:' + repr(conn_state_rep))
                            print('= Connection state response:\n' + str(conn_state_rep))

                        # DISCONNECT REQUEST
                        elif decoded_frame.header.service_type_descriptor ==\
                                knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST:
                            print('= Disconnect request:\n' + str(decoded_frame))
                            disconnect_resp = knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_RESPONSE,
                                                                  self.channel_id,
                                                                  self.status)
                            self.send(disconnect_resp.frame)
                            print('Frame sent:' + repr(disconnect_resp))
                            print('= Disconnect response:\n' + str(disconnect_resp))

                        # TUNNELLING REQUEST
                        elif decoded_frame.header.service_type_descriptor ==\
                                knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST:
                            print('= Tunnelling request:\n' + str(decoded_frame))
                            tunnel_ack = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_ACK,
                                                             self.channel_id,
                                                             self.status)
                            self.send(tunnel_ack.frame)
                            print('Frame sent:' + repr(tunnel_ack))
                            print('= Tunnelling ack:\n' + str(tunnel_ack))

                        else:
                            print('The frame is not supported')
        finally:
            self.socket.close()

    def send(self, frame):
        if self.server_running:
            if self.addr is not None:
                self.socket.sendto(frame, self.addr)

    def close_server(self):
        self.server_running = False
        self.socket.sendto(b'exit', ('localhost', self.udp_port))

if __name__ == '__main__':
    serv = Knxserver()
    serv.start()
