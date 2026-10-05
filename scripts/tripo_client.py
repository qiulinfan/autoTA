"""Small resumable Tripo v3 adapter; credentials stay outside receipts.

Paid operations are explicit `submit` commands. Never automatically retry a
POST: a timeout may mean a billed task exists. Query the account before retrying.
Generated files must go through auto-ta's independent DCC/engine gates.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

BASE = 'https://openapi.tripo3d.ai/v3'
ENDPOINTS = {
    'generate': '/generation/text-to-model',
    'texture': '/models/texture',
    'convert': '/models/convert',
}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def request(key, path, payload=None):
    headers = {'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(BASE + path, data=data, headers=headers)
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=60) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Do not print request headers or untrusted error bodies containing keys.
        raise RuntimeError('Tripo HTTP ' + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError('Network failure; POST outcome may be unknown. Do not resubmit blindly.') from None
    if result.get('code') != 0:
        raise RuntimeError('Tripo error code ' + str(result.get('code')))
    return result

def save_new(path, value):
    # Refuse to overwrite a completed operation receipt or a pending submit.
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('balance')
    submit = sub.add_parser('submit')
    submit.add_argument('--operation', choices=ENDPOINTS, required=True)
    submit.add_argument('--payload', type=Path, required=True)
    query = sub.add_parser('query')
    query.add_argument('--task-id', required=True)
    args = parser.parse_args()
    key = args.key_file.read_text(encoding='utf-8-sig').strip().strip('"').strip("'")
    if not key or any(c.isspace() for c in key):
        raise RuntimeError('Credential file must contain one token only')
    args.output.mkdir(parents=True, exist_ok=True)
    if args.command == 'balance':
        result = request(key, '/account/balance')
        path = args.output / ('balance-' + datetime.datetime.now().strftime('%Y%m%dT%H%M%S%f') + '.json')
    elif args.command == 'submit':
        payload = json.loads(args.payload.read_text(encoding='utf-8-sig'))
        if not isinstance(payload, dict):
            raise ValueError('Payload must be an object')
        if key in json.dumps(payload):
            raise ValueError('Credential must never be part of payload')
        balance = request(key, '/account/balance')
        if float(balance['data']['balance']) <= 0:
            raise RuntimeError('API_BALANCE_EMPTY: purchase API credits before generation')
        attempt = args.output / 'submission-attempt.json'
        save_new(attempt, {'time': now(), 'operation': args.operation, 'payload': payload,
                           'balance_before': balance['data'], 'status': 'submission_started'})
        result = request(key, ENDPOINTS[args.operation], payload)
        path = args.output / 'submission-result.json'
    else:
        task_id = urllib.parse.quote(args.task_id, safe='')
        result = request(key, '/tasks/' + task_id)
        path = args.output / ('task-' + datetime.datetime.now().strftime('%Y%m%dT%H%M%S%f') + '.json')
    save_new(path, {'time': now(), 'response': result})
    data = result.get('data', {})
    print(json.dumps({'receipt': str(path.resolve()), 'task_id': data.get('task_id'),
                      'status': data.get('status'), 'balance': data.get('balance'),
                      'frozen': data.get('frozen'), 'progress': data.get('progress')}))

if __name__ == '__main__':
    main()
