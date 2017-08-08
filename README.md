# alf2neuroscope

Converts ALF files to be read in neuroscope

Use:

`alf2neuroscope.py sample_rate destination_directory source_directory1 source_directory2 ...`  
Reads files in ALF (ALyx Files) and converts them so you can load them into [neurosope](http://neuroscope.sourceforge.net/UserManual/data-files.html).  
Works recursively on all source directories, finding any `.npy` files within any subdirectories  
Writes `neuroscope.dat`, `neuroscope.evt.evt`, `neuroscope.res.*`, `neuroscope.clu.*` to destination_directory

# What is ALF? 

ALF stands for "ALyx Files". It isn't so much a format as a format-neutral file-naming convention. 

In ALF, different measurements in an experiment are represented bycollection of files in a directory. Each filename has three parts, for example `spikes.times.npy` or `spikes.clusters.npy`. We will refer to these three parts of the filenames parts as the "object", the "attribute" and the "extension". The extension says what physical format the file is in - for now we only use .npy and .tsv but you could use any format, for video or json .

Each file contains information about particular attribute of the object. For example `spikes.times.npy` indicates the times of spikes and `spikes.clusters.npy` indicates their cluster assignments. You could have another file `spikes.amplitudes.npy` to convey their amplitudes. The important thing is that every file describing an object has the same number of rows (i.e. the 1st dimension of an npy file, number of frames in a video file, etc).  You can therefore think of the files for an object as together defining a table, with column headings given by the attributte in the file names, and values given by the file contents.

Some files will contain multiple columns, for example clusters.ccf_location.tsv would be a 4-column tab-delimited text file in which the first 3 columns contain xyz coordinates of a cluster and the 4th contains its inferred brain location as text. In this case, an additional file clusters.ccf_location.fields could be a tsv file with one row per column of the original file. The first column of this .fields file will be a name for each column. Additional columns in the .fields file can provide further info on them.

ALF objects can represent anything. But three types of object are special:

## Event series

If there is a file with attribute `times`, (i.e. filename `obj.times.ext`), it indicates that this object is an event series. The `times` file contains a numerical array containing times of the events in seconds, relative to a universal timescale common to all files. Other attributes of the events are stored in different files. If you want to represent times relative to another timescale, do this with an attribute of the form `times_timescale`.

## Interval series

If there is a file with attribute `intervals`, (i.e. filename `tones.intervals.npy`), it should have two columns, indicating the start and end times of each interval relative to the universal timescale. Again, other attributes of the events can be stored in different files (e.g. `tones.frequencies.npy`. Event times relative to other timescales can be represented by a file with attribute `intervals_timescale`.

## Continuous timeseries

If there is a file with attribute `timestamps`, it indicates the object is a continuous timeseries. The timestamps file represents information required to synchronize the timeseries to the universal timebase, even if they were unevenly sampled. Each row of the `timestamps` file represents a synchronization point, with the first column giving the sample number, and the second column giving the corresponding time in universal seconds. The times corresponding to all samples are then found by linear interpolation. Note that all files representing a continuous timeseries object must have one row per sample, except the `timestamps` file itself, which will often have substantially less. An evenly-sampled recording, for example, could have just two timestamps, giving the times of the first and last sample.
