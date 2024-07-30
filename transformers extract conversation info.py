#!pip install torch transformers
def extract_entities_from_conversation(json_data):
  """Extracts entities from a Bahasa Indonesia conversation in JSON format.

  Args:
    json_data: A JSON-formatted string containing the conversation transcript.
      The JSON should have a 'transcription' key with a list of turns, 
      where each turn has 'speaker', 'start_time', 'end_time', and 'text' fields.

  Returns:
    A dictionary with entity types as keys and a list of corresponding entities as values.
    The following entity types are extracted:
      - Person
      - Organization
      - Price
      - Product
      - Location
      - Time
      - Quantity
  """
  import json
  from transformers import pipeline

  # Load the Bahasa Indonesia NER model
  ner_model = pipeline('ner', model='cahya/bert-base-indonesian-NER')
  
  data = json.loads(json_data)
  
  # Extract text from the conversation
  text = " ".join([turn['text'] for turn in data['transcription']])

  # Perform NER
  entities = ner_model(text)

  # Initialize the result dictionary
  result = {
      "Person": [],
      "Organization": [],
      "Price": [],
      "Product": [],
      "Location": [],
      "Time": [],
      "Quantity": []
  }

  # Extract entities based on their labels
  for entity in entities:
    if entity['entity'] == 'B-PER':
      result["Person"].append(entity['word'])
    elif entity['entity'] == 'B-ORG':
      result["Organization"].append(entity['word'])
    elif entity['entity'] == 'B-LOC':
      result["Location"].append(entity['word'])
    elif entity['entity'] == 'B-TIME':
      result["Time"].append(entity['word'])
    # Add more entity types as needed

  # Remove duplicates and return the result
  for entity_type in result:
      result[entity_type] = list(set(result[entity_type]))
  
  return result

# Test the function with the provided example
json_data = """
{
"id": "64ad100b03cb62af904e0d65",
"name": "Test Record",
"transcription": [
{
"end_time": "0:00:03",
"speaker": "B",
"start_time": "0:00:00",
"text": "halo selamat sore perkenalkan saya ",
"type": "audio"
},
{
"end_time": "0:00:07",
"speaker": "A",
"start_time": "0:00:03",
"text": "bobby saya mau verifikasi data pekerja ",
"type": "audio"
},
{
"end_time": "0:00:11",
"speaker": "B",
"start_time": "0:00:07",
"text": "rido mohon dibantu untuk data pekerjaan ",
"type": "audio"
},
{
"end_time": "0:00:19",
"speaker": "A",
"start_time": "0:00:11",
"text": "pak oke pak boleh disebutkan pekerjaannya saat ini pekerjaan saya sebagai programmer baik selanjutnya ",
"type": "audio"
},
{
"end_time": "0:00:25",
"speaker": "B",
"start_time": "0:00:19",
"text": "saya minta data tempat tinggal boleh dibantu tempat tinggal ini untuk tepat tinggal ",
"type": "audio"
},
{
"end_time": "0:00:37",
"speaker": "A",
"start_time": "0:00:25",
"text": "saya ada di jakarta barat oke selanjutnya boleh tolong dibantu untuk status penghasilannya untuk penghasilan ",
"type": "audio"
},
]
}
"""

entities = extract_entities_from_conversation(json_data)
print(entities)
