setBatchMode(true);
run("Bio-Formats Macro Extensions");

suffix = "Pos0.ome.tif";
prefix = "MAX_";

Dialog.create("Batch z-project");
Dialog.addString("Suffix : ", suffix);
Dialog.addString("Prefix : ", prefix);
Dialog.addCheckbox("Use bioformats for saving", false);
Dialog.addMessage("Now click OK to choose a directory.");
Dialog.show();
suffix = Dialog.getString();
prefix = Dialog.getString();
use_bioformats = Dialog.getCheckbox(); 

input = getDirectory("Choose a directory");

input = input + "/";

function processFolder(input) {
    list = getFileList(input);
    for (i = 0; i < list.length; i++) {
        if(endsWith(list[i], "/"))
            processFolder(input + list[i]);
        if(endsWith(list[i], suffix) && !startsWith(list[i], prefix))
            processFile(input, list[i]);
    }
}

function processFile(input, file) {
    print("Processing: " + input + file);
    open(input + file);
    run("Z Project...", "projection=[Max Intensity] all");
    if (use_bioformats) {
        run("Bio-Formats Exporter", "save=" + input + prefix + file + " write_each_channel compression=Uncompressed");
    }
    else{
        run("Save", "save=" + input + prefix + file);
    }
    
    while (nImages>0) {
        selectImage(nImages);
        close();
    }
}

processFolder(input);
print("Done");