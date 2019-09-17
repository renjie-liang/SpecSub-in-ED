from phe import paillier
from twocloud_client import PlaintextCloud
import math
class SpecSubED():
    def __init__(self,decrypt_cloud: PlaintextCloud, 
                inc = 160,
                window_len=400, 
                a_in = 4,
                b_in = 0.001,
                NIS = 23,
                quantizer=2**32):

        self.inc = inc
        self.wlen = window_len #windowlen
        self.Len_message = None
        self.Num_w = None

        self.Q=quantizer
        self.A = a_in
        self.B = b_in
        self.NIS = NIS
        self.alpha_hamming = 0.46

        self.cloud=decrypt_cloud
        self.pvk = self.cloud.get_privatekey()
        self.mul_qua=self.cloud.multiply_with_quantizer
        self.mul = self.cloud.multiply
        self.div = self.cloud.divide
        self.sqrt = self.cloud.square_root
        self.big = self.cloud.bigger



    def spec_sub(self, signal_in, noise):


        self.Len_message = len(signal_in)
        self.Num_w=(self.Len_message - self.wlen) // self.inc + 1

        sptrRe, sptrIm = self.enframed_windowed_dft(signal_in) # Q^3
        print(sptrRe[0][0])
        print(pvk.decrypt(sptrRe[0][0]))
        print(pvk.decrypt(sptrRe[0][0]) / self.Q / self.Q / self.Q  )
        print('Q: ', self.Q)
        print('QQ: ', self.Q * self.Q)
        print('QQQ: ', self.Q * self.Q * self.Q)
        input()

        sptrRe, sptrIm = self.sptr_sub(sptrRe,sptrIm)
        outSignal = overlap_add(sptrRe,sptrIm)
        return outSignal

    def enframed_windowed_dft(self, signal_in):

        sptrRe = [[0]*self.wlen] * self.Num_w           # wlen * Num_w int 
        sptrIm = [[0]*self.wlen] * self.Num_w
        window = self.get_hamming_window(self.wlen)     #  Q


        for index_w in range(self.Num_w):
            temp = [0] * self.wlen
            for j in range(self.wlen):
                temp[j] = signal_in[index_w + j] * window[j] # Q^2

            re, im = self.DFT(temp) # Q^3
            sptrRe[index_w] = re
            sptrIm[index_w] = im

        return sptrRe, sptrIm # Q^3



    def sptr_sub(self, sptrRe, sptrIm):
        amp = [[0]*self.wlen] * self.Num_w # Q^6
        amp_avg = [0] * self.wlen

        for i in range(self.Num_w):
            for j in range(self.wlen):

                print('sptrRe[i][j] of ciphertext = ', sptrRe[i][j].ciphertext())
                print('sptrRe[i][j] of plaintext = ', pvk.decrypt(sptrRe[i][j]))
                print('sptrRe[i][j] / Q^3  of plaintext= ', pvk.decrypt(sptrRe[i][j])/self.Q/self.Q/self.Q)
                input()



                x = self.mul(sptrRe[i][j], sptrRe[i][j]) # Q^6
                y = self.mul(sptrIm[i][j], sptrIm[i][j]) # Q^6
                amp[i][j] = x + y  

        for i in range(self.wlen):
            for j in range(self.NIS):
                amp_avg = amp_avg[i] + amp[j][i]

        for i in range(self.wlen):
            A_amp = self.A * amp_avg[i]
            B_amp = self.B * amp_avg[i]

            for j in range(self.Num_w):
                
                x = self.Q * amp[j][i] - A_amp
                x = self.big(x, B_amp)

                x = self.div(x, amp[j][i])
                x = self.sqrt(x)
                sptrRe[j][i] = self.mul(sptrRe[j][i], x)
                sptrIm[j][i] = self.mul(sptrIm[j][i], x)
        return sptrRe, sptrIm

        

    def overlap_add(self, sptrRe, sptrIm):
        outSignal = [0] * self.Len_message

        for i in range(self.Num_w):
            re, im = DFT(sptrRe, sptrIm)
            for j in range(self.inc):
                outSignal[i * self.inc + j] = outSignal[i * self.inc + j] + re[j]

        return outSignal
        

    def DFT(self, re_in, img_in = None):  # Q^2
        len_s = len(re_in)
        p = (-2 * math.pi) / len_s

        aux_re, aux_im = [], [] # Q

        for i in range(len_s):
            row_re, row_im = [], []
            for j in range(len_s):
                x = math.cos(i * j * p) * self.Q
                y = math.sin(i * j * p) * self.Q
                row_re.append(x)
                row_im.append(y)
            aux_re.append(row_re)
            aux_im.append(row_im) # Q


        re, im = [0] * len_s, [0] * len_s
        for i in range(len_s):
            for j in range(len_s):
                x = re_in[j] * aux_re[i][j] # Q^3
                re[i] = re[i] + x
                y = re_in[j] * aux_im[i][j] 
                im[i] = im[i] + y


        if img_in:
            for i in range(len_s):
                for j in range(len_s):
                    x = -1 * aux_re[i][j] * img_in[j] # QQ
                    re[i] = re[i] + x
                    y = -1 * aux_im[i][j] * img_in[j] # QQ
                    im[i] = im[i] + y


        return re, im # Q^3


    def get_hamming_window(self, wlen):
        win = []
        p = (2 * math.pi) / (self.wlen - 1)
        for i in range(wlen):
            x = math.cos(p * i)
            x = self.alpha_hamming * x + (1 - self.alpha_hamming)
            x = x * self.Q
            win.append(x)
        return win # 1 * wlen int Q



if __name__=='__main__':
    q=2**32
    ft=SpecSubED(PlaintextCloud(('127.0.0.1',9999)),
                inc = 50    ,
                window_len=64, 
                a_in = 4,
                b_in = 0.001,
                NIS = 23,
                quantizer=2**32) #
    pbk=ft.cloud.pbk
    pvk=ft.cloud.get_privatekey()


    noise,sigin=[],[]
    # f = open('./data/noise.txt', 'r')
    # for index, l in enumerate(f):
    #     noise.append(pbk.encrypt(int(float(l)*q)))
    #     print('{}|{}'.format(index,1024))
    # f.close()

    f = open('./data/lms_input.txt', 'r')
    for index, l in enumerate(f):
        sigin.append(pbk.encrypt(int(float(l)*q)))
        print('{}|{}'.format(index,256))
    f.close()

    #sigin # Q
    out,err=ft.spec_sub(sigin, noise)


    # noise,sigin=[],[]
    # f = open('c:/users/hjm/desktop/noise.txt', 'r')
    # for l in f:
    #     noise.append(pbk.encrypt(int(float(l)*q)))
    # f.close()
    # f = open('c:/users/hjm/desktop/lms_input.txt', 'r')
    # for l in f:
    #     sigin.append(pbk.encrypt(int(float(l)*q)))
    # f.close()
    # out,err=ft.lms(noise,sigin)

    # f=open('c:/users/hjm/desktop/lms_output.txt','w')
    # for e in err:
    #     f.write(str(pvk.decrypt(e)/q)+'\n')
    # f.close()
