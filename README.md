<h2># NMTemplater</h1>
<h2>Python code to generate NONMEM control files from template, tokens and specification file</h2>
There are four input files, arguments to makeControlFiles: <br>
   template file (ASCII text)<br>
   tokens file (JSON)<br>
   population file (JSON) - will eventually be optional, if missing will generate random population<br>
   options file (JSON) - note the the nmfePath is hard coded in this, likely will need to change with an installation. Currently c:\nm744\util\nmfe74.bat<br>
   final arugument is the home folder for the anlaysis.<br>
<br>
requirements:<br>
Should run on Windows or Linux<br>
Python <br>

Same rules apply in the tokens, one line per THETA/ETA/EPS. so<br>
["*EXP(ETA(ETALAG))",<br>
			"*EXP(ETA(ETALAG))",<br>
			"$OMEGA  ;; diagonal OMEGA \n0.1 \t\t;; ETA(ETALAG) ETA ON ALAG1\n 0.1"<br>
		],<br>
		["*EXP(ETA(ETALAG1))",<br>
			"*EXP(ETA(ETALAG2))",<br>
			"$OMEGA BLOCK(2) ;; block OMEGA block \n0.1 \t\t;; ETA(ETALAG) ETA ON ALAG1\n 0.01 0.1"<br>
		]<br>
<br>
is legal - 2 ETAs, 2 rows. (note the \n that separate lines, so the $OMEGA BLOCK(2) will end up as<br>
$OMEGA BLOCK(2) ;; block OMEGA block <br>
0.1         ;; ETA(ETALAG) ETA ON ALAG1<br>
0.01 0.1<br>
The template file is identical to the previous. The tokens file is JSON. Note that JSON can be validated at<br>
https://jsonlint.com/<br>
this is very helpful.<br>
The population file, which will eventually be optional (include here for initial development and probably eventually for restarting interrupted runs), is also JSON.<br>
<br>
This version will run the generated code, and read the results using pharmpy.<br>



