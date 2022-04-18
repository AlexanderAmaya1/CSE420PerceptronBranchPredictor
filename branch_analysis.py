import csv
from fileinput import filename
import sys

def command_args():
   
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]
    file_name = ""
    try:

        if "-f" in opts:

            file_name = args[opts.index("-f")] 
        


    except Exception as e:
        raise SystemExit("Specify the required options: -f")

    return file_name


def open_csv(file_name):
   
    with open(file_name, newline="\n") as csvfile:

        branch_reader = csv.reader(csvfile, delimiter=',')

        for row in branch_reader:
            branch_analysis(row)

    return 0

def branch_analysis(row):

    try:

        if row[2] not in branch_dict:

            branch_stat = {
                "wrong" : 0,
                "correct": 0
            }

            if row[3] != row[4]:
                branch_stat["wrong"] += 1
            else:
                branch_stat["correct"] += 1

            branch_dict[row[2]] = branch_stat
        else:
            if row[3] != row[4]:
                branch_dict[row[2]]["wrong"] += 1
            else:
                branch_dict[row[2]]["correct"] += 1

    except:
       return

def main():
    file_name  = command_args()
    global branch_dict
    branch_dict = {}
    open_csv(file_name)
    
    poplist = []

    for key in branch_dict:
        if branch_dict[key]["wrong"] < 100:
            poplist.append(key)
        elif branch_dict[key]["wrong"] - branch_dict[key]["correct"] < 0:
            poplist.append(key)    

    for key in poplist:
        branch_dict.pop(key)


    print(branch_dict)

    

if __name__ == "__main__":
    main()


# Addresses that contain more wrong than right (no minimum)
# Addresses that contain an order of magnitude more wrong than right
# Addresses that have wrong > 100 but have an order of magnitude more right
# per address what is the average distance between when two mispredicts only counting corrrect predictions of its on address
# PC range that are missing
# histograms for PC 
# run this script on both perceptron and tournament
# what stays consistant 

# how accurate on first encounter with PC

# percent of branches would be good to 