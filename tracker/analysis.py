import numpy as np
import pandas as pd
import pywt
import csv
from scipy import signal
from matplotlib import pyplot as plt
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image, io
from scipy.fftpack import fft, ifft
from sklearn.neighbors import KernelDensity
from scipy.stats import gaussian_kde
from matplotlib import cm
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from .models import Building, Event, Report


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
    # Read Data
    print("READ DATA")
    try:
        if len(top_acc) < 1000 or len(bot_acc) < 1000 or bot_acc is None:
            if event.acceleration_top_file is not None and event.acceleration_bot_file is not None:
                try:
                    top_parse = pd.read_table(event.acceleration_top_file)
                    bot_parse = pd.read_table(event.acceleration_bot_file)
                    top_acc = top_parse.values.squeeze()
                    bot_acc = bot_parse.values.squeeze()
                except Exception as error:
                    return error, "Error"
                else:
                    event.acceleration_top = top_acc.tolist()
                    event.acceleration_bot = bot_acc.tolist()
                    event.save()
            else:
                return "Your data may not have been parsed or is complete.", "Error"
        else:
            pass
    except Exception as error:
        print("DATA ERROR")
        return error, "Error"
    
    # Find Max
    try:
        event.intensity = round(max(top_bot), 3)
    except Exception as error:
        return error, "Error"
    else:
        event.save()

    # Fourier Transform
    print("FFT")
    try:
        top_fft = fft(top_acc)
        bot_fft = fft(bot_acc)
    except Exception as error:
        print("FFT ERROR")
        event.error = True
        even.save()
        return error, "Error"
    print("SMOOTH")
    try:
        temp_fourier_top = savitzky_golay(np.array(np.abs(top_fft)), smooth_str, smooth_deg)
        temp_fourier_bot = savitzky_golay(np.array(np.abs(bot_fft)), smooth_str, smooth_deg)
        temp_number = len(top_acc)
    except Exception as error:
        print("SMOOTH ERROR")
        event.error = True
        event.save()
        return error, "Error"
    else:
        event.fourier_top = temp_fourier_top.tolist()
        event.fourier_bot = temp_fourier_bot.tolist()
        event.number = temp_number
        event.save()

    print("TRANSFER FUNCTION")
    try:
        transfer_function = []
        for i in range(event.number):
            transfer_function.append(np.abs(top_fft[i]) / np.abs(bot_fft[i]))
    except Exception as error:
        event.error = True
        event.save()
        return error, "Error"
    else:
        event.transfer_function = transfer_function
        event.save()
    
    # Process Graph
    print("GRAPH")
    try:
        ### ADD GRAPH FUNCTION
        print("Missing Graph Function")
    except Exception as error:
        print("ERROR")
        return "Could not process graph", "Error"

    # Process Predominant Period
    ### REVIEW THIS CODE
    print("PREDOMINANT FREQUENCY")
    try:
        n = int((2*event.number)/32766)
        print(n)
        print(event.number)
        transfer_peak = max(event.transfer_function[50*n:1000*n])
        for n in range(len(event.fourier_top)):
            if (event.transfer_function[n] == transfer_peak):
                predominant_period = round(1/(n/event.number)/100, 3)
                break
    except Exception as error:
        event.error = True
        even.save()
        print("ERROR")
        return error, "Error"
    event.predominant_period = predominant_period
    event.error = False
    event.processed = True
    event.save()
    return "", "Complete"


# Buidldings
def AppendPeriod(building):
    try:
        events = Event.objects.all().filter(building=building).order_by('add_time')
        predominant_periods = []
        for event in events:
            if event.error is False and event.processed is True:
                if event.might_be_error is False or event.confirmed_not_error is True:
                    predominant_periods.append(event.predominant_period)
        building.predominant_periods = predominant_periods
        building.save()
        return "Periods Appended", "Complete"
    except Exception as err:
        return err, "Error"


def SmoothenPredominantPeriod(building):
    try:
        print(len(building.predominant_periods))
        period_len = len(building.predominant_periods)
        if period_len < 10:
            err = "There is not enough predominant period to significantly smoothen."
            return err, "Error"
        smoothen_bucket = building.predominant_periods[:4]
        smoothened = []
        for i in range(5, period_len, 1):
            smoothen_bucket.append(building.predominant_periods[i])
            smoothen_bucket.pop(0)
            smoothened.append(sum(smoothen_bucket)/len(smoothen_bucket))
    except Exception as err:
        return err, "Error"
    try:
        building.predominant_periods_smooth = smoothened
        building.save()
    except Exception as err:
        return err, "Error"
    print(building.predominant_periods_smooth)
    return "", "Complete"


def AveragePeriod(building):
    try:
        if len(building.predominant_periods) < 10:
            err = "There is not enough predominant period to significantly smoothen."
            return err, "Error"
        else:
            try:
                average = sum(building.predominant_periods_smooth)/len(building.predominant_periods_smooth)
                building.predominant_period_avg = average
                building.save()
            except Exception as err:
                return err, "Error"
    except Exception as err:
        return err, "Error"
    return "", "Complete"


def WarningSigns(building):
    try:
        if building.predominant_period_avg <= 0:
            err = "There is not enough data to determine building status."
            return err, "Error"
        else:
            try:
                percent_change = building.predominant_period_avg/building.predominant_periods_smooth[-1]
                if percent_change > 1.3:
                    building.warning_message = "Significant Lowering of Predominant Period!"
                    building.building_status = "Caution"
                elif percent_change > 1.6:
                    building.building_status = "Dangerous"
                    building.warning_message = "Extremely Significant Lowering of Predominant Period!"
                elif percent_change < 0.8:
                    building.building_status = "Abnormal"
                    building.warning_message = "Sifnificant Increase of Predominant Period!"
                elif percent_change < 0.6:
                    building.building_status = "Abnormal"
                    building.warning_message = "Extremely Significant Incrase of Predominant Period!"
                else:
                    building.building_status = "Good"
                    building.warning_message = "Everything seems fine"
                building.save()
                return "Warning Scanned", "Complete"
            except Exception as err:
                return err, "Error"
    except Exception as err:
        return err, "Error"

# Upload Event, Process Event, Append Period, Smoothen, Average_period, warning signs
# Function to compare event predominant frequency and ask if error