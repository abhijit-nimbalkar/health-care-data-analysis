#Name:Abhijit Nimbalkar
import os
import json
import csv
import argparse
import subprocess
import progressbar
from datetime import datetime
import fhirclient.models.bundle as b
import fhirclient.models.claim  as c


def parse_claims_into_csv(bundle_path, output_path, claims_file_name):
    """Reads a directory of fhir bundles, parses fhir bundles into
    fhirclient bundle objects, parses out claims data, writes claims data to a
    csv file.

    Hint : translate relative to absolute paths
    Hint : walk the subdirectory to find files
    Hint : call parse_bundle_for_file
    Hint : call get_claims_from_bundle
    Hint : call write_claims_to_csv

    Arguments:
        bundle_path {String} -- path to the fhir data directory for this assignment e.g. ~/assignments/data/fhir
        output_path {String} -- path to the output directory for this assignment e.g. ~/assignments/out
        claims_file_name {String} -- claims file name e.g. claims.csv
    """
    fhir_dir=os.path.abspath(bundle_path)                 #getting absolute path of fhir file directory 
    if not os.path.exists(fhir_dir):                      #Checking if that file already exist
        print("Path to fhir diretory does not exist. Please provide the correct path of fhir directory to execute the program.")
        return
    
    output_dir=os.path.abspath(output_path)               #getting absolute path of output file directory
    if not os.path.exists(output_dir):                    #checking if that file already exist
        try:
            os.makedirs(output_dir)
        except:
            print("Output directory can not be created.")

    try:
        list_of_all_files=[file for file in os.listdir(fhir_dir) if os.path.isfile(os.path.join(fhir_dir,file))]    #listing out all files from directory
    except:
        print("There are no files in existing directory. Please try running program again.")
        return

    claims=[]
    for file in list_of_all_files:
        bundle=parse_bundle_for_file(os.path.join(fhir_dir,file))   #creating bundle object of each file
        claims.append(get_claims_from_bundle(bundle))               #appending each bundle in the claim list

    flattened_claims=[obj for claim in claims for obj in claim]     #as claim list was not one dimentional. creating 1d list of bundle objects

    output=write_claims_to_csv(flattened_claims,output_dir,claims_file_name,new_file=True)  

    return output

def parse_bundle_for_file(fhir_bundle_path):
    """Reads a fhir bundle file and returns a fhir bundle class object
    
    Arguments:
        fhir_bundle_path {String} -- path to a fhir bundle
    
    Returns:
        fhirclient.models.bundle.Bundle -- fhir bundle class object for the
        fhir bundle file passed into the function
    """
    with open(fhir_bundle_path,'r') as f:
        fhir_object=json.load(f)            #loading bundle object
    try:
        bundle=b.Bundle(fhir_object)        #initiating bundle object
        return bundle
    except:
        print("There are no fhir format files in the provided directory. Please try again.")
        return
            

def get_claims_from_bundle(bundle):
    """Extracts a fhir claim resource from a FHIR bundle containing a claim

    Arguments:
        bundle {fhirclient.models.bundle.Bundle} -- fhir bundle representing a
        single synthea fhir file

    Returns:
        list -- list of all fhir fhirclient.models.claim.Claim resources 
        contained within a single fhir bundle
    """
    claims=[entry.resource for entry in bundle.entry if entry.request.url=='Claim']   #parsing claim objects from bundle objects
    return(claims)


def write_claims_to_csv(claims, output_path, claims_file_name, new_file=True):
    """Writes information contained within a list of claims to a csv file
    at the specified path

    Ex: must match exact format with no spaces between fields
    status,use,billable_period_start,billable_period_end,total,currency

    Arguments:
        claims {list} -- List of fhirclient.models.claim.Claim objects
        output_path {String} -- path to the output directory for this assignment e.g. ~/assignments/out
        claims_file_name {String} -- claims file name e.g. claims.csv
        new_file {Boolean} -- indicates if a csv file should be created or updated
    """

    header=["status","use","billable_period_start","billable_period_end","total","currency"] #defining header for csv file
    csv_data=get_csv_values_from_claim(claims)
    
    if(new_file):               #if user wants to create new file
        if os.path.exists(os.path.join(output_path,claims_file_name)):    #eventhough user wants to create new, there is same file exist in directory then confirm with user if he/she wants to replace it with new file
            ans=input("The existing data into file will be replaced with new data. Are you sure you want to proceed(Yes/No)?")
            if(ans.lower()=='yes'):
                with open(os.path.join(output_path,claims_file_name),mode='w',newline='') as f:
                    writer = csv.writer(f, delimiter=',')
                    writer.writerow(header)
                    for row in csv_data:
                        writer.writerow(row)
                return 1
            else:
                print("File already exist and based on your input program can not proceed further.")
                return 0
        else:
            with open(os.path.join(output_path,claims_file_name),mode='w',newline='') as f:     #creating new file
                writer = csv.writer(f, delimiter=',')
                for row in csv_data:
                    writer.writerow(row)
            return 1
    else:                                                                                       #if user wants to update existing file
        if os.path.exists(os.path.join(output_path,claims_file_name)):
            with open(os.path.join(output_path,claims_file_name),mode='a',newline='') as f:
                writer = csv.writer(f, delimiter=',')
                for row in csv_data:
                    writer.writerow(row)
            return 1
        else:
            print("There is not existing file to update. Therefore can not proceed.")
            return 0


def get_csv_values_from_claim(claims):
    """Takes a fhirclient.models.claim.Claim object and returns a list of 
    strings for the following attributes

    status
    use
    billiable_period_start as an iso string
    billable_period_end as an iso string
    total
    currency

    Ex: must match exact format with no spaces between fields
    active,complete,2009-06-22T06:16:39-04:00,2009-06-22T06:31:39-04:00,255.0,USD

    Arguments:
        claim {fhirclient.models.claim.Claim} -- fhir Claim object

    Returns:
        list -- list of String values
    """
    ## parsing attributes from claim object
    csv_data=[[obj.status,obj.use,(obj.billablePeriod.start.date).isoformat(),(obj.billablePeriod.end.date).isoformat(),obj.total.value,obj.total.code] for obj in claims]
    return(csv_data)


 #DO NOT MODIFY BELOW THIS LINE
def get_parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fhir", default="data/fhir/", help="path to the fhir data directory for this assignment e.g. ~/assignments/data/fhir")
    parser.add_argument("-o", "--output", default="out/", help="path to the output directory for this assignment e.g. ~/assignments/out")
    return parser.parse_args()


if __name__ == "__main__":
    parsed_args = get_parsed_args()
    claims = parse_claims_into_csv(parsed_args.fhir, parsed_args.output, 'claims.csv')
    if(claims):     #execute if all operations are executed successfully
        print(f"The output csv file is created at folder path {parsed_args.output}")
    else:
        print("Due to above error, program was halted.")
