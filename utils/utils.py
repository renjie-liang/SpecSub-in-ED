import datetime
import os
import re
import matplotlib.pyplot as plt
import numpy as np

from scipy.io import wavfile

def wgn(x, snr):
    P_signal = np.mean(x**2)
    P_noise = P_signal/(10**(snr/10.0))
    return np.random.randn(len(x)) * np.sqrt(P_noise)

def make_dir(args):
    if args.debug:
        return
    if not os.path.exists('runs'):
        os.mkdir('runs')

    now_time = datetime.datetime.now()
    now_time = datetime.datetime.strftime(now_time, '%Y-%m-%d %H-%M-%S')
    run_dir = args.name + '_dB' + str(args.noise_db) + '_' + now_time
    run_dir = os.path.join('runs', run_dir)

    os.mkdir(run_dir)
    os.mkdir(os.path.join(run_dir, 'output'+str(args.noise_db)+'dB'))
    os.mkdir(os.path.join(run_dir, 'images'+str(args.noise_db)+'dB'))
    os.mkdir(os.path.join(run_dir, 'noise'+str(args.noise_db)+'dB'))
    return run_dir


def get_img_namedir(file_name, run_dir, args):


    wav_name = re.split(r'[./]',file_name)[-2]

    output_name = os.path.join(run_dir, 'output'+str(args.noise_db)+'dB')
    noise_name = os.path.join(run_dir, 'noise'+str(args.noise_db)+'dB')
    img_name = os.path.join(run_dir, 'images'+str(args.noise_db)+'dB')

    output_name =  os.path.join(output_name, wav_name+'.wav')
    noise_name =  os.path.join(noise_name, wav_name+'.txt')
    img_name =  os.path.join(img_name, wav_name+'.png')
    return [output_name, noise_name, img_name]


def save_rslt(sigin_list, name_list, save_name_list):

    output_name, noise_name, img_name = save_name_list
    plot_signal(sigin_list, name_list, img_name ,len_plot = 20000, scale = 1000)


    f=open(noise_name,'wt')
    for ns in noise:
        f.write(str(ns)+'\n')
    f.close()

    wavfile.write(output_name,16000,sigout_encrypted)




def plot_signal(sigin_list, name_list,  img_name, len_plot = 1000, scale = 50):

    ls =  []
    for i in sigin_list:

        if len(i) > len_plot:
            ls.append(i[0:len_plot])
        else:
            ls.append(i)


    colors = ['r','g','b','k','y']
    N = len(ls[0])

    for i in range(len(ls)):
        
        ax = plt.subplot(len(ls),1, i+1)
        ax.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        if i < len(ls)-1:
            ax.get_xaxis().set_visible(False) #不显示x轴

        plt.plot(ls[i], linewidth=0.5, color = colors[i])
        ax.set_ylim(-2,2)
        ax.set_title(name_list[i],pad = 0.2)

        plt.grid()

        plt.gca().margins(x=0)


        # plt.gcf().subplots_adjust(left=0.03, right=1.-0.03)
        plt.gcf().set_size_inches(N/scale, plt.gcf().get_size_inches()[1])

    plt.savefig(img_name,dpi = 600)



