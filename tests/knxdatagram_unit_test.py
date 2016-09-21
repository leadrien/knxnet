#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from knxnet.knxnet import *
from knxnet.utils import *

__author__ = "Adrien Lescourt"
__copyright__ = "HES-SO 2014, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.1"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


class KnxdatagramTestCase(unittest.TestCase):

    def test_group_addr_translation(self):
        print()
        addr_str = '0/0/0'
        addr_bytes = bytearray()
        addr_bytes.append(0x00)
        addr_bytes.append(0x00)
        print('Test group address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(GroupAddress.from_str(addr_str).frame, addr_bytes)
        self.assertEqual(str(GroupAddress.from_bytes(addr_bytes)), addr_str)
        print('Success')

        addr_str = '1/1/1'
        addr_bytes = bytearray()
        addr_bytes.append(0x09)
        addr_bytes.append(0x01)
        print('Test group address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(GroupAddress.from_str(addr_str).frame, addr_bytes)
        self.assertEqual(str(GroupAddress.from_bytes(addr_bytes)), addr_str)
        print('Success')

        addr_str = '1/4/10'
        addr_bytes = bytearray()
        addr_bytes.append(0x0c)
        addr_bytes.append(0x0a)
        print('Test group address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(GroupAddress.from_str(addr_str).frame, addr_bytes)
        self.assertEqual(str(GroupAddress.from_bytes(addr_bytes)), addr_str)
        print('Success')

        addr_str = '1.2.3@1/4/10'
        addr_bytes = bytearray()
        addr_bytes.append(0x0c)
        addr_bytes.append(0x0a)
        print('Test group address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(GroupAddress.from_full_address(addr_str).frame, addr_bytes)
        print('Success')

        addr_str = '1/-1/10'
        print('Test invalid group address translation, {0}.....'.format(addr_str), end='')
        self.assertRaises(KnxnetUtilsException, GroupAddress.from_str, addr_str)
        print('Success')

        addr_str = '32/1/10'
        print('Test invalid group address translation, {0}.....'.format(addr_str), end='')
        self.assertRaises(KnxnetUtilsException, GroupAddress.from_str, addr_str)
        print('Success')

        addr_str = '1/1/256'
        print('Test invalid group address translation, {0}.....'.format(addr_str), end='')
        self.assertRaises(KnxnetUtilsException, GroupAddress.from_str, addr_str)
        print('Success')

    def test_individual_addr_translation(self):
        print()
        addr_str = '0.0.0'
        addr_bytes = 0
        print('Test individual address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(IndividualAddress.from_str(addr_str).get_bytes(), addr_bytes)
        self.assertEqual(str(IndividualAddress.from_bytes(addr_bytes)), addr_str)
        print('Success')

        addr_str = '1.1.1'
        addr_bytes = 0x1101
        print('Test individual address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(IndividualAddress.from_str(addr_str).get_bytes(), addr_bytes)
        self.assertEqual(str(IndividualAddress.from_bytes(addr_bytes)), addr_str)
        print('Success')

        addr_str = '5.12.7'
        addr_bytes = 0x5C07
        print('Test individual address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(IndividualAddress.from_str(addr_str).get_bytes(), addr_bytes)
        self.assertEqual(str(IndividualAddress.from_bytes(addr_bytes)), addr_str)
        print('Success')

        addr_str = '5.12.7@1/2/3'
        addr_bytes = 0x5C07
        print('Test individual address translation, {0}.....'.format(addr_str), end='')
        self.assertEqual(IndividualAddress.from_full_address(addr_str).get_bytes(), addr_bytes)
        print('Success')

        addr_str = '-1.1.3'
        print('Test invalid individual address translation, {0}.....'.format(addr_str), end='')
        self.assertRaises(KnxnetUtilsException,
                          IndividualAddress.from_str, addr_str)
        print('Success')

        addr_str = '1.16.0'
        print('Test invalid individual address translation, {0}.....'.format(addr_str), end='')
        self.assertRaises(KnxnetUtilsException,
                          IndividualAddress.from_str, addr_str)
        print('Success')

        addr_str = '1.1.256'
        print('Test invalid individual address translation, {0}.....'.format(addr_str), end='')
        self.assertRaises(KnxnetUtilsException,
                          IndividualAddress.from_str, addr_str)
        print('Success')

    def test_tunneling_request(self):
        print()
        print('Test tunnelling request frame creation, 1 byte data.....', end='')
        # dest_addr_group=1/4/10, channel=0x07, data=0x01
        t1_b = bytearray()
        t1_b.append(0x06)  # header
        t1_b.append(0x10)
        t1_b.append(0x04)
        t1_b.append(0x20)
        t1_b.append(0x00)
        t1_b.append(0x15)
        t1_b.append(0x04)  # connection header
        t1_b.append(0x07)
        t1_b.append(0x00)
        t1_b.append(0x00)
        t1_b.append(0x11)  # cEMI frame
        t1_b.append(0x00)
        t1_b.append(0xbc)
        t1_b.append(0xe0)
        t1_b.append(0x00)
        t1_b.append(0x00)
        t1_b.append(0x0c)  # group dest
        t1_b.append(0x0a)
        t1_b.append(0x01)  # data size
        t1_b.append(0x00)  # bit 0 and 1 are the two msb for apci command
        t1_b.append(0x81)  # bit 6 and 7 are the two lsb for apci command, bit 0 is data
        t1_dest_addr = GroupAddress.from_str('1/4/10')
        t1_channel_id = 0x7
        t1_data = 0x01
        t1_data_size = 1
        t1_apci = 0x02
        t1_tunnel_req = create_frame(ServiceTypeDescriptor.TUNNELLING_REQUEST,
                                     t1_dest_addr,
                                     t1_channel_id,
                                     t1_data,
                                     t1_data_size,
                                     t1_apci)
        self.assertEqual(t1_tunnel_req.frame, t1_b)
        print('Success')

        print('Test tunnelling request frame creation, 4 byte data.....', end='')
        # dest_addr_group=1/4/10, channel=0x12, data=0xab
        t2_b = bytearray()
        t2_b.append(0x06)  # header
        t2_b.append(0x10)
        t2_b.append(0x04)
        t2_b.append(0x20)
        t2_b.append(0x00)
        t2_b.append(0x16)
        t2_b.append(0x04)  # connection header
        t2_b.append(0x12)
        t2_b.append(0x00)
        t2_b.append(0x00)
        t2_b.append(0x11)  # cEMI frame
        t2_b.append(0x00)
        t2_b.append(0xbc)
        t2_b.append(0xe0)
        t2_b.append(0x00)
        t2_b.append(0x00)
        t2_b.append(0x0c)
        t2_b.append(0x0a)
        t2_b.append(0x02)  # data size
        t2_b.append(0x00)  # bit 0 and 1 are the two msb for apci command
        t2_b.append(0x80)  # bit 6 and 7 are the two lsb for apci command
        t2_b.append(0xab)  # data
        t2_dest_addr = '1/4/10'
        t2_channel_id = 0x12
        t2_data = 0xab
        t2_data_size = 2
        t2_apci = 0x02
        t2_tunnel_req = create_frame(ServiceTypeDescriptor.TUNNELLING_REQUEST,
                                     t2_dest_addr,
                                     t2_channel_id,
                                     t2_data,
                                     t2_data_size,
                                     t2_apci)
        self.assertEqual(t2_tunnel_req.frame, t2_b)
        print('Success')

        print('Test tunnelling request frame decode, 1 byte data.....', end='')
        t1_tunnel_req = decode_frame(t1_b)
        self.assertEqual(t1_tunnel_req.header.header_length, 0x06)
        self.assertEqual(t1_tunnel_req.header.version, 0x10)
        self.assertEqual(t1_tunnel_req.header.service_type_descriptor.value, 0x0420)
        self.assertEqual(t1_tunnel_req.header.frame_length, 0x0015)
        self.assertEqual(t1_tunnel_req.channel_id, t1_channel_id)
        self.assertEqual(t1_tunnel_req.dest_addr_group.frame, t1_dest_addr.frame)
        self.assertEqual(t1_tunnel_req.data, t1_data)
        self.assertEqual(t1_tunnel_req.data_size, t1_data_size)
        print('Success')

        print('Test tunnelling request frame decode, 4 byte data.....', end='')
        t2_tunnel_req = decode_frame(t2_b)
        self.assertEqual(t2_tunnel_req.header.header_length, 0x06)
        self.assertEqual(t2_tunnel_req.header.version, 0x10)
        self.assertEqual(t2_tunnel_req.header.service_type_descriptor.value, 0x0420)
        self.assertEqual(t2_tunnel_req.header.frame_length, 0x0016)
        self.assertEqual(t2_tunnel_req.channel_id, t2_channel_id)
        self.assertEqual(str(t2_tunnel_req.dest_addr_group), t2_dest_addr)
        self.assertEqual(t2_tunnel_req.data, t2_data)
        self.assertEqual(t2_tunnel_req.data_size, t2_data_size)
        print('Success')

    def test_tunnel_ack(self):
        print()
        print('Test tunnel ack frame creation.....', end='')
        b = bytearray()
        b.append(0x06)  # header
        b.append(0x10)
        b.append(0x04)
        b.append(0x21)
        b.append(0x00)
        b.append(0x0A)
        b.append(0x04)
        b.append(0x01)  # channel_id
        b.append(0x00)  # sequence counter
        b.append(0x00)
        channel_id = 1
        status = 0
        tunnel_ack = create_frame(ServiceTypeDescriptor.TUNNELLING_ACK,
                                  channel_id,
                                  0)
        self.assertEqual(tunnel_ack.frame, b)
        print('Success')

        print('Test tunnel ack frame decode.....', end='')
        tunnel_ack = decode_frame(b)
        self.assertEqual(tunnel_ack.header.header_length, 0x06)
        self.assertEqual(tunnel_ack.header.version, 0x10)
        self.assertEqual(tunnel_ack.header.service_type_descriptor.value, 0x0421)
        self.assertEqual(tunnel_ack.header.frame_length, 10)
        self.assertEqual(tunnel_ack.channel_id, channel_id)
        self.assertEqual(tunnel_ack.status, status)
        print('Success')

    def test_hpai(self):
        print()
        print('Test hpai data to bytes.....', end='')
        ip = '123.30.0.1'
        port = 1234
        b = bytearray()
        b.append(0x08)
        b.append(0x01)
        b.append(123)
        b.append(30)
        b.append(0)
        b.append(1)
        b.append(0x04)
        b.append(0xD2)
        hpai_endpoint = Hpai.from_data(ip, port)
        self.assertEqual(hpai_endpoint.frame, b)
        print('Success')

        print('Test hpai bytes to data.....', end='')
        hpai_endpoint = Hpai.from_frame(b)
        self.assertEqual(hpai_endpoint.ip_addr, ip)
        self.assertEqual(hpai_endpoint.port, port)
        print('Success')

    def test_connection_request(self):
        print()
        print('Test connection request frame creation.....', end='')
        b = bytearray()
        b.append(0x06)  # header
        b.append(0x10)
        b.append(0x02)
        b.append(0x05)
        b.append(0x00)
        b.append(0x1A)
        b.append(0x08)  # HPAI control endpoint
        b.append(0x01)
        b.append(127)
        b.append(0)
        b.append(0)
        b.append(1)
        b.append(0x0E)
        b.append(0x58)
        b.append(0x08)  # HPAI data endpoint
        b.append(0x01)
        b.append(10)
        b.append(11)
        b.append(12)
        b.append(13)
        b.append(0x0E)
        b.append(0x59)
        b.append(0x04)  # end
        b.append(0x04)
        b.append(0x02)
        b.append(0x00)
        control_endpoint = ('127.0.0.1', 3672)
        data_endpoint = ('10.11.12.13', 3673)
        connection_request = create_frame(ServiceTypeDescriptor.CONNECTION_REQUEST,
                                          control_endpoint,
                                          data_endpoint)
        self.assertEqual(connection_request.frame, b)
        print('Success')

        print('Test connection request frame decode.....', end='')
        connection_request = decode_frame(b)
        self.assertEqual(connection_request.header.header_length, 0x06)
        self.assertEqual(connection_request.header.version, 0x10)
        self.assertEqual(connection_request.header.service_type_descriptor.value, 0x0205)
        self.assertEqual(connection_request.header.frame_length, 0x1A)
        self.assertEqual(connection_request.control_endpoint.ip_addr, '127.0.0.1')
        self.assertEqual(connection_request.control_endpoint.port, 3672)
        self.assertEqual(connection_request.data_endpoint.ip_addr, '10.11.12.13')
        self.assertEqual(connection_request.data_endpoint.port, 3673)
        print('Success')

    def test_connection_response(self):
        print()
        print('Test connection response frame creation.....', end='')
        b = bytearray()
        b.append(0x06)  # header
        b.append(0x10)
        b.append(0x02)
        b.append(0x06)
        b.append(0x00)
        b.append(0x14)
        b.append(0x07)  # channel id
        b.append(0x0)   # status
        b.append(0x08)  # HPAI
        b.append(0x01)
        b.append(0x00)
        b.append(0x00)
        b.append(0x00)
        b.append(0x00)
        b.append(0x00)
        b.append(0x00)
        b.append(0x04)  # end
        b.append(0x04)
        b.append(0xff)
        b.append(0xff)
        channel_id = 0x07
        status = 0x00
        data_endpoint = ('0.0.0.0', 0)
        connection_response = create_frame(ServiceTypeDescriptor.CONNECTION_RESPONSE,
                                           channel_id,
                                           status,
                                           data_endpoint)
        self.assertEqual(connection_response.frame, b)
        print('Success')

        print('Test connection response frame decode.....', end='')
        connection_response = decode_frame(b)
        self.assertEqual(connection_response.header.header_length, 0x06)
        self.assertEqual(connection_response.header.version, 0x10)
        self.assertEqual(connection_response.header.service_type_descriptor.value, 0x0206)
        self.assertEqual(connection_response.header.frame_length, 0x14)
        self.assertEqual(connection_response.channel_id, channel_id)
        self.assertEqual(connection_response.status, status)
        self.assertEqual(connection_response.data_endpoint.ip_addr, '0.0.0.0')
        self.assertEqual(connection_response.data_endpoint.port, 0)
        print('Success')

    def test_connection_state_request(self):
        print()
        print('Test connection state request frame creation.....', end='')
        b = bytearray()
        b.append(0x06)  # header
        b.append(0x10)
        b.append(0x02)
        b.append(0x07)
        b.append(0x00)
        b.append(0x10)
        b.append(0x12)  # channel_id
        b.append(0x00)
        b.append(0x08)  # control enpoint
        b.append(0x01)
        b.append(127)
        b.append(0)
        b.append(0)
        b.append(1)
        b.append(0x0E)
        b.append(0x58)
        channel_id = 0x12
        control_endpoint = Hpai.from_data('127.0.0.1', 3672)
        connection_state_request = create_frame(ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
                                                channel_id,
                                                control_endpoint)
        self.assertEqual(connection_state_request.frame, b)
        print('Success')

        print('Test connection state request frame decode.....', end='')
        connection_state_request = decode_frame(b)
        self.assertEqual(connection_state_request.header.header_length, 0x06)
        self.assertEqual(connection_state_request.header.version, 0x10)
        self.assertEqual(connection_state_request.header.service_type_descriptor.value, 0x0207)
        self.assertEqual(connection_state_request.header.frame_length, 0x10)
        self.assertEqual(connection_state_request.channel_id, channel_id)
        self.assertEqual(connection_state_request.control_endpoint.ip_addr, '127.0.0.1')
        self.assertEqual(connection_state_request.control_endpoint.port, 3672)
        print('Success')

    def test_connection_state_response(self):
        print()
        print('Test connection state response frame creation.....', end='')
        b = bytearray()
        b.append(0x06)  # header
        b.append(0x10)
        b.append(0x02)
        b.append(0x08)
        b.append(0x00)
        b.append(0x08)
        b.append(0x12)  # channel_id
        b.append(0x01)  # status
        channel_id = 0x12
        status = 1
        connection_state_response = create_frame(ServiceTypeDescriptor.CONNECTION_STATE_RESPONSE,
                                                 channel_id,
                                                 status)
        self.assertEqual(connection_state_response.frame, b)
        print('Success')

        print('Test connection state response frame decode.....', end='')
        connection_state_response = decode_frame(b)
        self.assertEqual(connection_state_response.header.header_length, 0x06)
        self.assertEqual(connection_state_response.header.version, 0x10)
        self.assertEqual(connection_state_response.header.service_type_descriptor.value, 0x0208)
        self.assertEqual(connection_state_response.header.frame_length, 0x08)
        self.assertEqual(connection_state_response.channel_id, channel_id)
        self.assertEqual(connection_state_response.status, status)
        print('Success')

    def test_disconnect_request(self):
        print()
        print('Test disconnect request frame creation.....', end='')
        b = bytearray()
        b.append(0x06)  # header
        b.append(0x10)
        b.append(0x02)
        b.append(0x09)
        b.append(0x00)
        b.append(0x10)
        b.append(0x12)  # channel_id
        b.append(0x00)
        b.append(0x08)  # control enpoint
        b.append(0x01)
        b.append(127)
        b.append(0)
        b.append(0)
        b.append(1)
        b.append(0x0E)
        b.append(0x58)
        channel_id = 0x12
        control_endpoint = ('127.0.0.1', 3672)
        disconnect_request = create_frame(ServiceTypeDescriptor.DISCONNECT_REQUEST,
                                          channel_id,
                                          control_endpoint)
        self.assertEqual(disconnect_request.frame, b)
        print('Success')

        print('Test disconnect request frame decode.....', end='')
        disconnect_request = decode_frame(b)
        self.assertEqual(disconnect_request.header.header_length, 0x06)
        self.assertEqual(disconnect_request.header.version, 0x10)
        self.assertEqual(disconnect_request.header.service_type_descriptor.value, 0x0209)
        self.assertEqual(disconnect_request.header.frame_length, 0x10)
        self.assertEqual(disconnect_request.channel_id, channel_id)
        self.assertEqual(disconnect_request.control_endpoint.ip_addr, '127.0.0.1')
        self.assertEqual(disconnect_request.control_endpoint.port, 3672)
        print('Success')

    def test_disconnect_response(self):
        print()
        print('Test disconnect response frame creation.....', end='')
        b = bytearray()
        b.append(0x06)  # header
        b.append(0x10)
        b.append(0x02)
        b.append(0x0a)
        b.append(0x00)
        b.append(0x08)
        b.append(0x12)  # channel_id
        b.append(0x01)  # status
        channel_id = 0x12
        status = 1
        disconnect_response = create_frame(ServiceTypeDescriptor.DISCONNECT_RESPONSE,
                                           channel_id,
                                           status)
        self.assertEqual(disconnect_response.frame, b)
        print('Success')

        print('Test disconnect response frame decode.....', end='')
        disconnect_response = decode_frame(b)
        self.assertEqual(disconnect_response.header.header_length, 0x06)
        self.assertEqual(disconnect_response.header.version, 0x10)
        self.assertEqual(disconnect_response.header.service_type_descriptor.value, 0x020a)
        self.assertEqual(disconnect_response.header.frame_length, 0x08)
        self.assertEqual(disconnect_response.channel_id, channel_id)
        self.assertEqual(disconnect_response.status, status)
        print('Success')

if __name__ == '__main__':
    unittest.main()
