import requests
from io import BytesIO
from zipfile import ZipFile
import numpy as np
import time

paragraph_tags = ['PA','PAC','PAI', 'PAL', 'PAR', 'PARA', 'PA0', 'PA1', 'PA2', 'PA3', 'PAPI.sup.1,', 'PARENT', 'NUM', 'TBL']
patent_information_tags = ['PATN', 'INVT', 'ASSG', 'PRIR', 'REIS', 'RLAP', 'CLAS', 'UREF', 'FREF', 'OREF', 'LREP', 'PCTA', 'ABST', 'GOVT', 'PARN', 'BSUM', 'DRWD', 'DETD', 'CLMS', 'DCLM']

'''
Bibliographic information (PATN)
Contains the bibliographic information that appears on the front page of a patent
'''
bibliographic_information = {
    'WKU': 'Patent Number',
    'SRC': 'Series Code',
    'APN': 'Application Number',
    'APT': 'Application Type',
    'PBL': 'Publication Level',
    'ART': 'Art unit',
    'APD': 'Application Filing Date',
    'TTL': 'Title of Invention',
    'ISD': 'Issue Date',
    'NCL': 'Number of Claims',
    'ECL': 'Exemplary Claim Number(s)',
    'EXP': 'Primary Examiner',
    'EXA': 'Assistant Examiner',
    'NDR': 'Number of Drawing Sheets',
    'NFG': 'Number of figures',
    'DCD': 'Disclaimer Date',
    'NPS': 'Number of Pages of Specifications',
    'TRM': 'Term of Patent'
}

'''
Inventor information (INVT)
Contains information on the inventor
'''
inventor_information = {
    'NAM': 'inventor name',
    'STR': 'Street',
    'CTY': 'City',
    'STA': 'State',
    'CNT': 'Country',
    'ZIP': 'Zip code',
    'R47': 'Rule 47 indicator',
    'ITX': 'Inventor descriptive text'
}

'''
Assignee information (ASSG)
Contains the data identifying the assignee(s) of an invention at the time of issue
'''

assignee_information = {
    'NAM': 'inventor name',
    'CTY': 'City',
    'STA': 'State',
    'CNT': 'Country',
    'ZIP': 'Zip code',
    'COD': 'Assignee type code',
    'ITX': 'Assignee descriptive text'
}

'''
Foreign priority (PRIR)
Contains the data indicating in which foreign countries an application claims priority
'''

foreign_priority_information = {
    'CNT': 'Country code',
    'APD': 'Priority application date',
    'APN': 'Priority application number'
}

'''
Reissue (REIS)
Contains the data describing the reissue of a patent
'''

reissue_information = {
    'COD': 'Reissue code',
    'APN': 'Application number',
    'APD': 'Application filing date',
    'PNO': 'Patent number',
    'ISD': 'Issue date'
}

'''
Related U.S. application data (RLAP)
Contains the coded version of parent case/continuation data of prior applications related to this patent
'''

related_application_information = {
    'COD': 'Parent code',
    'APN': 'Application number',
    'APD': 'Application filing date',
    'PSC': 'Patent status code',
    'PNO': 'Patent number',
    'ISD': 'Issue date'
}

'''
Classification (CLAS)
Provides the U.S. and international classification codes for patents
'''

classification_information = {
    'OCL': 'US classification',
    'XCL': 'Cross reference',
    'UCL': 'Unofficial reference',
    'DCL': 'Digest reference',
    'EDF': 'Edition field',
    'ICL': 'International classification',
    'FSC': 'Field of search class',
    'FSS': 'Field of search subclass'
}

'''
U.S. reference (UREF)
Contains the data identifying patents which are referenced as prior art
'''

us_reference_information = {
    'PNO': 'Patent number',
    'ISD': 'Issue date',
    'NAM': 'Patentee name',
    'OCL': 'US classification',
    'XCL': 'Cross reference',
    'UCL': 'Unofficial reference'
}

'''
Foreign reference (FREF)
Contains the data identifying the foreign patents cited as references
'''

foreign_reference_information = {
    'PNO': 'Foreign patent number',
    'ISD': 'Issue date',
    'CNT': 'Country code',
    'OCL': 'Classification'
}

'''
Other reference (OREF)
Contains the data for other references cited as prior art
'''

other_reference_information = {
    'PAL': 'Reference paragraphs text data'
}

'''
Legal information (LREP)
Contains data describing the attorneys or representative representing an applicant's patent
'''

legal_information = {
    'FRM': 'Legal firm name',
    'FR2': 'Principal attorney name',
    'AAT': 'Associate attorney name',
    'AGT': 'Agent name',
    'ATT': 'Attorney name',
    'REG': 'Registration number',
    'NAM': 'Representative name',
    'STR': 'Street',
    'CTY': 'City',
    'STA': 'State',
    'CNT': 'Country',
    'ZIP': 'Zip code'
}

'''
PCT Information (PCTA)
Provides the descriptive data for related PCT information
'''

pct_information = {
    'PCN': 'PCT number',
    'PD1': 'PCT 371 date',
    'PD2': 'PCT 102 (e) date',
    'PD3': 'PCT filing date',
    'PCP': 'PCT publication No.',
    'PCD': 'PCT publication date'
}

'''
Abstract (ABST)
Contains the abstract section from a patent
'''

abstract_information = {
    'PAL': 'Abstract paragraph',
    'PAC': 'Abstract title',
    'PAL': 'text'
}

'''
Government interest (GOVT)
Contains data describing the government's interest in a patent
'''

government_interest_information = {
    'PAC': 'Interest title',
    'PAR': 'Paragraph text',
    'PAL': 'text'
}

'''
Parent case (PARN)
Contains the text of parent case/continuation data of prior applications related to this patent
'''

parent_case_information = {
    'PAC': 'title text',
    'PAR': 'paragraph text',
    'PAL': 'paragraph text'
}

'''
Brief summary (BSUM)
Contains the summary description of the invention
'''

summary_information = {
    'PAC': 'title text',
    'PAR': 'paragraph text',
    'PAL': 'paragraph text'
}

'''
DRAWING DESCRIPTION (DRWD)
Identifies the drawing(s) presented in a patent.
'''

drawings_information = {
    'PAC': 'title text',
    'PAR': 'paragraph text',
    'PAL': 'paragraph text'
}

'''
Detail description (DETD)
Contains the detailed technical specification from a patent.
'''

detailed_description_information = {
    'PAC': 'title text',
    'PAR': 'paragraph text',
    'PAL': 'paragraph text'
}

'''
Claims information (CLMS)
Contains the claim(s) information from a patent.
'''

claims_information = {
    'STM': 'Claim statement',
    'NUM': 'Claims number',
    'PAC': 'title text',
    'PAR': 'paragraph text',
    'PAL': 'paragraph text'
}

'''
Design claims (DCLM)
Contains the claim information for a design patent.
'''

design_claim_information = {
    'PAC': 'title text',
    'PAR': 'paragraph text',
    'PAL': 'paragraph text'
}


patent_information_tags = {'PATN': bibliographic_information, 
                           'INVT': inventor_information, 
                           'ASSG': assignee_information, 
                           'PRIR': foreign_priority_information, 
                           'REIS': reissue_information, 
                           'RLAP': related_application_information, 
                           'CLAS': classification_information, 
                           'UREF': us_reference_information, 
                           'FREF': foreign_reference_information, 
                           'OREF': other_reference_information, 
                           'LREP': legal_information, 
                           'ABST': abstract_information, 
                           'GOVT': government_interest_information, 
                           'PARN': parent_case_information, 
                           'BSUM': summary_information, 
                           'DETD': detailed_description_information, 
                           'CLMS': claims_information,
                           'DRWD': drawings_information
                          }


def get_patents_list(patents_txt_data):
    patent_data_list = patents_txt_data[1:]
    pat_idx = [i[0] for i in enumerate(patent_data_list) if i[1] == 'PATN']
    for pat_tag_idx in pat_idx:
        patent_data_list[pat_tag_idx] = patent_data_list[pat_tag_idx].replace(' ', '')
    patent_data_list = np.array(patent_data_list)
    patent_data_list = np.split(patent_data_list, np.where(patent_data_list == 'PATN')[0])[1:]
    patents_data = [[ln.split() for ln in patent] for patent in patent_data_list]
    return patents_data

def parse_txt_patent_data(patent_text_data,source_url=None, data_items_list = ['INVT','ASSG','PRIR','REIS','RLAP','CLAS','UREF','FREF','OREF','LREP','ABST','GOVT','PARN','BSUM','DRWD','DETD','CLMS','DCLM', 'URL']):
    patent_data = {}
    filtered_data = {}
    for line in patent_text_data:
        if line:
            line_start = line[0]
            if line_start in patent_information_tags.keys() and line_start not in patent_data.keys() and len(line) == 1: #Main non-existing tag (e.g. PATN)
                current_patent_main_tag = line[0]
                patent_data[current_patent_main_tag] = [{}]
                current_paragraphs = {'PA': 'PA_1', 'PAC': 'PAC_1', 'PAI': 'PAI_1', 'PAL': 'PAL_1', 'PAR': 'PAR_1', 'PARA': 'PARA_1', 'NUM':'NUM_1', 'TBL': 'TBL_1'}
                current_patent_sub_tag = None
            elif current_patent_main_tag and line_start in patent_information_tags.keys() and line_start in patent_data.keys() and len(line) == 1 and line_start != 'PATN': #New existing tag (e.g. new citation)
                patent_data[line_start].append({})
                current_patent_main_tag = line[0]
            elif current_patent_main_tag and line_start in patent_information_tags[current_patent_main_tag].keys() or (line_start in paragraph_tags and current_patent_main_tag != 'PATN'): #part of the current tag or a paragraph
                current_patent_sub_tag = line_start
                if current_patent_sub_tag in patent_data[current_patent_main_tag][-1].keys() and current_patent_sub_tag in current_paragraphs.keys(): # if there is already a similar paragraph
                    joint_text = ' '.join(line[1:])
                    current_paragraphs[current_patent_sub_tag] = current_patent_sub_tag + '_' + str(int(current_paragraphs[current_patent_sub_tag].split('_')[1]) + 1)
                    patent_data[current_patent_main_tag][-1][current_paragraphs[current_patent_sub_tag]] = []
                    patent_data[current_patent_main_tag][-1][current_paragraphs[current_patent_sub_tag]].append(joint_text)
                    current_patent_sub_tag = current_paragraphs[current_patent_sub_tag]
                elif current_patent_sub_tag in patent_data[current_patent_main_tag][-1].keys():
                    joint_text = ' '.join(line)
                    patent_data[current_patent_main_tag][-1][current_patent_sub_tag].append(joint_text)
                else:
                    patent_data[current_patent_main_tag][-1][current_patent_sub_tag] = line[1:]
            elif current_patent_main_tag and current_patent_sub_tag and line_start not in ['CTY','CNT']: # there is no tag, treat it as a continuation of the previous line if there is a subtag
                    joint_text = ' '.join(line)
                    patent_data[current_patent_main_tag][-1][current_patent_sub_tag].append(joint_text)
            elif current_patent_main_tag:
                    joint_text = ' '.join(line)
                    patent_data[current_patent_main_tag][-1][current_paragraphs['PA']] = joint_text
                    current_paragraphs['PA'] = 'PA_' + str(int(current_paragraphs['PA'].split('_')[1]) + 1)

    filtering_tags = list(set(data_items_list).intersection(list(patent_data.keys())))
    filtered_data['bibliographic_information'] = {bibliographic_information[tag]: ' '.join(value) for tag,value in patent_data['PATN'][0].items()}
    if 'URL' in data_items_list and source_url != None:
        filtered_data['source_file'] = source_url
    if 'ABST' in filtering_tags:
        filtered_data['abstract'] = '. '.join([' '.join(text_list) for text_list in patent_data['ABST'][0].values()])
    if 'UREF' in filtering_tags:
        filtered_data['citations'] = [{us_reference_information[tag]: ' '.join(value) for tag,value in citation.items()} for citation in patent_data['UREF']]
    if 'FREF' in filtering_tags:
        filtered_data['foreign_citations'] = [{foreign_reference_information[tag]: ' '.join(value) for tag,value in citation.items()} for citation in patent_data['FREF']]
    if 'ASSG' in filtering_tags:
        filtered_data['assignees'] = [{assignee_information[tag]: ' '.join(value) for tag,value in citation.items()} for citation in patent_data['ASSG']]
    if 'CLAS' in filtering_tags:
        filtered_data['classifications'] = patent_data['CLAS']
    if 'LREP' in filtering_tags:
        filtered_data['legal_information'] = {legal_information[tag]: ' '.join(value) for tag,value in patent_data['LREP'][0].items()}
    if 'INVT' in filtering_tags:
        filtered_data['inventors'] = [{inventor_information[tag]: ' '.join(value) for tag,value in citation.items()} for citation in patent_data['INVT']]
    if 'BSUM' in filtering_tags:
        filtered_data['breif_summary'] = {tag: ' '.join(value) for tag,value in patent_data['BSUM'][0].items()}
    if 'PARN' in filtering_tags:
        filtered_data['patent_case'] = {tag: ' '.join(value) for tag,value in patent_data['PARN'][0].items()}
    if 'PRIR' in filtering_tags:
        filtered_data['foreign_priority'] = [{foreign_priority_information[tag]: ' '.join(value) for tag,value in citation.items()} for citation in patent_data['PRIR']]
    if 'REIS' in filtering_tags:
        filtered_data['reissue_information'] = {reissue_information[tag]: ' '.join(value) for tag,value in patent_data['REIS'][0].items()}
    if 'RLAP' in filtering_tags:
        filtered_data['related_us_patent_applications'] = [{related_application_information[tag]: ' '.join(value) for tag,value in citation.items()} for citation in patent_data['RLAP']]
    if 'OREF' in filtering_tags:
        filtered_data['other_citations'] = [' '.join(reference) for reference in patent_data['OREF'][0].values()]
    if 'GOVT' in filtering_tags:
        filtered_data['government_interest'] = {tag: ' '.join(value) for tag,value in patent_data['GOVT'][0].items()}
    if 'DETD' in filtering_tags:
        filtered_data['detailed_description'] = {tag: ' '.join(value) for tag,value in patent_data['DETD'][0].items()}
    if 'CLMS' in filtering_tags:
        filtered_data['claim_information'] = {tag: ' '.join(value) for tag,value in patent_data['CLMS'][0].items()}
        
    return filtered_data


def read_data_from_url_txt(url):
    trial = 1
    while trial < 6:
        try:
            response = requests.get(url)
            read_url = ZipFile(BytesIO(response.content))
            file_name = list(filter(lambda file: '.txt' in file, read_url.namelist()))[0]
            data_bytes = read_url.open(file_name).readlines()
            data_string = [i.decode(errors="ignore").replace('\r\n','').replace('\n','').replace('\r','') for i in data_bytes]
            patents= get_patents_list(data_string)
            read_url.close()
            return patents
        except:
            trial += 1
            if trial ==5:
                print(f'Failed to download file {url}')
            else:
                time.sleep(10)

def read_and_parse_txt_from_disk(path_to_file,data_items):
    with open(path_to_file) as f:
        txt = f.read()
    txt = txt.split('\n')
    raw_patent_data= get_patents_list(txt)
    parsed_data = []
    for patent in raw_patent_data:
        parsed_data.append(parse_txt_patent_data(patent,data_items_list = data_items))
    return parsed_data

