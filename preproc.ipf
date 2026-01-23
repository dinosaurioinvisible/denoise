#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.

// for preprocessing (de-interleave + register) of images in folder
Macro preProcessing()

	string dirpath = "path to images"
	string newdirpath = "path to preproc images" 
	
	// /O overwrites symbolic path if already exists
	NewPath/O/M="Choose folder with images to preprocess" pop
	

return pop