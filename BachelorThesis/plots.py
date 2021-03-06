'''
AUTHOR(S):
Nicklas Hansen,
Michael Kirkegaard

Module is responsible for creating figures and plots for evaluation and testing purposes, as well as for the GUI.
'''

from numpy import *
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

COLOR = ['black', 'orange', 'green', 'red']
def plot_results(timecol, signals, labels, wake_states, rem, illegals, arousals, duration = None, figure = None):
	'''
	Plotting of signals (with labels) into subplots with a shared x-axis.
	Function returns a figure if one is given, as is the case of the GUI.
	'''
	if figure is None:
		rr = plt.subplot(611)
		plt.Axes.autoscale(rr, True, axis = 'y')
		show_signals(timecol, [signals[0]], [labels[0]], COLOR, duration)
		rwa = plt.subplot(612, sharex=rr)
		plt.Axes.autoscale(rr, True, axis = 'y')
		show_signals(timecol, [signals[1]], [labels[1]], COLOR, duration)
		ptt = plt.subplot(613, sharex=rr)
		plt.Axes.autoscale(rr, True, axis = 'y')
		show_signals(timecol, [signals[2]], [labels[2]], COLOR, duration)
		pwa = plt.subplot(614, sharex=rr)
		plt.Axes.autoscale(rr, True, axis = 'y')
		show_signals(timecol, [signals[3]], [labels[3]], COLOR, duration)
		ssa = plt.subplot(615, sharex=rr)
		plt.Axes.autoscale(rr, True, axis = 'y')
		show_signals(timecol, [signals[4]], [labels[4]], COLOR, duration)
		aai = plt.subplot(616, sharex=rr)
		plt.Axes.autoscale(rr, True, axis = 'y')
		try:
			show_signals(timecol, signals[5:], labels[5:], COLOR, duration)
		except Exception as e:
			show_signals(timecol, [signals[5]], [labels[5]], COLOR, duration)
	else:
		rr = figure.add_subplot(611)
		show_signals(timecol, [signals[0]], [labels[0]], COLOR, duration, a = rr)
		rwa = figure.add_subplot(612, sharex=rr)
		show_signals(timecol, [signals[1]], [labels[1]], COLOR, duration, a = rwa)
		ptt = figure.add_subplot(613, sharex=rr)
		show_signals(timecol, [signals[2]], [labels[2]], COLOR, duration, a = ptt)
		pwa = figure.add_subplot(614, sharex=rr)
		show_signals(timecol, [signals[3]], [labels[3]], COLOR, duration, a = pwa)
		ssa = figure.add_subplot(615, sharex=rr)
		show_signals(timecol, [signals[4]], [labels[4]], COLOR, duration, a = ssa)
		aai = figure.add_subplot(616, sharex=rr)
		show_signals(timecol, [signals[5]], [labels[5]], COLOR, duration, a = aai)

	stretch = 0.05
	rr.set_xlim(0, duration/60)
	rr.set_ylim(0-stretch,1+stretch)
	rr.set_ylabel('Norm. val.')
	rr.legend()

	rwa.set_xlim(0, duration/60)
	rwa.set_ylim(0-stretch,1+stretch)
	rwa.set_ylabel('Norm. val.')
	rwa.legend()

	ptt.set_xlim(0, duration/60)
	ptt.set_ylim(0-stretch,1+stretch)
	ptt.set_ylabel('Norm. val.')
	ptt.legend()

	pwa.set_xlim(0, duration/60)
	pwa.set_ylim(0-stretch,1+stretch)
	pwa.set_ylabel('Norm. val.')
	pwa.legend()

	ssa.set_xlim(0, duration/60)
	ssa.set_ylim(0-stretch,2+stretch)
	ssa.set_ylabel('Sleep stage')
	ssa.legend()

	aai.set_xlim(0, duration/60)
	aai.set_ylim(0-stretch,1+stretch) if 'y' not in labels else aai.set_ylim(-1-stretch,1+stretch)
	aai.set_xlabel('Minutes')
	aai.set_ylabel('Arousals')
	aai.legend()

	plt.setp(rr.get_xticklabels(), visible=False)
	plt.setp(rwa.get_xticklabels(), visible=False)
	plt.setp(ptt.get_xticklabels(), visible=False)
	plt.setp(pwa.get_xticklabels(), visible=False)
	plt.setp(ssa.get_xticklabels(), visible=False)
	if figure is None:
		plt.show()
	else:
		figure.tight_layout()
		return figure

def show_signals(timecol, array, labels = None, colors = COLOR, duration = None, a = None):
	'''
	Plots a given signal to a subplot with corresponding time axis.
	'''
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
		signal = signal * -1 if labels[i] == 'y' else signal
		if a is not None:
			a.plot(x, signal, colors[i], label=labels[i], linewidth=linewidth)
		else:
			plt.plot(x, signal, colors[i], label=labels[i], linewidth=linewidth)
	return a

def plot_data(signals, peaksIndexs=None, labels=None, normalization=False, indice = (0,10000)):
	'''
	Plots list of signals (with labels) and marked peaks into a plot
	'''
	def normalize(X, scaler=MinMaxScaler()):
		return squeeze(scaler.fit_transform(X.reshape(X.shape[0], 1)))

	for i,sig in enumerate(signals):
		if sig is not None:
			sig = sig[indice[0]:indice[1]]
			if normalization:
				sig = normalize(sig)
			signals[i] = sig

	color = ['b-','k-', 'g-', 'y-']
	peakcolor = ['ro','yo','gx', 'rx']
	for i,signal in enumerate(signals):
		if signal is not None:
			x = range(0,indice[1]-indice[0])
			plt.plot(x, signal, color[i], label=(labels[i] if labels else 'signal'+str(i+1)))
	if peaksIndexs != None:
		for i,peaks in enumerate(peaksIndexs):
			k = i if len(signals) > i else len(signals)-1
			if peaks is not None and signals[k] is not None:
				peaks = [j for j in peaks if indice[0] <= j <= indice[1]]
				plt.plot(peaks, [signals[k][j] for j in peaks], peakcolor[i],label=(labels[i]+' peaks' if labels else 'signal'+str(i+1)+' peaks'))
				plt.plot()
	plt.legend()
	plt.show()