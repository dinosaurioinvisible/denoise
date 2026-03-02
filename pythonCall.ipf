#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.

// this just executes a python script from the terminal
Function RunPythonScriptOnMovie(string path_to_python_script, string path_to_movie)
	ExecuteScriptText/B "python "+path_to_python_script+" "+path_to_movie
End

print GetWavesDataFolder(steps_pre_AF10_a1001, 0)


// modification of load movie()
Function LoadAndGetMovieInfo()

String ImgWaveName, FirstWave, FileName, FNTrunc, FNNum, FNPath, StrNum
	string  header, s_info = "No header info available\r"
	Variable PointPos, startnum, cont = 1, newframes,currentframes, frames
	
	ImageLoad /Q /O /C=-1
	
	if (v_flag == 0)
		return "-1"
	endif
	
		header = s_info
		PointPos = strsearch(S_Filename, ".tif", 0)
		ImgWaveName = S_FileName[0,PointPos-1]
		FileName = S_FileName[0,PointPos-1]
		ImgWaveName = ReplaceString("-", ImgWaveName, "_")
		PointPos = strsearch(S_Wavenames, ";", 0)
		FirstWave =S_Wavenames[0,PointPos-1]
		FNPath = S_Path
	
		FNTrunc = FileName[0,strlen(FileName)-4]
		
	if (waveexists(:tw0))
		killwaves /z tw0
	endif
		
	duplicate /o/free $FirstWave, TempImage
	killwaves /z  $FirstWave
	
	variable refnum
	
	string fn2
	
	Do
		startnum +=1
		currentframes=dimsize(TempImage,2)
		
		if (startnum < 10)
			FNNum = "00"+Num2Str(startnum)
		elseif (startnum < 100)
			FNNum = "0"+Num2Str(startnum)
		else
			FNNum = Num2Str(startnum)
		endif
			
		FileName = 	FnPath+FNTrunc+FNNum+".tif"
		fn2 = 	FnPath+FNTrunc+FNNum
		open /z=1 /r  refnum as FileName
		
		if (v_flag==0)
			ImageLoad /c=-1 /n=tw /o /q FileName
			
			
			PointPos = strsearch(S_Wavenames, ";", 0)
			FirstWave =S_Wavenames[0,PointPos-1]
			Wave sec = $firstwave
			
			
			frames=dimsize(sec,2)
			if(frames==0)
				frames = 1
			endif
			
			newframes=currentframes+frames
			
			redimension/n=(-1,-1,newframes) TempImage
			
			TempImage[][][currentframes,newframes-1] = sec[p][q][r-currentframes]
			
									
			close refnum
			killwaves $firstwave
		else
			cont = 0
		endif
		
		
	While(cont)
	
	
	if (waveexists($ImgWaveName))
		killwaves /z $ImgWaveName
	endif
	
	
	duplicate /o TempImage, $ImgWaveName
	Killwaves /z $FirstWave, TempImage
	
	redimension /s $ImgWaveName		//convert to single precision floating point
	
	
	Note $ImgWaveName, header
	Note $ImgWaveName, "file.path="+s_path
	Note $ImgWaveName, "file.name="+s_filename
	
	Print "Saved as "+ ImgWaveName
	
	Return ImgWaveName
End

