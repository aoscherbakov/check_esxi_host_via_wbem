#!/usr/bin/python
#####################################
## Written by Shcherbakov A.O.     ##
##                                 ##
## Check ESXi host hardware status ##
## v.0.1                           ##
##                                 ##
## pywbem v.8.0 requied            ##
##                                 ##
#####################################

import pywbem
import argparse

#user='root'
#password='kirgudu_1234'

def parse_arguments():
    argparser = argparse.ArgumentParser(description="Check ESXi CIM Classes")
    argparser.add_argument("--host", help="ESXi host to check",required=True)
    argparser.add_argument("--hw", help="what hardware to check", choices=['raid','power','temp'],required=True)
    argparser.add_argument("--model","-m", help="print server model", action='store_true')
    argparser.add_argument("--verbose","-v", help="verbose output", action='store_true')
    argparser.add_argument("--auth","-u", help="authentication data USER:PASS", required=True)

    return argparser.parse_args()


def showmodel():
    try:
      wbemchassis=wbemconn.EnumerateInstances('CIM_Chassis')
    except pywbem.cim_operations.CIMError,args:
      if ( args[1].find('Socket error') >= 0 ):
        print "UNKNOWN: %s" %args
        sys.exit (ExitUnknown)
      else:
        verboseoutput("Unknown CIM Error: %s" % args)
    except pywbem.cim_http.AuthError,arg:
      verboseoutput("Global exit set to UNKNOWN")
      GlobalStatus = ExitUnknown
      print "UNKNOWN: Authentication Error"
      sys.exit (GlobalStatus)
    
    for instance in wbemchassis:
        vendor = instance['Manufacturer']
        hw_model = instance['Model']
        sn = instance['SerialNumber']
    
    model = [ vendor, hw_model, sn ]
    return model

args = parse_arguments()
hosturl = "https://" + args.host
user, password = args.auth.split(":")

if args.verbose:
    print("your host: {}".format(hosturl))
    print("your hardware to check: {}".format(args.hw))

wbemconn = pywbem.WBEMConnection(hosturl,(user,password), no_verification=True)

if args.model:
    for key in showmodel():
        print key,
