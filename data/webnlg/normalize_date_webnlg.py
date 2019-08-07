# extracted from preprocess_webnlgy for David

import datetime

class WebNLGTargets():
    @staticmethod
    def is_date(string):
        try:
            datetime.datetime.strptime(string, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    @staticmethod
    def to_ordinal(n):
        # else covers 11th-13th
        return str(n) + ("th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))

    @staticmethod
    def get_month(int):
        months = "january february march april may june july august september october november december".split()
        int = int - 1
        if 0 <= int <= 11:
            return months[int]
        else:
            return ""

    @staticmethod
    def convert_to_text_date(date):
        month = WebNLGTargets.get_month(date.month)
        year = date.year
        day = WebNLGTargets.to_ordinal(date.day)
        date_string = "%s %s , %d" % (month, day, year)

        return date_string

    @staticmethod
    def normalize_date(string):
        """
        map date to format november 18th , 1923
        :param string:
        :return:
        """
        if WebNLGTargets.is_date(string):
            date = datetime.datetime.strptime(string, '%Y-%m-%d')
            string = WebNLGTargets.convert_to_text_date(date)
        return string

# normalize date if necessary
string = "1907-07-11" #some word e.g. one of these "adams county, national park, 1907-07-11"
string_to_delex_with_normalized_date = WebNLGTargets.normalize_date(string)\
# output for each of the words: adams county, national park, 11th of July 1907
# (strings that do not match the date regex are not changed)
# if you apply this after lowercasing, you have to lowercase the string_to_delex_with_normalized_date
# because the month name is probably uppercased
