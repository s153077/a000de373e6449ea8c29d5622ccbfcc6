from scipy.signal import butter, filtfilt
from peakutils.peak import indexes
import numpy as np

def lowpass_butter_filter(data, Norder=5, lowcut=0.03):
	B, A = butter(Norder, Wn=lowcut, btype='lowpass', output='ba')
	return filtfilt(B,A, data)

def cubing_filter(data):
	return data**3 #power of three to reverse negative values

def PPG_Peaks(data, freq, plot=False):
	_data = data
	_data = lowpass_butter_filter(_data)
	_data = cubing_filter(_data)

	slice = 1/2
	peaks = indexes(_data, min_dist=freq*slice) # Heartbeat should not be faster than 120 BPM (2 Beats per second)
	peaks, amps = zip(*[getMax(data, i, freq) for i in peaks])

	if plot:
		plotData(data, _data, peaks)

	return peaks, amps

# Max value within a 0.5 frequency span (min-dist)
def getMax(data, i, freq):
	slice = 1/4
	h,j = int(max(i-(slice*freq),0)), int(min(i+(slice*freq), len(data)))
	_data = data[h:j]
	amp = max(_data)
	k = h + list(_data).index(amp)
	return k, amp

# Plot
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import preprocessing as p

def plotData(data, _data, peaks, i=0, j=45000):
	i,j = int(max(i,0)),int(min(len(data),j))
	x = range(i,j)
	plt.figure(figsize=(6.5, 4))
	nd = p.normalize(data[i:j]) ; plt.plot(x, nd, 'b-', label='data')
	nx = p.normalize(_data[i:j]) ; plt.plot(x, nx, 'g-', label='filter')
	ns = [ix for ix in peaks if i <= ix < j]
	plt.plot(ns, [nd[ix] for ix in ns], 'rx', label='peak')
	plt.legend()
	plt.show()