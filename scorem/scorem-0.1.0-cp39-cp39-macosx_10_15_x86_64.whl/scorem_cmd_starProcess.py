#!/usr/local/bin/python3.9

import argparse
import os.path
from scorem import starHandler
from scorem import starDisplay

scorem_parser = argparse.ArgumentParser(
    prog="scorem_starProcess",
    usage="%(prog)s [command] [arguments]",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
#scorem_parser.add_argument("section", type=str,  help='choose between starProcess, assess')
#scorem_parser.add_argument("command", type=str)

#scorem_program = scorem_parser.add_subparsers(dest="section")
command = scorem_parser.add_subparsers(dest="command")



STAR_deleteTags = command.add_parser (
    "deleteTags", description="Cleans StarTags", help='delete tags with a certain prefix'
)
STAR_deleteTags.add_argument("--i", required=True, type=str, help="input file for deleting tags")
STAR_deleteTags.add_argument("--o", required=False, default=None,  type=str, help="output file with deleted tags file")
STAR_deleteTags.add_argument("--prefix", required=False, default='_scorem_', type=str, help="prefix for the tag to remove")
def cleanTags(args):
    inputFile=args.i
    outputFile=args.o
    tagPrefix=args.prefix
    if (outputFile==None):
        outputFile=inputFile
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
        exit(0)
    starHandler.removeColumnsTagsStartingWith(inputFile, outputFile, tagPrefix)




STAR_exportTags = command.add_parser (
    "exportTags", description="export StarTags", help='export tags from input'
)
STAR_exportTags.add_argument("--i", required=True, type=str, help="input file for updating tags")
STAR_exportTags.add_argument("--tagsFile", required=True, type=str, help="input file with tags to export")
STAR_exportTags.add_argument("--tags", required=True, type=str, help="comma separated tags to export")
STAR_exportTags.add_argument("--o", required=False, default=None,  type=str, help="output file")
def exportTags(args):
    inputFile=args.i
    tagsFile=args.tagsFile
    tags=str(args.tags).split(',')
    outputFile=args.o
    if (outputFile==None):
        outputFile=inputFile
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
        exit(0)
    columnToAddContent=starHandler.readColumns(tagsFile, tags)
    starHandler.addDataframeColumns(inputFile, outputFile, tags, columnToAddContent)



STAR_multiplyTags = command.add_parser (
    "multiplyTags", description="multiply StarTags", help='multiply StarTags each others'
)
STAR_multiplyTags.add_argument("--i", required=True, type=str, help="input file for updating tags")
STAR_multiplyTags.add_argument("--outTag", required=True, type=str, help="name of the output tag")
STAR_multiplyTags.add_argument("--tags", required=True, type=str, help="comma separated tags to multiply")
STAR_multiplyTags.add_argument("--o", required=False, default=None,  type=str, help="output file")
def multiplyTags(args):
    inputFile=args.i
    outTag=args.outTag
    tags=str(args.tags).split(',')
    outputFile=args.o
    if (outputFile==None):
        outputFile=inputFile
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
        exit(0)
    #print ("out_tags=",tags)
    columnsToMultiply=starHandler.readColumns(inputFile, tags)
    columnsToMultiply[outTag]=columnsToMultiply[tags[0]]
    for ii in range (1,len(tags)):
        columnsToMultiply[outTag]= columnsToMultiply[outTag]*columnsToMultiply[tags[ii]]
    starHandler.addDataframeColumns(inputFile, outputFile, [outTag], columnsToMultiply[[outTag]])




STAR_selectWorst = command.add_parser (
    "selectWorst", description="selectWorst", help='select worst scoring particles'
)
STAR_selectWorst.add_argument("--i", required=True, type=str, help="input file")
STAR_selectWorst.add_argument("--num", required=True, type=str, help="number of particles to select")
STAR_selectWorst.add_argument("--tag", required=True, type=str, help="tag to select worst")
STAR_selectWorst.add_argument("--o", required=False, default=None,  type=str, help="output file")
def selectWorst(args):
    inputFile=args.i
    tag=str(args.tag)
    outputFile=args.o
    if (outputFile==None):
        outputFile=inputFile
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
        exit(0)
    starHandler.extractWorst(inputFile, outputFile, int(args.num), tag)



STAR_selectBest = command.add_parser (
    "selectBest", description="selectBest", help='select best particles'
)
STAR_selectBest.add_argument("--i", required=True, type=str, help="input file")
STAR_selectBest.add_argument("--num", required=True, type=str, help="number of particles to select")
STAR_selectBest.add_argument("--tag", required=True, type=str, help="tag to select best")
STAR_selectBest.add_argument("--o", required=False, default=None,  type=str, help="output file")
def selectBest(args):
    inputFile=args.i
    tag=str(args.tag)
    outputFile=args.o
    if (outputFile==None):
        outputFile=inputFile
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
        exit(0)
    starHandler.extractBest(inputFile, outputFile, int(args.num), tag)



STAR_thresholdTagValue = command.add_parser (
    "thresholdTagValue", description="thresholdTagValue", help='threshold Tag less than a certain value'
)
STAR_thresholdTagValue.add_argument("--i", required=True, type=str, help="input file for updating tags")
STAR_thresholdTagValue.add_argument("--tag", required=True, type=str, help="comma separated tags to multiply")
STAR_thresholdTagValue.add_argument("--tagOut", required=False, default=None, type=str, help="threshold if less then a certain value")
STAR_thresholdTagValue.add_argument("--threshold", required=False, default=0, type=float, help="threshold value")
STAR_thresholdTagValue.add_argument("--o", required=False, default=None,  type=str, help="output file")
def thresholdTagValue(args):
    #inputFile=args.i
    tagOut=args.tagOut
    outputFile=args.o
    tag=args.tag
    if (outputFile==None):
        outputFile=args.i
    if (tagOut==None):
        tagOut=args.tag
    if (not os.path.isfile(args.i)):
        print('ERROR: file \"',args.i,'\" not existing')
        exit(0)
    #print ('threshold=',args.threshold)
    print ("args.i=",args.i)
    print ("tag=",tag)
    columnsToThreshold=starHandler.readColumns(args.i, [tag] )
    #columnsToThreshold[columnsToThreshold < args.threshold] = args.threshold
    #columnsToThreshold[columnsToThreshold < args.threshold] = 0
    columnsToThreshold[columnsToThreshold[tag] < 0.0] = 0.0

    #print (columnsToThreshold.head)


    #columnsToThreshold = columnsToThreshold.clip_upper(args.threshold)
    starHandler.addDataframeColumns(args.i, outputFile, [tagOut], columnsToThreshold )


###################
##  DISPLAY
STAR_eulerHist = command.add_parser (
    "eulerHist", description="thresholdTagValue", help='threshold Tag less than a certain value'
)
STAR_eulerHist.add_argument("--i", required=True, type=str, help="input star file")
STAR_eulerHist.add_argument("--title", required=False, default="phi/theta histogram", type=str, help="Title of the plot")
STAR_eulerHist.add_argument("--maxValue", required=False, default=None, type=str, help="maximum value to display")
STAR_eulerHist.add_argument("--numBins", required=False, default=40, type=float, help="Number of bins for the histogram")
STAR_eulerHist.add_argument("--outImage", required=False, default=None,  type=str, help="output file where storing image")
STAR_eulerHist.add_argument("--show", required=False, default=True,  type=bool, help="whether or not display the image (e.g. set to False if you are saving the plot and don't want to show it on the screen)")
def eulerHist(args):
    if (not os.path.isfile(args.i)):
        print('ERROR: file \"',args.i,'\" not existing')
        exit(0)
    Phi=starHandler.readColumns(args.i, ['_rlnAngleRot'] )
    Theta=starHandler.readColumns(args.i, ['_rlnAngleTilt'] )
    starDisplay.plotEulerHist(Phi, Theta, args.title, args.maxValue, args.numBins, args.outImage, args.show)




#################
#################
###  MAIN
################
def main(command_line=None):
    #f = open("scorEM.txt", "w")
    #f.write("scorEM session recorded at %s.\n\n" % (datetime.datetime.now()))
    args = scorem_parser.parse_args(command_line)
    if args.command == "deleteTags":
        cleanTags(args)
    elif args.command == "exportTags":
        exportTags(args)
    elif args.command == "multiplyTags":
        multiplyTags(args)
    elif args.command == "selectBest":   
        selectBest(args) 
    elif args.command == "selectWorst":   
        selectWorst(args) 
    elif args.command == "thresholdTagValue":   
        thresholdTagValue(args) 
    elif args.command == "eulerHist":   
        eulerHist(args) 
    else:
        scorem_parser.print_help()


if __name__ == "__main__":
    main()
