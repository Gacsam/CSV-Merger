import os
import glob
import shutil

import pandas as pd

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

pd.set_option("display.max_rows", 1000)
pd.set_option("display.max_columns", 1000)
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


def FoundConflict(modFiles, conflictItemID, massOverwrite=False, overwriteAll=False):
    targetID = 0
    if massOverwrite:
        if overwriteAll:
            targetID = conflictItemID
        else:
            targetID = conflictItemID + 1
    else:
        conflictUserInput = GetUserInputZero("Select which - 0 or 1 - to keep: ")
        if conflictUserInput:
            targetID = conflictItemID + 1
        else:
            targetID = conflictItemID
    modFiles.drop(targetID, inplace=True)


def SearchForDuplicatesInFile(modFiles, modCount):
    indexedModFiles = modFiles.reset_index()
    overwriteFiles = False
    massEdit = False
    overwriteAll = False
    noConflictFound = True
    # last means the first copy is true, check by row id that is the index
    for itemID, fileAlreadyExists in enumerate(modFiles.index.duplicated(keep="last")):
        if fileAlreadyExists:
            if noConflictFound:
                overwriteFiles = GetUserInputZero(
                    "Conflicts found, would you like to solve them? 0 - Overwrite. 1 - Solve. ")
                if overwriteFiles:
                    massEdit = GetUserInputZero(
                        "Would you like to apply this to all files? 0 - Yes. 1 - No. ")
                    if massEdit:
                        overwriteAll = GetUserInputZero(
                            "0 - Overwrite all. 1 - Keep all. ")
                noConflictFound = False
            modConflict = modFiles.iloc[itemID:itemID + 2, :].reset_index().set_index("Row Name").T \
                .drop_duplicates(keep=False).T.reset_index().set_index("Row ID").reset_index()
            if overwriteFiles:
                if massEdit:
                    if overwriteAll:
                        FoundConflict(indexedModFiles, itemID, True, True)
                    else:
                        FoundConflict(indexedModFiles, itemID, True, False)
                else:
                    FoundConflict(indexedModFiles, itemID)
            else:
                print(modFiles.iloc[itemID - 25:itemID + 25, :2])
                print("Found conflicts: ")
                print(modConflict)
                anyFreeRows = GetUserInputZero(
                    "Do you see any free Row ID? Are items different? 0 - Yes, 1 - No ")
                if anyFreeRows:
                    newID = input("Please enter the new Row ID for <" + indexedModFiles.at[itemID, "Row Name"] + ">")
                    indexedModFiles.at[itemID, "Row ID"] = int(newID)
                else:
                    FoundConflict(indexedModFiles, itemID)
    # Clear_Screen()
    return indexedModFiles


def Clear_Screen():
    # for mac and linux(here, os.name is 'posix')
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        # for windows platform
        _ = os.system('cls')
    # print out some text


def MergeMods(vanillaFile, onlyModdedItems=False):
    baseFileName = os.path.basename(vanillaFile)
    newMods = glob.glob(os.path.join(".\\1.Mod_CSVs\\**", baseFileName), recursive=True)
    # if any mod files are found
    if newMods:
        # index by Row Name so we don't have to worry about just different names in exact same files
        baseCSV = pd.read_csv(vanillaFile, sep=";", index_col=False,
                              converters={"Row ID": int, "Row Name": str}).set_index("Row Name")
        allModdedFiles = pd.DataFrame()
        # go through each individual mod
        modCount = 0
        for newMod in newMods:
            # Clear_Screen()
            # get mod name
            modName = os.path.basename(os.path.dirname(newMod))
            # read mod CSV
            modCSV = pd.read_csv(newMod, sep=";", index_col=False,
                                 converters={"Row ID": int, "Row Name": str}).set_index("Row Name")
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
            print("Adding entries from folder <" + modName + "> to  <" + baseFileName + ">")
            # search for duplicates
            allModdedFiles = SearchForDuplicatesInFile(allModdedFiles, modCount)
            # rename index back to Row ID
            allModdedFiles = allModdedFiles.rename(columns={"index": "Row ID"}).set_index("Row ID")
            modCount = modCount + 1
        # overwrite Mod ID with Row ID as our index

        allModdedFiles = SetNewIndex(allModdedFiles, "ModID").set_index("Row ID")
        # set row name as index again to drop vanilla files
        allModdedFiles = SetNewIndex(allModdedFiles.sort_index(), "Row Name")
        mergedCSV = allModdedFiles
        if not onlyModdedItems:
            # merge new files to the base csv
            mergedCSV = pd.concat([baseCSV, allModdedFiles])
            # remove duplicates from base, keep new ones
            mergedCSV = mergedCSV.drop_duplicates(subset=["Row ID"], keep="last")
        # put Row ID back as our index
        mergedCSV = SetNewIndex(mergedCSV, "Row ID")
        # let it sort itself out
        mergedCSV = mergedCSV.sort_index()
        # and export to a file

        if not mergedCSV.empty:
            mergedCSV.to_csv(os.path.join(mergeDir, baseFileName), sep=";", index=True)


if __name__ == "__main__":
    baseList = glob.glob(".\\0.Base_CSVs\\*.csv")
    mergeDir = os.path.join(os.path.basename(__file__), "..\\2.Merged_CSVs")
    # check if base files exist
    onlyModFiles = not GetUserInputZero(
        "How do you want your CSV formatted? 0 - Ready for regulation.bin, 1 - List only edited entries: ")
    if baseList:
        for baseFile in baseList:
            MergeMods(baseFile, onlyModFiles)
    else:
        input("No base file found, press any key to exit")
    input("Merging complete, press any key to continue")
