from model.spec_sub_plain import *
from scipy.io import wavfile
import glob
import utils.utils
import numpy as np

file=glob.glob('data/short/*')
file = file[0]

fq,sigin=wavfile.read(file)
sigin=sigin-np.mean(sigin)
sigin=sigin/max(abs(sigin))

noise=[]
f=open('arctic_a0001-swn.txt','r')
for l in f:
	noise.append(float(l))
f.close()

sig_ns=np.add(sigin,noise)

ft=SpecSub_plain(inc = 160,
                window_len=400, 
                a_in = 4,
                b_in = 0.001,
                NIS = 23)

outpd=ft.spec_sub(sig_ns)

fq,outed=wavfile.read('arctic_a0001-swn.wav')

name_list = ['input sigin','noise', 'sigin with noise', 'removed noise in plain']
sigin_list = [sigin, noise, sig_ns, outed]


utils.utils.plot_signal(sigin_list, name_list, 'test.png', len_plot = 20000, scale = 1000)