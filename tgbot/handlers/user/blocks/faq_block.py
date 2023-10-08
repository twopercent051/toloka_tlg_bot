from aiogram.types import CallbackQuery
from aiogram import F, Router

from create_bot import bot
from tgbot.handlers.user.inline import MainInline
from tgbot.middlewares.black_list import BlockUserMiddleware

router = Router()
router.message.outer_middleware(BlockUserMiddleware())
router.callback_query.outer_middleware(BlockUserMiddleware())

inline = MainInline()


@router.callback_query(F.data == "faq")
async def faq_block(callback: CallbackQuery):
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur aliquam lacinia odio, eget faucibus " \
           "odio vulputate ac. Aenean maximus mattis leo ac dignissim. Pellentesque vel arcu ac sapien sodales " \
           "pharetra. Etiam auctor risus a lorem sagittis blandit. Ut porta sagittis luctus. Pellentesque quis elit " \
           "vestibulum tellus blandit efficitur. Suspendisse blandit, sem sit amet blandit posuere, nunc risus " \
           "ultrices lorem, vel convallis nunc neque nec nibh. Nulla cursus convallis est, nec venenatis nisl semper " \
           "ornare. Sed commodo aliquet rhoncus. Fusce libero dui, semper at egestas sed, posuere nec nibh. " \
           "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum " \
           "blandit blandit ultrices. Maecenas suscipit nibh est, ultricies consequat ligula pulvinar id. Vestibulum " \
           "in lacinia tortor."
    kb = inline.home_kb()
    await callback.message.answer(text, reply_markup=kb)
    await bot.answer_callback_query(callback.id)
