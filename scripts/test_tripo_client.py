import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import tripo_client as client

class SubmissionSafety(unittest.TestCase):
    def run_submit(self, root, request):
        key = root / 'credential.txt'
        key.write_text('test-token-do-not-log', encoding='utf-8')
        payload = root / 'payload.json'
        payload.write_text(json.dumps({'model':'test','prompt':'sofa'}), encoding='utf-8')
        argv = ['tripo_client', '--key-file',str(key),'--output',str(root/'job'),
                'submit','--operation','generate','--payload',str(payload)]
        with patch('sys.argv', argv), patch.object(client,'request',side_effect=request), contextlib.redirect_stdout(io.StringIO()) as output:
            client.main()
        self.assertNotIn('test-token-do-not-log', output.getvalue())

    def test_completed_submission_cannot_be_repeated(self):
        calls=[]
        def request(key,path,payload=None):
            calls.append(path)
            return {'code':0,'data':{'balance':100}} if payload is None else {'code':0,'data':{'task_id':'job-1'}}
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            self.run_submit(root,request)
            with self.assertRaises(FileExistsError):self.run_submit(root,request)
            self.assertEqual(calls.count('/generation/text-to-model'),1)
            for p in (root/'job').glob('*.json'):self.assertNotIn('test-token-do-not-log',p.read_text())

    def test_unknown_post_outcome_blocks_blind_retry(self):
        posts=[]
        def request(key,path,payload=None):
            if payload is None:return {'code':0,'data':{'balance':100}}
            posts.append(path)
            raise RuntimeError('network timeout')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            with self.assertRaises(RuntimeError):self.run_submit(root,request)
            self.assertTrue((root/'job/submission-attempt.json').exists())
            with self.assertRaises(FileExistsError):self.run_submit(root,request)
            self.assertEqual(len(posts),1)

    def test_empty_balance_does_not_post(self):
        calls=[]
        def request(key,path,payload=None):
            calls.append(path)
            return {'code':0,'data':{'balance':0}}
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError,'API_BALANCE_EMPTY'):self.run_submit(Path(temp),request)
        self.assertEqual(calls,['/account/balance'])

if __name__=='__main__':unittest.main()
