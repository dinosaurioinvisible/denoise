#pragma rtGlobals=1		// Use modern global access method.

#include "Sarfia"
#include "Resize"
#include "KalmanFilter"
#include "Corr_ROI"
#include "DeltaF"
//#include "ROIprobe"
#include "DeltaF"
//#include "Realign Mask"											//Paul removes to compile in Igor7 Jan17
#include "Timing"
//#include "Kmeansprobe"
#include "QuickROI"
#include "Segmentation"
#include "getinfo"
//#include "Scrub"														//Paul removes to compile in Igor7 Jan17
#include "AveRepsInMovie"
#include "LoadScanImage"
#include "RegisterStack"
#include "Regfolder"
#include "imshow"
#include "ROIbuddy"
#include "Ch2LineRes"													//fernando inclusion 1/26
#include "pig"															//fernando inclusion 3/26
// #include "pigthon_load_movie"

//NewDataFolder/O root:Packages:AROItools
//Variable/G root:Packages:AROItools:FOVatZoom1=610

Window AdvancedROI() : Panel_ART									//Paul adds "_ART" to differentiate from iGluSnFR panel...
	PauseUpdate; Silent 1		// building window...
	NewDataFolder/O root:Packages:AROItools
	Variable/G root:Packages:AROItools:FOVatZoom1=610
	
	// fernando: changing this to include pig
	// NewPanel /W=(993,45,1274,519) as "Advanced ROI tools"
	// /w=(left, top, right, bottom)
	NewPanel /W=(993,45,1274,666) as "Advanced ROI tools"
	ModifyPanel cbRGB=(19452,22124,22440)
	SetDrawLayer UserBack
	SetDrawEnv linethick= 0,fillfgc= (10283,48779,31735)
	DrawRRect 21,218,258,453
	SetDrawEnv linethick= 0,fillfgc= (60450,21530,15568)
	DrawRRect 32,274,246,325
	SetDrawEnv linethick= 0,fillfgc= (10283,48779,31735)
	DrawRRect 21,34,258,71
	SetDrawEnv fsize= 16,fstyle= 1,textrgb= (65535,65535,65535)
	DrawText 30,26,"Input"
	SetDrawEnv fsize= 16,fstyle= 1,textrgb= (65535,65535,65535)
	DrawText 30,101,"Process"
	SetDrawEnv linethick= 0,fillfgc= (10283,48779,31735)
	DrawRRect 21,105,258,179
	SetDrawEnv fsize= 16,fstyle= 1,textrgb= (65535,65535,65535)
	DrawText 31,212,"Explore"
	SetDrawEnv fsize= 15,textrgb= (65535,65535,65535)
	DrawText 39,273,"Segmentation"
	SetDrawEnv linethick= 0,fillfgc= (60450,21530,15568)
	DrawRRect 33,351,248,379
	SetDrawEnv fsize= 15,textrgb= (65535,65535,65535)
	DrawText 39,351,"Modify Mask"
	// Fernando included pig 3/26
	SetDrawEnv fsize= 16,fstyle= 1,textrgb= (65535,65535,65535)
	DrawText 30,485,"pig"
	// light green & orange rectangles
	SetDrawEnv linethick= 0,fillfgc= (10283,48779,31735)
	DrawRRect 20,495,255,605
	SetDrawEnv linethick= 0,fillfgc= (60450,21530,15568)
	DrawRRect 25,525,250,555
	// text in rectangle
	SetDrawEnv fsize= 15,textrgb= (65535,65535,65535)
	DrawText 30,522,"Select "
	// pig buttons
	Button pigMovie,pos={30,530},size={65,20},proc=ButtonProc_pigMovie,title="movie"
	Button pigMovie,fColor=(16191,18504,18761)
	Button pigScript,pos={105,530},size={65,20},proc=ButtonProc_pigScript,title="script"
	Button pigScript,fColor=(16191,18504,18761)
	Button pigInterpreter,help={"python script"}
	Button pigInterpreter,pos={180,530},size={65,20},proc=ButtonProc_pigInterpreter,title="python"
	Button pigInterpreter,fColor=(16191,18504,18761)
	Button pigInterpreter,help={"dir of python interpreter (may be conda/venv)"}
	Button pigRun,pos={50,570},size={180,25},proc=ButtonProc_pigRun,title="run"
	Button pigRun,fColor=(16191,18504,18761)
	// ART
	Button Threshold,pos={175,277},size={65,20},proc=ButtonProc_34,title="Thresh"
	Button Threshold,font="Lucida Grande",fStyle=0,fColor=(16191,18504,18761)
	Button Kalman,pos={28,147},size={65,20},proc=ButtonProc_35,title="Kalman"
	Button Kalman,fColor=(16191,18504,18761)
	Button Resize,pos={177,115},size={65,20},proc=ButtonProc_36,title="Resize"
	Button Resize,fColor=(16191,18504,18761)
	Button Noise,pos={37,277},size={65,20},proc=ButtonProc_37,title="Corr Map"
	Button Noise,labelBack=(16191,18504,18761),fColor=(11822,12079,12593)
	Button Corr_ROI,pos={37,301},size={65,20},proc=ButtonProc_38,title="Segment"
	Button Corr_ROI,fColor=(16191,18504,18761)
	Button DelatF,pos={99,390},size={80,20},proc=ButtonProc_40,title="ÆF/F"
	Button DelatF,fColor=(16191,18504,18761)
	Button Check_mask,pos={108,355},size={65,20},proc=ButtonProc_41,title="Check"
	Button Check_mask,fColor=(16191,18504,18761)
	Button Realign,pos={180,354},size={65,20},proc=ButtonProc_42,title="Realign"
	Button Realign,fColor=(16191,18504,18761)
	// f: changed display size to add KS button
	//Button GetROIs,pos={110,301},size={65,20},proc=ButtonProc_1,title="GetROIS"
	Button GetROIs,pos={106,301},size={65,20},proc=ButtonProc_1,title="GetROIS"
	Button GetROIs,fColor=(16191,18504,18761)
	Button Scale,pos={182,42},size={65,20},proc=ButtonProc,title="Scale SI"
	Button Scale,fColor=(16191,18504,18761)
	Button Scrub,pos={37,355},size={65,20},proc=ButtonProc_3,title="Scrub"
	Button Scrub,fColor=(16191,18504,18761)
	// f: just changing display here, to add Ch2st button
	// Button AveM,pos={122,147},size={100,20},proc=ButtonProc_2,title="Ave reps in vid"
	Button AveM,pos={104,147},size={65,20},proc=ButtonProc_2,title="Ave reps"
	Button AveM,fColor=(16191,18504,18761)
	Button Load,pos={29,42},size={65,20},proc=ButtonProc_4,title="Load"
	Button Load,fColor=(16191,18504,18761)
	Button Reg,pos={104,115},size={65,20},proc=ButtonProc_5,title="Register"
	Button Reg,fColor=(16191,18504,18761)
	Button Show,pos={50,229},size={178,20},proc=ButtonProc_6,title="Show"
	Button Show,fColor=(16191,18504,18761)
	// f: button for channel 2 to stimulus
	Button Ch2st,pos={177,147},size={65,20},proc=ButtonProc_43,title="Ch2st"
	Button Ch2st,fColor=(16191,18504,18761)
	// f: button - orginally for KS, empty for now
	Button Uiop,pos={175,301},size={65,20},proc=ButtonProc_44,title=""
	Button Uiop,fColor=(16191,18504,18761)	
	SetVariable FOV,pos={104,43},size={68,19},proc=SetVarProc_1,title="FOV"
	SetVariable FOV,help={"Field of view in µm @ zoom 1"},fSize=12,fStyle=1
	SetVariable FOV,fColor=(65535,65535,65535)
	SetVariable FOV,limits={0,inf,0},value= root:Packages:AROItools:FOVatzoom1
	Button ROIbud,pos={50,421},size={178,20},proc=ROIbuddybutton,title="ROI Buddy"
	Button ROIbud,fColor=(16191,18504,18761)
	Button Regfold,pos={27,115},size={65,20},proc=RegFolder,title="Reg Fold"
	Button Regfold,help={"Register all Ch1 data in a folder"}
	Button Regfold,fColor=(16191,18504,18761)
	Button JoinButton,pos={106,277},size={65,20},proc=JoinButton,title="Join"
	Button JoinButton,labelBack=(16191,18504,18761),fColor=(11822,12079,12593)
EndMacro

Menu "Macros"
	
	"Advanced ROI panel", advancedroi() 

end

// Function RegFolder(ba) : ButtonControl
//	STRUCT WMButtonAction &ba
//
//	switch( ba.eventCode )
//		case 2: // mouse up
//			 loadfoldRaw()
//			break
//		case -1: // control being killed
//			break
//	endswitch
//
//	return 0
// End

// fernando: buttons for pig
// pig1: load movie
function ButtonProc_pigMovie(ba) : ButtonControl
	STRUCT WMButtonAction &ba
	switch( ba.eventCode )
		case 2: // mouse up
		
			pigLoadMovie()
			
			break
		case -1: // control being killed
			break
	endswitch
	return 0
end

// pig2: select python script
function ButtonProc_pigScript(ba) : ButtonControl
	STRUCT WMButtonAction &ba
	switch( ba.eventCode )
		case 2: // mouse up
		
			pigSelectPythonScript()
			
			break
		case -1: // control being killed
			break
	endswitch
	return 0
end

// pig3: select/change python interpreter
function ButtonProc_pigInterpreter(ba) : ButtonControl
	STRUCT WMButtonAction &ba
	switch( ba.eventCode )
		case 2: // mouse up
		
			pigDefinePythonInterpreterPath()
			
			break
		case -1: // control being killed
			break
	endswitch
	return 0
end

// pig4: run pigthon
function ButtonProc_pigRun(ba) : ButtonControl
	STRUCT WMButtonAction &ba
	switch( ba.eventCode )
		case 2: // mouse up
		
			pigRunPythonScriptOnMovie()
			
			break
		case -1: // control being killed
			break
	endswitch
	return 0
end


// f: KS method coded in igor pro (empty for now)
function ButtonProc_44(ba) : ButtonControl
	STRUCT WMButtonAction &ba
	switch( ba.eventCode )
		case 2: // mouse up

			// KS method coded in igor
			
			break
		case -1: // control being killed
			break
	endswitch
	return 0
end

// f: Ch2st from Ch2LineRes
Function ButtonProc_43(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
		
			string list=wavelist("*",";","DIMS:3")
			string name
			prompt name, "choose wave (Ch2 in theory)", popup,list
			doprompt "pick your movie ", name
				if(V_flag==1)
					Abort
				endif	
			wave picwave=$name
			
			waveCh2lineRes(picwave)
			
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End


Function ButtonProc_34(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			ThreshROI()
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End

Function ButtonProc_35(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			Kalman()
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End

Function ButtonProc_36(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			Resize()
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End




Function ButtonProc_40(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			popdf()
			break
		case -1: // control being killed
			break
	endswitch
 
	return 0
End

Function ButtonProc_41(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			//CheckMask()							//Paul removes to compile in Igor7 Jan17
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End

Function ButtonProc_42(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
		//	Realign()								//Paul removes to compile in Igor7 Jan17
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End



Function ButtonProc_37(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			segCorr()
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End

Function ButtonProc_38(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			segment()
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End



Function ButtonProc(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			
			getinfo()
			
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End

Function ButtonProc_1(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			
			string mov, roi
			string list=wavelist("*",";","DIMS:3")
			string listM=wavelist("*ROI*",";","DIMS:2")
			prompt mov, "Movie select", popup, list
			prompt roi, "ROI mask select", popup, listm			
			doprompt "pick your movie and ROI mask ", mov, roi
				if(V_flag==1)
					Abort
				endif	

			wave w=$mov
			wave m=$roi
			
			extractrois(w,m)
			string qa=mov+"_qa"
			roiCor($qa)
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End

Function ButtonProc_3(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			string list=wavelist("*ROI*",";","DIMS:2")
			string roi
			prompt roi, "ROI mask select", popup, list
			doprompt "pick your ROI mask, make sure you have a keep wave! ",  roi
				if(V_flag==1)
					Abort
				endif	
			wave w=$roi
//			scrub(w)									//Paul removes to compile in Igor7 Jan17
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End


Function ButtonProc_2(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
		
			string mov
			variable n=3
			string list=wavelist("*",";","DIMS:3")
			prompt mov, "Movie select", popup, list
			prompt n, "Number of repitions"
			doprompt "pick your movie and number of repititions ", mov, n
				if(V_flag==1)
					Abort
				endif	
			
			wave w=$mov
			 aveREPs(w, n)	
			
			// click code here
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End



Function ButtonProc_4(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			
			string LSIname = LoadScanImage(), Ch1Name,Ch2Name,Ch3Name,Ch4Name
			Variable nChannels, ii
			if (stringmatch(LSIname, "-1"))
				break
			else 
				ApplyHeaderInfo($LSIname)
				nChannels=nChannelsFromHeader($LSIname)
				if(nChannels > 1)
				
					SplitChannels($LSIname,nChannels)
					Ch1Name=LSIName+"_Ch1"
					Ch2Name=LSIName+"_Ch2"
					Ch3Name=LSIName+"_Ch3"	
					Ch4Name=LSIName+"_Ch4"
					getinfo1($Ch1name)
					getinfo1($Ch2name)
					getinfo1($Ch3name)		
					getinfo1($Ch4name)		
				
				
				endif				
			endif
			
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End





Function ButtonProc_5(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			
			string list=wavelist("*",";","DIMS:3")
			string name
			prompt name, "wave to register", popup,list
			doprompt "pick your movie ", name
				if(V_flag==1)
					Abort
				endif	
			wave picwave=$name
			
			RegisterStack(picwave)
			
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End



Function ButtonProc_6(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			imshow()
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End


Function SetVarProc_1(sva) : SetVariableControl
	STRUCT WMSetVariableAction &sva

	switch( sva.eventCode )
		case 1: // mouse up
		case 2: // Enter key
		case 3: // Live update
			Variable dval = sva.dval
			String sval = sva.sval
			
			variable/G root:packages:aroitools:FOVatzoom1=dval
			
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End

getinfo1

Function ButtonProc_7(ba) : ButtonControl	// ave button
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			
			string list=wavelist("*",";","DIMS:3")
			string name
			prompt name, "wave to average", popup,list
			doprompt "pick your movie ", name
				if(V_flag==1)
					Abort
				endif	
			wave picwave=$name
			string outname=name+"AVE"
			
			imagetransform averageimage picwave
			wave M_AveImage, M_StdvImage
			
			duplicate/o M_AveImage, $outname
			
			killwaves/z M_AveImage, M_StdvImage
			
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End



Function ROIbuddybutton(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			
			string list=wavelist("*QA*",";","DIMS:2")
			string name
			prompt name, "Data wave", popup,list
			doprompt "Pick data to examine ", name
				if(V_flag==1)
					Abort
				endif	
			
			wave w=$name
			
			roibuddy(w)
			
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End


Function RegFolder(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			 loadfoldRaw()
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End



Function JoinButton(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			string list=wavelist("*ROI*",";","DIMS:2")
			string name
			variable dist=5
			prompt name, "ROI Mask", popup,list
			prompt dist, "Join ROIs in the concern table that have a distance less than"
			doprompt "Join ROIs", name, dist
				if(V_flag==1)
					Abort
				endif	
			
			wave w=$name
			
//			join(w,dist)						//Paul removes to compile in Igor7 Jan17
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End