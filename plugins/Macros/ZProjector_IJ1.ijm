setBatchMode(true);
run("Bio-Formats Macro Extensions");

suffix = "Pos0.ome.tif";
prefix = "MAX_";

Dialog.create("Batch z-project");
Dialog.addString("Suffix : ", suffix);
Dialog.addString("Prefix : ", prefix);
Dialog.addMessage("Now click OK to choose a directory.");
Dialog.show();
suffix = Dialog.getString();
prefix = Dialog.getString();

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
    run("Bio-Formats Exporter", "save=" + input + prefix + file + " compression=Uncompressed");

    while (nImages>0) {
        selectImage(nImages);
        close();
    }
}

processFolder(input);
print("Done");
