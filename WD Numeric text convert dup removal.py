# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 16:35:43 2020

@author: andrew.white
"""
import pprint
import os
import pandas as pd
from docx import Document

mydir = r"C:\Users\andrew.white\Documents\Lists\WD Numeric"
docs = os.listdir(mydir)
records = {}

record_names = set()
for file in docs:
    if file.endswith(".docx"):

        docx = Document(os.path.join(mydir, file))
    else:
        continue
# TODO None of this works, not sure how to stucture/update the dict
    for ip, para in enumerate(docx.paragraphs, 1):
        for ir, run in enumerate(para.runs, 1):
            if run.bold:
                try:
                    para.text.index(": ")
                    record_names.add(para.text)
                except ValueError:
                    continue
        for p in record_names:
            field = p.split(": ", 1)
            u = {
                field[0]: field[1]
                }
            if file in records:
                records.update({file: [u]})
            else:
                records[file] = [u]
pprint.pprint(records)
