#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.

#include "LoadMultipleFiles"

// ~ index
// 1. runCommandOnMacosShell - to run a simple command on macos
// 2. runPythonScriptOnMovieWindows - to run a script on a movie in windows
// 3. runPythonScriptOnMovieMacOs - to run a script on a movie in macos
// 4. definePythonInterpreterPath - to look up for, or change python interp.
// 5. pigLoadMovie - simpler than ART Load, for python processing
// 6. pigSelectPythonScript - to choose a python script
// 7. pigRunPythonScriptOnMovie - general fx


// this is a small manual, for debugging or testing:
// (these examples kind of go increasing in difficulty)
// to execute a line command in the macos terminal from Igor:
	// string igorcmd0
	// command0 = "here goes any shell command"
	// sprintf igorcmd0, "do shell script \"%s\"", command0
	// executeScriptText/z igorcmd0
	// print s_value

	// other commands:
	// create an empty file
	// command0 = "touch ~/Desktop/test.txt"
	// create/write something into a file (> overwrites, >> appends new line)
	// command0 = "echo is invisibility a super power really?  >> ~/Desktop/test.txt"
	// you can put things together using &&
	// command0 = command0 = "touch ~/Desktop/test2.txt && echo im hungry now >> ~/Desktop/test2.txt"
	// note that you can do the same without writing out, for text-like output
	// command0 = "ls -a"
	// but then you have to look at it using:
	// print s_value 
	// (usually this shows issues if some, or nothing if fine)
	
	// now then, to look for python interpreters, first you'd do things like:
	// command0 = "find ~ name pyvenv.cfg -maxdepth 3 2>/dev//null >> test2.txt"
	// command0 = conda env list
	// for venvs or conda envs, respectively. Or, for system interepreters:
	// command0 = "which -a python3 >> ~/Desktop/test.txt"
	// but, results prob. be different from results in the actual terminal
	// in fact, for conda/venvs you most likely will see "exited with non-zero status" 
	// this is basically "not found", because Igor's $PATH is different, you can check with:
	// command0 = "echo $PATH >> ~/Desktop/test.txt"
	// or simply:
	// command0 = "echo $PATH" (and then checking s_value after executing)
	// so, either we pass the location to the interpreter (text or window) 
	// or search in common locations, like conda, miniconda, homebrew, etc
	// here we'll try to guess, and if this fails, ask for user input

// 0
// we want to define paths that can be reused
// for the path to the python interpreter: 
// there is a function that may be called only once
// we're creating a txt file that can be read every time pigthon is loaded
// the txt contains the path to the python interpreter
// that path (if exists) is loaded as a global variable


// 1
// basic fx for running single shell commands in macos
// print s_value isn't really needed, can be ommitted, but is useful
function runCommandOnMacosShell(string command)
	string igorcmdx
	sprintf igorcmdx, "do shell script \"%s\"", command
	executeScriptText/z igorcmdx
	print s_value
end


// 2
// this just executes a python script from the terminal - windows only
function runPythonScriptOnMovieWindows(string path_to_python_script, string path_to_movie)
	ExecuteScriptText "python "+path_to_python_script+" "+path_to_movie
end


// 3
// on mac this is a pain, mostly because of the "do shell script"
function runPythonScriptOnMovieMacOs(string path_to_python, string path_to_python_script, string path_to_movie)
	string igorcmd
	sprintf igorcmd, "do shell script \"%s %s %s\"", path_to_python, path_to_python_script, path_to_movie
	// better not to comment out these prints
	print "\nshell command:"
	print igorcmd
   executeScriptText/b/z igorcmd
   // this shows errors from python
   print "s_value:"
   print s_value
end


// 4
// look up for txt with python interpreter in default txt, otherwise create one
function pigDefinePythonInterpreterPath()
	// search for file in pigthon folder in user procedures
	string pigPath = SpecialDirPath("Igor Pro User Files", 0, 0, 0) + "User Procedures:Pig:"
	string pigPythonPath_txt = pigPath + "pig_path_to_python_interpreter.txt"
	variable fref
	string line
	string platform = IgorInfo(2)
	// try to read python interpreter location from txt file in pig folder
	// r: read only, z: prevents abort if file doesn't exist
	open/r/z fref as pigPythonPath_txt
	if (v_flag != 0)
		// TODO
		// string message = "Select a Python interpreter"
		// is enough with python3 only?
		GetFileFolderInfo/d/q
		string pythonEnvironmentDir = s_path
		string path_to_python = pythonEnvironmentDir+"bin:python3"
		// for macos: make unix paths
		if (CmpStr(platform, "Windows") != 0)
			string pathToPython = ParseFilePath(5, path_to_python, "/", 0, 0)
			// ParseFilePath fails if file doesn't exist yet
			string pathToTxt = pigPythonPath_txt
			pathToTxt = ReplaceString("Macintosh HD:", pathToTxt, "/")
			pathToTxt = ReplaceString(":", pathToTxt, "/")
			// for debugging
			// print unix_path_to_python
			// print unix_path_to_txt
			// create file and write path to python interpreter on it 
			string cmd
			sprintf cmd, "do shell script \"touch '%s' && echo %s >> '%s'\"", pathToTxt, pathToPython, pathToTxt
			executeScriptText cmd
			print "\npath to python saved at: "+pathToTxt
		else
			// TODO
			// windows
			// re-check this
			ExecuteScriptText "python "+pathToPython+" > "+pigPythonPath_txt
		endif
	// if txt file already exists
	else
		freadLine fref, pathToPython
		close fref
		print "\npython path in txt file at: "+pathToPython
	endif
	// save as constant - /g: global
	// string/g pigPythonPath = pathToPython
	string/g pigPathToPython = pathToPython
	// for debug:
   // print pigPythonPath
end


// 5
// loads movie only - split channels & ch2stimulus > in python
function pigLoadMovie()
	imageload/q/o/c=-1
	// flag=0 is no image in imageload
	if (v_flag == 0)
		Abort
	endif
	// remove extension
	string fileName = s_filename
	string movieName = s_filename[0,strsearch(s_filename,".tif",0)-1]+"_pig"
	if (waveExists($movieName))
		killwaves/z $movieName
	endif
	rename $s_filename, $movieName
	// retrieve necessary info
	string metadata = s_info
	// get info - to access note info: print note($"movieName")
	string expDate = stringByKey("state.internal.triggerTimeString",s_info,"=","\r")
	variable nframes = numberByKey("state.acq.numberOfFrames",s_info,"=","\r")
	variable nrows = numberByKey("state.acq.linesPerFrame",s_info,"=","\r")
	variable ncols = numberByKey("state.acq.pixelsPerLine",s_info,"=","\r")
	variable frameRate = numberByKey("state.acq.frameRate",s_info,"=","\r")
	variable msPerLine = numberByKey("state.acq.msPerLine",s_info,"=","\r")
	variable zoomFactor = numberByKey("state.acq.zoomFactor",s_info,"=","\r")
	note $movieName, "expDate="+expDate
	note $movieName, "nframes="+num2str(nframes)
	note $movieName, "nrows="+num2str(nrows)
	note $movieName, "ncols="+num2str(ncols)
	note $movieName, "frameRate="+num2str(frameRate)
	note $movieName, "msPerLine="+num2str(msPerLine)
	note $movieName, "zoomFactor="+num2str(zoomFactor)
	// note $movieName, metadata
	note $movieName, "fdir="+s_path
	note $movieName, "fname="+s_filename
	string filePath = s_path+s_filename
	note $movieName, "fpath="+filePath
	// convert to double precision floating point
	// redimension /d $movieName
	// make global string for path
	string platform = IgorInfo(2)
	if (CmpStr(platform, "Windows") != 0)
		string/g pigPathToMovie = parseFilePath(5,filePath,"/",0,0)
	endif
	print "\nloaded movie from: "+pigPathToMovie
end


// 6
// select python script
function pigSelectPythonScript()
	// d: dialog, r: read only
	string filter_script = ".py"
	string message_script = "select python script"
	Open/d/r/f=filter_script/m=message_script refNum
	string path_to_python_script = s_fileName
	print path_to_python_script
	// mode 5 is for macOS
	string platform = IgorInfo(2)
	if (CmpStr(platform, "Windows") != 0)
		path_to_python_script = parseFilePath(5,path_to_python_script,"/",0,0)
	endif
	string/g pigPathToScript = path_to_python_script
	print "\nselected python script at: "+pigPathToScript
end


// 7
// runs script on movie depending whether system is windows or macos
function pigRunPythonScriptOnMovie([string pathToPython, string pathToScript, string pathToMovie])
	// check platform
	string platform = IgorInfo(2)
	
	// 1. check for paths
	
	// 1.1 check whether python interpreter has been defined
	// TODO
	// on windows: mk file
	if (paramIsDefault(pathToPython) != 0)
		// this functions looks up for, or creates a txt file with the path to python
		// the path inside the txt file is made a global string = pigthonPythonPath
		pigDefinePythonInterpreterPath()
		// svar makes a reference to the global string pigPythonPath
		svar pigPathToPython = root:pigPathToPython
		// trim removes whitespaces & newlines, need because of echo + just in case
		pathToPython = TrimString(pigPathToPython)
	endif

	// 1.2 check for path to script	
	svar/z pigPathToScript = root:pigPathToScript
	// if script in args, make script as preferred
	if (paramIsDefault(pathToScript) == 0)
		string/g pigPathToScript = pathToScript
	// if not, and there is preferred script, used that
	elseif (svar_Exists(pigPathToScript) == 1)
		pathToScript = pigPathToScript
	else
		pigSelectPythonScript()
		pathToScript = pigPathToScript
	endif
	
	// 1.3 check path to movie
	svar/z pigPathToMovie = root:pigPathToMovie
	// same as 1.2
	if (paramIsDefault(pathToMovie) == 0)
		string/g pigPathToMovie = pathToMovie
	// if not, and there is preferred script, used that
	elseif (svar_Exists(pigPathToMovie) == 1)
		pathToMovie = pigPathToMovie
	else
		pigLoadMovie()
		pathToMovie = pigPathToMovie
	endif
	
	// print as check
	print "\npig:"
	print "path to python interpreter: "+pathToPython
	print "path to python script: "+pathToScript
	print "path to movie: "+pathToMovie
	
	// 2. run python script from terminal
	// TODO
	// popup windows
	if (CmpStr(platform, "Windows") == 0)
		RunPythonScriptOnMovieWindows(pathToScript, pathToMovie)
	else
		RunPythonScriptOnMovieMacOs(pathToPython, pathToScript, pathToMovie)
	endif
	
	// 3. load files in new folder in igor
	string dirpath
	if (CmpStr(platform, "Windows") == 0)
		dirpath = pathToMovie[0,strsearch(pathToMovie, "\\", strlen(pathToMovie)-1, 3)]
	else
		dirpath = pathToMovie[0,strsearch(pathToMovie, "/", strlen(pathToMovie)-1, 3)]
	endif
	string path_to_python_output = dirpath+"python_output"
	// for debugging
	print "temporal files at: "+path_to_python_output
	LoadFiles(dirpath=path_to_python_output)
	
	// 4. remove temporal folders
	// TODO
	// same for windows
	string cmd
	sprintf cmd, "do shell script \"rm -rf %s\"", path_to_python_output
	executeScriptText/z cmd
	print s_value
	
end





