###################################
# Script:  InventoryGISDataInGDBs_V2.py
# Author:  CJuice on GitHub
# Date Created:  05/02/2017
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
import os
import GenerateDateInfo
import FeatureClassObject_Class
import GeodatabaseDomain_Class

doLogging = False
if doLogging:
    print "Logging Enabled\n"
                 
#These paths are for the various environment sets of SDE Connections. Not sure why universal path causes problems.
##dictSDEConnectionPaths = {1 : u'\\\\tceq4apmgisdata\\giswrk\\IRGIS\\GIS Data\\2_TCEQ Data Inventory\\SDE_Connections_ForDataOwnersInventoryPurpose\\DEV_EnterpriseGDB',
##                          2 : u'\\\\tceq4apmgisdata\\giswrk\\IRGIS\\GIS Data\\2_TCEQ Data Inventory\\SDE_Connections_ForDataOwnersInventoryPurpose\\TST_EnterpriseGDB',
##                          3 : u'\\\\tceq4apmgisdata\\giswrk\\IRGIS\\GIS Data\\2_TCEQ Data Inventory\\SDE_Connections_ForDataOwnersInventoryPurpose\\USRTST_EnterpriseGDB',
##                          4 : u'\\\\tceq4apmgisdata\\giswrk\\IRGIS\\GIS Data\\2_TCEQ Data Inventory\\SDE_Connections_ForDataOwnersInventoryPurpose\\PRD_EnterpriseGDB',
##                          5 : u'\\\\tceq4apmgisdata\\giswrk\\IRGIS\\GIS Data\\2_TCEQ Data Inventory\\SDE_Connections_ForDataOwnersInventoryPurpose\\USRPRD_EnterpriseGDB',
##                          6 : u'\\\\tceq4apmgisdata\\giswrk\\IRGIS\\GIS Data\\2_TCEQ Data Inventory\\TEST_SDE_Connections'}
dictSDEConnectionPaths = {1 : r"M:\IRGIS\GIS Data\2_TCEQ Data Inventory\SDE_Connections_ForDataOwnersInventoryPurpose\DEV_EnterpriseGDB",
                          2 : r"M:\IRGIS\GIS Data\2_TCEQ Data Inventory\SDE_Connections_ForDataOwnersInventoryPurpose\TST_EnterpriseGDB",
                          3 : r"M:\IRGIS\GIS Data\2_TCEQ Data Inventory\SDE_Connections_ForDataOwnersInventoryPurpose\USRTST_EnterpriseGDB",
                          4 : r"M:\IRGIS\GIS Data\2_TCEQ Data Inventory\SDE_Connections_ForDataOwnersInventoryPurpose\PRD_EnterpriseGDB",
                          5 : r"M:\IRGIS\GIS Data\2_TCEQ Data Inventory\SDE_Connections_ForDataOwnersInventoryPurpose\USRPRD_EnterpriseGDB",
                          6 : r"M:\IRGIS\GIS Data\2_TCEQ Data Inventory\TEST_SDE_Connections"}
intDictLength = len(dictSDEConnectionPaths)

# Get the users choice of environments to examine.
boolInvalidAnswer = True
while boolInvalidAnswer:
    print "Here are the choices of sde connection files to examine."
    for key in dictSDEConnectionPaths.keys():
        print str(key) + ". " + os.path.basename(dictSDEConnectionPaths[key])
    strUserChoice = raw_input("\nWhich set of sde connections do you want to examine? Enter the corresponding number (1-" + str(intDictLength) + "). \n(or type 'exit' to abort)\n")
    if strUserChoice == "exit":
        print "goodbye"
        boolInvalidAnswer = False
        exit()
    elif not strUserChoice.isalpha() and (int(strUserChoice) >= 1 and int(strUserChoice) <= intDictLength ):
        boolInvalidAnswer = False
    else:
        print "Your answer was not in the range of 1 through " + str(intDictLength)
        print "Try again..."
        continue        

# Set the path
sdeFilesPath = dictSDEConnectionPaths[int(strUserChoice)]

lsDateParts = GenerateDateInfo.getDateParts()
strDateToday = lsDateParts[0] #Original date format
strDateTodayDatabaseField = lsDateParts[2] + "/" + lsDateParts[3] + "/" + lsDateParts[1] #redesigned date format to meet Access database format for Date
sdeFilesList = []
strOutputFile = r"\\tceq4apmgisdata\giswrk\IRGIS\GIS Data\2_TCEQ Data Inventory" + "\\" + strDateToday + "_" + os.path.basename(sdeFilesPath) +  "__FeatureClassInventory.csv"
strOutputFieldsFile = r"\\tceq4apmgisdata\giswrk\IRGIS\GIS Data\2_TCEQ Data Inventory" + "\\" + strDateToday + "_" + os.path.basename(sdeFilesPath) +  "__FeatureClassFIELDSInventory.csv"
strOutputDomainsFile = r"\\tceq4apmgisdata\giswrk\IRGIS\GIS Data\2_TCEQ Data Inventory" + "\\" + strDateToday + "_" + os.path.basename(sdeFilesPath) +  "__GeodatabaseDomainsInventory.csv"
lsFCHeaders = ["FC_ID","ADM_ID","FC_FDNAME","FC_NAME","FC_DATATYPE","FC_SHAPETYPE","FC_SPATIALREFNAME","FC_DATEEXPORT", "FC_MEETSLOOSESTD", "FC_MEETSSTRICTSTD", "CP_ID"]
lsFieldHeaders = ["FIELD_ID","FC_ID","FLD_ALIAS","FLD_NAME","FLD_TYPE","FLD_DEF_VAL","FLD_DOMAIN","FLD_ISNULLABLE","FLD_LENGTH","FLD_PRECISION","FLD_SCALE","FLD_REQUIRED"]
lsDomainHeaders = ["DOMAIN_ID","ENV_ID","DOM_NAME","DOM_OWNER","DOM_DESC","DOM_DOMAINTYPE","DOM_TYPE","DOM_CODEDVALKEYS","DOM_CODEDVALVALUES","DOM_RANGE","DOM_DATEEXPORT"]
lsFeatureDataSetADMs = []
lsFeatureDataSetNames = []
dictFDParts = {}
intRoundCount = 0

print "Importing arcpy...\n"
import arcpy

try:
    
    # Set the workspace to the user chosen folder
    arcpy.env.workspace = sdeFilesPath
    
    # Iterate through the sde files in the folder. By the most current design, there should only be one SDE@ connection file per environment. But the script can
    #     handle more than one to accommodate investigations into particular ADM accounts/partitions.
    for sdeFile in arcpy.ListFiles():
        sdeFilesList.append(sdeFile)
except:
    print "Issue creating list of sde file names.\n"
    print arcpy.GetMessages()
    exit()

# Create the new output file for the feature class inventory with headers
try:
    fhand = open(strOutputFile,"w")
    fhand.write(",".join(lsFCHeaders) + "\n")
    fhand.close()
except:
    print "Problem creating or checking existence of " +  strOutputFile + " file.\n"
    exit()

# Create the new output file for the feature class fields inventory with headers
try:
    fhandFieldsFile = open(strOutputFieldsFile,"w")
    fhandFieldsFile.write(",".join(lsFieldHeaders) + "\n")
    fhandFieldsFile.close()
except:
    print "Problem creating or checking existence of " +  strOutputFieldsFile + " file.\n"
    exit()

# Create the new output file for the Domains inventory with headers
try:
    fhandDomainsFile = open(strOutputDomainsFile,"w")
    fhandDomainsFile.write(",".join(lsDomainHeaders) + "\n")
    fhandDomainsFile.close()
except:
    print "Problem creating or checking existence of " +  strOutputDomainsFile + " file.\n"
    exit()
    
# Iterate through the sde files to inventory feature classes. Due to the glitch in SDE where all Feature Datasets are visible from any SDE connection file the script first looks
#    at all uncontained/loose Feature Classes sitting in the root geodatabase. After inventorying all of those it then lists the Feature Datasets and proceeds to step into each dataset
#    by altering the arcpy.env.workspace to the dataset so that the ListFeatureClasses() function returns with results. The feature classes within a feature dataset are not visible unless
#    the workspace is the dataset itself.
sdeFilesTuple = tuple(sdeFilesList)
lsTrackEnvironments = []
for admSDEFile in sdeFilesTuple:
    lsFeatureClasses = None
    lsFeatureDataSets = None
    lsDomainObjects = None
    strSDENameAlteration = admSDEFile.replace("@",".")
    lsSDENameParts = strSDENameAlteration.split(".")
    
    # Need the ENVIRONMENT name to create the unique ID's for the inventory database table records. This comes from the sde file name, not an environment property. So, if the filename is wrong, this is wrong.
    strENVName = lsSDENameParts[1]

    # Open/Create the output files for results to be appended.
    try:
        fhand = open(strOutputFile, "a")
    except:
        print "Feature Class File did not open. Iteration: " + admSDEFile +"\n"
        exit()
    try:
        fhandFieldsFile = open(strOutputFieldsFile, "a")
    except:
        print "Fields File did not open. Iteration: " + admSDEFile +"\n"
        exit()
    try:
        fhandDomainsFile = open(strOutputDomainsFile, "a")
    except:
        print "Domains File did not open. Iteration: " + admSDEFile +"\n"
        exit()

    # Change the workspace to the sde file gdb of interest. In the ideal design situation the workspace will be the single SDE connection file. But, the script can handle multiple SDE files for lower
    #    level ADMs
    try:
        arcpy.env.workspace = sdeFilesPath + "\\" + admSDEFile + "\\\\"
    except:
        print "Problem establishing workspace for: " + admSDEFile +"\n"

    print "Accessing {0}...\n".format(admSDEFile)
    
    # make a list of domains for the geodatabase workspace environment. If multiple sde files are examined for an environment, to prevent duplicates in file, the environment name is checked for previous use/examination.
    try:
        lsDomainObjects = arcpy.da.ListDomains()
    except:
        print "arcpy.da.ListDomains() failed"
    if strENVName not in lsTrackEnvironments:
        lsTrackEnvironments.append(strENVName)
        for domainObject in lsDomainObjects:
            gdbD = GeodatabaseDomain_Class.GeodatabaseDomains(strENVName, domainObject, strDateTodayDatabaseField)
            fhandDomainsFile.write(gdbD.generateDatabaseEntryText() + "\n")
    else:
        pass
    
    # make a list of feature classes present, outside of Feature Datasets
    lsFeatureClasses = arcpy.ListFeatureClasses()
    try:
        if doLogging:
            print "Looking for feature classes in... " + arcpy.env.workspace +"\n"
            print lsFeatureClasses
        
        for fc in lsFeatureClasses:
            
            # For purposes of building the FC_ID consistent with the portion of the script that iterates through feature datasets
            strFDName = ""
            
            # Instead of using Describe objects basename, which is ADMName.FeatureClassName, grab just the feature class name for use
            lsFCParts = fc.split(".",1)
            strADMName = lsFCParts[0]
            strFCName = lsFCParts[1]
            strADM_ID = strENVName + "." + strADMName
            strFC_ID = strADM_ID + "." + strFDName + "." + strFCName
            strContactPerson = "1" # This is revised in the data inventory database environment. The default value of 1 equals "Unknown" contact person
            
            try:
                
                # Get the arcpy.Desribe object for each feature class
                fcDesc = arcpy.Describe(fc)
                lsBaseNameParts = fcDesc.baseName.split(".",1)
             
                try:
                    
                    # Build the feature class object
                    FC = FeatureClassObject_Class.FeatureClassObject(strFC_ID, strADM_ID, strFDName, strFCName, fcDesc, strDateTodayDatabaseField, strContactPerson)
                except:
                    print "FeatureClassObject didn't instantiate"
                try:
                    # Evaluate the Loose standards
                    FC.evaluateFC_LooseStandards()
                except:
                    print "Loose standards evaluation failed"
                try:
                    # Evaluate the Loose standards
                    FC.evaluateFC_StrictStandards()
                except:
                    print "Strict standards evaluation failed"
                try:
                    fhand.write(FC.writeFeatureClassProperties() + "\n")
                except:
                    print "Did not write FC properties to file"
            except:
                print "Error with " + fc +"\n"
               
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
                        print "FeatureClassFieldDetailsObject didn't instantiate"
                    try:
                        fhandFieldsFile.write(fcFieldDetails.writeFeatureClassFieldProperties() + "\n")
                    except:
                        print "Did not write fcFieldDetails properties to file"
            except:
                print "Error with writing field details for " + strField_ID + "\n"
                
                # For feature class field details that don't process correctly this write statement records their presence so that they don't go undocumented.
                fhandFieldsFile.write(strField_ID + strFC_ID + "ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n")
    except:
        print "Problem iterating through feature classes" +"\n"
        
    # make a list of feature datasets present.
    lsFeatureDataSets = arcpy.ListDatasets()
    strFDName = "" # resetting from above because it is used below.
    for fd in lsFeatureDataSets:
        print "Examining feature dataset: " + fd
        
        # For purposes of building the FC_ID and documenting the feature dataset name without the ADM name (ADM_Name.FD_Name) we need to isolate the feature dataset name
        lsFDParts = fd.split(".",1)
        strFDName = lsFDParts[1]
        
        # Step into each feature dataset by altering the workspace
        arcpy.env.workspace = sdeFilesPath + "\\" + admSDEFile + "\\\\" + fd
        if doLogging:
                print "Looking for feature classes in... ", arcpy.env.workspace +"\n"
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
                        print "FeatureClassObject didn't instantiate"
                    try:
                        
                        # Evaluate the Loose standards
                        FC.evaluateFC_LooseStandards()
                    except:
                        print "Loose standards evaluation failed"
                    try:
                        
                        # Evaluate the Loose standards
                        FC.evaluateFC_StrictStandards()
                    except:
                        print "Strict standards evaluation failed"
                    try:
                        fhand.write(FC.writeFeatureClassProperties() + "\n")
                    except:
                        print "Did not write FC properties to file"
                except:
                    print "Error with " + fc +"\n"
                   
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
                            print "FeatureClassFieldDetailsObject didn't instantiate"
                        try:
                            fhandFieldsFile.write(fcFieldDetails.writeFeatureClassFieldProperties() + "\n")
                        except:
                            print "Did not write fcFieldDetails properties to file"
                except:
                    print "Error with writing field details for " + strField_ID + "\n"
                    
                    # For feature class field details that don't process correctly this write statement records their presence so that they don't go undocumented.
                    fhandFieldsFile.write(strField_ID + strFC_ID + "ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n")
        except:
            print "Problem iterating through feature classes within feature dataset" +"\n"
        
    fhand.close()
    fhandFieldsFile.close()
    fhandDomainsFile.close()
print "\nScript completed."
