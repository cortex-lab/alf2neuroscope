# alf2neuroscope

Converts ALF files to be read in neuroscope

There is just one file: alf2neuroscope.py

Use:

`alf2neuroscope.py sample_rate destination_directory source_directory1 source_directory2 ...`  
Reads files in ALF (ALyx Format) and converts them so you can load them into neurosope.  
Works recursively on all source directories, finding any `.npy` files within any subdirectories  
Writes `neuroscope.dat`, `neuroscope.evt.evt`, `neuroscope.res.*`, `neuroscope.clu.*` to destination_directory

For `sample_rate`, recommendation is 1250. For documentation on neuroscope see [here](http://neuroscope.sourceforge.net/UserManual/data-files.html)

# What is ALF? 

ALF stands for "ALyx Format" but in fact it isn't so much a format as a format-neutral file-naming convention. 

In ALF, each filename has three parts, for example `spikes.times.npy` or `spikes.clusters.npy`. We will refer to these parts as the "object", the "attribute" and the "extension". The extension says what physical format the file is in - for now we only use .npy but you could use any format, for example plain text, video (e.g. .avi) or json .

Each file contains information about an object. For example `spikes.times.npy` indicates the times of spikes and `spikes.clusters.npy` indicates their cluster assignments. You could have another file `spikes.amplitudes.npy` to convey their amplitudes. The important thing is that every file describing the object has the same number of rows (i.e. the 1st dimension of an npy file, frames in a video file, etc).  You can therefore think of the files for an object as together defining a table, with column headings given by the attributte in the file names, and entries given by the file contents.

ALF objects can represent anything. But three types of object are special:

## Event series

If there is a file with attribute `times`, (i.e. filename `obj.times.ext`), it indicates that this object is an event series. The `times` file contains a numerical array containing times of the events in seconds, relative to a universal timescale common to all files. Other attributes of the events are stored in different files. If you want to represent times relative to another timescale, do this an extension name of the form `times_timescale`.

## Interval series

If there is a file with attribute `intervals`, (i.e. filename `obj.intervals.ext`), it should have two columns, indicating the start and endpoints relative to the universal timescale. Again, other attributes of the events can be stored in different files, and other timescales can be represented by files with attribute `intervals_timescale`.

## Continuous series

If there is a file with attribute `timestamps`, it indicates the object is a continuous timeseries. The timestamps file has two columns, and represents information required to synchronize the timeseries to the universal timebase, allowing unevenly sampled series to be represented. Each row of the `timestamps` file represents a sync point with the first column giving the sample number, and the second column giving the corresponding time in universal seconds. Note that all files representing a continuous timeseries object must have one row per sample, except the `timestamps` file, which will often have substantially less. An evenly-sampled file, for instance, will just have two timestamps, for the first and last sample.
