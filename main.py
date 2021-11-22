# imports
import pandas as pd
import math

# setup variables
data_path = "./input_data/"

test_file_path = data_path + "RVTools_ORY519_export_all_2021-04-22_test.xlsx"

metrics_test = {"storage_metric": "TiB"}
# open rvtools
test_db = pd.read_excel(test_file_path, "vInfo")
test_db1 = pd.read_excel(test_file_path, "vPartition")
test_db2 = pd.read_excel(test_file_path, "vHost")


# recap function
def vinfo_summary(vinfo_db, vpartition_db, vhost_db, metrics=""):
    # get number of total VMs (rows)
    vm = vinfo_db.shape[0]

    # get number of VMs with "Guest state" values
    # todo store name and specs of VMs not running for analysis
    temp = vinfo_db["Guest state"].unique()
    if "running" in temp:
        vm_running = vinfo_db["Guest state"].value_counts()["running"]
    elif "notRunning" in temp:
        vm_notrunning = vinfo_db["Guest state"].value_counts()["notRunning"]

    # get number of VMs with "Powerstate" values
    # todo store name and specs of VMs not running for analysis
    temp = vinfo_db["Powerstate"].unique()
    if "poweredOn" in temp:
        vm_on = vinfo_db["Powerstate"].value_counts()["poweredOn"]
    elif "poweredOff" in temp:
        vm_off = vinfo_db["Powerstate"].value_counts()["poweredOff"]

    # get CPUs count
    # todo add option of choosing to take out VMs of scope (ie poweredOff)
    CPU = vinfo_db.CPUs.sum()

    # get memory count rounded up
    ram = math.ceil(vinfo_db.Memory.sum() / 1024)

    # get consumed storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    consumed_sto = math.ceil(vpartition_db["Consumed MB"].sum() / 1024)

    # get consumed storage rounded up (in GiB or TiB)
    # todo: add option to have consumed for running and in use for notrunning VMs
    capacity_sto = math.ceil(vpartition_db["Capacity MB"].sum() / 1024)

    # change to TiB if asked
    #if metrics["storage_metric"] == "TiB":
    #    consumed_sto = math.ceil(consumed_sto / 1024)

    # count hosts
    host_count = vhost_db.shape[0]

    # count cores of hosts
    host_cores = vhost_db["# Cores"].sum()

    # get host models & count of each
    host_models = vhost_db.Model.value_counts()

    # get host ESX versions
    host_esx = vhost_db["ESX Version"].value_counts()

    # get cluster names & size
    host_clusters = vhost_db.Cluster.value_counts()

    # get OS (config file) counts
    vm_os = vinfo_db["OS according to the configuration file"].value_counts()

    # aggregate results for test
    output_list = {"VM(s)": vm,
                   "CPU(s)": CPU,
                   "RAM": ram,
                   "Consumed Storage": consumed_sto,
                   "Capacity Storage": capacity_sto,
                   "Host Count": host_count,
                   "Host Cores": host_cores,
                   "Host Models": host_models,
                   "Host ESX Versions": host_esx,
                   "Host Cluster(s)": host_clusters,
                   "VM OS count(s)": vm_os}

    return output_list

t = vinfo_summary(test_db, test_db1, test_db2)