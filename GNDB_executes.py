#-------------------------------------------------------------
#
# Name:       GNDB_executes.py (This should only be called from GNDB.pyt)
# Purpose:    A python-tool to work with the "Greenlandic Names Data Base" (GNDB) and NIS.
# Author:     Martin Hvidberg
# e-mail:     mahvi@gst.dk, Martin@Hvidberg.net
# Created:    2014-09-16
# Copyright:  CopyLeft - I want my humble inventions to be freely available to others ...
# ArcGIS ver: 10.2.0
# Python ver: 2.7.3
#
# Error numbers strategy:
#    1xx : Fundamental program logic fails
#    2xx : Something 'fishy' with the input data ...
#
# History
#    Ver. 0.1.0 - Creating class GNDBruninTOC() 
#        Sceleton works, but no changes written to output, yet.
#        Obey Selection and obey Definition querries on input data. '141001/mahvi
#    Ver. 0.2.0 - Splitting execute() into seperate .py file
#
# ToDo
#    Look for XXX in the code
#
#-------------------------------------------------------------
        
# ====== Helper functions =====================================================

def CorrectNaming(mode, dicN):
    bNG = str(type(dicN["Name_NGL"]))=="<type 'unicode'>"
    if bNG:
        bNG = len(dicN["Name_NGL"])!=0
    bOG = str(type(dicN["Name_GL"]))=="<type 'unicode'>"
    if bOG:
        bOG = len(dicN["Name_GL"])!=0
    bDA = str(type(dicN["Name_DK"]))=="<type 'unicode'>"
    if bDA:
        bDA = len(dicN["Name_DK"])!=0
    bEN = str(type(dicN["Name_UK"]))=="<type 'unicode'>"
    if bEN:
        bEN = len(dicN["Name_UK"])!=0
    #arcEC.SetMsg("     GNDB the bool  : [NG,OG,DA,EN]"+str([bNG,bOG,bDA,bEN]),0)

    ### This section decides the rules for how 4 Potential names is transfered to 2 Place holders ###
    strN = ""   # Name
    strL = ""   # Local name
    numS = 999  # Return code. 0 = Success
    if mode == "Berit":
        if bNG: # If New Greenlandic name exists
            strN = dicN["Name_NGL"]
            if bDA: # If Danish name exists
                strL = dicN["Name_DK"]
            elif bEN: # If English name exists
                strL = dicN["Name_UK"]
            numS = 0
        elif bOG: # If Old Greenlandic name exists
            strN = dicN["Name_GL"]
            if bDA: # If Danish name exists
                strL = dicN["Name_DK"]
            elif bEN: # If English name exists
                strL = dicN["Name_UK"]
            numS = 0
        elif bDA: # If Danish name exists
            strN = dicN["Name_DK"]
            if bEN: # English name exists
                strL = dicN["Name_UK"]
            numS = 0
        elif bEN: # If English name exists
            strN = dicN["Name_UK"]
            numS = 0
        else:
            numS = 1

    lstCorrect = [numS,strN,strL]
    return lstCorrect


def encodeIfUnicode(strval):
    """Encode if string is unicode."""
    if isinstance(strval, unicode):
        return strval.encode('ISO-8859-1')
    return str(strval)

dic_NT = {"2" : "GNDB=2 S�",
            "3" : "GNDB=3 Fjord",
            "4" : "GNDB=4 Bugt",
            "5" : "GNDB=5 Hav",
            "6" : "GNDB=6 �",
            "7" : "GNDB=7 �gruppe",
            "8" : "GNDB=8 Sund",
            "9" : "GNDB=9 Kyst",
            "10" : "GNDB=10 Bredning",
            "11" : "GNDB=11 Vig",
            "12" : "GNDB=12 Sn�vring",
            "13" : "GNDB=13 Munding",
            "14" : "GNDB=14 Sk�r",
            "15" : "GNDB=15 Str�de",
            "17" : "GNDB=17 Banke",
            "21" : "GNDB=21 Isfjord",
            "27" : "GNDB=27 Nedlagt bygd",
            "50" : "GNDB=50 N�s/Pynt",
            "52" : "GNDB=52 Halv�",
            "57" : "GNDB=57 Klint",
            "60" : "GNDB=60 Fjeld",
            "61" : "GNDB=61 Skr�ning",
            "62" : "GNDB=62 Dal",
            "63" : "GNDB=63 Forbjerg",
            "65" : "GNDB=65 Kl�ft",
            "67" : "GNDB=67 Afsats",
            "68" : "GNDB=68 Nunatak",
            "70" : "GNDB=70 Slette",
            "101" : "GNDB=101 Bjergpas",
            "102" : "GNDB=102 Lavning",
            "110" : "GNDB=110 Isareal",
            "111" : "GNDB=111 Br�",
            "146" : "GNDB=146 Knold,Kovs",
            "166" : "GNDB=166 Sommerplads"}

def Make_NT(num_NT):
    if str(num_NT) in dic_NT.keys():
        return dic_NT[str(num_NT)]
    else:
        print "dic too short, missing:", str(num_NT)
        return "GNDB="+str(num_NT)    

# ====== Individual Tools Execute functions ===================================

def GNDBruninTOC_execute(parameters, messages):

    from datetime import datetime # for datetime.now()
    import arcpy
    import arcEC

    strExecuName  = "GNDBruninTOC_execute()"
    strExecuVer   = "0.2.0"
    strExecuBuild = "'1410229,1310"

    timStart = datetime.now()
        
    # *** Begin
    arcEC.SetMsg("Exec. '"+strExecuName+"' ver. "+strExecuVer+" build "+strExecuBuild,0)
    
    # *** Manage input parameters ***
    
    # ** Harvest strings from GUI
    
    arcEC.SetMsg("GUI said",0)
    try: # this will work when called from a .pyt
        strFC = parameters[0].valueAsText # FeatureClasse(s)
        strGN = parameters[1].valueAsText # GNDB point FC
        strMode = parameters[2].valueAsText # Mode (string)
        strOverwrite = parameters[3].valueAsText # Overwrite (string (boolean))
    except: # this will work when called from a .bxt, though __main__ below
        strFC = parameters[0] # FeatureClasse(s)
        strGN = parameters[1] # GNDB point FC
        strMode = parameters[2] # Mode (string)
        strOverwrite = parameters[3] # Overwrite (string (boolean))
    if strOverwrite.lower() == "true":
        bolOverwrite = True
    else:
        bolOverwrite = False
    arcEC.SetMsg(" Feature classe(s)  : "+strFC,0)
    arcEC.SetMsg(" GNDB table         : "+strGN,0)
    arcEC.SetMsg(" Mode               : "+strMode,0)
    arcEC.SetMsg(" Overwrite          : "+str(bolOverwrite),0)
    
    
    # *** Open Feature Layer(s) ***                
    arcEC.SetMsg("Open Feature Layer",0)
    
    # ** find Feature Layer & GNDB
    mxd = arcpy.mapping.MapDocument('CURRENT')
    #arcEC.SetMsg(" MXD: "+str(mxd),0)
    if (len(arcpy.mapping.ListDataFrames(mxd)) != 1):
        arcEC.SetMsg("Multiple Data frames... Picking the first one.", 1)
    daf = arcpy.mapping.ListDataFrames(mxd)[0] # Only first data frame is considered, others are ignored... Improve this later XXX
    
    # * find Layer
    #arcEC.SetMsg(" daf: "+str(daf),0)
    for lay_i in arcpy.mapping.ListLayers(mxd, "", daf): # list of Layers from the first frame in TOC
        if str(lay_i) in strFC:
            arcEC.SetMsg(" TOC input layer    : "+str(lay_i),0)
            lay_in = lay_i
    # XXX show number of records, and number of selected records...    
            
    # * find GNDB
    for lay_i in arcpy.mapping.ListLayers(mxd, "", daf): # list of Layers from the first frame in TOC
        if str(lay_i) in strGN:
            arcEC.SetMsg(" TOC GNDB           : "+str(lay_i),0)
            lay_gndb = lay_i
        
    del lay_i, daf, mxd # Keep lay_in and lay_gndb

    
    # *** Load GNDB to memory ***
    dic_GNDB = dict()
    arcpy.SelectLayerByAttribute_management (lay_gndb, "CLEAR_SELECTION") # Make sure no records are selected
    # Handled by the cursor # lay_gndb.definitionQuery = "TO_DATE IS NULL"  # Excluding obsolete records
    lst_fields = ["NID", "NAMETYPE", "GST_GL_name", "GST_DK_name", "GST_UK_name", "SHAPE@XY"]
    try:
        #with arcpy.da.SearchCursor(lay_gndb, lst_fields, "TO_DATE IS NULL and NAME_GREENLAND_NEW = 'Nuuk'") as cursor:
        with arcpy.da.SearchCursor(lay_gndb, lst_fields, "TO_DATE IS NULL") as cursor: # if TO_DATE != NULL then info is obsolete ...
            for row in cursor:
                dic_new = dict()
                dic_new["NameType"] = row[1]
                dic_new["Name_GL"] = row[2]
                dic_new["Name_DK"] = row[3]
                dic_new["Name_UK"] = row[4]
                dic_new["XY_tuple"] = row[5]
                #===============================================================
                # # Clean a little
                # if dic_new["Name_NGL"]:
                #     dic_new["Name_NGL"] = dic_new["Name_NGL"].split("(")[0].strip() # remove anything right of first '('
                # if dic_new["Name_GL"]:
                #     dic_new["Name_GL"] = dic_new["Name_GL"].split("(")[0].strip() # remove anything right of first '('
                # if dic_new["Name_DK"]:
                #     dic_new["Name_DK"] = dic_new["Name_DK"].split("(")[0].strip() # remove anything right of first '('
                # if dic_new["Name_UK"]:
                #     dic_new["Name_UK"] = dic_new["Name_UK"].split("(")[0].strip() # remove anything right of first '('
                #===============================================================
                dic_GNDB[row[0]] = dic_new
                del dic_new
                
                #arcEC.SetMsg("{}".format(row[0]),0)          
                # Don't try Msg Danish, nor Grenlandic name with strance characters  
    except arcpy.ExecuteError:
        arcpy.AddError("Error 201: arcpy.ExecuteError: "+arcpy.GetMessages(2))
    except Exception as e:
        arcpy.AddError("Error 202: Exception: "+e.args[0])
    
    arcEC.SetMsg("  - count entries   : "+str(len(dic_GNDB.keys())),0)
    #=======================================================================
    # key_samp = "{687F98C5-49AF-44BA-8905-8C2A76CA7EA5}" # <--- This record is known to be free of special characters
    # dic_samp = dic_GNDB[key_samp]
    # arcEC.SetMsg(" - sample           : "+key_samp,0)
    # arcEC.SetMsg("   - name type      : "+str(dic_samp["NameType"]),0)
    # arcEC.SetMsg("   - Greenland      : "+str(dic_samp["Name_GL"]),0)
    # arcEC.SetMsg("   - Danish         : "+str(dic_samp["Name_DK"]),0)
    # arcEC.SetMsg("   - English        : "+str(dic_samp["Name_UK"]),0)
    # arcEC.SetMsg("   - X,Y            : "+str(dic_samp["XY_tuple"]),0)
    #=======================================================================
    
    lst_fields_we_want = ["GST_NID","OBJNAM","NOBJNM","NIS_EDITOR_COMMENT","NAMETYPE"]
    
    # *** for each record:
    arcEC.SetMsg("\nRunning through the rows ...",0)
    arcEC.SetMsg("Overwrite: "+str(bolOverwrite),0)
    # bolOverwrite = True # XXXXXX remove line before release
    
    #try:
    num_row_count = 0
    num_row_changed = 0
    with arcpy.da.UpdateCursor(lay_in, lst_fields_we_want, "GST_NID IS NOT NULL") as cursor:
        for row in cursor:
            if row[0] in dic_GNDB.keys():
                num_row_count += 1
                bolChanges = False
                arcEC.SetMsg(" Hit GNDB           : "+str(row[0]),0)
                
                # ** Process the row <----------------------------------------- This is where the real business is going on
                # * Calculate the official values from GNDB
                lstOfficialNames = CorrectNaming(strMode, dic_GNDB[row[0]])
                OBJNAM_off = encodeIfUnicode(lstOfficialNames[1])
                NOBJNM_off = encodeIfUnicode(lstOfficialNames[2])
                arcEC.SetMsg("     GNDB official  : ("+str(OBJNAM_off)+" / "+str(NOBJNM_off)+")",0)
                
                # * OBJNAM
                if OBJNAM_off != None and len(OBJNAM_off) > 1: # OBJNAM holds valid data
                    OBJNAM_cur = encodeIfUnicode(row[1])
                    if bolOverwrite or OBJNAM_cur == "" or OBJNAM_cur == None: # Edits are allowed
                        if (OBJNAM_off != OBJNAM_cur) and (OBJNAM_off != None and OBJNAM_off != ""): # There is a need for update...
                            arcEC.SetMsg("      OBJNAM   <<   : "+OBJNAM_cur+" << "+OBJNAM_off,0)
                            row[1] = OBJNAM_off
                            bolChanges = True
                        else:
                            arcEC.SetMsg("      OBJNAM   ==   : "+OBJNAM_cur,0)
                            
                #* NOBJNM
                if NOBJNM_off != None and len(NOBJNM_off) > 1: # NOBJNM holds valid data
                    NOBJNM_cur = encodeIfUnicode(row[2])
                    if bolOverwrite or NOBJNM_cur == "" or NOBJNM_cur == None: # Edits are allowed
                        if (NOBJNM_off != NOBJNM_cur) and (NOBJNM_off != None and NOBJNM_off != ""): # There is a need for update...
                            arcEC.SetMsg("      NOBJNM   <<   : "+NOBJNM_cur+" << "+NOBJNM_off,0)
                            row[2] = NOBJNM_off
                            bolChanges = True
                        else:
                            arcEC.SetMsg("      NOBJNM   ==   : "+NOBJNM_cur,0)
                                            
                # * NIS_EDITOR_COMMENT
                NISECo_cur = encodeIfUnicode(row[3])
                # Assuming form "GNDB=13 Munding", i.e. some string + "GNDB=<int> <string>" + more string, so I split tail on ' 's  
                # search for existing string
                if "GNDB" in NISECo_cur:
                    num_pos1 = NISECo_cur.find("GNDB")    
                    num_poseq = NISECo_cur.find("=",num_pos1)   
                    num_posfs = NISECo_cur.find(" ",num_poseq)
                    if " " in NISECo_cur[num_posfs+1:]:
                        num_pos2 = NISECo_cur.find(" ",num_posfs+1)
                    else:
                        num_pos2 = len(NISECo_cur)
                    if NISECo_cur[num_pos1:num_pos2][-1] in (",",";"): # if last is , then move 1
                        num_pos2 -= 1 
                    str_head = NISECo_cur[:num_pos1]
                    str_GNDB = NISECo_cur[num_pos1:num_pos2]
                    str_tail = NISECo_cur[num_pos2:]
                    del num_pos1, num_poseq, num_posfs, num_pos2     
                    # find official GNDB= ...
                    num_NT = row[4]
                    NISECo_off = Make_NT(num_NT)
                    arcEC.SetMsg("      NISECo   cur  : "+str_GNDB,0)
                    arcEC.SetMsg("      NISECo   off  : "+NISECo_off,0) 
                    str_new_comm = str_head+NISECo_off+str_tail
                    row[3] = str_new_comm
                    bolChanges = True
                    
                # * Write back to row
                if bolChanges:
                    cursor.updateRow(row)
                    num_row_changed += 1
                    
            else:
                arcEC.SetMsg(" !*! No Hit in GNDB : "+str(row[0]),0)
                
        # ** End of - Process row.
    
    arcEC.SetMsg("Processed rows      : "+str(num_row_count),0)
    arcEC.SetMsg("    Changed rows    : "+str(num_row_changed),0)
    
    # *** All Done - Cleaning up ***
    
    timEnd = datetime.now()
    durRun = timEnd-timStart
    arcEC.SetMsg("Python stript duration (h:mm:ss.dddddd): "+str(durRun),0)
    
    return 0

    # *** End of function GNDBruninTOC()
    
if __name__ == "__main__":
    # This allows the 'executes' to be called from classic .tbx
    parameters = [arcpy.GetParameterAsText(0), arcpy.GetParameterAsText(1), arcpy.GetParameterAsText(2), arcpy.GetParameterAsText(3)]
    messages = []
    result = GNDBruninTOC_execute(parameters, messages)

# *** End of Script ***

# Music that accompanied the coding of this script:
#   Pink Floyd - Dark side of the moon