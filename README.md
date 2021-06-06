<h2># NMTemplater</h1>
<h2>Python code to generate NONMEM control files from template, tokens and specification file</h2>
There are four input files, arguments to makeControlFiles: <br>
   template file (ASCII text)<br>
   tokens file (JSON)<br>
   population file (JSON) - will eventually be optional, if missing will generate random population<br>
   options file (JSON) - note the the nmfePath is hard coded in this, likely will need to change with an installation. Currently c:\nm744\util\nmfe74.bat<br>
   final arugument is the home folder for the analysis.<br>
<br>
requirements:<br>
Should run on Windows or Linux<br>
Python 3.3 or later <br>
<br>
<br>
This will only support one level of nesting, but I've actually decided that is enough, keeping track of two levels is hard (and also results in genes that aren't used). I'm pretty sure I couldn't do three levels. I think I decided that it is better to have many token set in a single level than nested levels.
<h2>New constraints:<br></h2>
  Unlike previous, this doesn't require a tag for code for initial estimates But to keep track of THETA/ETA/EPS indices there is a new requirement that each THETA/ETA/EPS initial estimate must be on exactly one line. e.g.,<br>
$OMEGA BLOCK(2)<br>
1<br>
0.4 1   ; two etas, two lines<br>
<br>
is legal<br>
$OMEGA BLOCK(2)<br>
1 0.4 1   ; two ETAs one line<br>
<br>
is not, nor is<br>
$OMEGA BLOCK(2)<br>
1<br>
0.4 <br>
1 ;; two ETAs, three lines<br>
even though those are legal in NMTRAN. <br>
Comments/blank lines between lines is permitted, so<br>
<br>
$OMEGA BLOCK(2)<br>
;; first ETA<br>
1<br>
;; next ETA<br>
<br>
0.4 1<br>
is legal.<br>
Similar for THETA<br>
$THETA<br>
  (0,1,10) (0,2,20) (0,0.1,1)  ;; three THETAs, one line.<br>
is not legal, has to be<br>
$THETA<br>
 (0,1,10)<br>
 (0,2,20)<br>
 (0,0.1,1) ;; three THETAs, three line<br>
<br>
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
is legal (note the \n that separate lines, so the $OMEGA BLOCK(2) will end up as<br>
$OMEGA BLOCK(2) ;; block OMEGA block <br>
0.1         ;; ETA(ETALAG) ETA ON ALAG1<br>
0.01 0.1<br>
This the only way I could find to keep track of which token ended up with which<br>
<br>
The template file is identical to the previous. The tokens file is JSON. Note that JSON can be validated at<br>
https://jsonlint.com/<br>
<br>
this is very helpful.<br>
<br>
The population file, which will eventually be optional (include here for initial development and probably eventually for restarting interrupted runs), is also JSON.<br>

This version will run the generated code, and read the results using pharmpy, which looks somewhat useful.<br>
I think this should actually be pretty easy to implement in DEAP. Haven't yet implemented parallel execution/queue. I think, maybe DEAP will include that, not sure.<br>
At some point will need a GUI, writing the token JSON file in notepad is a pain.<br>
three examples included, example2 has nested tokens, example3 is linear (ADVAN2) vs nonlinear (ADVAN13).<br>
