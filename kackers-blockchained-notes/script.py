import hashlib
import string
import json
import logging
import requests

logging.basicConfig(filename="log.log", level=logging.INFO)
session = requests.Session()


def find_src_by_hash_sufix(sufix):
    n = 0
    while True:
        src = str(n)
        hash_value = hashlib.md5(src.encode('ascii')).hexdigest()
        if hash_value[32-len(sufix):] == sufix:
            return src
        n += 1
    logging.error(f"Not found src for hash sufix: {sufix}")
    input("wtf?!")


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def get_captcha_hash_value(url):
    html = session.get(url).text
    captcha_hash = html[html.find('<input name="hash" value="') + 26:html.find('" type="hidden">')]
    return captcha_hash


def get_secret(url, data):
    html = session.post(url, data).text
    html = html[html.find("step secret is:") + 15:]
    html = html.replace('<br>', '').replace('\n', '').replace(' ', '').replace('\t', '')
    return html[:html.find('<')]


def main():
    pt = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas in felis iaculis, venenatis"
    get_url = lambda file_name: f"http://tasks.open.kksctf.ru:20005/{file_name}.php"
    current_page_hash = "379f65a74464e75e6207ff657229b547"
    with open("hash-dump.json") as file:
        hashes = json.loads(file.read())

    session.get(get_url(current_page_hash))

    while True:
        current_url = get_url(current_page_hash)
        captcha_hash_value = get_captcha_hash_value(current_url)
        if "Not Found" in captcha_hash_value:
            print(f"Finish. Current page hash: {current_page_hash}, plaintext: {pt}")
            break
        captcha = hashes[captcha_hash_value]
        src = find_src_by_hash_sufix(captcha)
        data = {
            "hash": captcha_hash_value,
            "ch": src,
            "s": "OK"
        }
        secret = get_secret(current_url, data)
        pt += f" {secret}"
        current_page_hash = md5(f"{current_page_hash}{secret}")
        logging.info(f"New secret: {secret}, current page hash: {current_page_hash}, plaintext: {pt}")


def generate_captcha_hashes():
    alphabet = "0123456789abcdef"
    hash_dict = {}
    for c1 in alphabet:
        for c2 in alphabet:
            for c3 in alphabet:
                for c4 in alphabet:
                    value = c1 + c2 + c3 + c4
                    hash_dict.update({md5(value): value})
    return hash_dict


if __name__ == "__main__":
    if "hash-dump.json" not in os.listdir():
        logging.info("Not found file with hashes, start generating...")
        hash_dict = generate_captcha_hashes()
        with open("hash-dump.json", "w") as file:
            file.write(json.dumps(hash_dict))
        logging.info("Hashes is genereted")
    main()
