from numpy import *
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

"""
WRITTEN BY:
Nicklas Hansen,
Michael Kirkegaard
"""

COLOR = ['black', 'orange', 'green', 'red']

def plot_results(timecol, signals, labels, wake_states, rem, illegals, arousals, duration = None, figure = None):
	if figure is None:
		ecg = plt.subplot(411)
		plt.Axes.autoscale(ecg, True, axis = 'y')
		show_signals(timecol, [signals[0]], [labels[0]], COLOR, duration)
		ptt = plt.subplot(412, sharex=ecg)
		plt.Axes.autoscale(ptt, True, axis = 'y')
		show_signals(timecol, [signals[1]], [labels[1]], COLOR, duration)
		aai = plt.subplot(413, sharex=ecg)
		plt.Axes.autoscale(aai, True, axis = 'y')
		show_signals(timecol, signals[3:], labels[3:], COLOR, duration)
		ssa = plt.subplot(414, sharex=ecg)
		plt.Axes.autoscale(ssa, True, axis = 'y')
		show_signals(timecol, [signals[2]], [labels[2]], COLOR, duration)
	else:
		ecg = figure.add_subplot(411)
		show_signals(timecol, [signals[0]], [labels[0]], COLOR, duration, a = ecg)
		ptt = figure.add_subplot(412, sharex=ecg)
		show_signals(timecol, [signals[1]], [labels[1]], COLOR, duration, a = ptt)
		aai = figure.add_subplot(413, sharex=ecg)
		show_signals(timecol, [signals[3]], [labels[3]], COLOR, duration, a = aai)
		ssa = figure.add_subplot(414, sharex=ecg)
		show_signals(timecol, [signals[2]], [labels[2]], COLOR, duration, a = ssa)

	ecg.set_xlim(0, duration/60)
	ecg.set_ylim(-0.25,1.25)
	ecg.set_ylabel('Normalised values')
	ecg.legend()

	ptt.set_xlim(0, duration/60)
	ptt.set_ylim(-0.25,1.25)
	ptt.set_ylabel('Normalised values')
	ptt.legend()

	aai.set_xlim(0, duration/60)
	aai.set_ylim(-1.25,1.25)
	aai.set_ylabel('Arousals')
	aai.legend()

	ssa.set_xlim(0, duration/60)
	ssa.set_ylim(-0.25,2.25)
	ssa.set_xlabel('Minutes')
	ssa.set_ylabel('Sleep stage')
	ssa.legend()

	plt.setp(ecg.get_xticklabels(), visible=False)
	plt.setp(ptt.get_xticklabels(), visible=False)
	plt.setp(aai.get_xticklabels(), visible=False)
	plt.Axes.autoscale(ssa, True, axis = 'y')
	if figure is None:
		plt.show()
	else:
		return figure

def show_signals(timecol, array, labels = None, colors = COLOR, duration = None, a = None):
	if array is None:
		return a
	if duration is None:
		duration = 0
		for i,signal in enumerate(array):
			if len(signal) > duration:
				duration = len(signal)
	x = timecol/60
	for i,signal in enumerate(array):
		linewidth = 1.8 if labels[i] == 'y' else 0.6
		if a is not None:
			a.plot(x, signal, colors[i], label=labels[i], linewidth=linewidth)
		else:
			plt.plot(x, signal, colors[i], label=labels[i], linewidth=linewidth)
	return a

def show_spans(timecol, array, color, alpha = 0.3, a = None):
	if array is None:
		return a
	x = timecol/60
	for _,obj in enumerate(array):
		if a is not None:
			a.axvspan(x[obj[0]], x[obj[1]], color=color, alpha=alpha)
		else:
			plt.axvspan(x[obj[0]], x[obj[1]], color=color, alpha=alpha)
	return a

def plot_data(signals, peaksIndexs=None, labels=None, normalization=False, indice = (0,10000)):
	def normalize(X, scaler=MinMaxScaler()):
		return squeeze(scaler.fit_transform(X.reshape(X.shape[0], 1)))

	for i,sig in enumerate(signals):
		if sig is not None:
			sig = sig[indice[0]:indice[1]]
			if normalization:
				sig = normalize(sig)
			signals[i] = sig

	color = ['b-', 'g-']
	peakcolor = ['rx','kx']
	for i,signal in enumerate(signals):
		if signal is not None:
			x = range(0,indice[1]-indice[0])
			plt.plot(x, signal, color[i], label=(labels[i] if labels else 'signal'+str(i+1)))
	if peaksIndexs != None:
		for i,peaks in enumerate(peaksIndexs):
			if peaks is not None and signals[i] is not None:
				peaks = [j for j in peaks[indice[0]:indice[1]] if indice[0] <= j <= indice[1]]
				plt.plot(peaks, [signals[i][j] for j in peaks], peakcolor[i],label=(labels[i]+' peaks' if labels else 'signal'+str(i+1)+' peaks'))
				plt.plot()
	plt.legend()
	plt.show()