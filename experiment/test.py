#test
import csv

print("writing data")
fileName = 'demandResponseController/experiments/outputs/exp1_'+str(datetime.date.today())+'.csv'
print(fileName)

newDf = {}
newDf['battery'] = 420
newDf['ac_out'] = 69

try:
    with open(fileName) as csvfile:
        df = pd.read_csv(fileName)
        df = pd.concat([df,newDf], ignore_index = True)
        #df = df.append(newDf, ignore_index = True)
        df.to_csv(fileName, sep=',',index=False)
except Exception as e:
    print(e)
    newDF.to_csv(fileName, sep=',',index=False)