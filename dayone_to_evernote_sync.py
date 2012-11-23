#import modules
import os, sys, inspect, glob, re, fnmatch, getpass, smtplib, plistlib, unicodedata, codecs, datetime, time
# sys.setdefaultencoding is cancelled by site.py
reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')
from time import strftime #ADDED
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"lib")))
if cmd_subfolder not in sys.path:
     sys.path.insert(0, cmd_subfolder)

import markdown2

#functions
def file_exists(filename):
    '''
    a file exists if you can open and close it
    '''
    try:
        f = open(filename)
        f.close()
        return True
    except:
        return False

now = datetime.datetime.now()
today = now.strftime("%m/%d/%Y")
processed = 0
#look for sync_list.xml in the same directory as this script. if it is not found, ask for user input
if file_exists('sync_list.xml'):
    print ("sync_list.xml exists. Using information stored there.")   #TEST TO BE REMOVED
else:
    #ask for full path to dayone entries, save as var filepath
    fpath = raw_input("Please enter the FULL filepath to the directory where your Day One Journal entries are stored, or hit Enter to use default Dropbox directory: ")
    if fpath == "":
        filepath = os.path.expanduser('~/Dropbox/Apps/Day One/Journal.dayone/entries')
    else:
        filepath = fpath
    #ask for evernote email address, save as var enmail
    enmail = raw_input("Please enter your Evernote email address: ")
    while not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", enmail):
        enmail = raw_input("Please enter a valid Evernote email address: ")
    #ask for gmail email address, save as var gmailadd
    gmailadd = raw_input("Please enter your Gmail address: ")
    while not re.match(r"^[A-Za-z0-9\.\+_-]+@gmail.com*$", gmailadd):
        gmailadd = raw_input("Please enter a valid Gmail address: ")
    #ask for evernote notebook to store notes in, if empty ignore, save as var ennotebook
    bookinput = raw_input("Enter the name of the notebook here, or hit Enter to use default: ")
    if bookinput != "":
        ennotebook = "@" + bookinput
    else:
        ennotebook = ""
    #ask for tags to add to note as coma-delim list, if empty ignore, save as var entags
    taginput = raw_input("Enter any tags separated by commas, or hit Enter for no tags: ")
    if taginput != "":
        etags = [x.strip() for x in taginput.split(',')]
    else:
        entags = ""
    print ("this is your path: " + filepath)
    print ("this is your Evernote email: " + enmail)
    print ("this is your Gmail: " + gmailadd)
    if 'ennotebook' in locals():
        print ("this is your notebook: " + ennotebook)
    else:
        print ("You are using your default notebook")
    if 'entags' != "":  
        entags = '#' + ' #'.join(etags) 
        print ("Below are your tags: ") 
        print (entags)  
    else: 
        print ("You are using no tags")

    #create sync_list.xml in same directory as script
    root = ET.Element("root")

    #add <key>filepath</key><string> var filepath
    path = ET.SubElement(root, "filepath")
    path.set("name", "Day One entries filepath")
    path.text = filepath
    #add <key>Evernote Email</key><string> var enmail
    mail = ET.SubElement(root, "enmail")
    mail.set("name", "Evernote email")
    mail.text = enmail
    #add <key>Gmail Address</key><string> var gmailadd
    gmail = ET.SubElement(root, "gmailadd")
    gmail.set("name", "Gmail Address")
    gmail.text = gmailadd
    #add <key>Evernote Notebook</key><string> var ennotebook
    notebook = ET.SubElement(root, "ennotebook")
    notebook.set("name", "Evernote Notebook")
    notebook.text = ennotebook
    #add <key>Evernote Tags</key><dict>, for each tag extracted from coma-delim list create key with incrementing number suffix. ie. <key>Tag1</key><string>, <key>Tag2</key><string>, <key>Tag3</key><string> etc.
    tags = ET.SubElement(root, "entags")
    tags.set("name", "Evernote Tags")
    tags.text = entags  #THIS RETURNS ERROR WITH SPACES
    #add <key> Already Synced Entries</key><dict>, <key>UUID1</key><string>
    synced = ET.SubElement(root, "synced")
    synced.set("name", "Already Synced")
    sfile = ET.SubElement(synced, "sfile")
    sfile.set("date", today)
    sfile.text = "firstsync"

    tree = ET.ElementTree(root)
    tree.write("sync_list.xml")

#no matter what, ask for the user's gmail password to configure the smtplib to send email. do not store this variable, instead, ask for it each time it is run.
gmpass = getpass.getpass("Please enter your Gmail password. This will only be stored for the current session: ")
#if sync_list.xml exists get the above variables from the list
tree = ET.parse("sync_list.xml")
root = tree.getroot()

for elem in root.findall('filepath'):
    filepath = elem.text
for elem in root.findall('enmail'):
    enmail = elem.text
for elem in root.findall('gmailadd'):
    gmailadd = elem.text
for elem in root.findall('ennotebook'):
    ennotebook = elem.text
for elem in root.findall('entags'):
    entags = elem.text
for elem in root.findall('sfile'):
    synced = elem.text
dcheck = 0
for elem in root.findall('synced/sfile'):
  fdate = elem.attrib.get('date')
  if fdate == today:
    dcheck += 1
#if sync_list.xml exists get the list of (UUIDs) $entries that have already been synced, and exclude them from the current query. If no UUID's exist in sync_list.xml, ignore
synclimit = 250 - dcheck #default
print "dcheck " + str(dcheck)
print "synclimit " + str(synclimit)
if synclimit == 0:
    print "Sorry, you've reached your limit for file syncing today. The limit is reset by Evernote each night at 12:00 a.m."
    sys.exit()
synclimit = int(raw_input("How many files do you want to sync today? You have a max amount of " + str(synclimit) + " left today: "))
#get the list of all file names (UUID#.doentry) within var filepath that are NOT listed in sync_list.xml, if sync_list.xml does not exist, get all files (*.doentry) in var filepath
    #FOR EACH file name, open as xml document and get the data
tree = ET.parse("sync_list.xml")
#Thanks to unutbu http://stackoverflow.com/users/190597/unutbu
root = tree.getroot()
synced = [elt.text for elt in root.findall('synced/sfile')]
for filename in os.listdir(filepath):
    if processed >= synclimit:
        print "You've successfully synced " + str(synclimit) + " files."
        sys.exit()
    else:
        if fnmatch.fnmatch(filename, '*.doentry') and filename not in synced:
            filename = os.path.join(filepath, filename)
    #Thanks Martijn Pieters http://stackoverflow.com/users/100297/martijn-pieters
            result = plistlib.readPlist(filename)
            t = result['Creation Date']
            docreationdate = t.strftime('%m/%d/%Y') #ADDED
            entry = result['Entry Text']
            donotecontent = markdown2.markdown(entry)
            if result['Starred'] == True:
              dostarred = "#DayOne Starred"
            else:
              dostarred = ""
            dofilename = result['UUID'] + ".doentry"
            if result.get('Weather', None):
              weather = result['Weather']
            else:
                weather = ""
            if result.get('Celsius', None):
              dotempcel = weather['Celsius'] + '&#xb0;'
            else:
                dotempcel = ""
            if result.get('Description', None):
              doweatherdesc = weather['Description']
            else:
                doweatherdesc = ""
            if result.get('Fahrenheit', None):
              dotempfah = weather['Fahrenheit'] + '&#xb0;'
            else:
              dotempfah = ""
            if result.get('Location', None):
              location = result['Location']
            else:
                location = ""
            if result.get('Administrative Area', None):
              dolocarea = location['Administrative Area'] + ', '
            else:
                dolocarea =""
            if result.get('Country', None):
              doloccountry = location['Country']
            else:
                doloccountry = ""
            if result.get('Locality', None):
              doloccity = location['Locality'] + ', '
            else:
                doloccity = ""
            if result.get('Longitude', None):
              doloclong = location['Longitude']
            else:
                doloclong = ""
            if result.get('Latitude', None):
              doloclat = location['Latitude']
            else:
                doloclat = ""
            if result.get('Place Name', None):
              dolocadd = location['Place Name'] + ', '
            else:
                dolocadd = ""
              
            #Thanks to RocketDonkey http://stackoverflow.com/users/1009277/rocketdonkey
            if result.get('Tags', None):
                dtags = result["Tags"]
                dotags = '#' + ' #'.join(dtags)
            else:
                dotags = ""
            if result.get('Time Zone', None):
                dotimezone = result["Time Zone"]
            else:
                dotimezone = ""
                
            #create an email
                # SEND TO var enmail

            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Day One Entry: ' + docreationdate + ' ' + ennotebook + ' ' + entags + ' ' + dotags + ' ' + dostarred
            msg['From'] = gmailadd
            msg['To'] = enmail
            html = donotecontent + '<br /><br />' + dotempfah + ' ' + doweatherdesc + '<br /><br />' + dolocadd + doloccity + dolocarea + doloccountry
            part1 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
            msg.attach(part1)
                # SENT FROM var gmailadd
                # SMTP pass var gmpass
            gmail_pwd = gmpass
            smtpserver = smtplib.SMTP("smtp.gmail.com",587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo
            smtpserver.login(gmailadd, gmail_pwd)
                # SUBJECT Day One Journal Entry: var docreationdate, if var ennotebook is not empty @ennotebook, if var entags is not empty, explode list of each individual tag as #tag1 #tag2 #tag3, if var dostarred exists #dostarred

                #Send email
            # sent = 0
            # while sent < 3:
            #     try:
            #         smtpserver.sendmail(gmailadd, enmail, msg.as_string())
            #         smtpserver.quit()
            #     except Exception, e:
            #         print "Unable to send email. Error: %s" % str(e)
            #         print "Waiting one minute before trying again."
            #         time.sleep(60)
            #         sent += 1
            # continue
            smtpserver.sendmail(gmailadd, enmail, msg.as_string())
            smtpserver.quit()

            #Add dofilename to sync_list.xml as incremented <key>UUID#</key>
            #Thanks to J.F. Sebastian http://stackoverflow.com/users/4279/j-f-sebastian
            tree = ET.parse('sync_list.xml')
            synced = tree.find('synced')
            sfile = ET.SubElement(synced, "sfile", date=today)
            sfile.text = dofilename

            tree.write('sync_list.xml', encoding='utf-8', xml_declaration=True)
            #Thanks Martijn Pieters http://stackoverflow.com/users/100297/martijn-pieters
            processed += 1

            print 'Synced ' + dofilename + '....>'

    #END FOR EACH LOOP
print 'done!'
#END FILE