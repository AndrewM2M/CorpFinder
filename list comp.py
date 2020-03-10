# -*- coding: utf-8 -*-
"""
Fun with list comperhentions.

Created on Mon Feb 24 10:09:14 2020

@author: andrew.white
"""
import pprint
import os
import pandas as pd
from docx import Document


mydir = r"C:\Users\andrew.white\Documents\Lists\WD Numeric"
docs = os.listdir(mydir)
Sources = set()
records = []
columns = {"Source"}
rec_dict = {"Source": []}
idx = 0

for file in docs:
    bold_list = set()
    record_values = set()
    if file.endswith(".docx"):
        docx = Document(os.path.join(mydir, file))
        Sources.add(file)
    else:
        continue
    for para in docx.paragraphs:
        bold_text = {para.text for run in para.runs if run.text.find(": ")}
        if len(bold_text) > 0:
            bold_list = bold_list.union(bold_text)
    for feilds in bold_list:
        idx = idx+1
        c = feilds.split(": ", 1)[0].strip()
        c = c.rstrip(":.?,")
        try:
            v = feilds.split(": ", 1)[1].strip()
        except IndexError:
            v = None
        columns.add(c)
        record_values.add(v)
        records.append((idx, "Source", file))
        records.append((idx, c, v))
pprint.pprint(records)
df = pd.DataFrame.from_records(records)
print(df.groupby(df[0]))
# df.to_csv(os.path.join(mydir, "results.csv"))

