
# KNXNET

knxnet is a Python3 library to create and decode KNXnet/IP datagram for Tunnelling.

Then you can send/receive the frames to/from a KNXnet/IP gateway with UDP.

**This library was developed to suit the needs of the project HES-SO/EMG4B. It is not complete and some commands/parameters are missing.**


# Installation

python setup.py install


# Usage

* To create a frame you can use the factory:

```python
    BinaryFrame = create_frame(SERVICE_TYPE_DESCRIPTOR, *param)
```

* To decode a frame:

```python
    KnxnetObject = decode_frame(frame)
```

then you have access to all fields in the KNX frame


* The following *SERVICE_TYPE_DESCRIPTOR* are available, with the required parameters for frame creation:

```python
 * CONNECTION_REQUEST:
    create_frame(ServiceTypeDescriptor.CONNECTION_REQUEST,
                 CONTROL_ENPOINT,
                 DATA_ENDPOINT)

- CONNECTION_RESPONSE:
    create_frame(ServiceTypeDescriptor.CONNECTION_RESPONSE,
                 CHANNEL_ID,
                 STATUS,
                 DATA_ENDPOINT)

- CONNECTION_STATE_REQUEST
    create_frame(ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
                 CHANNEL_ID,
                 CONTROL_ENPOINT)

- CONNECTION_STATE_RESPONSE
    create_frame(ServiceTypeDescriptor.CONNECTION_STATE_RESPONSE,
                 CHANNEL_ID,
                 STATUS)

- DISCONNECT_REQUEST
    create_frame(ServiceTypeDescriptor.DISCONNECT_REQUEST,
                 CHANNEL_ID,
                 CONTROL_ENPOINT)

- DISCONNECT_RESPONSE
    create_frame(ServiceTypeDescriptor.DISCONNECT_RESPONSE,
                 CHANNEL_ID,
                 STATUS)

- TUNNELLING_REQUEST
    create_frame(ServiceTypeDescriptor.TUNNELLING_REQUEST,
                 DEST_GROUP_ADDR,
                 CHANNEL_ID,
                 DATA,
                 DATA_SIZE)

- TUNNELLING_ACK
    create_frame(ServiceTypeDescriptor.TUNNELLING_ACK,
                 CHANNEL_ID,
                 STATUS)
```

* Parameters type:

    *CONTROL_ENDPOINT* is a Hpai object or a tuple with IP as string and port as int: through NAT, put everything to zero ('0.0.0.0', 0)
    
    *DATA_ENDPOINT* is a Hpai object or a tuple with IP as string and port as int: through NAT, put everything to zero ('0.0.0.0', 0)
    
    *CHANNEL_ID* is a byte
    
    *STATUS* is a byte: 0 = all ok
    
    *DEST_GROUP_ADDR* is the destination group address as string '16/5/2' or as GroupAdress object
    
    *DATA* is a datapoint type (**only boolean and 8 bit unsigned are currently supported**)
    
    *DATA_SIZE* in byte



* Basic KNXnet usage:
```python
    -> Connection request
    <- Connection response
    -> Connection state request
    <- Connection state response
    -> Tunnelling request
    <- Tunnelling ack
    -> Disconnect request
    <- Disconnect response
```


# Example

You can test the library with the simple local client/server examples: **test_knx_server.py** and **test_knx_client.py**.
