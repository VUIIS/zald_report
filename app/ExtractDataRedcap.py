import sys,os
from redcap import Project

DEFAULT_COLUMNS=['dtiQA_v2','fMRIQA','FS','FSL_First','Multi_Atlas','TRACULA','VBMQA']

########################################################
#                  Get Data from REDCap                #
########################################################
def get_data():
    """Top-level function.Use to get a DataFrame from the redcap project

    Callers **should** catch errors"""
    return dict_from_csv(csv_from_redcap())

def csv_from_redcap():
    API_URL = os.environ['API_URL']
    API_KEY_ZALD_TTS = os.environ['KEY_ZALD']
    rc_fields=['record_id','experiment_xnat','scan_xnat','scan_sd_xnat','process_name_xnat','quality_control_complete']
    p = Project(API_URL, API_KEY_ZALD_TTS)
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

def sort_list(list_tuplet,proc):
    if proc=='fMRIQA':
        tupList=[(x[0].strip().split('_')[1].replace('gonogo','go'),x[1]) for x in list_tuplet]
        return sorted(tupList, key=lambda tuplet: tuplet[0]) 
    else:
        tupList=[(x[0].strip().split('_')[0],x[1]) for x in list_tuplet]
        return sorted(tupList, key=lambda tuplet: tuplet[0])  

########################################################
#   Get Html code for the page using data from REDCap  #
########################################################
def html_from_dict(data):
    #first level:
    html_main='<div class="mainContainer">\n'
    html_main+=html_table(data)
    html_main+='</div>\n'
    return html_main
    
def html_table(data):
    #table
    html_table='<table class="Maintable">\n'
    #header
    html_table+=html_table_header()
    #body
    html_table+=html_table_body(data)
    #close table
    html_table+='</table>\n'
    return html_table
    
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
    
def html_table_body(data):
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
                html_body+=html_table_cell(data[session][h],h)
            else:
                html_body+=html_table_cell(None,h)
            html_body+='</td>\n'
        html_body+='</tr>\n'
    html_body+='</tbody>\n'
    return html_body

def html_table_cell(list_tuplet,proc):
    html_cell='<div class="processcolumn">\n'
    if not list_tuplet:
        html_cell+=html_div_cell_no_data(' -- ')
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
