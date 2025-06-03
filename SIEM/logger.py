    import sys
    from datetime import datetime
    class Logger:
        def __init__(self,filename):
            if filename[-4:] == ".log":
                self.filename = filename
                open(self.filename, 'a').close()
            else:
                print("please provide .log file")
                sys.exit()

        def log_info(self, message):
            now = datetime.now().strftime("%y/%m/%Y %H:%M:%S")
            with open(self.filename, "a") as f:
                f.write(f"{now} INFO: {message}\n")

        def log_error(self, message):
            now = datetime.now().strftime("%y/%m/%Y %H:%M:%S")
            with open(self.filename, "a") as f:
                f.write(f"{now} ERROR: {message}\n")


    info = Logger("info.log")
    error = Logger("error.log")
    info.log_info("this is a info message")
    error.log_error("this is an error message")
            



