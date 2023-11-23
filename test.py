
import json

def print_json(json_data):
    json_object = json.loads(json_data)
    json_formatted_str = json.dumps(json_object, indent=2)
    print(json_formatted_str)



json_data = '[{"ID":10,"Name":"Pankaj","Role":"CEO"},' \
            '{"ID":20,"Name":"David Lee","Role":"Editor"}]'

print_json(json_data)






