import numpy as np
import argparse
import yaml
from astropy import units as u


if __name__ == '__main__':
    usage = "usage: %(prog)s"
    description = "read in new data from text file and add to existing data"
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument('--file', help="file containing new data")
    parser.add_argument('--alldata', help="file containing all data points",
                        default = 'data/limits_data.yaml')
    parser.add_argument('--plotstyles', help="file lists of plotstyles",
                        default = 'config/plotstyles.yaml')
    parser.add_argument('--plotstyle', help="plot style for new data",
                        choices = ['fill', 'fill_between', 'plot'])
    parser.add_argument('--sens', help="is this a sensitivity of a future measurement (yes/no)?",
                        choices = ['yes', 'no'])
    parser.add_argument('--hint', help="is this a detection / hint of a detection (yes/no)?",
                        choices = ['yes', 'no'])
    parser.add_argument('--cosmo', help="Do these constraints come from cosmological (yes/no)?",
                        choices = ['yes', 'no'])
    parser.add_argument('--output', help="name of output file with all limits")
    parser.add_argument('--munit', help="unit of ALP mass in file")
    parser.add_argument('--gunit', help="unit of photon-ALP coupling in file")
    parser.add_argument('--label', help="label to be shown in plot")
    parser.add_argument('--name', help="identifier for new data")
    parser.add_argument('--rotation', help="rotation angle of label in plot")
    parser.add_argument('--textcolor', help="text color of label in plot")
    parser.add_argument('--xylabel', help="xy coordinates of label in plot")
    parser.add_argument('--z', help="z order of limits in plot", type = float)
    args = parser.parse_args()

    if args.file is None:
        args.file = input("Enter text file with new data points\n")
    d = np.loadtxt(args.file).T
    del args.file

    if args.alldata is None:
        args.alldata = input("Enter yaml file with all old data points\n")
    print ("reading old data from {0:s}".format(args.alldata))
    with open(args.alldata) as f:
        alldata = yaml.load(f)
    del args.alldata

    if args.name is None:
        args.name = input("Enter name of new data\n")
    name = args.name
    del args.name

    if args.plotstyles is None:
        args.plotstyles = input("Enter yaml file with plot style lists\n")
    print ("reading old plot styles from {0:s}".format(args.plotstyles))
    with open(args.plotstyles) as f:
        plotstyles = yaml.load(f)

    if args.plotstyle is None:
        args.plotstyle = input("What plot style do you want for your data (fill/fill_between/plot)?\n")
    plotstyle = args.plotstyle
    del args.plotstyle
    if not (plotstyle == 'fill' or plotstyle == 'fill_between' or plotstyle == 'plot'):
        raise ValueError("plot style must be either 'fill', 'fill_between' or 'plot' ")
    plotstyles[plotstyle].append(name)

    if args.munit is None:
        args.munit = input("Enter unit of ALP masses in file\n")
    munit = u.Unit(args.munit)
    del args.munit

    if args.gunit is None:
        args.gunit = input("Enter unit of photon-ALP coupling in file\n")
    gunit = u.Unit(args.gunit)
    del args.gunit

    if args.sens is None:
        args.sens = input("Is this a sensitivity of a future measurement (yes/no)?\n")
    sens = False if args.sens.lower() == "no" else True
    del args.sens
    if sens:
        plotstyles['sens'].append(name)

    if args.hint is None:
        args.hint = input("Is this a detection / hint for a detection (yes/no)?\n")
    hint = False if args.hint.lower() == "no" else True
    del args.hint
    if hint:
        plotstyles['hint'].append(name)

    if args.cosmo is None:
        args.cosmo = input("Do these constraints come from cosmological probes (yes/no)?\n")
    cosmo = False if args.cosmo.lower() == "no" else True
    del args.cosmo
    if cosmo:
        plotstyles['cosmo'].append(name)

# update plot styles
    with open(args.plotstyles, "w") as f:
        yaml.dump(plotstyles, f)
    del args.plotstyles

    if args.label is None:
        args.label = input("Enter label of new data to be displayed in plot\n")

    if args.textcolor is None:
        args.textcolor = input("Enter text color of the label\n")

    if args.rotation is None:
        args.rotation = float(input("Enter rotation of label in plot in degrees\n"))

    if args.xylabel is None:
        args.xylabel= input("Enter the coordinates of the label in the plot in" \
                   " ALP mass and coupling separated by a comma \n")
    args.xylabel = [float(r) for r in args.xylabel.split(",")]


    if args.z is None:
        args.z = float(input("Enter z order for new data in plot\n"))

    if args.output is None:
        args.output = input("Enter new yaml output file name\n")
    output = args.output
    del args.output

    args.log_m = np.log10(d[0] * munit.to('eV'))
    args.log_g = np.log10(d[1] * gunit.to('GeV^-1'))

    alldata.update({name: vars(args)})

    with open(output, "w") as f:
        yaml.dump(alldata, f)
    print ("Written all data including new data to {0:s}".format(output))
