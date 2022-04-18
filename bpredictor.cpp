//******************************************
// Author: Alexander Amaya
// Email: amamaya2@asu.edu
// Purpose: CSE 420 Lab 2
// Description: Creates a tournament branch
// predictor using Intel Pin tools. 
//******************************************
#include <iostream>
#include <stdio.h>
#include <assert.h>
#include <fstream> 
#include <cmath>
#include <vector>

#include "pin.H"
using namespace std;

static UINT64 takenCorrect = 0;
static UINT64 takenIncorrect = 0;
static UINT64 notTakenCorrect = 0;
static UINT64 notTakenIncorrect = 0;

ofstream outfile;
UINT64 insCount = 0;
UINT64 branchCount =0;

class BranchPredictor {

  public:
  BranchPredictor() { }

  virtual BOOL makePrediction(ADDRINT address) {return FALSE;};

  virtual void makeUpdate(BOOL takenActually, BOOL takenPredicted, ADDRINT address) {};

};

int global_index = 0;

//One bit predictor based on a finite state machine
struct oneBitPredictor{
  bool prediction = true;
  
  void update_prediction(bool taken_actuallly){
    if(prediction != taken_actuallly){
      prediction = taken_actuallly;
    }
  }

  bool get_prediction(UINT64 address){
    return prediction;
  }
};

//two bit predictor based on a finite state machine
struct twoBitPredictor{

  UINT8 state = 0;

  void update_prediction(bool taken_actually){
    bool prediction = true;
      if(state < 2){prediction = true;}
      else{prediction = false;}

    if(taken_actually != prediction){
      
      if(state < 2){state++;}
      else{state--;}

    }else{

      if(state < 2 && state > 0){state--;}
      else if(state > 1 && state < 3){state++;}

    }

  }

  bool get_prediction(UINT64 address){
       if(state < 2){return true;}
       else{return false;}
  }
};

//Three bit predictor based on a 3bit finite state machine
struct threeBitPredictor{

  UINT8 state = 0;

  void update_prediction(bool taken_actually){
    bool prediction = true;
      if(state < 4){prediction = true;}
      else{prediction = false;}

    if(taken_actually != prediction){

      if(state < 4){state++;}
      else{state--;}

    }else{

      if(state < 4 && state > 0){state--;}
      else if(state > 3 && state < 7){state++;}

    }
  }

  bool get_prediction(UINT64 address){
       if(state < 4){return true;}
       else{return false;}
  }
};

struct correlatingPredictor{
  //Stores 12 bits of history information per index; all initially set to taken
  UINT16 last_results[512] = {4096-1};

  threeBitPredictor threeList[4096];

  void update_prediction(bool taken_actually, UINT64 address){
    // Update prediction
    threeList[last_results[address%512]].update_prediction(taken_actually);
    
    // Update history 
    if(taken_actually){
      last_results[address%512] = ((last_results[address%512] << 1) > 4096 -1)? ((last_results[address%512] << 1) - 4096 )+1 : (last_results[address%512] << 1) + 1;
    }else{
      last_results[address%512] = ((last_results[address%512] << 1) > 4096 -1 )? (last_results[address%512] << 1) - 4096 : (last_results[address%512] << 1);
    }

  }

  bool get_prediction(UINT64 address){
  
    return threeList[last_results[address%512]].get_prediction(address);

  }

};

struct gshare{
  //Stores 12 bits of history information; all initially set to taken
  UINT16 last_results = 8192-1;

  threeBitPredictor threeList[8192];


  void update_prediction(bool taken_actually, UINT64 address){

    // Update prediction
    threeList[(last_results) ^ (address%8192)].update_prediction(taken_actually);
    
    // Update last results 
    if(taken_actually){
      last_results = ((last_results << 1) > (8192 -1))? ((last_results << 1) - 8192) + 1 : (last_results << 1) + 1;
    }else{
      last_results = ((last_results << 1) > (8192-1))? (last_results << 1) - 8192: (last_results << 1);
    }
  }

  bool get_prediction(UINT64 address){
    return threeList[(last_results) ^ (address%8192)].get_prediction(address);

  }

};

struct perceptron{

 // 8192 rows of  weight registers 
  vector<INT64> weight[8192];

  // 8192 rows of n bit history registers 
  vector<INT64> history[8192];

  INT64 y[8192] = {0};

  INT64 threshhold = (int)floor(1.93*256+14);

  perceptron(){

    for(int i = 0; i < 8192; i++){

      for(int j = 0; j < 256; j++){

        history[i].push_back(1);
        weight[i].push_back(0);
      }

    }


  }

  void training(bool taken_actually, UINT64 address){
      INT64 last_taken = 0;
      if(taken_actually){
        last_taken = 1;
      }else{
        last_taken = -1;
      }

    if( abs(y[address%8192]) <= threshhold || ((y[address%8192] >= 0) != taken_actually)){

        for(int i  = 0; i < 256; i++){
          
          if(history[address % 8192][i] == last_taken){

            weight[address % 8192][i]++;

          }else{

            weight[address % 8192][i]--;

          }
            

        }

    }




  }

  void update_prediction(bool taken_actually, UINT64 address){

      INT64 last_taken = 0;

      if(taken_actually){
        last_taken = 1;
      }else{
        last_taken = -1;
      }


      //Update History
      history[address % 8192].push_back(last_taken);
      history[address % 8192].erase(history[address%8192].begin());
      
      weight[address % 8192].push_back(0);
      weight[address % 8192].erase(weight[address%8192].begin());

      //Train
      training(taken_actually, address);

      INT64 running = weight[address%8192][255];



      for(UINT64 i = 1; i < 256; i++){

        running += (weight[address%8192][i]*history[address%8192][i]);

      }


      y[address%8192] = running;




  }

  bool get_prediction(UINT64 address){

   if(y[address%8192] >= 0)
    return true;
   else
    return false;

  }

};


struct tournament{

  UINT8 selector[512] = {0};

  correlatingPredictor localPredictor;
  gshare globalPredictor;


  void update_prediction(bool taken_actually, UINT64 address){

    //update the selector value
    if( (taken_actually != localPredictor.get_prediction(address)) && (taken_actually == globalPredictor.get_prediction(address))){

      if(selector[address%512] < 3){selector[address%512]++;}


    }else if((taken_actually == localPredictor.get_prediction(address)) && (taken_actually != globalPredictor.get_prediction(address))){

      if(selector[address%512] > 0){selector[address%512]--;}

    }

    //update the both predictors based on the last results
    localPredictor.update_prediction(taken_actually, address);
    globalPredictor.update_prediction(taken_actually, address);

  }

  bool get_prediction(UINT64 address){
    // If selector is less than 2 the the local predictor's prediction is returned; else global prediction is returned. 
    if(selector[address%512] < 2){return localPredictor.get_prediction(address);}
    else{return globalPredictor.get_prediction(address);}

  }


};


class myBranchPredictor: public BranchPredictor {
  public:
  myBranchPredictor() {

  }

   tournament predictor;

  BOOL makePrediction(ADDRINT address){

    return predictor.get_prediction(address);

  }

  void makeUpdate(BOOL takenActually, BOOL takenPredicted, ADDRINT address){

    predictor.update_prediction(takenActually,address);

  }
  
};

myBranchPredictor* BP;


// This knob sets the output file name
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "result.out", "specify the output file name");

void branch_output(ADDRINT address, BOOL takenActually, BOOL takenPredicted ){

  outfile << insCount << "," << branchCount << "," <<address << "," << takenActually << "," << takenPredicted << "\n";
 
}


void handleBranch(ADDRINT ip, BOOL direction)
{

  BOOL prediction = BP->makePrediction(ip);
  BP->makeUpdate(direction, prediction, ip);
  branchCount++;

  if(prediction && direction){

    takenCorrect++;

  }else if(!prediction && direction){

    notTakenIncorrect++;

  }else if(prediction && !direction){

    takenIncorrect++;


  }else{

    notTakenCorrect++;

  }

  branch_output(ip,direction, prediction);

}

VOID instrCount(UINT32 maxR){
    
    insCount++;

}

void instrumentBranch(INS ins, void * v)
{ 

  INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)instrCount, IARG_END);

  if(INS_IsBranch(ins) && INS_HasFallThrough(ins)) {
    INS_InsertCall(
      ins, IPOINT_TAKEN_BRANCH, (AFUNPTR)handleBranch,
      IARG_INST_PTR,
      IARG_BOOL,
      TRUE,
      IARG_END); 

    INS_InsertCall(
      ins, IPOINT_AFTER, (AFUNPTR)handleBranch,
      IARG_INST_PTR,
      IARG_BOOL,
      FALSE,
      IARG_END);
  }
}


void ml_stats(ofstream& outfile){

    double truePositives = (double)takenCorrect;
    double falsePositives = (double)notTakenIncorrect;
    double falseNegatives = (double)takenIncorrect;
    double trueNegatives = (double)notTakenCorrect;

    double accuracy = (truePositives + trueNegatives) / (truePositives + falseNegatives + falsePositives + trueNegatives);
    double sensitivity = truePositives / (truePositives + falseNegatives);
    double specifity = trueNegatives / (falsePositives + trueNegatives);
    double truePositiveRate = sensitivity;
    double falsePositiveRate = 1 - specifity;
    double precision = truePositives / (truePositives + falsePositives);
    double f1_score = 2 * ((precision * sensitivity) / (precision + sensitivity));

    string roc_analysis = "";
    if ((truePositiveRate == 1) && (falsePositiveRate == 0)) {
        roc_analysis = "perfect";
    }
    else if (falsePositiveRate > truePositiveRate) {
        roc_analysis = "worse";
    }
    else if (truePositiveRate > falsePositiveRate) {
        roc_analysis = "better";
    }
    else if (truePositiveRate == falsePositiveRate) {
        roc_analysis = "random";
    }

  outfile << "TP: " << truePositives << "\nFP: " << falsePositives << "\nTN: " << trueNegatives << "\nFN: " << falseNegatives << "\n\nACCURACY: " << accuracy << "\nSensitivity: " << sensitivity << "\nSpecifity: " << specifity << "\nPrecision: " << precision << "\nF1 Score: " << f1_score << "\n\nTrue Positive Rate: " << truePositiveRate << "\nFalse Positive Rate: " << falsePositiveRate << "\n\nROC: " << roc_analysis << "\n";

}

/* ===================================================================== */
VOID Fini(int, VOID * v)
{ 
  double sum = (takenCorrect+takenIncorrect+notTakenCorrect+notTakenIncorrect);
  double sum_correct = takenCorrect+notTakenCorrect;
  double percent = sum_correct/sum * 100;
  
  cout << "\nPercent Accuracy: " << percent <<endl;
  //cout << "Size of Predictor: " << sizeof(BP->predictor) << " bytes out of 4125 bytes "<<endl;



  //ofstream outfile;
  ///outfile.open(KnobOutputFile.Value().c_str());
 // outfile.setf(ios::showbase);
  //outfile << "takenCorrect: "<< takenCorrect <<"  takenIncorrect: "<< takenIncorrect <<" notTakenCorrect: "<< notTakenCorrect <<" notTakenIncorrect: "<< notTakenIncorrect <<"\n";
  
  //ml_stats(outfile);

  //outfile.close();
}



// argc, argv are the entire command line, including pin -t <toolname> -- ...
int main(int argc, char * argv[])
{


    // Make a new branch predictor
    BP = new myBranchPredictor();

    // Initialize pin
    PIN_Init(argc, argv);

    outfile.open(KnobOutputFile.Value().c_str());
    outfile.setf(ios::showbase);

    // Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(instrumentBranch, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    outfile.close();

    return 0;
}



