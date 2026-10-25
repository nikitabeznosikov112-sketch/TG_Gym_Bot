from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from aiogram.fsm.context import FSMContext
import asyncio
import os
from dotenv import load_dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from databases import session, User, Workout, Exercise

load_dotenv()
from states import WorkoutCreation
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()



@dp.message(Command("start")) #Тут запоминаниеи юзера и кнопки идущие на трени и их создание
async def cmd_start(message: types.Message):
    try:
        user = session.query(User).filter_by(tg_id=message.from_user.id).first()
        if not user:
            new_user = User(tg_id=message.from_user.id, username=message.from_user.username)
            session.add(new_user)
            session.commit()
            await message.answer(f'Все красава я тебя запомнил, {message.from_user.first_name}')
        else:
            await message.answer('С возвращением браток')
    except Exception as e:
        session.rollback()
        print (f'Ошибка БД: {e}')
        await message.answer('сорян проихошла ошибка попробуй позже')
    finally:
        session.close()
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Мои трени')], [KeyboardButton(text='Создать треню')]], resize_keyboard=True)
    await message.answer("Шо делаем", reply_markup=keyboard)

@dp.message(lambda message: message.text == 'Создать треню') #тут ответ на кнопку создать треню и ждем название трени
async def start_worcout_creation(message: types.Message, state:FSMContext):
    await message.answer('Как назовем треню')
    await state.set_state(WorkoutCreation.waiting_for_title)

@dp.message(WorkoutCreation.waiting_for_title) #тут получаем название трени и добавляем треню в бд
async def catch_title(message: types.Message, state: FSMContext):
    title = message.text
    await state.update_data(title=title)

    try:
        new_workout = Workout(title=title, user_id=message.from_user.id)
        session.add(new_workout)
        session.commit()
        await message.answer('Треня создана')
    except Exception as e:
        session.rollback()
        await message.answer('СОрри ошибка какаято')
    finally:
        session.close()
    await state.clear()

@dp.callback_query(F.data.startswith('del_workout:'))
async def delete_workout(callback: CallbackQuery):
    workout_id = int(callback.data.split(':')[1])

    try:
        workout = session.query(Workout).filter_by(id=workout_id).first()
        if workout:
            session.delete(workout)
            session.commit()
            await callback.message.edit_text('Треня и ее упражнения удалены')
        else:
            await callback.answer('Удалено уже')
    except Exception as e:
        session.rollback()
        await callback.answer('Сорян ошибка')
        print(e)
    finally:
        session.close()
    await callback.answer()

@dp.callback_query(F.data.startswith('add_ex:')) #тут ответ на инлайн кнопку добавить упражнение
async def start_exercise(callback: CallbackQuery, state: FSMContext):
    workout_id = int(callback.data.split(':')[1])

    await state.update_data(workout_id=workout_id)

    await callback.message.answer('Введи название упражнения')
    await state.set_state(WorkoutCreation.waiting_for_exercise)
    await callback.answer()

@dp.message(WorkoutCreation.waiting_for_exercise) #тут получаем упражнение и спрашиваем подходы 
async def catch_ex(message: types.Message, state: FSMContext):
    await state.update_data(exercise_name=message.text)
    await message.answer('Скок подходов')
    await state.set_state(WorkoutCreation.waiting_for_sets)

@dp.message(WorkoutCreation.waiting_for_sets) #тут получаем подходы и спрашиваем повторения
async def catch_sets(message: types.Message, state: FSMContext):
    try:
        sets = int(message.text)
    except ValueError:
        await message.answer('Эт не число братан я так нен могу')
        return

    await state.update_data(sets = sets)
    await message.answer('А скок повторений')
    await state.set_state(WorkoutCreation.waiting_for_reps)

@dp.message(WorkoutCreation.waiting_for_reps) #тут получаем повторения и спрашиваем вес
async def catch_reps(message: types.Message, state: FSMContext):
    try:
        reps = int(message.text)
    except ValueError:
        await message.answer('Эт не число братан я так не могу')
        return

    await state.update_data(reps = reps)
    await message.answer('И какой вес')
    await state.set_state(WorkoutCreation.waiting_for_weight)

@dp.message(WorkoutCreation.waiting_for_weight) #тут получаем вес и добавляем упражнение в бд
async def complete_ex(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
    except ValueError:
        await message.answer('Эт не число братан я так не могу')

    data = await state.get_data()

    await state.update_data(weight = weight)
    try:
        exercise = Exercise(workout_id=data['workout_id'], name=data['exercise_name'], sets=data['sets'], reps=data['reps'], weight=weight)
        session.add(exercise)
        session.commit()
        await message.answer(f'Упражнение {data["exercise_name"]} добавлено')
    except Exception as e:
        session.rollback()
        await message.answer('Сорян ошибка попробуй еще раз')
        print(e)
    finally:
        session.close()

    await state.clear()

@dp.message(lambda message: message.text =='Мои трени') #тут ответ на кнопку мои трени вывод трень 
async def show_workouts(message: types.Message):
    try:
        workouts = session.query(Workout).filter_by(user_id=message.from_user.id).all()

        if not workouts:
            await message.answer('У тя пока нет трень')

        show_ex = InlineKeyboardBuilder()            

        text = 'Твои трени: \n\n'
        for work in workouts:
            show_ex.button(
                text=f'{work.title}',
                callback_data=f"view_workout:{work.id}"
            )
        show_ex.adjust(1)

        await message.answer('Выбери треню:', reply_markup=show_ex.as_markup())
    finally:
        session.close()

@dp.callback_query(F.data.startswith('view_workout:'))
async def show_work_details(callback: CallbackQuery):
    workout_id = int(callback.data.split(':')[1])

    try:
        workout = session.query(Workout).filter_by(id=workout_id).first()

        if not workout:
            await callback.answer('Сори треня не найдена')
            return
        text = f" **{workout.title}**\n\n"
        if not workout.exercises:
            text += "Пока нет упражнений."
        else:
            for i, ex in enumerate(workout.exercises, 1):
                text += f"{i}. {ex.name} — {ex.sets}x{ex.reps} ({ex.weight} кг)\n"

        builder = InlineKeyboardBuilder()
        builder.button(text='Добавить упражнение', callback_data=f'add_ex:{workout.id}')
        builder.button(text='Удалить тренировку', callback_data=f'del_workout:{workout.id}')
        builder.adjust(1)

        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode='Markdown')

        await callback.answer()
    finally:
        session.close()

async def main():
    print('Бот запущен . . .')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

