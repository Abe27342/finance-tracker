from os import listdir
from os.path import isfile, splitext, join

from azure.keyvault import KeyVaultClient, KeyVaultId
from azure.common.credentials import UserPassCredentials

from abc import abstractproperty, abstractmethod
from json import loads, load

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

class Vault:
	def __init__(self, ac):
		self._uri = ac["uri"]
		self._client = KeyVaultClient(UserPassCredentials(ac["username"], ac["password"], resource='https://vault.azure.net'))

	def get_website_credentials(self, website_name):
		secret_bundle = self._client.get_secret(self._uri, website_name, KeyVaultId.version_none)
		return JSONCredentials(secret_bundle.value)

def get_vault():
	ac = load(open('Credentials/azure.json', 'r'))
	return Vault(ac)

if __name__ == '__main__':
	client = get_keyvault_client()
	basedir = 'Credentials/'
	for fname in listdir(basedir):
		(website, ext) = splitext(fname.lower())
		if isfile(join(basedir, fname)) and ext == '.json':
			website_credentials = ''.join(open(join(basedir, fname), 'r').readlines())
			client.set_secret(ac["uri"], website, website_credentials)
