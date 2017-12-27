from abc import abstractproperty, abstractmethod
from json import loads

class Credentials:
	@abstractproperty
	def username(self):
		pass

	@abstractproperty
	def password(self):
		pass

	@abstractmethod
	def answer_security_question(question):
		"""
		Args:
		    question (str): Security question

		Returns:
		    str: Answer for the provided security question.
		"""
		pass


class JSONCredentials(Credentials):
	"""
	Implements the credentials API using a "credential info JSON" with the following format:
	{
	    "username" : "userFoo",
	    "password" : "passwordBar",
	    "security_questions" : 
	    {
	        "What's your favorite color?" : "Red",
	        "What is your name?" : "None of your business"
	    }
	}
	"""

	def __init__(self, json_credentials):
		"""
		Args: 
			json_credentials (str): Description of the credentials in the above format.
		"""
		self._credentials = loads(json_credentials)

	@property
	def username(self):
		return self._credentials["username"]

	@property
	def password(self):
		return self._credentials["password"]

	def answer_security_question(self, question):
		return self._credentials["security_questions"][question]

