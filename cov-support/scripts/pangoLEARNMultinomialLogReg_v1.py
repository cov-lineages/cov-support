import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
from datetime import datetime
import joblib
import sys


# file with lineage assignments
lineage_file = sys.argv[1]
# file with sequences
sequence_file = sys.argv[2]
# how much of the data will be used for testing, instead of training
testingPercentage = sys.argv[3]

dataList = []

snpDict = dict()
keepDict = dict()
# dict for lookup efficiency
indiciesToRemove = dict()


# small class for storing/comparing vector objects
# useful for finding snps
class VectorObject:
	def __init__(self, vector):
		self.vector = vector

	def equals(self, vector):
		for i in range(len(vector.vector)):
			if vector.vector[i] != self.vector[i]:
				return False

		return True


# geneate a one-hot encoded vector for a particular nucleotide
def getOneHotEncoding(char):
	# ATCGN-

	if char == "A":
		return VectorObject([1, 0, 0, 0, 0, 0])
	elif char == "T":
		return VectorObject([0, 1, 0, 0, 0, 0])
	elif char == "C":
		return VectorObject([0, 0, 1, 0, 0, 0])
	elif char == "G":
		return VectorObject([0, 0, 0, 1, 0, 0])
	elif char == "-":
		return VectorObject([0, 0, 0, 0, 0, 1])
	else:
		return VectorObject([0, 0, 0, 0, 1, 0])


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
						idToSeq[currentId] = currentSeq

					# the new id
					currentId = line[1:]
					# clearing the sequence
					currentSeq = ""

				else:
					# incrementally collecting the sequence
					currentSeq = currentSeq + line

		# one left at the end of the file
		if currentId and currentSeq:
			idToSeq[currentId] = currentSeq

	# close the file
	f.close()

	# for each sequence id
	for key in idToSeq.keys():

		# create a new dataLine
		dataLine = []

		# add the lineage
		dataLine.append(idToLineage[key])

		if "lineage" in line:
			# this is the header line. don't do anything.
			print("skipping header")
		else:
			# for each character in the sequence
			for char in idToSeq[key]:
				# get the one hot encoding and append it to the line
				dataLine.append(getOneHotEncoding(char))
			# add the line ot the dataList
			dataList.append(dataLine)


# find columns in the data list which always have the same value
def findColumnsWithoutSNPs():
	# for each index in the length of each sequence
	for index in range(len(dataList[0])):
		keep = False

		# loop through all lines
		for line in dataList:
			# if there is a difference somewhere, then we want to keep it
			if index == 0 or not dataList[0][index].equals(line[index]):
				keep = True

		# otherwise, save it to remove this index from the data later
		if not keep:
			indiciesToRemove[index] = True


# remove columns from the data list which don't have any SNPs. We do this because
# these columns won't be relevant for a logistic regression which is trying to use
# differences between sequences to assign lineages
def removeIndices(indiciesToRemove):
	# instantiate the final list
	finalList = []

	# initial headers, a list of all of the indicies in the sequences
	headers = list(range(len(dataList[0])))

	# will hold the final headers for the model
	finalHeaders = []

	# while the dataList isn't empty
	while len(dataList) > 0:

		# pop the first line
		line = dataList.pop(0)

		# initialize the finalLine
		finalLine = []

		# for each index in the line
		for index in range(len(line)):
			# if its the first index, then that's the lineage assignment, so keep it
			if index == 0:
				finalLine.append(line[index])
			# otherwise only keep it if its not in indicesToRemove
			elif index not in indiciesToRemove:
				finalLine.extend(line[index].vector)

		# save the finalLine to the finalList
		finalList.append(finalLine)

	# getting the indices to remove as a list so we can sort it
	indicies = list(indiciesToRemove.keys())
	# sorting the list
	indicies.sort()

	# for each index (after sorting them backwards so we can remove them from highest to 
	# lowest to prevent index offset problems)
	for i in reversed(indicies):
		# remove the relevant header
		headers.pop(i)

	# then, for each remaining header
	for i in headers:
		# the first one is just "lineage" since we know its the lineage assignment
		if i == 0:
			finalHeaders.append("lineage")
		# otherwise, we actually need several headers for each genomic location because of the one-hot encoding
		else:
			vector = [str(i) + "-A", str(i) + "-T", str(i) + "-C", str(i) + "-G", str(i) + "-N", str(i) + "-gap"]
			finalHeaders.extend(vector)

	# return
	return finalList, finalHeaders


print("reading in data " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"));

readInAndFormatData()

print("processing snps, formatting data " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"));

findColumnsWithoutSNPs()

dataList, headers = removeIndices(indiciesToRemove)

pima = pd.DataFrame(dataList, columns=headers)

# get the list of column names in list format
# apparently there is a built in function in pandas letting you get the column header names this way
feature_cols = list(pima)

print("setting up training " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"));

# remove the last column from the data frame. This is because we are trying to predict these values.
h = feature_cols.pop(0)
X = pima[feature_cols]
y = pima[h]

# separate the data frame into testing/training data sets. 25% of the data will be used for training, 75% for test.
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=testingPercentage,random_state=0)

print("training " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"));

# instantiate the mulinomial logistic regression
logreg = LogisticRegression(multi_class='multinomial',solver ='newton-cg')

# fit the model
logreg.fit(X_train,y_train)

print("testing " + datetime.now().strftime("%H:%M:%S"));

# classify the test data
y_pred=logreg.predict(X_test)
# get the scores from these predictions
y_scores = logreg.predict_proba(X_test)

print("generating statistics " + datetime.now().strftime("%H:%M:%S"));

#print the confusion matrix
print("--------------------------------------------")
print("CONFUSION MATRIX")
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
print(cnf_matrix)

print("--------------------------------------------")
print("Classification report")
print(metrics.classification_report(y_test, y_pred, digits=3))

print("--------------------------------------------")
print("Overall Stats")

print("accuracy: " + str(accuracy_score(y_test, y_pred)))
print("f1 score: " + str(f1_score(y_test, y_pred, average="macro")))
print("precision: " + str(precision_score(y_test, y_pred, average="macro")))
print("recall: " + str(recall_score(y_test, y_pred, average="macro")))

# save the model files to compressed joblib files
# using joblib instead of pickle because these large files need to be compressed
joblib.dump(logreg, "panglolearnMultinomialLogReg.joblib", compress=9)
joblib.dump(headers, "panglolearnMultinomialLogReg_headers.joblib", compress=9)
