import os
import glob
import shutil

import pandas as pd

pd.set_option("display.max_rows", 1000)
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1000)


def GetUserInputZero(string=""):
    variable = None
    acceptedVals = ["0", "1"]
    while variable not in acceptedVals:
        variable = input(string)
    return int(variable) == 0


def GiveModID(mergedFiles, currentModName):
    return mergedFiles.reset_index().reset_index().rename(columns={"index": "ModID"}) \
        .assign(ModID=currentModName).set_index("Row ID")


def SortByRowID(files):
    return RemoveDoubleIndex(CreateDoubleIndex(files).sort_values(["Row ID", "index"]))


def CreateDoubleIndex(files):
    return files.reset_index().reset_index()


def RemoveDoubleIndex(files):
    return files.set_index("index").reset_index(drop=True).set_index("Row ID")


def SetNewIndex(files, index_name):
    return files.reset_index().set_index(index_name)


def FoundConflict(modFiles, conflictItemID):
    conflictUserInput = GetUserInputZero("Found conflicts, select which - 0 or 1 - to keep: ")
    if conflictUserInput:
        modFiles.drop(conflictItemID + 1, inplace=True)
    else:
        modFiles.drop(conflictItemID, inplace=True)


def SearchForDuplicates(modFiles):
    indexedModFiles = modFiles.reset_index()
    # last means the first copy is true, check by row id that is the index
    for itemID, fileAlreadyExists in enumerate(modFiles.index.duplicated(keep="last")):
        if fileAlreadyExists:
            modConflict = modFiles.iloc[itemID:itemID + 2, :2]
            print()
            print(modConflict.reset_index().rename(columns={"index": "Row ID"}))
            userInput = GetUserInputZero(
                "Found conflicts, would you like to try to solve them? 0 - Yes, 1 - Overwrite instead ")
            if userInput:
                print(modFiles.iloc[itemID - 25:itemID + 25, :2])
                userInput = GetUserInputZero(
                    "Do you see any free Row ID? 0 - Yes, 1 - No ")
                if userInput:
                    newID = input("Please enter the new Row ID: ")
                    indexedModFiles.at[itemID, "Row ID"] = int(newID)
                else:
                    FoundConflict(indexedModFiles, itemID)
            else:
                FoundConflict(indexedModFiles, itemID)
    #Clear_Screen()
    return indexedModFiles


def Clear_Screen():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platfrom
        _ = os.system('cls')
    # print out some text


def MergeMods(vanillaFile):
    baseFileName = os.path.basename(vanillaFile)
    newMods = glob.glob(os.path.join(".\\1.Mod_CSVs\\**", baseFileName), recursive=True)
    # if any mod files are found
    if newMods:
        # index by Row Name so we don't have to worry about just different names in exact same files
        baseCSV = pd.read_csv(vanillaFile, sep=";", index_col=False).set_index("Row Name")
        allModdedFiles = pd.DataFrame()
        # go through each individual mod
        for newMod in newMods:
            # Clear_Screen()
            # get mod name
            modName = os.path.basename(os.path.dirname(newMod))
            # read mod CSV
            modCSV = pd.read_csv(newMod, sep=";", index_col=False).set_index("Row Name")
            # merge two base files to cancel each other out, this way we keep ONLY the edited files
            # rather than having a list of files that were edited along with their non-edited counterparts
            newModFiles = pd.concat([baseCSV, baseCSV, modCSV]).drop_duplicates(keep=False)
            del modCSV
            # give each mod their own unique ID
            newModFilesWithModID = GiveModID(newModFiles, modName)
            del newModFiles
            # concatenate files with mod ID
            allModdedFiles = pd.concat([allModdedFiles, newModFilesWithModID])
            del newModFilesWithModID
            # sort modded files by row ID
            allModdedFiles = SortByRowID(allModdedFiles)
            print("Added entries from folder <" + modName + "> to  <" + baseFileName + ">")
            # search for duplicates
            allModdedFiles = SearchForDuplicates(allModdedFiles)
            # rename index back to Row ID
            allModdedFiles = allModdedFiles.rename(columns={"index": "Row ID"}).set_index("Row ID")
        # overwrite Mod ID with Row ID as our index
        allModdedFiles = SetNewIndex(allModdedFiles, "ModID").set_index("Row ID")
        # set row name as index again to drop vanilla files
        allModdedFiles = SetNewIndex(allModdedFiles.sort_index(), "Row Name")
        # merge new files to the base csv
        mergedCSV = pd.concat([baseCSV, allModdedFiles])
        # remove duplicates from base, keep new ones
        mergedCSV = mergedCSV.drop_duplicates(subset=["Row ID"], keep="last")
        # put Row ID back as our index
        mergedCSV = SetNewIndex(mergedCSV, "Row ID")
        # let it sort itself out
        mergedCSV = mergedCSV.sort_index()
        # and export to a file
        mergedCSV.to_csv(os.path.join(mergeDir, baseFileName), sep=";", index=True)


if __name__ == "__main__":
    baseList = glob.glob(".\\0.Base_CSVs\\*.csv")
    mergeDir = os.path.join(os.path.basename(__file__), "..\\2.Merged_CSVs")
    # check if base files exist
    if baseList:
        for baseFile in baseList:
            MergeMods(baseFile)
    else:
        input("No base file found, press any key to exit")
    input("Merging complete, press any key to continue")
