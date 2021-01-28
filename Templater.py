import json
import re
#import tensorflow as tf
class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class Model:
    def __init__(self):
        self.modelNum = None
        self.control = self.output = None
        self.OFV = None
        self.CORR = self.COV = self.success = False
        self.eigenvalues = None
        self.code = []  # integer values for token indices
        self.status= "Not initialized"
        self.NTHETA =self.NOMEGA = self.NSIGMA = None
        self.THETA = self.OMEGA = self.SIGMA = None
        self.SETHETA = self.SEOMEGA = self.SESIGMA = None
        self.defaultTHETA = self.defaultSEOMEGA = self.defaultSESIGMA = None
        self.lastFixedTHETA = None
        self.lastFixedETA = None
        self.lastFixedEPS = None
        self.homeDir = None
    def runModel(self):
        with open('GAControl_' + str(self.modelNum) +".mod", 'w') as f: 
            f.write(self.control)
            f.close()
    def readOuput(self):
        self.OFV = -9999
         
 
def getFixedParms(Template):
     ## 

    NFixedTHETA,THETABlock = getFixedTHETA(Template)
    NFixedOMEGA = getFixedRandom(Template,"$OMEGA")
    NFixedSIGMA = getFixedRandom(Template,"$SIGMA")
     
 
    return  NFixedTHETA, NFixedOMEGA,  NFixedSIGMA

def removeComments(Code):
    
    lines = Code.splitlines()
    newCode = ""
    for thisline in lines:
        if thisline.find(";") > -1:
            thisline = thisline[:thisline.find(";")]
        newCode = newCode + thisline + '\n' 
    return newCode


def getFixedRandom(Code,key):
    Code = removeComments(Code) 
    nkeys = Code.count(key)
    # get the block from NONMEM control/temlate
    # e.g., $THETA, even if $THETA is in several sections
    # were key is $THETA,$OMEGA,$SIGMA
    block = ""
    start = 0
    end = 0
    nRandVars = 0
    for thisKey in range(nkeys):  
        start = Code.find(key,start)
        end = Code.find("$",start+1)
        block =  Code[start: end] + '\n'
        start = end +2
        # split each block , look for BLOCK()
        lines = block.splitlines()
        # does first line have "BLOCK(", if so 
        # should be on first line
        if lines[0].upper().find("BLOCK")> -1:
            lstart = lines[0].find("(")
            lend = lines[0].find(")",lstart + 1)
            blockDim = lines[0][(lstart+1):lend]
            try:
                nRandVars = nRandVars + int(blockDim)
            except:
                return "Cannot parse " + key + "Block"
        else: 
            for thisline in lines:
                thisline = thisline.strip()
                if thisline !='' and thisline!=key and thisline.find('{') == -1:
                    thisline = thisline.replace("FIXED","")
                    thisline = thisline.replace("FIX","")  
                    thisline = thisline.strip()  
                    while thisline.find("  ") !=-1:
                        thisline = thisline.replace("  "," ")
                    while thisline.find(" \n") !=-1:
                        thisline = thisline.replace(" \n","\n")       
                    thisline = thisline.replace("\n"," ")
                    thisline = thisline.replace(" ",",") 
                    thisline = thisline.split(',')
                    try:
                        nRandVars = nRandVars + len(thisline)            
                    except:
                        return "Cannot parse " + key + "Block"
            
    return nRandVars
def getFixedRandomall(Code,key):
        ## need to remove comments in case they have $THETA in them,
    ## then find first $OMEG/SIGMA, then next $*, until no more $THETA, buy by lines
     
    cleanCode = removeComments(Code)
    
    lines = cleanCode.splitlines()
    Code = Code.splitlines()
    randomBlock = []
    nLines = len(lines) 
    nkeys = 0
    for thisline in lines:
        if thisline.find(key) > -1:
            nkeys = nkeys + 1

    
    # get the block from NONMEM control/temlate
    # e.g., $THETA, even if $THETA is in several sections 
    start = 0 
    thisline = 0
    while thisline  < nLines: 
        if lines[thisline].find(key) > -1:
            randomBlock.append(Code[thisline])
            thisline = thisline + 1 

            while thisline < nLines and lines[thisline].find("$") == -1:
                randomBlock.append(Code[thisline])
                thisline = thisline + 1
        thisline = thisline + 1 
    return randomBlock

def getFixedTHETA(Code):
    key = "$THETA" 
    nkeys = Code.count(key)
    # get the block from NONMEM control/temlate
    # e.g., $THETA, even if $THETA is in several sections
    # were key is $THETA,$OMEGA,$SIGMA
    block = ""
    start = 0
    THETABlock = []
    for thisKey in range(nkeys):  
        start = Code.find(key,start)
        end = Code.find("$",start+1)
        block = block + Code[start: end] + '\n'
        start = end  
        ## remove blank lines, and trim
    lines = block.splitlines()
    THETABlock.append(lines)
    Code = ""
    for thisline in lines:
        thisline = thisline.strip()
        ### remove blanks, options and tokens
        if thisline !="" and thisline!=key and thisline.find("NUMBERP")== -1 and thisline.find("NUMP")== -1 and thisline.find("{") == -1:
            ## remove fixed
            thisline = thisline.replace("FIXED","")
            thisline = thisline.replace("FIX","")
            ## check for parens, if present, replace entire contens with collapsed
            if thisline.find("(")!=-1:
                ## collapse on ","s
                thisline = thisline.replace(",","")
                ## should be first position and last??
                thisline = thisline.strip()
                length = len(thisline)-1
                thisline = thisline[1:length]
            Code = Code + thisline + '\n' 

    ## replace "\n" witi ","
    while Code.find("  ") !=-1:
        Code = Code.replace("  "," ")
    while Code.find(" \n") !=-1:
        Code = Code.replace(" \n","\n")       
    Code = Code.replace("\n"," ")
    Code = Code.strip()
    Code = Code.replace(" ",",") 
    ## replace "  " with " "
    

    Code = Code.split(",")
 
def getFixedTHETAall(Code):
    ## need to remove comments in case they have $THETA in them,
    ## then find first $THETA, then next $*, until no more $THETA, buy by lines
     
    cleanCode = removeComments(Code)
    
    lines = cleanCode.splitlines()
    Code = Code.splitlines()
    THETABlock = []
    nLines = len(lines)
    key = "$THETA" 
    nkeys = 0
    for thisline in lines:
        if thisline.find(key) > -1:
            nkeys = nkeys + 1
    
    # get the block from NONMEM control/temlate
    # e.g., $THETA, even if $THETA is in several sections 
    start = 0 
    thisline = 0
    while thisline  < nLines: 
        if lines[thisline].find(key) > -1:
            THETABlock.append(Code[thisline])
            thisline = thisline + 1
            while thisline < nLines and lines[thisline].find("$") == -1:
                THETABlock.append(Code[thisline])
                thisline = thisline + 1
        thisline = thisline + 1 
    return THETABlock

def getFixedTHETA(Code):
    key = "$THETA" 
    nkeys = Code.count(key)
    # get the block from NONMEM control/temlate
    # e.g., $THETA, even if $THETA is in several sections
    # were key is $THETA,$OMEGA,$SIGMA
    block = ""
    start = 0
    THETABlock = []
    for thisKey in range(nkeys):  
        start = Code.find(key,start)
        end = Code.find("$",start+1)
        block = block + Code[start: end] + '\n'
        start = end  
        ## remove blank lines, and trim
    lines = block.splitlines()
    THETABlock.append(lines)
    Code = ""
    for thisline in lines:
        thisline = thisline.strip()
        ### remove blanks, options and tokens, comments
        while thisline.find(";") !=-1:
            thisline = thisline[0:thisline.find(";")]
        while thisline.find("\t") !=-1:
            thisline = thisline.replace("\t","")
        if thisline !="" and thisline!=key and thisline.find("NUMBERP")== -1 and thisline.find("NUMP")== -1 and thisline.find("{") == -1:
             ## remove comments
            while thisline.find(";") !=-1:
                thisline = thisline[0:thisline.find(";")]
            ## remove fixed
            thisline = thisline.replace("FIXED","")
            thisline = thisline.replace("FIX","")
            ## check for parens, if present, replace entire contens with collapsed
            ## for (lower,init,upper) syntax
            if thisline.find("(")!=-1:
                ## collapse on ","s
                thisline = thisline.replace(",","")
                ## should be first position and last??
                thisline = thisline.strip()
            #    length = len(thisline)-1
            #    thisline = thisline[1:length]
            Code = Code + thisline + '\n' 

    ## replace "\n" witih ","    
    ## get rid of any ","
  #  while Code.find(",") !=-1:
  #      Code = Code.replace(",","")
     
     
   # while Code.find("  ") !=-1:
   #     Code = Code.replace("  "," ")  
   # Code = Code.strip() 
    Code = Code.split()

    return len(Code),THETABlock


def cleanUpTemplate(Template):
    newTemplate = Template
    while newTemplate.rfind("{ ") > -1:
        newTemplate=newTemplate.replace("{ ","{") 
    while newTemplate.rfind("[ ") > -1:
        newTemplate=newTemplate.replace("[ ","[") 
    while newTemplate.rfind("( ") > -1:
        newTemplate=newTemplate.replace("( ","(") 
 
    while newTemplate.rfind(" }") > -1:
        newTemplate=newTemplate.replace(" }","}") 
    while newTemplate.rfind(" ]") > -1:
        newTemplate=newTemplate.replace(" ]","]") 
    while newTemplate.rfind(" )") > -1:
        newTemplate=newTemplate.replace(" )",")")  
    while newTemplate.rfind("] ") > -1:
        newTemplate=newTemplate.replace("] ","]") 
    while newTemplate.rfind(" [") > -1: 
        newTemplate=newTemplate.replace(" [","[") 
        ## remove all comments
    
    return newTemplate
 
def makeControlFiles(TemplateTextFile,tokensFile,populationFile,HomeDirectory): 
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
        tokens = json.loads(open(tokensFile,'r').read()) 
    except:
        return "Failed to parse JSON tokens in " + tokensFile
    try:    
        population = json.loads(open(populationFile,'r').read())  
    except:
        return "Failed to parse JSON population file in " + populationFile
    if len(population.get("Population")) <=0:
        errMsgs.append("Population size is 0")
        return errMsgs
    nModels = len(population.get("Population"))  
    ## get number of THETA, ETAS, EPS
    nFixedTHETA,nFixedETA,nFixedEPS = getFixedParms(TemplateText)
    
    Template = cleanUpTemplate(TemplateText) 
    for thisInd in range(nModels):  
        print("Starting " + str(thisInd))
        tempTemplate = Template 
        
        anyFound = False # are there any matching tokens in this model/individual ON FIRST PASS ONLY/if not, report and error
        thisModel =Model()  
        thisModel.homeDir = HomeDirectory
        thisModel.modelNum = thisInd
        thisModel.lastFixedTHETA=nFixedTHETA
        thisModel.lastFixedETA=nFixedETA
        thisModel.lastFixedEPS=nFixedEPS
        keyNum = 0  ## need keyNum just to assemble token text, e.g. [1]
        thisModelIndices = population.get("Population")[thisInd]
        ## subtract 1 from each index for 0 based array
        thisModelIndices = [x - 1 for x in thisModelIndices]
        theseTokenSets = [] # keep track of all tokenset for this model, will need for matchReferences
        for thisKey in tokens.keys(): 
            errMsgs.append(thisKey)
            if tempTemplate.rfind(thisKey) >= 0:   
                tokenSet = tokens.get(thisKey)[thisModelIndices[keyNum]] 
                theseTokenSets.append(tokenSet)
                tokenNum = 1
                for thistoken in tokenSet:  
                    replacementText =thistoken  
                    fullKey = "{" + thisKey + "[" + str(tokenNum)+"]"+"}"
                    tempTemplate=tempTemplate.replace(fullKey,replacementText) 
                    tokenNum = tokenNum + 1
            keyNum = keyNum + 1
        thisModel.control = tempTemplate 
        matchReferences(thisModel,theseTokenSets)
        thisModel.code = population.get("Population")[thisInd]  
        Models.append(thisModel)
       # print(thisModel.control)
    return Models,errMsgs,warnings

def matchTHETA(Model,tokenSets):  
    # get the required THETA(?) where ? is a letter 
    # find the sequence of those that appear in $THETA
    # put that sequence into THETA(A) etc.
    # for each token set, see if any include "THETA("
    # if they do, 
    #      get the letter index(s)
    #      get the position in the $THETA Block, must be only one token in $THETA per token set??
    #  Once you've gotten the positions of all THETA-including tokens in the $THETA block, you can assign indexes to
    #  the THETA(A
    # keep list of matched pairs, put back into original, to preserve comments, etc 
     
    ## sort tokenPositions 
## get positionn of any tokens in THETA Block
## need to get current THETAblock
## should not be "clear", keep comments etc
    THETABlock = getFixedTHETAall(Model.control) # return is a tuple, only need 
    nextTHETA = Model.lastFixedTHETA + 1
    ## need single string to search for position of THETA token in THETA block
    newTHETABlock = ""
    for thisline in THETABlock:
        newTHETABlock = newTHETABlock  + thisline + "\n" 
    
    THETABlock = newTHETABlock #' '.join([str(elem) for elem in THETABlock]) 
    ## need to remove comments from each line of fixedTHETABlock
    ## and from tokens
     
    ##fixedTHETABlock = removeComments(fixedTHETABlock)
    tokenPositions = []
    THETAIndices = [] ## for each token found in the $THETA, get any indices and write here
                      ## may be more than one index, need to parse the text found in the $THETA block 
                      ## to figure out how many indices are needed
    numTHETAs = []  ## number of thetas in each token, e.g., ADVAN[2] typically has 2, for k12 and k21
    for thisTokenSet in tokenSets: 
        for thistoken in thisTokenSet:       
            # get all tokens in $THETA block
            ## just for testing, remove comments
            testtoken = thistoken
          #  if testtoken.find(";"):
          #      testtoken = thistoken[:thistoken.find(";")]
            if THETABlock.find(testtoken) > -1 and testtoken.strip() != "": ## look for any tokens in the $THETA block
                ## get
                ## token may have init for more than one THETA, e.g., (0,1,4)\n(=1,0.1,4) or just 4 4
                ## are there ()? if so reduce to just contents
                ## if no (), then each value is a THETA init

                ## remove any comments, if still in THETAblock, then add
                tokenPosition = THETABlock.find(thistoken)
                if tokenPosition > -1: 
                    nTHETA = 0
                    # we have identified one or more theta(s) needing an index, based on position in $THETA
                    # next need to find the THETA(?) in that same token set
                    # find the corresponding token with the same stem in THETA(*)
                    # in tokens2.txt
                    # ADVAN has 3 tokens, 2 token sets
                    # CL~WT has 2 tokens, 3 token sets
                    # V~WT has 2 tokens, 2 token sets
                    # RESERR has 2 tokens, 2 token sets
                    
                    for thisTHETAtoken in thisTokenSet:
                        start = 0 
                        ## maybe more than one THETA in a token
                        ## need to remove comments
                        trimmedToken = removeComments(thisTHETAtoken)  
                        ## look for the start and the end of the the THETA(??) token
                        ##while trimmedToken.find("THETA(",start) > -1: ## \D not decimal digit
                        ## can use upper and lower case and ~ in tokens, cannot use digits or other special characters
                        # white space should already be gone, but space it there anyway
                        alltokens= re.findall("THETA\([ 0-9a-zA-Z~]+\)", trimmedToken)
                        for i in alltokens:
                            ## GET WHATEVER IS INSIDE {THETA()}
                            ## may be multiple THETAs  
                            start = i.find("THETA(")+6
                            last = i.find(")",start)
                            index = i[start:last]
                            index.replace("(","")
                            index.replace(")","")
                            index.replace("T","")
                            index.replace("H","")
                            index.replace("E","")
                            index.replace("A","")
                            while index.find(" ") > -1:
                                index = index.replace(" ","") 
                            THETAIndices.append(index) #i[start:last])  
                            nTHETA = nTHETA+1
                    if nTHETA > 0:
                        tokenPositions.append(tokenPosition)
                        numTHETAs.append(nTHETA)
                    nTHETA = 0
                            
   
    # have to generate entire set of token keys before matching references 
    # generate addition THETA indices, based on the tokenpositions in the $THETA block
    newIndices = []
    nTokenSets = len(tokenPositions)
    for thisset in range(nTokenSets):
        # for all entries in token positions, find the first, assign that token to the current index for THETA
        lowestIndex = tokenPositions.index(min(tokenPositions))
        nTHETA = numTHETAs[lowestIndex]
        ## loop over numTHETAs, add to new indices
        for thisindex in range(nTHETA):
            key = THETAIndices[sum(numTHETAs[0:lowestIndex])+thisindex ]
            value = nextTHETA
            newIndices.append ({"token":key,"replacement":value})
            nextTHETA = nextTHETA + 1
    ## remove lowest    
        tokenPositions.pop(lowestIndex)
        THETAIndices.pop(lowestIndex)
    ## and replace tokens
    for thisset in newIndices:
        old = "THETA(" + thisset['token'] + ")"
        new = "THETA(" + str(thisset['replacement'])+")" 
        Model.control = Model.control.replace(old,new)
   


def matchRandom(Model,tokenSets,key):  
    if key=="ETA":
        BlockKey = "$OMEGA"
        nextIndex = Model.lastFixedETA + 1
        grepString = "ETA\([ 0-9a-zA-Z~]+\)"
        searchString = "ETA("
    else:
        BlockKey = "SIGMA"
        nextIndex = Model.lastFixedEPS + 1
        grepString = "EPS\([ 0-9a-zA-Z~]+\)"
        searchString = "EPS("
    RandomBlock = getFixedRandomall(Model.control,BlockKey) # return is a tuple, only need  
     
    ## need single string to search for position of THETA token in THETA block
    newBlock = ""
    for thisline in RandomBlock:
        newBlock = newBlock  + thisline + "\n" 
    
    RandomBlock = newBlock #' '.join([str(elem) for elem in THETABlock]) 
    ## need to remove comments from each line of fixedTHETABlock
    ## and from tokens
     
    ##fixedTHETABlock = removeComments(fixedTHETABlock)
 
    tokenPositions = []
    Indices = [] ## for each token found in the $THETA, get any indices and write here
                      ## may be more than one index, need to parse the text found in the $THETA block 
                      ## to figure out how many indices are needed
    nRandoms = []  ## number of thetas in each token, e.g., ADVAN[2] typically has 2, for k12 and k21
    for thisTokenSet in tokenSets: 
        for thistoken in thisTokenSet:       
            # get all tokens in $THETA block
            ## just for testing, remove comments
            testtoken = thistoken
           # if testtoken.find(";"):
           #     testtoken = thistoken[:thistoken.find(";")]
            if RandomBlock.find(testtoken) > -1 and testtoken.strip() != "": ## look for any tokens in the $THETA block
                ## get
                ## token may have init for more than one THETA, e.g., (0,1,4)\n(=1,0.1,4) or just 4 4
                ## are there ()? if so reduce to just contents
                ## if no (), then each value is a THETA init

                ## remove any comments, if still in THETAblock, then add
                tokenPosition = RandomBlock.find(thistoken)
                if tokenPosition > -1: 
                    nRandom = 0
                    # we have identified one or more theta(s) needing an index, based on position in $THETA
                    # next need to find the THETA(?) in that same token set
                    # find the corresponding token with the same stem in THETA(*)
                    # in tokens2.txt
                    # ADVAN has 3 tokens, 2 token sets
                    # CL~WT has 2 tokens, 3 token sets
                    # V~WT has 2 tokens, 2 token sets
                    # RESERR has 2 tokens, 2 token setsdir
                    
                    for thisRandtoken in thisTokenSet:
                        start = 0 
                        ## maybe more than one THETA in a token
                        ## need to remove comments
                        trimmedToken = removeComments(thisRandtoken)  
                        ## look for the start and the end of the the THETA(??) token
                        ##while trimmedToken.find("THETA(",start) > -1: ## \D not decimal digit
                        ## can use upper and lower case and ~ in tokens, cannot use digits or other special characters
                        # white space should already be gone, but space it there anyway
                        alltokens= re.findall(grepString, trimmedToken)
                        for i in alltokens:
                            ## GET WHATEVER IS INSIDE {THETA()}
                            ## may be multiple THETAs  
                            start = i.find(searchString)+4
                            last = i.find(")",start)
                            index = i[start:last]
                            index.replace("(","")
                            index.replace(")","")
                            index.replace("T","")
                            index.replace("P","")
                            index.replace("E","")
                            index.replace("A","")
                            while index.find(" ") > -1:
                                index = index.replace(" ","") 
                            Indices.append(index) #i[start:last])  
                            nRandom = nRandom+1
                    if nRandom > 0:
                        tokenPositions.append(tokenPosition)
                        nRandoms.append(nRandom)
                    nRandom = 0
                            
   
    # have to generate entire set of token keys before matching references 
    # generate addition THETA indices, based on the tokenpositions in the $THETA block
    newIndices = []
    nTokenSets = len(tokenPositions)
    for thisset in range(nTokenSets):
        # for all entries in token positions, find the first, assign that token to the current index for THETA
        lowestIndex = tokenPositions.index(min(tokenPositions))
        nRandom = nRandoms[lowestIndex]
        ## loop over numTHETAs, add to new indices
        for thisindex in range(nRandom):
            key = Indices[sum(nRandoms[0:lowestIndex])+thisindex ]
            value = nextIndex
            newIndices.append ({"token":key,"replacement":value})
            nextIndex = nextIndex + 1
    ## remove lowest    
        tokenPositions.pop(lowestIndex)
        Indices.pop(lowestIndex)
    ## and replace tokens
    for thisset in newIndices:
        old = searchString + thisset['token'] + ")"
        new = searchString + str(thisset['replacement'])+")" 
        Model.control = Model.control.replace(old,new)          
   
    # have to generate entire set of token keys before matching references 
    # generate addition THETA indices, based on the tokenpositions in the $THETA block
    newIndices = []
    nTokenSets = len(tokenPositions)
    for thisset in range(nTokenSets):
        # for all entries in token positions, find the first, assign that token to the current index for THETA
        lowestIndex = tokenPositions.index(min(tokenPositions))
        nRandom = nRandoms[lowestIndex]
        ## loop over numTHETAs, add to new indices
        for thisindex in range(nRandom):
            key = Indices[sum(nRandoms[0:lowestIndex])+thisindex ]
            value = nextIndex
            newIndices.append ({"token":key,"replacement":value})
            nextIndex = nextIndex + 1
    ## remove lowest    
        tokenPositions.pop(lowestIndex)

         ## and replace tokens
    for thisset in newIndices:
        old = searchString+"(" + thisset['token'] + ")"
        new = searchString+"(" + str(thisset['replacement'])+")" 
        Model.control = Model.control.replace(old,new) 
   

def matchReferences(Model,tokenSets):
    matchTHETA(Model,tokenSets)  
    matchRandom(Model,tokenSets,"ETA")  
    matchRandom(Model,tokenSets,"EPS")  
    return Model

def runModels(Models):
    for thisModel in Models:
        thisModel.runModel()
        thisModel.status = "Done" 
 
     
#HomeDirectory = "c:\GAtemplate"
#Template= open("TwoComp_template.txt",'r').read()
#tokens = json.loads(open("TOKENS2COMP.TXT",'r').read())
#population = json.loads(open("POPULATION2COMP.TXT",'r').read() )  

Models, errMsgs,warnings = makeControlFiles("TwoComp_template.txt","TOKENS2COMP.TXT","POPULATION2COMP.TXT","c:\GAtemplate")
 
#print(Models[0].status)
#runModels(Models)
#print(Models[0].status)
 
