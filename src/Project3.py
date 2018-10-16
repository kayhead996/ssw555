#!/usr/bin/env python
from Family import Family
from Individual import Individual
from prettytable import PrettyTable

"""project2.py SSW 555-WS Project 2 GEDCOM validator"""

__author__ = "Keyur Ved, Monica Razak, Jacob Ciesieleski, Bora Bibe"

import sys 

valid_tags = { 0: ["INDI", "FAM", "HEAD", "RLR", "NOTE", "TRLR"],
               1: ["NAME", "SEX", "BIRT", "DEAT", "FAMC", "FAMS", "MARR", "HUSB", "WIFE", "CHIL", "DIV"],
               2: ["DATE"]
            }

def validate(level, tag):
    return level in valid_tags.keys() and tag in valid_tags[level]

def process_tag(level, curr_dict, tag, arg):
    if tag == 'INDI':
        curr_dict = {'INDI': arg}
    else:
        if tag == "FAMS" or tag == "FAMC" or tag == "CHIL":
            if tag == "FAMS" or tag == "FAMC":
                tag = "FAM"
            arg = [arg]

            if tag in curr_dict:
                curr_dict[tag] += arg
            else:
                curr_dict[tag] = arg
        elif arg != '':
            curr_dict[tag] = arg

def process_file(file):
    individuals = []
    curr_indiv = {}
    families = []
    curr_fam = {}
    prev_tag = ""
    fam_process = False

    with open(file, "r") as f:
        for line in f:
            line_splt = line.split()
            line_splt = list(map(lambda x: x.strip(), line_splt))

            level = int(line_splt[0])
            tag = line_splt[1]
            arg = ""

            if len(line_splt) > 2:
                arg = ' '.join(line_splt[2:])

                if line_splt[2] == "INDI" or line_splt[2] == "FAM":
                    tag = line_splt[2]
                    arg = line_splt[1]

                    if level == 0 and tag == "FAM":
                        if curr_indiv != {}:
                            individuals.append(Individual.instance_from_dict(curr_indiv))
                            curr_indiv = {}
                            fam_process = True
                
            if validate(level, tag):
                if not fam_process:
                    if level == 0:
                        if curr_indiv != {}:
                            individuals.append(Individual.instance_from_dict(curr_indiv))
                        if tag == "INDI":
                            curr_indiv = {'INDI': arg}
                        else:
                            curr_indiv = {}
                    else:
                        if tag == "BIRT" or tag == "DEAT":
                            prev_tag = tag
                        elif tag == "DATE":
                            tag = prev_tag
                            prev_tag = ""
                    process_tag(level, curr_indiv, tag, arg)
                else:
                    if level == 0 and curr_fam != {}:
                        if 'CHIL' in curr_fam.keys():
                            children = curr_fam['CHIL']
                        curr_fam['CHIL'] = []

                        for indiv in individuals:
                            if indiv.id == curr_fam['HUSB']:
                                curr_fam['HUSB'] = indiv
                            elif indiv.id == curr_fam['WIFE']:
                                curr_fam['WIFE'] = indiv
                            elif indiv.id in children:
                                curr_fam['CHIL'].append(indiv)

                        families.append(Family.instance_from_dict(curr_fam))
                        if tag == "FAM":
                            curr_fam = {"FAM": arg}
                        else:
                            curr_fam = {}
                    else:
                        if tag == "MARR" or tag == "DIV":
                            prev_tag = tag
                        elif tag == "DATE":
                            tag = prev_tag
                            prev_tag = ""
                        process_tag(level, curr_fam, tag, arg)
                   
    return individuals, families
            
def run():
    if len(sys.argv) <= 1:
        exit("Required arg <filename> missing") 

    indivs, fams = process_file(sys.argv[1])

    indiv_table = PrettyTable()
    indiv_table.field_names = Individual.row_headers
    
    for indiv in indivs:
        indiv_table.add_row(indiv.to_row())
        indiv.print_errors()

    fam_table = PrettyTable()
    fam_table.field_names = Family.row_headers

    for fam in fams:
        fam_table.add_row(fam.to_row())
        fam.print_errors()
        fam.print_anomalies()

    print(indiv_table)
    print(fam_table)


if __name__ == "__main__":
    run()
