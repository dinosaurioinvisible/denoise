#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.


Function RunPythonScriptOnMovie(string path_to_python, string path_to_python_script, string path_to_movie)
	// run python script from terminal
	string platform = IgorInfo(2)
	if (CmpStr(platform, "Windows") == 0) 
		RunPythonScriptOnMovieWindows(path_to_python_script, path_to_movie)
	else
		RunPythonScriptOnMovieMacOs(path_to_python, path_to_python_script, path_to_movie)
	endif
	// open files in new folder in igor
	string dirpath = path_to_python_script[0,strsearch(path_to_python_script, "\\", strlen(path_to_python_script)-1, 3)]
	string path_to_python_output = dirpath+"python_output"
	LoadFiles(dirpath=path_to_python_output)
End


// this just executes a python script from the terminal - windows only
Function RunPythonScriptOnMovieWindows(string path_to_python_script, string path_to_movie)
	ExecuteScriptText "python "+path_to_python_script+" "+path_to_movie
End


// on mac this is a pain
function RunPythonScriptOnMovieMacOs(string path_to_python, string path_to_python_script, string path_to_movie)
	string igorcmd
	sprintf igorcmd, "do shell script \"%s %s %s\"", path_to_python, path_to_python_script, path_to_movie
	print igorcmd
   ExecuteScriptText/B/Z igorcmd
   Print S_value
End

stringbyKey(

// windows
// string path_to_python = "none"
// string path_to_python_script = "C:\Users\Fernando\zf\denoise\ks_method.py"
// string path_to_movie = "'C:\Users\Fernando\Desktop\Steps_pre_AF10_a1015.tif'"

// macos
// string path_to_python = "/Users/f/vi/bin/python3"
// string path_to_python_script = "/Users/f/Dropbox/_r66y/r66xe/denoise/igor_fxs.py"
// string path_to_movie = "'/Users/f/Dropbox/_r66y/r66xe/2p_data/glu_a2/Steps_pre_AF10_a1014.tif"

