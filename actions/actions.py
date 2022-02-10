# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet,AllSlotsReset

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import json
import smtplib
  

#Read the Zomato data
ZomatoData = pd.read_csv('zomato.csv',encoding= 'unicode_escape')
ZomatoData = ZomatoData.drop_duplicates().reset_index(drop=True)
WeOperate = ['New Delhi', 'Gurgaon', 'Noida', 'Faridabad', 'Allahabad', 'Bhubaneshwar', 'Mangalore', 'Mumbai', 'Ranchi', 'Patna', 'Mysore', 'Aurangabad', 'Amritsar', 'Puducherry', 'Varanasi', 'Nagpur', 'Vadodara', 'Dehradun', 'Vizag', 'Agra', 'Ludhiana', 'Kanpur', 'Lucknow', 'Surat', 'Kochi', 'Indore', 'Ahmedabad', 'Coimbatore', 'Chennai', 'Guwahati', 'Jaipur', 'Hyderabad', 'Bangalore', 'Nashik', 'Pune', 'Kolkata', 'Bhopal', 'Goa', 'Chandigarh', 'Ghaziabad', 'Ooty', 'Gangtok', 'Shimla']

def RestaurantSearch(City,Cuisine,Budget):
    if Budget == 'Low':
         TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
         TEMP = TEMP.loc[TEMP['Average Cost for two'] <= 300,]
         TEMP = TEMP.sort_values("Aggregate rating",ascending=False)
         return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]
    elif Budget == 'Medium':
         TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
         TEMP = TEMP.loc[TEMP['Average Cost for two'] >= 300,]
         TEMP = TEMP.loc[TEMP['Average Cost for two'] <= 700,]
         TEMP = TEMP.sort_values("Aggregate rating",ascending=False)
         return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]
    elif Budget == 'High':
         TEMP = ZomatoData[(ZomatoData['Cuisines'].apply(lambda x: Cuisine.lower() in x.lower())) & (ZomatoData['City'].apply(lambda x: City.lower() in x.lower()))]
         TEMP = TEMP.loc[TEMP['Average Cost for two'] >= 700,]
         TEMP = TEMP.sort_values("Aggregate rating",ascending=False)
         return TEMP[['Restaurant Name','Address','Average Cost for two','Aggregate rating']]
    
   
class ActionSearchRestaurant(Action):

    def name(self) -> Text:
        return "action_search_restaurant"

    def run(self, dispatcher, tracker, domain):

        tslots = tracker.slots
        print(tslots)

        cuisine = tracker.get_slot('cuisine')
        location = tracker.get_slot('location')
        budget = tracker.get_slot('budget')

        results = RestaurantSearch(City=location,Cuisine=cuisine,Budget = budget)
        response=""
        if results.shape[0] == 0:
            response= "no results"
        else:   
            for restaurant in results.iloc[:5].iterrows(): 
                print(restaurant)
                restaurant = restaurant[1]
              #top5 = results.head(5) 
                response=response + F"{restaurant['Restaurant Name']} in {restaurant['Address']} has been rated {restaurant['Aggregate rating']} with avg cost {restaurant['Average Cost for two']} \n\n"

        dispatcher.utter_message("-----"+response)

        #how to set slot [SlotSet('location',loc)]
        return []



class ActionSendEmail(Action):
    def name(self):
        return 'action_send_email'

    def run(self, dispatcher, tracker, domain):
        MailID = tracker.get_slot('email')
        cuisine = tracker.get_slot('cuisine')
        location = tracker.get_slot('location')
        budget = tracker.get_slot('budget')

        results = RestaurantSearch(City=location,Cuisine=cuisine,Budget = budget)
        response=""
        if results.shape[0] == 0:
            response= "no results"
        else:   
             for restaurant in results.iloc[:10].iterrows(): 
                print(restaurant)
                restaurant = restaurant[1]
              #top5 = results.head(5) 
                response=response + F"Found {restaurant['Restaurant Name']} in {restaurant['Address']} rated {restaurant['Aggregate rating']} with avg cost {restaurant['Average Cost for two']} \n\n"

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("testkdchatbot@gmail.com", "testkd@123")
  
        # sending the mail
        s.sendmail("testkdchatbot@gmail.com", MailID, response)
  
        # terminating the session
        s.quit()
        return []

class ActionCheckLocation(Action):

    def name(self):
        return 'action_check_location'

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        
        if loc is None:
          dispatcher.utter_message("Sorry, we dont operate in this city. Can you please specify some other location")
          return [SlotSet('check_resp',False)]

        cities_lower=[x.lower() for x in WeOperate]
        
        if loc.lower() not in cities_lower:
            dispatcher.utter_message("Sorry, we dont operate in this city. Can you please specify some other location")
            return [SlotSet('check_resp',False)]


        dispatcher.utter_message("Congo.. We operate in this city.")
        return [SlotSet('check_resp',True)]

class ActionResetAllSlots(Action):

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]
