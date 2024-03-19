from scipy import signal as sig
import scipy.io.wavfile as wav
import numpy as np
import matplotlib.pyplot as plt


# J. Beskow 2023
# Static vowel formant synthesis

# calculate 2-pole filter coefficients for a formant
# filter at freq f*fs with bandwidth b*fs
def formant(f, b):
    theta = 2 * np.pi * f
    r = np.exp(-np.pi * b)
    b0 = 1
    a1 = -2 * r * np.cos(theta)
    a2 = r ** 2
    return [b0, 0, 0, 1, a1, a2]  # scipy sos (second-order-section) format


# measure actual frequency and bandwith for formants
# sos is filter coefficients in sos form
def measurepeaks(fs, sos):
    w, h = sig.sosfreqz(sos, fs)
    f = w * fs / (2 * np.pi)
    db = 20 * np.log10(np.maximum(np.abs(h), 1e-5))
    peaks = sig.find_peaks(db)[0]
    res = []
    for ind, peak in enumerate(peaks):
        freq = f[peak]
        thres = db[peak] - 3  # 3 db threshold
        k = np.nonzero(np.diff(db > thres))[0]  # find where db curve crosses threshold
        n = np.digitize(peak, k)  # find crossing point interval containing the peak
        ival3db = [f[k[n - 1]], f[k[n]]]
        bw = ival3db[1] - ival3db[0]  # bandwidth is the width of this interval in Hz.
        # print('peak {}: freq {}, bandwidth {}'.format(ind,f[peak],bw))
        res.append({'freq': freq, 'bw': bw, 'top': db[peak], 'ival3db': ival3db})
    return res


# filter signal x with cascade formant filter, optinally plot
def ffilter(fs, x, fmt, bw=100, normalize=True, plot=False):
    if not isinstance(bw, list):
        bw = [bw] * len(fmt)
    sos = []
    for f, b in zip(fmt, bw):
        sos.append(formant(f / fs, b / fs))

        # plot frequency response and bandwidths
    if plot:
        peaks = measurepeaks(fs, sos)
        w, h = sig.sosfreqz(sos, fs)
        f = w * fs / (2 * np.pi)
        db = 20 * np.log10(np.maximum(np.abs(h), 1e-3))
        plt.plot(f, db)
        for p in peaks:
            plt.plot(p['freq'], p['top'], 'g.')
            plt.plot(p['ival3db'], [p['top'] - 3, p['top'] - 3], 'r.-')
        plt.show()

    y = sig.sosfilt(sos, x)
    if normalize:
        y /= np.max(np.abs(y))
    return y


def get_transfer_function(fs, fmt, bw=100):
    if not isinstance(bw, list):
        bw = [bw] * len(fmt)
    sos = []
    for f, b in zip(fmt, bw):
        sos.append(formant(f / fs, b / fs))

    w, h = sig.sosfreqz(sos, fs)
    f = w * fs / (2 * np.pi)
    hdb = 20 * np.log10(np.maximum(np.abs(h), 1e-3))
    return f, hdb


# impulse train source function
def impulsetrain(fs, f, duration):
    t = np.arange(int(fs * duration))
    x = (np.fmod(t, fs / f) < 1).astype(float)
    # fade in/out 0.1s
    ease = int(0.1 * fs)
    x[0:ease] *= np.linspace(0, 1, ease)
    x[-ease:] *= np.linspace(1, 0, ease)

    return x


if __name__ == '__main__':
    fs = 16000
    x = impulsetrain(fs, 72, 1.5)
    wav.write('source.wav', fs, x)
    """
    y = ffilter(fs, x, [300, 600], 100)
    wav.write('o.wav', fs, y)
    y = ffilter(fs, x, [600, 950], 100)
    wav.write('a.wav', fs, y)
    """
    y = ffilter(fs, x, [250, 2200], plot=True)
    wav.write('i.wav', fs, y)
    y = ffilter(fs, x, [118, 250, 2200], plot=True)
    wav.write('i_m.wav', fs, y)
    y = ffilter(fs, x, [183, 250, 2200], plot=True)
    wav.write('i_f.wav', fs, y)
