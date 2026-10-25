from aiogram.fsm.state import State, StatesGroup

class WorkoutCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_exercise = State()
    waiting_for_sets = State()
    waiting_for_reps = State()
    waiting_for_weight = State()
    

