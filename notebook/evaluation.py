'''
Custom Model Monitoring script for baselining and analysis

'''
# Python Built-Ins:
from collections import defaultdict
import datetime
import json
import os
import traceback
from types import SimpleNamespace
import csv
import jsonlines

# External Dependencies:
import numpy as np
import pandas as pd

#Method to get the environment variables
def get_environment():
    '''
    Load configuration variables for SageMaker Model Monitoring job

    See https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-byoc-contract-inputs.html
    
    '''
    try:
        with open("/opt/ml/config/processingjobconfig.json", "r") as conffile:
            defaults = json.loads(conffile.read())["Environment"]
    except Exception as e:
        traceback.print_exc()
        print("Unable to read environment vars from SM processing config file")
        defaults = {}

    return SimpleNamespace(
        dataset_format=os.environ.get("dataset_format", defaults.get("dataset_format")),
        dataset_source=os.environ.get(
            "dataset_source",
            defaults.get("dataset_source", "/opt/ml/processing/input/endpoint"),
        ),
        end_time=os.environ.get("end_time", defaults.get("end_time")),
        output_path=os.environ.get(
            "output_path",
            defaults.get("output_path", "/opt/ml/processing/resultdata"),
        ),
        publish_cloudwatch_metrics=os.environ.get(
            "publish_cloudwatch_metrics",
            defaults.get("publish_cloudwatch_metrics", "Enabled"),
        ),
        sagemaker_endpoint_name=os.environ.get(
            "sagemaker_endpoint_name",
            defaults.get("sagemaker_endpoint_name"),
        ),
        sagemaker_monitoring_schedule_name=os.environ.get(
            "sagemaker_monitoring_schedule_name",
            defaults.get("sagemaker_monitoring_schedule_name"),
        ),
        baseline_constraints=os.environ.get(
            "baseline_constraints",
            defaults.get("baseline_constraints"),
        ),
        baseline_statistics=os.environ.get(
            "baseline_statistics",
            defaults.get("baseline_statistics"),
        ),
        start_time=os.environ.get("start_time", defaults.get("start_time")),
        max_ratio_threshold=float(os.environ.get("THRESHOLD", defaults.get("THRESHOLD", "nan"))),      
    )

def print_env(env):
    '''
    Method to print env variables
    '''
    print("The baseline_statistics file is: ",env.baseline_statistics)
    print("The dataset source is: ",env.dataset_source)
    print("The dataset format is:", env.dataset_format)
    

def parse_training_data(env):
    '''
    Method to parse training data and create baseline constrains and statistics files
    ''' 
    print("Create the baseline and constraints file...")
    
    al_stats,al_constraints,al_list = [],[],[]
    al_count,al_sum,baseline_al_avg = 0,0,0
    
    for path, directories, filenames in os.walk(env.dataset_source):
        for filename in filter(lambda f: f.lower().endswith(".csv"),filenames):
            print("filename is..",filename)
            with open(os.path.join(path, filename), "r") as file:
                for row in file:
                    al_list.append(row.split(',')[1])
    
    for al in al_list[1:]:
        al_count += 1
        al_sum += int(al)
        baseline_al_avg = float(al_sum/al_count)

    al_stats.append({
        "version" : 0,
        "features" : [ {   
        "feature_name" : al_list[0],
        "count" : al_count,
        "sum" : al_sum,
        "average" : baseline_al_avg
        }]})

    al_constraints.append({
        "version" : 0,
        "features" : [ {
        "feature_name" : al_list[0],
        "threshold" : float(baseline_al_avg - 20),
        "completeness" : 1
         }]})
    
    # You could also consider writing a statistics.json and constraints.json here, per the standard results:
    # https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-interpreting-results.html
    
    with open("/opt/ml/output/baseline_statistics.json","w") as outfile:
        outfile.write(json.dumps(al_stats))   
    
    with open("/opt/ml/output/baseline_constraints.json","w") as outfile:
        outfile.write(json.dumps(al_constraints))
    
    #TODO utility to upload these files to S3 which is avaiable OOTB in suggest_baseline
    print("Done writing the constraints and violations file...!..Listing the files written..",os.listdir('/opt/ml/output'))
    
    return al_stats,al_constraints,al_list[1:]

def parse_captured_data(env):
    '''
    Method to parse captured data
    '''
    
    al_data,al_count,al_sum = 0,0,0
    al_stats,al_constraints = [],[]
    
    counts = defaultdict(int)  # dict defaulting to 0 when unseen keys are requested
    for path, directories, filenames in os.walk(env.dataset_source):
        for filename in filter(lambda f: f.lower().endswith(".jsonl"), filenames):
            with open(os.path.join(path, filename), "r") as file:
                for item in jsonlines.Reader(file):
                    try:
                        al_count += 1
                        al_data = (item["captureData"]["endpointInput"]["data"]).split(',')[2]
                        al_sum += float(al_data)
                    except:
                        continue
    
    al_average = float(al_sum/al_count)
    
    al_stats.append({
        "version" : 0,
        "features" : [ {   
        "count" : al_count,
        "sum" : al_sum,
        "average" : al_average
        }]})
    
    al_constraints.append({
        "version" : 0,
        "features" : [ {
        "threshold" : float(al_average - 20),
        "completeness" : 1
         }]})
        
    return al_stats,al_constraints

def read_constraints_file(path,filename):
    with open(os.path.join(path, filename), "r") as file:
        data = json.load(file)
        threshold_constraint = data["custom_constraints"][0]["features"][0]["threshold"]
    
    return threshold_constraint

def generate_analysis_statistics(stats_data):
    
    with open("/opt/ml/output/analysis_statistics.json","w") as outfile:
        outfile.write(json.dumps(stats_data))          
    
    print("Done writing analysis statistics file!..Listing files..",os.listdir('/opt/ml/output')) 
    
def generate_analysis_constraints(constraints_data):
    
    with open("/opt/ml/output/analysis_constraints.json","w") as outfile:
        outfile.write(json.dumps(constraints_data))   
    
    print("Done writing analysis constraints file!..Listing files..",os.listdir('/opt/ml/output'))   
    
def compute_violations(threshold_value, captured_data_list):
    #parse captured data and get the value of each al and compare against the baseline_threshold value
    num_of_records,violations = 0,0
    al_violations = []
    
    for record in captured_data_list:
        num_of_records += 1
        if float(record) > threshold:
            violations += 1
    
    if violations > 0:
        al_violations.append({
            "version" : 0,
            "features" : [ {
            "number_of_records" : count,
            "violations" : violations
             }]})
        with open(os.path.join(env.output_path, "constraints_violations.json"), "w") as outfile:
            outfile.write(json.dumps({"violations": al_violations},indent=2,))
            print("Job completed with {} violations",violations)

    else:
        print("Job completed with no violations")
    
    return al_violations

if __name__=="__main__":
    
    #Parsing the environment variables
    env = get_environment()
    print_env(env)
    
    threshold_value = 0
    
    #Based on the type of Input data i.e JSONL(Captured input) or CSV(Training Data) preprocess the Input to compute the baseline statistics and constraints json file
    for path, directories, filenames in os.walk(env.dataset_source):
        for filename in filter(lambda f: f.lower(),filenames):
            if filename is not None:
                if filename.endswith(".jsonl"):
                    stats_data,constraints_data = parse_captured_data(env)
                elif filename.endswith(".csv"):
                    stats_data,constraints_data,data_list = parse_training_data(env) 
            else:
                print("No input data is provided..Please check again..")
     
    
    print(f"Starting evaluation with config:\n{env}")
    #Perform some analysis and constraints definitions on the data
    generate_analysis_statistics(stats_data)
    generate_analysis_constraints(constraints_data)
    
    #Check if the baseline Inputs are provided        
    if env.baseline_statistics and env.baseline_constraints:
        #read the baseline_statistics
        threshold_value = read_constraints_file('/opt/ml/output/','baseline_statistics.json')
        #Compute violations
        violations = compute_violations(threshold_value,data_list)
            
    else:
        print("No baseline defined to compare against..Please check again..")
     
    #Write cloudwatch metrics if enabled
    if env.publish_cloudwatch_metrics:
        print("Writing CloudWatch metrics...")
        with open("/opt/ml/output/metrics/cloudwatch/cloudwatch_metrics.jsonl", "a+") as outfile:
            json.dump(
                {
                    "MetricName": f"feature_data_PredictedClass",
                    "Timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), 
                    "Dimensions": [
                        { "Name": "Endpoint", "Value": env.sagemaker_endpoint_name or "unknown" },
                        {
                            "Name": "MonitoringSchedule",
                            "Value": env.sagemaker_monitoring_schedule_name or "unknown",
                        },
                    ],
                    "StatisticValues": {
                        #Add additional statistics as required for your usecase
                        "Threshold": threshold_value or "unknown"
                    },
                },
                outfile
            )
            outfile.write("\n")