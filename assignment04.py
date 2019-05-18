#Abhijit Nimbalkar (asnimbal)

import sys
import os
import json
import numpy as np
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import fhirclient.models.bundle as b
import seaborn as sns
from textwrap import wrap




def get_fhir_object_list(bundle_path,object_name='Patient'):
    fhir_dir=os.path.abspath(bundle_path)       #getting absolute path of fhir file directory 
    
    if not os.path.exists(fhir_dir):            #Checking if that file already exist
        print("Path to fhir diretory does not exist. Please provide the correct path of fhir directory to execute the program.")
        return 0    
    
    try:
        list_of_all_files=[file for file in os.listdir(fhir_dir) if os.path.isfile(os.path.join(fhir_dir,file))]    #listing out all files from directory
    except:
        print("There are no files in existing directory. Please try running program again.")
        return 0

    fhir_objects=[]
    
    for file in list_of_all_files:
        bundle=parse_bundle_for_file(os.path.join(fhir_dir,file))           #creating bundle object of each file
        fhir_objects.append(get_objects_from_bundle(bundle,object_name))    #appending each bundle in the claim list
    
    flattened_objects=[obj for fhir_obj in fhir_objects for obj in fhir_obj]     #as resource object was not one dimentional. creating 1d list of bundle objects
    return flattened_objects


def parse_bundle_for_file(fhir_bundle_path):
    with open(fhir_bundle_path,'r', encoding="utf8") as f:
        fhir_object=json.load(f)            #loading bundle object
    try:
        bundle=b.Bundle(fhir_object)        #initiating bundle object
        return bundle
    except:
        print("There are no fhir format files in the provided directory. Please try again.")
        return


def get_objects_from_bundle(bundle, object_name="Patient"):
    objects=[entry.resource for entry in bundle.entry if entry.request.url==object_name]   #parsing required object with given name
    return(objects)

def get_age(birth_date):                  #function to get age with given date
    today = date.today()          
    age= today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return(age)


def get_resource_data(resource_object,attribute1,attribute2,attribute3="age"):  #getting resource data with given attributes
    data={}
    for obj in resource_object:
        if eval(f"obj.{attribute1}") not in data.keys():                        #checking if attribute already exist in dictionary 
            data[eval(f"obj.{attribute1}")]=[]
        try:
            if (isinstance(eval(f"obj.{attribute2}"),date)):                    #if resource data is of date instance
                if(attribute3.lower()=="age"):                                  #if user wants to know age
                    data[eval(f"obj.{attribute1}")].append(get_age(eval(f"obj.{attribute2}")))  #insterting a value in a key
                if(attribute3.lower()=="dead_or_not"):
                    if(hasattr(obj,attribute2.split('.',1)[0])):
                        data[eval(f"obj.{attribute1}")].append('True')
            elif isinstance(eval(f"obj.{attribute2}"),str):                        #if resource data is of string format
                data[eval(f"obj.{attribute1}")].append(eval(f"obj.{attribute2}"))
        except:
            data[eval(f"obj.{attribute1}")].append('False')
    return data

def get_observation_resource_data(resource_object,attribute1,attribute2,resources): #getting resource data from observation object
    data={}
    for obj in resource_object:
        if(eval(f"obj.{attribute1}") in resources):
            if eval(f"obj.{attribute1}") not in data.keys():
                data[eval(f"obj.{attribute1}")]=[]
            try:
                if eval(f"obj.{attribute1}")=='55284-4':
                    data[eval(f"obj.{attribute1}")].append(obj.component[0].valueQuantity.value)
                else:
                    data[eval(f"obj.{attribute1}")].append(eval(f"obj.{attribute2}"))
            except:
                pass
    return data


def plot_age_by_gender(bundle_path, figure_name='q1_age_by_gender.png'):
    """17 points for correctness, 3 Points for Style and Efficiency
    See https://briankolowitz.github.io/data-focused-python/individual-project/project-description.html
    Save the figure to a PNG file with the specified figure_name
    Note : you CANNOT use Numpy or Pandas
    Note : you MUST ONLY use matplotlib
    
    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    patients=get_fhir_object_list(bundle_path)                      #get all patients object
    data=get_resource_data(patients,"gender","birthDate.date","age")#get required resource data to plots
    
    #plot the required data
    plt.suptitle("Patient age by gender")
    
    s1=plt.subplot(1,2,1)
    s1.yaxis.tick_right()
    s1.set_yticklabels([])
    plt.hist(data['male'],bins=20,color='#8b0000',orientation='horizontal')
    plt.gca().invert_xaxis()
    plt.xlabel("Count")
    s1.title.set_text("Male")
    
    s2=plt.subplot(1,2,2)
    plt.hist(data['female'],bins=20,color='#00008b',orientation='horizontal')
    plt.xlabel("Count")
    s2.title.set_text("Female")
       
    plt.savefig(figure_name, facecolor='grey')
    plt.show()

def plot_by_gender_and_race(bundle_path, figure_name='q2_by_gender_and_race.png'):
    """17 points for correctness, 3 Points for Style and Efficiency
    See https://briankolowitz.github.io/data-focused-python/individual-project/project-description.html
    Save the figure to a PNG file with the specified figure_name
    Note : you CANNOT use Numpy or Pandas
    Note : you MUST ONLY use matplotlib
    
    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    patients=get_fhir_object_list(bundle_path)                                                  #get all patients object
    data=get_resource_data(patients,"gender","extension[0].extension[0].valueCoding.display")   #get required data from patient object
    
    #plot the required data
    male_x=sorted(list(set(data['male'])))
    female_x=sorted(list(set(data['female'])))
    
    male_y=[data['male'].count(x) for x in male_x]
    female_y=[data['female'].count(x) for x in female_x]    
    
    width=0.2
    x_labels=[ '\n'.join(wrap(l, 20)) for l in male_x ]
    xm = [x for x in range(len(male_x))]
    xf = [x+width for x in xm]
    xpo= [x+width/2 for x in xm]
    
    ax = plt.subplot()
    ax.bar(xm, male_y, width, color='#8b0000', label='Male')
    ax.bar(xf, female_y, width, color='#00008b', label='Female')
    
    ax.set_ylabel('Number of Patients')
    ax.set_xticklabels(x_labels)
    ax.set_xticks(xpo)
    ax.set_title('Patients by Gender and Race')
    ax.legend()

    plt.savefig(figure_name, facecolor='grey')
    plt.show()

def plot_by_gender_and_birth_country(bundle_path, figure_name='q3_by_gender_and_birth_country.png'):
    """17 points for correctness, 3 Points for Style and Efficiency
    See https://briankolowitz.github.io/data-focused-python/individual-project/project-description.html
    Save the figure to a PNG file with the specified figure_name
    Note : you CANNOT use Numpy or Pandas
    Note : you MUST ONLY use matplotlib
    
    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    patients=get_fhir_object_list(bundle_path)                                      #get all patients object
    data=get_resource_data(patients,"gender","extension[4].valueAddress.country")   #get all required data
    
    #plot required data
    male_x=set(data['male'])
    female_x=set(data['female'])
    
    total_x=sorted(list(male_x.union(female_x)))
    
    male_y=[data['male'].count(x) for x in total_x]
    female_y=[data['female'].count(x) for x in total_x]    
    
    width=0.2
    x_labels=total_x
    xm = [x for x in range(len(total_x))]
    xf = [x+width for x in xm]
    xpo= [x+width/2 for x in xm]
    
    ax = plt.subplot()
    ax.bar(xm, male_y, width, color='#8b0000', label='Male')
    ax.bar(xf, female_y, width, color='#00008b', label='Female')
    
    ax.set_ylabel('Number of Patients')
    ax.set_xticklabels(x_labels)
    ax.set_xticks(xpo)
    ax.set_title('Patients by Gender and Birth_Country')
    ax.legend()

    plt.savefig(figure_name,  facecolor='grey')
    plt.show()

def plot_by_gender_and_mortality(bundle_path, figure_name='q4_by_gender_and_mortality.png'):
    """17 points for correctness, 3 Points for Style and Efficiency
    See https://briankolowitz.github.io/data-focused-python/individual-project/project-description.html
    Save the figure to a PNG file with the specified figure_name
    Note : you CANNOT use Numpy or Pandas
    Note : you MUST ONLY use matplotlib
    
    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    patients=get_fhir_object_list(bundle_path)                                              #get all patients object
    data=get_resource_data(patients,"gender","deceasedDateTime.date.date()","dead_or_not")  #get all required data
    
    #plot required data
    male_x=sorted(list(set(data['male'])))
    female_x=sorted(list(set(data['female'])))
    
    male_y=[data['male'].count(x) for x in male_x]
    female_y=[data['female'].count(x) for x in female_x]    
    
    width=0.2
    x_labels=male_x
    xm = [x for x in range(len(male_x))]
    xf = [x+width for x in xm]
    xpo= [x+width/2 for x in xm]
    
    ax = plt.subplot()
    ax.bar(xm, male_y, width, color='#8b0000', label='Male')
    ax.bar(xf, female_y, width, color='#00008b', label='Female')
    
    ax.set_ylabel('Number of Patients')
    ax.set_xticklabels(x_labels)
    ax.set_xticks(xpo)
    ax.set_title('Patients by Gender and Deceased')
    ax.legend()

    plt.savefig(figure_name,  facecolor='grey')
    plt.show()

def plot_condition_comorbidity_matrix(bundle_path, figure_name='q5_condition_comorbidity_matrix.png'):
    """5 Points
    Plot the condition comorbidity matrix showing the top conditions.
    See https://briankolowitz.github.io/data-focused-python/individual-project/project-description.html
    Save the figure to a PNG file with the specified figure_name

    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    conditions=get_fhir_object_list(bundle_path,object_name="Condition")
    patient_dict_conditions=get_resource_data(conditions,"subject.reference","code.coding[0].display","subject_ref")
    for index, condition in enumerate(patient_dict_conditions.values()):
        column_names=sorted(list(set(condition)))
        row_names=sorted(list(set(condition)))
        if index==0:
            matrix=np.ones((len(condition),len(condition)),dtype=np.int32)
            df=pd.DataFrame(matrix,columns=column_names,index=row_names)
        else:
            for row in row_names:
                for col in column_names:
                    if col not in df.index:
                        df.loc[col]=0   
                        df[col]=0
                    element=df.loc[row][col]
                    element+=1
                    df.loc[row][col]=element
    df=df.iloc[0:15,0:15]
           
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)
    matrix=ax.matshow(df, interpolation='nearest')
    
    for (i, j), z in np.ndenumerate(df):
        ax.text(j, i, z, ha='center', va='center', color='white')
    
    fig.colorbar(matrix)
    ax.xaxis.tick_bottom()
    ax.set_xticklabels(['']+list(df.index), rotation='vertical',minor=False)
    ax.set_yticklabels(['']+list(df.columns),minor=False)  
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.set_title('Condition Comorbidity')
    plt.xlabel('Condition')
    plt.ylabel('Condition')   
    
    plt.savefig(figure_name,  facecolor='grey')
    plt.show()


def plot_challenge_question_1(bundle_path, figure_name='q6_challenge_question_1.png'):
    """5 Points
    Plot anything you want that uses at least 2 FHIR resources
    Save the figure to a PNG file with the specified figure_name

    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    patients=get_fhir_object_list(bundle_path)                                      #get all patients object
    data=get_resource_data(patients,"gender","maritalStatus.coding[0].display")     #get required data from object
    #change the abbreviation in obtained data
    data['female']=['Married' if w=='M' else w for w in data['female']]
    data['male']=['Married' if w=='M' else w for w in data['female']]
    data['female']=['Never Married' if w=='S' else w for w in data['female']]
    data['male']=['Never Married' if w=='S' else w for w in data['female']]
    data['female']=['UnMarried' if w=='U' else w for w in data['female']]
    data['male']=['UnMarried' if w=='U' else w for w in data['female']]
    data['female']=['Widowed' if w=='W' else w for w in data['female']]
    data['male']=['Widowed' if w=='W' else w for w in data['female']]
    data['female']=['Divorced' if w=='D' else w for w in data['female']]
    data['male']=['Divorced' if w=='D' else w for w in data['female']]
    
    #plot the required data
    male_x=set(data['male'])
    female_x=set(data['female'])
    
    total_x=sorted(list(male_x.union(female_x)))
    
    male_y=[data['male'].count(x) for x in total_x]
    female_y=[data['female'].count(x) for x in total_x]    
    
    width=0.2
    x_labels=total_x
    xm = [x for x in range(len(total_x))]
    xf = [x+width for x in xm]
    xpo= [x+width/2 for x in xm]
    
    ax = plt.subplot()
    ax.bar(xm, male_y, width, color='#8b0000', label='Male')
    ax.bar(xf, female_y, width, color='#00008b', label='Female')
    
    ax.set_ylabel('Number of Patients')
    ax.set_xticklabels(x_labels)
    ax.set_xticks(xpo)
    ax.set_title('Patients by Gender and Marital_Status')
    ax.legend()

    plt.savefig(figure_name,  facecolor='grey')
    plt.show()
    
def plot_challenge_question_2(bundle_path, figure_name='q7_challenge_question_2.png'):
    """5 Points
    Plot anything you want that uses at least 2 FHIR resources
    Save the figure to a PNG file with the specified figure_name

    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    #plotting scatter plot Total Blood Pressure Vs Total Cholesterol
    observations=get_fhir_object_list(bundle_path,object_name="Observation")   #get all required observation objects
    observation_dict=get_observation_resource_data(observations,"code.coding[0].code","valueQuantity.value",['2093-3','55284-4']) #get required data
    
    if(len(observation_dict['55284-4']) > len(observation_dict['2093-3'])):
        observation_dict['55284-4']=observation_dict['55284-4'][:len(observation_dict['2093-3'])]
    else:
        observation_dict['2093-3']=observation_dict['2093-3'][:len(observation_dict['55284-4'])]
    
    observation_dict['Total Blood Pressure']=observation_dict.pop('55284-4')
    observation_dict['Total Cholesterol']=observation_dict.pop('2093-3')
    
    #plot the required data
    df = pd.DataFrame.from_dict(observation_dict, orient='index')
    df.index.rename('Observation', inplace=True)

    stacked = df.stack().reset_index()
    stacked.rename(columns={0: 'Value'}, inplace=True)
    
    sns.swarmplot(data=stacked, x='Observation', y='Value', hue='Observation')
    
    plt.savefig(figure_name,  facecolor='grey')
    plt.show()
    
def plot_challenge_question_3(bundle_path, figure_name='q8_challenge_question_3.png'):
    """5 Points
    Plot anything you want that uses at least 3 FHIR resources
    Save the figure to a PNG file with the specified figure_name

    Arguments:
        bundle_path {str} -- path to Synthea generated FHIR bundles
    """
    #plotting box plot for Body Mass Index, Body Weight and Body Weight
    observations=get_fhir_object_list(bundle_path,object_name="Observation")
    observation_dict=get_observation_resource_data(observations,"code.coding[0].code","valueQuantity.value",['39156-5','29463-7','8302-2'])
    
    labels, data = [*zip(*observation_dict.items())]  
    labels, data = observation_dict.keys(), observation_dict.values()
    
    #plot required data
    box1=plt.boxplot(data,notch=True,vert=True,patch_artist=True)
    for patch, color in zip(box1['boxes'], ['lightgreen','lightblue','yellow']):
        patch.set_facecolor(color)
    plt.xticks(range(1, len(labels) + 1), ['Body Mass index','Body Weight','Body Height'])
    
    plt.savefig(figure_name,  facecolor='grey')
    plt.show()    

# do not modify below this line

if __name__ == "__main__":
    bundle_path = sys.argv[1]
    plot_age_by_gender(bundle_path)
    plot_by_gender_and_race(bundle_path)
    plot_by_gender_and_birth_country(bundle_path)
    plot_by_gender_and_mortality(bundle_path)
    plot_condition_comorbidity_matrix(bundle_path)
    plot_challenge_question_1(bundle_path)
    plot_challenge_question_2(bundle_path)
    plot_challenge_question_3(bundle_path)
