#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.

//This function loads locomotion and QA traces of images pre-processed with Suite2P.

Function LoadingSuite2P()
	//Find FOV folders in root path
	String pathroot = "C:Data:Adoracion:20250207"
	newpath/o S_path, pathroot
	String Directories = IndexedDir(S_path, -1, 0)
	wave/t WaveFOV = ListToTextWave(Directories, ";")
	Variable NumFields = dimsize(WaveFOV, 0)
	Variable i
	string expcode = "ori"
	string filename, pathstr, RegPlaneStr, pathROIMask, DFF0Str1, DFF0Str2, LocoChStr, LocoStr

	for (i=0;i<NumFields;i+=1)

	//Load registered planes
		String FOVIndex = WaveFOV[i]
		pathstr= pathroot + ":" + FOVIndex
		Variable FOVIndex2 = str2num(FOVIndex)
		if (FOVIndex2 < 10)
			filename = expcode + "_0000"
		elseif (FOVIndex2 >= 10)
			filename = expcode + "_000"
		endif

		RegPlaneStr= filename + FOVIndex + "_Ch1_nr.tif"
		AutoLoadScanImage(pathstr, RegPlaneStr)
		Killdatafolder Tag0

	//Load ROIs
		pathROIMask = pathstr + ":Suite2P_out.mat"
		MLLoadWave/Q/O/M=2/Y=4/E/V/S pathROIMask
		string ROIMask= "ROIMask_" + expcode + FOVIndex
		Rename ROIWave, $ROIMask

	//Calculate DFF0
		RegPlaneStr= filename + FOVIndex + "_Ch1_nr"
		DFF0($ROIMask, $RegPlaneStr)
		DFF0Str2= "QA_Nor_" + expcode + FOVIndex
		DFF0Str1= filename + FOVIndex + "_Ch1_nr_DFF0"
		Rename $DFF0Str1, $DFF0Str2
		String USWave1 = filename + FOVIndex + "_Ch1_nr"			//Waves I don´t use
		String USWave2 = filename + FOVIndex + "_Ch1_nr_sqr"
		String USWave3 = filename + FOVIndex + "_Ch1_nr_sqrROI"
	//Load raw images and calculate loco trace
		LocoChStr = filename + FOVIndex + "_Ch3.tif"
		AutoLoadScanImage(pathroot, LocoChStr)
		LocoChStr = filename + FOVIndex + "_Ch3"
		average($LocoChStr)
		wave Ch3Loco_AvUni
		Locotocm_s(Ch3Loco_AvUni) //Transform Loco from intensity values to cm/s
		LocoStr= "Loco_" + expcode + FOVIndex
		Rename Ch3Loco_AvUni, $LocoStr

	//SetScale
		variable delta = 0.1647446457990115
		SetScale/P x 0, delta,"", $LocoStr
		SetScale/P x 0, delta,"", $DFF0Str2

	//KillWaves
		killwaves/Z Ch3Loco_Av, destFrame, DFF_S2p, ExcluderegMovie, Histo, QA_NP_S2p, QA_S2p, ROI, tempFrame, tempFrameMovie, tempMovie
		killdatafolder/z Tag0
		killwaves/z $USWave1, $USWave2, $USWave3, $LocoChStr

	endfor
end
