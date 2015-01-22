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

macro "Get OME String [m]"{
    run("Get OME String");
}

macro "Crop Multi Roi [p]"{
    run("Crop Multi Roi");
}

macro "ROI Manager [r]"{
    run("ROI Manager...");
}

macro "Build Kymograph [y]"{

    if (selectionType!=5)
        exit("Straight line selection required");

    input_id = getImageID;
    input_title = getTitle();

    getPixelSize(unit, width, height, depth);
    getDimensions(width, height, channels, slices, frames);
    getLine(x1, y1, x2, y2, lineWidth);

    dx = x1 - x2;
    dy = y1 - y2;
    dist = sqrt(dx * dx + dy * dy);
    dx /= dist;
    dy /= dist;

    for (i=0; i < lineWidth - 1; i++){
        showProgress(i + 1, lineWidth);
        n = i - lineWidth / 2;
        new_x1 = x1 + n * dy;
        new_y1 = y1 - n * dx;
        new_x2 = x2 + n * dy;
        new_y2 = y2 - n * dx;
        makeLine(new_x1, new_y1, new_x2, new_y2);
        run("Reslice [/]...", "output=1.000 slice_count=1 rotate avoid");
        selectImage(input_title);
    }
    makeLine(x1, y1, x2, y2);

    run("Images to Stack", "name=Stack title=[] use");
    stack_id = getImageID;
    getDimensions(width, height, channels, slices, frames);
    run("Z Project...", "start=1 stop=" + slices + " projection=[Max Intensity]");

    selectImage(stack_id);
    close();
}
