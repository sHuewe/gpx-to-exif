import copyExif as cE
import argparse
import os

def main(args):
    timezone=args.timezone
    if not timezone:
        timezone=float(os.environ.get("timezone",None))
    default=args.default
    if not default:
        default=os.environ.get("default",None)
    eM=cE.ExifMatcher(args.source,args.target,timeZone=timezone,defaultLocation=default)
    eM.matchNext(True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--source", help="Source path with gpx data",default="/data/source")
    parser.add_argument("-t","--target",help="Target folder with images to be changed",default="/data/target")
    parser.add_argument("-tz","--timezone",type=int,help="Timezone",default=None)
    parser.add_argument("-d","--default", help="Default location to be set if no data match. Location has to be defined in default-locations.json",default=None)
    args = parser.parse_args()
    main(args)