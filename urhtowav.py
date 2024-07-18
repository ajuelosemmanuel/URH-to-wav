#!/usr/bin/env python
# Emmanuel Ajuelos, 2021-2022

import math, wave, sys, os
import numpy as np
from scipy.signal import lfilter
from scipy.fftpack import fft
import matplotlib.pyplot as plt

def main(fpath = '', fs=1000000, downer=7):
    # Extension checking
    if not fpath.endswith(".complex"):
        raise ValueError("You should input a .complex file. Make sure it isn't a .complex16s file or something else.")
    
    # Checking if the file is too big (for some reason, it's not working if the file is "heavier" than 190MB)
    if os.path.getsize(fpath) > 190000000:
        raise ValueError("The file must have a size of 190MB or less.")
    
    # Reading the file with numpy
    c = np.fromfile(fpath, np.float32)
    I = c[0:min(len(c),23752362):2]
    Q = c[1:min(len(c),23752362):2]

    # Sampling I and Q
    Idown = I[0::downer]
    Qdown = Q[0::downer]

    # Demodulation
    a = [math.atan2(ely,elx) for ely, elx in zip(Qdown, Idown)]

    unwrap_atan2 = np.unwrap(a)
    strad = unwrap_atan2[1:] - unwrap_atan2[:-1]

    # create an order 6 Butterworth lowpass filter to remove unwanted stations, that
    # starts cutting at 0.2392*fs/2 and has the coefficients:
    b1 = [0.00073786 , 0.00442716, 0.01106791 , 0.01475721 , 0.01106791 , 0.00442716, 0.00073786]
    a1 = [1.000000 ,-3.183561 , 4.622162 , -3.779396 , 1.813557 , -0.479983 , 0.054443]
    
    # The coefficients are used like this:
    # a(1)*y(n) = b(1)*x(n) + b(2)*x(n-1) + ... + b(nb+1)*x(n-nb)
    # - a(2)*y(n-1) - ... - a(na+1)*y(n-na)
    # which is equivalent to the lfilter command below
    Ifilt = lfilter(b1,a1,I)
    Qfilt = lfilter(b1,a1,Q)

    # Same as above (line 24), but with a Butterworth filter
    Ifiltdown = Ifilt[::downer]
    Qfiltdown = Qfilt[::downer]
    b = [math.atan2(ely,elx) for ely, elx in zip(Qfiltdown,Ifiltdown)]
    unwrap_atan2_down = np.unwrap(b)
    stradfilt = unwrap_atan2_down[1:] - unwrap_atan2_down[:-1]

    #SpecFM is the spectrum of the demodulated signal
    specFM = np.abs(fft(stradfilt))

    freq = np.array(range(len(stradfilt))) *1.0 / len(stradfilt) * (fs *1.0 / downer)
    return specFM, strad, stradfilt, freq

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:  ./urhtowav.py file")
        sys.exit(0)
    fs = 1000000
    downer = 7
    specFM, strad, stradfilt, freq = main(sys.argv[1],fs, downer)
    
    # Output .wav files of the resulting audio
    # Audio without using the Butterworth filter
    f = wave.open("strad-"+sys.argv[1].replace(".complex", "").replace("/", "").replace(".", "").replace("\\", "") +".wav", "wb")
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(fs * 1.0 / downer)
    factor = 16383.0 / max(abs(strad.max()),abs(strad.min()))
    f.writeframes((strad * factor).astype(np.int16).tobytes())
    f.close()
    
    # Audio using the Butterworth filter
    f = wave.open("stradfilt-"+sys.argv[1].replace(".complex", "").replace("/", "").replace(".", "").replace("\\", "")+".wav", "wb")
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(fs * 1.0 / downer)
    factor = 16383.0 / max(abs(stradfilt.max()),abs(stradfilt.min()))
    f.writeframes((stradfilt * factor).astype(np.int16).tobytes())
    f.close()
    
#plt.plot([1,2,3,4], [1,4,9,16])
# Plot the spectrum of the demodulated signal. You should see a monaural bump at low
# frequency, a pilot carrier at 19 kHz, a stereo bump at 38 kHz, and, on some stations,
# an RDS bump at 57 kHz.
plt.plot(freq, specFM)
plt.show()