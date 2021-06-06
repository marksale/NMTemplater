<h2># NMTemplater</h1>
<h2>Python code to generate NONMEM control files from template, tokens and specification file</h2>
There are four input files, arguments to makeControlFiles: <br>
   template file (ASCII text)<br>
   tokens file (JSON)<br>
   population file (JSON) - will eventually be optional, if missing will generate random population<br>
   options file (JSON) - note the the nmfePath is hard coded in this, likely will need to change with an installation. Currently c:\nm744\util\nmfe74.bat<br>
   final arugument is the home folder for the anlaysis.<br>

requirements:
Should run on Windows or Linux
Python 
