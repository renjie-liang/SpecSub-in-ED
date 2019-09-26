import os
# import math
from tqdm import tqdm
import re
# # from phe import paillier

from lib.twocloud_client import PlaintextCloud
# # import numpy as np
# # import random

#import matplotlib.pyplot as plt

from utils.option import args
import logging
import glob

from model.spec_sub_encrypted import SpecSubED
from model.spec_sub_plain import SpecSub_plain

from utils.utils import *
run_dir = make_dir(args)

file_list = glob.glob(args.input_dir + '*')

# a = 4-SNR*3/20

specsub_plain=SpecSub_plain(inc = args.inc, 
                    window_len=args.wlen, 
                    a_in = args.a_in,
                    b_in = args.b_in,
                    NIS = args.NIS) 

# specsub_encrypted=SpecSubED(PlaintextCloud(('127.0.0.1',9999)),
#             inc = args.inc,
#             window_len=args.wlen, 
#             a_in = args.a_in,
#             b_in = args.b_in,
#             NIS = args.NIS,
#             quantizer=args.quantizer)

# pbk=specsub_encrypted.cloud.pbk
# pvk=specsub_encrypted.cloud.get_privatekey()

print(file_list)
input()
for index_f, file in enumerate(file_list):
    print('\nWav:{}|{}'.format(index_f,len(file_list)-1))

    fq,sigin=wavfile.read(file)
    
    sigin=sigin-np.mean(sigin)
    sigin=sigin/max(abs(sigin))

    print('Plain:')
    sigout_plain=specsub_plain.spec_sub(sigin)

    noise=wgn(sigin,args.noise_db)
    sig_ns=np.add(sigin,noise)

    # sigin_en = []
    # print('Encrypted:')
    # for i in tqdm(sig_ns, desc = 'trans data'):
    #     sigin_en.append(pbk.encrypt(int(i*args.quantizer)))

    # sigout_encrypted=specsub_encrypted.spec_sub(sigin_en)


    if args.debug:
        continue
    save_name_list = get_img_namedir(file, run_dir, args)

    name_list = ['input sigin','noise', 'sigin with noise', 'removed noise in plain']
    sigin_list = [sigin, noise, sig_ns, sigout_plain]
    save_rslt(sigin_list, name_list, save_name_list)
    # sigin = np.array(sigin)
    # sigout=ft.spec_sub(sigin)

