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
	loader()
End


// this just executes a python script from the terminal - windows only
Function RunPythonScriptOnMovieWindows(string path_to_python_script, string path_to_movie)
	ExecuteScriptText/B "python "+path_to_python_script+" "+path_to_movie
End


// on mac this is a pain
function RunPythonScriptOnMovieMacOs(string path_to_python, string path_to_python_script, string path_to_movie)
	string igorcmd
	sprintf igorcmd, "do shell script \"%s %s %s\"", path_to_python, path_to_python_script, path_to_movie
	print igorcmd
   ExecuteScriptText/B/Z igorcmd
   Print S_value
End


// string path_to_python = "/Users/f/vi/bin/python3"
// string path_to_python_script = "/Users/f/Dropbox/_r66y/r66xe/denoise/igor_fxs.py"
// string path_to_movie = "'/Users/f/Dropbox/_r66y/r66xe/2p_data/glu_a2/Steps_pre_AF10_a1014.tif"


function loader()
    //initialize loop variable
    variable i=0
    string wname,fname            //wave names and file name, respectively
    
    //Ask the user to identify a folder on the computer
    getfilefolderinfo/D
    
    //Store the folder that the user has selected as a new symbolic path in IGOR called cgms
        //!!!!!!!!! if you prefer a different name, change ALL instances of cgms in the function !!!!!!!!
    newpath/O cgms S_path
 
    //Create a list of all files that are .txt files in the folder. -1 parameter addresses all files.
       // !!!!!!!!! if your files have a different extension, change .TXT below to your extension!!!!!!!!!!!!
    string filelist= indexedfile(cgms,-1,".TXT")
 
    //Begin processing the list
    do
        //store the ith name in the list into wname.
        fname = stringfromlist(i,filelist)
 
        //strip away ".txt" to get the name of the chromatogram, which is the file name
                //!!!!!!!!!! change the next line if you want a different name for the waves that are created !!!!!!!!!!!!!!!
        wname = fname[0,strlen(fname)-5]
 
        //reference a wave with the name of the chromatogram.
        wave w = $wname
        
        //if the referenced wave does not exist, create it.
        if (!waveexists(w) )
 
            //The /L parameter tells IGOR to load no headers, and to load the 3rd column of data (indexed as 2) only
                        //!!!!!!!! You must change this next line to tell IGOR how to load the data in each file !!!!!!!!!!!!!!!
            LoadWave/G/D/A=wave/P=cgms/O/L={0,0,0,2,0} stringfromlist(i,filelist)
 
            //wave created is wave0. It is renamed after the chromatogram.
            rename wave0 $wname
 
            //And scaled accordingly.
                        //!!!!!!!!! you MUST change or delete the following line according to your data's scaling or lack thereof. !!!!!!!!!!!!
            setscale/P x,0,0.0033333,$wname
            //Print confirmation of what was just loaded.
            print   "Loaded "+fname
 
        else 
            //Othewise, tell the user that this chromatogram was previously loaded.
            print   fname+" was previously loaded. Its corresponding wave exists."
        endif
        i += 1          //move to next file
    while(i<itemsinlist(filelist))          //end when all files are processed.
end