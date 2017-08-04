def getDateToday():
    import datetime
    dateToday = datetime.date.today()
    return dateToday
def getDateParts():
    import datetime
    dateToday = datetime.date.today()
    strDay = None
    strMonth = None
    strYear = None
    strFullDate = None
    intDay = dateToday.day
    if intDay < 10:
        strDay = "0" + str(intDay)
    else:
        strDay = str(intDay)
    intMonth = dateToday.month
    if intMonth < 10:
        strMonth = "0" + str(intMonth)
    else:
        strMonth = str(intMonth)
    intYear = dateToday.year
    strYear = str(intYear)
    strFullDate = strYear + strMonth + strDay
    lsDateParts = [strFullDate, strYear, strMonth, strDay]
    return lsDateParts
