# -*- coding: utf-8 -*-

__author__ = "Adrien Lescourt"
__copyright__ = "HES-SO 2015, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.1"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


class GroupAddress():
    def __init__(self, main_group, middle_group, sub_group):
        self.main_group = main_group
        self.middle_group = middle_group
        self.sub_group = sub_group

    @property
    def frame(self):
        out = bytearray()
        b = self.main_group << 3
        b |= self.middle_group
        out.append(b)
        out.append(self.sub_group)
        return out

    @classmethod
    def from_str(cls, group_address_str):
        """
        Create the GroupAddress object from a group address string
        :param group_address_str: eg: '1/4/10'
        """
        groups = group_address_str.split('/')
        if len(groups) is not 3:
            raise KnxnetUtilsException('Format must be x/y/z')
        main_group = int(groups[0])
        middle_group = int(groups[1])
        sub_group = int(groups[2])
        if main_group < 0 or main_group > 31:
            raise KnxnetUtilsException('Main group must be 0 <= main_group < 32')
        if middle_group < 0 or middle_group > 7:
            raise KnxnetUtilsException('Main group must be 0 <= main_group < 8')
        if sub_group < 0 or sub_group > 255:
            raise KnxnetUtilsException('Main group must be 0 <= main_group < 256')
        return cls(main_group, middle_group, sub_group)

    @classmethod
    def from_full_address(cls, address):
        """
        Create the GroupAddress object from a full address
        :param address: as string full address (individual + group) (eg: 1.2.3@4.5.6)
        """
        if '@' not in address:
            raise KnxnetUtilsException('Invalid address format')
        data = address.split('@')[1]
        return cls.from_str(data)

    @classmethod
    def from_bytes(cls, group_address_bytes):
        """
        Create the GroupAddress object from 2 bytes group address
        :param group_address_bytes: a 2 bytes bytearray
        """
        if len(group_address_bytes) > 2:
            raise KnxnetUtilsException('Group address must be two bytes')
        main_group = group_address_bytes[0] >> 3
        middle_group = group_address_bytes[0] & 0x7
        sub_group = group_address_bytes[1]
        return cls(main_group, middle_group, sub_group)

    def __repr__(self):
        return 'KNX group address: {0}/{1}/{2}'.format(self.main_group, self.middle_group, self.sub_group)

    def __str__(self):
        return '{0}/{1}/{2}'.format(self.main_group, self.middle_group, self.sub_group)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class IndividualAddress():
    def __init__(self, area, line, bus_device):
        self.area = area
        self.line = line
        self.bus_device = bus_device

    def get_bytes(self):
        b = self.area << 4
        b |= self.line
        b <<= 8
        b |= self.bus_device
        return b

    @classmethod
    def from_str(cls, individual_address):
        """
        Create the IndividualAddress object from an individual address string
        :param individual_address: as string (eg: 4.0.10)
        """
        data = individual_address.split('.')
        if len(data) is not 3:
            raise KnxnetUtilsException('Format must be x.y.z')
        area = int(data[0])
        line = int(data[1])
        bus_device = int(data[2])
        if area < 0 or area > 15:
            raise KnxnetUtilsException('Area must be 0 <= area < 16')
        if line < 0 or line > 15:
            raise KnxnetUtilsException('Line must be 0 <= line < 16')
        if bus_device < 0 or bus_device > 255:
            raise KnxnetUtilsException('Line must be 0 <= bus_device < 256')
        return cls(area, line, bus_device)

    @classmethod
    def from_full_address(cls, address):
        """
        Create the IndividualAddress object from a full address
        :param address: as string full address (individual + group) (eg: 1.2.3@4.5.6)
        """
        if '@' not in address:
            raise KnxnetUtilsException('Invalid address format')
        data = address.split('@')[0]
        return cls.from_str(data)

    @classmethod
    def from_bytes(cls, individual_address):
        """
        Create the IndividualAddress object from a 2 bytes individual address
        :param individual_address: 2 bytes
        """
        if individual_address > 0xFFFF:
            raise KnxnetUtilsException('Physical address must be two bytes')
        area = (individual_address >> 12) & 0xF
        line = (individual_address >> 8) & 0xF
        bus_device = individual_address & 0xFF
        return cls(area, line, bus_device)

    def __repr__(self):
        return 'KNX Physical address: {0}.{1}.{2}'.format(self.area, self.line, self.bus_device)

    def __str__(self):
        return '{0}.{1}.{2}'.format(self.area, self.line, self.bus_device)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class Hpai():
    def __init__(self, ip_addr, port, structure_length, host_protocol_code):
        self.structure_length = structure_length
        self.host_protocol_code = host_protocol_code
        self.ip_addr = ip_addr
        self.port = port

    @classmethod
    def from_data(cls, ip_addr, port, structure_length=0x08, host_protocol_code=0x01):
        """
        :param ip_addr: IPv4 as string
        :param port: as integer
        :structure_length: = 8
        :host_protocol_code: 0x01 = IPV4 UDP
        """
        return cls(ip_addr, port, structure_length, host_protocol_code)

    @classmethod
    def from_frame(cls, hpai_bytes):
        structure_length = hpai_bytes[0]
        host_protocol_code = hpai_bytes[1]
        ip_addr = str(hpai_bytes[2]) + '.'
        ip_addr += str(hpai_bytes[3]) + '.'
        ip_addr += str(hpai_bytes[4]) + '.'
        ip_addr += str(hpai_bytes[5])
        port = (hpai_bytes[6] << 8) | hpai_bytes[7]
        return cls(ip_addr, port, structure_length, host_protocol_code)

    @property
    def frame(self):
        out = bytearray()
        out.append(self.structure_length)
        out.append(self.host_protocol_code)
        fields = self.ip_addr.split('.')
        if len(fields) != 4:
            raise KnxnetUtilsException('Invalid IP address')
        for field in fields:
            field_int = int(field)
            if field_int > 255:
                raise KnxnetUtilsException('Invalid IP address')
            out.append(field_int)
        out.append((self.port >> 8) & 0xFF)
        out.append(self.port & 0xFF)
        return out

    def __str__(self):
        return self.ip_addr + ':' + str(self.port)


class KnxnetUtilsException(Exception):
    pass
