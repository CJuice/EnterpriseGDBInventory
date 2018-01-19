###################################
# Script:  InventoryGISDataInGDBs_V2.py
# Author:  CJuice on GitHub
# Date Created:  05/02/2017
# Compatibility: Revised on 20180118 for Python 3.6.2
# Purpose:  Run through a folder containing a(n) .sde connection file inventory the feature classes.
# Inputs:  User defined folder choice (integer)
# Outputs:  Text csv file
# Modifications:  Originated as V1. That script examined any ADM connection file. We realized the master SDE connection file sees all so we
#                    switched to just examine that file. When the switch was made the functionality to look into the Feature Datasets was broken.
#                    A redesign was done. A glitch exists with examining Feature Datasets. From any sde connection file you can see feature datasets
#                    in other ADMs despite them being protected behind login and passwords to protect the compartments of data for different program areas.
#                    For example, if you call a list of feature datasets while looking at MSW_ADM you can see the feature datasets in the GW_ADM. By moving to 
#                    examining just the master SDE connection for an environment all of the Feature Datasets and Feature Classes are visible and accessible. 
#                    This allowed a redesign so that the script could step into the Feature Datasets to get the Feature Classes, which aren't visible from the
#                    root gdb. The script arcpy.env.workspace has to change to the Feature Dataset to access/see the Feature Classes within.
###################################
# IMPORTS
import os, sys
# import GenerateDateInfo
import FeatureClassObject_Class
import GeodatabaseDomain_Class
import logging
from UtilityClass import UtilityClassFunctionality
import arcpy

# VARIABLES
    # Logging setup
strLogFileName = "LOG_TaxMapProcessing.log"
logging.basicConfig(filename=strLogFileName,level=logging.INFO)
UtilityClassFunctionality.printAndLog(" {} - InventoryGISDataInGDBs_V2.py Initiated".format(UtilityClassFunctionality.getDateTimeForLoggingAndPrinting()), UtilityClassFunctionality.INFO_LEVEL)
    # Inputs:
        # Get the users choice of environments to examine. Check validity.
sdeFilesPath = None
strUserSDEFilePathChoice = UtilityClassFunctionality.rawInputBasicChecks("\nPaste the precise path to the .sde connection file you wish to use\n>>")
if UtilityClassFunctionality.checkPathExists(strUserSDEFilePathChoice):
    sdeFilesPath = strUserSDEFilePathChoice
else:
    UtilityClassFunctionality.printAndLog("Path does not exist.\n{}".format(strUserSDEFilePathChoice), UtilityClassFunctionality.ERROR_LEVEL)
    exit()

        # Get the output directory location. Check validity.
strOutputFileDirectory = None
strUsersOutputFileDirectoryChoice = UtilityClassFunctionality.rawInputBasicChecks("\nPaste the path to the directory where new output files will be created.\n>>")
if UtilityClassFunctionality.checkPathExists(strUsersOutputFileDirectoryChoice):
    strOutputFileDirectory = strUsersOutputFileDirectoryChoice
else:
    UtilityClassFunctionality.printAndLog("Path does not exist.\n{}".format(strOutputFileDirectory), UtilityClassFunctionality.ERROR_LEVEL)
    exit()

lsDateParts = UtilityClassFunctionality.getDateParts() #GenerateDateInfo.getDateParts()
strDateToday = lsDateParts[0] #Original date format
strDateTodayDatabaseField = lsDateParts[2] + "/" + lsDateParts[3] + "/" + lsDateParts[1] #redesigned date format to meet Access database format for Date
sdeFilesList = []

strOutputFeatureClassFile = os.path.join(strOutputFileDirectory, "{}_{}__FeatureClassInventory.csv".format(strDateToday, os.path.basename(sdeFilesPath)))
strOutputFieldsFile = os.path.join(strOutputFileDirectory, "{}_{}__FeatureClassFIELDSInventory.csv".format(strDateToday, os.path.basename(sdeFilesPath)))
strOutputDomainsFile = os.path.join(strOutputFileDirectory, "{}_{}__GeodatabaseDomainsInventory.csv".format(strDateToday, os.path.basename(sdeFilesPath)))

lsFCHeaders = ["FC_ID","ADM_ID","FC_FDNAME","FC_NAME","FC_DATATYPE","FC_SHAPETYPE","FC_SPATIALREFNAME","FC_DATEEXPORT", "FC_MEETSLOOSESTD", "FC_MEETSSTRICTSTD", "CP_ID"]
lsFieldHeaders = ["FIELD_ID","FC_ID","FLD_ALIAS","FLD_NAME","FLD_TYPE","FLD_DEF_VAL","FLD_DOMAIN","FLD_ISNULLABLE","FLD_LENGTH","FLD_PRECISION","FLD_SCALE","FLD_REQUIRED"]
lsDomainHeaders = ["DOMAIN_ID","ENV_ID","DOM_NAME","DOM_OWNER","DOM_DESC","DOM_DOMAINTYPE","DOM_TYPE","DOM_CODEDVALKEYS","DOM_CODEDVALVALUES","DOM_RANGE","DOM_DATEEXPORT"]

lsFeatureDataSetADMs = []
lsFeatureDataSetNames = []
dictFDParts = {}
intRoundCount = 0

# METHODS
@UtilityClassFunctionality.captureAndPrintGeoprocessingErrors
def runESRIGPTool(func, *args, **kwargs):
    """Pass ESRI geoprocessing function and arguements through Decorator containing error handling functionality"""

    return func(*args, **kwargs)

# FUNCTIONALITY
arcpy.env.workspace = sdeFilesPath


# try:
#     # Set the workspace to the user chosen folder
#     arcpy.env.workspace = sdeFilesPath
#     for sdeFile in arcpy.ListFiles():
#         sdeFilesList.append(sdeFile)
# except Exception as e:
#     UtilityClassFunctionality.printAndLog(e,UtilityClassFunctionality.ERROR_LEVEL)
#     print(arcpy.GetMessages())
#     exit()

# Create the new output file for the feature class inventory with headers
try:
    with open(strOutputFeatureClassFile, "w") as fhand:
        fhand.write(",".join(lsFCHeaders) + "\n")
        fhand.close()
except:
    UtilityClassFunctionality.printAndLog("Problem creating or checking existence of {} file.\n".format(strOutputFeatureClassFile), UtilityClassFunctionality.ERROR_LEVEL)
    exit()

# Create the new output file for the feature class fields inventory with headers
try:
     with open(strOutputFieldsFile,"w") as fhandFieldsFile:
         fhandFieldsFile.write(",".join(lsFieldHeaders) + "\n")
         fhandFieldsFile.close()
except:
    UtilityClassFunctionality.printAndLog("Problem creating or checking existence of {} file.\n".format(strOutputFieldsFile), UtilityClassFunctionality.ERROR_LEVEL)
    exit()

# Create the new output file for the Domains inventory with headers
try:
     with open(strOutputDomainsFile,"w") as fhandDomainsFile:
         fhandDomainsFile.write(",".join(lsDomainHeaders) + "\n")
         fhandDomainsFile.close()
except:
    UtilityClassFunctionality.printAndLog("Problem creating or checking existence of {} file.\n".format(strOutputDomainsFile),UtilityClassFunctionality.ERROR_LEVEL)
    exit()

# TODO: Continue here

# Iterate through the sde files to inventory feature classes.
#   Due to the glitch in SDE where all Feature Datasets are visible from any SDE connection file, the script first looks
#   at all uncontained/loose Feature Classes sitting in the root geodatabase. After inventorying all of those it then lists the Feature Datasets and proceeds to step into each dataset
#   by altering the arcpy.env.workspace to the dataset so that the ListFeatureClasses() function returns with results. The feature classes within a feature dataset are not visible unless
#   the workspace is the dataset itself.

# sdeFilesList.append(os.path.basename(sdeFilesPath)) #Original design could handle multiple sde files. Redesign focuses on one sde file.
# UtilityClassFunctionality.printAndLog(sdeFilesPath, UtilityClassFunctionality.INFO_LEVEL) #TROUBLESHOOTING

# sdeFilesTuple = tuple(sdeFilesList)
sdeEnvironment_FileName = os.path.basename(sdeFilesPath)
# lsTrackEnvironments = []
lsFeatureClasses = None
lsFeatureDataSets = None
lsDomainObjects = None
# strSDENameAlteration = admSDEFile.replace("@",".") # was environment specific manipulation
lsSDENameParts = sdeEnvironment_FileName.split(".")


# Need the ENVIRONMENT name to create the unique ID's for the inventory database table records. This comes from the sde file name, not an environment property. So, if the filename is wrong, this is wrong.
# strENVName = lsSDENameParts[1] # environment name was list index 1 item in previous design
strENVName = lsSDENameParts[0]

# Open/Create the output files for results to be appended.
try:
    fhand = open(strOutputFeatureClassFile, "a")
except:
    print("Feature Class File did not open. Iteration: " + sdeEnvironment_FileName +"\n")
    exit()
try:
    fhandFieldsFile = open(strOutputFieldsFile, "a")
except:
    print("Fields File did not open. Iteration: " + sdeEnvironment_FileName +"\n")
    exit()
try:
    fhandDomainsFile = open(strOutputDomainsFile, "a")
except:
    print("Domains File did not open. Iteration: " + sdeEnvironment_FileName +"\n")
    exit()
try:
    arcpy.env.workspace = sdeFilesPath
except:
    print("Problem establishing workspace: " + sdeFilesPath +"\n")

UtilityClassFunctionality.printAndLog("Accessing {}\n".format(arcpy.env.workspace),UtilityClassFunctionality.INFO_LEVEL)

# make a list of domains for the geodatabase workspace environment. If multiple sde files are examined for an environment, to prevent duplicates in file, the environment name is checked for previous use/examination.
try:
    lsDomainObjects = runESRIGPTool(arcpy.da.ListDomains,arcpy.env.workspace)
except:
    UtilityClassFunctionality.printAndLog("arcpy.da.ListDomains() failed", UtilityClassFunctionality.ERROR_LEVEL)
    exit()

# if len(lsDomainObjects) > 0 and strENVName not in lsTrackEnvironments:
#     lsTrackEnvironments.append(strENVName)
for domainObject in lsDomainObjects:
    gdbD = GeodatabaseDomain_Class.GeodatabaseDomains(sdeEnvironment_FileName, domainObject, strDateTodayDatabaseField)
    fhandDomainsFile.write(gdbD.generateDatabaseEntryText() + "\n")
else:
    pass

# make a list of feature classes present, outside of Feature Datasets
try:
    lsFeatureClasses = runESRIGPTool(arcpy.ListFeatureClasses, arcpy.env.workspace)
except:
    UtilityClassFunctionality.printAndLog("Error creating list of feature classes outside of feature datasets", UtilityClassFunctionality.ERROR_LEVEL)
    exit()

#TODO: start here
#TODO: How to deal with creating a unique FC id without the ADM accounts
try:
    if lsFeatureClasses != None and len(lsFeatureClasses) > 0:
        UtilityClassFunctionality.printAndLog("Looking for feature classes in {}\n".format((arcpy.env.workspace), UtilityClassFunctionality.INFO_LEVEL))
        for fc in lsFeatureClasses:

            # For purposes of building the FC_ID consistent with the portion of the script that iterates through feature datasets
            strFDName = "_"

            # COMMENTED OUT DURING REFACTORING. strADMName existed at previous employer. Don't know
            # Instead of using Describe objects basename, which is ADMName.FeatureClassName, grab just the feature class name for use
            # lsFCParts = fc.split(".",1)
            # strADMName = lsFCParts[0]
            # strFCName = lsFCParts[1]
            # strADM_ID = strENVName + "." + strADMName
            # strFC_ID = strADM_ID + "." + strFDName + "." + strFCName
            # strContactPerson = "1" # This is revised in the data inventory database environment. The default value of 1 equals "Unknown" contact person
            strADMName = None
            strFCName = None
            if "." in fc:
                lsFCParts = fc.split(".",1)
                strADMName = lsFCParts[0]
                strFCName = lsFCParts[1]
            else:
                strADMName = "_"
                strFCName = fc

            strADM_ID = strENVName + "." + strADMName
            strFC_ID = strADM_ID + "." + strFDName + "." + strFCName
            strContactPerson = "1" # This is revised in the data inventory database environment. The default value of 1 equals "Unknown" contact person

            try:

                # Get the arcpy.Describe object for each feature class
                fcDesc = arcpy.Describe(fc)
                lsBaseNameParts = fcDesc.baseName.split(".",1)

                try:

                    # Build the feature class object
                    FC = FeatureClassObject_Class.FeatureClassObject(strFC_ID, strADM_ID, strFDName, strFCName, fcDesc, strDateTodayDatabaseField, strContactPerson)
                except:
                    print("FeatureClassObject didn't instantiate")
                try:
                    # Evaluate the Loose standards
                    FC.evaluateFC_LooseStandards()
                except:
                    print("Loose standards evaluation failed")
                try:
                    # Evaluate the Loose standards
                    FC.evaluateFC_StrictStandards()
                except:
                    print("Strict standards evaluation failed")
                try:
                    fhand.write(FC.writeFeatureClassProperties() + "\n")
                except:
                    print("Did not write FC properties to file")
            except:
                print("Error with " + fc +"\n")

                # For feature classes that don't process correctly this write statement records their presence so that they don't go undocumented.
                fhand.write(strFC_ID +","+ strADM_ID +","+ strFDName +","+ strFCName +",ERROR,ERROR,ERROR," + strDateTodayDatabaseField +",ERROR,ERROR,"+ strContactPerson +"\n")

            try:

                # Get the fields in each feature class
                lsFCFields = fcDesc.fields
                for field in lsFCFields:
                    strField_ID = strFC_ID + "." + field.name
                    try:

                        # Build the feature class field details object
    #                         fcFieldDetails = FeatureClassObject_Class.FeatureClassFieldDetails(strFC_ID, field.aliasName, field.name, field.type, field.defaultValue, field.domain, field.isNullable, field.length, field.precision, field.required)
                        fcFieldDetails = FeatureClassObject_Class.FeatureClassFieldDetails(lsFCFields, strField_ID, strFC_ID, field)
                    except:
                        print("FeatureClassFieldDetailsObject didn't instantiate")
                    try:
                        fhandFieldsFile.write(fcFieldDetails.writeFeatureClassFieldProperties() + "\n")
                    except:
                        print("Did not write fcFieldDetails properties to file")
            except:
                print("Error with writing field details for " + strField_ID + "\n")

                # For feature class field details that don't process correctly this write statement records their presence so that they don't go undocumented.
                fhandFieldsFile.write(strField_ID + strFC_ID + "ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n")
    else:
        pass
except:
    print("Problem iterating through feature classes" +"\n")

# make a list of feature datasets present.
lsFeatureDataSets = arcpy.ListDatasets()
strFDName = "" # resetting from above because it is used below.
if len(lsFeatureDataSets) > 0:
    for fd in lsFeatureDataSets:
        print("Examining feature dataset: " + fd)

        # For purposes of building the FC_ID and documenting the feature dataset name without the ADM name (ADM_Name.FD_Name) we need to isolate the feature dataset name
        lsFDParts = fd.split(".",1)
        strFDName = lsFDParts[1]

        # Step into each feature dataset by altering the workspace
        arcpy.env.workspace = os.path.join(sdeFilesPath,fd)
        UtilityClassFunctionality.printAndLog("Looking for feature classes in {}\n".format(arcpy.env.workspace), UtilityClassFunctionality.INFO_LEVEL)
        lsFeatureClasses = arcpy.ListFeatureClasses()
        try:
            for fc in lsFeatureClasses:

                # Instead of using Describe objects basename, which is ADMName.FeatureClassName, grab just the feature class name for use
                lsFCParts = fc.split(".",1)
                strADMName = lsFCParts[0]
                strFCName = lsFCParts[1]
                strADM_ID = strENVName + "." + strADMName
                strFC_ID = strADM_ID + "." + strFDName + "." + strFCName
                strContactPerson = "1" # This is revised in the data inventory database environment. The default value of 1 is "Unknown" contact person

                try:

                    # Get the arcpy.Desribe object for each feature class
                    fcDesc = arcpy.Describe(fc)
                    lsBaseNameParts = fcDesc.baseName.split(".",1)

                    try:

                        # Build the feature class object
                        FC = FeatureClassObject_Class.FeatureClassObject(strFC_ID, strADM_ID, strFDName, strFCName, fcDesc, strDateTodayDatabaseField, strContactPerson)
                    except:
                        print("FeatureClassObject didn't instantiate")
                    try:

                        # Evaluate the Loose standards
                        FC.evaluateFC_LooseStandards()
                    except:
                        print("Loose standards evaluation failed")
                    try:

                        # Evaluate the Loose standards
                        FC.evaluateFC_StrictStandards()
                    except:
                        print("Strict standards evaluation failed")
                    try:
                        fhand.write(FC.writeFeatureClassProperties() + "\n")
                    except:
                        print("Did not write FC properties to file")
                except:
                    print("Error with " + fc +"\n")

                    # For feature classes that don't process correctly this write statement records their presence so that they don't go undocumented.
                    fhand.write(strFC_ID +","+ strADM_ID +","+ strFDName +","+ strFCName +",ERROR,ERROR,ERROR," + strDateTodayDatabaseField +","+ strContactPerson +"\n")

                try:

                    # Get the fields in each feature class
                    lsFCFields = fcDesc.fields
                    for field in lsFCFields:
                        strField_ID = strFC_ID + "." + field.name
                        try:

                            # Build the feature class field details object
    #                         fcFieldDetails = FeatureClassObject_Class.FeatureClassFieldDetails(strFC_ID, field.aliasName, field.name, field.type, field.defaultValue, field.domain, field.isNullable, field.length, field.precision, field.required)
                            fcFieldDetails = FeatureClassObject_Class.FeatureClassFieldDetails(lsFCFields, strField_ID, strFC_ID, field)
                        except:
                            print("FeatureClassFieldDetailsObject didn't instantiate")
                        try:
                            fhandFieldsFile.write(fcFieldDetails.writeFeatureClassFieldProperties() + "\n")
                        except:
                            print("Did not write fcFieldDetails properties to file")
                except:
                    print("Error with writing field details for " + strField_ID + "\n")

                    # For feature class field details that don't process correctly this write statement records their presence so that they don't go undocumented.
                    fhandFieldsFile.write(strField_ID + strFC_ID + "ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n")
        except:
            print("Problem iterating through feature classes within feature dataset" +"\n")
else:
    pass
fhand.close()
fhandFieldsFile.close()
fhandDomainsFile.close()
print("\nScript completed.")
