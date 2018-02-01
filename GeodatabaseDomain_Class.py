class GeodatabaseDomains(object):
    def __init__(self, strENVName, objectDomain, strDate):
        self.strENVName = strENVName
        self.objectDomain = objectDomain
        self.date = strDate
        self.name = objectDomain.name
        self.owner = objectDomain.owner
        self.description = objectDomain.description
        self.domainType = objectDomain.domainType
        self.type = objectDomain.type
        self.codedValues = objectDomain.codedValues
        self.range = objectDomain.range
    
    def generateDatabaseEntryText(self):
        lsCodedValuesKeys = []
        lsCodedValuesValues = []
        strDomainID = "{}.{}".format(self.strENVName,self.name)
        try:
            lsCodedValuesKeys = self.objectDomain.codedValues.keys()
        except:
            pass
        try:
            lsCodedValuesValues = self.objectDomain.codedValues.values()
        except:
            pass
        strENVNameUPPER = self.strENVName.upper()
        lsRecordValues = [strDomainID,strENVNameUPPER,self.name,self.owner,self.description,self.domainType,self.type,lsCodedValuesKeys,lsCodedValuesValues,self.range,self.date]
        for i in range(len(lsRecordValues)):
            strTemp = str(lsRecordValues[i])
            lsRecordValues[i] = strTemp.replace(",", "|")
        return ",".join(lsRecordValues)