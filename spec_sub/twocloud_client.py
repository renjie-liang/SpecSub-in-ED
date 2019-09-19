import socket, pickle, random, time
from phe.paillier import EncryptedNumber
from socket_recvsize import *


class PlaintextCloud(object):

    def __init__(self, ip_port: tuple):
        self.ip_port = ip_port
        sk = socket.socket()
        sk.connect(ip_port)
        sendall_size(sk,pickle.dumps(['pbk']))
        self.pbk = pickle.loads(recv_size(sk))
        sk.close()

    # 获得私钥，仅测试用
    def get_privatekey(self):
        arg=['pvk']
        sk = socket.socket()
        sk.connect(self.ip_port)
        sendall_size(sk,pickle.dumps(arg))
        data = recv_size(sk)
        sk.close()
        return pickle.loads(data)

    # 密文乘法
    def multiply(self, c1: EncryptedNumber, c2: EncryptedNumber):
        r1 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        r2 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        arg=['mul',c1+r1,c2+r2]
        sk = socket.socket()
        sk.connect(self.ip_port)
        sendall_size(sk,pickle.dumps(arg))
        data=recv_size(sk)
        sk.close()
        return pickle.loads(data)-c1*r2-c2*r1-self.pbk.encrypt(r1)*r2

    def multiply_with_quantizer(self, c1: EncryptedNumber, c2: EncryptedNumber, quantizer: int):
        r1 = random.SystemRandom().randrange(1, self.pbk.max_int//quantizer)
        r2 = random.SystemRandom().randrange(1, self.pbk.max_int//quantizer)
        arg=['mulq',c1 + r1*quantizer,c2 + r2*quantizer,quantizer]
        sk = socket.socket()
        sk.connect(self.ip_port)
        sendall_size(sk,pickle.dumps(arg))
        data = recv_size(sk)
        sk.close()
        return pickle.loads(data) - c1 * r2 - c2 * r1 - self.pbk.encrypt(r1) * (r2*quantizer)


    # 密文除法
    def divide(self, c1: EncryptedNumber, c2: EncryptedNumber, quantizer: int, r=0):
        if r == 0:
            r = random.SystemRandom().randrange(1, (self.pbk.max_int**0.5).__round__())
        arg=['div',r*quantizer,c2*r]
        sk = socket.socket()
        sk.connect(self.ip_port)
        sendall_size(sk,pickle.dumps(arg))
        data = pickle.loads(recv_size(sk))  # temp=E(quantizer/m2)
        sk.close()
        return self.multiply(c1, data)

    # 密文开方
    def square_root(self, c1: EncryptedNumber, quantizer: int, r=0):
        if r == 0:
            r = random.SystemRandom().randrange(1, (self.pbk.max_int**0.25).__round__())
        arg=['sqrt',r * quantizer,c1 * r**2 + 1]
        sk = socket.socket()
        sk.connect(self.ip_port)
        sendall_size(sk,pickle.dumps(arg))
        data = pickle.loads(recv_size(sk))
        sk.close()
        return self.multiply(c1, data)

    # 密文求最大值
    def bigger(self, c1:EncryptedNumber, c2:EncryptedNumber):
        sk = socket.socket()
        sk.connect(self.ip_port)
        r = random.SystemRandom().randrange(1, (self.pbk.max_int**0.5).__round__())
        sendall_size(sk,pickle.dumps(['bgr',(c1-c2)*r]))
        ci = pickle.loads(recv_size(sk))
        r1 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        r20 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        r21 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        sendall_size(sk,pickle.dumps([c1+r1+ci*r20, c2 + r1 + (ci-1) * r21]))
        data = recv_size(sk)
        sk.close()
        return pickle.loads(data)-r1


if __name__ == '__main__':
    start=time.clock()
    ip='127.0.0.1'
    cld=PlaintextCloud((ip,9999))
    pbk=cld.pbk
    pvk=cld.get_privatekey()
    a = pbk.encrypt(-300)
    b = pbk.encrypt(2)
    quantizer=random.SystemRandom().randrange(1,2**32)
    print('a=', pvk.decrypt(a))
    print('b=', pvk.decrypt(b))
    print('quantizer=', quantizer,'\n')
    print('a*b=', pvk.decrypt(cld.multiply(a, b)))
    print('with_q a*b=', pvk.decrypt(cld.multiply_with_quantizer(a*quantizer, b*quantizer,quantizer))/quantizer)
    print('a/b=', pvk.decrypt(cld.divide(a, b, quantizer))/quantizer)
    print('b^0.5=', pvk.decrypt(cld.square_root(b, quantizer))/quantizer)
    print('max{a,b}=',pvk.decrypt(cld.bigger(a, b)),'\n')
    print('ip:',ip)
    print('runtime:',time.clock()-start,'s')
