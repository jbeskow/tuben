import numpy as np 
import scipy.signal as sig
import scipy.io.wavfile as wav 
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import formantsynt
import pandas as pd


# J. Beskow 2023
# Tube-to-formant calculation, after
# Liljencrants, J., & Fant, G. (1975). Computer program for VT-resonance frequency calculations. 
# STL-QPSR, 16, 15-21.

class tuben:
    def __init__(self, method='determinant', maxnrformants=4, samplerate = 16000, topfreq = 8000, c=35300):
        self.method = method
        self.maxnrformants = maxnrformants
        self.fs = samplerate
        self.topfreq = topfreq
        self.c = c
        self.F = np.arange(1,self.topfreq)

    # 1: determinant based method
    def _wormfrek_det_vec(self,L,A):
        wc=2*np.pi*self.F/self.c
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
    def _wormfrek_phase_vec(self,L,A):
        wc=2*np.pi*self.F/self.c
        vnp=np.arctan(wc*L[0])
        for l,a,a_1 in zip(L[1:],A[1:],A[0:-1]):
            vnp = wc*l + np.arctan(a*np.sin(vnp)/(a_1*np.cos(vnp)))
        y = np.sin(vnp)**2
        return y

    def set_tube(self,L,A):
        if type(L)!=list or type(A)!=list:
            print('bad input')
            import pdb;pdb.set_trace()
        self.L = L
        self.A = A
        self.updated = False

    # use one of the two methods to find resonances of tube

    def update(self):
        if not self.updated:
            l = [0]+self.L[:]
            a = [1]+self.A[:] 
            if self.method=='determinant':
                self.Y = self._wormfrek_det_vec(l,a)
            elif self.method=='phase':
                self.Y = self._wormfrek_phase_vec(l,a)
            else:
                print('no such method')
                exit(1)
            
            # find the peaks of Y, these correspond to the formant locations
            fmt,_ = sig.find_peaks(self.Y,distance=100)
            self.fmt = fmt[:self.maxnrformants]
            self.updated = True
    
    def get_formants(self,L=None,A=None):
        if L is not None and A is not None:
            #print('L:',L,len(L),'A:',A,len(A))
            self.set_tube(L,A)
        self.update()
        #print('FMT:',self.fmt)
        return self.fmt,self.Y

    def plot(self):
        self.update()

        fig, ax = plt.subplots(3,1)
        fig.tight_layout(pad=2.5)

        # plot tube
        x=0
        for l,a in zip(self.L,self.A):
            ax[0].add_patch(Rectangle((x,0),l,a,ls='--',ec='k'))
            x += l

        ax[0].set_xlim([0,x])
        ax[0].set_ylim([0,max(self.A)*1.1])
        ax[0].set_title('tube')
        ax[0].set_xlabel('distance from lips (cm)')
        ax[0].set_ylabel('area ($cm^2$)')

        # plot function & peaks
        ax[1].plot(self.F,self.Y,':')
        ax[1].plot(self.F[self.fmt],self.Y[self.fmt],'.')
        ax[1].set_title('peakfunction:' + self.method)
        ax[1].set_xlabel('frequency (Hz)')

        ax[2].set_title('transfer function')
        ax[2].set_xlabel('frequency (Hz)')
        ax[2].set_ylabel('dB')
        plt.sca(ax[2])
        f,h = formantsynt.get_transfer_function(self.fs,self.fmt)
        ax[2].plot(f,h)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('tuben',description = 'Calculate formant frequencies of vocal tract tube. VT specified by lists of lengths and areas of tubes, starting at the lips. ')
    parser.add_argument('-l','--lengths',help='list of tube segment lengths in cm',default='')
    parser.add_argument('-a','--areas',help='list of tube segment areas in cm^2',default='')
    parser.add_argument('-t','--table',help='table of areas in csv format',default='Fant1971.csv')
    parser.add_argument('-s','--symbol',help='symbol in table to synthesize',default='a')
    parser.add_argument('-m','--method',help='method: "determinant" or "phase"',default='determinant')
    parser.add_argument('-n','--maxnrformants',help='max number of formants',type=int,default=4)
    parser.add_argument('-p','--plot',help='plot tube and peak function',action='store_true')
    parser.add_argument('-v','--verbose',help='more output',action='store_true')
    parser.add_argument('-o','--output',help='output synthesized wavfile',default='out.wav')
    parser.add_argument('--synt-f0',help='synt. source frequency in Hz',type=float,default=70.0)
    parser.add_argument('--synt-dur',help='synt. duration in seconds',type=float,default=1.5)
    parser.add_argument('-fs','--samplerate',help='sample rate',type=float,default=16000)
    parser.add_argument('-c',help='speed of sound in cm/s',type=float,default=35300)
    args = parser.parse_args()

    tub = tuben(args.method,args.maxnrformants,args.samplerate,args.samplerate/2,args.c)

    # the tube segments are defined by the lists L (lengths, cm) and A (areas, cm^2) lip-to-glottis

    # if table is given, read it and get the areas for the symbol
    if args.table != '':

        try:
            df = pd.read_csv(args.table)
        except:
            print('could not read table:',args.table)
            exit(1)

        if args.symbol in df.columns:
            # get areas for symbol
            A = df[args.symbol].dropna().tolist()
            cm = df['cm'].dropna().tolist()
            # get tube lengths from differences in cm
            L = [t-s for s,t in zip(cm,cm[1:])]
            L = L[0:len(A)]
        else:
            print('no such symbol:',args.symbol)
            exit(1)

    # if areas or lengths are given as arguments, they will override the table
    if args.areas != '':
        A = [float(a) for a in args.areas.split(',')]
    if args.lengths != '':
        L = [float(l) for l in args.lengths.split(',')]
        if len(L) == 1 and len(A) > 1:
            L = [L[0]]*len(A)

    if len(L) != len(A):
        print('"lengths" and "areas" don\'t match', 'L:',L,'A:',A)
        exit(1)

    if args.verbose:
        print('lenths:',L)
        print('areas:',A)

    fmt,Y = tub.get_formants(L,A)
    print('formant frequencies (Hz): ', ', '.join([str(x) for x in fmt]))

    if args.output:
        fs = args.samplerate
        x = formantsynt.impulsetrain(fs,args.synt_f0, args.synt_dur)
        y = formantsynt.ffilter(fs,x,fmt)
        wav.write(args.output,fs,y)
        print('wrote:',args.output)

    if args.plot:
        tub.plot()
        plt.show()
