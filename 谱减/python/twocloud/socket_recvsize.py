import sys

def sendall_size(the_socket,content):
    size=str(len(content))
    size='0'*(8-len(size))+size
    return the_socket.sendall(size.encode()+content)


def recv_size(the_socket):
    # data length is packed into 4 bytes
    total_len, total_data = 0, []
    size = sys.maxsize
    size_data = sock_data = b''
    recv_size = 8192
    while total_len < size:
        sock_data = the_socket.recv(recv_size)
        if not total_data:
            if len(size_data) + len(sock_data) > 8:
                size_data += sock_data
                size = int(size_data[:8])
                recv_size = size
                total_data.append(size_data[8:])
            else:
                size_data += sock_data
        else:
            total_data.append(sock_data)
        total_len = sum([len(i) for i in total_data])
    return b''.join(total_data)