import datetime
import os
import re
import matplotlib.pyplot as plt

def make_dir(args):
    if args.debug:
        return
    if not os.path.exists('runs'):
        os.mkdir('runs')

    now_time = datetime.datetime.now()
    now_time = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
    run_dir = args.name + '_dB' + args.noise_db + '_' + now_time
    run_dir = os.path.join('runs', run_dir)

    os.mkdir(run_dir)
    os.mkdir(os.path.join(run_dir, 'output'+args.noise_db+'dB'))
    os.mkdir(os.path.join(run_dir, 'images'+args.noise_db+'dB'))
    return run_dir


def get_img_namedir(file_name, run_dir, args):


    wav_name = re.split(r'[./]',file_name)[-2]

    output_name = os.path.join(run_dir, 'output'+args.noise_db+'dB')
    img_name = os.path.join(run_dir, 'images'+args.noise_db+'dB')

    output_name =  os.path.join(output_name, wav_name+'.wav')
    img_name =  os.path.join(img_name, wav_name+'.png')
    return [output_name, img_name]

def save_plot(sigin, sigout_plain, sigout_encrypted, names_list):
    output_name, img_name = names_list
    plot_signal(sigin, sigout_plain, sigout_encrypted, img_name)
    save_wave(sigin, sigout_plain, sigout_encrypted, output_name)

def save_wave(sigin, sigout_plain, sigout_encrypted, output_name):
    pass

def plot_signal(sigin, sigout_plain, sigout_encrypted, img_name):

    colors = ['r','g','b']
    ls = [sigin, sigout_plain, sigout_encrypted]
    N = len(sigin)

    for i in range(3):
        
        plt.subplot(3,1, i+1)
        plt.plot(ls[i], linewidth=0.5, color = colors[i])

        plt.grid()

        plt.gca().margins(x=0)

        # plt.gcf().subplots_adjust(left=0.03, right=1.-0.03)
        plt.gcf().set_size_inches(N/100, plt.gcf().get_size_inches()[1])

    plt.savefig(img_name,dpi = 600)



