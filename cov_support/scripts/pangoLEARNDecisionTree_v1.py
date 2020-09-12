import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix, make_scorer
from datetime import datetime
import joblib
import sys
from sklearn.model_selection import cross_val_score


# file with lineage assignments
lineage_file = sys.argv[1]
# file with sequences
sequence_file = sys.argv[2]
# how much of the data will be used for testing, instead of training
testing_percentage = float(sys.argv[3])

# data storage
dataList = []
# dict for lookup efficiency
indiciesToKeep = dict()

# function for handling weird sequence characters
def clean(x):
    if x == 'A' or x == 'C' or x == 'T' or x == '-':
    	return x
    return 'N'

def readInAndFormatData():
	idToLineage = dict()
	idToSeq = dict()

	# create a dictionary of sequence ids to their assigned lineages
	with open(lineage_file, 'r') as f:
		for line in f:
			line = line.strip()

			split = line.split(",")

			idToLineage[split[0]] = split[1]

	# close the file
	f.close()

	# create a dictionary of sequence ids to their assosciated sequence strings
	with open(sequence_file) as f:
		currentId = False
		currentSeq = ""

		for line in f:
			if "taxon,lineage" not in line:
				line = line.strip()

				if ">" in line:
					# starting new entry, saving the old one
					if currentId and currentSeq:
						#idToSeq[currentId] = currentSeq

						key = currentId
						dataLine = []

						# add the lineage
						if key in idToLineage:

							dataLine.append(idToLineage[key])

							if "lineage" in line:
								# this is the header line. don't do anything.
								print("skipping header")
							else:
								# for each character in the sequence
								for char in currentSeq:
									# get the one hot encoding and append it to the line
									dataLine.append(clean(char))
								# add the line ot the dataList
								dataList.append(dataLine)
						else:
							print("Unable to find the lineage classification for: " + key)

					# the new id
					currentId = line[1:]
					# clearing the sequence
					currentSeq = ""

				else:
					# incrementally collecting the sequence
					currentSeq = currentSeq + line

		# one left at the end of the file
		if currentId and currentSeq:
			key = currentId
			dataLine = []

			# add the lineage
			if key in idToLineage:

				dataLine.append(idToLineage[key])

				if "lineage" in line:
					# this is the header line. don't do anything.
					print("skipping header")
				else:
					# for each character in the sequence
					for char in currentSeq:
						# get the one hot encoding and append it to the line
						dataLine.append(clean(char))
					# add the line ot the dataList
					dataList.append(dataLine)
			else:
				print("Unable to find the lineage classification for: " + key)

	# close the file
	f.close()


# find columns in the data list which always have the same value
def findColumnsWithoutSNPs():
	# for each index in the length of each sequence
	for index in range(len(dataList[0])):
		keep = False

		# loop through all lines
		for line in dataList:
			# if there is a difference somewhere, then we want to keep it
			if index == 0 or not dataList[0][index] == line[index]:
				keep = True
				break

		# otherwise, save it
		if keep:
			indiciesToKeep[index] = True


# remove columns from the data list which don't have any SNPs. We do this because
# these columns won't be relevant for a logistic regression which is trying to use
# differences between sequences to assign lineages
def removeOtherIndices(indiciesToKeep):
	# instantiate the final list
	finalList = []

	indicies = list(indiciesToKeep.keys())
	indicies.sort()

	# while the dataList isn't empty
	while len(dataList) > 0:

		# pop the first line
		line = dataList.pop(0)
		seqId = line.pop(0)

		# initialize the finalLine
		finalLine = []

		for index in indicies:
			if index == 0:
				# if its the first index, then that's the lineage assignment, so keep it
				finalLine.append(seqId)
			else:
				# otherwise keep everything at the indices in indiciesToKeep
				finalLine.extend(line[index])

		# save the finalLine to the finalList
		finalList.append(finalLine)

	# return
	return finalList


print("reading in data " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True);

readInAndFormatData()

print("processing snps, formatting data " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True);

findColumnsWithoutSNPs()

dataList = removeOtherIndices(indiciesToKeep)

# headers are the original genome locations
headers = list(indiciesToKeep.keys())
headers[0] = "lineage"

print("setting up training " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True);

pima = pd.DataFrame(dataList, columns=headers)

# nucleotide symbols which can appear
categories = ['A', 'C', 'G', 'T', 'N', '-']

# one hot encoding of all headers other than the first which is the lineage
dummyHeaders = headers[1:]

# add extra rows to ensure all of the categories are represented, as otherwise 
# not enough columns will be created when we call get_dummies
for i in categories:
	line = [i] * len(dataList[0])
	pima.loc[len(pima)] = line

# get one-hot encoding
pima = pd.get_dummies(pima, columns=dummyHeaders)

# get rid of the fake data we just added
pima.drop(pima.tail(len(categories)).index, inplace=True)

feature_cols = list(pima)

# remove the last column from the data frame. This is because we are trying to predict these values.
h = feature_cols.pop(0)
X = pima[feature_cols]
y = pima[h]

# separate the data frame into testing/training data sets. 25% of the data will be used for training, 75% for test.
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=testing_percentage,random_state=0)

print("training " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True);

# instantiate the random forest with 1000 trees
dt = DecisionTreeClassifier()

# fit the model
dt.fit(X,y)

print("testing " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True);

# classify the test data
y_pred=dt.predict(X_test)

print(y_pred)

# get the scores from these predictions
y_scores = dt.predict_proba(X_test)

print("generating statistics " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), flush=True);

#print the confusion matrix
print("--------------------------------------------")
print("Confusion Matrix")
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
print(cnf_matrix)

print("--------------------------------------------")
print("Classification report")
print(metrics.classification_report(y_test, y_pred, digits=3))

# save the model files to compressed joblib files
# using joblib instead of pickle because these large files need to be compressed
joblib.dump(dt, "pangolearnDecisionTree_v1.joblib", compress=9)
joblib.dump(headers, "pangolearnDecisionTree_v1_headers.joblib", compress=9)

print("model files created", flush=True)

# this method is used below when running 10-fold cross validation. It ensures
# that the per-lineage statistics are generated for each cross-fold
def classification_report_with_accuracy_score(y_true, y_pred):
	print("--------------------------------------------")
	print("Crossfold Classification Report")
	print(metrics.classification_report(y_true, y_pred, digits=3))
	return accuracy_score(y_true, y_pred)

# optionally, run 10-fold cross validation (comment this out if not needed as it takes a while to run)
cross_validation_scores = cross_val_score(dt, X=X, y=y, cv=10, scoring=make_scorer(classification_report_with_accuracy_score))
