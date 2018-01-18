class UtilityClassFunctionality(object):
    """
    Utility methods for use in scripts.
    """

    INFO_LEVEL = "info"
    WARNING_LEVEL = "warning"
    ERROR_LEVEL = "error"

    def __init__(self):
        """
        Initialize UtilityClassFunctionality object

        As of 20171109 all custom methods were static.
        """
        return

    @staticmethod
    def rawInputBasicChecks(strRawInputPromptSentence):
        """
        Prompt user for input and check for empty entry.

        Static method in UtilityClass
        :param strRawInputPromptSentence: The prompting language to help user
        :return: String
        """
        import sys
        strUserInput = None
        while True:
            version = sys.version
            strUserInput = None
            if version.startswith("2.7."):
                strUserInput = raw_input(strRawInputPromptSentence)
            elif version.startswith("3."):
                strUserInput = input(strRawInputPromptSentence)
            else:
                exit()
            if strUserInput == None or len(strUserInput) == 0:
                pass
            else:
                break
        return strUserInput

    @staticmethod
    def processUserEntry_YesNo(strUserEntry):
        """
        Evaluate the users response to a raw_input for yes or no.

        Static method in UtilityClass
        :param strUserEntry: Users entry
        :return: No return, or return exit on fail
        """
        if strUserEntry.lower() == "y":
            pass
        else:
            return exit()

    @staticmethod
    def captureAndPrintGeoprocessingErrors(func):
        """
        Wrap a function with try and except. Decorator.

        :param func: The ESRI geoprocessing function object
        :return: The resulting value from the tool on successful run, or exit on fail.
        """

        from arcpy import ExecuteError, GetMessages
        def f(*args, **kwargs):
            try:
                resultValue = func(*args, **kwargs)
            except ExecuteError:
                UtilityClassFunctionality.printAndLog("UtilityClass.captureAndPrintGeoprocessingErrors: Geoprocessing Error.\n{}".format(GetMessages(2)), UtilityClassFunctionality.ERROR_LEVEL)
                return exit()
            except Exception as e:
                UtilityClassFunctionality.printAndLog("UtilityClass.captureAndPrintGeoprocessingErrors: {}".format(e),UtilityClassFunctionality.ERROR_LEVEL)
                return exit()
            return resultValue
        return f

    @staticmethod
    def checkPathExists(strPath):
        """
        Check for path existence.

        :param strPath: The path of interest
        :return: No return, or exit on fail
        """
        import os.path
        if os.path.exists(strPath):
            return
        else:
            UtilityClassFunctionality.printAndLog("Path does not exist.", UtilityClassFunctionality.ERROR_LEVEL)
            return exit()

    @staticmethod
    def printAndLog(strMessage, strLogLevel):
        """
        Print and log any provided message based on the indicated logging level.

        :param strMessage:
        :param strLogLevel:
        :return:
        """
        import logging
        strMessage = str(strMessage).rstrip("\n")
        if strLogLevel is UtilityClassFunctionality.INFO_LEVEL:
            logging.info(strMessage)
        elif strLogLevel is UtilityClassFunctionality.WARNING_LEVEL:
            logging.warning(strMessage)
        elif strLogLevel is UtilityClassFunctionality.ERROR_LEVEL:
            logging.error(strMessage)
        print(strMessage)
        return

    @staticmethod
    def getDateTimeForLoggingAndPrinting():
        """
        Generate a preformatted date and time string for logging and printing purposes.

        :return: String {}/{}/{} UTC[{}:{}:{}] usable in logging, and printing statements if desired
        """
        import datetime
        tupTodayDateTime = datetime.datetime.utcnow().timetuple()
        strTodayDateTimeForLogging = "{}/{}/{} UTC[{}:{}:{}]".format(tupTodayDateTime[0]
                                                                     , tupTodayDateTime[1]
                                                                     , tupTodayDateTime[2]
                                                                     , tupTodayDateTime[3]
                                                                     , tupTodayDateTime[4]
                                                                     , tupTodayDateTime[5])
        return strTodayDateTimeForLogging

    # USED DURING TESTING
    # @staticmethod
    # def examineResultObject(resultObjectFromESRIProcess):
    #     """
    #     Examine the result object generated from an ESRI process.
    #
    #     Static method in UtilityClass
    #     :param resultObjectFromESRIProcess: result object from geoprocessing process
    #     :return: No return
    #     """
    #     lenResult = len(resultObjectFromESRIProcess)
    #     print("len: {}".format(lenResult))
    #     for i in range(0,lenResult):
    #         strTemp = str(resultObjectFromESRIProcess[i])
    #         print("\t{}".format(strTemp))
