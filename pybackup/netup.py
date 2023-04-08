import os
from asyncio import create_subprocess_shell, open_connection, run, wait_for
from asyncio.subprocess import PIPE, STDOUT

import async_to_sync as sync


async def a_netup():
    con = open_connection("www.bitbucket.org", 80)
    try:
        (r, w) = await wait_for(con, 20)
        w.write(b"HEAD")
        w.write(b"/")
        await w.drain()
        w.close()
        await w.wait_closed()
        # await r.read()
        if os.getuid() != 10749:
            # return await a_netup2()
            return True
        else:
            return True
    except Exception as e:
        print("network error ", e)
        raise e
        return False


cmd2 = "termux-wifi-connectioninfo | jq -r '.ip'"


async def a_netup2():
    p = await create_subprocess_shell(cmd2, stdout=PIPE, stderr=STDOUT)
    (so, se) = await p.communicate()
    rv = so.decode()
    rv = rv.strip()
    print(rv)
    return p.returncode == 0 and rv != "0.0.0.0"


netup = sync.function(a_netup)


if __name__ == "__main__":
    print(netup())
