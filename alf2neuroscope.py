# -*- coding: utf-8 -*-
"""
alf2neuroscope.py sample_rate destination_directory source_directory1 source_directory2 ...
Reads files in ALF (ALyx Format) and converts them so you can load them into neurosope.
Works recursively on all source directories, finding any .npy files within any subdirectories
Writes neuroscope.dat, neuroscope.evt.evt, neuroscope.res.*, neuroscope.clu.* to destination_directory
for sample_rate, recommendation is 1250.

For documentation on ALF see http://[soon-to-be written documentation website]
For documentation on neuroscope see http://neuroscope.sourceforge.net/UserManual/data-files.html
"""

"""
Created on Wed Jul 26 18:03:28 2017

@author: Kenneth D. Harris @kdharris101 - my first real pyton program!
"""



import sys
import os
import numpy as np
import scipy.interpolate as ip


def main():
    sample_rate = sys.argv[1]
    target_dir = sys.argv[2]
    source_dirs = sys.argv[3:]

    #source_dir = r'\\zserver.cortexlab.net\data\expInfo\Robbins\2017-06-13\1'
    # source_dirs = [r'\\zserver.cortexlab.net\Data\EyeCamera\Robbins\2017-06-13\1', \
    # 	r'\\zserver.cortexlab.net\data\expInfo\Robbins\2017-06-13\1', \
    #     r'\\zserver\Data\Subjects\Robbins\2017-06-13']
    # target_dir = '.'
    sample_rate = '1250'


    dt = 1.0/float(sample_rate)

    # find directories recursively
    walkout = [i for d in source_dirs for i in os.walk(d)]
    print("directory: " + '\ndirectory: '.join([w[0] for w in walkout]))

    # files[] is list of tuples storing full file name, file split into words, and home directory 

    files =  [ (os.path.join(wa[0], f), f.split('.'), wa[0] ) \
                for wa in walkout for f in wa[2] if f.endswith('.npy')]

    filebases = set([f[1][0] for f in files])
    spike_files = [f for f in files if f[1][:2] == ['spikes', 'times']]
    event_files = [f for f in files if f[1][1] == 'times' and not f[1][0] == 'spikes']
    interval_files = [f for f in files if f[1][1] == 'intervals' and not f[1][0] == 'spikes']
    timestamp_files = [f for f in files if f[1][1] == 'timestamps']
     
    # CONTINUOUS TIMESERIES 
    # first load each timestamps file and make list of interpolator functions
    interp_fn = []
    max_t = 0
    print('Loading timestamps...')
    for f in timestamp_files:

        ts = np.load(f[0]) 

        # interp_fn[i] converts time to samples for the i'th file, returns nan if out of bounds
        # a list of functions - gotta love python
        interp_fn.append(ip.interp1d(ts[:,1], ts[:,0], bounds_error=False, axis=0))
            
        # keep track of max time
        max_t = max(max_t,ts[:,1].max())

    # sample times in universal seconds
    t = np.arange(0,max_t,dt) 

    ch_file = open(os.path.join(target_dir, 'dat_channel_list.txt'), 'w')
    all_chans = [] # list to contain all all_chans, resampled files
    c = 0 # to keep track of channel numbers
    for i,f in enumerate(timestamp_files):
        # load all the other files for this timestamp file

        series_files = [sf for sf in files \
            if sf[1][0]==f[1][0] and not sf[1][1].startswith('timestamps')]
    		
        array_list = [np.load(f[0]) for f in series_files]
        data = np.concatenate(array_list, axis=1)

        for j in range(len(array_list)):
            print ('Channel %d: %s.%s' % (c, series_files[j][1][0], series_files[j][1][1]))
            ch_file.write('Channel %d: %s.%s\n' % (c, series_files[j][1][0], series_files[j][1][1]))
            c += array_list[j].shape[1]

        # find time coordinates for this timescale
        my_t = interp_fn[i](t)
        my_t[np.isnan(my_t)] = 0 # overwrite out of bounds with first sample value


        resampled = data[my_t.astype(int),:]
        shifted = resampled - np.nanmedian(resampled,axis=0,keepdims=1)
        scaled = (2.0**15)*shifted/(1e-20 + np.nanmax(np.abs(shifted),axis=0,keepdims=1))

        # now convert to unit 16 and save
        all_chans.append(scaled.astype('int16'))
        
    ch_file.close()

    print('%d channels total' % c)

    # we have all the data on the same timescale. Append them and save
    out = open(os.path.join(target_dir, 'neuroscope.dat'), 'w')
    np.concatenate(all_chans, axis=1).tofile(out)
    out.close();

    ## SPIKE FILES
    ri_file = open(os.path.join(target_dir, 'clu_file_list.txt'), 'w')
    for n,f in enumerate(spike_files):

        # load data        
        times = np.load(f[0])
        cluster_file = [c for c in files if c[2]==f[2] and c[1][:2]==['spikes','clusters']][0]
        clusters = np.load(cluster_file[0])

        # write data mapping
        ri_file.write('neuroscope.clu.%d: %s' % (n, f[2]))
        print('neuroscope.clu.%d: %s' % (n, f[2]))

        # write spike files
        np.savetxt(os.path.join(target_dir, 'neuroscope.res.'+ str(n) ), times/dt, '%d')
        np.savetxt(os.path.join(target_dir, 'neuroscope.clu.'+ str(n) ), \
            np.insert(clusters, 0, max(clusters)),'%d')

    ri_file.close()

    # EVENT AND INTERVAL SERIES...
    # We first load them in, then sort, then output
    lines = [] # carries a list of tuples (t, text)
    for f in interval_files:
           
        print('reading ' + f[0])
        times = np.load(f[0]) 
        
        lines.extend([(t[0], str(t[0]*1000) + ' ' + f[1][0] + ' ON\n') for t in times])
        lines.extend([(t[1], str(t[1]*1000) + ' ' + f[1][0] + ' OFF\n') for t in times])
            
    # now event files
    for f in event_files:

        print('reading ' + f[0])
        times = np.load(f[0]) 
        lines.extend([(t, str(t*1000) + ' ' + f[1][0] + '\n') for t in times])
           
    # sort them
    lines.sort(key=lambda x:x[0])

    out = open(os.path.join(target_dir, 'neuroscope.evt.evt'), 'w')
        #now print output. 
    out.writelines([s[1] for s in lines])
    out.close();


if len(sys.argv)<3:
    print(__doc__)
else:
    main()


