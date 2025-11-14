from bot.routing import main
import asyncio


if __name__ == "__main__":
    import maxapi
    from maxapi.types import MessageCallback
    import inspect

    print("maxapi file:", maxapi.__file__)
    print("MessageCallback.answer signature:", inspect.signature(MessageCallback.answer))
    asyncio.run(main())