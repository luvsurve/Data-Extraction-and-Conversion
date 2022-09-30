#import logging and testing libraries
import logging
import unittest
from urllib3.exceptions import HTTPError #Unit test error handling
log_format = '%(asctime)s:%(levelname)s:%(message)s'

logging.basicConfig(filename = 'logs.log', level = logging.DEBUG,
                    format = log_format)

"""Importing Program Libraries"""
#For extracting initial xml file content
from bs4 import BeautifulSoup 

#For handling http requests
import requests               

#For handling .zip file
from zipfile import ZipFile   

#For Buffered I/O implementation using internal memory
from io import BytesIO        

#For accessing file names
import os

#To handle xml files and create output csv files
import xmltodict, csv

logging.info('Libraries Loaded successfully')


"""Functions"""
def get_url_content(url):
  """Scans XML pointed by URL and 
  downloads required zip file"""
  #Gets xml content from url
  response = requests.get(url)
  if response.status_code == 200:
    xml_data = response.content
    logging.info('URL exists, xml content loaded successfully')
    #Parses xml content from data
    soup = BeautifulSoup(xml_data,"lxml-xml") 

    #Looks up for DLTINS string
    file_types = soup.find_all('str',string="DLTINS") 
  
    #Gets parent tag of DLTINS file type
    link_tag_parent = file_types[0].parent 

    #Gets required zip file link
    zip_link = link_tag_parent.find('str',
                                    {'name':'download_link'}).text
    logging.info(' .zip link found')

    #To extract file to local destination '/'
    get_zip_content(zip_link)
    logging.info(' .zip file downloaded and extracted')

  else:
    logging.error(f'URL error: {response.status_code}')
  
def get_zip_content(zip_link):
  """Downloads and extracts .zip file 
  using provided zipfile link"""
  #Gets zip file data through http request
  zip_resp = requests.get(zip_link)

  if zip_resp.status_code == 200:
    #Downloads .zip file as byte stream 
    zip = ZipFile(BytesIO(zip_resp.content)) 

    #Extracts downloaded .zip file
    zip.extractall("") 
  else:
    logging.error('Erroneous zip url')  
    raise HTTPError
    

def get_xml_file_name():
  """Returns .xml file name"""
  for file in os.listdir(): #Check directory
    if file[-4:] == ".xml": #locates .xml file
      return file           #returns located file
  else:
    raise FileNotFoundError

def xml_to_csv(file_name):
  """converts extracted xml file to csv"""
  #Opens extracted xml file and stores it as xmltodict object
  with open(file_name,'r',encoding='utf8') as xml_file:
    xml = xmltodict.parse(xml_file.read())

  #Creates output csv file to write xml data
  csvfile = open('data.csv','w',encoding='utf-8',newline='')
  csvfile_writer = csv.writer(csvfile)
  
  #Manually fed Header data
  header = ['FinInstrmGnlAttrbts.Id',
            'FinInstrmGnlAttrbts.FullNm',
            'FinInstrmGnlAttrbts.ClssfctnTp',
            'FinInstrmGnlAttrbts.CmmdtyDerivInd',
            'FinInstrmGnlAttrbts.NtnlCcy','Issr']

  #Writes header
  csvfile_writer.writerow(header)   
  
  #Performs remaining content extraction
  read_xml_rows(xml,csvfile_writer) 

def read_xml_rows(xml,csv_writer):
  """Extract rows from provided xml data 
  object and writes them onto csv file"""
  #Locates initial data store containing all required xml records
  data1 = xml['BizData']['Pyld']['Document'] #Temp variable
  data = data1['FinInstrmRptgRefDataDltaRpt']['FinInstrm']

  #keeps tract of records read(Optional)
  record_count = 0

  #Accessing individual records
  for record in data:
    #Getting main record name 
    rcd = [i for i in record.keys()][0]

    #Getting parameters corresponding to csv headers
    Id = record[rcd]['FinInstrmGnlAttrbts']['Id']
    Full_name = record[rcd]['FinInstrmGnlAttrbts']['FullNm']
    ClssfctnTp = record[rcd]['FinInstrmGnlAttrbts']['ClssfctnTp']
    CmmdtyDerivInd = record[rcd]['FinInstrmGnlAttrbts']['CmmdtyDerivInd']
    NtnlCcy = record[rcd]['FinInstrmGnlAttrbts']['NtnlCcy']
    Issr = record[rcd]['Issr']
    
    #Csv line to be written
    csv_line = [Id,Full_name,ClssfctnTp,CmmdtyDerivInd,NtnlCcy,Issr]

    #Writing line to csv file
    csv_writer.writerow(csv_line)
    
    #Record count update(Optional)
    record_count+=1
  logging.info(f'{record_count} records found and transferred to csv')


"""Main Program"""
#Initial xml file url
url = 'https://registers.esma.europa.eu/solr/esma_registers_\
firds_files/select?q=*&fq=publication_date:%5B2021-01\
-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent\
=true&start=0&rows=100'
logging.info('URL Loaded successfully')

#Get URL content, download and extract file
get_url_content(url)
logging.info('Function get_url_content executed successfully')

#Get file name to access xml content
file_name = get_xml_file_name()
if file_name:
  logging.info("Downloaded content found and ready for conversion")

  #Convert xml file to required output csv file
  xml_to_csv(file_name)
  logging.info("Conversion successful, outputfile generated")

else:
  logging.error("File not found or not downloaded")

logging.info("End of execution")
