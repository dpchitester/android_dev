import logging
import pybackup

logging.basicConfig(filename="pybackup.log", encoding="utf-8", level=logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.DEBUG)
pybackup.main()
