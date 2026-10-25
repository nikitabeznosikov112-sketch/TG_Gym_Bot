from databases import session, User, Workout, Exercise


user = session.query(User).all()
w = session.query(Workout).all()
e = session.query(Exercise).all()
print(user)
print(e)
print(w)




