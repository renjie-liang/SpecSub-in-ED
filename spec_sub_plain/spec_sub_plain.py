import math
import numpy as np
import random
import copy

from utils.option import args
from tqdm import tqdm
class SpecSub_plain():
    def __init__(self, inc = 160,
                window_len=400, 
                a_in = 4,
                b_in = 0.001,
                NIS = 23):

        self.inc = inc
        self.wlen = window_len #windowlen
        self.Len_message = None
        self.Num_w = None

        self.A = a_in
        self.B = b_in
        self.NIS = NIS
        self.alpha_hamming = 0.46


    def spec_sub(self, signal_in):

        self.Len_message = len(signal_in)
        self.Num_w=(self.Len_message - self.wlen) // self.inc + 1

        # self.print_info()
        sptrRe, sptrIm = self.enframed_windowed_dft(signal_in) # Q^3

        # sptrRe, sptrIm = self.sptr_sub(sptrRe,sptrIm) # NIS^0.5 * Q^15
        # outSignal = self.overlap_add(sptrRe,sptrIm)
        # return outSignal

    def enframed_windowed_dft(self, signal_in):

        sptrRe = []         # wlen * Num_w  
        sptrIm = [] 
        window = self.get_hamming_window(self.wlen)     #  Q int
        print(window)
        input()
        # for index_w in tqdm(range(self.Num_w),desc = "Process 1 enframed and windowed"):
        #     temp = [0] * self.wlen
        #     for j in range(self.wlen):
        #         temp[j] = signal_in[index_w *self.inc + j] * window[j] # Q^2

        #     re, im = np.fft.fft(temp) # Q^3 
        #     sptrRe[index_w] = re
        #     sptrIm[index_w] = im

        # return sptrRe, sptrIm # Q^3

# np.fft.fft(y) 

        # def sptr_sub(self, sptrRe, sptrIm):
        #     amp_avg = [0] * self.wlen   # Q^6
        #     amp = []

        #     for i in tqdm(range(self.Num_w),desc = "Process 21 get amplitude"):
        #         amp_row = []
        #         for j in range(self.wlen):
        #             x = self.mul(sptrRe[i][j], sptrRe[i][j]) # Q^6
        #             y = self.mul(sptrIm[i][j], sptrIm[i][j]) # Q^6
        #             amp_row.append(x + y)
        #         amp.append(amp_row)

        #     for i in tqdm(range(self.wlen),desc = "Process 22 avg amplitude"):
        #         for j in range(self.NIS):
        #             amp_avg[i] = amp_avg[i] + amp[j][i] #  NIS * Q^6

        #     for i in tqdm(range(self.wlen),desc = "Process 23 remove nosie"):
        #         A_amp = self.A * amp_avg[i] # int * EncryptedNumber # NIS * Q^7
        #         B_amp = self.B * amp_avg[i] # NIS * Q^7

        #         for j in range(self.Num_w):
                    
        #             x = self.NIS * self.Q * amp[j][i] - A_amp # NIS * Q * Q^6 - NIS * Q^7 = NIS * Q^7
        #             x = self.big(x, B_amp)

        #             x = self.div(x, amp[j][i], self.Q ** 7) # (NIS * Q^7) / Q^6 * Q^7 = NIS * Q^8
        #             # print('x div = ', self.pvk.decrypt(x)/(self.NIS * self.Q ** 8))
        #             x = self.sqrt(x, self.Q ** 5) #  NIS^0.5 * Q^9
        #             # print('x sqrt = ', self.pvk.decrypt(x)/(self.NIS ** 0.5 * self.Q ** 9))

        #             sptrRe[j][i] = self.mul(sptrRe[j][i], x) # Q^6 * NIS^0.5 * Q^9 = NIS^0.5 * Q^15
        #             # print('x mul 15 = ', self.pvk.decrypt(sptrRe[j][i])/(self.NIS **0.5 * self.Q ** 15))
        #             # input()
        #             sptrIm[j][i] = self.mul(sptrIm[j][i], x) # NIS^0.5 * Q^15
        #     return sptrRe, sptrIm

            

        # def overlap_add(self, sptrRe, sptrIm): # NIS^0.5 * Q^15
        #     outSignal = [pbk.encrypt(0)] * self.Len_message 

        #     for i in tqdm(range(self.Num_w),desc = "Process 3 overlap add"):
        #         _, re = self.DFT(sptrIm[i], sptrRe[i])
        #         for j in range(self.wlen):
        #             outSignal[i * self.inc + j] = outSignal[i * self.inc + j] + re[j]

        #     return outSignal
            

        # def DFT(self, re_in, img_in = None):  # Q^2
        #     len_s = len(re_in)
        #     p = (-2 * math.pi) / len_s

        #     aux_re, aux_im = [], [] # Q int

        #     for i in range(len_s):
        #         row_re, row_im = [], []
        #         for j in range(len_s):
        #             x = int(math.cos(i * j * p) * self.Q)
        #             y = int(math.sin(i * j * p) * self.Q)
        #             row_re.append(x)
        #             row_im.append(y)
        #         aux_re.append(row_re)
        #         aux_im.append(row_im) # Q

        #     re, im = [0] * len_s, [0] * len_s
        #     for i in range(len_s):
        #         for j in range(len_s):
        #             x = re_in[j] * aux_re[i][j] # Q^3
        #             re[i] = re[i] + x
        #             y = re_in[j] * aux_im[i][j] 
        #             im[i] = im[i] + y
        #     if img_in:
        #         for i in range(len_s):
        #             for j in range(len_s):
        #                 x = -1 * aux_re[i][j] * img_in[j] # QQ
        #                 re[i] = re[i] + x
        #                 y = -1 * aux_im[i][j] * img_in[j] # QQ
        #                 im[i] = im[i] + y
        #     return re, im # Q^3


    def get_hamming_window(self, wlen):
        win = []
        p = (2 * math.pi) / (self.wlen - 1)
        for i in range(wlen):
            x = math.cos(p * i)
            x = self.alpha_hamming * x + (1 - self.alpha_hamming)
            x = x 
            win.append(x)
        return win # 1 * wlen int Q
        
        # def print_info(self):
        #     print()
        #     print('-'*40)
        #     print('Encrypted info:')
        #     print('Q: ',self.Q)
        #     print()

        #     print('siginal info:')
        #     print('Len_message:',self.Len_message)
        #     print('inc: ',self.inc)
        #     print('wlen: ',self.wlen)
        #     print('Num_w: ',self.Num_w)
        #     print()

        #     print('spec sub infor')
        #     print('A: ',self.A/self.Q)
        #     print('B: ',self.B/self.Q)
        #     print('NIS: ',self.NIS)
        #     print('alpha_hamming: ',self.alpha_hamming)
        #     print('-'*40)
        #     print()
            


# hjm test git

if __name__=='__main__':

    ft=SpecSub_plain(inc = args.inc,
                window_len=args.wlen, 
                a_in = args.a_in,
                b_in = args.b_in,
                NIS = args.NIS) #

    sigin=[]

    f = open(args.input, 'r')
    for  l in tqdm(f,desc = "Reading: "):
        sigin.append(float(l))
    f.close()
    sigin = np.array(sigin)

    sigout=ft.spec_sub(sigin)




    sigout=sigout-sigout.mean()

    sigout=sigout/max(abs(sigout))

    f = open(args.output, 'wt')
    for i in tqdm(sigout,desc = 'Storing'):
        f.write(str(i)+'\n')
    f.close()
    print("Done!")

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
