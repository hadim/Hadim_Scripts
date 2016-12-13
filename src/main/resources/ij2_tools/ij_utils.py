from net.imagej.axis import Axes
from net.imagej.ops import Ops


def print_info(data):
    print("X : %s" % data.dimension(data.dimensionIndex(Axes.X)))
    print("Y : %s" % data.dimension(data.dimensionIndex(Axes.Y)))
    print("Z : %s" % data.dimension(data.dimensionIndex(Axes.Z)))
    print("TIME : %s" % data.dimension(data.dimensionIndex(Axes.TIME)))
    print("CHANNEL : %s" % data.dimension(data.dimensionIndex(Axes.CHANNEL)))



def get_axis(axis_type):
    return {
        'X': Axes.X,
        'Y': Axes.Y,
        'Z': Axes.Z,
        'TIME': Axes.TIME,
        'CHANNEL': Axes.CHANNEL,
    }.get(axis_type, Axes.Z)


def get_projection_method(method):
    return {
        'Max': Ops.Stats.Max,
        'Mean': Ops.Stats.Mean,
        'Median': Ops.Stats.Median,
        'Min': Ops.Stats.Min,
        'StdDev': Ops.Stats.StdDev,
        'Sum': Ops.Stats.Sum,
    }.get(method, Ops.Stats.Max)