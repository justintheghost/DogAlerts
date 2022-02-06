# DogAlerts
Sends alerts whenever new pups become available for adoption at Wrightway Rescue!

# Components
* Scrape Wrightway Rescue website and identify when new pups are added (Python requests and BeautifulSoup)
* Send SMS message with link to new pup(s) (Python Twilio API)
* Schedule function to run on a schedule (Google Cloud Serverless + Pub/Sub)