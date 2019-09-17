from phe import paillier
from twocloud_client import PlaintextCloud


class LmsFilterED():
    def __init__(self,decrypt_cloud: PlaintextCloud, window_len=12, mu=0.05, quantizer=2**32):
        self.mu=mu
        self.w_len=window_len
        self.q=quantizer
        self.cloud=decrypt_cloud
        self.w=[decrypt_cloud.pbk.encrypt(0)]*window_len

    def lms(self, signal_in, expection):
        signal_in=[self.cloud.pbk.encrypt(0)]*(self.w_len-1)+signal_in
        signal_out,error=[],[]
        mq=self.cloud.multiply_with_quantizer
        for n in range(len(expection)):
            y=0
            for i in range(self.w_len):
                y=y+mq(signal_in[n+i],self.w[i],self.q)
            e= expection[n] - y
            signal_out.append(y)
            error.append(e)
            for i in range(self.w_len):
                self.w[i]+=mq(signal_in[n+i],e,int(self.q//self.mu))
        return signal_out,error


if __name__=='__main__':
    q=2**32
    ft=LmsFilterED(PlaintextCloud(('127.0.0.1',9999)))
    pbk=ft.cloud.pbk
    pvk=ft.cloud.get_privatekey()




    noise,sigin=[],[]
    f = open('c:/users/hjm/desktop/noise.txt', 'r')
    for l in f:
        noise.append(pbk.encrypt(int(float(l)*q)))
    f.close()
    f = open('c:/users/hjm/desktop/lms_input.txt', 'r')
    for l in f:
        sigin.append(pbk.encrypt(int(float(l)*q)))
    f.close()
    out,err=ft.lms(noise,sigin)

    f=open('c:/users/hjm/desktop/lms_output.txt','w')
    for e in err:
        f.write(str(pvk.decrypt(e)/q)+'\n')
    f.close()
