import requests
import json
import math

# testing requests
# todo : functions to change all params
template_json = {
    "globalSpecs": {
        "clusterLimit": 16,
        "cpuHeadroom": 15,
        "fttAndftm": "AUTO_AUTO",
        "instanceType": "I3",
        "region": "us-west-2",
        "sddcApplianceSize": "AUTO",
        "sizingType": "QUICK",
        "stretchedCluster": "false"
    },
    "workloads": [
        {
            "profileName": "Workload Profile - 1",
            "vmProfile": {
                "aggregatedIOPs": 5000,
                "compressionRatio": 1,
                "dedup": 1,
                "dedupOrCompressionRatio": 1,
                "ioProfile": {
                    "blockSizeInKB": 4,
                    "ioAccessPattern": "Random",
                    "ioRatios": "70/30"
                },
                "iopsPerVM": 50,
                "resourceUtilization": {
                    "cpuUtilization": {
                        "description": "string",
                        "units": "KB",
                        "value": 10
                    },
                    "memoryUtilization": {
                        "description": "string",
                        "units": "KB",
                        "value": 10
                    }
                },
                "targetRAMRatio": 1,
                "vCpusPerCore": 4,
                "vCpusPerVM": 2,
                "vRAMPerVM": {
                    "description": "string",
                    "units": "GiB",
                    "value": 200
                },
                "vmdkSize": {
                    "description": "string",
                    "units": "GiB",
                    "value": 200
                },
                "vmsNum": 1000
            },
            "workloadType": "GPW_GVM"
        }
    ]
}

template2_json = {
    "globalSpecs": {},
    "workloads": [
        {
            "profileName": "Workload Profile - 1",
            "vmProfile": {
                "vCpusPerCore": 4,
                "vCpusPerVM": 2,
                "vRAMPerVM": {
                    "value": 200
                },
                "vmdkSize": {
                    "value": 200
                },
                "vmsNum": 1000
            },
            "workloadType": "GPW_GVM"
        }
    ]
}


def input_post_metrics(template_request, vmsNum, cpu, ram, sto):
    template_request['workloads'][0]['vmProfile']['vCpusPerVM'] = math.ceil(cpu / vmsNum)
    template_request['workloads'][0]['vmProfile']['vRAMPerVM']['value'] = math.ceil(ram / vmsNum)
    template_request['workloads'][0]['vmProfile']['vmdkSize']['value'] = math.ceil(sto / vmsNum)
    template_request['workloads'][0]['vmProfile']['vmsNum'] = int(vmsNum)

    return template_request


def response_to_dict(response):
    return json.loads(response.text)


def read_outputs_to_graphs(response_json):
    return



headers = {'content-type': 'application/json'}

response = requests.post("https://vmc.vmware.com/api/sizer/v4/recommendation?cloudProviderType=VMC_ON_AWS",
                         json=template2_json, headers=headers)

out = response_to_dict(response)

clean = out['genericResponse']

out['genericResponse']['sizingAssumptions']
out['genericResponse']['sddcInformation']
