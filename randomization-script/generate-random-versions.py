import os
import re
import glob
import random
import subprocess
import fnmatch


def extractQuestions(texString):
	'''Process a tex file and split it [beginning, questionsBlock, end] 
	to extract the questions'''
	beginning,questions,end = splitAtDelimiters(texString, ["\\begin{questions}", "\\end{questions}"])
	beginning = beginning + '\n\\begin{questions}'
	end = '\\end{questions}\n'+end
	questions = splitAtDelimitersAndKeep(questions, ["\\question"])
	return [beginning, questions, end]

def splitAtDelimiters(str, delimitersList):
	'''Split a string at multiple delimiters defined in a list'''
	regexPattern = '|'.join(map(re.escape, delimitersList))
	return re.split(regexPattern, str)

def splitAtDelimitersAndKeep(str, delimitersList, verbose=False):
	'''Split a string at multiple delimiters defined in a list and return 
	each element with the corresponding delimiter kept in front'''
	regexPattern = '|'.join(map(re.escape, delimitersList))
	allHits = re.split(f"({regexPattern})", str)
	finalList = []
	delimiters = list(map(re.escape, delimitersList))
	for i in range(len(allHits)):
		# starting from last element to first
		pos = len(allHits)-1-i
		elem = allHits[pos]
		if (re.escape(elem) in delimiters) & (pos+1<len(allHits)):
		    finalList.insert(0, elem+allHits[pos+1])
		elif (pos==0) & (re.escape(elem) not in delimiters):
			if verbose:
				print(f"The first element didn't match anything.\nElement: {elem}")
	return finalList


def ensureDir(filePath):
	directory = os.path.dirname(filePath)
	if not os.path.exists(directory):
	    os.makedirs(directory)

def saveFile(texString, fileName, folder):
	basename = os.path.basename(fileName)
	ensureDir(f"{folder}/{basename}")
	with open(f"{folder}/{basename}", "w") as f:
	    f.write(texString)
	    f.close()

###########################
## Update figure URLs in file if figures in another folder
def getUpdatedFigUrl(figUrl, PathToFolderWithFigs):
	return f"{PathToFolderWithFigs}/{figUrl}"

def getAllFigUrls(texString, nameToMatch, extension):
	figURLinFile = findAllFigs(nameToMatch, extension, texString)
	return [filename[1:-1] for filename in figURLinFile]

def findAllFigs(figureNamePattern, extensionPattern, texString):
	regex = r'\{[^}]*' + figureNamePattern + r'[^}]*' + extensionPattern + r'[^}]*}'
	match = re.findall(regex, texString)
	return match

def updateAllFigUrl(texString, nameToMatch, extension, pathToFolderWithFigs):
	allFigs = getAllFigUrls(texString, nameToMatch, extension)
	newPaths = [getUpdatedFigUrl(fig, pathToFolderWithFigs) for fig in allFigs]
	for figPath,figNewPath in zip(allFigs, newPaths):
		print(figPath, figNewPath)
		beginning,end = texString.split(figPath)
		newTexString = beginning + figNewPath + end
	return newTexString

#############################
## Randomize figure URLs in file
def randomizeFigures(figsToReplace=[], folderWithFigsOptions="./"):
	#if figures to randomly choose, do it first
	if len(figsToReplace)>0:
		for fig in figsToReplace:
			with open(texFile, 'rb') as f:
				text = f.read().decode('utf-8')
				text = replaceFigRandomly(text, fig, folderWithFigsOptions)
			with open(texFile, "w") as f:
				f.write(text)
				f.close()

# randomization of figure files
def getFigOptions(figureName, folder, pattern="-v"):
	name, extension = figureName.split(".")
	optionNames = glob.glob(f"{folder}/{name}{pattern}*.{extension}")
	return optionNames

def findFigureUrl(figure, texString):
	regex = r'\{[^}]*' + figure + r'[^}]*}'
	match = re.findall(regex, texString)[0]
	return match

def replaceFigRandomly(texString, figure, folderWithOptions):
	options = getFigOptions(figure, folderWithOptions)
	figURLinFile = findFigureUrl(figure, texString)[1:-1]
	beginning,end = texString.split(figURLinFile)
	newFigURL = random.choice(options)
	newTexString = beginning + newFigURL + end
	return newTexString



def randomizeFigsAndQuestions(texString, figsToReplace=[], folderWithFigsOptions="./"):
	'''Randomize questions order as well as choices order for multiple choice questions
	as well as figures if optional figures are available'''

	######################
	# Randomize Figures
	# if figures to randomly choose, do it first
	if len(figsToReplace)>0:
		for fig in figsToReplace:
			texString = replaceFigRandomly(texString, fig, folderWithFigsOptions)

	######################
	# Randomize questions and answer order
	[beginningDoc, questions, endDoc] = extractQuestions(texString)
	# if multiple choice question, randomize choices order for each question
	for i,question in enumerate(questions):
		choicePattern = splitAtDelimiters(question, ["\\begin{choices}", "\\end{choices}"])
		if (len(choicePattern)>1) & (len(choicePattern)==3):
			start, choices, end = choicePattern
			start = start+'\n\\begin{choices}'
			end = '\\end{choices}\n'+end
			choices = splitAtDelimitersAndKeep(choices, ["\choice", "\CorrectChoice"])
			random.shuffle(choices)
			questions[i] = "\n".join([start]+choices+[end])
		elif len(choicePattern) == 1:
			continue
		else:
			print(f"Error in length of choicePattern: {len(choicePattern)}")
			break

	# add minipage environment to each question to prevent page break in question
	questions = ["\n".join(["\\begin{minipage}{\linewidth}\n", question, "\\end{minipage}"]) for question in questions]

	# randomize question order
	random.shuffle(questions)
	finalTex = "\n".join([beginningDoc]+questions+[endDoc])
	return finalTex


def processFileAndSave(texFile, outputName, outputFolder, figsToReplace=[], folderWithFigsOptions="./",
											 updateFigPath={"needed": False, "nameToMatch": "fig", "extension": "pdf", "pathToFolderWithFigs": "./"}):
	# 1- open file
	with open(texFile, 'rb') as f:
		texString = f.read().decode('utf-8')
	# 2- update paths of all figs in file if necessary
	if updateFigPath["needed"]:
		texString = updateAllFigUrl(texString, updateFigPath["nameToMatch"], updateFigPath["extension"], updateFigPath["pathToFolderWithFigs"])
	# 3- process file
	texString = randomizeFigsAndQuestions(texString, figsToReplace=figsToReplace, folderWithFigsOptions=folderWithFigsOptions)
	# 4- save file
	saveFile(texString, outputName, outputFolder)
	# 5- log some info
	print(f"file {texFile} processed and randomized!\nThe randomized version has been saved at {outputFolder}/{outputName}\n")
	return

def compileAllLatexFilesInFolder(folder, nCompilations=1):
	filesToCompile = glob.glob(f"{folder}/*.tex")
	for file in filesToCompile:
		for i in range(nCompilations): # in case several compilations are necessary
			subprocess.call(['pdflatex', '-output-directory', folder, file], shell=False) # shell should be set to False


def cleanUpFolderAndKeep(folder, tupleOfExtensionsToKeep):
	fileList = os.listdir(folder)
	for filename in fileList:
		if filename.endswith(tupleOfExtensionsToKeep): #if filename.endswith(('.pdf', '.tex')):
			continue
		else:
			os.remove(f"{folder}/{filename}")


if __name__ == '__main__':
	
	nVersions = 10 # number of different versions to generate
	inputFolder = "../master-file/latex-files"
	outputFolder = "outputRandom"

	files = glob.glob(f"{inputFolder}/*.tex")
	

	# ONLY FIGURE fig0.pdf will be randomized
	for texFile in files:
		basename = os.path.basename(texFile)
		name, extension = basename.split(".")
		for i in range(nVersions):
			outputName = f"{name}-v{i}.{extension}"
			processFileAndSave(texFile, outputName, outputFolder, figsToReplace=["fig0.pdf"], folderWithFigsOptions="../master-file/figs", 
				updateFigPath={"needed": True, "nameToMatch": "fig", "extension": "pdf", "pathToFolderWithFigs": "../master-file/figs"})

	# compile latex files
	# need to compile twice to update grading table
	compileAllLatexFilesInFolder(outputFolder, nCompilations=2)
	
	# clean up latex generated files
	cleanUpFolderAndKeep(outputFolder, ('.pdf'))
	

	print("All done!")

