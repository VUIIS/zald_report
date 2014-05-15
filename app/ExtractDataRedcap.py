import sys,os
from redcap import Project

DEFAULT_COLUMNS=['dtiQA_v2','fMRIQA','FS','FSL_First','Multi_Atlas','TRACULA','VBMQA']

########################################################
#                  Get Data from REDCap                #
########################################################
def get_data(KEY):
    """Top-level function.Use to get a DataFrame from the redcap project

    Callers **should** catch errors"""
    return dict_from_csv(csv_from_redcap(KEY))

def csv_from_redcap(KEY):
    API_URL = os.environ['API_URL']
    API_KEY= os.environ[KEY]
    rc_fields=['record_id','experiment_xnat','scan_xnat','scan_sd_xnat','process_name_xnat','quality_control_complete']
    p = Project(API_URL, API_KEY)
    return p.export_records(fields=rc_fields,format='csv')

def dict_from_csv(csvString):
    data=dict()
    for index,line in enumerate(csvString.split('\n')):
        labels=map(lambda x: x.strip('"'),line.split(','))
        if len(labels)>1:
            d=data.get(labels[1],{})
            d2=d.get(labels[4],[])
            d2.append((labels[2]+'_'+labels[3],labels[-1]))
            d[labels[4]]=d2
            data[labels[1]]=d
    #remove two lines that should not be there (header,if session is NULL)
    data.pop('',None)
    data.pop('experiment_xnat',None)
    return data

def sort_list_ZALD(list_tuplet,proc):
    if proc=='fMRIQA':
        tupList=[(x[0].strip().split('_')[1].replace('gonogo','go'),x[1]) for x in list_tuplet]
        return sorted(tupList, key=lambda tuplet: tuplet[0]) 
    else:
        tupList=[(x[0].strip().split('_')[0],x[1]) for x in list_tuplet]
        return sorted(tupList, key=lambda tuplet: tuplet[0])
    
def sort_list(list_tuplet,proc):
    tupList=[(x[0].strip().split('_')[0],x[1]) for x in list_tuplet]
    return sorted(tupList, key=lambda tuplet: tuplet[0])

########################################################
#   Get Html code for the page using data from REDCap  #
########################################################
def html_from_dict(data,project):
    #Number of Sessions:
    html_main='<h4>Project: '+project+ ' -- Number of Sessions: '+str(len(data.keys()))+'</h4>\n'
    #legend:
    html_main+=html_legend_table()
    #Main table
    html_main+='<div class="mainContainer">\n'
    html_main+=html_table(data,project)
    html_main+='</div>\n'
    #Count table
    html_main+='<div Style="clear:both"></div>\n'
    html_main+='<div id="footer">\n'
    html_main+=html_div_count(data)
    html_main+='</div>\n'
    return html_main

def html_legend_table():
    html_legend='<table class="legend">\n'
    html_legend+='<tr>\n'
    html_legend+='<td text-align="center" id="failed">Failed</td>\n'
    html_legend+='<td text-align="center" id="unverified">Unverified</td>\n'
    html_legend+='<td text-align="center" id="passed">Passed</td>\n'
    html_legend+='<td text-align="center" id="nodata">No data</td>\n'
    html_legend+='</tr>\n'
    html_legend+='</table>\n<br>'
    return html_legend
    
def html_table(data,project):
    #table
    html_table='<table class="Maintable">\n'
    #header
    html_table+=html_table_header()
    #body
    html_table+=html_table_body(data,project)
    #close table
    html_table+='</table>\n'
    return html_table

def html_div_count(data):
    html_div_count='<br><table class="Counttable">\n'
    html_div_count+='<tr>\n'
    #Total count
    html_div_count+='<td id="defaultcolumn">Total</th>\n'
    for h in DEFAULT_COLUMNS:
        Proc_List=get_proc_list(data,h)
        html_div_count+='<td id="count">'+str(len(Proc_List))+'</th>\n'
    html_div_count+='</tr><tr>\n'
    #PAssed
    html_div_count+='<td width="100px" id="passed" >Passed</th>\n'
    for h in DEFAULT_COLUMNS:
        Proc_List=get_proc_list(data,h)
        nb_passed=[proc for proc in Proc_List if proc[1]=='2']
        html_div_count+='<td id="count">'+str(len(nb_passed))+'</th>\n'
    html_div_count+='</tr><tr>\n'
    #Failed
    html_div_count+='<td width="100px" id="failed">Failed</th>\n'
    for h in DEFAULT_COLUMNS:
        Proc_List=get_proc_list(data,h)
        nb_passed=[proc for proc in Proc_List if proc[1]=='0']
        html_div_count+='<td id="count">'+str(len(nb_passed))+'</th>\n'
    html_div_count+='</tr><tr>\n'
    #Unverified
    html_div_count+='<td width="100px" id="unverified">Unverified</th>\n'
    for h in DEFAULT_COLUMNS:
        Proc_List=get_proc_list(data,h)
        nb_passed=[proc for proc in Proc_List if proc[1]=='1']
        html_div_count+='<td id="count">'+str(len(nb_passed))+'</th>\n'
    html_div_count+='</tr>\n'
    html_div_count+='</table><br>\n'
    return html_div_count

def get_proc_list(data,h):
    proc_list=[]
    Procs=[procs[h] for session,procs in data.items() if h in procs.keys()]
    for p in Procs:
        for item in p:
            proc_list.append(item)
    return proc_list

############### DEFAULT TEMPLATE ###############
def html_table_header():
    html_header='<thead>\n<tr>\n'
    #first column: Session
    html_header+='<th>Session</th>\n'
    #Add each column
    for h in DEFAULT_COLUMNS:
        idname='defaultcolumn'
        if h=='fMRIQA':
            idname='fmriqacolumn'           
        html_header+='<th id="'+idname+'">' + h + '</th>\n'
    html_header+='</tr>\n'
    html_header+='</thead>\n'
    return html_header
    
def html_table_body(data,project):
    html_body='<tbody>\n'
    for session in sorted(data.iterkeys()):
        html_body+='<tr>\n'
        #add the session as first column
        html_body+='<td><div class="processcolumn">' + session + '</div></td>\n'
        for h in DEFAULT_COLUMNS:
            idname='defaultcolumn'
            if h=='fMRIQA':
                idname='fmriqacolumn'
            html_body+='<td id="'+idname+'">'
            if h in data[session].keys():
                html_body+=html_table_cell(data[session][h],h,project)
            else:
                html_body+=html_table_cell(None,h,project)
            html_body+='</td>\n'
        html_body+='</tr>\n'
    html_body+='</tbody>\n'
    return html_body

def html_table_cell(list_tuplet,proc,project):
    html_cell='<div class="processcolumn">\n'
    if not list_tuplet:
        html_cell+=html_div_cell_no_data(' -- ')
    else:
        if project=='ZALD_TTS':
            sorted_tuplet=sort_list_ZALD(list_tuplet,proc)
        else:
            sorted_tuplet=sort_list(list_tuplet,proc)
        for scan_qa in sorted_tuplet:
            #get value of scan if one
            if scan_qa[0]=='_' or scan_qa[0]=='':
                scan=' -- '
            else:
                scan=scan_qa[0]
            #Add the value to table
            if scan_qa[1]=='0':
                html_cell+=html_div_cell_failed(scan)
            elif scan_qa[1]=='1':
                html_cell+=html_div_cell_unverified(scan)
            elif scan_qa[1]=='2':
                html_cell+=html_div_cell_passed(scan)
    html_cell+='</div>\n'
    return html_cell
    

def html_div_cell_failed(textcell):
    return '<div class="processcell" id="failed">'+textcell+'</div>\n'
def html_div_cell_unverified(textcell):
    return '<div class="processcell" id="unverified">'+textcell+'</div>\n'
def html_div_cell_passed(textcell):
    return '<div class="processcell" id="passed">'+textcell+'</div>\n'
def html_div_cell_no_data(textcell):
    return '<div class="processcell" id="nodata">'+textcell+'</div>\n'
