import numpy as np 
import scipy.signal as sig 

# J. Beskow 2023
# Tube-to-formant calculation, after
# Liljencrants, J., & Fant, G. (1975). Computer program for VT-resonance frequency calculations. 
# STL-QPSR, 16, 15-21.

# 1: determinant based method
def wormfrek_det_vec(L,A,F,c):
    wc=2*np.pi*F/c
    v = wc*L[1]
    d1=1
    y = np.cos(v)-wc*L[0]*np.sin(v)
    for l,a,a_1 in zip(L[2:],A[2:],A[1:-1]):
        v1=v
        v = wc*l
        d2=d1
        d1=y
        kp=a/a_1
        bp=kp*np.sin(v)/np.sin(v1)
        dp=np.cos(v)+bp*np.cos(v1)
        y=dp*d1-bp*d2
    y = np.cos(np.arctan(y))**2
    return y

# 2: phase based method
def wormfrek_phase_vec(L,A,F,c):
    wc=2*np.pi*F/c
    vnp=np.arctan(wc*L[0])
    for l,a,a_1 in zip(L[1:],A[1:],A[0:-1]):
        vnp = wc*l + np.arctan(a*np.sin(vnp)/(a_1*np.cos(vnp)))
    y = np.sin(vnp)**2
    return y

def find_formants(L,A,method,topfreq,maxnrformants,c):
    l = [0]+L[:]
    a = [1]+A[:] 

    if len(L)!=len(A):
        print('the "lengths" and "areas" lists must be of equal length')
        exit(1)

    topfreq = args.samplerate/2

    # F: array of frequnecies to sample
    F = np.arange(1,topfreq)
    c = args.c

    if method=='determinant':
        Y = wormfrek_det_vec(l,a,F,c)
    elif method=='phase':
        Y = wormfrek_phase_vec(l,a,F,c)
    else:
        print('no such method')
        exit(1)
    
    # find the peaks of Y, these correspond to the formant locations
    fmt,_ = sig.find_peaks(Y,distance=100)
    fmt = fmt[:maxnrformants]
    return fmt


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('tuben',description = 'Calculate formant frequencies of vocal tract tube. VT specified by lists of lengths and areas of tubes, starting at the lips. ')
    parser.add_argument('-l','--lengths',help='list of tube segment lengths in cm',default='4,4,4,4')
    parser.add_argument('-a','--areas',help='list of tube segment areas in cm^2',default='2,2,2,2')
    parser.add_argument('-m','--method',help='method: "determinant" or "phase"',default='determinant')
    parser.add_argument('-n','--maxnrformants',help='max number of formants',type=int,default=4)
    parser.add_argument('-p','--plot',help='plot tube and peak function',action='store_true')
    parser.add_argument('-o','--output',help='output synthesized wavfile',default='')
    parser.add_argument('--synt-f0',help='synt. source frequency in Hz',type=float,default=70.0)
    parser.add_argument('--synt-dur',help='synt. duration in seconds',type=float,default=1.5)
    parser.add_argument('-fs','--samplerate',help='sample rate',type=float,default=16000)
    parser.add_argument('-c',help='speed of sound in cm/s',type=float,default=35300)
    args = parser.parse_args()

    # aa: --lengths 2,6,6,2 --areas 0.5,5,1,2
    # ii: --lengths 2,6,6,2 --areas 0.5,0.2,3,0.2
    # oo: --lengths 4,3,9,2 --areas 0.1,6,1,0.2
    # the tube segments are defined by the lists L (lengths, cm) and A (areas, cm^2)
    L = [float(l) for l in args.lengths.split(',')]
    A = [float(a) for a in args.areas.split(',')]

    if len(L)!=len(A):
        print('the "lengths" and "areas" lists must be of equal length')
        exit(1)

    topfreq = args.samplerate/2

    fmt = find_formants(L,A,args.method,topfreq,args.maxnrformants,args.c)

    print('formant frequencies (Hz): ', ', '.join([str(x) for x in fmt]))

    if args.plot:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

        fig, ax = plt.subplots(3,1)
        fig.tight_layout(pad=2.5)

        # plot tube
        x=0
        for l,a in zip(L,A):
            #ax[0].add_patch(Rectangle((x,-a/2),l,a,ls='--',ec='k'))
            ax[0].add_patch(Rectangle((x,0),l,a,ls='--',ec='k'))
            x += l

        ax[0].set_xlim([0,x])
        ax[0].set_ylim([0,max(A)*1.1])
        ax[0].set_title('tube')
        ax[0].set_xlabel('distancce from lips (cm)')
        ax[0].set_ylabel('area ($cm^2$)')

        # plot function & peaks
        ax[1].plot(F,Y,':')
        ax[1].plot(F[fmt],Y[fmt],'.')
        ax[1].set_title('peakfunction:' + args.method)
        ax[1].set_xlabel('frequency (Hz)')

        ax[2].set_title('transfer function')
        ax[2].set_xlabel('frequency (Hz)')
        ax[2].set_ylabel('dB')
        plt.sca(ax[2])

    if args.output:
        fs = args.samplerate
        import formantsynt
        import scipy.io.wavfile as wav 
        x = formantsynt.impulsetrain(fs,args.synt_f0, args.synt_dur)
        y = formantsynt.ffilter(fs,x,fmt,plot=args.plot)
        wav.write(args.output,fs,y)
        print('wrote:',args.output)

    if args.plot:
        plt.show()