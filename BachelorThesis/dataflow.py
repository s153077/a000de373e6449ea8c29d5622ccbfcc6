from numpy import *
from features import epochs_from_prep, make_features
from epoch import epoch
from gru import gru, gru_config
from timeseries import timeseries, region, add_ECG_overhead
from dataset import dataset
from model_selection import add_predictions, reconstruct
from plots import plot_results
from log import Log, get_log
import filesystem as fs
import settings

"""
WRITTEN BY:
Nicklas Hansen
"""

def test_dataflow():
	X,y = fs.load_csv('mesa-sleep-2472')
	epochs = epochs_from_prep(X, y, settings.EPOCH_LENGTH, settings.OVERLAP_FACTOR, settings.SAMPLE_RATE, filter=False, removal=True)
	epochs = gru(load_graph=True).predict(epochs)
	epochs.sort(key=lambda x: x.index_start, reverse=False)
	yhat, _ = reconstruct(X, epochs)
	X,_,mask = make_features(X, None, settings.SAMPLE_RATE, removal=False)
	X = transpose(X)
	ss = X[6].copy()
	for i,_ in enumerate(ss):
		if X[7,i]:
			ss[i] = 2
		elif X[5,i]:
			ss[i] = 0
	plot_results(X[0]/settings.SAMPLE_RATE, [X[1], X[3], ss, yhat, y*(-1)], ['RR interval', 'PTT', 'Sleep stage', 'yhat', 'y'], region(X[5]), region(X[7]), None, None, int(X[0,-1]/settings.SAMPLE_RATE))

def dataflow(X, cmd_plot = False):
	epochs = epochs_from_prep(X, None, settings.EPOCH_LENGTH, settings.OVERLAP_FACTOR, settings.SAMPLE_RATE, filter=False, removal=True)
	epochs = gru(load_graph=True).predict(epochs)
	epochs.sort(key=lambda x: x.index_start, reverse=False)
	yhat, _ = reconstruct(X, epochs)
	summary = {}
	#summary = summary_statistics(X, epochs, yhat, wake, rem, illegal)
	X,_,mask = make_features(X, None, settings.SAMPLE_RATE, removal=False)
	X = transpose(X)
	ss = X[6].copy()
	for i,_ in enumerate(ss):
		if X[7,i]:
			ss[i] = 2
		elif X[5,i]:
			ss[i] = 0
	if cmd_plot:
		plot_results(X[0]/settings.SAMPLE_RATE, [X[1], X[3], ss, yhat, y*(-1)], ['RR interval', 'PTT', 'Sleep stage', 'yhat', 'y'], region(X[5]), region(X[7]), None, None, int(X[0,-1]/settings.SAMPLE_RATE))
	return X[0]/settings.SAMPLE_RATE, [X[1], X[3], ss, yhat, y*(-1)], ['RR interval', 'PTT', 'Sleep stage', 'yhat', 'y'], region(X[5]), region(X[7]), None, None, int(X[0,-1]/settings.SAMPLE_RATE), summary

def get_timeseries_prediction(X, model, y=None):
	epochs = epochs_from_prep(X, y, settings.EPOCH_LENGTH, settings.OVERLAP_FACTOR, filter = False, removal=True)
	epochs = model.predict(epochs)
	epochs.sort(key=lambda x: x.index_start, reverse=False)
	y, yhat, wake, rem, illegal, timecol = timeseries(epochs, epochs, settings.EPOCH_LENGTH, settings.OVERLAP_FACTOR, settings.SAMPLE_RATE)
	if y is not None:
		return epochs, y, yhat, wake, rem, illegal, timecol
	return epochs, yhat, wake, rem, illegal, timecol

def postprocess(timecol, yhat, combine = False, remove = False):
	prev, start, bin, n = None, 0, False, 0
	for i,p in enumerate(yhat):
		if p:
			if not bin:
				start, bin = i, True
		elif bin:
			bin = False
			curr = [start, i-1]
			if remove:
				timecol, yhat, n = conditional_remove(timecol, yhat, curr, n)
			if combine and prev is not None:
				timecol, yhat, n = conditional_combine(timecol, yhat, curr, prev, n)
			prev = [start, i-1]
	return yhat, n

def conditional_remove(timecol, yhat, curr, n):
	dur = timecol[curr[1]] - timecol[curr[0]]
	if dur < 1 * settings.SAMPLE_RATE:
		n += 1
		for j in range(curr[0], curr[1]+1):
			yhat[j] = 0
	return timecol, yhat, n
		

def conditional_combine(timecol, yhat, curr, prev, n):
	diff = timecol[curr[0]] - timecol[prev[1]]
	if diff < 3 * settings.SAMPLE_RATE:
		n += 1
		for j in range(prev[1], curr[0]):
			yhat[j] = 1
	return timecol, yhat, n



#time = [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800, 4000, 4400, 4600, 4800, 5000, 5200, 5400, 5600]
#y	 = [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0]

#yhat = postprocess(time, y)
#breakpoint = 0

def region(array, count = False):
	regions, start, bin, n = [], 0, False, 0
	for i,val in enumerate(array):
		if val == 1:
			if not bin:
				start, bin = i, True
		elif bin:
			bin = False
			n += 1
			regions.append([start, i-1])
			#if i-1-start <= 3 and start > 2:
			#	regions.append([start-2,i-1])
			#else:
			#	regions.append([start, i-1])
	if bin:
		regions.append([start, i])
		n += 1
	if count:
		return regions, n
	return regions






def summary_statistics(X, epochs, yhat, wake, rem, illegal):
	timecol = transpose(X)[0]
	rec_dur_float = ((timecol[-1]-timecol[0])/settings.SAMPLE_RATE)/60
	rec_dur = str(int(rec_dur_float)) + ' min'
	_, n_wake = region(wake, count = True)
	p_wake = n_wake/len(wake)
	pct_wake = str(int(p_wake*100)) + '%'
	_, n_rem = region(rem, count = True)
	pct_rem = str(int((n_rem/len(rem))*100)) + '%'
	_, n_ill = region(illegal, count = True)
	ill_score = str(int((n_ill/len(illegal))*(10**5)))
	arousals, n = region(yhat, count = True)
	n_arousals = len(arousals)
	arousals_hr = '{0:.1f}'.format(n_arousals/(rec_dur_float/60)*(1-p_wake))
	arousal_dur = []
	for arousal in arousals:
		arousal_dur.append(arousal[1] - arousal[0])
	return	[('rec_dur', rec_dur)
			,('pct_wake', pct_wake)
			,('pct_rem', pct_rem)
			,('n_arousals', str(n_arousals))
			,('arousals_hr', arousals_hr)
			,('avg_arousal', '{0:.1f}'.format(mean(arousal_dur)))
			,('med_arousal', '{0:.1f}'.format(median(arousal_dur)))
			,('std_arousal', '{0:.1f}'.format(std(arousal_dur)))
			,('ill_score', ill_score)
			]