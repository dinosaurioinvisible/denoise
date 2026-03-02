
#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.

////////////////////////////////////////////////////////////////////////////////////////////////////////
//This is the first function in workflow. 
//Input is: .csv file(s) from Bonzeb.  This is a 2D matrix. 1 or more files can be selected fro the dialog box.
//Output is the conversion  of csv(s) into IGOR 2D wave(s). first row of csv is for column labels 
////////////////////////////////////////////////////////////////////////////////////////////////////////
 


Function/S LoadFiles()
    Variable refNum
    String message = "Select one or more files"
    String outputPaths
    String fileFilters = "Data Files (*.txt,*.dat,*.csv):.txt,.dat,.csv;"
    fileFilters += "All Files:.*;"

    Open /D /R /MULT=1 /F=fileFilters /M=message refNum
    outputPaths = S_fileName
   
    if (strlen(outputPaths) == 0)
        Print "Cancelled"
    else
        Variable numFilesSelected = ItemsInList(outputPaths, "\r")
        Variable i
        for(i=0; i<numFilesSelected; i+=1)
            String path = StringFromList(i, outputPaths, "\r")
            Printf "%d: %s\r", i, path
          
            
            LoadWave/J/M/U={0,0,1,0}/D/A/K=0/L={0,0,0,0,0}/n=tempwave path
            String desiredName = ParseFilePath(3, path, ":", 0, 0)
            
            string loadedWavename="tempWave0" 
    Duplicate/O $loadedWavename, $desiredName
        endfor
   wave tempwave0     
   killwaves tempwave0
    endif
   
   
   
    return outputPaths      // Will be empty if user canceled
End

//Patricio 1/5/25