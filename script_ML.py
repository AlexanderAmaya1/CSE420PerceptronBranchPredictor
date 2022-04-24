from fileinput import filename
import sys
from texttable import Texttable
import matplotlib.pyplot as plt
  
def addROCValues():
    # add x-axis value
    x.append(FP_rate_float)
    # add y-axis value
    y.append(TP_rate_float)
    return

def saveLines(lines):
    # read and store benchmark's true positives results
    global TP
    TP = ""
    for char in lines[0]:
        if char.isdigit() or char == ".":
            TP += char
            
    # read and store benchmark's false positives results
    global FP
    FP = ""
    for char in lines[1]:
        if char.isdigit() or char == ".":
            FP += char
            
    # read and store benchmark's true negatives results
    global TN
    TN = ""
    for char in lines[2]:
        if char.isdigit() or char == ".":
            TN += char
            
    # read and store benchmark's false negatives results
    global FN
    FN = ""
    for char in lines[3]:
        if char.isdigit() or char == ".":
            FN+= char
            
    # read and store benchmark's accuracy results
    global accuracy
    accuracy = ""
    for char in lines[5]:
        if char.isdigit() or char == ".":
            accuracy += char
    global accuracy_float
    accuracy_float = float(accuracy)
    accuracy = "{:.8f}".format(accuracy_float)
    
    # read and store benchmark's sensitivity results
    global sensitivity
    sensitivity = ""
    for char in lines[6]:
        if char.isdigit() or char == ".":
            sensitivity += char
    global sensitivity_float
    sensitivity_float = float(sensitivity)
    sensitivity = "{:.8f}".format(sensitivity_float)
            
    # read and store benchmark's specifity results
    global specifity
    specifity = ""
    for char in lines[7]:
        if char.isdigit() or char == ".":
            specifity += char
    global specifity_float
    specifity_float = float(specifity)
    specifity = "{:.8f}".format(specifity_float)
    
    # read and store benchmark's precision results
    global precision
    precision = ""
    for char in lines[8]:
        if char.isdigit() or char == ".":
            precision += char
    global precision_float
    precision_float = float(precision)
    precision = "{:.8f}".format(precision_float)
            
    # read and store benchmark's f1_score results
    global f1_score
    f1_score = ""
    digit_found = False
    for char in lines[9]:
        if char.isdigit() or char == ".":
            if digit_found == False and char == "1":
                digit_found = True
            else:
                f1_score += char
    global f1_score_float
    f1_score_float = float(f1_score)
    fl_score = "{:.8f}".format(f1_score_float)
    
    # read and store benchmark's true positive rate results
    temp_TP_rate = ""
    for char in lines[11]:
        if char.isdigit() or char == ".":
            temp_TP_rate += char
    global TP_rate
    TP_rate = temp_TP_rate
    global TP_rate_float
    TP_rate_float = float(temp_TP_rate)

    # read and store benchmark's false positive rate results
    temp_FP_rate = ""
    for char in lines[12]:
        if char.isdigit() or char == ".":
            temp_FP_rate += char
    global FP_rate
    FP_rate = temp_FP_rate
    global FP_rate_float
    FP_rate_float = float(temp_FP_rate)
    
    #temp_roc_analysis = ""
    #if "better" in lines[14]:
     #   temp_roc_analysis = "better"
    #if "worse" in lines[14]:
     #   temp_roc_analysis = "worse"
    #if "perfect" in lines[14]:
     #   temp_roc_analysis = "perfect"
    #if "random" in lines[14]:
     #   temp_roc_analysis = "random"
    #global roc_analysis
    #roc_analysis = temp_roc_analysis
    
    return
            
    
def open_file(file_name):
    # list
    lines = []
    # save file lines to lines list
    with open(file_name, 'r') as file:
        lines = file.readlines()
        saveLines(lines)
    return
    
       
def plotROC():
    # for full plot
    # plot scatter plot points
    #counter = 0
    #for color in colors:
     #   plt.scatter(x[counter], y[counter], color=color, s=15)
      #  counter = counter + 1
    # set axis ranges
    #plt.xlim([0, 1])
    #plt.ylim([0, 1])

    
    # for zoomed in plot
    # plot scatter plot points
    counter = 0
    for color in colors:
        plt.scatter(x[counter], y[counter], color=color, s=150)
        counter = counter + 1
    # set axis ranges
    plt.xlim([0, 0.125])
    plt.ylim([0.8, 1])
     
    # x-axis label
    plt.xlabel('False Postive Rate')
    # frequency label
    plt.ylabel('True Positive Rate')
    # plot title
    plt.title('ROC Results')
    # showing legend
    plt.legend()
     
    # function to show the plot
    plt.show()
    return
       

def main():

    # tables
    global t
    t = Texttable()
    global t2
    t2 = Texttable()
    global t3
    t3 = Texttable()
    
    # colors for scatter plot
    global colors
    colors = ["darkblue", "darkgreen", "yellow", "black", "maroon", "red", "purple", "darkorange", "grey", "cyan", "lime", "pink", "magenta", "tan", "teal"]
    
    # format tables
    # set column widths
    t_widths = ["15", "10", "10", "10", "10"]
    t.set_cols_width(t_widths)
    t2_widths = ["15", "11", "11", "11", "11", "11", "11", "11"]
    t2.set_cols_width(t2_widths)
    t3_widths = ["15", "10"]
    t3.set_cols_width(t3_widths)
    # set columns align to center
    t.set_cols_align(["c", "c", "c", "c", "c"])
    t2.set_cols_align(["c", "c", "c", "c", "c", "c", "c", "c"])
    t3.set_cols_align(["c", "c"])
    # set columns type
    t.set_cols_dtype(["i", "i", "i", "i", "i"])
    t2.set_cols_dtype(["t", "t", "t", "t", "t", "t", "t", "t"])
    t3.set_cols_dtype(["t", "t"])

    # lists to hold coordinated for scatter plot
    global x
    x = []
    global x_index
    x_index = 0
    global y
    y = []
    global y_index
    y_index = 0
                
    # results files from benchmarks
    fileNames = ["bodytrack___sequenceB_1___4___1___1000___5___0___1.out",
                "cholesky___-p1_______tk14.0.out",
                "ferret___corel___lsh___queries___10___20___1___Ferret_binary_output.txt.out",
                "fft___-m16___-p1___Ferret_binary_output.txt.out",
                "fluidanimate___1___5___in_35K.fluid.out",
                "loop___loop_binary_output.txt.out",
                "loopy___loop2_binary_output.txt.out",
                "multiplication.out",
                "patmch_______pattern.txt.out",
                "raytrace___happy_buddha.obj.out",
                "stream.out",
                "sudoku_______sudoku_input.txt.out",
                "swaptions___-10___-5___-5___input_test___swaptions_binary_output.txt.out",
                "afi___F26-A64-D250K_bayes.dom___1000___1___1___afi_binary_output.txt.out",
                "blackscholes___1___in_4K.txt___Black-Scholes_binary_output.txt.out"]
    
    # add column titles
    t.header(["Benchmark", "TP", "FP", "TN", "FN"])
    t2.header(["Benchmark", "Accuracy", "Sensitivity", "Specifity", "Precision", "F1 Score", "True Positive Rate", "False Positive Rate"])
    t3.header(["Benchmark", "Color"])

    # for each results file/benchmark
    counter = 0
    for file in fileNames:
        open_file(file)
        
        file_str = ""
        if file == "bodytrack___sequenceB_1___4___1___1000___5___0___1.out":
            file_str = "Bodytrack"
        if file == "cholesky___-p1_______tk14.0.out":
            file_str = "Cholesky"
        if file == "ferret___corel___lsh___queries___10___20___1___Ferret_binary_output.txt.out":
            file_str = "Ferret"
        if file == "multiplication.out":
            file_str = "MatMul"
        if file == "patmch_______pattern.txt.out":
            file_str = "PatMCH"
        if file == "raytrace___happy_buddha.obj.out":
            file_str = "Raytrace"
        if file == "loop___loop_binary_output.txt.out":
            file_str = "Loops"
        if file == "loopy___loop2_binary_output.txt.out":
            file_str = "Loops 2"
        if file == "stream.out":
            file_str = "Stream"
        if file == "sudoku_______sudoku_input.txt.out":
            file_str = "Soduku"
        if file == "swaptions___-10___-5___-5___input_test___swaptions_binary_output.txt.out":
            file_str = "Swaptions"
        if file == "fluidanimate___1___5___in_35K.fluid.out":
            file_str = "Fluidanimate"
        if file == "fft___-m16___-p1___Ferret_binary_output.txt.out":
            file_str = "FFT"
        if file == "raytrace___happy_buddha.obj.out":
            file_str = "Raytrace"
        if file == "blackscholes___1___in_4K.txt___Black-Scholes_binary_output.txt.out":
            file_str = "Blackscholes"
        if file == "afi___F26-A64-D250K_bayes.dom___1000___1___1___afi_binary_output.txt.out":
            file_str = "AFI"
        
        # add a row for this benchmark to each table
        t.add_row([file_str, TP, FP, TN, FN])
        t2.add_row([file_str, accuracy, sensitivity, specifity, precision, f1_score, TP_rate, FP_rate])
        t3.add_row([file_str, colors[counter]])
        counter = counter + 1
        # add scatter plot point for this benchmark
        addROCValues()
    
    # draw tables
    print(t.draw())
    print("")
    print(t2.draw())
    print("")
    print(t3.draw())
    
    # plot scatter plot
    plotROC()
    
    return 0
  

if __name__ == "__main__":
    main()

