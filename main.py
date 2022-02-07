import requests
from bs4 import BeautifulSoup
from datetime import datetime
from twilio.rest import Client
import utils

# Scrapes Wrightway/Petango site and returns all animal IDs
def get_all_animals_from_site():
    #petango_soup = BeautifulSoup(open("response.txt").read(),'html.parser')
    petango_url = "https://ws.petango.com/webservices/adoptablesearch/wsAdoptableAnimals.aspx?species=Dog&gender=A&agegroup=UnderYear&location=&site=&onhold=A&orderby=name&colnum=3&css=http://ws.petango.com/WebServices/adoptablesearch/css/styles.css&authkey=io53xfw8b0k2ocet3yb83666507n2168taf513lkxrqe681kf8&recAmount=&detailsInPopup=No&featuredPet=Include&stageID=&wmode=opaque"
    petango_url_response = requests.get(url=petango_url)
    petango_soup = BeautifulSoup(petango_url_response.text, 'html.parser')
    petango_table_all_animals = petango_soup.find("table",{"id":"tblSearchResults"})

    return petango_table_all_animals

def get_all_animal_ids_from_site(all_animals):
    animal_id_all = all_animals.find_all("div", {"class":"list-animal-id"})
    animal_id_all_list = [int(i.getText()) for i in animal_id_all]
    return animal_id_all_list

# Identifies which animal IDs are new, returns list of new animal IDs
def identify_new_animal_ids(all_animals):
    # Check IDs in Database and compare to id_list
    # if there are any IDs in the id_list that aren't in the database, those are new
    all_animal_ids_from_site = get_all_animal_ids_from_site(all_animals)
    existing_animal_ids = get_existing_animal_ids()
    new_animal_id_list = list(set(all_animal_ids_from_site) - set(existing_animal_ids))

    return new_animal_id_list


def get_new_animal_info(all_animals, new_animal_id_list):
    new_animal_info_all = []
    
    all_animals_result_set = all_animals.find_all("td",{"class":"list-item"})
    for animal in all_animals_result_set:
        if animal.find("div",{"class":"list-animal-id"}) is not None:
            animal_id = animal.find("div",{"class":"list-animal-id"})
            animal_id_int = int(animal_id.getText())
            if animal_id_int in new_animal_id_list:
                name = animal.find("div", {"class":"list-animal-name"}).getText()
                species = animal.find("div", {"class":"list-anima-species"}).getText()
                gender = animal.find("div", {"class":"list-animal-sexSN"}).getText()
                breed = animal.find("div", {"class":"list-animal-breed"}).getText()
                age = animal.find("div", {"class":"list-animal-age"}).getText()
                image_url = animal.find("img", {"class":"list-animal-photo"})['src']
                new_animal_info = {"animal_id": animal_id_int
                    , "name": name
                    , "species":species
                    , "gender": gender
                    , "breed": breed
                    , "age": age
                    , "details_url": f"https://ws.petango.com/webservices/adoptablesearch/wsAdoptableAnimalDetails.aspx?id={animal_id_int}"
                    , "image_url": image_url
                }
                new_animal_info_copy = new_animal_info.copy()
                new_animal_info_all.append(new_animal_info_copy)
    return new_animal_info_all

def get_existing_animal_ids():
    query = "SELECT dog_id FROM dog_alerts.dogs"
    existing_animal_ids = utils.execute_select_query(query)
    existing_animal_ids_clean = [i[0] for i in existing_animal_ids]

    return existing_animal_ids_clean

def send_sms(new_animal_info):          
    message_body = f"Petunia Alert! There are {str(len(new_animal_info))} new pups available at Wrightway Rescue."

    for animal in new_animal_info:
        message_body = message_body + f"""
        Name: {animal['name']}
        Gender: {animal['gender']}
        Link: {animal['details_url']}
        """
    twilio_account_sid = utils.access_secret_version("twilio_account_sid")
    twilio_auth_token = utils.access_secret_version("twilio_auth_token")

    client = Client(twilio_account_sid, twilio_auth_token)
    numbers = ['+12244064823','+12174930473']
    for number in numbers:
        try:
            message = client.messages \
            .create(
                body=message_body,
                from_='+19035009230',
                to=number
            )
            print(message.sid)
        except Exception as e:
            print(f"Message failed with error message: {e}")

def add_new_animals_to_database(new_animal_id_list):
    data = [(i, datetime.now(), datetime.now()) for i in new_animal_id_list]
    try:
        utils.execute_multiple_row_insert(data)
        print("Added new animals to database successfully!")
    except Exception as e:
        print(f"Failed to write new animals to database with error: {e}")

def main(request):
    all_animals = get_all_animals_from_site()
    new_animal_id_list = identify_new_animal_ids(all_animals)
    new_animal_info = get_new_animal_info(all_animals, new_animal_id_list)

    if len(new_animal_id_list) > 0:
        send_sms(new_animal_info)
        add_new_animals_to_database(new_animal_id_list)
    else:
        print("No new pups :(")

    return f'Hello World'
def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <https://flask.palletsprojects.com/en/1.1.x/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'    