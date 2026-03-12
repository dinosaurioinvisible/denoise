#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.

#include "LoadMultipleFiles"

// ~ index
// 0. runCommandOnMacosShell - to run a simple command on macos
// 1. runPythonScriptOnMovieWindows - to run a script on a movie in windows
// 2. runPythonScriptOnMovieMacOs - to run a script on a movie in macos
// 3. definePythonInterpreterPath - to look up for, or change python interp.
// 4. runPythonScriptOnMovie - general function


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
// basic fx for running single shell commands in macos
function runCommandOnMacosShell(string command)
	string igorcmdx
	sprintf igorcmdx, "do shell script \"%s\"", command
	executeScriptText/z igorcmdx
	// print s_value
end


// 1
// this just executes a python script from the terminal - windows only
function runPythonScriptOnMovieWindows(string path_to_python_script, string path_to_movie)
	ExecuteScriptText "python "+path_to_python_script+" "+path_to_movie
end


// 2
// on mac this is a pain, mostly because of the "do shell script"
function runPythonScriptOnMovieMacOs(string path_to_python, string path_to_python_script, string path_to_movie)
	string igorcmd
	sprintf igorcmd, "do shell script \"%s %s %s\"", path_to_python, path_to_python_script, path_to_movie
	print igorcmd
   executeScriptText/b/z igorcmd
   print s_value
end


// 3
// this is a function that may be called only once
// we're creating a txt file that can be read every time pigthon is loaded
// the txt contains the path to the python interpreter
// it should be a button on an Igor panel to do this, even if only once
// especially in case user would like to change interpreter for any reason
strConstant pigtonPythonPath = "none"
// TODO 
// test for windows 
function definePythonInterpreterPath()
	// search for file in pigthon folder in user procedures
	string pigthonPath = SpecialDirPath("Igor Pro User Files", 0, 0, 0) + "User Procedures:Pigthon:"
	string pigthonPythonPath_txt = pigthonPath + "pigthon_path_to_python_interpreter.txt"
	variable fref
	string line
	string platform = IgorInfo(2)
	// r: read only, z: prevents abort if file doesn't exist
	open/r/z fref as pigthonPythonPath_txt
	if (v_flag != 0)
		// TODO
		// string message = "Select a Python interpreter"
		// is enough with python3 only?
		GetFileFolderInfo/d/q
		string pythonEnvironmentDir = s_path
		string pathToPython = pythonEnvironmentDir+"bin:python3"
		// for macos: make unix paths
		if (CmpStr(platform, "Windows") != 0)
			string unix_path_to_python = ParseFilePath(5, pathToPython, "/", 0, 0)
			string unix_path_to_txt = pigthonPythonPath_txt
			unix_path_to_txt = ReplaceString("Macintosh HD:", unix_path_to_txt, "/")
			unix_path_to_txt = ReplaceString(":", unix_path_to_txt, "/")
			string cmd
			// creates file and write path to python interpreter on it 
			sprintf cmd, "do shell script \"touch '%s' && echo %s >> '%s'\"", unix_path_to_txt, unix_path_to_python, unix_path_to_txt
			executeScriptText cmd
		else
			// TODO
			// re-check this
			ExecuteScriptText "python "+pathToPython+" > "+pigthonPythonPath_txt
		endif
	else
		freadLine fref, pathToPython
		close fref
	endif
	// save as constant
	string/g pigtonPythonPath = pathToPython
   print pigtonPythonPath
end


// 4
// runs script on movie depending whether system is windows or macos
function runPythonScriptOnMovie(string path_to_python_script, string path_to_movie, [string path_to_python])

	// 1. check whether python interpreter has been defined
	// TODO
	// on macos: mk file
	if (paramIsDefault(path_to_python) != 0)
		// this functions looks up for, or creates a txt file with the path to python
		// the path inside the txt file is made a global string = pigthonPythonPath
		definePythonInterpreterPath()
		// svar makes a reference to the global string pigthonPythonPath
		svar pigtonPythonPath = root:pigtonPythonPath
		// trim removes whitespaces & newlines, need because echo, but also just in case
		path_to_python = TrimString(pigtonPythonPath)
		// path_to_python = pigtonPythonPath
		print "path to python:"
		print path_to_python
	endif
	
	// 2. run python script from terminal
	// TODO
	// popup windows
	string platform = IgorInfo(2)
	if (CmpStr(platform, "Windows") == 0)
		RunPythonScriptOnMovieWindows(path_to_python_script, path_to_movie)
	else
		RunPythonScriptOnMovieMacOs(path_to_python, path_to_python_script, path_to_movie)
	endif
	
	// 3. load files in new folder in igor
	string dirpath
	if (CmpStr(platform, "Windows") == 0)
		dirpath = path_to_movie[0,strsearch(path_to_movie, "\\", strlen(path_to_movie)-1, 3)]
	else
		dirpath = path_to_movie[0,strsearch(path_to_movie, "/", strlen(path_to_movie)-1, 3)]
	endif
	string path_to_python_output = dirpath+"python_output"
	// print path_to_python_output
	LoadFiles(dirpath=path_to_python_output)
	
	// 4. remove temporal folders
	
	
end







// example for windows
// string path_to_python = "none"
// string path_to_python_script = "C:\Users\Fernando\zf\denoise\ks_method.py"
// string path_to_movie = "'C:\Users\Fernando\Desktop\Steps_pre_AF10_a1015.tif'"

// example for macos
// string path_to_python = "/Users/f/vi/bin/python3"
// path_to_python = "/Users/f/vi/bin/python3" (to hardcode inside function)
// string path_to_python_script = "/Users/f/Dropbox/_r66y/r66xe/denoise/igor_fxs.py"
// string path_to_movie = "/Users/f/Dropbox/_r66y/r66xe/2p_data/glu_a2/Steps_pre_AF10_a1014.tif"



