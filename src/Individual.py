import sys
import datetime
from user_stories import US23, US24

class Individual():
    row_headers = [
            "ID", "Name", "Gender", "Birthday", "Age", "Alive", "Death",
            "Children", "Spouse"
    ]

    error_header = "ERROR: INDIVIDUAL:"
    anomaly_header = "ANOMALY: INDIVIDUAL:"

    def __init__(self, id, name, gender, bday, age, familes, alive, death=None, children=None, spouses=None):
        if '@' in id:
            id.replace('@', '')
        self.id = id
        self.name = name
        self.gender = gender
        self.bday = bday
        self.age = age
        self.alive = alive
        self.families = familes
        self.death = death

        if children is None:
            self.children = []
        else:
            self.children = children

        if spouses is None:
            self.spouses = []
        else:
            self.spouses = spouses
        self.errors = []
        self.anomalies = []
        self.validate()

    def validate(self):
        self._check_dates()
        self._check_marriages2()
        self._check_birthday_coming()


    def _add_error(self, story, error):
        self.errors.append("%s %s: %s: %s" % 
                (Individual.error_header, story, self.id, error))
  
    def _add_anomaly(self, story, anomaly):
        self.anomalies.append("%s %s: %s: %s" %
                (Individual.anomaly_header, story, self.id, anomaly))

    def _check_birthday_coming(self):
        bday_in = self.bday
        curr_year = datetime.datetime.now().year
        bday_in = bday_in.replace(year=curr_year, month=bday_in.month, day=bday_in.day)
        check = bday_in - datetime.datetime.now()
        if check.days<30 and check.days>0:
            print("US31: "+self.id+" Upcoming birthday on: "+str(self.bday))
    def _check_marriages2(self):
        #US17 No marriages to descendants
        childrenList = []
        temp = self.children
        if self.children is not None:
            while temp != []:
                for group in temp:
                    childrenList.append(group)
                    if type(group.children)!=list:
                        temp.append(group.children)
                        temp.remove(group)
                    else:
                        temp = []
        for spouse in self.spouses:
            if spouse in childrenList:
                self._add_anomaly("US17", "Husband is a descendant")
           
                    
    def _check_dates(self):
        now = datetime.datetime.now()

        # Birth and death dates before current date
        if self.bday is not None and self.bday > now:
            self._add_error("US01", "Birthday %s occurs in the future" % (self.bday.strftime('%Y-%m-%d')))
        elif self.death is not None:
            if self.death > now:
                self._add_error("US01", "Death %s occurs in the future" % (self.death.strftime('%Y-%m-%d')))
            # Death before birth
            if self.death < self.bday:
                self._add_error("US03", "Died %s before born %s" % (self.death.strftime('%Y-%m-%d'), self.bday.strftime('%Y-%m-%d')))
            # Died over 150 years old
            if abs(self.death.year - self.bday.year) > 150:
                self._add_error("US07", "More than 150 years old at death - Birth %s: Death %s" % (self.bday.strftime("%Y-%m-%d"), self.death.strftime("%Y-%m-%d")))
        # Over 150 and still alive        
        elif abs(now.year - self.bday.year) > 150:
            self._add_error("US07", "More than 150 years old - Birth %s" % (self.bday.strftime("%Y-%m-%d")))

    def print_errors(self):
        for i in self.errors:
            print(i, file=sys.stderr)

    def print_anomalies(self):
        for i in self.anomalies:
            print(i, file=sys.stderr)            

    @staticmethod
    def instance_from_dict(info_dict):
        id = info_dict['INDI']
        name = info_dict['NAME']
        gender = info_dict['SEX']
        bday = datetime.datetime.strptime('01 Jan 1900', '%d %b %Y')

        if 'BIRT' in info_dict.keys():
            try:
                #abbrev_to_num = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
                #check_valid = info_dict['BIRT']
                #check_valid = check_valid.split(" ")
                #check_valid[1] = str(abbrev_to_num[check_valid[1]])
                #check_valid = "-".join(check_valid)
                if(US24(info_dict['BIRT'])):
                    bday = datetime.datetime.strptime(info_dict['BIRT'], '%d %b %Y')
                else:
                    print('Invalid Date: US24: %s' % info_dict['BIRT'], file=sys.stderr)
            except:
                print("ERROR: US24: INVALID DATE: %s" % info_dict['BIRT'], file=sys.stderr)
                bday = datetime.datetime.strptime('01 Jan 1900', '%d %b %Y')
        else:
            bday = datetime.datetime.strptime('01 Jan 1900', '%d %b %Y')

        today = datetime.datetime.today()
        
        #US27 - Displaying age of individual based on today's date.
        age = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))
        if 'FAM' in info_dict:
            families = info_dict['FAM']
        else:
            families=[]
        alive = True
        death = None

        if 'DEAT' in info_dict.keys():
            alive = False
            death = datetime.datetime.strptime(info_dict['DEAT'], '%d %b %Y')
        return Individual(id, name, gender, bday, age, families, alive, death=death)

    def add_child(self, child):
        self.children.append(child)

    def add_children(self, children):
        for child in children:
            self.add_child(child)
            
    def add_spouse(self, sp):
        self.spouses.append(sp)

    def set_spouse(self, spouse):
        if spouse not in self.spouses:
            self.spouses.append(spouse)

    def to_row(self):
        ret = []

        ret.append(self.id)
        ret.append(self.name)
        ret.append(self.gender)
        ret.append(self.bday.strftime('%Y-%m-%d'))
        ret.append(self.age)

        ret.append('True' if self.alive else 'False')

        ret.append('NA' if self.alive else self.death.strftime('%Y-%m-%d'))

        if len(self.children) > 0:
            ret.append("{%s}" % ','.join(list(map(lambda x: x.id, self.children))))
        else:
            ret.append('NA')

        if len(self.spouses) > 0:
            ret.append("{%s}" % ','.join(list(map(lambda x: x.id, self.spouses))))
        else:
            ret.append('NA')
        return ret

    def __str__(self):
        return str(dict(zip(Individual.row_headers, self.to_row())))
