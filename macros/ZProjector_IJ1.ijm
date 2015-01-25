setBatchMode(true);
run("Bio-Formats Macro Extensions");

input = getArgument();

if(input == ""){
    print("Please specify a folder as argument.");
    eval("script", "System.exit(0);");
}

input = input + "/";

suffix = "Pos0.ome.tif";

function processFolder(input) {
    list = getFileList(input);
    for (i = 0; i < list.length; i++) {
        if(endsWith(list[i], "/"))
            processFolder(input + list[i]);
        if(endsWith(list[i], suffix) && !startsWith(list[i], "MAX_"))
            processFile(input, list[i]);
    }
}

function processFile(input, file) {
    print("Processing: " + input + file);
    open(input + file);
    run("Z Project...", "projection=[Max Intensity] all");
    run("Bio-Formats Exporter", "save=" + input + "MAX_" + file + " compression=Uncompressed");
    close();
}

processFolder(input);
print("Done");
eval("script", "System.exit(0);");
