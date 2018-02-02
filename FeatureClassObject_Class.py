class FeatureClassObject(object):
    # Class to hold feature class objects from the arcpy.Describe functionality
    def __init__(self, fcID, ADM_ID, featureDataset, fcName, arcpyDescribeObject, dateExport):
        self.fcID = fcID
        self.ADM_ID = ADM_ID
        self.featureDataset = featureDataset
        self.fcName = fcName
        self.fcFeatureCount = -9999
        self.arcpyDescribeObject = arcpyDescribeObject
        self.dataType = arcpyDescribeObject.dataType
        self.shapeType = arcpyDescribeObject.shapeType
        self.spatialRefName = arcpyDescribeObject.spatialReference.name
        self.dateExport = dateExport

        
    def writeFeatureClassProperties(self):
        lsObjectFeatures = [self.fcID, self.ADM_ID, self.featureDataset, self.fcName, self.dataType, self.shapeType, self.spatialRefName, self.fcFeatureCount, self.dateExport]
        for i in range(len(lsObjectFeatures)):
            lsObjectFeatures[i] = str(lsObjectFeatures[i])
        return ",".join(lsObjectFeatures)
    


class FeatureClassFieldDetails(object):
    # Class to hold the details on the feature class object fields using the arpy.Describe fields info
    def __init__(self, lsFeatureClassFields, fieldID, fcID, field):
        self.lsFeatureClassFields = lsFeatureClassFields
        self.fieldID = fieldID
        self.fcID = fcID
        self.fieldAlias = field.aliasName.strip()
        self.fieldName = field.name.strip()
        self.fieldType = field.type
        self.fieldDefValue = field.defaultValue
        self.fieldDomain = field.domain
        self.fieldIsNullable = field.isNullable
        self.fieldLength = field.length
        self.fieldPrecision = field.precision
        self.fieldScale = field.scale
        self.fieldRequired = field.required
        
    def writeFeatureClassFieldProperties(self):
        lsObjectFeatures = [self.fieldID, self.fcID, self.fieldAlias, self.fieldName, self.fieldType, self.fieldDefValue, self.fieldDomain,
                            self.fieldIsNullable, self.fieldLength, self.fieldPrecision, self.fieldScale, self.fieldRequired]
        for i in range(len(lsObjectFeatures)):
            lsObjectFeatures[i] = str(lsObjectFeatures[i])
        return ",".join(lsObjectFeatures)

