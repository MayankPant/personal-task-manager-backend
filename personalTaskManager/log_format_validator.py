import jsonschema
import json

"""
File validates the logs before writing them to the message broker.
Validation involves making sure the logs are of a particuler format.
"""

expected_log_schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Log",
  "type": "object",
  "properties": {
    "level": {
      "type": "string",
      "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
      "description": "Severity level of the log entry."
    },
    "message": {
      "type": "string",
      "minLength": 1,
      "description": "The log message content."
    },
    "timestamp": {
      "type": "string",
     "pattern": "^\\d{2}-\\d{2}-\\d{4}, \\d{2}:\\d{2}:\\d{2}$",
      "description": "Custom timestamp format: DD-MM-YYYY, HH:MM:SS"
    },
    "service": {
      "type": "string",
      "minLength": 1,
      "description": "The service generating the log (e.g., 'auth', 'logging')."
    },
    "extra_data": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      },
      "description": "Optional key-value pairs of additional information."
    }
  },
  "required": ["level", "message", "timestamp", "service"],
}

class JsonSchemaValidator():

    def __init__(self) -> None:
        pass
    
    def validate(self, user_input: dict, schema:dict=expected_log_schema):
        try:
            jsonschema.validate(schema=schema, instance=user_input)
            print("JSON SCHEMA VALIDATED")
            return True
        except jsonschema.ValidationError as e:
            print("JSON SCHEMA VALIDATION UNSUCCESSFUL")
            return False
        except Exception as e:
            print(f"Exception occured: {e}\n\n\n\n\n")
            return False
        
    def validate_jsonschema(self, schema):
        """
        The most widely used json schema is the draft7 schema and so
        we will be using it here, atleast for now

        """
        print(f"Recieved schema for validation: {schema}\n\n\n\n")
        try:
            schema = json.loads(schema)
            jsonschema.Draft7Validator.check_schema(schema=schema)
            return True
        except jsonschema.ValidationError as e:
            print("Validation Error")
            return False
        except Exception as e:
            print(f"Exception occured: {e}\n\n\n\n\n")
            return False