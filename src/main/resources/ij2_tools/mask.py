import os


def apply_mask(ij, data, mask, save=False, output_dir=""):

    output = ij.dataset().create(data)

    targetCursor = output.localizingCursor()
    dataRA = data.randomAccess()
    maskRA = mask.randomAccess()

    while targetCursor.hasNext():
        targetCursor.fwd()
        dataRA.setPosition(targetCursor)
        maskRA.setPosition(targetCursor)

        if maskRA.get().get() == 0:
            targetCursor.get().set(0)
        else:
            targetCursor.get().set(dataRA.get())

    # Set the correct axes
    axes = [data.axis(d) for d in range(0, data.numDimensions())]
    output.setAxes(axes)

    if save:
        fname = os.path.join(output_dir, "Masked.tif")
        ij.log().info("Saving at %s" % fname)
        output.setSource(fname)
        ij.io().save(output, fname)

    return output
