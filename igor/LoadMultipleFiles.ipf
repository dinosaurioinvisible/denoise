
#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.

////////////////////////////////////////////////////////////////////////////////////////////////////////
// Input is any kind of file from a given folder
// Output is the conversion of files into IGOR 2D wave(s)
////////////////////////////////////////////////////////////////////////////////////////////////////////
 


Function/S LoadFiles([string dirpath])
	variable refNum
	string message = "Select one or more files"
	string outputPaths
	string fileFilters = "All Files"
	string sep = "\r"
	string platform = IgorInfo(2)

	// look for path
	if (paramIsDefault(dirpath) == 0)
		Print "Loading from: "+dirpath
		// dirpath has to end with ": or / or \"
		if (cmpstr(dirpath[0],dirpath[strlen(dirpath)-1]) != 0)
			// this is working for macOs
			// TODO
			// check again for windows
			dirpath += dirpath[0]
		endif
		sep = ";"
		// for macos only
		if (CmpStr(platform, "Windows") != 0)
			string macdirpath = "Macintosh HD:" + ReplaceString("/", dirpath[1,strlen(dirpath)-1], ":")
			newPath/O sdirpath, macdirpath
		else
			newPath/O sdirpath, dirpath
		endif
		// indexFile only takes symbolic path as arg1, not str
		// arg3 takes exactly 4 chars matching last 4 chars in filename
		outputPaths = indexedFile(sdirpath, -1, "????")
	else
		dirpath = ""
		Open /D /R /MULT=1 /F=fileFilters /M=message refNum
		outputPaths = S_fileName
	endif
   
	if (strlen(outputPaths) == 0)
		Print "Cancelled"
	else
		// for optional dirpath
		variable numFilesSelected = ItemsInList(outputPaths, sep)
		Variable iFile
		for(iFile=0; iFile<numFilesSelected; iFile+=1)
			String path = dirpath+StringFromList(iFile, outputPaths, sep)
			Printf "%d: %s\r", iFile, path
			// for macos
			if (CmpStr(platform, "Windows") != 0)
				path = "Macintosh HD:" + ReplaceString("/", path[1,strlen(path)-1], ":")
				// Printf "%d: %s\r", iFile, path
			endif
			// for igor fname in data browser
			string fname = ParseFilePath(3, path, ":", 0, 0)
			
			if (cmpStr(path[strlen(path)-4,strlen(path)-1], ".tif")  == 0)
				ImageLoad/Q/T=TIFF/N=$fname/S=0/C=-1/LR3D path
			elseif (cmpStr(path[strlen(path)-5,strlen(path)-1], ".tiff")  == 0) 
				ImageLoad/Q/T=TIFF/N=$fname/S=0/C=-1/LR3D path
			elseif (cmpStr(path[strlen(path)-4,strlen(path)-1], ".png")  == 0)
				ImageLoad/Q/T=rpng/N=$fname path
			elseif (cmpStr(path[strlen(path)-5,strlen(path)-1], ".jpeg")  == 0)	
				ImageLoad/Q/T=jpeg/N=$fname path
			elseif (cmpStr(path[strlen(path)-4,strlen(path)-1], ".csv")  == 0)
				LoadWave/J/M/U={0,0,1,0}/D/A/K=0/L={0,0,0,0,0}/n=$fname path
			elseif (cmpStr(path[strlen(path)-4,strlen(path)-1], ".txt")  == 0)
				LoadWave/J/M/U={0,0,1,0}/D/A/K=0/L={0,0,0,0,0}/n=$fname path
			else
				print fname
				print "No recognized file type (tif, tiff, png, jpeg, csv, txt)"
				print path
			endif 
			
		endfor
		wave tempwave0     
		killwaves tempwave0
	endif
   
	return outputPaths      // Will be empty if user canceled
End


// Patricio 1/5/25
// Fernando & Pawel 2/3/26