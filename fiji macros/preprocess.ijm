

// this uses StackReg for registration 
// so the BIG-EPFL is needed (help -> update...)

// default starting dir
default_dir = "C:/Users/Fernando/zf/data";
// set starting dir
if (File.exists(default_dir)) {
	File.setDefaultDir(default_dir);
} else {
	print("default dir doesn't exist, using C:/Users/");
	File.setDefaultDir("C:/Users/");
}

// check if there's an open file already
if (nImages() == 0) {
	// choose tiff file
	path = File.openDialog("Choose an image");
	// check open
	if (path == "") exit("No file selected");
	open(path);
} else {
	// already open image 
	if (nImages() > 1) {
    	print("more than 1 image open: " + nImages());
	}
}

// print some stuff
print("");
selectImage(getTitle());
print("image: " + getTitle());
cwd = getDirectory("image");
print("cwd: " + cwd);

// get name for later
original_stack = getTitle();

// check for de-interleave
width = 0;
height = 0;
channels = 0; 
slices = 0;
frames = 0;

getDimensions(width,height,channels,slices,frames);

print(" ");
print("start -->");
print("title: " + original_stack);
print("width: " + width);
print("height: " + height);
print("channels: " + channels);
print("slices:" + slices);
print("frames:" + frames);

// de-interleave, if necessary
if (channels > 1) {
    run("Split Channels");
} else {
	// this doesn't duplicate
    run("Deinterleave", "how=2");
}

// close stimulus (discard)
// always comes first, but TODO something serious
selectImage(getTitle());
close();

// de-interneaved stack
deint_stack = getTitle();
getDimensions(width,height,channels,slices,frames);

print(" ");
print("de-interleaved title: " + deint_stack);
print("width: " + width);
print("height: " + height);
print("channels: " + channels);
print("slices:" + slices);
print("frames:" + frames);

// convert to 32 bits
run("32-bit");

// pad (to avoid missalignment) & register
run("Canvas Size...", "width+=200 height+=200 position=Center");
run("StackReg ", "transformation=[Rigid Body]");


// name for saving
// cwd = getDirectory("current");
dot_index = lastIndexOf(deint_stack, ".");
base_name = substring(deint_stack, 0, dot_index);
save_name = cwd + base_name;

// Save as TIFF
fname = save_name + "_pp.tiff";
if (File.exists(fname)) {
    print("");
    print("tiff file already exists at: " + fname);
} else {
	// seemingly save creates a new instance 
	// and flushes the prev. one
	saveAs("Tiff", fname);
	print("");
	print("saved tiff at: " + fname);
	// quick check, just in case 
	if (nImages() > 1) {
		close();
	}
	// rename to match the rest of the code
	// not cleaning this now
	rename(deint_stack);
	// print(getTitle());
}

// enlarge (zoom)
selectWindow(deint_stack);
run("Set... ", "zoom=600");
print("");
print("zoom to 600%");
print("");

// get rid of the log 
if (isOpen("Log")) {
	print("");
	print("bye bye");
	print("");
	selectWindow("Log");
	run("Close");
}

exit();










