macro "AutoInstall" {
    // run all the .ijm scripts provided in macros/AutoInstall/
    autoInstallDirectory = getDirectory("imagej") + "/macros/AutoInstall/";
    if (File.isDirectory(autoInstallDirectory)) {
        list = getFileList(autoInstallDirectory);
        // make sure startup order is consistent
        Array.sort(list);
        for (i = 0; i < list.length; i++) {
            if (endsWith(list[i], ".ijm")) {
                run("Install...", "install=" + autoInstallDirectory + list[i]);
            }
        }
    }
}
