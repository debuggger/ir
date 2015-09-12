import codecs
from twython import Twython
import pprint
import sys
import cPickle
import json

CUST_KEY = 'cXCAkr4c56LTDr6alRqLk03pt'
CUST_SECRET = 'KCTBzcUkq4EJIWaopdXAygPHpRxuDMwZCMlg9v8J4aLFz1Uhqe'

class FileStore:
	filterKeys =  {'coordinates': u'[\'coordinates\']', 'created_at': u'[\'created_at\']', 'favorite_count': u'[\'favorite_count\']' , 'id': u'[\'id\']', 'lang': u'[\'lang\']', 'text': u'[\'text\']', 'user_followers_count': u'[\'user\'][\'followers_count\']', 'retweet_count': u'[\'retweet_count\']'}

	

	def __init__(self, filename):
		self.filename = filename
	
		
	def filter(self, tweet):
		filteredTweet = {}
			
		for key in FileStore.filterKeys:
			try:
				filteredTweet[key] = eval('tweet' + FileStore.filterKeys[key])
			except:
				print '==tweet' + FileStore.filterKeys[key]
			
		return filteredTweet
	
	def storeFilteredData(self, data):
		with codecs.open(self.filename+'_tweets_filtered'+'.json', 'w', encoding="utf8") as fileHandle:
			json.dump([self.filter(tweetData) for tweetData in data], fileHandle)
		fileHandle.close()	
	
	def storeTweet(self, data):	
		with codecs.open(self.filename+'_tweets'+'.txt', 'w', encoding="utf8") as fileHandle:
			for tweet in data:
				fileHandle.write(str(tweet["id"])+'--->'+tweet['text']+'\n')
		fileHandle.close()
			
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
		uniqueTweets = self.deduplicate(data + storedJson)
		
		with codecs.open(self.filename+'.json', 'w', encoding="ISO-8859-1") as fileHandle:
			json.dump(uniqueTweets, fileHandle)
		fileHandle.close()
		
		self.storeTweet(uniqueTweets)
		self.storeFilteredData(uniqueTweets)
	
	def store(self, data):
		self.jsonStore(data)
		
			
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

		except:
			pass
		
		return data		


class TwitterAPI:
	

	def __init__(self):
		self.apiHandle = Twython(CUST_KEY, CUST_SECRET)
		
	def search(self, keyword, language='en'):
		apiResponse = self.apiHandle.search(q=keyword, lang=language, count=200)
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
	
	data = fileStore.jsonLoad()

	for i in data:
		try:
			print i['text']
		except:
			pass

	print(len(data))		