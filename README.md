# alf2neuroscope

Converts ALF files to be read in neuroscope

Use:

`alf2neuroscope.py sample_rate destination_directory source_directory1 source_directory2 ...`  
Reads files in ALF (ALyx Files) and converts them so you can load them into [neurosope](http://neuroscope.sourceforge.net/UserManual/data-files.html).  
Works recursively on all source directories, finding any `.npy` files within any subdirectories  
Writes `neuroscope.dat`, `neuroscope.evt.evt`, `neuroscope.res.*`, `neuroscope.clu.*` to destination_directory

# What is ALF? 

ALF is a file naming convention designed for neurophysiology data, described at https://github.com/cortex-lab/ALF
