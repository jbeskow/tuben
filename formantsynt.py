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

def ffilter_super(fs, x, fmt, z=None, bw=100):
    sos = np.vstack([formant(f/fs, bw/fs) for f in fmt])
    if z is None:
        # Get the initial filter state scaled by the first sample of x
        z = sig.sosfilt_zi(sos) * x[0] if x.size > 0 else sig.sosfilt_zi(sos)

    y, z = sig.sosfilt(sos, x, zi=z)
    return y, z


def interpolate_formants(formant_sequence, steps, time=0.1):
    interpolated_sequence = [(formant_sequence[0])]
    # interpolated_sequence = []
    for i in range(len(formant_sequence) - 1):
        start_formant, start_duration = formant_sequence[i]
        end_formant, end_duration = formant_sequence[i + 1]

        # interpolated_sequence.append((start_formant,start_duration))
        for step in range(steps):
            ratio = step / float(steps)
            interpolated_formant = [s + ratio * (e - s) for s, e in zip(start_formant, end_formant)]
            interpolated_sequence.append((interpolated_formant, time / steps))

        interpolated_sequence.append((end_formant, end_duration))

    return interpolated_sequence


def synthesize_vowel_sequence(fs, formant_sequence, base_freq=175, steps=5):
    interpolated_sequence = interpolate_formants(formant_sequence, steps)
    total_duration = sum(duration for _, duration in interpolated_sequence)
    x = impulsetrain(fs, base_freq, total_duration)
    synthesized = np.zeros(int(fs * total_duration))

    start_index = 0
    z = None
    for fmt, duration in interpolated_sequence:
        segment_length = int(duration * fs)
        segment_end_index = start_index + segment_length
        segment = x[start_index:segment_end_index]

        # Apply the formant filter to the segment
        synthesized_segment, z = ffilter_super(fs, segment, fmt, z=z)
        synthesized[start_index:segment_end_index] = synthesized_segment

        start_index = segment_end_index
    synthesized /= np.max(np.abs(synthesized))
    wav.write('you.wav', fs, synthesized.astype(np.float32))
    return synthesized

def flaring(f_obs, l_short, r, sound_speed=35204):
    # take the leftmost section (lips) as input?
    l_inc = (sound_speed / (4 * f_obs)) - (l_short + 0.6 * r)
    return l_short + l_inc


if __name__ == '__main__':
    fs = 16000
    #change f in implusetrain to change f0
    x = impulsetrain(fs, 75, 1.5)
    wav.write('source.wav', fs, x)
    """
    y = ffilter(fs, x, [300, 600], 100)
    wav.write('o.wav', fs, y)
    y = ffilter(fs, x, [600, 950], 100)
    wav.write('a.wav', fs, y)
    """
    y = ffilter(fs, x, [250, 2200], plot=True)
    print(y[7500:9500])
    print(len(y))
    wav.write('i.wav', fs, y)
    # 118 and 183 are common male/female f0 from google
    # y = ffilter(fs, x, [200, 250, 2200], plot=True)
    # wav.write('i_m.wav', fs, y)
    # y = ffilter(fs, x, [183, 250, 2200], plot=True)
    # wav.write('i_f.wav', fs, y)
    fs = 16000
    # formant_sequence = [([300, 600], 1), ([250, 2200], 1), ([600, 950], 1)]
    formant_sequence = [
        ([800, 1200], 0.5),  # "how"
        ([730, 1090], 0.5),  # "are"
        ([300, 2000], 0.2),  # "y" part of "you"
        ([300, 870], 0.3)  # "ou" part of "you"
    ]
    sound = synthesize_vowel_sequence(fs, formant_sequence, steps=100)
    wav.write('howareyou.wav', fs, sound.astype(np.float32))
