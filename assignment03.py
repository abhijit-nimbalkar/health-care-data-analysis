import json
import csv
import os


def create_patient_dictionary(patient_file_name):
    """Parses a synthea generated patients.csv file and returns a dictionary of 
    patients where the key is the patient Id and the value is a dictionary 
    containing the following fields.

        Id
        BIRTHDATE
        FIRST
        LAST
        GENDER
    
    Arguments:
        patient_file_name {str} -- file path including name to a synthea 
        patients.csv file
    
    Returns:
        [dict] -- dictionary of all patients in the patients.csv
    """
    #creating patient dictionary to save each patient details
    patient_dict=dict()
    if(os.path.exists(patient_file_name)):
        with open(patient_file_name, mode="r") as f:   
            patient=csv.DictReader(f)
            for row in patient:         #traversing through each patient
                patient_dict[row['Id']]={'Id':row['Id'],'BIRTHDATE':row['BIRTHDATE'],'FIRST':row['FIRST'],'LAST':row['LAST'],'GENDER':row['GENDER']}
        return(patient_dict)
    else:
        #if path specified does not have required csv file then print error and return
        print("Patients directory path you have provided is wrong! Please provide correct file path.")
        return 0
        

def add_encounters_to_patients(patients, encounters_file_name, resource_name='ENCOUNTERS'):
    """
    Parses a synthea generated encounters file and appends encounters to the
    appropriate patient based on the patient Id. A new key identified by the
    resource_name is added to the patient dictionary as a key. The value of the
    new resource is a dictionary having a key that represents the Encounter Id
    and a dictionary containing the following fields as the value.

        Id
        START
        STOP
        CODE
        DESCRIPTION

    Arguments:
        patients {dict} -- dictionary of patients
        encounters_file_name {str} -- file path including name to a synthea 
        encounters.csv file
    
    Keyword Arguments:
        resource_name {str} -- [description] (default: {'ENCOUNTERS'})
    """
    #creating encounters and patients dictionary to save each record
    encounters_dict=dict()
    patient_record_dict=dict()
    if(os.path.exists(encounters_file_name)):
        with open(encounters_file_name, mode="r") as f:
            encounters=csv.DictReader(f)
            for row in encounters:  #traversing through each encounter record
                if row['PATIENT'] in patients.keys():   #if we found the patient key in encounter record
                    patient_record_dict=patients[row['PATIENT']]    #ectract the patient record for temporary purpose
                    #create encounter dictionary record with required values
                    encounters_dict[row['Id']]={'Id':row['Id'],'START':row['START'],'STOP':row['STOP'],'CODE':row['CODE'],'DESCRIPTION':row['DESCRIPTION'].strip(' ')}
                    #add this record to temporary patient record
                    patient_record_dict[resource_name]=encounters_dict
                    patients[row['PATIENT']]=patient_record_dict          #finally add temporary record to patient dictionary
        return(patients)
    else:
        print("Encounters directory path you have provided is wrong! Please provide correct file path.")
        return 0
    

def add_medications_to_patients(patients, medications_file_name, resource_name='MEDICATIONS'):
    """Parses a synthea generated medications file and appends medications to the
    appropriate patient based on the patient Id. A new key identified by the
    resource_name is added to the patient dictionary as a key. The value of the
    new resource is a list that contains dictionaries having the following fields.
        ENCOUNTER
        START
        STOP
        CODE
        DESCRIPTION
    
    Arguments:
        patients {dict} -- dictionary of patients
        medications_file_name {str} -- file path including name to a synthea 
        MEDICATIONS.csv file
    
    Keyword Arguments:
        resource_name {str} -- [description] (default: {'MEDICATIONS'})
    """
    medications_list=[]
    temp_medication_lists=[]
    patient_record_dict=dict()
    #check if file path exist
    if(os.path.exists(medications_file_name)):
        with open(medications_file_name, mode="r") as f:
            medications=csv.DictReader(f)
            for row in medications: #traverse through each medication record
                if row['PATIENT'] in patients.keys(): #finding out the patient id in medication record
                    patient_record_dict=patients[row['PATIENT']] #extracting patient record for temporary purpose
                    #creating medication record with required values
                    medications_list=[{'ENCOUNTER':row['ENCOUNTER'],'START':row['START'],'STOP':row['STOP'],'CODE':row['CODE'],'DESCRIPTION':row['DESCRIPTION'].strip(' ')}]
                    if resource_name in patients[row['PATIENT']].keys():    #if medication key already exist
                        if row['CODE'] in patients[row['PATIENT']][resource_name].keys():   #if medication code already exist
                            temp_medication_lists=patients[row['PATIENT']][resource_name][row['CODE']]
                            temp_medication_lists.append(medications_list[0])   #attaching dictionary from above created list
                            patient_record_dict[resource_name][row['CODE']]=temp_medication_lists
                        else:
                            patient_record_dict[resource_name][row['CODE']]=medications_list
                    else:
                        patient_record_dict[resource_name]={row['CODE']:medications_list}
                    patients[row['PATIENT']]=patient_record_dict       #finally attaching updated temporary patient record to patient  
        return(patients)
    else:
        print("Medications directory path you have provided is wrong! Please provide correct file path.")
        return 0

def problem1(patients):
    """Returns a list of distinct medication codes across all patients
    
    Arguments:
        patients {dict} -- dictionary of patients
    
    Returns:
        list -- list of distinct medication codes
    """
    resource_name='MEDICATIONS'
    unique_codes=set()
    set_of_unique_codes=set()
    #traversing through each patient id
    for row in patients: 
        if resource_name in patients[row].keys(): #check if medication key exist
            unique_codes={record for record in patients[row]['MEDICATIONS'].keys()} #extract all unique codes
            set_of_unique_codes.update(unique_codes)    #add all unique codes to set
    return (list(set_of_unique_codes))  #return list of unique codes

def problem2(patients):
    """Returns a list of distinct (encounter description, medication description)
    tuples across all patients including only the encounters where medications
    were documented.
    
    Arguments:
        patients {dict} -- dictionary of patients
    
    Returns:
        list -- list of distinct (encounter description, medication description)
        tuples
    """
    resource_name1='ENCOUNTERS'
    resource_name2='MEDICATIONS'
    description_key='DESCRIPTION'
    set_of_description=set()
    encounterid_list,medication_encounter_id_list=[],[]
    for row in patients:    #traversing through each patient
        if resource_name1 in patients[row].keys() and resource_name2 in patients[row].keys(): #check if ENCOUNTERS and MEDICATIONS key exist
            encounterid_list=patients[row][resource_name1].keys() #extract all encounter id keys into list
            for medication_id in patients[row][resource_name2].keys():  #traverse through each medication id from MEDICATION item in dictionary
                lenth_of_medication_list=len(patients[row][resource_name2][medication_id]) #calculate the length of each list of MEDICATION item
                #extract all encounter id from medication item
                medication_encounter_id_list=[patients[row][resource_name2][medication_id][i]['ENCOUNTER'] for i in range(lenth_of_medication_list)]
                #traverse through each encounter id extracted in above list
                for medication_encounter_id in medication_encounter_id_list:
                    if medication_encounter_id in encounterid_list:  #if encounter id found in medication code exist in ENCOUNTER item 
                        encounter_description=patients[row][resource_name1][medication_encounter_id][description_key] #description of encounter
                        list_to_medications=patients[row][resource_name2][medication_id]  #description of medication
                        medication_description=[description[description_key] for description in list_to_medications if description['ENCOUNTER']==medication_encounter_id][0]
                        set_of_description.update([(encounter_description,medication_description)]) #creating set of each medication and encounter description
    return (list(set_of_description))

# do not modify below this line

def write_ndjson(file_name, patients):
    with open(file_name, 'w') as output:
        for patient_id in patients:
            output.write(json.dumps(patients[patient_id], separators=(',', ':')) + "\n")

if __name__ == "__main__":
    # part 1
    patients = create_patient_dictionary('data/csv/patients.csv')
    add_encounters_to_patients(patients, 'data/csv/encounters.csv')
    add_medications_to_patients(patients, 'data/csv/medications.csv')
    write_ndjson('out/assignment03.ndjson', patients)

    # part 2
    codes = problem1(patients)
    print(codes)
    descriptions = problem2(patients)
    print(descriptions)