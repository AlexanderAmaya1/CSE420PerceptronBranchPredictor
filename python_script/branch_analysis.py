#*******************************************
#  Author: Alexander Amaya, Mason Blumling
#          Jacob Sumner, Sarah Hope Swaim
# 
#  Purpose: CSE 420 Semester Project
# 
#  Description: Performs an analysis on branch 
#  output files from all benchmarks.  
#******************************************


import csv
from fileinput import filename
import sys
from unicodedata import category

from sympy import E

def command_args():
   
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    file_name = ""


    if "-f" in opts:

        file_name = args[opts.index("-f")] 
        

    return file_name


def open_csv(file_name):
   
    with open(file_name, newline="\n") as csvfile:

        branch_reader = csv.reader(csvfile, delimiter=',')

        for row in branch_reader:
            branch_analysis(row)

    return 0

def write_csvs(filename):
    with open(filename+"_branches.csv", 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        cat = list(branch_dict[list(branch_dict.keys())[0]].keys())
        cat.insert(0,"branch_address")
        cat.pop()

        writer.writerow(cat)

        for key in list(branch_dict.keys()):
            row = []
            row = list(branch_dict[key].values())
            row.insert(0,key)
            row.pop()

            writer.writerow(row)

    with open(filename+"_targets.csv", 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        cat = list(target_dict[list(target_dict.keys())[0]].keys())
        cat.insert(0,"target_address")
     

        writer.writerow(cat)

        for key in list(target_dict.keys()):
            row = []
            row = list(target_dict[key].values())
            row.insert(0,key)
         

            writer.writerow(row)



def branch_analysis(row):

    try:

        if row[3] not in target_dict:
        
            target_address = {

                "branch_address" : [],
                "mispredicts" : 0,
                "correct_predicts" : 0

            }

            if row[4] != row[5]:
                target_address["mispredicts"] +=1
            else:
                target_address["correct_predicts"] +=1
        
            target_address["branch_address"].append(row[2])

            target_dict[row[3]] = target_address

        else:

            if row[4] != row[5]:
                target_dict[row[3]]["mispredicts"] +=1
            else:
                target_dict[row[3]]["correct_predicts"] +=1

            if(target_dict[row[3]]["branch_address"].count(row[2]) == 0):
                target_dict[row[3]]["branch_address"].append(row[2]) 

        if row[2] not in branch_dict:
            
            branch_stat = {
                
                "first_encounter_correct": False,
                "mispredicts" : 0,
                "correct_predicts": 0,
                "average_mispredict_distance" : 0,
                "correct_streak" : 0

            }

            if row[4] != row[5]:
                branch_stat["mispredicts"] += 1
                
            else:

                branch_stat["first_encounter_correct"] = True
                branch_stat["correct_predicts"] += 1
                branch_stat["correct_streak"] = 1

            branch_dict[row[2]] = branch_stat


        else:

            if row[4] != row[5]:
                branch_dict[row[2]]["mispredicts"] += 1
                
                branch_dict[row[2]]["average_mispredict_distance"] = int((branch_dict[row[2]]["average_mispredict_distance"] + branch_dict[row[2]]["correct_streak"]) /  branch_dict[row[2]]["mispredicts"])
                branch_dict[row[2]]["correct_streak"] = 0

            else:
                branch_dict[row[2]]["correct_predicts"] += 1
                branch_dict[row[2]]["correct_streak"] += 1

    except Exception as e:
       #print(e)
       #print(row)
       return

def main():

    file_name  = command_args()
    global branch_dict
    branch_dict = {}

    global target_dict
    target_dict = {}

    # Hardcoded for our benchmarks use -f to specify a single file
    fileNames = ["blackscholes___1___in_4K.txt___Black-Scholes_binary_output.txt.out",
                "bodytrack___sequenceB_1___4___1___1000___5___0___1.out",
                "cholesky___-p1_______tk14.0.out",
                "ferret___corel___lsh___queries___10___20___1___Ferret_binary_output.txt.out",
                "fft___-m16___-p1___Ferret_binary_output.txt.out",
                "fluidanimate___1___5___in_35K.fluid.out",
                "raytrace___happy_buddha.obj.out",
                "swaptions___-10___-5___-5___input_test___swaptions_binary_output.txt.out",
                "afi___F26-A64-D250K_bayes.dom___1000___1___1___afi_binary_output.txt.out",
                "loop___loop_binary_output.txt.out",
                "loopy___loop2_binary_output.txt.out",
                "stream.out",
                "multiplication.out",
                "patmch_______pattern.txt.out",
                "sudoku_______sudoku_input.txt.out"
                ]

    if file_name != "":
        open_csv(file_name)
        write_csvs(file_name)
    else:
        for f in fileNames:
            print("Analyzing: "+f)
            branch_dict = {}
            target_dict = {}

            open_csv(f)
            write_csvs(f)

    
if __name__ == "__main__":
    main()


