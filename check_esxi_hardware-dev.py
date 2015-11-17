#!/usr/bin/python
#####################################
## Written by Shcherbakov A.O.     ##
##                                 ##
## Check ESXi host hardware status ##
## v.0.3                           ##
##                                 ##
## pywbem v.8.0 requied            ##
##                                 ##
#####################################

import pywbem
import argparse
import sys

ExitMsg = ''
result_list = []

def parse_arguments():
    argparser = argparse.ArgumentParser(description="Check ESXi CIM Classes")
    argparser.add_argument("--host", help="ESXi host to check",required=True)
    argparser.add_argument("--hw", help="what hardware to check", choices=['raid','power','temp'],required=True)
    #argparser.add_argument("--model","-m", help="print server model", action='store_true')
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
        0  : 'OK',    # Unknown
        5  : 'OK',    # OK
        10 : 'WARNING',  # Degraded
        15 : 'WARNING',  # Minor
        20 : 'CRITICAL',  # Major
        25 : 'CRITICAL',  # Critical
        30 : 'CRITICAL',  # Non-recoverable Error
        }[status]

    return result

args = parse_arguments()
hosturl = "https://" + args.host
user, password = args.auth.split(":")

wbemconn = pywbem.WBEMConnection(hosturl,(user,password), no_verification=True)

wbemchassis = connect('CIM_Chassis')

for instance in wbemchassis:
        mf = str(instance['Manufacturer'])
        model = str(instance['Model'])
        sn = str(instance['SerialNumber'])

model = "{} {} {} ".format(mf,model,sn)

if args.verbose:
    ExitMsg += model

if args.hw == 'power':
    wbempower = connect('OMC_PowerSupply')
    for instance in wbempower:
        name = str(instance['ElementName'])
        if instance['HealthState'] is not None :
            status = interpretStatus(instance['HealthState'])
        else:
            status = "None"
        res = "{} {} ".format(name,status)
        if status == 'WARNING' or status == 'CRITICAL' or args.verbose:
            ExitMsg += res
            result_list.append('Failure')

if args.hw == 'raid':
    wbemraid = connect('VMware_StorageExtent')
    for instance in wbemraid:
        name = str(instance['ElementName'])
        if instance['HealthState'] is not None :
            status = interpretStatus(instance['HealthState'])
        else:
            status = "None"
        if status == 'WARNING' or status == 'CRITICAL' or args.verbose:
            res = "{} {} ".format(name,status)
            ExitMsg += res
            result_list.append('Failure')

if 'Failure' not in result_list:
    print "Status OK"
else:
    print ExitMsg
