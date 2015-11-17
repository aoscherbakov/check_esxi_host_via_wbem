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
import sys

ExitOK = 0
ExitWarning = 1
ExitCritical = 2
ExitUnknown = 3

def parse_arguments():
    argparser = argparse.ArgumentParser(description="Check ESXi CIM Classes")
    argparser.add_argument("--host", help="ESXi host to check",required=True)
    argparser.add_argument("--hw", help="what hardware to check", choices=['raid','power','temp'],required=True)
    argparser.add_argument("--model","-m", help="print server model", action='store_true')
    argparser.add_argument("--verbose","-v", help="verbose output", action='store_true')
    argparser.add_argument("--auth","-u", help="authentication data USER:PASS", required=True)

    return argparser.parse_args()


def connect(classe):
    try:
        wbemclass=wbemconn.EnumerateInstances(classe)
    except pywbem.cim_operations.CIMError,args:
        if ( args[1].find('Socket error') >= 0 ):
            print("UNKNOWN: {}".format(args))
            sys.exit (ExitUnknown)
        else:
            print("UNKNOWN CIM Error: {}".format(args))
    except pywbem.cim_http.AuthError,arg:
        print("UNKNOWN: Authentication Error")
        sys.exit (ExitUnknown)
    return wbemclass

def interpretStatus(status):
    result = {
        0  : ExitOK,    # Unknown
        5  : ExitOK,    # OK
        10 : ExitWarning,  # Degraded
        15 : ExitWarning,  # Minor
        20 : ExitCritical,  # Major
        25 : ExitCritical,  # Critical
        30 : ExitCritical,  # Non-recoverable Error
        }[status]
    return result

args = parse_arguments()
hosturl = "https://" + args.host
user, password = args.auth.split(":")

wbemconn = pywbem.WBEMConnection(hosturl,(user,password), no_verification=True)

if args.verbose:
    print("your host: {}".format(hosturl))
    print("your hardware to check: {}".format(args.hw))

if args.model:
    wbemchassis = connect('CIM_Chassis')
    
    for instance in wbemchassis:
        model = {
            'mf': instance['Manufacturer'],
            'model': instance['Model'],
            'sn': instance['SerialNumber']
            }
        print model['mf'],model['model'],model['sn']

if args.hw == 'power':
    wbempower = connect('OMC_PowerSupply')
    for instance in wbempower:
        name = instance['ElementName']
        status = interpretStatus(instance['HealthState'])
 #       interpretStatus = {
 #           0  : ExitOK,    # Unknown
 #           5  : ExitOK,    # OK
 #           10 : ExitWarning,  # Degraded
 #           15 : ExitWarning,  # Minor
 #           20 : ExitCritical,  # Major
 #           25 : ExitCritical,  # Critical
 #           30 : ExitCritical,  # Non-recoverable Error
 #       }[status]
        
        if status == ExitWarning:
            print "WARNING: {} Failed, ".format(name),
        elif status == ExitCritical:
            print "CRITICAL: {} Failed, ".format(name),
        else:
            print "{} Status OK, ".format(name),
