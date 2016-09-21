# -*- coding: utf-8 -*-

from knxnet.utils import *

from abc import ABCMeta, abstractmethod, abstractclassmethod, abstractproperty
from enum import Enum

__author__ = "Adrien Lescourt"
__copyright__ = "HES-SO 2015, Project EMG4B"
__credits__ = ["Adrien Lescourt", "Bouchedakh Mohamed Nizar "]
__version__ = "1.0.2"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


def create_frame(service_type_descriptor, *data):
    frametype = ServiceTypeDescriptor.to_class(service_type_descriptor)
    if frametype is not None:
        return frametype.create_from_data(*data)


def decode_frame(frame):
    header = KnxnetHeader.create_from_frame(frame)
    frametype = ServiceTypeDescriptor.to_class(ServiceTypeDescriptor(header.service_type_descriptor))
    if frametype is not None:
        return frametype.create_from_frame(frame)


class ServiceTypeDescriptor(Enum):
    CONNECTION_REQUEST = 0x0205
    CONNECTION_RESPONSE = 0x0206
    CONNECTION_STATE_REQUEST = 0x0207
    CONNECTION_STATE_RESPONSE = 0x0208
    DISCONNECT_REQUEST = 0x0209
    DISCONNECT_RESPONSE = 0x020a
    TUNNELLING_REQUEST = 0x0420
    TUNNELLING_ACK = 0x0421

    @staticmethod
    def to_class(x):
        return {
            ServiceTypeDescriptor.CONNECTION_REQUEST: ConnectionRequest,
            ServiceTypeDescriptor.CONNECTION_RESPONSE: ConnectionResponse,
            ServiceTypeDescriptor.CONNECTION_STATE_REQUEST: ConnectionStateRequest,
            ServiceTypeDescriptor.CONNECTION_STATE_RESPONSE: ConnectionStateResponse,
            ServiceTypeDescriptor.DISCONNECT_REQUEST: DisconnectRequest,
            ServiceTypeDescriptor.DISCONNECT_RESPONSE: DisconnectResponse,
            ServiceTypeDescriptor.TUNNELLING_REQUEST: TunnellingRequest,
            ServiceTypeDescriptor.TUNNELLING_ACK: TunnellingAck
            }[x]


class KnxnetFrame():
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def __repr__(self):
        return str([hex(h) for h in self.frame])

    @abstractclassmethod
    def create_from_frame(cls, frame):
        pass

    @abstractclassmethod
    def create_from_data(cls, *data):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractproperty
    def frame(self):
        pass


class KnxnetHeader(KnxnetFrame):
    HEADER_LENGTH = 0x06
    VERSION = 0x10

    def __init__(self, header_length, version, service_type_descriptor, frame_length):
        super().__init__()
        self.header_length = header_length
        self.version = version
        self.service_type_descriptor = service_type_descriptor
        self.frame_length = frame_length

    @classmethod
    def create_from_frame(cls, frame):
        if len(frame) < 6:
            raise KnxnetException('Frame size is < 6')
        header_length = frame[0]
        version = frame[1]
        service_type_descriptor = ServiceTypeDescriptor((frame[2] << 8) | frame[3])
        frame_length = (frame[4] << 8) | frame[5]
        return cls(header_length, version, service_type_descriptor, frame_length)

    @classmethod
    def create_from_data(cls, service_type_descriptor, frame_length):
        return cls(KnxnetHeader.HEADER_LENGTH,
                   KnxnetHeader.VERSION,
                   service_type_descriptor,
                   frame_length)

    @property
    def frame(self):
        """
        Create the KNXnet header frame (6 bytes)
        """
        frame = bytearray()
        frame.append(self.header_length)
        frame.append(self.version)
        frame.append((self.service_type_descriptor.value >> 8) & 0xff)
        frame.append(self.service_type_descriptor.value & 0xff)
        frame.append((self.frame_length >> 8) & 0xff)
        frame.append(self.frame_length & 0xff)
        return frame

    def __str__(self):
        out = '{:<25}'.format('header_length')
        out += '{:>10}\n'.format(hex(self.header_length))
        out += '{:<25}'.format('version')
        out += '{:>10}\n'.format(hex(self.version))
        out += '{:<25}'.format('service_type_descriptor')
        out += '{:>10}\n'.format(hex(self.service_type_descriptor.value))
        out += '{:<25}'.format('frame_length')
        out += '{:>10}\n'.format(hex(self.frame_length))
        return out

    def __repr__(self):
        return super().__repr__()


class TunnellingRequest(KnxnetFrame):
    """
    TunnellingRequest KNXnet/IP frame
    """

    def __init__(self, knxnet_header, dest_addr_group, channel_id, data, data_size, apci, data_service, sequence_counter):
        super().__init__()
        self.header = knxnet_header
        self.dest_addr_group = dest_addr_group
        self.channel_id = channel_id
        self.data_service = data_service  # See Data Service under
        """
        FROM NETWORK LAYER TO DATA LINK LAYER
        – L_Raw.req 0x10
        – L_Data.req 0x11 Data Service. Primitive used for transmitting a data frame
        – L_Poll_Data.req 0x13 Poll Data Service
        FROM DATA LINK LAYER TO NETWORK LAYER
        – L_Poll_Data.con 0x25 Poll Data Service
        – L_Data.ind 0x29 Data Service. Primitive used for receiving a data frame
        – L_Busmon.ind 0x2B Bus Monitor Service
        – L_Raw.ind 0x2D
        – L_Data.con 0x2E Data Service. Primitive used for local confirmation that a frame was sent (does not indicate a successful receive though)
        – L_Raw.con 0x2F )
        """
        self.data = data
        self.data_size = data_size
        self.apci = apci  # (0x0 == group value read; 0x1 == group value response; 0x2 == group value write)
        self.sequence_counter = sequence_counter

    @classmethod
    def create_from_frame(cls, frame):
        """
        Create the Tunnelling request object from a frame
        :param frame: knx tunnelling request datagram frame (list of bytes)
        """
        if frame is None:
            raise KnxnetException('Tunnelling request frame is None')
        if len(frame) < 16:
            raise KnxnetException('Tunnelling request length is < 16')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        channel_id = raw_body[1]
        sequence_counter = raw_body[2]
        data_service = raw_body[4]
        dest_addr_group = GroupAddress.from_bytes(raw_body[10:12])
        data_size = raw_body[12]
        if data_size > 2:
            raise KnxnetException('Invalid frame: Unsupported datapoint type (data size > 2')
        apci = (raw_body[13] & 3 << 2) | (raw_body[14] >> 6)
        # only two datapoint types are supported:
        data = 0
        if data_size == 1:  # boolean
            data = raw_body[14] & 1
        elif data_size == 2:  # 8 bits unsigned
            data = raw_body[15]
        return cls(header, dest_addr_group, channel_id, data, data_size, apci, data_service, sequence_counter)

    @classmethod
    def create_from_data(cls, dest_addr_group, channel_id, data, data_size, apci=0x2, data_service=0x11, sequence_counter=0x0):
        """
        Create the Tunnelling request object from data
        :param dest_addr_group: GroupAddress object, or string
        :param channel_id: 1 byte with channel ID
        :param data: effective data
        :param data_size: data size in byte
        :param apci: APCI command. 0x2 is group value write    0 is group value read
        """
        frame_length = 0x14 + data_size
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.TUNNELLING_REQUEST, frame_length)
        if isinstance(dest_addr_group, GroupAddress):
            dest = dest_addr_group
        else:
            dest = GroupAddress.from_str(dest_addr_group)
        return cls(header, dest, channel_id, data, data_size, apci, data_service, sequence_counter)

    @property
    def frame(self):
        # KNXnet header
        frame = self.header.frame
        # Connection header
        frame.append(0x04)  # structure length
        frame.append(self.channel_id & 0xff)  # channel id
        frame.append(self.sequence_counter)  # sequence counter
        frame.append(0x00)  # reserved
        # cEMI
        frame.append(self.data_service) #frame.append(0x11)  # message code = data service transmitting
        frame.append(0x00)  # no additionnal info
        frame.append(0xbc)  # control byte
        frame.append(0xe0)  # DRL byte
        frame.append(0x00)  # Source address (filled by gateway)
        frame.append(0x00)
        frame += self.dest_addr_group.frame  # destination address group
        frame.append(self.data_size)  # routing (4 bits) + data size (4 bits)
        frame.append(0x0 | ((self.apci >> 2) & 3))  # The last 2 bits are the two msb for the APCI command
        # only two datapoint types are supported:
        if self.data_size == 1:  # boolean
            frame.append(((self.apci & 3) << 6) | (self.data & 1))  # the fist 2 bits are lsb APCI, bit 0 is data
        elif self.data_size == 2:  # 8 bits unsigned
            frame.append((self.apci & 3) << 6)  # the fist 2 bits are lsb APCI
            frame.append(self.data & 0xFF)  # data
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('dest_addr_group')
        out += '{:>10}\n'.format(str(self.dest_addr_group))
        out += '{:<25}'.format('channel_id')
        out += '{:>10}\n'.format(hex(self.channel_id))
        out += '{:<25}'.format('sequence_counter')
        out += '{:>10}\n'.format(hex(self.sequence_counter))
        out += '{:<25}'.format('data_service')
        out += '{:>10}\n'.format(hex(self.data_service))
        out += '{:<25}'.format('data')
        out += '{:>10}\n'.format(hex(self.data))
        out += '{:<25}'.format('data_size')
        out += '{:>10}\n'.format(hex(self.data_size))
        out += '{:<25}'.format('apci')
        out += '{:>10}\n'.format(hex(self.apci))
        return out

    def __repr__(self):
        return super().__repr__()


class TunnellingAck(KnxnetFrame):
    """
    Tunnelling ack KNXnet/IP frame
    """

    def __init__(self, knxnet_header, channel_id, status, sequence_counter):
        super().__init__()
        self.header = knxnet_header
        self.channel_id = channel_id
        self.status = status
        self.sequence_counter = sequence_counter

    @classmethod
    def create_from_frame(cls, frame):
        if frame is None:
            raise KnxnetException('Tunnelling ack frame is None')
        if len(frame) != 10:
            raise KnxnetException('Tunnelling ack length must be 10 bytes')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        channel_id = raw_body[1]
        sequence_counter = raw_body[2]
        status = raw_body[3]
        return cls(header, channel_id, status, sequence_counter)

    @classmethod
    def create_from_data(cls, channel_id, status, sequence_counter=0x0):
        frame_length = 10
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.TUNNELLING_ACK, frame_length)
        return cls(header, channel_id, status, sequence_counter)

    @property
    def frame(self):
        frame = self.header.frame
        frame.append(0x04)  # structure length
        frame.append(self.channel_id)
        frame.append(self.sequence_counter)
        frame.append(self.status)
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('channel_id')
        out += '{:>10}\n'.format(str(self.channel_id))
        out += '{:<25}'.format('sequence_counter')
        out += '{:>10}\n'.format(str(self.sequence_counter))
        out += '{:<25}'.format('status')
        out += '{:>10}\n'.format(str(self.status))
        return out

    def __repr__(self):
        return super().__repr__()


class ConnectionRequest(KnxnetFrame):
    """
    Connection_request KNXnet/IP frame
    """

    def __init__(self, knxnet_header, control_endpoint, data_endpoint):
        super().__init__()
        self.header = knxnet_header
        self.control_endpoint = control_endpoint
        self.data_endpoint = data_endpoint

    @classmethod
    def create_from_frame(cls, frame):
        if frame is None:
            raise KnxnetException('Connection request frame is None')
        if len(frame) < 24:
            raise KnxnetException('Connection request length must >= 24 bytes')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        control_endpoint = Hpai.from_frame(raw_body[:8])
        data_endpoint = Hpai.from_frame(raw_body[8:16])
        return cls(header, control_endpoint, data_endpoint)

    @classmethod
    def create_from_data(cls, control_endpoint, data_endpoint):
        """
        :param control_endpoint Hpai object or tuple (ip, port)
        :param data_endpoint Hpai object or tuple (ip, port)
        """
        frame_length = 0x1A
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.CONNECTION_REQUEST, frame_length)
        if isinstance(control_endpoint, Hpai):
            ctrl_endpt = control_endpoint
        else:
            ctrl_endpt = Hpai.from_data(control_endpoint[0], control_endpoint[1])
        if isinstance(data_endpoint, Hpai):
            data_endpt = data_endpoint
        else:
            data_endpt = Hpai.from_data(data_endpoint[0], data_endpoint[1])
        return cls(header, ctrl_endpt, data_endpt)

    @property
    def frame(self):
        # KNXnet header
        frame = self.header.frame
        # HPAI
        frame += self.control_endpoint.frame
        frame += self.data_endpoint.frame
        # CRI (Connection request info) to be defined
        frame.append(0x04)  # structure length
        frame.append(0x04)  # Tunnel Connection
        frame.append(0x02)  # KNX Tunnel link layer
        frame.append(0x00)  # Reserved
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('control_endpoint')
        out += '{:>10}\n'.format(str(self.control_endpoint))
        out += '{:<25}'.format('data_endpoint')
        out += '{:>10}\n'.format(str(self.data_endpoint))
        return out

    def __repr__(self):
        return super().__repr__()


class ConnectionResponse(KnxnetFrame):
    """
    Connection_response KNXnet/IP frame
    """

    def __init__(self, knxnet_header, channel_id, status, data_endpoint):
        super().__init__()
        self.header = knxnet_header
        self.channel_id = channel_id
        self.status = status
        self.data_endpoint = data_endpoint

    @classmethod
    def create_from_frame(cls, frame):
        if frame is None:
            raise KnxnetException('Connection response frame is None')
        if len(frame) < 18:
            raise KnxnetException('Connection response length must be >= 18 bytes')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        channel_id = raw_body[0]
        status = raw_body[1]
        data_endpoint = Hpai.from_frame(raw_body[2:10])
        return cls(header, channel_id, status, data_endpoint)

    @classmethod
    def create_from_data(cls, channel_id, status, data_endpoint):
        """
        :param channel_id  one byte
        :param status  one byte
        :param data_endpoint Hpai object or tuple (ip, port)
        """
        frame_length = 20
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.CONNECTION_RESPONSE, frame_length)
        if isinstance(data_endpoint, Hpai):
            data_endpt = data_endpoint
        else:
            data_endpt = Hpai.from_data(data_endpoint[0], data_endpoint[1])
        return cls(header, channel_id, status, data_endpt)

    @property
    def frame(self):
        frame = self.header.frame
        frame.append(self.channel_id)
        frame.append(self.status)
        frame += self.data_endpoint.frame
        # CRD (connection response data) is to be defined
        frame.append(0x04)
        frame.append(0x04)
        frame.append(0xff)
        frame.append(0xff)
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('channel_id')
        out += '{:>10}\n'.format(str(self.channel_id))
        out += '{:<25}'.format('status')
        out += '{:>10}\n'.format(str(self.status))
        out += '{:<25}'.format('data_endpoint')
        out += '{:>10}\n'.format(str(self.data_endpoint))
        return out

    def __repr__(self):
        return super().__repr__()


class ConnectionStateRequest(KnxnetFrame):
    """
    Connection state request KNXnet/IP frame
    """

    def __init__(self, knxnet_header, channel_id, control_endpoint):
        super().__init__()
        self.header = knxnet_header
        self.channel_id = channel_id
        self.control_endpoint = control_endpoint

    @classmethod
    def create_from_frame(cls, frame):
        if frame is None:
            raise KnxnetException('Connection state request frame is None')
        if len(frame) != 16:
            raise KnxnetException('Connection state request length must be 16 bytes')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        channel_id = raw_body[0]
        control_endpoint = Hpai.from_frame(raw_body[2:10])
        return cls(header, channel_id, control_endpoint)

    @classmethod
    def create_from_data(cls, channel_id, control_endpoint):
        """
        :param channel_id  one byte
        :param control_endpoint  Hpai object or tuple (ip, port)
        """
        frame_length = 16
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.CONNECTION_STATE_REQUEST, frame_length)
        if isinstance(control_endpoint, Hpai):
            ctrl_endpt = control_endpoint
        else:
            ctrl_endpt = Hpai.from_data(control_endpoint[0], control_endpoint[1])
        return cls(header, channel_id, ctrl_endpt)

    @property
    def frame(self):
        frame = self.header.frame
        frame.append(self.channel_id)
        frame.append(0x00)
        frame += self.control_endpoint.frame
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('channel_id')
        out += '{:>10}\n'.format(str(self.channel_id))
        out += '{:<25}'.format('control_endpoint')
        out += '{:>10}\n'.format(str(self.control_endpoint))
        return out

    def __repr__(self):
        return super().__repr__()


class ConnectionStateResponse(KnxnetFrame):
    """
    Connection state response KNXnet/IP frame
    """

    def __init__(self, knxnet_header, channel_id, status):
        super().__init__()
        self.header = knxnet_header
        self.channel_id = channel_id
        self.status = status

    @classmethod
    def create_from_frame(cls, frame):
        if frame is None:
            raise KnxnetException('Connection state response frame is None')
        if len(frame) != 8:
            raise KnxnetException('Connection state response length must be 8 bytes')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        channel_id = raw_body[0]
        status = raw_body[1]
        return cls(header, channel_id, status)

    @classmethod
    def create_from_data(cls, channel_id, status):
        frame_length = 8
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.CONNECTION_STATE_RESPONSE, frame_length)
        return cls(header, channel_id, status)

    @property
    def frame(self):
        frame = self.header.frame
        frame.append(self.channel_id)
        frame.append(self.status)
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('channel_id')
        out += '{:>10}\n'.format(str(self.channel_id))
        out += '{:<25}'.format('status')
        out += '{:>10}\n'.format(str(self.status))
        return out

    def __repr__(self):
        return super().__repr__()


class DisconnectRequest(KnxnetFrame):
    """
    Disconnect request KNXnet/IP frame
    """

    def __init__(self, knxnet_header, channel_id, control_endpoint):
        super().__init__()
        self.header = knxnet_header
        self.channel_id = channel_id
        self.control_endpoint = control_endpoint

    @classmethod
    def create_from_frame(cls, frame):
        if frame is None:
            raise KnxnetException('Disconnect request frame is None')
        if len(frame) != 16:
            raise KnxnetException('Disconnect request length must be 16 bytes')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        channel_id = raw_body[0]
        control_endpoint = Hpai.from_frame(raw_body[2:10])
        return cls(header, channel_id, control_endpoint)

    @classmethod
    def create_from_data(cls, channel_id, control_endpoint):
        """
        :param channel_id  one byte
        :param control_endpoint  Hpai object or tuple (ip, port)
        """
        frame_length = 16
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.DISCONNECT_REQUEST, frame_length)
        if isinstance(control_endpoint, Hpai):
            ctrl_endpt = control_endpoint
        else:
            ctrl_endpt = Hpai.from_data(control_endpoint[0], control_endpoint[1])
        return cls(header, channel_id, ctrl_endpt)

    @property
    def frame(self):
        frame = self.header.frame
        frame.append(self.channel_id)
        frame.append(0x00)
        frame += self.control_endpoint.frame
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('channel_id')
        out += '{:>10}\n'.format(str(self.channel_id))
        out += '{:<25}'.format('control_endpoint')
        out += '{:>10}\n'.format(str(self.control_endpoint))
        return out

    def __repr__(self):
        return super().__repr__()


class DisconnectResponse(KnxnetFrame):
    """
    Disconnect response KNXnet/IP frame
    """

    def __init__(self, knxnet_header, channel_id, status):
        super().__init__()
        self.header = knxnet_header
        self.channel_id = channel_id
        self.status = status

    @classmethod
    def create_from_frame(cls, frame):
        if frame is None:
            raise KnxnetException('Disconnect response frame is None')
        if len(frame) != 8:
            raise KnxnetException('Disconnect response length must be 8 bytes')
        raw_header = frame[:6]
        raw_body = frame[6:]
        header = KnxnetHeader.create_from_frame(raw_header)
        if len(frame) != header.frame_length:
            raise KnxnetException('Invalid frame: effective total length != announced total length')
        channel_id = raw_body[0]
        status = raw_body[1]
        return cls(header, channel_id, status)

    @classmethod
    def create_from_data(cls, channel_id, status):
        frame_length = 8
        header = KnxnetHeader.create_from_data(ServiceTypeDescriptor.DISCONNECT_RESPONSE, frame_length)
        return cls(header, channel_id, status)

    @property
    def frame(self):
        frame = self.header.frame
        frame.append(self.channel_id)
        frame.append(self.status)
        return frame

    def __str__(self):
        out = str(self.header)
        out += '{:<25}'.format('channel_id')
        out += '{:>10}\n'.format(str(self.channel_id))
        out += '{:<25}'.format('status')
        out += '{:>10}\n'.format(str(self.status))
        return out

    def __repr__(self):
        return super().__repr__()


class KnxnetException(Exception):
    pass


if __name__ == '__main__':
    pass
