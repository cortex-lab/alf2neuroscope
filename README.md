# alf2neuroscope

Converts ALF files to be read in neuroscope

Use:

`alf2neuroscope.py sample_rate destination_directory source_directory1 source_directory2 ...`  
Reads files in ALF (ALyx Files) and converts them so you can load them into [neurosope](http://neuroscope.sourceforge.net/UserManual/data-files.html).  
Works recursively on all source directories, finding any `.npy` files within any subdirectories  
Writes `neuroscope.dat`, `neuroscope.evt.evt`, `neuroscope.res.*`, `neuroscope.clu.*` to destination_directory

# What is ALF? 

ALF stands for "ALyx Files". It not a format but rather a format-neutral file-naming convention. 

In ALF, the measurements in an experiment are represented by collections of files in a directory. Each filename has three parts, for example `spikes.times.npy` or `spikes.clusters.npy`. We will refer to these three parts of the filenames as the "object", the "attribute" and the "extension". The extension says what physical format the file is in - we primarily use .npy and .tsv but you could use any format, for example video or json .

Each file contains information about particular attribute of the object. For example `spikes.times.npy` indicates the times of spikes and `spikes.clusters.npy` indicates their cluster assignments. You could have another file `spikes.amplitudes.npy` to convey their amplitudes. The important thing is that every file describing an object has the same number of rows (i.e. the 1st dimension of an npy file, number of frames in a video file, etc).  You can therefore think of the files for an object as together defining a table, with column headings given by the attribute in the file names, and values given by the file contents.

ALF objects can represent anything. But three types of object are special:

## Event series

If there is a file with attribute `times`, (i.e. filename `obj.times.ext`), it indicates that this object is an event series. The `times` file contains a numerical array containing times of the events in seconds, relative to a universal timescale common to all files. Other attributes of the events are stored in different files. If you want to represent times relative to another timescale, do this by appending to `timescale` after an underscore (e.g. `times_ephysClock`).

## Interval series

If there is a file with attribute `intervals`, (i.e. filename `tones.intervals.npy`), it should have two columns, indicating the start and end times of each interval relative to the universal timescale. Again, other attributes of the events can be stored in different files (e.g. `tones.frequencies.npy`. Event times relative to other timescales can be represented by a file with attribute `intervals_timescale`.

## Continuous timeseries

If there is a file with attribute `timestamps`, it indicates the object is a continuous timeseries. The timestamps file represents information required to synchronize the timeseries to the universal timebase, even if they were unevenly sampled. Each row of the `timestamps` file represents a synchronization point, with the first column giving the sample number (counting from 0), and the second column giving the corresponding time in universal seconds. The times corresponding to all samples are then found by linear interpolation. Note that the `timestamps` file is an exception to the rule that all files representing a continuous timeseries object must have one row per sample, as it will often have substantially less. An evenly-sampled recording, for example, could have just two timestamps, giving the times of the first and last sample.

# Metadata
Sometimes you will want to provide metadata on the columns or rows of a data file. For example, clusters.ccf_location.tsv could be a 4-column tab-delimited text file in which the first 3 columns contain xyz coordinates of a cluster and the 4th contains its inferred brain location as text. In this case, an additional JSON file clusters.ccf_location.metadata.json could provide information about the columns and rows. The metadata file can contain anything, but if it has a top-level key "columns", that should be an array of size the number of columns, and if it has a top-level key "rows" that should be an array of size the number of rows. If the entries in the columns and rows arrays have a key "name" that defines a name for the column or row; a key "unit" defines a unit of measurement. You can add anything else you want.

Note that in ALF you should not have generally two data files with the same object and attribute: if you have tones.frequencies.npy, you can't also  have tones.frequencies.tsv. Metadata files are an exception to this: if you have tones.frequencies.npy, you can also have tones.frequencies.metadata.json.

# File types
ALF can deal with any sort of file, as long as it has a concept of a number of rows (or primary dimension). The type of file is recognized by its extension. Preferred choices:

.npy: numpy array file. This is recommended over flat binary since datatype and shape is stored in the file. If you want to name the columns, use a metadata file. If you have an array of 3 or more dimensions, the first dimension counts as the number of rows. To access npy files from MATLAB use [this](https://github.com/kwikteam/npy-matlab).

.tsv: tab-delimited text file. This is recommended over comma-separated files since text fields often have commas in. All rows should have the same number of columns. There should not be a header row; if you want to name the columns, use a metadata file.

.bin: flat binary file. It's better to .npy for storing binary data but some recording systems save in flat binary. Rather than convert them, you can ALFize a flat binary file by adding a metadata file, which specifies the number of columns (as the size of the "columns" array) and the binary datatype as a top-level key "dtype", using numpy naming conventions.

# Unique file names
An extension to ALF that will make archiving and backups easier would be to have each file have a unique filename. In this proposal, each file would have a four-part name: object.attribute.HASH.extension, where HASH is the md5 hash of the file. The filenames would be long. However the important part is in the first two parts, and users can tab-autocomplete when typing them at the command line; because the extension is last, they can also double-click the file to open it in a movie viewer (or whatever).
