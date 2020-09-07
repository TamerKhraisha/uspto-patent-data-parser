import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from xml.etree.ElementTree import fromstring, ElementTree
import re
import numpy as np
from html.entities import html5
import time
import requests
from io import BytesIO
from zipfile import ZipFile
import json

entity_characters_mapping = {
'&dagger;': '†',
'&aring;': 'å',
'&rsqb;': ']',
'&middot;': '·',
'&lt;': ' less than ',
'&gt;': ' greater than ',
'&sacute;': 'ś',
'&rsquo;': '’',
'&equiv;': '≡',
'&uuml;': 'ü',
'&trade;': '(trademark)',
'&times;': '×',
'&boxH;': '═',
'&empty;': '∅',
'&ne;': '≠',
'&uacute;': 'ú',
'&lE;': '≦',
'&copy;': '(copyright)',
'&rdquo;': '”',
'&oslash;': 'ø',
'&atilde;': 'ã',
'&lsquo;': '‘',
'&aacute;': 'á',
'&rcub;': '}',
'&plus;': '+',
'&bull;': '•',
'&egrave;': 'è',
'&aelig;': 'æ',
'&equals;': '=',
'&gE;': '≧',
'&perp;': '⊥',
'&lsqb;': '[',
'&acirc;': 'â',
'&Uuml;': 'Ü',
'&frac34;': '¾',
'&frac78;': '⅞',
'&prop;': '∝',
'&rarr;': '→',
'&lcub;': '{',
'&minus;': '−',
'&ecirc;': 'ê',
'&deg;': '°',
'&ominus;': '⊖',
'&quest;': '?',
'&auml;': 'ä',
'&frac12;': '½',
'&ocirc;': 'ô',
'&eacute;': 'é',
'&ntilde;': 'ñ',
'&apos;': "'",
'&cacute;': 'ć',
'&sect;': '§',
'&reg;': '(copyright)',
'&num;': '#',
'&Prime;': '″',
'&frac14;': '¼',
'&amp;': 'and',
'&emsp;': '\u2003',
'&frac18;': '⅛',
'&commat;': '@',
'&Auml;': 'Ä',
'&Ouml;': 'Ö',
'&excl;': '!',
'&frac38;': '⅜',
'&ldquo;': '“',
'&euml;': 'ë',
'&oacute;': 'ó',
'&Aacute;': 'Á',
'&tilde;': '˜',
'&angst;': 'Å',
'&iuml;': 'ï',
'&ccedil;': 'ç',
'&plusmn;': '±',
'&prime;': '′',
'&iacute;': 'í',
'&ouml;': 'ö',
'&mdash;': '—',
'&square;': '□',
'&eegr;':'η',
'&kgr;':'κ',
'&tgr;':'τ',
'&agr;':'α',
'&ohgr;':'ω',
'&ngr;':'ν',
'&egr;':'ε',
'&Lgr;':'Λ',
'&Dgr;':'Δ',
'&pgr;':'π',
'&thgr;':'θ',
'&OHgr;':'Ω',
'&Ggr;':'Γ',
'&bgr;':'β',
'&phgr;':'φ',
'&mgr;':'μ',
'&PSgr;':'Ψ',
'&lgr;':'λ',
'&dgr;':'δ',
'&ggr;':'γ',
'&Sgr;':'Σ',
'&rgr;': 'ρ',
'&zgr;': 'ζ',
'&Circlesolid;':'◯',
'&bsol;': ' '
}

utf_encodings = {i[0]:str(i[1].encode('UTF-8')).replace('b','').replace('\\','').replace('\'','') for i in entity_characters_mapping.items()}
html5_entity_mappings = {f'&{key}':value for key,value in html5.items()}
utf_encodings = {**html5_entity_mappings,**utf_encodings}


def map_entity_characters(string, mapping_dictionary):
    mapped_string = string
    patent_entity_chars = list(set(re.findall(r"&\w+;", string)))
    for entity in patent_entity_chars:
        try:
            mapped_string = re.sub(entity, mapping_dictionary[entity], mapped_string)
        except:
            mapped_string = re.sub(entity, entity.replace('&','"').replace(';','"'), mapped_string)
    return mapped_string

def remove_problematic_strings(string):
    cleaned_string = string.replace("<URL:","").replace("'<'URL:","").replace('&;','&')
    cleaned_string = re.sub(r'<(?![a-zA-Z]|/|!)', 'less than ', cleaned_string)
    #cleaned_string = re.sub(r'\(>[^\d]*', 'greater than ', cleaned_string)
    return cleaned_string

def get_continuation_data(root_tree):
    #Only part of the data is parsed
    early_applications_info = root_tree.findall('SDOBI/B600/B630/B631/PARENT-US') #Earlier application from which the present document has been divided out
    partial_continuation_docs_info = root_tree.findall('SDOBI/B600/B630/B632/PARENT-US') #Document of which this is a continuation-in-part
    continuation_data = {}
    if early_applications_info:
        continuation_data['early_applications_documents'] = []
        for early_application in early_applications_info:
            early_application_data = {}
            if early_application.find('CDOC/DOC/DNUM'):
                early_application_data['child_document_identification'] = early_application.find('CDOC/DOC/DNUM/PDAT').text
            if early_application.find('PDOC/DOC/DNUM'):
                early_application_data['parent_document_identification'] = early_application.find('PDOC/DOC/DNUM/PDAT').text
            if early_application.find('PSTA'): # 00 ... Pending, 01 ... Granted (Patent), 03 ... Abandoned, 04 ... Statutory Invention Registration (SIR)
                early_application_data['parent_status_code'] = early_application.find('PSTA/PDAT').text
            if early_application.find('PPUB/DOC/DNUM'): #id of patent associated with parent
                early_application_data['parent_patent_id'] = early_application.find('PPUB/DOC/DNUM/PDAT').text
            if early_application.find('B650/DOC/DNUM'): #id of previously-published document concerning the same application
                early_application_data['previous_related_patent_id'] = early_application.find('B650/DOC/DNUM/PDAT').text
            continuation_data['early_applications_documents'].append(early_application_data)
    if partial_continuation_docs_info:
        continuation_data['partial_continuation_docs_info'] = []
        for partial_continuation_doc in partial_continuation_docs_info:
            partial_continuation_doc_data = {}
            if partial_continuation_doc.find('CDOC/DOC/DNUM'):
                partial_continuation_doc_data['child_document_identification'] = partial_continuation_doc.find('CDOC/DOC/DNUM/PDAT').text
            if partial_continuation_doc.find('PDOC/DOC/DNUM'):
                partial_continuation_doc_data['parent_document_identification'] = partial_continuation_doc.find('PDOC/DOC/DNUM/PDAT').text
            if partial_continuation_doc.find('PSTA'): # 00 ... Pending, 01 ... Granted (Patent), 03 ... Abandoned, 04 ... Statutory Invention Registration (SIR)
                partial_continuation_doc_data['parent_status_code'] = partial_continuation_doc.find('PSTA/PDAT').text
            if partial_continuation_doc.find('PPUB/DOC/DNUM'): #id of patent associated with parent
                partial_continuation_doc_data['parent_patent_id'] = partial_continuation_doc.find('PPUB/DOC/DNUM/PDAT').text
            if partial_continuation_doc.find('B650/DOC/DNUM'): #id of previously-published document concerning the same application
                partial_continuation_doc_data['previous_related_patent_id'] = partial_continuation_doc.find('B650/DOC/DNUM/PDAT').text
            continuation_data['partial_continuation_docs_info'].append(partial_continuation_doc_data)
    return  continuation_data

def get_reissue_data(root_tree):
    #Only part of the data is parsed
    reissue_info = root_tree.findall('SDOBI/B600/B640/PARENT-US') #Related patents of applications of which the parent is a reissue
    reissues_data = []
    if reissue_info:
        for reissue in reissue_info:
            reissue_data = {}
            if reissue.find('CDOC/DOC/DNUM'):
                reissue_data['child_document_identification'] = reissue.find('CDOC/DOC/DNUM/PDAT').text
            if reissue.find('PDOC/DOC/DNUM'):
                reissue_data['parent_document_identification'] = reissue.find('PDOC/DOC/DNUM/PDAT').text
            if reissue.find('PSTA'): # 00 ... Pending, 01 ... Granted (Patent), 03 ... Abandoned, 04 ... Statutory Invention Registration (SIR)
                reissue_data['parent_status_code'] = reissue.find('PSTA/PDAT').text
            if reissue.find('PPUB/DOC/DNUM'):
                reissue_data['parent_patent_id'] = reissue.find('PPUB/DOC/DNUM/PDAT').text
            reissues_data.append(reissue_data)
    return  reissues_data

def get_patent_field_of_search_data(root_tree):
    field_search_info = root_tree.find('SDOBI/B500/B580')
    field_search_data = {}
    if field_search_info:
        national_classification = field_search_info.findall('B582/PDAT') #Use for structured US Classification information: ...Pos. 1 - 3 ... Class 3 alphanumeric characters, right justified; D for design classes, followed by one or two right-justified digits; PLT for Plant classes ...Pos. 4 - ... Subclass alphanumeric, variable length
        us_classification_unstructured = field_search_info.findall('B583US/PDAT') #US classification, unstructured. Could be any combination of classes, subclasses, ranges of subclasses, etc.
        international_patent_classification = field_search_info.findall('B581/PDAT') # IPC
        if national_classification:
            field_search_data['national_classifications'] = [classification.text for classification in national_classification]
        if us_classification_unstructured:
            field_search_data['us_classification_unstructured'] = [classification.text for classification in us_classification_unstructured]
        if international_patent_classification:
            field_search_data['international_classification'] = [classification.text for classification in international_patent_classification]
    return field_search_data

def get_patent_abstract(root_tree):
    abstract_data = []
    abstract_paragraphs = root_tree.findall('SDOAB/BTEXT/PARA')
    if abstract_paragraphs: 
        for paragraph in abstract_paragraphs:
            abstract_data.append("".join(paragraph.itertext()))
    return abstract_data

def get_patent_term_of_grant(root_tree):
    term_of_grant_info = root_tree.find('SDOBI/B400/B472')
    term_extension = 'SDOBI/B400/B472/B474US' # Either "5 years", or the number of days (as an integer) if the extension is less than five years
    term_of_grant_data = {}
    if term_of_grant_info:
        if term_of_grant_info.find('B474'):
            term_of_grant_data['term_of_grant'] = term_of_grant_info.find('B474/PDAT').text
        if term_of_grant_info.find('B474US'):
            term_of_grant_data['term_extension'] = term_of_grant_info.find('B474US/PDAT').text
    return term_of_grant_data

def get_patent_foreign_priority_data(root_tree):
    foreign_claims = root_tree.findall('SDOBI/B300')
    foreign_claims_data = []
    if foreign_claims:
        for claim in foreign_claims:
            foreign_claim_data = {}
            if claim.find('B310/DNUM'):
                foreign_claim_data['document_number'] = claim.find('B310/DNUM/PDAT').text
            if claim.find('B320/DATE'):
                foreign_claim_data['date'] = claim.find('B320/DATE/PDAT').text
            if claim.find('B330/CTRY'):
                foreign_claim_data['country'] = claim.find('B330/CTRY/PDAT').text
            foreign_claims_data.append(foreign_claim_data)
    return foreign_claims_data

def get_patent_claims(root_tree):
    claims = root_tree.find('SDOCL/CL')
    claims_data = []
    if claims:
        for claim in claims:
            if claim.find('PARA/PTEXT'):
                claims_data.append(claim.find('PARA/PTEXT/PDAT').text)
    return claims_data

def get_patent_identification_data(root_tree):
    document_identification_data = root_tree.find('SDOBI/B100')
    document_data = {}
    if document_identification_data:
        if document_identification_data.find('B130'):
            document_data['document_kind'] = document_identification_data.find('B130/PDAT').text
        if document_identification_data.find('B110/DNUM'):
            document_data['document_number'] = document_identification_data.find('B110/DNUM/PDAT').text
        if document_identification_data.find('B140/DATE'):
            document_data['document_date'] = document_identification_data.find('B140/DATE/PDAT').text
        if document_identification_data.find('B190'):
            document_data['publishing_country_or_organization'] = document_identification_data.find('B190/PDAT').text
        if root_tree.find('SDOBI/B500/B540/STEXT'):
            document_data['title_of_invention'] = root_tree.find('SDOBI/B500/B540/STEXT/PDAT').text
        patent_term_data = get_patent_term_of_grant(root_tree)
        document_data = {**document_data, **patent_term_data}
        return document_data
    
def get_patent_classifications(root_tree):
    international_patent_classification = root_tree.find('SDOBI/B500/B510')
    domestic_or_national_patent_classification = root_tree.find('SDOBI/B500/B520')
    patent_classification_data = {}
    if international_patent_classification.findall('B511'):
        patent_classification_data['main_or_locrano_class'] = [classification.text for classification in international_patent_classification.findall('B511/PDAT')]
    if international_patent_classification.findall('B512'):
        patent_classification_data['further_ipc_classification'] = [classification.text for classification in international_patent_classification.findall('B512/PDAT')]
    if international_patent_classification.findall('B516'):
        patent_classification_data['ipc_edition'] = [classification.text for classification in international_patent_classification.findall('B516/PDAT')]
    if domestic_or_national_patent_classification.findall('B521'):
        patent_classification_data['domestic_main_classification'] = [classification.text for classification in domestic_or_national_patent_classification.findall('B521/PDAT')]
    if domestic_or_national_patent_classification.findall('B522'):
        patent_classification_data['domestic_further_classification'] = [classification.text for classification in domestic_or_national_patent_classification.findall('B522/PDAT')]
    field_of_search_classifications = get_patent_field_of_search_data(root_tree)
    if field_of_search_classifications:
        patent_classification_data = {**patent_classification_data,**field_of_search_classifications}
    return patent_classification_data

def get_patent_citations(tree_root):
    patent_citations = tree_root.findall('SDOBI/B500/B560/B561')
    patent_citations_data = []
    if patent_citations:
        for citation in patent_citations:
            citation_data = {}
            if citation.find('PCIT/DOC'):
                for item in citation.find('PCIT/DOC'):
                    citation_data[item.tag] =  item.find('PDAT').text
            if citation.findall('CITED-BY-EXAMINER'):
                citation_data['CITING_PARTY'] = "examiner"
            if citation.findall('CITED-BY-OTHER'):
                citation_data['CITING_PARTY'] = "other"
            if citation.findall('PCIT/PARTY-US/NAM/SNM/STEXT/PDAT'):
                citation_data['US_PARTY_NAME'] = citation.findall('PCIT/PARTY-US/NAM/SNM/STEXT/PDAT')[0].text
            if citation.findall('PCIT/PNC/PDAT'):
                citation_data['PNC'] = citation.findall('PCIT/PNC/PDAT')[0].text
            if citation.findall('PCIT/PIC/PDAT'):
                citation_data['PIC'] = citation.findall('PCIT/PIC/PDAT')[0].text
            patent_citations_data.append(citation_data)
    return patent_citations_data

def get_non_patent_citations(tree_root):
    non_patent_citations = tree_root.findall('SDOBI/B500/B560/B562')
    non_patent_citations_data = []
    if non_patent_citations:
        for citation in non_patent_citations:
            citation_data = {}
            if citation.findall('NCIT/STEXT/PDAT'):
                citation_data['title'] = citation.findall('NCIT/STEXT/PDAT')[0].text
            if citation.find('NCIT/STEXT/HIL'):
                for item in citation.find('NCIT/STEXT/HIL'):
                    citation_data[item.tag] =  item.find('PDAT').text
            if citation.findall('CITED-BY-EXAMINER'):
                citation_data['CITING_PARTY'] = "examiner"
            if citation.findall('CITED-BY-OTHER'):
                citation_data['CITING_PARTY'] = "other"
            non_patent_citations_data.append(citation_data)
    return non_patent_citations_data

def get_assignee_data(tree_root):
    assignee_type_codes = {
        '01':'Unassigned',
        '02':'United States company or corporation',
        '03':'Foreign company or corporation',
        '04':'United States individual',
        '05':'Foreign individual',
        '06':'United States government',
        '07':'Foreign government',
        '08':'County government (US)',
        '09':'State government (US)'
    }
    assignee_info = tree_root.findall('SDOBI/B700/B730')
    assignees = []
    if assignee_info:
        for assignee in assignee_info:
            assignee_parties = assignee.findall('B731/PARTY-US')
            assignee_data = {}
            if assignee_parties:
                assignee_data['assignee_parties'] = []
                for assignee_party in assignee_parties:
                    assignee_party_data = {}
                    if assignee_party.find('NAM/ONM/STEXT'):
                        assignee_party_data['organization_name'] = assignee_party.find('NAM/ONM/STEXT/PDAT').text
                    if assignee_party.find('ADR/CTRY'):
                        assignee_party_data['country'] = assignee_party.find('ADR/CTRY/PDAT').text
                    if assignee_party.find('ADR/CITY'):
                        assignee_party_data['city'] = assignee_party.find('ADR/CITY/PDAT').text
                    if assignee_party.find('ADR/STATE'):
                        assignee_party_data['state'] = assignee_party.find('ADR/STATE/PDAT').text
                    if assignee_party.find('NAM/FNM'):
                        assignee_party_data['first_name'] = assignee_party.find('NAM/FNM/PDAT').text
                    if assignee_party.find('NAM/SNM/STEXT'):
                        assignee_party_data['sir_name'] = assignee_party.find('NAM/SNM/STEXT/PDAT').text
                    assignee_data['assignee_parties'].append(assignee_party_data)
            if assignee.find('B732US'):
                assignee_data['assignee_type'] = assignee_type_codes[assignee.find('B732US/PDAT').text] if assignee.find('B732US/PDAT').text in assignee_type_codes.keys() else assignee.find('B732US/PDAT').text
            assignees.append(assignee_data)
        return assignees
    
def get_inventor_data(tree_root):
    inventors_info = tree_root.findall('SDOBI/B700/B720/B721')
    inventors = []
    if inventors_info:
        for inventor in inventors_info:
            inventor_data = {}
            inventor_info = inventor.find('PARTY-US')
            if inventor_info:
                if inventor_info.find('NAM/FNM'):
                    inventor_data['first_name'] = inventor_info.find('NAM/FNM/PDAT').text
                if inventor_info.find('NAM/SNM/STEXT'):
                    inventor_data['sir_name'] = inventor_info.find('NAM/SNM/STEXT/PDAT').text
                if inventor_info.find('ADR/STR'):
                    inventor_data['street'] = inventor_info.find('ADR/STR/PDAT').text
                if inventor_info.find('ADR/CITY'):
                    inventor_data['city'] = inventor_info.find('ADR/CITY/PDAT').text
                if inventor_info.find('ADR/STATE'):
                    inventor_data['state'] = inventor_info.find('ADR/STATE/PDAT').text
                if inventor_info.find('ADR/PCODE'):
                    inventor_data['post_code'] = inventor_info.find('ADR/PCODE/PDAT').text
                if inventor_info.find('ADR/CTRY'):
                    inventor_data['country'] = inventor_info.find('ADR/CTRY/PDAT').text
                if inventor_info.find('DTXT/STEXT'):
                    inventor_data['descriptive_text'] = inventor_info.find('DTXT/STEXT/PDAT').text
                if inventor_info.find('ADR/OMC'):
                    inventor_data['organization_mail_code'] = inventor_info.find('ADR/OMC/PDAT').text
                inventors.append(inventor_data)
        return inventors
    
def get_legal_representative_data(tree_root):
    legal_representative_info = tree_root.findall('SDOBI/B700/B720/B721/LEGAL-REPRESENTATIVE/PARTY-US')
    legal_representatives = []
    if legal_representative_info:
        for legal_representative in legal_representative_info:
            legal_representative_data = {}
            if legal_representative.find('NAM/SNM/STEXT'):
                legal_representative_data['sir_name'] = legal_representative.find('NAM/SNM/STEXT/PDAT').text
            if legal_representative.find('DTXT/STEXT'):
                legal_representative_data['descriptive_text'] = legal_representative.find('DTXT/STEXT/PDAT').text   
            if legal_representative.find('DNAM/FNM'):
                legal_representative_data['first_name'] = legal_representative.find('DNAM/FNM/PDAT').text                     
            if legal_representative.find('ADR/CITY/PDAT'):
                legal_representative_data['first_name'] = legal_representative.find('DNAM/FNM/PDAT').text                        
            if legal_representative.find('ADR/CITY'):
                legal_representative_data['city'] = legal_representative.find('ADR/CITY/PDAT').text                       
            if legal_representative.find('ADR/CTRY'):
                legal_representative_data['country'] = legal_representative.find('ADR/CTRY/PDAT').text
            legal_representatives.append(legal_representative_data)
    return legal_representatives

def get_government_interest_data(tree_root):
    government_interest_information_header = tree_root.findall('SDODE/GOVINT/BTEXT/H/STEXT')
    government_interest_information_text = tree_root.findall('SDODE/GOVINT/BTEXT/PARA/PTEXT')
    government_interest_data = []
    if government_interest_information_header:
        for header_text in government_interest_information_header:
            government_interest_data.append(header_text.find('PDAT').text)
    if government_interest_information_text:
        for paragraph_text in government_interest_information_text:
            government_interest_data.append(paragraph_text.find('PDAT').text)
    return government_interest_data

def get_detailed_description(tree_root):
    detailed_description_info = tree_root.find('SDODE/DETDESC/BTEXT')
    description = []
    if detailed_description_info:
        for paragraph in detailed_description_info.findall('PARA/PTEXT'):
            description.append("".join(paragraph.itertext()))
    return description

def get_brief_summary(tree_root):
    brief_summary_info = tree_root.find('SDODE/BRFSUM/BTEXT')
    summary = []
    if brief_summary_info:
        for paragraph in brief_summary_info.findall('PARA/PTEXT'):
            summary.append("".join(paragraph.itertext()))
    return summary

def get_related_patents_data(tree_root):
    related_patents_info = tree_root.find('SDODE/RELAPP/BTEXT')
    related_patents = []
    if related_patents_info:
        for paragraph in related_patents_info.findall('PARA/PTEXT'):
            related_patents.append("".join(paragraph.itertext()))
    return related_patents

def read_data_from_url_xml_2(url):
    response = requests.get(url)
    read_url = ZipFile(BytesIO(response.content))
    file_name = list(filter(lambda file: '.xml' in file.lower(), read_url.namelist()))[0]
    data_bytes = read_url.open(file_name).readlines()
    data_string = [i.decode(errors="ignore").replace('\r\n','').replace('\n','') for i in data_bytes]
    patent_joined_text_data = ''.join(data_string).split('<?xml version="1.0" encoding="UTF-8"?>')

    all_patents_mapped_entities = []
    for patent in patent_joined_text_data[1:]:
        entity_mapped_patent_string = map_entity_characters(patent,utf_encodings)
        entity_mapped_patent_string = remove_problematic_strings(entity_mapped_patent_string)
        entity_mapped_patent_string = remove_problematic_strings(entity_mapped_patent_string)
        all_patents_mapped_entities.append(entity_mapped_patent_string)
    read_url.close()
    return all_patents_mapped_entities

def parse_patent_data_xml_2(patent_tree_root,source_url=None, data_items_list = ['INVT','ASSG','PRIP','REIS','RLAP','CLAS','UREF','FREF','OREF','LREP','PCTA','ABST','GOVT','PARN','BSUM','DRWD','DETD','CLMS','DCLM','CITA','URL']):
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
    if 'ASSG' in data_items_list:
        assignees = get_assignee_data(patent_tree_root)
        if assignees:
            filtered_data['assignees'] = assignees
    if 'LREP' in data_items_list:
        legal_information = get_legal_representative_data(patent_tree_root)
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
    if 'BSUM' in data_items_list:
        brief_summary = get_brief_summary(patent_tree_root)
        if brief_summary:
            filtered_data['brief_summary'] = brief_summary
    if 'PRIP' in data_items_list:
        foreign_priority = get_patent_foreign_priority_data(patent_tree_root)
        if foreign_priority:
            filtered_data['foreign_priority'] = foreign_priority
    if 'REIS' in data_items_list:
        reissue_information = get_reissue_data(patent_tree_root)
        if reissue_information:
            filtered_data['reissue_information'] = reissue_information
    if 'RLAP' in data_items_list:
        related_us_patent_applications = get_related_patents_data(patent_tree_root)
        if related_us_patent_applications:
            filtered_data['related_us_patent_applications'] = related_us_patent_applications
    if 'OREF' in data_items_list:
        other_citations = get_non_patent_citations(patent_tree_root)
        if other_citations:
            filtered_data['other_citations'] = other_citations
    if 'GOVT' in data_items_list:
        government_interest = get_government_interest_data(patent_tree_root)
        if government_interest:
            filtered_data['government_interest'] = government_interest
    if 'DETD' in data_items_list:
        detailed_description = get_detailed_description(patent_tree_root)
        if detailed_description:
            filtered_data['detailed_description'] = detailed_description
    if 'CLMS' in data_items_list:
        claim_information = get_patent_claims(patent_tree_root)
        if claim_information:
            filtered_data['claim_information'] = claim_information
    return filtered_data

def read_and_parse_xml2_from_disk(path_to_file, data_items):
    with open(path_to_file) as f:
        xml = f.read()
    all_patents = xml.split('<?xml version="1.0" encoding="UTF-8"?>')
    all_patents_mapped_entities = []
    for patent in all_patents[1:]:
        entity_mapped_patent_string = map_entity_characters(patent,utf_encodings)
        entity_mapped_patent_string = remove_problematic_strings(entity_mapped_patent_string)
        entity_mapped_patent_string = remove_problematic_strings(entity_mapped_patent_string)
        all_patents_mapped_entities.append(entity_mapped_patent_string)
        parsed_data = []
    for patent in all_patents_mapped_entities:
        root_tree = ElementTree(fromstring(patent))
        parsed_data.append(parse_patent_data_xml_2(root_tree, data_items_list=data_items))
    return parsed_data