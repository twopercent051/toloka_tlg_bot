import asyncio

from tgbot.handlers.echo import router as echo_router
from tgbot.handlers.admin.blocks.main_block import router as admin_main_block
from tgbot.handlers.admin.blocks.settings_block import router as admin_settings_block
from tgbot.handlers.admin.blocks.users_profile_block import router as admin_users_profile_block
from tgbot.handlers.user.blocks.main_block import router as user_main_block
from tgbot.handlers.user.blocks.referal_block import router as user_referal_block
from tgbot.handlers.user.blocks.faq_block import router as user_faq_block
from tgbot.handlers.user.blocks.support_block import router as user_support_block
from tgbot.handlers.user.blocks.set_work_block import router as user_set_work_block
from tgbot.handlers.user.blocks.get_work_block import router as user_get_work_block
from tgbot.handlers.messages_reposts import router as messages_reposts_block
from tgbot.misc.scheduler import scheduler_jobs
from tgbot.models.redis_connector import RedisConnector as rds

from create_bot import bot, dp, scheduler, logger, register_global_middlewares, config


admin_router = [
    admin_main_block,
    admin_settings_block,
    admin_users_profile_block,
]


user_router = [
    user_main_block,
    user_referal_block,
    user_faq_block,
    user_support_block,
    user_set_work_block,
    user_get_work_block
]


async def main():
    logger.info("Starting bot")
    scheduler_jobs()
    rds.redis_start()
    dp.include_routers(
        *admin_router,
        *user_router,
        echo_router,
        messages_reposts_block
    )

    try:
        scheduler.start()
        register_global_middlewares(dp, config)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()
        scheduler.shutdown(True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
