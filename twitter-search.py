import codecs
from twython import Twython
import pprint
import sys
import cPickle
import json

CUST_KEY = 'cXCAkr4c56LTDr6alRqLk03pt'
CUST_SECRET = 'KCTBzcUkq4EJIWaopdXAygPHpRxuDMwZCMlg9v8J4aLFz1Uhqe'

class FileStore:
	def __init__(self, filename):
		self.filename = filename
		
	def storeTweet(self, data):	
		data = self.deduplicate(data)
	
		with codecs.open(self.filename+'_tweets'+'.txt', 'a', encoding="utf8") as fileHandle:
			for tweet in data:
				fileHandle.write(tweet['text']+'\n')
			
	def jsonLoad(self):
		data = []
		
		try:
			with codecs.open(self.filename+'.json', 'r', encoding="ISO-8859-1") as fileHandle:
				try: 
					data = json.load(fileHandle)
				except:
					pass
		except:
			pass
					
		return data
				
	def jsonStore(self, data):
		storedJson = self.jsonLoad()
		data = data + storedJson
		
		with codecs.open(self.filename+'.json', 'w', encoding="ISO-8859-1") as fileHandle:
			json.dump(data, fileHandle)
		
	
	def store(self, data):
		storedData = self.load()
		data = self.deduplicate(data + storedData)
		
		self.jsonStore(data)
		self.storeTweet(data)
		
		for tweet in data:
			with codecs.open(self.filename+'.dat', 'ab', encoding="ISO-8859-1") as fileHandle:
				cPickle.dump(tweet, fileHandle, -1)
			
	def deduplicate(self, data):
		uniqueTweets = {}
		for tweet in data:
			if not uniqueTweets.has_key(tweet['id']):
				uniqueTweets[tweet['id']] = tweet
			
		return uniqueTweets.values()
			
	def load(self):
		data = []
		try:
			with codecs.open(self.filename+'.dat', 'rb', encoding="ISO-8859-1") as fileHandle:
				while True:
					try:
						data.append(cPickle.load(fileHandle))
					except:
						break
			data = self.deduplicate(data)
	
		except:
			pass
		
		return data		


class TwitterAPI:
	filterKeys =  {'coordinates': u'[\'coordinates\']', 'created_at': u'[\'created_at\']', 'favorite_count': u'[\'favorite_count\']' , 'id': u'[\'id\']', 'lang': u'[\'lang\']', 'metadata': u'[\'metadata\']', 'text': u'[\'text\']', 'user_followers_count': u'[\'user\'][\'followers_count\']'}

	def __init__(self):
		self.apiHandle = Twython(CUST_KEY, CUST_SECRET)
		
		
	def filter(self, tweet):
		filteredTweet = {}
			
		for key in TwitterAPI.filterKeys:
			try:
				filteredTweet[key] = eval('tweet' + TwitterAPI.filterKeys[key])
			except:
				print '==tweet' + TwitterAPI.filterKeys[key]
			
		return filteredTweet
		
		
	def search(self, keyword, language='en'):
		apiResponse = self.apiHandle.search(q=keyword, lang=language, count=100)
		#response = [self.filter(tweet) for tweet in apiResponse['statuses']]
		
		return apiResponse['statuses']

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('ISO-8859-1')
	
	if(len(sys.argv) >= 4):
		persistentFileStore = sys.argv[1]
		searchTerm = sys.argv[2]
		language = sys.argv[3]
	elif(len(sys.argv) == 3):
		language = 'en'
	else:
		print("Insufficent arguments")
		exit()
	
	twitterAPI = TwitterAPI()
	fileStore = FileStore(persistentFileStore)
	
	response = twitterAPI.search(searchTerm, language)
	
	fileStore.store(response)
	
	data = fileStore.load()

	for i in data:
		try:
			print i['text']
		except:
			pprint.pprint(i)

	print(len(data))		