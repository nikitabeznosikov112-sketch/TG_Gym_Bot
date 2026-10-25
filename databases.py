from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, ForeignKey
import psycopg2
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

load_dotenv()

engine = create_engine(os.getenv('DB_URL'))
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    tg_id = Column(BigInteger, nullable=False, primary_key=True)
    username = Column(String, nullable=True)
    workouts = relationship('Workout', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'Юзер {self.tg_id}, name - {self.username}'


class Workout(Base):
    __tablename__ = 'workouts'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'))
    title = Column(String(100), nullable=False)
    exercises = relationship('Exercise', back_populates='workout', cascade='all, delete-orphan' )
    user = relationship('User', back_populates='workouts')

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    workout_id = Column(Integer, ForeignKey('workouts.id'))
    name = Column(String, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=True)
    workout = relationship('Workout', back_populates='exercises')

    