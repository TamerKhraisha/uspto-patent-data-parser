import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from xml.etree.ElementTree import fromstring, ElementTree
import re
import time
import json
import requests
from io import BytesIO
from zipfile import ZipFile

global patent_info_base_path,publication_info_base_path,application_reference_path,application_info_base_path,us_application_series_code_path,number_of_claims_path,priority_claims_path,us_exemplary_claim_path,us_term_of_grant_path,us_term_of_grant_length,us_term_of_grant_extension,us_term_of_grant_disclaimer_text,locarno_classification_base_path,national_classification_base_path,invention_title_path,us_citations_path,citation_path,patent_citation_document_id_relative_path,patent_citation_category_relative_path,patent_citation_classification_cpc_relative_path,patent_citation_classification_national_relative_path,patent_citation_other_citation_relative_path,us_field_of_classifications_path,us_classification_national_relative_path_old,us_classification_national_relative_path_new,us_classification_cpc_text_relative_path,us_classification_cpc_combination_text_relative_path,us_classification_classification_ipcr_relative_path_old,us_classification_classification_ipcr_relative_path_new,classifications_ipcr_relative_path,classifications_ipcr_relative_path_old,us_parties_base_path,us_parties_applicants_path,us_parties_inventors_path,us_parties_agents_path,us_parties_agents_path_old,us_parties_inventors_path_old,addressbook_address_path,addressbook_orgname_path,addressbook_first_name_path,addressbook_last_name_path,addressbook_role_path,residence_country_path,assignees_path,examiners_path,drawings_path,claims_path,patent_abstract_relative_path,description_path

patent_file_info = './us-patent-grant'
patent_info_base_path = './us-bibliographic-data-grant'
publication_info_base_path = f'{patent_info_base_path}/publication-reference/document-id'
application_reference_path = f'{patent_info_base_path}/application-reference'
application_info_base_path = f'{application_reference_path}/document-id'
us_application_series_code_path = f'{patent_info_base_path}/us-application-series-code'
number_of_claims_path = f'{patent_info_base_path}/number-of-claims'
priority_claims_path = f'{patent_info_base_path}/priority-claims/priority-claim'
us_exemplary_claim_path = f'{patent_info_base_path}/us-exemplary-claim'
us_term_of_grant_path = f'{patent_info_base_path}/us-term-of-grant'
us_term_of_grant_length = f'{us_term_of_grant_path}/length-of-grant'
us_term_of_grant_extension = f'{us_term_of_grant_path}/us-term-extension'
us_term_of_grant_disclaimer_text = f'{us_term_of_grant_path}/disclaimer/text'
locarno_classification_base_path = f'{patent_info_base_path}/classification-locarno'
national_classification_base_path = f'{patent_info_base_path}/classification-national'
us_field_of_classifications_path = f'{patent_info_base_path}/us-field-of-classification-search'
field_of_search_classification_path = f'{patent_info_base_path}/field-of-search'
us_classification_national_relative_path_old = f'{us_field_of_classifications_path}/classification-national'
us_classification_national_relative_path_new = f'{field_of_search_classification_path}/classification-national'
us_classification_cpc_text_relative_path = f'{us_field_of_classifications_path}/classification-cpc-text'
us_classification_cpc_combination_text_relative_path = f'{us_field_of_classifications_path}/classification-cpc-combination-text'
us_classification_classification_ipcr_relative_path_old = f'{field_of_search_classification_path}/classification-ipc'
us_classification_classification_ipcr_relative_path_new = f'{us_field_of_classifications_path}/us-classifications-ipcr'
classifications_ipcr_relative_path = f'{patent_info_base_path}/classifications-ipcr/classification-ipcr'
classifications_ipcr_relative_path_old = f'{patent_info_base_path}/classification-ipc'
invention_title_path = f'{patent_info_base_path}/invention-title'
us_citations_path = f'{patent_info_base_path}/us-references-cited/us-citation'
citation_path = f'{patent_info_base_path}/references-cited/citation'
patent_citation_document_id_relative_path = 'patcit/document-id'
patent_citation_category_relative_path = 'category'
patent_citation_classification_cpc_relative_path = 'classification-cpc-text'
patent_citation_classification_national_relative_path = 'classification-national'
patent_citation_other_citation_relative_path = 'nplcit/othercit'
us_parties_base_path = f'{patent_info_base_path}/us-parties'
us_parties_base_path_old = f'{patent_info_base_path}/parties'
us_parties_applicants_path = f'{us_parties_base_path}/us-applicants/us-applicant'
us_parties_inventors_path =  f'{us_parties_base_path}/inventors/inventor'
us_parties_agents_path = f'{us_parties_base_path}/agents/agent'
us_parties_agents_path_old = f'{us_parties_base_path_old}/agents/agent'
us_parties_inventors_path_old = f'{us_parties_base_path_old}/inventors/inventor'
addressbook_address_path = 'addressbook/address'
addressbook_orgname_path = 'addressbook/orgname'
addressbook_first_name_path = 'addressbook/first-name'
addressbook_last_name_path = 'addressbook/last-name'
addressbook_role_path = 'addressbook/role'
residence_country_path = 'residence/country'
assignees_path = f'{patent_info_base_path}/assignees/assignee'
examiners_path = f'{patent_info_base_path}/examiners'
drawings_path = './drawings/figure'
claims_path = './claims/claim'
patent_abstract_relative_path = './abstract/p'
description_path = './description'


def read_and_parse_xml4_from_disk(path_to_file,data_items):
    with open(path_to_file) as f:
        xml = f.read()
    all_patents = xml.split('<?xml version="1.0" encoding="UTF-8"?>')
    all_patents = all_patents[1:]
    parsed_data = []
    for patent in all_patents:
        root_tree = ElementTree(fromstring(patent))
        parsed_data.append(parse_patent_data_xml_4(root_tree,data_items_list=data_items))      
    return parsed_data

def read_data_from_url_xml_4(url):
    response = requests.get(url)
    read_url = ZipFile(BytesIO(response.content))
    file_name = list(filter(lambda file: '.xml' in file.lower(), read_url.namelist()))[0]
    data_bytes = read_url.open(file_name).readlines()
    data_string = [i.decode(errors="ignore").replace('\r\n','').replace('\n','') for i in data_bytes]
    patent_joined_text_data = ''.join(data_string).split('<?xml version="1.0" encoding="UTF-8"?>')
    patent_joined_text_data = patent_joined_text_data[1:]
    read_url.close()
    return patent_joined_text_data

def get_patent_identification_data(root_tree):
    publication_info = root_tree.find(publication_info_base_path)
    application_info = root_tree.find(application_info_base_path)
    term_of_grant_info = root_tree.find(us_term_of_grant_path)
    term_of_grant_length = root_tree.find(us_term_of_grant_length)
    term_of_grant_extension = root_tree.find(us_term_of_grant_extension)
    us_term_of_grant_disclaimer = root_tree.find(us_term_of_grant_disclaimer_text)
    invention_title = root_tree.find(invention_title_path)
    document_data = {}    
    if publication_info != None:
        publication_reference_info = {element.tag: element.text for element in list(publication_info)}
        document_data = {**document_data,**publication_reference_info}
    if application_info !=None:
        application_reference_info = {element.tag: element.text for element in list(application_info)}
        if application_info.attrib and application_info.attrib['appl-type']:
            application_reference_info['application_type'] =  application_info.attrib['appl-type']
        document_data = {**document_data,**application_reference_info}
    if term_of_grant_info != None:
        term_of_grant = {}
        if term_of_grant_length != None:
            term_of_grant['length'] = term_of_grant_length.text
        if term_of_grant_extension != None:
            term_of_grant['extension'] = term_of_grant_extension.text
        if us_term_of_grant_disclaimer != None:
            term_of_grant['disclaimer_text'] = us_term_of_grant_disclaimer.text
        document_data = {**document_data,**term_of_grant}
    if invention_title != None:
        document_data['invention_title'] = invention_title.text
    return document_data

def get_patent_citations(root_tree):
    citations_1 = root_tree.findall(us_citations_path)
    citations_2 = root_tree.findall(citation_path)
    if citations_1:
        citations = citations_1
    elif citations_2:
        citations = citations_2
    else:
        citations = None
    citations_list = []
    if citations:
        for citation in citations:
            if citation.find(patent_citation_other_citation_relative_path) == None:
                patent_citation_data = {}
                if citation.find(patent_citation_document_id_relative_path):
                    for item in citation.find(patent_citation_document_id_relative_path):
                        patent_citation_data[item.tag] = item.text
                if citation.find(patent_citation_category_relative_path) != None:
                    patent_citation_data['category'] = citation.find(patent_citation_category_relative_path).text
                if citation.find(patent_citation_classification_cpc_relative_path) != None:
                    patent_citation_data['classification_cpc'] = citation.find(patent_citation_classification_cpc_relative_path).text.replace(" ", "")
                if citation.find(patent_citation_classification_national_relative_path) != None:
                    for item in citation.find(patent_citation_classification_national_relative_path):
                        patent_citation_data[f'classification_national_{item.tag}'] = item.text.replace(" ", "")
                if citation.find(patent_citation_other_citation_relative_path) != None:
                    patent_citation_data['npl_citation'] = citation.find(patent_citation_other_citation_relative_path).text
                citations_list.append(patent_citation_data)
    return citations_list

def get_non_patent_citations(root_tree):
    citations_1 = root_tree.findall(us_citations_path)
    citations_2 = root_tree.findall(citation_path)
    if citations_1:
        citations = citations_1
    elif citations_2:
        citations = citations_2
    else:
        citations = None
    citations_list = []
    if citations:
        for citation in citations:
            if citation.find(patent_citation_other_citation_relative_path) != None:
                patent_citation_data = {}
                patent_citation_data['npl_citation'] = citation.find(patent_citation_other_citation_relative_path).text
                if citation.find(patent_citation_category_relative_path) != None:
                    patent_citation_data['category'] = citation.find(patent_citation_category_relative_path).text
                citations_list.append(patent_citation_data)
    return citations_list

def get_inventor_data(root_tree):
    inventors_new = root_tree.findall(us_parties_inventors_path)
    inventors_old = root_tree.findall(us_parties_inventors_path_old)
    if inventors_new:
        inventors = inventors_new
    elif inventors_old:
        inventors = inventors_old
    else:
        inventors = None
    us_parties_inventors_list = []
    if inventors:
        for inventor in inventors:
            inventor_data = {}
            if (inventor.attrib):
                inventor_data = {**inventor_data, **inventor.attrib}
            if (inventor.find(addressbook_address_path) != None):
                for address_item in inventor.find(addressbook_address_path):
                    inventor_data[address_item.tag] = address_item.text
            other_tags = [addressbook_orgname_path, addressbook_first_name_path, addressbook_last_name_path]
            for tag in other_tags:
                if (inventor.find(tag) != None):
                    inventor_data[tag] = inventor.find(tag).text
            us_parties_inventors_list.append(inventor_data)
    return us_parties_inventors_list

def get_applicant_data(root_tree):
    applicants = root_tree.findall(us_parties_applicants_path)
    us_parties_applicants_list = []
    if applicants:
        for us_applicant in applicants:
            us_applicant_data = {}
            if (us_applicant.attrib):
                us_applicant_data = {**us_applicant_data, **us_applicant.attrib}
            if (us_applicant.find(addressbook_address_path) != None):
                for address_item in us_applicant.find(addressbook_address_path):
                    us_applicant_data[address_item.tag] = address_item.text
            other_tags = [addressbook_orgname_path, addressbook_first_name_path, addressbook_last_name_path, residence_country_path]
            for tag in other_tags:
                if (us_applicant.find(tag) != None):
                    us_applicant_data[tag] = us_applicant.find(tag).text
            us_parties_applicants_list.append(us_applicant_data)
    return us_parties_applicants_list

def get_agents_data(root_tree):
    agents_new = root_tree.findall(us_parties_agents_path)
    agents_old = root_tree.findall(us_parties_agents_path_old)
    if agents_new:
        agents = agents_new
    elif agents_old:
        agents = agents_old
    else:
        agents = None
    us_parties_agents_list = []
    if agents:
        for agent in agents:
            agent_data = {}
            if (agent.attrib):
                agent_data = {**agent_data, **agent.attrib}
            if (agent.find(addressbook_address_path) != None):
                for address_item in agent.find(addressbook_address_path):
                    agent_data[address_item.tag] = address_item.text
            other_tags = [addressbook_orgname_path, addressbook_first_name_path, addressbook_last_name_path]
            for tag in other_tags: 
                if (agent.find(tag) != None):
                    agent_data[tag] = agent.find(tag).text
            us_parties_agents_list.append(agent_data)
    return us_parties_agents_list

def get_assignee_data(root_tree):
    assignees = root_tree.findall(assignees_path)
    assignees_list = []
    if assignees:
        for assignee in assignees:
            assignee_data = {}
            if (assignee.find(addressbook_address_path) != None):
                for address_item in assignee.find(addressbook_address_path):
                    assignee_data[address_item.tag] = address_item.text
            if assignee.find('orgname'):
                assignee_data[assignee.find('orgname').tag] = assignee.find('orgname').text
            if assignee.find('role'):
                assignee_data[assignee.find('role').tag] = assignee.find('role').text
            other_tags = [addressbook_orgname_path, addressbook_first_name_path, addressbook_last_name_path, addressbook_role_path]
            for tag in other_tags:
                if (assignee.find(tag) != None):
                    assignee_data[tag] = assignee.find(tag).text
            assignees_list.append(assignee_data)
    return assignees_list

def get_examiner_data(root_tree):
    examiners = root_tree.findall(examiners_path)
    examiner_list = []
    if examiners:
        for examiner_index in range(len(examiners)):
            examiner_data = {}
            for data_item in examiners[0][examiner_index]:
                examiner_data['examiner_type'] = examiners[0][examiner_index].tag
                examiner_data[data_item.tag] = data_item.text
            examiner_list.append(examiner_data)
    return examiner_list

def get_patent_abstract(root_tree):
    abstract = root_tree.findall('./abstract/p')
    abstract_data = []
    if abstract:
        for paragraph in abstract:
            abstract_data.append("".join(paragraph.itertext()))
    return abstract_data

def get_detailed_description(root_tree):
    description = root_tree.find('./description')
    description_data = {'general_description_paragraphs': []}
    if description:
        current_heading = ''
        for item in description:
            if item.tag == 'heading':
                current_heading = item.text
                description_data[current_heading] = []
            elif item.tag == 'p' and current_heading != '':
                description_data[current_heading].append("".join(item.itertext()))
            elif item.tag == 'p':
                description_data['general_description_paragraphs'].append("".join(item.itertext()))
    return description_data

def get_patent_claims(root_tree):
    claims = root_tree.findall(claims_path)
    claims_list = []
    if claims:
        for claim in claims:
            claim_data = {}
            if (claim.attrib):
                claim_data = {**claim_data, **claim.attrib}
            if (claim.findall('claim-text') != None):
                claim_texts = claim.findall('claim-text')
                textList = []
                for claim_text_index in range(len(claim_texts)):
                    textList.append(claim_texts[claim_text_index].text)
                claim_data['claim_text'] = textList
            claims_list.append(claim_data)
    return claims_list

def get_patent_foreign_priority_data(root_tree):
    priority_claims = root_tree.findall(priority_claims_path)
    priority_claims_data = []
    if priority_claims:
        priority_claims_data = [i for i in map(lambda claim: {'kind': None if claim.attrib['kind'] == None else claim.attrib['kind'], 
                                                     'country': None if claim.find('country') == None else claim.find('country').text,
                                                    'doc-number': None if claim.find('doc-number') == None else claim.find('doc-number').text.replace(" ", ""),
                                                     'date': None if claim.find('date') == None else claim.find('date').text,
                                                    }, priority_claims)]
    return priority_claims_data

def get_patent_classifications(root_tree):
    locarno_classifications = root_tree.find(locarno_classification_base_path)
    national_classifications = root_tree.find(national_classification_base_path)
    us_national_classifications_old = root_tree.findall(us_classification_national_relative_path_old)
    us_national_classifications_new = root_tree.findall(us_classification_national_relative_path_new)
    if us_national_classifications_old:
        us_national_classifications = us_national_classifications_old
    elif us_national_classifications_new:
        us_national_classifications = us_national_classifications_new
    else:
        us_national_classifications = None
    us_classification_cpc_text = root_tree.findall(us_classification_cpc_text_relative_path)
    us_classification_cpc_combination = root_tree.findall(us_classification_cpc_combination_text_relative_path)
    
    us_classification_classification_ipcr_old = root_tree.findall(us_classification_classification_ipcr_relative_path_old)
    us_classification_classification_ipcr_new = root_tree.findall(us_classification_classification_ipcr_relative_path_new)

    classifications_ipcr = root_tree.findall(classifications_ipcr_relative_path)
    classifications_ipc =  root_tree.findall(classifications_ipcr_relative_path_old)
    classification_data = {}
    if locarno_classifications:
        classification_locarno = {element.tag: element.text.replace(" ", "") for element in list(locarno_classifications)}
        classification_data['classification_locarno'] = classification_locarno

    if national_classifications:
        national_classification = {element.tag: element.text.replace(" ", "") for element in list(national_classifications)}
        classification_data['national_classification'] = national_classification

    if us_national_classifications:
        us_classifications_national_list = []
        for us_classification in us_national_classifications:
            national_classification_data = {item.tag: item.text.replace(" ", "") for item in us_classification}
            us_classifications_national_list.append(national_classification_data)
        classification_data['us_classifications_national_list'] = us_classifications_national_list

    if us_classification_cpc_text:
        us_classifications_cpc_text_list = []
        for us_classification in us_classification_cpc_text:
            us_classifications_cpc_text_list.append(us_classification.text.replace(" ", ""))
        classification_data['us_classifications_cpc_text'] = us_classifications_cpc_text_list
        
    if us_classification_cpc_combination:
        us_classifications_cpc_combination_text_list = []
        for us_classification in us_classification_cpc_combination:
            us_classifications_cpc_combination_text_list.append(us_classification.text.replace(" ", ""))
        classification_data['us_classifications_cpc_combination_text_list'] = us_classifications_cpc_combination_text_list
            
    if us_classification_classification_ipcr_new:
        us_classifications_ipcr_list = []
        for us_classification in us_classification_classification_ipcr_new:
            us_classifications_ipcr_list.append(us_classification.text.replace(" ", ""))
        classification_data['us_classifications_ipcr_list'] = us_classifications_ipcr_list
               
    if us_classification_classification_ipcr_old:
        us_classifications_ipcr_list = []
        for us_classification in us_classification_classification_ipcr_old:
            us_classifications_ipcr_list.append({element.tag: element.text.replace(" ", "") for element in list(us_classification)})
        classification_data['us_classifications_ipcr_list'] = us_classifications_ipcr_list
        
    if classifications_ipcr:
        classifications_ipcr_list = []
        classification_ipcr_tags = ['ipc-version-indicator/date', 'classification-level', 'section', 'class', 'subclass', 'main-group', 'subgroup', 'symbol-position', 'classification-value', 'action-date/date', 'generating-office/country', 'classification-status','classification-data-source']
        for classification in classifications_ipcr:
            classification_data = {}
            for tag in classification_ipcr_tags:
                if classification.find(tag) != None:
                    classification_data[tag] = classification.find(tag).text
            classifications_ipcr_list.append(classification_data)
        classification_data['classifications_ipcr_list'] = classifications_ipcr_list
    if classifications_ipc:
        classifications_ipc_list = []
        for classification_ipc in classifications_ipc:
            classifications_ipc_list.append({element.tag: element.text.replace(" ", "") for element in list(classification_ipc)})
        classification_data['us_classifications_ipc_list'] = classifications_ipc_list
    return classification_data

def parse_patent_data_xml_4(patent_tree_root,source_url=None, data_items_list = ['INVT','ASSG','PRIP','CLAS','LREP','ABST','DETD','CLMS','CITA','OREF','URL']):
    filtered_data = {}
    filtered_data['bibliographic_information'] = get_patent_identification_data(patent_tree_root)
    if 'URL' in data_items_list and source_url != None:
        filtered_data['source_file'] = source_url
    if 'ABST' in data_items_list:
        abstract = get_patent_abstract(patent_tree_root)
        if abstract:
            filtered_data['abstract'] = abstract
    if 'CITA' in data_items_list:
        citations = get_patent_citations(patent_tree_root)
        if citations:
            filtered_data['citations'] = citations
    if 'OREF' in data_items_list:
        other_citations = get_non_patent_citations(patent_tree_root)
        if other_citations:
            filtered_data['other_citations'] = other_citations
    if 'ASSG' in data_items_list:
        assignees = get_assignee_data(patent_tree_root)
        if assignees:
            filtered_data['assignees'] = assignees
    if 'LREP' in data_items_list:
        legal_information = get_agents_data(patent_tree_root)
        if legal_information:
            filtered_data['legal_information'] = legal_information
    if 'CLAS' in data_items_list:
        classifications = get_patent_classifications(patent_tree_root)
        if classifications:
            filtered_data['classifications'] = classifications
    if 'INVT' in data_items_list:
        inventors = get_inventor_data(patent_tree_root)
        if inventors:
            filtered_data['inventors'] = inventors
    if 'PRIP' in data_items_list:
        foreign_priority = get_patent_foreign_priority_data(patent_tree_root)
        if foreign_priority:
            filtered_data['foreign_priority'] = foreign_priority
    if 'DETD' in data_items_list:
        detailed_description = get_detailed_description(patent_tree_root)
        if detailed_description:
            filtered_data['detailed_description'] = detailed_description
    if 'CLMS' in data_items_list:
        claim_information = get_patent_claims(patent_tree_root)
        if claim_information:
            filtered_data['claim_information'] = claim_information
    return filtered_data
