class Error:
    def __init__(self, title, severity, offenders):
        self.title = title
        self.severity = severity
        self.offenders = offenders

    def __getError__(self, index):
    	return self.Error.errorId[index]

