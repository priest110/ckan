import random
from locust import HttpUser, task, constant_throughput
import ImportData
import pathlib
import os

dataset_names = ImportData.get_dataset_names()
datasets = ImportData.get_datasets()
tree_csv = next(os.walk(ImportData.csv_dataset_folder))  # initial value -> ('csv_dataset', [], csv_files)
counter_csv = 0
tree_nmea = next(
    os.walk(ImportData.nmea_dataset_folder))  # initial value -> ('nmea_datasets_folder', 'nmea_datasets', [])
tree_nmea[1].sort()
counter_nmea = 40
#tree_gnss = next( os.walk(ImportData.gnss_dataset_folder))  # initial value -> ('gnss_dataset', [], gnss_files)
counter_gnss = 0

#ImportData.delete_datasets(dataset_names)
ImportData.import_other_datasets()

class QuickStartUser(HttpUser):
    #wait_time = constant_throughput(0.25)
    # pool_manager = PoolManager(maxsize=10, block=True)
    """ 
    @task
    def get_datasets(self):
       # self.client.get("/api/3/action/current_package_list_with_resources", json={'limit': 100, 'page':1})
       self.client.get("/api/3/action/package_search?rows=20&start=0")
    
    @task
    def get_dataset(self):
       # if dataset_names != -1:
        #    index = random.randint(0, len(dataset_names) - 1)
         #   self.client.get("/api/3/action/package_show", json={'id': dataset_names[index]})
             self.client.get("/api/3/action/package_show", json={'id': 'sail_sd_gnss_nmea_20200123'})
    """
    @task
    def get_resource(self):
        if dataset_names != -1:
          #  index_dataset = random.randint(0, len(dataset_names) - 1)
           # resources = datasets[index_dataset]["resources"]
          #  if resources != -1:
           #     if len(resources) > 0:
            #        index_resource = random.randint(0, len(resources) - 1)
             #       self.client.get("/api/3/action/resource_show", json={'id': resources[index_resource]["id"]})
                     self.client.get("/api/3/action/resource_show", json={'id': 'c8fc77b0-4902-4cf1-86c0-fed20b5faa1c'})
                     self.client.get("/dataset/sail_sd_gnss_nmea_20200212/resource/c8fc77b0-4902-4cf1-86c0-fed20b5faa1c")
    """
    @task
    def get_groups(self):
        self.client.get("/api/3/action/group_list")
    
    @task
    def get_organizations(self):
        self.client.get("/api/3/action/organization_list")
     
    @task(1)
    def post_resource(self):
        global counter_csv, counter_nmea, counter_gnss
        
        if counter_csv == 0:
            dataset_folder_path, empty, resources = tree_csv
            counter_csv = 1
            type_of = "csv"
        elif counter_gnss == 0:
            dataset_folder_path, empty, resources = tree_gnss
            counter_gnss = 1
            type_of = "gnss"
        else:
        
        root, dirs, empty = tree_nmea
        dataset_folder_path = os.path.join(root, dirs[counter_nmea])
        counter_nmea += 1
        type_of = "nmea"
        resources = next(os.walk(dataset_folder_path))[2]
        json_data = ImportData.new_data(dataset_folder_path, type_of)
        self.client.post("/api/3/action/package_create",
                         json=json_data,
                         headers={
                             'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})
        
       #for resource_name in resources:
        resource_name = resources[0]
        json_data = ImportData.up_data(dataset_folder_path, resource_name, type_of)
        filepath = pathlib.Path(os.path.join(dataset_folder_path, resource_name))
        fd = filepath.open("rb")
        update_request = self.client.post("/api/3/action/package_revise",
                                              data=json_data,
                                              files=[("update__resources__-1__upload", (resource_name, fd))],
                                              headers={
                                                  'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})
        new_resource = update_request.json()["result"]["package"]["resources"][-1]
        self.client.post("/api/3/action/resource_create_default_resource_views",
                             json={"resource": new_resource},
                             headers={
                                 'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})
        self.client.post("/api/3/action/datastore_create",
                             json={"resource": new_resource},
                             headers={
                                 'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzcEdpUnhpR2I1NDg0V3BhRTVOMUl6eDN2VTlyWWozTUc1OExaRThubG1NIiwiaWF0IjoxNjUzNzkyNzEwfQ.UCY6CAYTYrv1mxGdE725k8nvDm4JxYmUP5XithQXDxI'})
    """ 
