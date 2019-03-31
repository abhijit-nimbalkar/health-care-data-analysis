'''
Requirement 1
File path-: ./src/main/resources/synthea.properties
open the file synthea.properties and change following properties to true
exporter.ccda.export = true
exporter.fhir.export = true
exporter.csv.export = true
exporter.text.export = true

Requirement 2
Running follwoing command
run_synthea -s 12345 -p 100 Pennsylvania Pittsburgh
result will get saved in output folder
'''

##Requirement 3
import argparse
import os
import sys
import subprocess

##Clearning the terminal
def clear_terminal():
    if(sys.platform=='win32'):
        os.system("cls")
    else:
        os.system("clear")

##Creating default forlder for generated data files from Synthea
def create_default_folder(current_dir,file_name):
    new_data_dir=os.path.join(current_dir,file_name)
    try:
        os.makedirs(new_data_dir)
    except:
        print("After successful completion ot process, data will be generated to the dir:",new_data_dir)
    return(new_data_dir)

##Parsing an argument. All arguements are optional
def parsing_argument():
    parser = argparse.ArgumentParser()
    try:
        default_path=os.path.normpath(os.getcwd() + os.sep + os.pardir)
        default_synthea_path=default_path+os.sep+"synthea"
        parser.add_argument("--script",default=default_synthea_path,help="path to the synthea script including the script name e.g. ~/synthea/run_synthea")

        new_data_dir=create_default_folder(os.getcwd(),"data")
        parser.add_argument("--data",default=new_data_dir,help="path to the data directory for this assignment e.g. ~/assignments/data")
    except:
        print("Please enter valid file formats for script and data files.")
    try:
        parser.add_argument("--population", default="100",type=int, help="number of living patients to include in the population")
    except:
        print("Please enter numeric population figure.")
    try:
        parser.add_argument("--seed", type=int,default="12345",help="random seed to use in patient generation")
    except:
        print("Please enter valid seed number. Ex. 12345")
    try:
        parser.add_argument("--state",nargs='*',default=["\"Pennsylvania\""],help="state to use when generating data")
    except:
        print("Please enter valid State. Make sure you enter state name in double or single quote. Eg. \"New York\"")
    try:
        parser.add_argument("--city",nargs='*',default=["\"Pittsburgh\""],help="city to use when generating data")
    except:
        print("Please enter valid City. Make sure you enter City name in double or single quote. Eg. \"San Diego\"")

    args = parser.parse_args()    
    return args


##Getting path of synthea##
def getting_path_for_synthea(script):
    existing_dir=os.getcwd()
    user_defined_path=os.path.abspath(script)
    if(os.path.isabs(user_defined_path)):
        base_path=os.path.basename(user_defined_path)
        if(base_path.lower()=="run_synthea"):
            return os.path.dirname(user_defined_path), existing_dir
        else:
            return user_defined_path, existing_dir
    else:
        print("The path you have specified does not exist. Please enter valid path where synthea is installed.")

##setting path to output the data generated from Synthea commond##
def setting_path_for_data_dir(script,data_path):
    path_for_synthea_dir, existing_dir=getting_path_for_synthea(script)
    path_for_synthea_property=os.path.join(path_for_synthea_dir,'src','main','resources')
    existing_dir=os.getcwd()
    os.chdir(path_for_synthea_property)
    newline=os.linesep
    new_data_path=os.path.abspath(data_path)
    
    if(sys.platform=='win32'):
        new_data_path="/".join(data_path.split(os.path.sep))+"/"+newline
    else:
        new_data_path=data_path+"/"+newline
    
    with open('synthea.properties',"r") as f:
        lines=f.readlines()
    
        lines[0]="exporter.baseDirectory = "+new_data_path

    with open('synthea.properties',"w") as f:
        f.writelines(lines)
    os.chdir(existing_dir)


##Running Synthea command
def run_synthea(script,data_dir,population,seed,state,city):
    path_for_synthea_dir, existing_dir=getting_path_for_synthea(script)
    os.chdir(path_for_synthea_dir)
    #running synthea command
    if(sys.platform=='win32'):
        synthea_run_cmd=".\\run_synthea.bat"+" -p %d -s %s %s %s"%(population,seed,state,city)
    else:
        synthea_run_cmd="./run_synthea"+" -p %d -s %s %s %s"%(population,seed,state,city)
    try:
        process=subprocess.Popen(synthea_run_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        status = process.wait()
        if(status):
            print("Error occured! Because of one of the following reason.\n1)State and city are not correct combination.\n2)You have not entered the argument correctly.\n3)Please follow the proper format.")
        else:
            print("Process completed successfully!")
    except:
        print("Seems like Synthea is not installed in your machine. Please install synthea and try to run the command.")
    finally:
        os.chdir(existing_dir)


def main():
    clear_terminal()
    args=parsing_argument()             #getting the argument from above defined function
    args.state=" ".join(args.state)     #handling state name if it has more that one words eg. New york
    args.city=" ".join(args.city)       #handling state name if it has more that one words eg. San Diego

    args.state="\"{}\"".format(args.state)
    args.city="\"{}\"".format(args.city)

    setting_path_for_data_dir(args.script,args.data)    #setting the data_dir file path if user has provided new file path
    run_synthea(args.script,args.data,args.population,args.seed,args.state,args.city)   #running the synthea command with provided arguments from user

if __name__=="__main__":
    main()
