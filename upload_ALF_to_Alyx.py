# Upload ALF to Alyx
# Python pseudocode - i.e. i have not run or debugged it, and many functions do not exist

root_dir = r'\\zserver.cortexlab.net\Data\Subjects\Cori\2016-12-18\alf'

Session_id = # the UUID for the appropriate session to add this data to
User_id = # the UUID for the user running this code

#Timescale_id = register_timescale() # create a timescale for everything in this directory

# find files in root directory
full_file_names = os.listdir(root_dir).sort()

dataset_id = {} # dict will hold UIDs for each file name
for f in full_file_names:
	fs = f.split('.')
	
	file_creation_time = os.path.gettime(os.path.join(root_dir, f))

	DataFormat_id = query_DataFormats(alf_filename='*.*.' + fs[2])
	if not DataFormat_id:
		warning('No DataFormat *.*.' + fs[2] + ' for file ' + f + ' in ' + root_dir)

	# query_DatasetTypes should look up the UID of a DatasetType with first two words of alf filename
	f01 = fs[0] + '.' + fs[1] + '.*'
	DatasetType_id = query_DatasetTypes(alf_filename=f01)
	
	if not DatasetType_id:
		warning('No DatasesetType ' + f01 + '.* for file ' + f + ' in ' + root_dir)
	
	# register_file_and_dataset is basically what Peter wrote in MATLAB. It should create an
	# entry in the FileRecords and Datasets table, and compute the md5, and return the UID for 
	# the created Dataset
	dataset_id[f] = register_file_and_dataset(session=Session_id, created_by=User_id, file=f,
		directory = root_dir, created_datetime=file_creation_time, dataset_type_id=DatasetType_id,
		data_format_id=DataFormat_id)

	# in some special cases we want to add additional DatasetTypes to the list, given by their second word
	if fs[1] in ['times', 'timestamps', 'intervals']
		DatasetType_id = query_DatasetTypes(alf_filename='*.' + fs[1] + '.*')
		add_DatasetType(dataset=dataset_id[f], dataset_type_id=DatasetType_id)

# loop through unique first words of file, which should correspond to ALF collections
for f0 in set([f.split('.')[0] for f in full_file_names]):
	# query database to see if there is a DataCollection with this alf_filename
	DatasetType_id = query_DatasetTypes(alf_filename=f0 + '.*.*')

	if not DatasetType_id:
		warning('No DatasetType for files of form ' + f0 + '.*.* in ' + root_dir)
		continue

	# create a dataset for the collection. It will have no files, but other datasets will link to it
	parent_dataset_id = create_DataSet(session=Session_id, created_by=User_id,
		dataset_type_id=DatasetType_id, data_format_name='ALF collection')

	# find all linked files and link them
	for l in [f for f in full_file_names if f.split('.')[0]==f0]:
		link_dataset_to_parent(Dataset_id=dataset_id[l], Parent_id=parent_dataset_id)

