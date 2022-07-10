import datetime
import logging
from pathlib import Path

import aiogram.utils.markdown as md
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
from environs import Env

logging.basicConfig(level=logging.INFO)

env = Env()
env.read_env()

shop_api_host_url = 'http://127.0.0.1:8000/'

images_path_str = 'P:\\projos\\aioshop\\shop_backend\\'
api_url = 'api/v0/'

BOT_TOKEN = env.str('API_TOKEN')

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

menu_button = InlineKeyboardButton('Menu', callback_data='menu')
back_to_cats_button = InlineKeyboardButton('Back', callback_data='back')


# @dp.message_handler(commands=['start', 'help'])
# async def send_welcome(message: types.Message):
#     """Provides the basic info on Shobot"""
#     await message.reply('Hi there!')

@dp.callback_query_handler(text='menu')
@dp.message_handler(commands=['start'])
async def start_shop(message: types.Message | types.CallbackQuery):
    buttons = 'Categories', 'Contact', 'My profile'

    shop_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(buttons[0], callback_data='categories')) \
        .row(InlineKeyboardButton(buttons[1], url='https://t.me/lolyge'),
             InlineKeyboardButton(buttons[2], callback_data='profile'))
    shop_keyboard.row_width = 10
    if type(message) == types.CallbackQuery:
        await message.answer()
        await bot.send_message(message.from_user.id, "Welcome to our easy store!", reply_markup=shop_keyboard)
    else:
        await message.reply("Welcome to our easy store!", reply_markup=shop_keyboard)


async def request_endpoint(endpoint: str):
    """Calls API for data"""
    async with aiohttp.ClientSession() as session:
        async with session.get(shop_api_host_url + api_url + endpoint) as resp:
            return await resp.json()


@dp.callback_query_handler(text='back')
@dp.callback_query_handler(text='categories')
async def show_categories(query: types.CallbackQuery):
    await query.answer()
    resp_data = await request_endpoint('categories')
    categories_buttons = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton('All', callback_data='all')) \
        .insert(menu_button)
    for category in resp_data:
        categories_buttons.add(InlineKeyboardButton(category['naming'], callback_data=category['id']))
    await bot.send_message(query.from_user.id, text='Choose category', reply_markup=categories_buttons)


async def render_positions_for_user(user_id, positions_data):
    cb_string = 'info' + str(positions_data['id'])
    details_button = InlineKeyboardButton(f'Details for {positions_data["naming"]}', callback_data=cb_string)
    product_photo = positions_data.get('look', '')
    if product_photo:
        path_photo = images_path_str + '\\'.join(product_photo.split('/')[-3:])
        await bot.send_photo(user_id,
                             photo=open(path_photo, 'rb'))
    await bot.send_message(user_id, md.text(
        md.bold(positions_data['naming']),
        md.text('Price: ', md.text(positions_data['price'])),
        sep='\n'
    ), reply_markup=InlineKeyboardMarkup().add(details_button),
                           parse_mode=ParseMode.MARKDOWN,
                           )


@dp.callback_query_handler(lambda cb: cb.data.startswith('info'))
async def details_on_position(query: types.CallbackQuery):
    await query.answer()
    prod_id = query.data.strip('info')
    resp_data = await request_endpoint(f'products/{prod_id}')
    date_time_details = datetime.datetime.strptime(resp_data['published_at'],
                                                   '%Y-%m-%dT%H:%M:%S.%fZ'
                                                   )
    back_to_cat_btn = InlineKeyboardButton('Back', callback_data=resp_data['category'])
    nav_btns = InlineKeyboardMarkup().add(back_to_cat_btn).insert(menu_button)
    await bot.send_message(query.from_user.id,
                           md.text(
                               md.hbold(resp_data['naming']),
                               md.text('Price: ', resp_data['price']),
                               md.hitalic(resp_data['description']),
                               md.text(str(date_time_details)[:-10]),
                               sep='\n'
                           ), parse_mode=ParseMode.HTML, reply_markup=nav_btns)


@dp.callback_query_handler(text='all')
async def show_all(query: types.CallbackQuery):
    await query.answer()
    resp_data = await request_endpoint('products')
    for prod in resp_data:
        await render_positions_for_user(query.from_user.id, prod)
    back_buttons = InlineKeyboardMarkup().add(back_to_cats_button) \
        .insert(menu_button)
    await bot.send_message(query.from_user.id, 'That`s all', reply_markup=back_buttons)


@dp.callback_query_handler(lambda cb: cb.data.isnumeric())
async def get_products_by_category(query: types.CallbackQuery):
    await query.answer()
    resp_data = await request_endpoint(f'prod_from_category?cat_id={query.data}')
    products_buttons = InlineKeyboardMarkup() \
        .add(back_to_cats_button) \
        .insert(menu_button)
    for pos in resp_data:
        await render_positions_for_user(query.from_user.id, pos)
    await bot.send_message(query.from_user.id, 'That`s it', reply_markup=products_buttons)


class Profile(StatesGroup):
    name = State()
    age = State()
    profession = State()


@dp.callback_query_handler(text='profile')
@dp.message_handler(commands='profill')
async def profiller_start(message: types.Message | types.CallbackQuery):
    await Profile.name.set()
    if type(message) == types.CallbackQuery:
        await message.answer('Hi! What`s your name?')
    else:
        await message.reply('Hi! What`s your name?')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='stop', ignore_case=True), state='*')
async def profiller_cancel(message: types.Message, state: FSMContext):
    """
    cancels at any point of conversation
    :param message: command or keyword
    :param state:
    :return: None
    """
    current_state = await state.get_state()
    if not current_state:
        return

    logging.info(f'Cancelling state {current_state}')
    await state.finish()
    await message.reply('Profiling cancelled', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda message: not message.text.isalpha(),
                    state=Profile.name)
async def process_name_invalid(message: types.Message):
    return await message.reply('Enter your real name, please.')


@dp.message_handler(state=Profile.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Any name should work fine
    :param message:
    :param state:
    :return:
    """
    async with state.proxy() as data:
        data['name'] = message.text

    await Profile.next()
    await message.reply('How old are you?')


@dp.message_handler(lambda message: not message.text.isdigit(), state=Profile.age)
async def process_age_invalid(message: types.Message):
    return await message.reply('Age should be a number!')


@dp.message_handler(lambda message: message.text.isdigit(), state=Profile.age)
async def process_age(message: types.Message, state: FSMContext):
    await Profile.next()
    await state.update_data(age=int(message.text))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add('IT').add('Sales').add('Industry').add('Finance'). \
        add('Management').add('Other')
    await message.reply('Okey, what are you?', reply_markup=markup)


@dp.message_handler(lambda message: message.text not in [
    'IT', 'Finance', 'Industry', 'Management', 'Other', 'Sales'
], state=Profile.profession)
async def process_job_invalid(message: types.Message):
    return await message.reply('Please, choose your profession from keyboard')


@dp.message_handler(state=Profile.profession)
async def process_profession(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['profession'] = message.text
        markup = types.ReplyKeyboardRemove()

        await bot.send_message(message.chat.id,
                               md.text(
                                   md.text('Okey! Glad to introduce this place to you, ',
                                           md.bold(data['name'])),
                                   md.text('Age: ', md.code(data['age'])),
                                   md.text('Profession: ', data['profession']),
                                   sep='\n',
                               ),
                               reply_markup=markup,
                               parse_mode=ParseMode.MARKDOWN,
                               )
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
