import random
from locust import HttpUser, task, constant_throughput
import MyAPI
import pathlib
import os

dataset_names = MyAPI.get_dataset_names()
datasets = MyAPI.get_datasets()
tree_csv = next(os.walk(MyAPI.csv_dataset_folder))  # initial value -> ('csv_datasets_folder', 'csv_datasets', [])
tree_nmea = next(os.walk(MyAPI.nmea_dataset_folder))  # initial value -> ('nmea_datasets_folder', 'nmea_datasets', [])
tree_nmea[1].sort()
tree_gnss = next( os.walk(MyAPI.gnss_dataset_folder))  # initial value -> ('gnss_datasets_folder', 'gnss_datasets', [])

class QuickStartUser(HttpUser):
    wait_time = constant_throughput(0.25)
    pool_manager = PoolManager(maxsize=10, block=True)

    @task
    def get_datasets(self):
       self.client.get("/api/3/action/current_package_list_with_resources", json={'limit': 100, 'page':1})
    
    @task
    def get_dataset(self):
        if dataset_names != -1:
            index = random.randint(0, len(dataset_names) - 1)
            self.client.get("/api/3/action/package_show", json={'id': dataset_names[index]})

    @task
    def get_resource(self):
        if dataset_names != -1:
            index_dataset = random.randint(0, len(dataset_names) - 1)
            resources = datasets[index_dataset]["resources"]
            if resources != -1:
            if len(resources) > 0:
                index_resource = random.randint(0, len(resources) - 1)
                self.client.get("/api/3/action/resource_show", json={'id': resources[index_resource]["id"]})

    @task
    def get_groups(self):
        self.client.get("/api/3/action/group_list")
    
    @task
    def get_organizations(self):
        self.client.get("/api/3/action/organization_list")
     
    @task
    def post_resource(self):
        global counter_csv, counter_nmea, counter_gnss
        type_list = ["csv", "nmea", "gnss"]
        type_of = random.choice(type_list)
        if type_of = "csv":
            root, dirs, empty = tree_csv
        elif type_of = "gnss":
            root, dirs, empty = tree_gnss
        else:
            root, dirs, empty = tree_nmea

        random_index = random.randrange(0, len(dirs))
        dataset_folder_path = os.path.join(root, dirs[random_index])
        resources = next(os.walk(dataset_folder_path))[2]
        json_data = MyAPI.new_data(dataset_folder_path, type_of)
        self.client.post("/api/3/action/package_create",
                         json=json_data,
                         headers={
                             'Authorization': MyAPI.api_token})
        random_index = random.randrange(0, len(resources))
        resource_name = resources[random_index]
        json_data = MyAPI.up_data(dataset_folder_path, resource_name, type_of)
        filepath = pathlib.Path(os.path.join(dataset_folder_path, resource_name))
        fd = filepath.open("rb")
        update_request = self.client.post("/api/3/action/package_revise",
                                              data=json_data,
                                              files=[("update__resources__-1__upload", (resource_name, fd))],
                                              headers={
                                                  'Authorization': MyAPI.api_token})
        new_resource = update_request.json()["result"]["package"]["resources"][-1]
        self.client.post("/api/3/action/resource_create_default_resource_views",
                             json={"resource": new_resource},
                             headers={
                                 'Authorization': MyAPI.api_token})
        self.client.post("/api/3/action/datastore_create",
                             json={"resource": new_resource},
                             headers={
                                 'Authorization': MyAPI.api_token})
