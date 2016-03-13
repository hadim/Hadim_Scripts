macro "Save ROI [s]"{
    dir = getDirectory("image");

    name = getTitle;
    index = lastIndexOf(name, ".");
    if (index!=-1){
        name = substring(name, 0, index);
    }
    name = name + ".zip";
    path = dir + name;

    roiManager("deselect");
    roiManager("Save", path);
    roiManager("Delete");
}

macro "Enhance contrast [c]"{
    run("Enhance Contrast", "saturated=0.35");
}

macro "Run TrackMate [k]"{
    run("TrackMate");
}

macro "Make Z projection [z]"{
    run("Z Project...", "projection=[Max Intensity] all");
}

macro "Synchronize Windows [w]"{
    run("Synchronize Windows");
}

macro "ROI Manager [r]"{
    run("ROI Manager...");
}
