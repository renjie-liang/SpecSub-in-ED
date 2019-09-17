import socket, pickle, random
from phe.paillier import EncryptedNumber


class PlaintextCloud(object):

    def __init__(self, ip_port: tuple):
        self.ip_port = ip_port
        sk = socket.socket()
        sk.connect(ip_port)
        sk.sendall('pbk'.encode())
        self.pbk = pickle.loads(sk.recv(9999))
        sk.close()

    # 获得私钥，仅测试用
    def get_privatekey(self):
        sk = socket.socket()
        sk.connect(self.ip_port)
        sk.sendall('pvk'.encode())
        data = sk.recv(9999)
        sk.close()
        return pickle.loads(data)

    # 密文乘法
    def multiply(self, c1: EncryptedNumber, c2: EncryptedNumber):
        sk = socket.socket()
        sk.connect(self.ip_port)
        sk.sendall('mul'.encode())
        r1 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        r2 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)

        r1 = 0
        print('c1 of ciphertext',c1.ciphertext())
        print('r1 of plaintext',r1)
        print('r1 of ciphertext',self.pbk.encrypt(r1).ciphertext())
        # r1 =1 
        print('+' * 40)
        print('c1+r1 = ', c1 + r1 )
        print('+' * 40)
        print('c1+r1  of ciphertext= ', (c1 + r1).ciphertext() )
        sk.recv(1)
        sk.sendall(pickle.dumps(c1+r1))
        sk.recv(1)
        sk.sendall(pickle.dumps(c2+r2))
        data=sk.recv(9999)
        sk.close()
        return pickle.loads(data)-c1*r2-c2*r1-self.pbk.encrypt(r1)*r2

    def multiply_with_quantizer(self, c1: EncryptedNumber, c2: EncryptedNumber, quantizer: int):
        sk = socket.socket()
        sk.connect(self.ip_port)
        sk.sendall('mulq'.encode())
        r1 = random.SystemRandom().randrange(1, self.pbk.max_int//quantizer)
        r2 = random.SystemRandom().randrange(1, self.pbk.max_int//quantizer)
        sk.recv(1)
        sk.sendall(pickle.dumps(c1 + r1*quantizer))
        sk.recv(1)
        sk.sendall(pickle.dumps(c2 + r2*quantizer))
        sk.recv(1)
        sk.sendall(pickle.dumps(quantizer))
        data = sk.recv(9999)
        sk.close()
        return pickle.loads(data) - c1 * r2 - c2 * r1 - self.pbk.encrypt(r1) * (r2*quantizer)


    # 密文除法
    def divide(self, c1: EncryptedNumber, c2: EncryptedNumber, quantizer: int, r=0):
        sk = socket.socket()
        sk.connect(self.ip_port)
        sk.sendall('div'.encode())
        if r == 0:
            r = random.SystemRandom().randrange(1, (self.pbk.max_int**0.5).__round__())
        sk.recv(1)
        sk.sendall(pickle.dumps(r*quantizer))
        sk.recv(1)
        sk.sendall(pickle.dumps(c2*r))
        temp = pickle.loads(sk.recv(9999))  # temp=E(quantizer/m2)
        sk.close()
        return self.multiply(c1, temp)

    # 密文开方
    def square_root(self, c1: EncryptedNumber, quantizer: int, r=0):
        sk = socket.socket()
        sk.connect(self.ip_port)
        sk.sendall('sqrt'.encode())
        if r == 0:
            r = random.SystemRandom().randrange(1, (self.pbk.max_int**0.25).__round__())
        sk.recv(1)
        sk.sendall(pickle.dumps(r * quantizer))
        sk.recv(1)
        sk.sendall(pickle.dumps(c1 * r**2 + 1))
        temp = pickle.loads(sk.recv(9999))
        sk.close()
        return self.multiply(c1, temp)

    # 密文求最大值
    def bigger(self, c1:EncryptedNumber, c2:EncryptedNumber):
        sk = socket.socket()
        sk.connect(self.ip_port)
        sk.sendall('bgr'.encode())
        r = random.SystemRandom().randrange(1, (self.pbk.max_int**0.5).__round__())
        sk.recv(1)
        sk.sendall(pickle.dumps((c1-c2)*r))
        ci = pickle.loads(sk.recv(9999))
        r1 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        r20 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        sk.sendall(pickle.dumps(c1+r1+ci*r20))
        r21 = random.SystemRandom().randrange(-self.pbk.max_int,self.pbk.max_int)
        sk.recv(1)
        sk.sendall(pickle.dumps(c2 + r1 + (ci-1) * r21))
        res = sk.recv(9999)
        sk.close()
        return pickle.loads(res)-r1


if __name__ == '__main__':
    cld=PlaintextCloud(('172.18.184.244',9999))
    pbk=cld.pbk
    pvk=cld.get_privatekey()
    a = pbk.encrypt(-300)
    b = pbk.encrypt(2)
    quantizer=random.SystemRandom().randrange(1,2**32)
    print('a=', pvk.decrypt(a))
    print('b=', pvk.decrypt(b))
    print('quantizer=', quantizer)
    print('a*b=', pvk.decrypt(cld.multiply(a, b)))
    print('with_q a*b=', pvk.decrypt(cld.multiply_with_quantizer(a*quantizer, b*quantizer,quantizer))/quantizer)
    print('a/b=', pvk.decrypt(cld.divide(a, b, quantizer))/quantizer)
    print('b^0.5=', pvk.decrypt(cld.square_root(b, quantizer))/quantizer)
    print('max{a,b}=',pvk.decrypt(cld.bigger(a, b)))
