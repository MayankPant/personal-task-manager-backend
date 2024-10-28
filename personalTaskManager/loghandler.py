import logging
import pika
import json
import environ
import os
from .log_format_validator import JsonSchemaValidator
import jsonschema
from datetime import datetime

env = environ.Env(
    DEBUG=(bool, False)
)

"""
This file defines a custom log handler which rather than showing
the logs on console writes them directly to a rabbitMQ exhange

"""

credentials = pika.PlainCredentials(env('RABBITMQ_DEFAULT_USER'), env('RABBITMQ_DEFAULT_PASS'))

class APILogHandler(logging.Handler):
    def __init__(self, token=None):
        super().__init__()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="172.18.0.4", credentials=credentials))
        # declaring a fanout exchange
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='logs_exchange', exchange_type='fanout')
               
    def emit(self, record):
        """
        Defining a producer which publishes the log messae to a message broker
        RabbitMQ.
        """
        log_entry = self.format(record)
        payload = {
            'message': log_entry,
            'level': record.levelname,
            'logger_name': record.name,
            'timestamp': datetime.strftime(datetime.fromtimestamp(record.created), '%d-%m-%Y, %H:%M:%S'),
            'service': 'PERSONAL_TASK_MANAGER'
        }
        print(f"The log record: {payload}")
        try:
            validator = JsonSchemaValidator()
            isValid = validator.validate(payload)
            if isValid:
                payload_message = json.dumps(payload)
                self.channel.basic_publish(exchange='logs_exchange', routing_key='', body=payload_message)
                print(f"Log sent to exchange: {payload_message}")
            else:
                raise jsonschema.ValidationError("Given log record does not conform to our log schema definition")
        except Exception as e:
            print(f"Failed to send log to message broker: {e}")
            # logging.error(f"Failed to send log to {self.url}: {e}")