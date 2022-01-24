sessions = []

def rememberSession(session):
  sessions.append(session)

def anyAuthenticatedSession():
  for session in sessions:
    if session._isAuthenticated():
      return session
  return None
