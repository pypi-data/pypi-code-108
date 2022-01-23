#!/usr/local/bin/python3.9

import argparse
import os.path
from scorem import starHandler
from scorem import assessParticles
from scorem import utils
import scorem_core
import numpy as np

scorem_parser = argparse.ArgumentParser(
    prog="scorem",
    usage="%(prog)s [command] [arguments]",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

command = scorem_parser.add_subparsers(dest="command")



scorem_normalizeScore = command.add_parser (
    "normalizeScore", description="Normalize Score in star file tag", help='normalize score'
)
scorem_normalizeScore.add_argument("--i", required=True, type=str, help="input star file to normalize")
scorem_normalizeScore.add_argument("--o", required=False,  type=str, help="output star file with deleted tags file")
scorem_normalizeScore.add_argument("--tag", required=True,  type=str, help="tag score to normalize")
scorem_normalizeScore.add_argument("--tagOut", required=True,  type=str, help="output tag with normalized score")
scorem_normalizeScore.add_argument("--numViews", required=False, default=50,  type=str, help="number of view for normalization")
def normalizeScore(args):
    inputFile=args.i
    outputFile=args.o
    numViews=args.numViews
    #tagPrefix=args.prefix
    if (outputFile==None):
        outputFile=inputFile
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
    #starHandler.removeColumnsTagsStartingWith(inputFile, outputFile, tagPrefix)
    #print ('inputFile=',inputFile)
    #print ('args.tag=',args.tag)
    coordinates = starHandler.readColumns(inputFile, ['_rlnAngleRot','_rlnAngleTilt','_rlnRandomSubset',args.tag])

    phiListParticle = coordinates['_rlnAngleRot'].tolist()
    thetaListParticle = coordinates['_rlnAngleTilt'].tolist()
    scores = coordinates[args.tag].tolist()
    randomSubset = coordinates['_rlnRandomSubset'].tolist()
    rankedParticles=scorem_core.EqualizedParticlesRank(phiListParticle,thetaListParticle,scores,randomSubset,int(numViews))
    starHandler.addColumns(inputFile, outputFile, [args.tagOut], [rankedParticles])



scorem_scoreParticles = command.add_parser (
    "scoreParticles", description="score Particles", help='score Particles described in star file'
)
scorem_scoreParticles.add_argument("--i", required=True, type=str, help="input star file with particles to score")
scorem_scoreParticles.add_argument("--mask", required=True, type=str, help="mrc volumetric file with mask")
scorem_scoreParticles.add_argument("--map", required=True, type=str, help="mrc volumetric file with reference map")
scorem_scoreParticles.add_argument("--o", required=False, default=None,  type=str, help="output file with scores")
scorem_scoreParticles.add_argument("--tags", required=False, default='CC,SSIM,PSNR,SSIM_blur_1,SSIM_blur_2,MI_blur_1,MI_blur_2,CC_firstDerivativeX_1,CC_firstDerivativeY_1,CC_secondDerivativeX_1,CC_secondDerivativeY_1',  type=str, help="tags to score (csv)")
def scoreParticles(args):
    inputFile=args.i
    outputFile=args.o
    mask=args.mask
    map=args.map
    #tagPrefix=args.prefix
    if (outputFile==None):
        outputFile=inputFile
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
    tags=str(args.tags).split(',')
    for ii in range(0,len(tags)):
        tags[ii]="_scorem_"+tags[ii]
    #print (tags)
    assessParticles.ParticleVsReprojectionScores(inputFile, outputFile, map, mask, listScoresTags = tags)
    #starHandler.removeColumnsTagsStartingWith(inputFile, outputFile, tagPrefix)
    #print ('inputFile=',inputFile)
    #print ('args.tag=',args.tag)
    #coordinates = starHandler.readColumns(inputFile, ['_rlnAngleRot','_rlnAngleTilt','_rlnRandomSubset',args.tag])
    #phiListParticle = coordinates['_rlnAngleRot'].tolist()
    #thetaListParticle = coordinates['_rlnAngleTilt'].tolist()
    #scores = coordinates[args.tag].tolist()
    #randomSubset = coordinates['_rlnRandomSubset'].tolist()
    #rankedParticles=scorem_core.EqualizedParticlesRank(phiListParticle,thetaListParticle,scores,randomSubset,int(numViews))
    #starHandler.addColumns(inputFile, outputFile, [args.tagOut], rankedParticles)



scorem_createCtfStack = command.add_parser (
    "createCtfStack", description="create CTF Stack", help='create CTF stack'
)
scorem_createCtfStack.add_argument("--i", required=True, type=str, help="input star file with particles to score")
scorem_createCtfStack.add_argument("--o", required=False, default=None,  type=str, help="output stack basename")
def createCtfStack(args):
    inputFile=args.i
    #tagPrefix=args.prefix
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
    utils.ctfStack(inputFile, args.o)


scorem_maskedMapContrast = command.add_parser (
    "maskedMapContrast", description="create Map Contrast", help='Masked Map Contrast Calculator'
)
scorem_maskedMapContrast.add_argument("--i", required=True, type=str, help="input map")
scorem_maskedMapContrast.add_argument("--mask", required=False, default=None,  type=str, help="mask")
def maskedMapContrast(args):
    inputFile=args.i
    #tagPrefix=args.prefix
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
    if (not os.path.isfile(args.mask)):
        print('ERROR: file \"',args.mask,'\" not existing')

    sizeMap=scorem_core.sizeMRC(inputFile)
    sizeMask=scorem_core.sizeMRC(args.mask)
    if not sizeMap == sizeMask:
        print ("ERROR: mask and map not of the same size")
        exit(1)
    inputMap=scorem_core.ReadMRC(inputFile)
    inputMask=scorem_core.ReadMRC(args.mask)
    minVal,maxVal=scorem_core.maskedMapContrast(inputMap,inputMask,sizeMap[0],sizeMap[1],sizeMap[2])
    print ('values=',minVal,',',maxVal)


scorem_createMask = command.add_parser (
    "createMask", description="create Masked Map", help='create Masked Map'
)
scorem_createMask.add_argument("--i", required=True, type=str, help="input map")
scorem_createMask.add_argument("--maskIn", required=False, default=None,  type=str, help="mask input")
scorem_createMask.add_argument("--maskOut", required=True, type=str, help="mask output")
def createMask(args):
    inputFile=args.i
    #tagPrefix=args.prefix
    if (not os.path.isfile(inputFile)):
        print('ERROR: file \"',inputFile,'\" not existing')
        exit(1)
    sizeMap=scorem_core.sizeMRC(inputFile)
    

    if args.maskIn==None:
        M=np.ones( (sizeMap[0],sizeMap[1],sizeMap[2]) )
    elif (not os.path.isfile(args.maskIn)):
        print('ERROR: file \"',inputFile,'\" not existing')
        exit(1)
    else:
        sizeMask=scorem_core.sizeMRC(args.maskIn)
        if not sizeMask==sizeMap:
            print('ERROR: map and mask of different sizes')
            exit(1)
        M=scorem_core.ReadMRC(args.maskIn)
    I=scorem_core.ReadMRC(inputFile)
    T=scorem_core.AutomaticThresholdMap(I,M,sizeMap[0],sizeMap[1],sizeMap[2])
    scorem_core.WriteMRC(T, args.maskOut ,sizeMap[0],sizeMap[1],sizeMap[2],1)
    scorem_core.replaceMrcHeader(inputFile,args.maskOut)



def main(command_line=None):
    args = scorem_parser.parse_args(command_line)
    if args.command == "normalizeScore":
        normalizeScore(args)
    elif args.command == "scoreParticles":
        scoreParticles(args)
    elif args.command == "createCtfStack":
        createCtfStack(args)
    elif args.command == "maskedMapContrast":
        maskedMapContrast(args)
    elif args.command == "createMask":
        createMask(args)
    else:
        scorem_parser.print_help()

if __name__ == "__main__":
    main()
