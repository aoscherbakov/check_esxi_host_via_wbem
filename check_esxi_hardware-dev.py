import pywbem
import argparse

argparser = argparse.ArgumentParser(description="Check ESXi CIM Classes")
argparser.add_argument("--host", help="ESXi host to check",required=True)
argparser.add_argument("--hw", help="what hardware to check", choices=['raid','power','temp'],required=True)
argparser.add_argument("--model", help="print server model", action='store_true')

args = argparser.parse_args()

print "your host: {}".format(args.host)
print "your hardware to check: {}".format(args.hw)
