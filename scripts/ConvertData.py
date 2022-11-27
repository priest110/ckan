import csv
import os
import sys

# AUX INFO #

max_longitude = -180
min_longitude = 180
max_latitude = -90
min_latitude = 90

# MAIN #

def convert_to_csv():
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

def choose_bbox(dataset_folder_path):
    global max_latitude, min_latitude, max_longitude, min_longitude
    files = os.listdir(dataset_folder_path)
    for file_name in files:
        filepath = os.path.join(dataset_folder, file_name)
        with open(filepath, 'r') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            for row in csvreader:
                try:
                    lon = float(row[3])
                    lat = float(row[4])
                except ValueError:
                    break
                if lon > max_longitude:
                    max_longitude = lon
                if lon < min_longitude:
                    min_longitude = lon
                if lat > max_latitude:
                    max_latitude = lat
                if lat < min_latitude:
                    min_latitude = lat
    coordinates = "[[[" + str(min_longitude) + "," +  str(min_latitude) + " ],[" + str(max_longitude) + "," +  str(min_latitude) + "],[" + str(max_longitude) + "," + str( max_latitude) + "], [" + str(min_longitude) + "," + str(max_latitude) + "], [" + str(min_longitude) + "," + str(min_latitude) +"]]]"
    return coordinates

# convert_to_csv()
# choose_bbox()
