from spec_sub_lrj import *

if __name__=='__main__':
    q=2**32
    ft=SpecSubED(PlaintextCloud(('127.0.0.1',9999)),
                inc = 80,
                window_len=200, 
                a_in = 4,
                b_in = 0.001,
                NIS = 23,
                quantizer=2**32) #
    pbk=ft.cloud.pbk
    pvk=ft.cloud.get_privatekey()

    sigin=[]

    
    f = open('./data/shortinput.txt', 'r')
    for index, l in enumerate(f):
        sigin.append(pbk.encrypt(int(float(l)*q)))
        print('Reading: {}|{}'.format(index,4000))
    f.close()
    #sigin # Q
    out=ft.spec_sub(sigin)
    sigout=[pvk.decrypt(i) for i in out]
    sigout=sigout-np.mean(sigout)
    sigout=sigout/max(abs(sigout))
    f = open('./data/shortoutput.txt', 'wt')
    for index,i in enumerate(sigout):
        f.write(str(i)+'\n')
        print('Storing: {}|{}'.format(index,4000))
    f.close()
    print("Done!")