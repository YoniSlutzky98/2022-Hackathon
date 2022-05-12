myToken = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE2MDE3MDU1OSwidWlkIjoyOTk1NzE5NCwiaWFkIjoiMjAyMi0wNS0xMlQwODoxODoyOS4xMDZaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MTE4NzU5MjIsInJnbiI6InVzZTEifQ.kvSNJQ9B9TrWUI_BX8Z9B2Vg0x6PSaLBW3cxp7wRi-Y"

import requests
import json

apiKey = myToken
apiUrl = "https://api.monday.com/v2"
headers = {"Authorization" : apiKey}
 
#Fields to be received from code, placeholders for now
boardId = "2663367465"
exercise_name = 'Algo Ex 6'
due_date = '2022-05-27'
ref_url = 'www.drive.cheating.com'
coverage = '88%'

query = 'mutation ($myItemName: String!, $columnVals: JSON!) { create_item (board_id:2663367465, item_name:$myItemName, column_values:$columnVals) { id } }'
vars = {
 'myItemName' : exercise_name,
 'columnVals' : json.dumps({
   'status' : {'label' : 'Working on it'},
   'date4' : {'date' : due_date},
     'text':ref_url,
     'text4':coverage
 })
}

data = {'query' : query, 'variables' : vars}
r = requests.post(url=apiUrl, json=data, headers=headers) # make request
