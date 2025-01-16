#test
import csv
from datetime import datetime, date
import time
import pandas as pd

print("writing data")
fileName = 'experiment/outputs/exp1_'+str(date.today())+'.csv'
print(fileName)

newDf = {}
newDf['battery'] = [420]
newDf['ac_out'] = [69]

newDf = pd.DataFrame.from_dict(newDf)

try:
    with open(fileName) as csvfile:
        df = pd.read_csv(fileName)
        df = pd.concat([df,newDf], ignore_index = True)
        #df = df.append(newDf, ignore_index = True)
        df.to_csv(fileName, sep=',',index=False)
except Exception as e:
    print(e)
    newDf.to_csv(fileName, sep=',',index=False)