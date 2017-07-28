# alf2neuroscope

Converts ALF format to be read in neuroscope

There is just one file: alf2neuroscope.py

Use:

alf2neuroscope.py sample_rate destination_directory source_directory1 source_directory2 ...  
Reads files in ALF (ALyx Format) and converts them so you can load them into neurosope.  
Works recursively on all source directories, finding any .npy files within any subdirectories  
Writes neuroscope.dat, neuroscope.evt.evt, neuroscope.res.*, neuroscope.clu.* to destination_directory


for sample_rate, recommendation is 1250.


For documentation on ALF see http://[soon-to-be written documentation website]

For documentation on neuroscope see http://neuroscope.sourceforge.net/UserManual/data-files.html
