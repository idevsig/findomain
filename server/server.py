import argparse
import http.server
import json
import os
from datetime import datetime
import socketserver
import socket
import requests

DATA_FILE = 'domains.json'


def workflow_dispatch():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        return

    repo = os.getenv('FD_REPOSITORY', 'idev-sig/findomain')
    ref = os.getenv('FD_REF', 'main')
    workflow_filename = os.getenv('FD_WORKFLOW', 'find-domain.yml')

    inputs = (
        {
            'domain': '',
            'domain_url': '',
            'start_char': '',
        },
    )

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'token {token}',
    }

    data = {'ref': ref, 'inputs': inputs}

    url = f'https://api.github.com/repos/{repo}/actions/workflows/{workflow_filename}/dispatches'
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 204:
        print('🎉 GitHub Action triggered successfully!')
    else:
        print(
            f'❌ Failed to trigger: {response.status_code} - {response.text}'
        )


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length).decode('utf-8')
            data_json = json.loads(raw_data)

            last_query_domain = data_json.get('last_query_domain')
            if not last_query_domain:
                self._send_json(
                    400, {'error': 'Missing last_query_domain in JSON data'}
                )
                return

            updated_time = data_json.get(
                'updated_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            data = {
                'last_query_domain': last_query_domain,
                'updated_time': updated_time,
            }

            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)

            # 未完成，则触发 GitHub Action
            if last_query_domain != '-1':
                workflow_dispatch()

            self._send_json(201, data)

        except json.JSONDecodeError:
            self._send_json(400, {'error': 'Invalid JSON data'})
        except Exception as e:
            self._send_json(500, {'error': str(e)})

    def do_GET(self):
        try:
            if not os.path.isfile(DATA_FILE):
                self._send_json(200, {})  # 空字典响应
                return

            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._send_json(200, data)
        except json.JSONDecodeError:
            self._send_json(
                500, {'error': 'Failed to parse JSON from data file'}
            )
        except Exception as e:
            self._send_json(500, {'error': str(e)})


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Findomain Server for Resume Query'
    )
    parser.add_argument(
        '-p', '--port', type=int, default=8000, help='Port to listen on'
    )
    parser.add_argument(
        '-n', '--name', default='findomain_server', help='Server name'
    )
    return parser.parse_args()


def run_server(port):
    while True:
        try:
            with socketserver.TCPServer(('', port), RequestHandler) as httpd:
                host = socket.gethostbyname(socket.gethostname())
                print(f'Listening on http://{host}:{httpd.server_address[1]}')
                print('Press Ctrl+C to stop')
                httpd.serve_forever()
        except OSError:
            print(
                f'Port {port} is already in use, trying a random available port...'
            )
            port = 0


def main():
    print('Findomain Server for Resume Query')
    args = parse_arguments()
    run_server(args.port)


if __name__ == '__main__':
    main()
