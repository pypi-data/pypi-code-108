#testRequest: wait for request
class testRequest:
  def __init__(self):
    self.text = 'Thinking'

#getAnswer: wait for answer and return it
def getAnswer(token, message, userid, username):
  try:
    x = testRequest()
    while x.text == 'Thinking':
      x = requests.get('https://api.daniton999.ml/chatbot', json = {'token': token, 'id': userid, 'language': 'de', 'name': username, 'message': message}, stream = True)
      time.sleep(3)
    x = x.json()['message']
  except Exception as es:
    print(es)
    x = '_ _'
  return x
