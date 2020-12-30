import copyExif as cE
import argparse

def main(args):
    eM=cE.ExifMatcher(args.source,args.target,timeZone=args.timezone)
    eM.matchNext(True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--source", help="Source path with gpx data",default="/data/source")
    parser.add_argument("-t","--target",help="Target folder with images to be changed",default="/data/target")
    parser.add_argument("-tz","--timezone",type=int,help="Timezone",default="2")
    args = parser.parse_args()
    main(args)