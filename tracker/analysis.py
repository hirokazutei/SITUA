import numpy as np
import pandas as pd
import pywt
import csv
from scipy import signal
from matplotlib import pyplot as plt
from scipy.fftpack import fft,ifft
from sklearn.neighbors import KernelDensity
from scipy.stats import gaussian_kde
from matplotlib import cm


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    import numpy as np
    from math import factorial
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except Exception as error:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size - 1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


def AnalyzeEvent(event, top_acc, bot_acc, smooth_str=101, smooth_deg=2):
    print("FFT")
    try:
        top_fft = fft(top_acc)
        bot_fft = fft(bot_acc)
    except Exception as error:
        print("FFT ERROR")
        return error, "Error"
    print("SMOOTH")
    try:
        temp_fourier_top = savitzky_golay(np.array(np.abs(top_fft)), smooth_str, smooth_deg)
        temp_fourier_bot = savitzky_golay(np.array(np.abs(bot_fft)), smooth_str, smooth_deg)
        temp_number = len(top_acc) if top_acc <= bot_acc else bot_acc
    except Exception as error:
        print("SMOOTH ERROR")
        return error, "Error"
    else:
        event.fourier_top = temp_fourier_top.tolist()
        event.fourier_bot = temp_fourier_bot.tolist()
        event.number = temp_number
        event.save()
    print("TRANSFER FUNCTION")
    try:
        temp = []
        for i in range(event.number):
            temp.append(np.abs(top_fft[i]) / np.abs(bot_fft[i]))
    except Exception as error:
        return error, "Error"
    else:
        event.transfer_function = temp
        event.save()

"""
class Analysis:
    
    def __init__(self, data):
        self.data = data
        self.events = []
        self.peaks = []
    
    def processGraph(self, x1, x2, y1, y2, fmin, fmax, name, nesw, weird = None):
        T = 1.0 / 100.0
        plt.ylabel('Amplitude')
        plt.xlabel('Frequency')
        
        for e in range(len(self.data)):
            event = self.Event(self.data[e])
            if weird is True:
                event.readEvent(True)
            else:
                event.readEvent()
            event.smoothen(151, 2)
            event.divFFT()
            self.events.append(event)
            print(event.N)
            
            if nesw == 0:
                xf = np.linspace(0.0, (event.N//2)/100, len(event.xfft0[:event.N//2]))
                plt.grid()
                plt.plot(xf, event.xfft0[:event.N//2], linewidth=0.5)
                plt.axis([x1, x2, y1, y2])

                m = (max(event.xfft0[fmin:fmax]))
                for n in range(len(event.xfft0[0:fmax])):
                    if (event.xfft0[n] == m):
                        self.peaks.append([n/100, self.data[e]])
                        break
            elif nesw == 1:
                xf = np.linspace(0.0, (event.N//2)/100, len(event.xfft1[:event.N//2]))
                plt.grid()
                plt.plot(xf, event.xfft1[:event.N//2], linewidth=0.5)
                plt.axis([x1, x2, y1, y2])
        
                m = (max(event.xfft1[fmin:fmax]))
                for n in range(len(event.xfft1[0:fmax])):
                    if (event.xfft1[n] == m):
                        self.peaks.append([n/100, self.data[e]])
                        break
            elif nesw == 2:
                xf = np.linspace(0.0, (event.N//2)/100, len(event.xfft2[:event.N//2]))
                plt.grid()
                plt.plot(xf, event.xfft2[:event.N//2], linewidth=0.5)
                plt.axis([x1, x2, y1, y2])
        
                m = (max(event.xfft2[fmin:fmax]))
                for n in range(len(event.xfft2[0:fmax])):
                    if (event.xfft2[n] == m):
                        self.peaks.append([n/100, self.data[e]])
                        break
                        
        print(self.peaks)
        plt.title(name)
        plt.ylabel('Amplitude') # DONT FORGET TO MAKE IT PRING NS and WE DIRECTIONS
        plt.xlabel('Frequency')
        plt.show()
    
    def shortTimeFastFourier(self, x1, x2, y1, y2, nesw, tvmin = 5, tvmax = 15, windowtype = 'parzen'):
        fs = 1
        a = 0
        if nesw is 0:
            for i in self.events:
                topffsf, topffst, topffs = signal.stft(np.abs(i.topdata0.real), fs, window=windowtype, nperseg=1000, noverlap=None, return_onesided=True, boundary=None, padded=True, axis=-1)
                botffsf, botffst, botffs = signal.stft(np.abs(i.botdata0.real), fs, window=windowtype, nperseg=1000, noverlap=None, return_onesided=True, boundary=None, padded=True, axis=-1)

                ffsx = []
                for n in range(len(topffs)):
                    ffsx.append(np.abs(topffs[n].real) / np.abs(botffs[n].real))

                plt.pcolormesh(topffst/200, topffsf*100, np.abs(ffsx), vmin=tvmin, vmax=tvmax)
                plt.axis([x1, x2, y1, y2]) 
                plt.title('STFT Magnitude: ' + str(self.data[a]))
                a += 1
                plt.ylabel('Frequency')
                plt.xlabel('Time')
                plt.show()
        
        elif nesw is 1:
            for i in self.events:
                topffsf, topffst, topffs = signal.stft(i.topdata1.real, fs, window=windowtype, nperseg=1000, noverlap=None, return_onesided=True, boundary=None, padded=True, axis=-1)
                botffsf, botffst, botffs = signal.stft(i.botdata1.real, fs, window=windowtype, nperseg=1000, noverlap=None, return_onesided=True, boundary=None, padded=True, axis=-1)

                ffsx = []
                for n in range(len(topffs)):
                    ffsx.append(topffs[n] / botffs[n])

                plt.pcolormesh(topffst/200, topffsf*100, np.abs(ffsx), vmin=tvmin, vmax=tvmax)
                plt.axis([x1, x2, y1, y2])
                plt.title('STFT Magnitude: ' + str(self.data[a]))
                a += 1
                plt.ylabel('Frequency')
                plt.xlabel('Time')
                plt.show()

    def plotPeaks(self, x1, x2, y1, y2):
        array = []
        plt.ylabel('PreDominant Frequency')
        plt.xlabel('Data')
        
        for e in range(len(self.peaks)):
            array.append(self.peaks[e][0])
            print(self.peaks[e])
        plt.grid()
        plt.plot(array, linewidth=1)
        plt.axis([x1, x2, y1, y2])
        plt.title('Peaks')
        plt.show()
    
    def plotVibration(self, x1, x2, y1, y2, bottop = 'all', nesw = 9):
        for event in self.events:
            xf = np.linspace(0.0, (event.N//2)/100, len(event.botdata0))#[:event.N//2]))
            plt.grid()
            if bottop == 'bot':
                if nesw == 0 or nesw == 9:
                    plt.plot(xf, event.botdata0, linewidth=0.2)
                if nesw == 1 or nesw == 9:
                    plt.plot(xf, event.botdata1, linewidth=0.2)
            elif bottop == 'top':
                if nesw == 0 or nesw == 9:
                    plt.plot(xf, event.topdata0, linewidth=0.2)
                if nesw == 1 or nesw == 9:
                    plt.plot(xf, event.topdata1, linewidth=0.2)
            elif bottop == 'all':
                if nesw == 0 or nesw == 9:
                    plt.plot(xf, event.topdata0, linewidth=0.2)
                    plt.plot(xf, event.botdata0, linewidth=0.2)
                if nesw == 1 or nesw == 9:
                    plt.plot(xf, event.topdata1, linewidth=0.2)
                    plt.plot(xf, event.botdata1, linewidth=0.2)
        plt.axis([x1, x2, y1, y2])
        plt.title('Vibration')
        plt.show()
    
  
def countN(range1, range2, weird = False):
    Ns = []
    for e in range(range1, range2):
        if weird:
            botfloorfilename0 = "EventNo." + str(e) + "/data/acc/acc_ch0_gl.csv"
        else:
            botfloorfilename0 = "EventNo." + str(e) + "/data/acc/acc_-1_0_gal.txt"
        try:
            botinfile0 = open(botfloorfilename0, 'r')
        except Exception:
            continue
        botaccdata0 = pd.read_table(botinfile0)
        botdata0 = botaccdata0.values.squeeze()
        N = len(botdata0)
        #print(N)
        appended = False
        for i in range(len(Ns)):
            if Ns[i][0] == N:
                Ns[i].append(e)
                appended = True
        if not appended:
            Ns.append([N, e])
    return Ns
"""