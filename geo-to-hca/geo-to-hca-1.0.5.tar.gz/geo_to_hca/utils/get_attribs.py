# --- core imports
import logging
import xml.etree.ElementTree as xm

# --- third-party imports
import requests as rq

# ---application imports
from geo_to_hca.utils import handle_errors

"""
Define constants.
"""
STATUS_ERROR_CODE = 400

log = logging.getLogger(__name__)


def get_attributes_pubmed(xml_content: object,iteration: int) -> [str,[],[],str]:
    author_list = list()
    grant_list=  list()
    try:
        title = xml_content.find("PubmedArticle").find("MedlineCitation").find("Article").find("ArticleTitle").text
    except:
        title = ''
        if iteration == 1:
            log.info("no publication title found")
    try:
        authors = xml_content.find("PubmedArticle").find("MedlineCitation").find("Article").find("AuthorList")
    except:
        if iteration == 1:
            log.info("no authors found in SRA")
        try:
            url = rq.get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={title}')
            if url.status_code == STATUS_ERROR_CODE:
                raise handle_errors.NotFoundENA(url, title)
            else:
                xml_content_2 = xm.fromstring(url.content)
            try:
                results = list()
                result_list = xml_content_2.find("resultList")
                for result in result_list:
                    results.append(result)
            except:
                authors = None
                if iteration == 1:
                    log.info("no authors found in ENA")
        except:
            authors = None
            if iteration == 1:
                log.info("no authors found in ENA")
    if authors:
        for author in authors:
            try:
                lastname = author.find("LastName").text
            except:
                lastname = ''
            try:
                forename = author.find("ForeName").text
            except:
                forename = ''
            try:
                initials = author.find("Initials").text
            except:
                initials = ''
            try:
                affiliation = author.find('AffiliationInfo').find("Affiliation").text
            except:
                affiliation = ''
            author_list.append([lastname,forename,initials,affiliation])
    try:
        grants = xml_content.find("PubmedArticle").find("MedlineCitation").find("Article").find("GrantList")
    except:
        grants = None
        if iteration == 1:
            log.info("no grants found in SRA or ENA")
    if grants:
        for grant in grants:
            try:
                id = grant.find("GrantID").text
            except:
                id = ''
            try:
                agency = grant.find("Agency").text
            except:
                agency = ''
            grant_list.append([id,agency])
    try:
        articles = xml_content.find('PubmedArticle').find('PubmedData').find('ArticleIdList')
        for article_id in articles:
            if "/" in article_id.text:
                article_doi_id = article_id.text
    except:
        article_doi_id = ''
        if iteration == 1:
            log.info("no publication doi found")
    return title,author_list,grant_list,article_doi_id


def get_attributes_biosample(element: object) -> []:
    """
    Extracts sample metadata from an an xml file which consists of many attributes.
    The xml is derived from a request with biosample accessions.
    """
    element_id = ''
    if element.attrib:
        element_id = element.attrib['accession']
    if element_id == '':
        for item in element.find('Ids'):
            if 'SAMN' in item.text:
                element_id = item.text
    if element_id == '':
        log.info('Could not find biosample id')
    sample_title = ''
    for description in element.findall('Description'):
        sample_title = description.find('Title').text
    attribute_list = []
    for attribute_set in element.findall('Attributes'):
        for attribute in attribute_set:
            attribute_list.append(attribute.text)
    if attribute_list == []:
        attribute_list = ['','']
    return [element_id,sample_title,attribute_list]


def get_attributes_library_protocol(experiment_package: object) -> []:
    """
    Extracts experiment metadata from an an xml file which consists of many attributes.
    The xml is derived from a request with experiment accessions.
    """
    experiment_id = experiment_package.find('EXPERIMENT').attrib['accession']
    for experiment in experiment_package.find('EXPERIMENT'):
        library_descriptors = experiment.find('LIBRARY_DESCRIPTOR')
        if library_descriptors:
            desc = library_descriptors.find('LIBRARY_CONSTRUCTION_PROTOCOL')
            library_construction_protocol = desc.text
        else:
            library_construction_protocol = ''
        illumina = experiment.find('ILLUMINA')
        if illumina:
            instrument = illumina.find('INSTRUMENT_MODEL').text
        else:
            instrument = ''
    return [experiment_id,library_construction_protocol,instrument]


def get_attributes_bioproject(xml_content: object, bioproject_accession: str) -> [str,str,str,str]:
    bioproject_metadata = xml_content.find('DocumentSummary')
    try:
        project_name = bioproject_metadata.find("Project").find('ProjectDescr').find('Name').text
    except:
        log.info("no project name")
        project_name = None
    try:
        project_title = bioproject_metadata.find("Project").find('ProjectDescr').find('Title').text
    except:
        log.info("no project title")
        project_title = None
    try:
        project_description = bioproject_metadata.find("Project").find('ProjectDescr').find('Description').text
    except:
        project_description = ''
        log.info("no project description")
    project_publication = bioproject_metadata.find("Project").find('ProjectDescr').find('Publication')
    try:
        if project_publication.find('DbType').text == 'Pubmed' or project_publication.find('DbType').text == 'ePubmed':
            project_pubmed_id = project_publication.find('Reference').text
    except:
        log.info("No publication for project %s was found: searching project title in EuropePMC" % (bioproject_accession))
    if not project_publication or not project_pubmed_id:
        if project_title:
            log.info("project title is: %s" % (project_title))
            url = rq.get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={project_title}')
            if url.status_code == STATUS_ERROR_CODE:
                raise handle_errors.NotFoundENA(url, project_title)
            else:
                xml_content = xm.fromstring(url.content)
                try:
                    results = list()
                    result_list = xml_content.find("resultList")
                    for result in result_list:
                        results.append(result)
                    journal_title = results[0].find("journalTitle").text
                    if not journal_title or journal_title == '':
                        project_pubmed_id = ''
                        log.info("no publication results for project title in ENA")
                    else:
                        answer = input("A publication title has been found: %s.\nIs this the publication title associated with the GEO accession? [y/n]: " % (journal_title))
                        if answer.lower() in ['y',"yes"]:
                            project_pubmed_id = results[0].find("pmid").text
                        else:
                            journal_title = results[1].find("journalTitle").text
                            if not journal_title or journal_title == '':
                                project_pubmed_id = ''
                                log.info("no publication results for project title in ENA")
                            else:
                                answer = input("An alternative publication title has been found: %s.\nIs this the publication title associated with the GEO accession? [y/n]: " % (journal_title))
                                if answer.lower() in ['y', "yes"]:
                                    project_pubmed_id = results[1].find("pmid").text
                                else:
                                    journal_title = results[2].find("journalTitle").text
                                    if not journal_title or journal_title == '':
                                        project_pubmed_id = ''
                                        log.info("no publication results for project title in ENA")
                                    else:
                                        answer = input("An alternative publication title has been found: %s.\nIs this the publication title associated with the GEO accession? [y/n]: " % (journal_title))
                                        if answer.lower() in ['y', "yes"]:
                                            project_pubmed_id = results[2].find("pmid").text
                                        else:
                                            project_pubmed_id = ''
                                            log.info("no publication results for project title in ENA")
                except:
                    log.info("no publication results for project title in ENA")
                    project_pubmed_id = ''
        if not project_pubmed_id or project_pubmed_id == '':
            if project_name:
                log.info("project name is %s:" % (project_name))
                url = rq.get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={project_name}')
                if url.status_code == STATUS_ERROR_CODE:
                    raise handle_errors.NotFoundENA(url, project_name)
                else:
                    xml_content = xm.fromstring(url.content)
                    try:
                        results = list()
                        result_list = xml_content.find("resultList")
                        for result in result_list:
                            results.append(result)
                        journal_title = results[0].find("journalTitle").text
                        if not journal_title or journal_title == '':
                            project_pubmed_id = ''
                            log.info("no publication results for project name in ENA")
                        else:
                            answer = input("A publication title has been found: %s.\nIs this the publication title associated with the GEO accession? [y/n]: " % (journal_title))
                            if answer.lower() in ['y',"yes"]:
                                project_pubmed_id = results[0].find("pmid").text
                            else:
                                journal_title = results[1].find("journalTitle").text
                                if not journal_title or journal_title == '':
                                    project_pubmed_id = ''
                                    log.info("no publication results for project name in ENA")
                                else:
                                    answer = input("An alternative publication title has been found: %s.\nIs this the publication title associated with the GEO accession? [y/n]: " % (journal_title))
                                    if answer.lower() in ['y', "yes"]:
                                        project_pubmed_id = results[1].find("pmid").text
                                    else:
                                        journal_title = results[2].find("journalTitle").text
                                        if not journal_title or journal_title == '':
                                            project_pubmed_id = ''
                                            log.info("no publication results for project name in ENA")
                                        else:
                                            answer = input("An alternative publication title has been found: %s.\nIs this the publication title associated with the GEO accession? [y/n]: " % (journal_title))
                                            if answer.lower() in ['y', "yes"]:
                                                project_pubmed_id = results[2].find("pmid").text
                                            else:
                                                project_pubmed_id = ''
                                                log.info("no publication results for project name in ENA")
                    except:
                        log.info("no publication results for project name in ENA")
                        project_pubmed_id = ''
        if not project_pubmed_id or project_pubmed_id == '':
            project_title = ''
            project_name = ''
            project_pubmed_id = ''
    return project_name,project_title,project_description,project_pubmed_id