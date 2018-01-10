import imp
import time
from datetime import datetime
import os
import glob
from prettytable import PrettyTable

# print glob.glob(cwd+"/*.py")

cwd = os.path.dirname(os.path.abspath(__file__))  # current work directory
TEST_CASE_DIR = cwd + "/tests/"
co_name = "testcase.co"


class Test:
    def __init__(self, name, description, run_func):
        self.name = name
        self.description = description
        self.time_elapsed = None
        self.run_func = run_func
        self.result = None

    def run(self):
        return self.run_func()

    def passed(self):
        print self.name + "(execution time " + str(
            self.time_elapsed.microseconds) + "ms) : " + '\033[92m' + "PASS!" + '\033[0m'
        self.result = True

    def failed(self):
        print self.name + "(execution time: " + str(
            self.time_elapsed.microseconds) + "ms) : " + '\033[91m' + "FAIL!" + '\033[0m'
        self.result = False

    def set_time_elapsed(self, time_elapsed):
        self.time_elapsed = time_elapsed


def get_run_func(test_case_name):
    f, p, d = imp.find_module(test_case_name, [TEST_CASE_DIR])
    test_module = imp.load_module(test_case_name, f, p, d)
    f.close()
    return getattr(test_module, "run")


def transfer_co_to_test_list():
    test_list = []
    f = open(cwd + "/" + co_name, 'r')
    line = f.readline().rstrip('\n')
    while line:
        if "#" in line:
            line = f.readline().rstrip('\n')
            continue
        line = line.split("    ")
        test_case_name = line[0]
        test_case_description = line[1]
        test_case_run_func = get_run_func(test_case_name)
        test_case = Test(test_case_name, test_case_description, test_case_run_func)
        test_list.append(test_case)

        line = f.readline().rstrip('\n')

    return test_list


def percentage(part, whole):
    result = 100 * float(part) / float(whole)
    return str(result) + "%"


def generate_test_case_table(test_list):
    report_table = PrettyTable(["Number", "Test Case Name", "Time Elapsed", "Pass/Fail"])
    number = 1
    for test_case in test_list:
        result = None
        if test_case.result == True:
            result = '\033[92m' + "PASS!" + '\033[0m'
        else:
            result = '\033[91m' + "FAIL!" + '\033[0m'
        report_table.add_row([number, test_case.name, test_case.time_elapsed, result])
        number += 1
    print report_table


def generate_result_table(test_list):
    total_case = 0
    pass_case = 0
    fail_case = 0
    pass_rate = 0

    for test_case in test_list:
        total_case += 1
        if test_case.result == True:
            pass_case += 1
        else:
            fail_case += 1

    if fail_case == 0:
        pass_rate = "100%"
    else:
        pass_rate = percentage(pass_case, total_case)

    report_table = PrettyTable(["Total Case", "Pass Case", "Fail Case", "Pass Rate"])
    report_table.add_row([total_case, pass_case, fail_case, pass_rate])
    print report_table


def main():
    test_list = transfer_co_to_test_list()

    for test_case in test_list:
        print "-------------------------------%s-----------------------------------" % test_case.name
        print "Description :" + test_case.description
        print "Test Start!"

        time_start = datetime.now()
        try:
            success = test_case.run_func()
            time_elapsed = datetime.now() - time_start
            test_case.set_time_elapsed(time_elapsed)
            if success:
                test_case.passed()
            else:
                test_case.failed()

        except Exception as e:
            print test_case.name + " Exception : " + str(e)
            time_elapsed = datetime.now() - time_start
            test_case.set_time_elapsed(time_elapsed)
            test_case.failed()

        print "Test Finish!"
        print "-------------------------------%s-----------------------------------" % test_case.name

    generate_test_case_table(test_list)
    generate_result_table(test_list)


if __name__ == '__main__':
    main()
