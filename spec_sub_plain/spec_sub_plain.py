import math
import numpy as np
import random
import copy

from utils.option import args
from tqdm import tqdm
import matplotlib.pyplot as plt
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
        
        sptrRe, sptrIm = self.sptr_sub(sptrRe,sptrIm) # NIS^0.5 * Q^15

        outSignal = self.overlap_add(sptrRe,sptrIm)
        return outSignal

    def enframed_windowed_dft(self, signal_in):

        sptrRe = []         # wlen * Num_w  
        sptrIm = [] 
        window = np.hamming(self.wlen)     #  Q int

        for index_w in tqdm(range(self.Num_w),desc = "Process 1 enframed and windowed"):
            temp = [0] * self.wlen
            for j in range(self.wlen):
                temp[j] = signal_in[index_w *self.inc + j] * window[j] # Q^2

            fft_out = np.fft.fft(temp) # Q^3
            re, im = fft_out.real, fft_out.imag

            sptrRe.append(re)
            sptrIm.append(im)

        return sptrRe, sptrIm # Q^3


    def sptr_sub(self, sptrRe, sptrIm):
        amp_avg = [0] * self.wlen   # Q^6
        amp = []

        for i in tqdm(range(self.Num_w),desc = "Process 21 get amplitude"):
            amp_row = []
            for j in range(self.wlen):
                x = sptrRe[i][j] * sptrRe[i][j]# Q^6
                y = sptrIm[i][j] *  sptrIm[i][j] # Q^6

                amp_row.append(x + y)
            amp.append(amp_row)

        for i in tqdm(range(self.wlen),desc = "Process 22 avg amplitude"):
            for j in range(self.NIS):
                amp_avg[i] = amp_avg[i] + amp[j][i] #  NIS * Q^6

        for i in tqdm(range(self.wlen),desc = "Process 23 remove nosie"):
            A_amp = self.A * amp_avg[i] # int * EncryptedNumber # NIS * Q^7
            B_amp = self.B * amp_avg[i] # NIS * Q^7

            for j in range(self.Num_w):
                 
                x = self.NIS  * amp[j][i] - A_amp # NIS * Q * Q^6 - NIS * Q^7 = NIS * Q^7
                x = max(x, B_amp)

                x = x / amp[j][i] # (NIS * Q^7) / Q^6 * Q^7 = NIS * Q^8
                # print('x div = ', self.pvk.decrypt(x)/(self.NIS * self.Q ** 8))
                x = x ** 0.5 #  NIS^0.5 * Q^9
                # print('x sqrt = ', self.pvk.decrypt(x)/(self.NIS ** 0.5 * self.Q ** 9))

                sptrRe[j][i] = sptrRe[j][i] * x # Q^6 * NIS^0.5 * Q^9 = NIS^0.5 * Q^15
                # print('x mul 15 = ', self.pvk.decrypt(sptrRe[j][i])/(self.NIS **0.5 * self.Q ** 15))
                # input()
                sptrIm[j][i] = sptrIm[j][i] * x # NIS^0.5 * Q^15
        return sptrRe, sptrIm

            

    def overlap_add(self, sptrRe, sptrIm): # NIS^0.5 * Q^15
        outSignal = [0] * self.Len_message 
        sptrRe = np.array(sptrRe)
        sptrIm = np.array(sptrIm)


        for i in tqdm(range(self.Num_w),desc = "Process 3 overlap add"):
            out_ifft = np.fft.fft(sptrRe[i] * 1j + sptrIm[i] )
            for j in range(self.wlen):
                outSignal[i * self.inc + j] = outSignal[i * self.inc + j] + out_ifft.imag[j]

        return np.array(outSignal)
            

def plot_signal(sigin, sigout):
    if len(sigin) < 500:
        plt.plot(sigin)
        plt.plot(sigout)
        plt.savefig('plain.png')
        return

    plt.plot(sigin)
    plt.plot(sigout)
    N = len(sigin) / 100
    plt.grid()

    plt.gca().margins(x=0)
    plt.gcf().canvas.draw()
    tl = plt.gca().get_xticklabels()
    maxsize = max([t.get_window_extent().width for t in tl])
    m = 0.2 # inch margin
    s = maxsize/plt.gcf().dpi*N+2*m
    margin = m/plt.gcf().get_size_inches()[0]

    plt.gcf().subplots_adjust(left=margin, right=1.-margin)
    plt.gcf().set_size_inches(s, plt.gcf().get_size_inches()[1])

    plt.savefig('plain.png')

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
    plot_signal(sigin, sigout)

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
