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
    
    class Event:
        def __init__(self, num):
            self.num = num
            self.N = None
            self.smoothed = False
            self.botdata0 = []
            self.botdata1 = []
            self.botdata2 = []
            self.topdata0 = []
            self.topdata1 = []
            self.topdata2 = []
            self.fftb0 = []
            self.fftb1 = []
            self.fftb2 = []
            self.fftt0 = []
            self.fftt1 = []
            self.fftt2 = []
            self.xfft0 = []
            self.xfft1 = []
            self.xfft2 = []
        
        def readEvent(self, weird = False):
            #Set Up Directory and File Names:
            if weird:
                botfloorfilename0 = "EventNo." + str(self.num) + "/data/acc/acc_ch0_gl.csv"
                botfloorfilename1 = "EventNo." + str(self.num) + "/data/acc/acc_ch1_gl.csv"
                topfloorfilename0 = "EventNo." + str(self.num) + "/data/acc/acc_ch0_top.csv"
                topfloorfilename1 = "EventNo." + str(self.num) + "/data/acc/acc_ch1_top.csv"

            else:
                botfloorfilename0 = "EventNo." + str(self.num) + "/data/acc/acc_-1_0_gal.txt"
                botfloorfilename1 = "EventNo." + str(self.num) + "/data/acc/acc_-1_1_gal.txt"
                botfloorfilename2 = "EventNo." + str(self.num) + "/data/acc/acc_-1_2_gal.txt"
                topfloorfilename0 = "EventNo." + str(self.num) + "/data/acc/acc_9_0_gal.txt"
                topfloorfilename1 = "EventNo." + str(self.num) + "/data/acc/acc_9_1_gal.txt"
                topfloorfilename2 = "EventNo." + str(self.num) + "/data/acc/acc_9_2_gal.txt"
            
            #Read the files
            botinfile0 = open(botfloorfilename0, 'r')
            botinfile1 = open(botfloorfilename1, 'r')
            topinfile0 = open(topfloorfilename0, 'r')
            topinfile1 = open(topfloorfilename1, 'r')
            
            #Let Panas parse the file
            botaccdata0 = pd.read_table(botinfile0)
            botaccdata1 = pd.read_table(botinfile1)
            topaccdata0 = pd.read_table(topinfile0)
            topaccdata1 = pd.read_table(topinfile1)
            
            #Squeeze the Values
            self.botdata0 = botaccdata0.values.squeeze()
            self.botdata1 = botaccdata1.values.squeeze()
            self.topdata0 = topaccdata0.values.squeeze()
            self.topdata1 = topaccdata1.values.squeeze()
            
            #Add length of data as well as the FFT
            self.N = len(self.botdata0)
            self.fftb0 = fft(self.botdata0)
            self.fftb1 = fft(self.botdata1)
            self.fftt0 = fft(self.topdata0.real)
            self.fftt1 = fft(self.topdata1.real)
            
            if not weird:
                botinfile2 = open(botfloorfilename2, 'r')
                topinfile2 = open(topfloorfilename2, 'r')
                botaccdata2 = pd.read_table(botinfile2)
                topaccdata2 = pd.read_table(topinfile2)
                self.botdata2 = botaccdata2.values.squeeze()
                self.topdata2 = topaccdata2.values.squeeze()
                self.fftb2 = fft(self.botdata2)
                self.fftt2 = fft(self.topdata2)

            
        def smoothen(self, strength, degree): #101, 2
            self.fftb0 = savitzky_golay(np.array(np.abs(self.fftb0)), strength, degree)
            self.fftb1 = savitzky_golay(np.array(np.abs(self.fftb1)), strength, degree)
            self.fftt0 = savitzky_golay(np.array(np.abs(self.fftt0)), strength, degree)
            self.fftt1 = savitzky_golay(np.array(np.abs(self.fftt1)), strength, degree)
            if len(self.fftb2) != 0:
                self.fftb2 = savitzky_golay(np.array(np.abs(self.fftb2)), strength, degree)
                self.fftt2 = savitzky_golay(np.array(np.abs(self.fftt2)), strength, degree)
                self.botdata2 = savitzky_golay(np.array(np.abs(self.botdata2)), strength, degree)
                self.topdata2 = savitzky_golay(np.array(np.abs(self.topdata2)), strength, degree)

            
            self.botdata0 = savitzky_golay(np.array(np.abs(self.botdata0)), strength, degree)
            self.botdata1 = savitzky_golay(np.array(np.abs(self.botdata1)), strength, degree)
            self.topdata0 = savitzky_golay(np.array(np.abs(self.topdata0)), strength, degree)
            self.topdata1 = savitzky_golay(np.array(np.abs(self.topdata1)), strength, degree)
        
        def divFFT(self):
            temp = []
            for i in range(len(self.fftb0)):
                temp.append(np.abs(self.fftt0[i]) / np.abs(self.fftb0[i]))
            self.xfft0 = temp
            temp = []
            for i in range(len(self.fftb1)):
                temp.append(np.abs(self.fftt1[i]) / np.abs(self.fftb1[i]))
            self.xfft1 = temp
            temp = []
            if len(self.fftb2) is not 0:
                for i in range(len(self.fftb2)):
                    temp.append(np.abs(self.fftt2[i]) / np.abs(self.fftb2[i]))
                self.xfft2 = temp
                
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

counts = countN(1, 4200)
for i in counts:
    print (i)

    counts = countN(1, 4200, True)
for i in counts:
    print (i)

    workdataweird1 = [33, 43, 47, 48, 51]
workdataweird3 = [9, 14, 16, 24, 25, 26, 27, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45, 46, 49, 50]
workdataweird6 = [11]
workdata1 = [59, 64, 65, 81, 83, 87, 94, 95, 105, 142, 150, 157, 165, 166, 249, 275, 278, 287, 322, 328, 329, 336, 339, 358, 359, 360, 407, 411, 441, 455, 457, 461, 482, 559, 571, 576, 600, 748, 1644, 1653, 1705, 1730, 1762]
workdata3 = [54, 58, 60, 61, 62, 63, 66, 84, 86, 91, 93, 102, 104, 146, 148, 154, 159, 162, 164, 167, 243, 245, 248, 252, 280, 285, 290, 320, 321, 340, 343, 357, 384, 385, 388, 390, 397, 410, 433, 434, 440, 442, 466, 492, 529, 541, 563, 573, 591, 607, 710, 1225, 1648, 1660, 1670, 1696, 1701, 1714, 1725, 1734, 1739, 1749, 1756, 1764]
workdata6 = [82, 111, 136, 151, 260]
analysis = Analysis(workdataweird1)
analysis.processGraph(0, 12.5, 0, 60, 200, 4000, "Half Data: 0", 0, True)
analysis.plotPeaks(0, 40, 0, 20)

analysis = Analysis([142])
analysis.processGraph(0, 12.5, 0, 60, 200, 600, "Half Data: 0", 0)
ffta = "EventNo.142/data/fft/wacc_input_0_fft.txt"
fftb = "EventNo.142/data/fft/wacc_res_0_fft.txt"
a = open(ffta, 'r')
b = open(fftb, 'r')
fta = []
lines = a.read().split('\n')
"""
for line in range(len(lines) -1):
    fta.append(float(lines[line][-8:]))
a= savitzky_golay(np.array(np.abs(fta)), 101, 2)
    
plt.plot(a,linewidth=0.5)
plt.axis([0, 2400, 0, 0.01])

plt.show()
"""

ftb = []
lineb = b.read().split('\n')
for line in range(len(lineb) -1):
    ftb.append(float(lineb[line][-8:]))
b = savitzky_golay(np.array(np.abs(ftb)), 101, 2)
    
plt.plot(b,linewidth=0.5)
plt.axis([0, 1200, 0, 0.2])

plt.show()