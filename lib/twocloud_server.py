import socketserver
import pickle
from phe import paillier
from socket_recvsize import *

# 生成秘钥对
pbk, pvk = paillier.generate_paillier_keypair(n_length=1024)
pbk.max_int = pbk.n//2


# 乘法
def multiply(conn,data):
    m1 = pvk.decrypt(data[1])
    m2 = pvk.decrypt(data[2])
    res = m1*m2 % pbk.n
    if res > pbk.max_int:
        res -= pbk.n
    sendall_size(conn,pickle.dumps(pbk.encrypt(res)))

def multiply_with_quantizer(conn,data):
    m1 = pvk.decrypt(data[1])
    m2 = pvk.decrypt(data[2])
    q = int(data[3])
    res = m1*m2//q % pbk.n
    if res > pbk.max_int:
        res -= pbk.n
    sendall_size(conn,pickle.dumps(pbk.encrypt(res)))

# 除法
def divide(conn,data):
    rq = data[1]
    rm2 = pvk.decrypt(data[2])
    sendall_size(conn,pickle.dumps(pbk.encrypt(rq//rm2)))


# 开方
def square_root(conn,data):
    rq = data[1]
    rrm = pvk.decrypt(data[2])
    sendall_size(conn,pickle.dumps(pbk.encrypt(rq//((rrm**0.5).__round__()))))


# 取最大值
def bigger(conn,data):
    if pvk.decrypt(data[1])>0:
        sendall_size(conn,pickle.dumps(pbk.encrypt(0)))
        bg=pickle.loads(recv_size(conn))[0]
    else:
        sendall_size(conn,pickle.dumps(pbk.encrypt(1)))
        bg = pickle.loads(recv_size(conn))[1]
    sendall_size(conn,pickle.dumps(pbk.encrypt(pvk.decrypt(bg))))


# 指令名与调用函数的映射
switch = {
    'pvk': lambda conn,d: sendall_size(conn,pickle.dumps(pvk)),  # 获取私钥
    'pbk': lambda conn,d: sendall_size(conn,pickle.dumps(pbk)),  # 获取公钥
    'mul': multiply,  # 乘法
    'mulq': multiply_with_quantizer,
    'div': divide,  # 除法
    'sqrt': square_root,  # 开方
    'bgr': bigger  # 求最大值
}


class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        cmd = pickle.loads(recv_size(self.request))
        print(self.client_address,':'+cmd[0])
        switch[cmd[0]](self.request,cmd)
        self.request.close()


if __name__ == '__main__':
    server=socketserver.ThreadingTCPServer(('0.0.0.0',9999),MyServer)
    server.serve_forever()
