import argparse
import concurrent.futures
import datetime
import json
import math
import os
import re
import requests
import sys
import time
import urllib3
from functools import reduce

"""
2/11/2024
These improvements should enhance the readability, maintainability, and robustness of original code.
"""

def nargs_fit(parser, args):
    '''
    Improvements made:

    1. Added comments to explain the purpose of each part of the code.
    2. Used set comprehensions to construct sets for short flags with nargs and short flags without args, improving readability and efficiency.
    3. Used set literal syntax ({}) to define sets instead of set() constructor, which is more concise.
    4. Changed the if conditions to use more descriptive variable names and improve readability.
    5. Introduced a regular expression (re.match()) to validate if a part is a valid flag, making the code more robust.
    6. Renamed the variable part to arg for clarity since it represents a command-line argument.
    These improvements should enhance the readability, maintainability, and robustness of the nargs_fit function.
    '''

    # Retrieve flags and their actions from the parser
    flags = parser._option_string_actions

    # Separate flags into short flags and long flags
    short_flags = [flag for flag in flags.keys() if len(flag) == 2]
    long_flags = [flag for flag in flags.keys() if len(flag) > 2]

    # Identify short flags with nargs and short flags without args
    short_flags_with_nargs = {flag[1]
                              for flag in short_flags if flags[flag].nargs}
    short_flags_without_args = {flag[1]
                                for flag in short_flags if flags[flag].nargs == 0}

    # Define a function to validate if a part is a valid flag
    def validate(part):
        return (re.match(r'-[^-]', part) and (set(part[1:-1]).issubset(short_flags_without_args) and '-' + part[-1] in short_flags)) or (part.startswith('--') and part in long_flags)

    # Initialize a variable to track if we are in a greedy state
    greedy = False

    # Iterate over each argument in the list
    for index, arg in enumerate(args):
        if arg.startswith('-'):  # If the argument starts with '-'
            valid = validate(arg)  # Check if it's a valid flag
            # If it's a valid flag with nargs
            if valid and arg[-1] in short_flags_with_nargs:
                greedy = True  # Switch to greedy mode
            elif valid:  # If it's a valid flag without nargs
                greedy = False  # Turn off greedy mode
            elif greedy:  # If we are in a greedy mode and this argument is not a valid flag
                # Prepend a space to the argument
                args[index] = ' ' + args[index]

    return args


def print_fit(string, pin=False):
    '''
    Overall, the print_fit() function provides a flexible way to print strings to the console, 
    either with or without keeping the cursor pinned at the end of the line.
    '''
    if pin == True:
        '''
        \r\033[K: These characters are ANSI escape sequences. 
        \r is the carriage return character, which moves the cursor to the beginning of the line, 
        and \033[K clears the line from the current cursor position to the end of the line.
        '''
        sys.stdout.write('\r\033[K')
        '''
        sys.stdout.write(string): 
        This line writes the string to the standard output without appending a newline character at the end of the line.
        '''
        sys.stdout.write(string)
        '''
        sys.stdout.flush(): 
        This line flushes the output buffer, ensuring that the output is displayed immediately.
        '''
        sys.stdout.flush()
    else:
        sys.stdout.write(string + '\n')


def input_fit(string=''):
    return input(string)


def merge(*dicts):
    result = {}
    for dictionary in dicts:
        result.update(dictionary)
    return result


def quit(string=''):
    print_fit(string)
    exit()


def make_dir(path):
    try:
        os.makedirs(path)
    except Exception as e:
        quit(str(e))


def confirm(message):
    while True:
        answer = input_fit('{} [Y/n] '.format(message)).strip()
        if answer.lower() == 'y':
            return True
        elif answer.lower() == 'n':
            return False
        print_fit('unexpected answer')


def progress(part, whole, percent=False):
    if percent:
        return f'{part}/{whole}({int(float(part) / whole * 100)}%)'
    else:
        return f'{part}/{whole}'


def request_fit(method, url, max_retry=0, cookie=None, stream=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Mobile Safari/537.36',
        'Cookie': cookie,
        # https://github.com/nondanee/weiboPicDownloader/issues/59
        # Friends whose size is 0 after the picture is downloaded look at it #59
        'referer': 'https://m.weibo.cn/'
    }
    return requests.request(method, url, headers=headers, timeout=5, stream=stream, verify=False)


def read_from_file(path):
    try:
        with open(path, 'r') as f:
            for line in f:
                return [line.strip()]
    except Exception as e:
        quit(str(e))


def nickname_to_uid(nickname):
    url = f'https://m.weibo.cn/n/{nickname}'
    response = request_fit('GET', url, cookie=token)
    if re.search(r'/u/\d{10}$', response.url):
        return response.url[-10:]
    else:
        return


def uid_to_nickname(uid):
    url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}'
    response = request_fit('GET', url, cookie=token)
    try:
        return json.loads(response.text)['data']['userInfo']['screen_name']
    except:
        return


def bid_to_mid(string):
    '''
    converts a Base62-encoded string to a decimal integer. 
    It first splits the input string into chunks of 4 characters each, 
    converts each chunk into a numeric value based on the Base62 alphabet, 
    joins the converted chunks into a single string, and finally converts the string to an integer.
    '''
    # Define the Base62 alphabet
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    # Create a dictionary mapping each character in the alphabet to its index
    alphabet_index = {char: index for index, char in enumerate(alphabet)}

    # Split the string into chunks of 4 characters each
    chunk_size = 4
    chunks = [string[max(-4 * (i + 1), -len(string)): -4 * i]
              for i in range(math.ceil(len(string) / chunk_size))]

    # Define a function to convert a chunk of characters to a number
    def convert_to_number(chunk):
        # Reverse the chunk and calculate its numeric value based on the alphabet mapping
        numeric_value = sum(alphabet_index[char] * len(alphabet)
                            ** index for index, char in enumerate(reversed(chunk)))
        # Zero-fill the numeric value to 7 digits
        return str(numeric_value).zfill(7)

    # Convert each chunk to a number and join them into a single string
    converted_chunks = [convert_to_number(chunk) for chunk in chunks]
    concatenated_string = ''.join(converted_chunks)

    # Convert the concatenated string to an integer and return
    return int(concatenated_string)


def parse_date(text):
    now = datetime.datetime.now()
    if '前' in text:
        if '小时' in text:
            return (now - datetime.timedelta(hours=int(re.search(r'\d+', text).group()))).date()
        else:
            return now.date()
    elif '昨天' in text:
        return now.date() - datetime.timedelta(days=1)
    elif re.search(r'^[\d|-]+$', text):
        if not re.search(r'^\d{4}', text):
            d = (str(now.year) + '-')
        else:
            d = ''
        return datetime.datetime.strptime(d + text, '%Y-%m-%d').date()


def compare(standard, operation, candidate):
    for target in candidate:
        try:
            result = '>=<'
            if standard > target:
                result = '>'
            elif standard == target:
                result = '='
            else:
                result = '<'
            return result in operation
        except TypeError:
            pass


def get_resources(uid, video, interval, limit):
    page = 1
    size = 25
    amount = 0
    total = 0
    empty = 0
    aware = 1
    exceed = False
    resources = []

    while empty < aware and not exceed:
        try:
            url = f'https://m.weibo.cn/api/container/getIndex?count={size}&page={page}&containerid=107603{uid}'
            response = request_fit('GET', url, cookie=token)
            assert response.status_code != 418
            json_data = json.loads(response.text)
        except AssertionError:
            print_fit(
                f'punished by anti-scraping mechanism (#{page})', pin=True)
            empty = aware
        except Exception:
            pass
        else:
            empty = empty + 1 if json_data['ok'] == 0 else 0
            if total == 0 and 'cardlistInfo' in json_data['data']:
                total = json_data['data']['cardlistInfo']['total']
            cards = json_data['data']['cards']
            for card in cards:
                if 'mblog' in card:
                    mblog = card['mblog']
                    if 'isTop' in mblog and mblog['isTop']:
                        continue
                    mid = int(mblog['mid'])
                    date = parse_date(mblog['created_at'])
                    mark = {
                        'mid': mid,
                        'bid': mblog['bid'],
                        'date': date,
                        'text': mblog['text']}
                    amount += 1
                    if compare(limit[0], '>', [mid, date]):
                        exceed = True
                    if compare(limit[0], '>', [mid, date]) or compare(limit[1], '<', [mid, date]):
                        continue
                    if 'pics' in mblog:
                        for index, pic in enumerate(mblog['pics'], 1):
                            if 'large' in pic:
                                resources.append(
                                    merge({'url': pic['large']['url'],
                                           'index': index,
                                           'type': 'photo'}, mark))
                    elif 'page_info' in mblog and video:
                        if 'media_info' in mblog['page_info']:
                            media_info = mblog['page_info']['media_info']
                            streams = [media_info[key] for key in ['mp4_720p_mp4', 'mp4_hd_url',
                                                                   'mp4_sd_url', 'stream_url'] if key in media_info and media_info[key]]
                            if streams:
                                resources.append(
                                    merge({'url': streams.pop(0), 'type': 'video'}, mark))
            print_fit('{} {}(#{})'.format('analysing weibos...' if empty <
                      aware and not exceed else 'finish analysis', progress(amount, total), page), pin=True)
            page += 1
        finally:
            time.sleep(interval)

    print_fit('\npractically scan {} weibos, get {} {}'.format(
        amount, len(resources), 'resources' if video else 'pictures'))
    return resources


def format_name(item):
    item['name'] = re.sub(r'\?\S+$', '', re.sub(r'^\S+/', '', item['url']))

    def safeify(name):
        template: dict = {'\\': '＼', '/': '／', ':': '：', '*': '＊',
                          '?': '？', '"': '＂', '<': '＜', '>': '＞', '|': '｜'}
        for illegal in template:
            name = name.replace(illegal, template[illegal])
        return name

    def substitute(matched):
        key = matched.group(1).split(':')
        if key[0] not in item:
            return ':'.join(key)
        elif key[0] == 'date':
            return item[key[0]].strftime(key[1]) if len(key) > 1 else str(item[key[0]])
        elif key[0] == 'index':
            return str(item[key[0]]).zfill(int(key[1] if len(key) > 1 else '0'))
        elif key[0] == 'text':
            return re.sub(r'<.*?>', '', item[key[0]]).strip()
        else:
            return str(item[key[0]])

    return safeify(re.sub(r'{(.*?)}', substitute, args.name))


def download(url, path, overwrite):
    if os.path.exists(path) and not overwrite:
        return True
    try:
        response = request_fit('GET', url, stream=True)
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)
    except Exception:
        if os.path.exists(path):
            os.remove(path)
        return False
    else:
        return True


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
  
    parser = argparse.ArgumentParser(
        prog='openwpd'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-u', metavar='user', dest='users', nargs='+',
        help='specify nickname or id of weibo users'
    )
    group.add_argument(
        '-f', metavar='file', dest='files', nargs='+',
        help='import list of users from files'
    )
    parser.add_argument(
        '-d', metavar='directory', dest='directory',
        help='set picture saving path'
    )
    parser.add_argument(
        '-s', metavar='size', dest='size',
        default=20, type=int,
        help='set size of thread pool'
    )
    parser.add_argument(
        '-r', metavar='retry', dest='retry',
        default=2, type=int,
        help='set maximum number of retries'
    )
    parser.add_argument(
        '-i', metavar='interval', dest='interval',
        default=1, type=float,
        help='set interval for feed requests'
    )
    parser.add_argument(
        '-c', metavar='cookie', dest='cookie',
        help='set cookie if needed'
    )
    parser.add_argument(
        '-b', metavar='boundary', dest='boundary',
        default=':',
        help='focus on weibos in the id range'
    )
    parser.add_argument(
        '-n', metavar='name', dest='name', default='{name}',
        help='customize naming format'
    )
    parser.add_argument(
        '-v', dest='video', action='store_true',
        help='download videos together'
    )
    parser.add_argument(
        '-o', dest='overwrite', action='store_true',
        help='overwrite existing files'
    )

    args = parser.parse_args(nargs_fit(parser, sys.argv[1:]))

    if args.users:
        users = args.users
    elif args.files:
        users = [read_from_file(path.strip()) for path in args.files]
        users = reduce(lambda x, y: x + y, users)
    users = [user.strip() for user in users]

    if args.directory:
        base = args.directory
        if os.path.exists(base):
            if not os.path.isdir(base):
                quit('saving path is not a directory')
        elif confirm(f'directory "{base}" doesn\'t exist, help to create?'):
            make_dir(base)
        else:
            quit('do it youself :)')
    else:
        base = os.path.join(os.path.dirname(__file__), 'weiboPic')
        if not os.path.exists(base):
            make_dir(base)

    boundary = args.boundary.split(':')
    boundary = boundary * 2 if len(boundary) == 1 else boundary

    def numberify(x):
        if re.search(r'^\d+$', x):
            return int(x)
        else:
            return bid_to_mid(x)

    def dateify(t):
        return datetime.datetime.strptime(t, '@%Y%m%d').date()

    def parse_point(p):
        if p.startswith('@'):
            return dateify(p)
        else:
            return numberify(p)

    try:
        boundary[0] = 0 if boundary[0] == '' else parse_point(boundary[0])
        boundary[1] = float(
            'inf') if boundary[1] == '' else parse_point(boundary[1])
        if type(boundary[0]) == type(boundary[1]):
            assert boundary[0] <= boundary[1]
    except:
        quit(f'invalid id range {args.boundary}')

    token = 'SUB={}'.format(args.cookie) if args.cookie else None
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=args.size)

    for number, user in enumerate(users, 1):

        print_fit(f'{number}/{len(users)} {time.ctime()}')

        if re.search(r'^\d{10}$', user):
            nickname = uid_to_nickname(user)
            uid = user
        else:
            nickname = user
            uid = nickname_to_uid(user)

        if not nickname or not uid:
            print_fit(f'invalid account {user}')
            print_fit('-' * 30)
            continue

        print_fit(f'{nickname} {uid}')

        try:
            resources = get_resources(uid, args.video, args.interval, boundary)
        except KeyboardInterrupt:
            quit()

        album = os.path.join(base, nickname)
        if resources and not os.path.exists(album):
            make_dir(album)

        retry = 0
        while resources and retry <= args.retry:

            if retry > 0:
                print_fit(f'automatic retry {retry}')

            total = len(resources)
            tasks = []
            done = 0
            failed = {}
            cancel = False

            for resource in resources:
                path = os.path.join(album, format_name(resource))
                tasks.append(pool.submit(
                    download, resource['url'], path, args.overwrite))

            while done != total:
                try:
                    done = 0
                    for index, task in enumerate(tasks):
                        if task.done() == True:
                            done += 1
                            if task.cancelled():
                                continue
                            elif task.result() == False:
                                failed[index] = ''
                        elif cancel:
                            if not task.cancelled():
                                task.cancel()
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    cancel = True
                finally:
                    if not cancel:
                        print_fit(
                            f"{'downloading...' if done != total else 'all tasks done'} \
                                {progress(done, total, True)}", pin=True)
                    else:
                        print_fit('waiting for cancellation... ({})'.format(
                            total - done), pin=True)

            if cancel:
                quit()

            print_fit(
                f'\nsuccess {total - len(failed)}, failure {len(failed)}, total {total}')

            resources = [resources[index] for index in failed]
            retry += 1

        for resource in resources:
            print_fit(f"{resource['url']} failed")
        print_fit('-' * 30)

    quit('bye bye')
