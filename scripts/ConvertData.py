import csv
import os
import pathlib

# AUX INFO #

dataset_folder = '/home/ruizinho/Desktop/Universidade/Tese/gsd/preprocessed/'
files = os.listdir(dataset_folder)

# MAIN #

for file_name in files:
    filepath = os.path.join(dataset_folder, file_name)
    file_to_read = open(filepath, 'r')
    new_filepath = filepath.rpartition('.')[0] + ".csv"
    file_to_write = open(new_filepath, 'w+')
    for line in file_to_read:
        new_line = line.replace(" ", ", ").replace("#, ", "")
        file_to_write.write(new_line)
    file_to_read.close()
    file_to_write.close()
