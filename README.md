# NMTemplater
Python code to generate NONMEM control files from template, tokens and specification file
There are three input files:
  control5_template.txt - this is the control file template, based loosely on the control5 example in the NONMEM installation
  Population2.txt - this is a JSON file with "genes" (in GA) for 46 models, 5 genees each. The genes correspond to the sequence of tokens in the tokens2.txt
  Tokens2.txt - JSON file with token sets:
              5 token groups - ADVAN,CL~WT, V~WT, KAETA and RESERR and 2 THETAs
              ADVAN has 2 token sets with 3 tokens each
              CL~WT has 3 token sets with 2 tokens each
              V~WT has 2 token sets with 2 tokens each
              KAETA has 2 token sets with 2 tokens each
              RESERR has 2 token sets with 2 tokens each
              
Note that the generated control files are not intended to be run, the models are not very sensible, (and no data set is provided).

requirements:
Should run on Windows or Linux
Python

To run:
  Install Python (https://www.python.org/)
  Install JSON ("pip install JSON: - without quotes, from command line; link = https://pypi.org/project/jsons/)
  Install regular expressions ("pip install regex" without quotes, from command line; link = https://pypi.org/project/regex/)

download files to some directory e.g, c:\GAtemplate
then from command line (6 steps):
start python (prompt will change to >>>)
import module
create control files
Check status of model 1 (should be 'Not Initialized")
write control files to disc (also pretends to run, but doesn't yet) - arguments are template file name, token file name, population file name, directory to be run in
Check status of model 1 (should be 'Done')


commands for this are:

python
import Templater
out = Templater.makeControlFiles("control5_Template.txt","Tokens2.txt","Population2.txt","c:\GAtemplate")
out[0][0].status
Templater.runModels(out[0]) 
out[0][0].status
