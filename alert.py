import urllib2, time, smtplib
from bs4 import BeautifulSoup
from prettytable import PrettyTable

#Start SETTINGS
SETTINGS = {}
SETTINGS["GMAIL_USERNAME"] = "changeme"
#SETTINGS["GMAIL_USERNAME"] = False #To disable email updates
SETTINGS["GMAIL_PASSWORD"] = "changeme"
SETTINGS["ALERT_EMAILS"] = ["changeme", "changeme2"]
SETTINGS["REFRESH_RATE"] = 60
#End SETTINGS

def send_email(username, password, recipients, subject, body):
	try:
		gmail = smtplib.SMTP("smtp.gmail.com", 587)
		gmail.ehlo()
		gmail.starttls()
		gmail.login(username, password)
		gmail.sendmail(username, recipients, "From: " + username + "\nTo: " + ", ".join(recipients) + "\nSubject: " + subject + "\n\n" + body)
		gmail.close()
		return True
	except:
		return False

def eStatus():
	results = []

	try:
		aRequest = urllib2.Request("http://vtr.aec.gov.au/HouseDefault-20499.htm", headers={'User-Agent': 'Mozilla/5.0'})
		aPage = urllib2.urlopen(aRequest).read()
		aSoup = BeautifulSoup(aPage)
	except:
		return results

	answers = aSoup.find("table", { "id" : "datatable" })
	if not answers:
		return results

	rows = answers.find("tbody").find_all("tr")
	if not rows or len(rows) == 0:
		return results

	for row in rows:
		tmp = row.findAll("td")
		results.append([row.find("th").get_text(), tmp[0].get_text(), tmp[1].get_text()])

	results.sort(key=lambda results: results[1])
	return results

last = None
current = None
while 1:
	time.sleep(SETTINGS['REFRESH_RATE'])

	tmp = eStatus()
	if len(tmp) == 0:
		continue
	else:
		last = current
		current = tmp

	if last != current:
		table_results = PrettyTable()
		table_results.field_names =["Party", "Seats", "Close"]
		for row in reversed(current):
			table_results.add_row([row[0], row[1], row[2]])
		tmp = "\n\nResults Updated @ " + time.ctime() + "\n" + table_results.get_string()
		if SETTINGS["GMAIL_USERNAME"]:
			send_email(SETTINGS['GMAIL_USERNAME'], SETTINGS['GMAIL_PASSWORD'], SETTINGS['ALERT_EMAILS'], "Polling Updates!", tmp)
		print tmp

