######################################################
# 
# Libraries
#
######################################################

from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os


######################################################
# 
# App instance
#
######################################################

app = Flask(__name__)
app.secret_key = "He thrust every elf Far back on the shelf High up on the mountain From whence it came"

######################################################
# 
# Routes
#
######################################################

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@app.route('/focus')
def focus():
    return render_template('focus.html')

@app.route('/vba')
def vba():
    return render_template('vba.html')

@app.route('/useful')
def useful():
    return render_template('useful.html')

@app.route('/namecreator')
def namecreator():
    return render_template('namecreator.html')

@app.route('/openedgar')
def openedgar():
    return render_template('openedgar.html')

@app.route('/timelinehelper')
def timelinehelper():
    return render_template('timelinehelper.html')



@app.route('/scrape')
def scrape():
    #flash(request.args.get('url'), 'success')
    url = request.args.get('url')
    
    try:    
        response = requests.get(url)
        content = BeautifulSoup(response.text, 'lxml').prettify()
    except:
        flash('Failed to retrieve URL "%s"' % url, 'danger')
        content = ''

    return render_template('scrape.html', content=content)


@app.route('/cnmv')
def cnmv():


    from urllib.parse import urljoin
    from urllib.request import urlopen as uReq
    from bs4 import BeautifulSoup as soup
    import time
    import re

    n = True

    #------------------------------------------------------------------------------------------------------

    timestr = time.strftime("%Y%m%d")
    timestring = str(timestr)

    #------------------------------------------------------------------------------------------------------

    base_url = 'http://www.cnmv.es/Portal/Consultas/'
    my_url = "http://www.cnmv.es/Portal/Consultas/BusquedaUltimosDias.aspx?idPerfil=2&tipo=2&lang=en"

    #------------------------------------------------------------------------------------------------------

    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")

    itemsFromListsID = page_soup.find("a", text = re.compile('Significant Holdings and own shares'))
    whichIsIt = itemsFromListsID.get('id')
    trimForUse = whichIsIt.replace("_hlElemento","")

    itemsFromLists = page_soup.findAll("a", id=lambda value: value and value.startswith(trimForUse))

    cnmvresults = []

    #------------------------------------------------------------------------------------------------------

    cmnvfile = "CNMV_" + timestring + ".csv"
    
    for i in itemsFromLists:
        linksFromList = i.get('href')
        textsFromList = i.text.replace(",", "").strip()
        wholeLinks = urljoin(base_url, linksFromList)
        pureLinks = wholeLinks.replace("javascript:void(0)", " ").strip()
        
        row = (textsFromList + "," + pureLinks + "\n").split(",")
        cnmvresults.append(row)

    return render_template('cnmv.html', cnmvresults=cnmvresults, cmnvfile=cmnvfile)


@app.route('/edgardaily')
def edgardaily():

    fileDate = request.args.get('date')
    fileType = str(request.args.get('type'))

    from urllib.request import urlopen
    import re

    #fileDate = input("Please input the date in YYYYMMDD format (e.g. 20200122) : ")

    base_url = "https://www.sec.gov/Archives/edgar/daily-index/"
    CIK_search_url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK="
    dailyfilings = []
    edgarNameandLinks = []

    yearUrl = fileDate[:4]
    monthUrl = fileDate[4:-2]

    if 1 <= int(monthUrl) <= 3:
        QTR = "QTR1"

    if 4 <= int(monthUrl) <= 6:
        QTR = "QTR2"

    if 7 <= int(monthUrl) <= 9:
        QTR = "QTR3"

    if 10 <= int(monthUrl) <= 12:
        QTR = "QTR4"

    try:

        lines = urlopen(str(base_url) + str(yearUrl) + "/" + str(QTR) + "/" + "crawler." + fileDate + ".idx", timeout = 4).read().decode('ascii').split("\n")
        #lines = ','.join(str(v) for v in linelist)
        
        for line in lines:
            if " " + fileType + " " in line:

                edgarName = re.sub(r" " + str(fileType) + ".*","",line).replace(",","").strip()
                #edgarLink = re.sub(r".* http","http",line)
                edgarLink = line.strip().rsplit(" ", 1)[1]
                CIK = " ".join(line.split()).rsplit(" ", 4)[2]
                CIKLink = CIK_search_url + str(CIK)
                row = (edgarName + "," + CIK + "," + CIKLink + "," + fileType + "," + str(fileDate) + "," + edgarLink).split(",")
                dailyfilings.append(row)      
                
        if dailyfilings == []:
            row = ("No filling for " + fileType + " for this day: " + str(fileDate) + "," + "" + "," + "" + "," + "" + "," + "" + ",").split(",")
            dailyfilings.append(row)

    except:

        row = ("No index file found on sec.gov for this day: " + str(fileDate) +  ". If you are sure there should be one then please double check here: https://www.sec.gov/Archives/edgar/daily-index/" + "," + "" + "," + "" + "," + "" + "," + "" + ",").split(",")
        dailyfilings.append(row)

    return render_template('edgardaily.html', dailyfilings=dailyfilings)

@app.route('/edgarquarterly')
def edgarquarterly():

    fileDate = request.args.get('date')
    fileQTR = request.args.get('qtr')
    fileType = str(request.args.get('type'))

    from urllib.request import urlopen
    import re

    #fileDate = input("Please input the date in YYYYMMDD format (e.g. 20200122) : ")

    base_url = "https://www.sec.gov/Archives/edgar/full-index/"
    CIK_search_url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK="
    dailyfilings = []
    edgarNameandLinks = []

    yearUrl = fileDate[:4]
    monthUrl = fileDate[5:8]

   

    lines = urlopen(str(base_url) + str(fileDate) + "/" + str(fileQTR) + "/" + "crawler.idx", timeout = 4).read().decode('ascii').split("\n")
    #lines = ','.join(str(v) for v in linelist)
    
    for line in lines:
        if " " + fileType + " " in line:         
            edgarName = re.sub(r" " + str(fileType) + ".*","",line).replace(",","").strip()
            #edgarLink = re.sub(r".* http","http",line)
            edgarLink = line.strip().rsplit(" ", 1)[1]
            #CIK = " ".join(line.split()).rsplit(" ", 5)[3]
            #filingDate = " ".join(line.split()).rsplit(" ", 5)[4]
            CIK = " ".join(line.split()).rsplit(" ", 4)[2]
            filingDate = " ".join(line.split()).rsplit(" ", 4)[3]
            CIKLink = CIK_search_url + str(CIK)
            row = (edgarName + "," + CIK + "," + CIKLink + "," + fileType + "," + str(filingDate) + "," + edgarLink).split(",")
            dailyfilings.append(row)      
            
    if dailyfilings == []:
        row = ("No filling for " + fileType + " for this day: " + str(filingDate) + "," + "" + "," + "" + "," + "" + "," + "").split(",")
        dailyfilings.append(row)

    def Sort(dailyfilings):
        return(sorted(dailyfilings, key = lambda x: x[4]))

    sortedList = (Sort(dailyfilings))

    filingsNumber = len(sortedList)



    return render_template('edgarquarterly.html', sortedList=sortedList, filingsNumber=filingsNumber)

# render results to screen
@app.route('/results')
def results():



    urlnostrip = request.args.get('url')
    correct_url = False
    url = urlnostrip.strip()

    invval = 0

    equitylist = ["equity-common", "adr", "edr", "gdr", "etf", "exchange traded fund", "reit", "depository receipt", "investment company", "mutual fund", "units", "savings share", "common stock (royalty trust)", "master limited partnership", "stapled security", "equity-depositary receipt", "equity funds", "equity-preferred", "equity-reit", "equity-unit", "registered investment company", "equityfund", "preferred", "other-partnership"]
    fixedlist = ["abs-collateralized bond-debt obligation", "abs-mortgage backed security", "abs-other", "dco", "dcr", "debt", "derivative-equity", "derivative-foreign exchange", "derivative-interest rate", "loan", "short-term investment vehicle", "repurchase agreement", "right", "rights", "structured note", "warrant", "private fund"]

    eqval = 0
    fival = 0
    otval = 0

    tickerPlusCountry = ''

    if 'https://www.sec.gov/Archives/edgar/data/' and '.xml' in url and 'xslFormNPORT-P_X01/primary_doc.xml' not in url: #need .xml ending:
        correct_url = True
    
    else:
        
        flash('Failed to recornize URL "%s" as an NPORT-P xml file.' % url, 'danger')

        proTip = 'You didn\'t paste in the NPORT-P xml link for parsing, please try again...!'
        results = ''
        fundNameString = ''
        reportDateString = ''
        regCIK = ''
        totAssets = 0 #'' can't convert string to float
        csvname = ''
        tickerPlusCountry = ''
        counter = 0  #counter not declared error


    if correct_url:

        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'xml')

        fundName = soup.find("seriesName")
        fundNameString = fundName.text.replace('.','').replace("/","")

        if fundNameString == "NA":
            fundName = soup.find("regName")
            fundNameString = fundName.text.replace('.','').replace("/","")

        totAssets = soup.find("totAssets").text

        reportDate = soup.find("repPdDate")
        reportDateString = str(reportDate.text)

        regCIK = soup.find("regCik").text

        onlySecs = soup.findAll("invstOrSec")

        csvnamenostring = "NPORT_P__" + str(fundNameString) + "_" + reportDateString + ".csv"
        csvname = str(csvnamenostring)
        counter = 0

        header = "Issue name, ISIN, Share, Value, Long-Short, Asset category, Total assets:," + str(totAssets)

        results = []

        for i in onlySecs:


            issueNamesTextFirst = onlySecs[counter]
            issueNamesTextFirstTag = issueNamesTextFirst.find("name").text #because name tag would only return the name of the tag, FUCK
            issueNamesText = str(issueNamesTextFirstTag).replace("\n","").replace(",","")

            if issueNamesText == "N/A":
                issueNamesTextFirst = onlySecs[counter]
                issueNamesTextFirstTag = issueNamesTextFirst.find("title").text #because name tag would only return the name of the tag, FUCK
                issueNamesText = str(issueNamesTextFirstTag).replace("\n","").replace(",","")

            isinTextFirst = onlySecs[counter].isin
            isinTextStringer = str(isinTextFirst)
            isinText = isinTextStringer.replace('<isin value="','').replace('"/>','').replace('<nport:isin value="','')

            if isinText == "None":
                isinText = ""

            sharenumberTextFirst = onlySecs[counter].balance.text
            shareNumberText = str(sharenumberTextFirst).replace("\n","")   

            if shareNumberText == None:
                shareNumberText = ""

            valueUSDTextFirst = onlySecs[counter].valUSD.text
            valueUSDText = str(valueUSDTextFirst).replace("\n","")

            if valueUSDText == None:
                valueUSDText = 0

            invval += float(valueUSDText)

            tickerTextFirst = onlySecs[counter].ticker
            tickerTextStringer = str(tickerTextFirst)
            tickerText = tickerTextStringer.replace('<ticker value="','').replace('"/>','').replace('<nport:ticker value="','')

            if tickerText == "None":
                tickerText = ""
                countryText = ""
            else:
                countryTextFirst = onlySecs[counter].invCountry.text
                countryText = str(countryTextFirst).replace("\n","")

                if countryText == "None":
                    countryText = ""

            tickerPlusCountry = tickerText + "." + countryText

            if tickerPlusCountry == ".":
                tickerPlusCountry = ""

            payoffProfileTextFirst = onlySecs[counter].payoffProfile.text
            payoffProfileText = str(payoffProfileTextFirst).replace("\n","")

            if payoffProfileText == None:
                payoffProfileText = ""

            cusipTextFirst = onlySecs[counter].cusip.text
            cusipText = str(cusipTextFirst).replace("\n","")

            if cusipText == "N/A":
                cusipTextFirst = onlySecs[counter].other
                cusipText = str(cusipTextFirst).replace('<other otherDesc="Primary Identifier" value="','').replace('"/>','').replace("\n","")           

            if cusipText == "000000000":
                cusipText = ""

            sedolText = ""

            if len(cusipText) == 7:
                sedolText = cusipText
                cusipText = ""

            if onlySecs[counter].assetCat == None:
                assetCategoryText = onlySecs[counter].assetConditional["desc"].replace(",","")
            else:
                assetCategoryTextFirst = onlySecs[counter].assetCat.text
                assetCategoryText = str(assetCategoryTextFirst).replace("\n","")

            if assetCategoryText == 'EC':
                assetCategoryText = 'Equity-common'

            if assetCategoryText == 'DBT':
                assetCategoryText = 'Debt'

            if assetCategoryText == 'RA':
                assetCategoryText = 'Repurchase Agreement'

            if assetCategoryText == 'STIV':
                assetCategoryText = 'Short-term investment vehicle'

            if assetCategoryText == 'ABS-MBS':
                assetCategoryText = 'ABS-mortgage backed security'

            if assetCategoryText == 'ABS-O':
                assetCategoryText = 'ABS-other'

            if assetCategoryText == 'ABS-CDBO':
                assetCategoryText = 'ABS-collateralized bond-debt obligation'

            if assetCategoryText == 'SN':
                assetCategoryText = 'Structured note'

            if assetCategoryText == 'LON':
                assetCategoryText = 'Loan'

            if assetCategoryText == 'EP':
                assetCategoryText = 'Equity-preferred'

            if assetCategoryText == 'DFE':
                assetCategoryText = 'Derivative-foreign exchange'

            if assetCategoryText == 'DIR':
                assetCategoryText = 'Derivative-interest rate'

            if assetCategoryText == 'DE':
                assetCategoryText = 'Derivative-equity'

            if assetCategoryText == 'RE':
                assetCategoryText = 'REIT'

            if assetCategoryText == 'DO':
                assetCategoryText = 'Warrant'

            if assetCategoryText == 'ABS-CBDO':
                assetCategoryText = 'ABS-collateralized bond-debt obligation'

            if assetCategoryText == None:
                assetCategoryText = ""


            

            if assetCategoryText.lower() in equitylist and payoffProfileText == "Long":
                eqval += float(valueUSDText)

            elif assetCategoryText.lower()  in fixedlist and payoffProfileText == "Long":
                fival += float(valueUSDText)

            elif assetCategoryText.lower()  not in equitylist and assetCategoryText.lower()  not in fixedlist and payoffProfileText == "Long":
                otval += float(valueUSDText)


            """
            issuerCategoryTextFirst = issuerCategory[counter]
            issuerCategoryText = issuerCategoryTextFirst.text

            if issuerCategoryText == 'CORP':
                issuerCategoryText = 'Corporate'

            if issuerCategoryText == 'MUN':
                issuerCategoryText = 'Municipal'

            if issuerCategoryText == 'RF':
                issuerCategoryText = 'Registered fund'

            if issuerCategoryText == 'USGSE':
                issuerCategoryText = 'U.S. government sponsored entity'

            if issuerCategoryText == 'USGA':
                issuerCategoryText = 'U.S. government agency'

            if issuerCategoryText == 'UST':
                issuerCategoryText = 'U.S. Treasury'

            """

            args = []
            
            
            row = (str(issueNamesText) + "," + isinText + "," + shareNumberText + "," + valueUSDText + "," + payoffProfileText + "," + assetCategoryText + "," + tickerPlusCountry + ',' + cusipText + "'" + ',' + sedolText + "'").split(",")

            results.append(row)

            counter = counter + 1
            proTip = ''

        if onlySecs == []:
            flash('This report is empty, couldn\'t parse contents! "%s"' % url, 'danger')
            proTip = 'This error means that the report contains no issues! The Fund could be under liquidation or merger, please investigate...'
            
    totAssets = '{:,}'.format(float(totAssets))
    invval = '{:,}'.format(invval)
    eqval = '{:,}'.format(eqval)
    fival = '{:,}'.format(fival)
    otval = '{:,}'.format(otval)


    return render_template('results.html', proTip=proTip, results=results, fundNameString=fundNameString, reportDateString=reportDateString, regCIK=regCIK, totAssets=totAssets, csvname=csvname, tickerPlusCountry=tickerPlusCountry, counter=counter, invval=invval, eqval=eqval, fival=fival, otval=otval)




@app.route('/danske')
def danskeFunds():

    from urllib.request import urlopen as uReq
    from bs4 import BeautifulSoup as soup
    import urllib.request



    danskeFunds = []

    # THIS IS THE DE PART

    header_counter = 1
    de_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=117"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=117&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=117&p_nFund=" + id

        full_link_for_source = "https://www.danskeinvest.de/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id
        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
            
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        de_counter = de_counter + 1
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)

        #print(".de | Scraping " + fundname_text + " is done!")
    
    
    print("")
    print("I have successfully saved info for: " + str((de_counter)) + " funds' TNA from the .de page.")
    print("")

    # THIS IS THE END OF THE DE PART

    # THIS IS THE DK PART

    header_counter = 1
    dk_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=75"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.dk/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
         
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        dk_counter = dk_counter + 1
        
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)
        


    # THIS IS THE END OF THE DK PART

    # THIS IS THE DK2 PART

    header_counter = 1
    dk2_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=31"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.dk/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})

            
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        dk2_counter = dk2_counter + 1
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)
        
        #print(".dk | Scraping " + fundname_text + " is done!")
        
        
        
    print("")
    print("I have successfully saved info for: " + str((dk2_counter)) + " funds' TNA from the .dk page.")
    print("")


    # THIS IS THE END OF THE DK2 PART

    # THIS IS THE DK3 PART

    header_counter = 1
    dk3_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=66"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.dk/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
        
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        dk3_counter = dk3_counter + 1
        
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)
        
        #print(".dk | Scraping " + fundname_text + " is done!")
        
        
        
    print("")
    print("I have successfully saved info for: " + str((dk3_counter)) + " funds' TNA from the .dk page.")
    print("")

    # THIS IS THE END OF THE DK3 PART

    # THIS IS THE DK4 PART

    header_counter = 1
    dk4_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=32"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=75&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.dk/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})

            
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        dk4_counter = dk4_counter + 1
        
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)
        
        #print(".dk | Scraping " + fundname_text + " is done!")
        
        
        
    print("")
    print("I have successfully saved info for: " + str((dk4_counter)) + " funds' TNA from the .dk page.")
    print("")

    # THIS IS THE END DK4 PART


    # THIS IS THE FI PART

    my_url = "https://www.danskeinvest.fi/web/show_page.prices_return?p_nId=61&p_nFundGroup=61&p_nTab=2"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")
    fund_list_table = page_soup.find("div", {"class":"fundvaelger"})

    list_counter = 1

    fund_list = fund_list_table.findAll("option")
    fund_counter = len(fund_list)

    while fund_counter > list_counter: 
        fund_from_list = fund_list[list_counter]
        fund_list_text = fund_from_list.text.replace(",", "").strip()
        
        fund_link_from_list = fund_list[list_counter]
        fund_link_text = fund_link_from_list["value"]
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?" + fund_link_text 
        
        
        full_link_for_nav_text = "https://www.danskeinvest.fi/web/show_fund.stamdata?" + fund_link_text
        
        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        
        isin_locate = page_soup_NAV.find("table", {"id":"stamdataTabel"})
        isin_selector = isin_locate.find("td", {"class":"tTop tleftbold tOdd bordered_last"})
        isin_text = isin_selector.text.replace(",", "").strip()
        
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
        
            
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        
        
        row = (fund_list_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)

        #print(".fi | Scraping " + fund_list_text + " is done!")
        
        list_counter = list_counter + 1


    print("")
    print("I have successfully saved info for: " + str((len(fund_list))) + " funds' TNA from the .fi page.")
    print("")

    fi_counter = len(fund_list)

    # THIS IS THE END OF THE FI PART

    
    return render_template('danske.html', danskeFunds=danskeFunds)



@app.route('/danske2')
def danskeFunds2():

    from urllib.request import urlopen as uReq
    from bs4 import BeautifulSoup as soup
    import urllib.request



    danskeFunds = []

    # THIS IS THE LU PART

    header_counter = 1
    lu_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=81"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=81&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=81&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.lu/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
        
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        lu_counter = lu_counter + 1
        
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)
        
        #print(".lu | Scraping " + fundname_text + " is done!")
        
        
        
    print("")
    print("I have successfully saved info for: " + str(lu_counter) + " funds' TNA from the .lu page.")
    print("")

    # THIS IS THE END OF THE LU PART

    # THIS IS THE NO PART

    header_counter = 1
    no_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=90"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=90&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=90&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.no/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
        
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        no_counter = no_counter + 1 
        
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)
        
        #print(".no | Scraping " + fundname_text + " is done!")
        
        
    print("")
    print("I have successfully saved info for: " + str((no_counter)) + " funds' TNA from the .no page.")
    print("")

    # THIS IS THE END OF THE NO PART

    # THIS IS THE NO 2 PART

    header_counter = 1
    no2_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=89"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=90&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=90&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.no/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
        
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        no2_counter = no2_counter + 1 
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)
        
        #print(".no | Scraping " + fundname_text + " is done!")
        
        
    print("")
    print("I have successfully saved info for: " + str((no2_counter)) + " funds' TNA from the .no page.")
    print("")
        

    # THIS IS THE END OF THE NO 2 PART

    # THIS IS THE SE PART

    header_counter = 1
    se_counter = 0

    my_url = "https://www.danskeinvest.lu/w/show_list.products?p_nId=1181&p_nFundGroup=74"

    # This needed for some pages against the 403 error
    req = urllib.request.Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

    page_html = urllib.request.urlopen(req).read()

    # We first locate all Fund's name and link
    page_soup = soup(page_html, "html.parser")

    fund_list_table = page_soup.tbody


    containers = fund_list_table.findAll('tr', {"class":"table-data product-element js-label"})


    for container in containers:
        id = container["id"]
        fundname = container.findAll("span", {"class":"headline-text"})
        fundname_text = fundname[0].text.replace(",", "").strip()
        isin_locate = container.findAll("td", {"class":"table-data-value"})
        isin_text = isin_locate[1].text.replace(",", "").strip()
        
        
        full_link_for_name_text = "https://www.danskeinvest.fi/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id
        
        full_link_for_nav_text = "https://www.danskeinvest.lu/web/show_fund.stamdata?p_nId=1181&p_nFundgroup=74&p_nFund=" + id
        
        full_link_for_source = "https://www.danskeinvest.se/web/show_fund.produkt?p_nId=1181&p_nFundgroup=74&p_nFund=" + id

        
        # Get the NAV for each Fund
        my_url_02 = str(full_link_for_nav_text)
        req = urllib.request.Request(my_url_02, headers={'User-Agent': 'Mozilla/5.0'})
        page_html_NAV = urllib.request.urlopen(req).read()
        page_soup_NAV = soup(page_html_NAV, "html.parser")
        fund_NAV_list = page_soup_NAV.find("table", {"id":"dagenstalTabel"})
        
        
        
        #for nav_info in fund_NAV_list:
        NAV_four_info = fund_NAV_list.findAll("tr")
            
        NAV_four_info_TA_date = fund_NAV_list.find("td", {"class":"tTop tleft tOdd"})
        NAV_four_info_TA_val = fund_NAV_list.find("td", {"class":"tTop trightbold tOdd bordered_last"})
        
        if NAV_four_info_TA_date == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_date_text = NAV_four_info_TA_date.text.replace(",", "").strip()
        

        if NAV_four_info_TA_val == None:
            TA_date_text = "NO INFO ON WEBSITE"
        else:
            TA_val_text = NAV_four_info_TA_val.text.replace(",", "").strip()
        
        se_counter = se_counter + 1
        
        row = (fundname_text + "," + isin_text + "," + TA_date_text + "," + TA_val_text + "\n").split(",")
        danskeFunds.append(row)

    return render_template('danske2.html', danskeFunds=danskeFunds)


@app.route('/currency')
def currency():

    from urllib.request import urlopen as uReq
    from bs4 import BeautifulSoup as soup

    #flash(request.args.get('url'), 'success')
    date = request.args.get('date')
   
    try:    
        base_url = "http://www.xe.com/currencytables/?from=USD&date="
        my_url = base_url + str(date)
        uClient = uReq(my_url)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        containers = page_soup.findAll("tbody")
        container = containers[0]
        rows = container.findAll("tr")
        value = container.findAll("td", {"class":"historicalRateTable-rateHeader"})

        eurName = rows[1].a.text
        gbpName = rows[2].a.text
        brlName = rows[22].a.text
        chfName = rows[7].a.text
        jpyName = rows[9].a.text
        dkkName = rows[31].a.text
        nokName = rows[28].a.text
        sekName = rows[19].a.text
        audName = rows[4].a.text
        cadName = rows[5].a.text
        hkdName = rows[15].a.text
        zarName = rows[17].a.text
        clpName = rows[39].a.text
        inrName = rows[3].a.text
        lacName = "LAC"
        croName = "CRO"
        myrName = rows[8].a.text
        sgdName = rows[6].a.text
        nzdName = rows[11].a.text
        phpName = rows[18].a.text
        idrName = rows[20].a.text
        plnName = rows[34].a.text
        arsName = rows[41].a.text
        mxnName = rows[16].a.text
        ronName = rows[53].a.text
        czkName = rows[42].a.text
        thbName = rows[12].a.text
        hufName = rows[13].a.text
        rubName = rows[30].a.text
        usdName = "USD"

        eurValue = value[3].text
        gbpValue = value[5].text
        brlValue = value[45].text
        chfValue = value[15].text
        jpyValue = value[19].text
        dkkValue = value[63].text
        nokValue = value[57].text
        sekValue = value[39].text
        audValue = value[9].text
        cadValue = value[11].text
        hkdValue = value[31].text
        zarValue = value[35].text
        clpValue = value[79].text
        inrValue = value[7].text
        lacValue = float(inrValue)*100000
        croValue = float(inrValue)*10000000
        myrValue = value[17].text
        sgdValue = value[13].text
        nzdValue = value[23].text
        phpValue = value[37].text
        idrValue = value[41].text
        plnValue = value[69].text
        arsValue = value[83].text
        mxnValue = value[33].text
        ronValue = value[107].text
        czkValue = value[85].text
        thbValue = value[25].text
        hufValue = value[27].text
        rubValue = value[61].text
        usdValue = 1.0000000000

        currency = []
        row = (eurName + "," + eurValue).split(",")
        currency.append(row)
        row = (gbpName + "," + gbpValue).split(",")
        currency.append(row)
        row = (brlName + "," + brlValue).split(",")
        currency.append(row)
        row = (chfName + "," + chfValue).split(",")
        currency.append(row)
        row = (jpyName + "," + jpyValue).split(",")
        currency.append(row)
        row = (dkkName + "," + dkkValue).split(",")
        currency.append(row)
        row = (nokName + "," + nokValue).split(",")
        currency.append(row)
        row = (sekName + "," + sekValue).split(",")
        currency.append(row)
        row = (audName + "," + audValue).split(",")
        currency.append(row)
        row = (cadName + "," + cadValue).split(",")
        currency.append(row)
        row = (hkdName + "," + hkdValue).split(",")
        currency.append(row)  
        row = (zarName + "," + zarValue).split(",")
        currency.append(row)
        row = (clpName + "," + clpValue).split(",")
        currency.append(row)
        row = (inrName + "," + inrValue).split(",")
        currency.append(row)
        row = (lacName + "," + str(lacValue)).split(",")
        currency.append(row)
        row = (croName + "," + str(croValue)).split(",")
        currency.append(row)
        row = (myrName + "," + myrValue).split(",")
        currency.append(row)
        row = (sgdName + "," + sgdValue).split(",")
        currency.append(row)
        row = (nzdName + "," + nzdValue).split(",")
        currency.append(row)
        row = (phpName + "," + phpValue).split(",")
        currency.append(row)
        row = (idrName + "," + idrValue).split(",")
        currency.append(row)
        row = (plnName + "," + plnValue).split(",")
        currency.append(row)
        row = (arsName + "," + arsValue).split(",")
        currency.append(row)
        row = (mxnName + "," + mxnValue).split(",")
        currency.append(row)
        row = (ronName + "," + ronValue).split(",")
        currency.append(row)
        row = (czkName + "," + czkValue).split(",")
        currency.append(row)
        row = (thbName + "," + thbValue).split(",")
        currency.append(row)
        row = (hufName + "," + hufValue).split(",")
        currency.append(row)
        row = (rubName + "," + rubValue).split(",")
        currency.append(row)
        row = (usdName + "," + str(usdValue)).split(",")
        currency.append(row)
       


    except:
        flash('Failed to retrieve date, now it has this value: "%s", to query a certain date please use this link: /currency?date=2019-10-31' % date, 'danger')
        currency = ''

    return render_template('currency.html', currency=currency, date=date)


######################################################
# 
# Run app
#
######################################################

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True, threaded=True)

"""
app = Flask(__name__)
app.secret_key = 'ghdjrit8564hnbvn834z3hed/'

"""