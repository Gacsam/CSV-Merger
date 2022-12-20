# CSV-Merger

# !DISCONTINUED! Yapped has been last updated for Elden Ring Reforged 1.04, use DSMapStudio instead, which has the merging functionality built in.

for Elden Ring

Guide

It is much more efficient on the computer if you know exactly which CSV files have been edited!
1. Use Yapped to export files you're wanting to edit, mass export will make it take longer as it will check every single file for new entries. This includes
   - Vanilla regulation.bin (current files are from 1.04 version)
   - Every mod regulation.bin
   - - When you export a mod csv file, import it right back in to test for errors, see below.
2. Place the vanilla csv files into 0.Base_CSVs
3. Place modded csv files into 1.Mod_CSVs
   - Place each of them in a separate folder - ideally named after the mod - the script uses folder name as Mod ID
4. Run the .exe file, ignore the virus warning, it's caused by the script being new and not in the database.
   - You probably want to stretch the console sideways because of the word wrapping.
5. Follow instructions, pay attention and when editing IDs - note them down and keep track of which ones you have already taken.

Errors

Not sure if Yapped or the game itself is causing the weird spacing in the csv files, such as Elden Ring Reforged﻿'s, but worry not, it's easily fixable.
1. Open the csv file in Notepad, right click -> edit.
2. Pick a line that starts with a semicolon ; and place your text cursor on the right of it
3. Press left arrow twice, so that you select both the semicolon and the spacing, so that your text cursor is on the line above
4. Press CTRL+H to initiate Search and Replace, put just a semicolon ; in the replacement target field.
5. Press Replace All. Your file should be lacking any weird spacing now, and can be found in 2.Merged_CSVs
6. Place the merged CSV into Yapped's folder and import it back in.
Notepad++ offers the option to open multiple files at once, as well as replacing in all open files, allowing you to do it just once.

Sometimes there's an Index error when importing into Yapped, this is caused by multiple items having the same index, such as is issue with Unlocked Unique Skills. The merger script does point those out and attempt to fix those.
