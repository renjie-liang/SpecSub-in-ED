import socketserver
import pickle
from phe import paillier

# 生成秘钥对
pbk, pvk = paillier.generate_paillier_keypair(n_length=1024)
pbk.max_int = pbk.n//2


# 乘法
def multiply(conn):
    conn.sendall(bytes(1))
    m1 = pvk.decrypt(pickle.loads(conn.recv(9999)))
    conn.sendall(bytes(1))
    m2 = pvk.decrypt(pickle.loads(conn.recv(9999)))
    res = m1*m2 % pbk.n
    if res > pbk.max_int:
        res -= pbk.n
    conn.sendall(pickle.dumps(pbk.encrypt(res)))

def multiply_with_quantizer(conn):
    conn.sendall(bytes(1))
    m1 = pvk.decrypt(pickle.loads(conn.recv(9999)))
    conn.sendall(bytes(1))
    m2 = pvk.decrypt(pickle.loads(conn.recv(9999)))
    conn.sendall(bytes(1))
    q = int(pickle.loads(conn.recv(9999)))
    res = m1*m2//q % pbk.n
    if res > pbk.max_int:
        res -= pbk.n
    conn.sendall(pickle.dumps(pbk.encrypt(res)))

# 除法
def divide(conn):
    conn.sendall(bytes(1))
    rq = pickle.loads(conn.recv(9999))
    conn.sendall(bytes(1))
    rm2 = pvk.decrypt(pickle.loads(conn.recv(9999)))
    conn.sendall(pickle.dumps(pbk.encrypt(rq//rm2)))


# 开方
def square_root(conn):
    conn.sendall(bytes(1))
    rq = pickle.loads(conn.recv(9999))
    conn.sendall(bytes(1))
    rrm = pvk.decrypt(pickle.loads(conn.recv(9999)))
    conn.sendall(pickle.dumps(pbk.encrypt(rq//((rrm**0.5).__round__()))))


# 取最大值
def bigger(conn):
    conn.sendall(bytes(1))
    if pvk.decrypt(pickle.loads(conn.recv(9999)))>0:
        conn.sendall(pickle.dumps(pbk.encrypt(0)))
        bg=pickle.loads(conn.recv(9999))
        conn.sendall(bytes(1))
        conn.recv(9999)
    else:
        conn.sendall(pickle.dumps(pbk.encrypt(1)))
        conn.recv(9999)
        conn.sendall(bytes(1))
        bg = pickle.loads(conn.recv(9999))
    conn.sendall(pickle.dumps(pbk.encrypt(pvk.decrypt(bg))))


# 指令名与调用函数的映射
switch = {
    'pvk': lambda conn: conn.sendall(pickle.dumps(pvk)),  # 获取私钥
    'pbk': lambda conn: conn.sendall(pickle.dumps(pbk)),  # 获取公钥
    'mul': multiply,  # 乘法
    'mulq': multiply_with_quantizer,
    'div': divide,  # 除法
    'sqrt': square_root,  # 开方
    'bgr': bigger  # 求最大值
}


class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        cmd = self.request.recv(50).decode()
        switch[cmd](self.request)
        print(self.client_address,':'+cmd)


if __name__ == '__main__':
    server=socketserver.ThreadingTCPServer(('0.0.0.0',9999),MyServer)
    server.serve_forever()
