# -*- coding: utf-8 -*-
"""
alfaneuroscope.py sample_rate destination_directory source_directory1 source_directory2 ...
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


def convert(target_dir, source_dirs, sample_rate=1250, MUA_BY_DEPTH = 0, KEEP_GROUPS = [2,3]):

    #source_dir = r'\\zserver.cortexlab.net\data\expInfo\Robbins\2017-06-13\1'
    # source_dirs = [r'\\zserver.cortexlab.net\Data\EyeCamera\Robbins\2017-06-13\1', \
    # 	r'\\zserver.cortexlab.net\data\expInfo\Robbins\2017-06-13\1', \
    #     r'\\zserver\Data\Subjects\Robbins\2017-06-13']
    # target_dir = '.'
    # sample_rate = '1250'

    # if source_dirs is just one string, convert to list
    from IPython.core.debugger import Tracer
    Tracer()()
    if isinstance(source_dirs, str): source_dirs = [source_dirs]

    dt = 1.0/float(sample_rate)

    # find directories recursively
    walkout = [i for d in source_dirs for i in os.walk(d)]
    print("directory: " + '\ndirectory: '.join([w[0] for w in walkout]))

    # files[] is list of tuples storing (full file path, file split into words, home directory)

    files =  [ (os.path.join(wa[0], f), f.split('.'), wa[0] ) \
                for wa in walkout for f in wa[2] if f.endswith('.npy')]

    if len(files)==0:
        print('No source files!')
        return

    filebases = set([f[1][0] for f in files])
    spike_files = [f for f in files if f[1][:2] == ['spikes', 'times']]
    event_files = [f for f in files if f[1][1] == 'times' and not f[1][0] == 'spikes']
    interval_files = [f for f in files if f[1][1] == 'intervals' and not f[1][0] == 'spikes']
    timestamp_files = [f for f in files if f[1][1] == 'timestamps']
     
           
    ## do spike files
    ri_file = open(os.path.join(target_dir, 'clu_file_list.txt'), 'w')
    for n,f in enumerate(spike_files):

        # load data        
        times = np.load(f[0]).flatten()

        if MUA_BY_DEPTH:
            cluster_file = [c for c in files if c[2]==f[2] and c[1][:2]==['spikes','depths']][0]
            clusters = np.load(cluster_file[0]).flatten()//MUA_BY_DEPTH
        else:
            cluster_file = [c for c in files if c[2]==f[2] and c[1][:2]==['spikes','clusters']][0]
            clusters = np.load(cluster_file[0]).flatten()
            # u_clus counts clusters  from 0 onwards, so they correspond to lines in clusters.*.npy files
            _, u_clus = np.unique(clusters, return_inverse=True) 

            # is there a cluster groups file? if so, keep only spikes in these groups
            cluster_groups_file = os.path.join(f[2], 'clusters.groups.npy')
            try: 
                cluster_groups = np.load(cluster_groups_file).flatten() # flatten everything because matlab
            except:
                pass
            else:
                keep = np.in1d(cluster_groups[u_clus], KEEP_GROUPS)
                times = times[keep]
                clusters = clusters[keep]

            # is there a cluster depths file? if so, sort into order starting with the highest
            cluster_depths_file = os.path.join(f[2], 'clusters.depths.npy')
            try:
                cluster_depths = np.load(cluster_depths_file)
            except:
                pass        
            else:
                # compute rank order of cluster depths. this is a bit fiddly due to inverse permutation
                depth_order = np.argsort(cluster_depths.flatten())
                depth_rank = np.zeros(len(depth_order),int)
                depth_rank[depth_order] = np.arange(len(depth_order))
                # now renumber cluster as depth rank depth

                clusters = max(depth_rank) - depth_rank[u_clus]



        # write data mapping
        ri_file.write('neuroscope.clu.%d: %s\n' % (n, f[2]))
        print('neuroscope.clu.%d: %s' % (n, f[2]))

        # write spike files
        np.savetxt(os.path.join(target_dir, 'neuroscope.clu.'+ str(n) ), \
            np.insert(clusters, 0, max(clusters)),'%d')
        np.savetxt(os.path.join(target_dir, 'neuroscope.res.'+ str(n) ), times/dt, '%d')

    ri_file.close()

    # EVENT AND INTERVAL SERIES...
    # We first load them in, then sort, then output
    lines = [] # carries a list of tuples (t, text)

    ## do event and interval files
    # we build up a list "lines" that stores tuples of times and lines to print corresponding to them
    for f in event_files + interval_files:
        print('reading ' + f[0])
        times = np.load(f[0]) 

        # find associated files: same directory and first word but not same second word as .times file
        assoc_files = [fa for fa in files if fa[2]==f[2] and fa[1][0] == f[1][0] and not fa[1][1] == f[1][1]]
        if len(assoc_files)>0:
            # load them all in
            assoc_data = [np.load(fa[0]) for fa in assoc_files]
            # make a list of strings for each of the associated files
            assoc_str = [['%s %f' % (fa[1][1], dax) for dax in da] for fa, da in zip(assoc_files, assoc_data)]
            # concatenate them onto one line
            assoc_lines = [' '.join(z) for z in zip(*assoc_str)]
            # print with associated data
        else:
            assoc_lines = ['']*len(times)

        if f in event_files:
            lines.extend([(t, '%f %s %s\n' % (t*1000, f[1][0], l)) for t,l in zip(times, assoc_lines)])
        else:
            lines.extend([(t[0], '%f %s ON %s\n' % (t[0]*1000, f[1][0], l)) for t,l in zip(times, assoc_lines)])
            lines.extend([(t[1], '%f %s OFF %s\n' % (t[1]*1000, f[1][0], l)) for t,l in zip(times, assoc_lines)])

           
    # sort them
    lines.sort(key=lambda x:x[0])

    out = open(os.path.join(target_dir, 'neuroscope.evt.evt'), 'w')
        #now print output. 
    out.writelines([s[1] for s in lines])
    out.close();


    # CONTINUOUS TIMESERIES 
    # first load each timestamps file and make list of interpolator functions
    interp_fn = []
    max_t = -np.inf
    min_t = np.inf
    print('Loading timestamps...')
    for f in timestamp_files:

        ts = np.load(f[0]) 

        # interp_fn[i] converts time to samples for the i'th file, returns nan if out of bounds
        # a list of functions - gotta love python
        interp_fn.append(ip.interp1d(ts[:,1], ts[:,0], bounds_error=False, axis=0))
            
        # keep track of max time
        max_t = max(max_t,ts[:,1].max())
        min_t = min(min_t,ts[:,1].min())

    # sample times in universal seconds
    t = np.arange(0,max_t,dt) 

    ch_file = open(os.path.join(target_dir, 'dat_channel_list.txt'), 'w')
    all_chans = [] # list to contain all all_chans, resampled files
    c = 0 # to keep track of channel numbers
    for i,f in enumerate(timestamp_files):
        
        # load all the other files related to this timestamp file
        series_files = [sf for sf in files \
            if sf[1][0]==f[1][0] and not sf[1][1].startswith('timestamps')]

        if len(series_files)==0:
            continue
    		
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

    return



if len(sys.argv)<3:
    print(__doc__)
else:
    MUA_BY_DEPTH = 0 # HOW MUCH TO DIVIDE SPIKES.DEPTHS.NPY TO GET CLUSTER NUMBER. IF 0, JUST USE CLUSTER NUMBER
    KEEP_GROUPS = [2,3]
    sample_rate = sys.argv[1]
    target_dir = sys.argv[2]
    source_dirs = sys.argv[3:]
    main(target_dir=target_dir, source_dirs=source_dirs, sample_rate=sample_rate, MUA_BY_DEPTH=MUA_BY_DEPTH, KEEP_GROUPS=KEEP_GROUPS)
    print('Done.')


