import json
import pickle
import re
from typing import OrderedDict
import collections
from unittest.mock import seal
import utils  
import os
import pharmpy  
from subprocess import DEVNULL, STDOUT, check_call, Popen
import time
os.chdir("e:/msale/GAtemplate")
class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Model:
    def __init__(self):
        self.modelNum = None
        self.control = self.output = self.controlBaseTokens = None
        #self.OFV = None
        #self.CORR = self.COV = self.success = False
        #self.eigenvalues = None
        self.code = []  # integer values for token indices
        self.status= "Not initialized"
        self.NTHETA =self.NOMEGA = self.NSIGMA = None
        self.THETA = self.OMEGA = self.SIGMA = None
        self.SETHETA = self.SEOMEGA = self.SESIGMA = None
        self.defaultTHETA = self.defaultSEOMEGA = self.defaultSESIGMA = None
        self.lastFixedTHETA = None  ## fixed THETA do not count toward penalty
        self.lastFixedETA =  self.lastFixedEPS =  self.homeDir =  self.template = None
        self.phenotype = None ## pheno type will be ordered dictionary, token stem:integer
        self.phenotypeHasTHETA = [] # for each token set does if have THETA(*) if so, which token(s), if not 0
        self.variableTHETAIndices = [] # for each token set does if have THETA(*) alphanumeric indices in THETA(*)
        self.THETAmatchesSequence = {} # dictionary of source (alpha) theta indices and sequence
                                       # e.g. THETA(ABC) is first in $THETA template, then THETA(DEF)
        self.THETABlock = self.nmfePath =  self.result = None
        self.Process = None
    def runModel(self):
        filestem = 'GAControl_' + str(self.modelNum)
        self.controlFileName = filestem +".mod"
        self.outputFileName = filestem +".lst"
        with open(self.controlFileName, 'w') as f: 
            f.write(self.control)  
        #cmd = [self.nmfe.path,self.controlFileName ,self.outputFileName]
        #os.system(cmd) 
        #check_call([self.nmfePath,self.controlFileName ,self.outputFileName], stdout=DEVNULL, stderr=STDOUT)
        self.Process = Popen([self.nmfePath,self.controlFileName ,self.outputFileName], stdout=DEVNULL, stderr=STDOUT)
        while(self.Process.poll()) == None:
            time.sleep(1)
        #with open(os.devnull, 'wb') as devnull:
         #   check_call(cmd, stdout=devnull, stderr=STDOUT)
        self.result = pharmpy.Model(self.controlFileName)
        #check_call([cmd], stdout=DEVNULL, stderr=STDOUT)
   
         
 
def getFixedParms(Template):
     ## broken !!!!

    NFixedTHETA,THETABlock = getFixedBlock(Template,"$THETA")
    NFixedOMEGA,OMEGABlock = getFixedBlock(Template,"$OMEGA")
    NFixedSIGMA,SIGMABlock = getFixedBlock(Template,"$SIGMA")
     
 
    return  NFixedTHETA, NFixedOMEGA,  NFixedSIGMA ,THETABlock,OMEGABlock,SIGMABlock 


def getFixedRandom(Code,key):   
    nkeys = Code.count(key)
    # get the block from NONMEM control/temlate
    # e.g., $THETA, even if $THETA is in several sections
    # were key is $THETA,$OMEGA,$SIGMA
    block = ""
    start = 0
    Block = []
    for thisKey in range(nkeys):  
        start = Code.find(key,start)
        end = Code.find("$",start+1)
        block = block + Code[start: end] + '\n'
        start = end  
        ## remove blank lines, and trim
    lines = block.splitlines()
    Block.append(lines)
    Code = []
    for thisline in lines:
        thisline = utils.removeComments(thisline).strip()
        ### remove blanks, options and tokens, comments 
        thisline = thisline.replace("FIXED","")
        thisline = thisline.replace("FIX","")
        if thisline != "":
            Code.append(thisline)
    return len(Code),Block

 

def getVariableTHETA(Code):
    ## need to remove comments in case they have $THETA in them,
    ## then find first $THETA, then next $*, until no more $THETA, by lines
     
    cleanCode = utils.removeComments(Code)
    
    lines = cleanCode.splitlines() 
    ## remove any blanks
    while("" in lines) :
        lines.remove("")
    varTHETABlock = [] 
    ## how many $THETA blocks - assume only 1 (for now??)
   
    for thisline in lines:
        if re.search("{.+}",thisline) !=None:
            varTHETABlock.append(thisline)
 
    return varTHETABlock


def getVariableRand(Code,BlockName):
    ## need to remove comments in case they have $THETA in them,
    ## then find first $THETA, then next $*, until no more $THETA, by lines
     
    cleanCode = utils.removeComments(Code)
    
    lines = cleanCode.splitlines() 
    ## remove any blanks
    while("" in lines) :
        lines.remove("")
    varBlock = [] 
    ## how many $THETA blocks - assume only 1 (for now??)
   
    for thisline in lines:
        if re.search("{.+}",thisline) !=None:
            varBlock.append(thisline)
 
    return varBlock

def getFixedBlock(Code,key): 
    nkeys = Code.count(key)
    # get the block from NONMEM control/temlate
    # e.g., $THETA, even if $THETA is in several sections
    # were key is $THETA,$OMEGA,$SIGMA
    block = ""
    start = 0
    FullBlock = []
    for thisKey in range(nkeys):  
        start = Code.find(key,start)
        end = Code.find("$",start+1)
        block = block + Code[start: end] + '\n'
        start = end  
        ## remove blank lines, and trim
    lines = block.splitlines()
    FullBlock.append(lines)
    Code = []
    nfixed = 0
    for thisline in lines: 
        ### remove blanks, options and tokens, comments
        thisline = utils.removeComments(thisline).strip()  
        ## count fixed only, n 
        if (thisline != "" and (not(re.search("^{.+}",thisline)))) and  not re.search("^\$.+",thisline):
            nfixed +=1
    return nfixed,FullBlock

 
def makeControlFiles(TemplateTextFile,tokensFile,populationFile,HomeDirectory,optionsFile): 
    Models = []
    errMsgs = []
    warnings = []
     
    try:    
        TemplateText= open(TemplateTextFile,'r').read()  
    except:
        return "Failed to open Template file " + TemplateTextFile
        ### json.load seems to return it's own error and exit immediately
        ## this try/except doesn't do anything
        
    try:    
        tokens = collections.OrderedDict(json.loads(open(tokensFile,'r').read()) )
        #print(tokens)
    except:
        return "Failed to parse JSON tokens in " + tokensFile
        
    try:    
       # options = collections.OrderedDict(json.loads(open(optionsFile,'r').read()) )
        with open (optionsFile, "r") as opfile:
            options = json.loads(opfile.read())
        #print(options["nmfePath"])
        #options = collections.OrderedDict(json.loads(open(optionsFile,'r').read()) )
        #print(tokens)
    except:
        return "Failed to parse JSON tokens in " + tokensFile
    try:    
        population = collections.OrderedDict(json.loads(open(populationFile,'r').read()))
    except:
        return "Failed to parse JSON population file in " + populationFile
    if len(population.get("Population")) <=0:
        errMsgs.append("Population size is 0")
        return errMsgs
    nModels = len(population.get("Population"))  
    ## get number of THETA, ETAS, EPS
    #print(TemplateText+"\n\n") 
    nFixedTHETA,nFixedETA,nFixedEPS, THETABlock, OMEGABlock,SIGMABlock = getFixedParms(TemplateText) 
    #Template = cleanUpTemplate(TemplateText) 
    varTHETABlock =  getVariableTHETA(THETABlock) # list of only the variable tokens in $THETA in template, will population with 
                                                  # tokens below
    varOMEGABlock =  getVariableRand(OMEGABlock,"OMEGA") # list of only the variable tokens in $THETA in template, will population with 
                                                  # tokens below
    varSIGMABlock =  getVariableRand(SIGMABlock,"SIGMA") # list of only the variable tokens in $THETA in template, will population with 
                                                  # tokens below
  
    for thisInd in range(nModels):
        thisModel =Model()
        thisModel.control = TemplateText ## need this to find tokens in $THETA, $OMEGA etc
        thisModel.homeDir = HomeDirectory
        thisModel.nmfePath = options["nmfePath"]
        thisModel.modelNum = thisInd
        thisModel.lastFixedTHETA=nFixedTHETA
        thisModel.lastFixedETA=nFixedETA
        thisModel.lastFixedEPS=nFixedEPS 
        phenotype =  population.get("Population")[thisInd] 
        thisModel.phenotype = OrderedDict(zip(tokens.keys(), phenotype))
        anyFound = True #keep looping, looking for nested tokens
        nLoops = 0 
     
        while anyFound:  
            nLoops = nLoops + 1 
            anyFound = False
            if nLoops > 9:
                return("Failed to find end of nested loops")
            anyFound, thisModel.control = utils.replaceTokens(tokens,thisModel.control,thisModel.phenotype)
   
        thisModel.control = utils.matchTHETAs(thisModel.control,tokens,varTHETABlock,thisModel.phenotype,thisModel.lastFixedTHETA)
        thisModel.control = utils.matchRands(thisModel.control,tokens,varOMEGABlock,thisModel.phenotype,thisModel.lastFixedETA,"ETA")
        thisModel.control = utils.matchRands(thisModel.control,tokens,varSIGMABlock,thisModel.phenotype,thisModel.lastFixedEPS,"EPS")
 
        thisModel.control+= "\n ;; Phenotype \n ;; " + str(thisModel.phenotype)
         
        Models.append(thisModel)
        if not(anyFound):
            errMsgs.append("No tokens found") 
    
 

    return Models,errMsgs,warnings 
  
 
def runModels(Models):
    for thisModel in Models:
        thisModel.runModel()
        thisModel.status = "Done" 

 
print("Starting example 1")
Models, errMsgs,warnings = makeControlFiles("example1_template.txt","example1_tokens.json","example1_pop.json","c:\GAtemplate","options.json")
runModels(Models)

print("Starting example 2")
Models, errMsgs,warnings = makeControlFiles("example2_template.txt","example2_tokens.json","example2_pop.json","c:\GAtemplate","options.json")
runModels(Models)

print("Starting example 3")
Models, errMsgs,warnings = makeControlFiles("example3_template.txt","example3_tokens.json","example3_pop.json","c:\GAtemplate","options.json")
runModels(Models)
 
