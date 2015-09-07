import codecs
from twython import Twython
import pprint
import sys
import cPickle

CUST_KEY = 'cXCAkr4c56LTDr6alRqLk03pt'
CUST_SECRET = 'KCTBzcUkq4EJIWaopdXAygPHpRxuDMwZCMlg9v8J4aLFz1Uhqe'

class FileStore:
	def __init__(self, filename):
		self.filename = filename
		
	def store(self, data):
		with codecs.open(self.filename, 'ab', encoding="ISO-8859-1") as fileHandle:
			cPickle.dump(data, fileHandle, -1)
			
	def deduplicate(self, data):
		uniqueTweets = {}
		for tweet in data:
			if not uniqueTweets.has_key(tweet['id']):
				uniqueTweets[tweet['id']] = tweet
			
		return uniqueTweets.values()
			
	def load(self):
		data = []
		with codecs.open(self.filename, 'rb', encoding="ISO-8859-1") as fileHandle:
			while True:
				try:
					data.append(cPickle.load(fileHandle))
				except:
					break
		data = self.deduplicate(data)
		
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
		apiResponse = self.apiHandle.search(q=keyword, lang=language)
		response = [self.filter(tweet) for tweet in apiResponse['statuses']]
		
		return response

if __name__ == "__main__":
	reload(sys)
	sys.setdefaultencoding('ISO-8859-1')

	twitterAPI = TwitterAPI()
	fileStore = FileStore('twitter-search-results.dat')
	
	response = twitterAPI.search('game of thrones')
	
	for i in response:
		fileStore.store(i)
	
	data = fileStore.load()

	for i in data:
		try:
			print i['text']
		except:
			print("=================")
			print (i)
			print("=================")
	print(len(data))		