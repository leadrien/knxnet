# -*- coding: utf-8 -*-

import sys
import socket

from knxnet import *

__author__ = "Adrien Lescourt"
__copyright__ = "HES-SO 2015, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.0"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


udp_ip = "127.0.0.1"
udp_port = 3671

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 3672))


def send_data_to_group_addr(dest_group_addr, data, data_size):
    data_endpoint = ('0.0.0.0', 0)
    control_enpoint = ('0.0.0.0', 0)

    # CONNECTION REQUEST
    conn_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST,
                                   control_enpoint,
                                   data_endpoint)
    print('==> Send connection request to {0}:{1}'.format(udp_ip, udp_port))
    print(repr(conn_req))
    print(conn_req)
    sock.sendto(conn_req.frame, (udp_ip, udp_port))

    # CONNECTION RESPONSE
    data_recv, addr = sock.recvfrom(1024)
    conn_resp = knxnet.decode_frame(data_recv)
    print('<== Received connection response:')
    print(repr(conn_resp))
    print(conn_resp)

    # CONNECTION STATE REQUEST
    conn_state_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
                                         conn_resp.channel_id,
                                         control_enpoint)
    print('==> Send connection state request to channel {0}'.format(conn_resp.channel_id))
    print(repr(conn_state_req))
    print(conn_state_req)
    sock.sendto(conn_state_req.frame, (udp_ip, udp_port))

    # CONNECTION STATE RESPONSE
    data_recv, addr = sock.recvfrom(1024)
    conn_state_resp = knxnet.decode_frame(data_recv)
    print('<== Received connection state response:')
    print(repr(conn_state_resp))
    print(conn_state_resp)

    # TUNNEL REQUEST
    tunnel_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST,
                                     dest_group_addr,
                                     conn_resp.channel_id,
                                     data,
                                     data_size)
    print('==> Send tunnelling request to {0}:{1}'.format(udp_ip, udp_port))
    print(repr(tunnel_req))
    print(tunnel_req)
    sock.sendto(tunnel_req.frame, (udp_ip, udp_port))

    # TUNNEL ACK
    data_recv, addr = sock.recvfrom(1024)
    ack = knxnet.decode_frame(data_recv)
    print('<== Received tunnelling ack:')
    print(repr(ack))
    print(ack)

    # DISCONNECT REQUEST
    disconnect_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST,
                                         conn_resp.channel_id,
                                         control_enpoint)
    print('==> Send disconnect request to channel {0}'.format(conn_resp.channel_id))
    print(repr(disconnect_req))
    print(disconnect_req)
    sock.sendto(disconnect_req.frame, (udp_ip, udp_port))

    # DISCONNECT RESPONSE
    data_recv, addr = sock.recvfrom(1024)
    disconnect_resp = knxnet.decode_frame(data_recv)
    print('<== Received connection state response:')
    print(repr(disconnect_resp))
    print(disconnect_resp)


if __name__ == '__main__':
    dest = knxnet.GroupAddress.from_str('12/4/1')
    send_data_to_group_addr('12/4/1', 42, 2)
    send_data_to_group_addr('12/5/2', 0, 1)
