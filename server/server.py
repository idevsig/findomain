import argparse
import http.server
import json
from datetime import datetime
import socketserver

DATA_FILE = 'domains.json'


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get content length and read data
            content_length = int(self.headers.get('Content-Length', 0))
            raw_data = self.rfile.read(content_length).decode('utf-8')

            # Parse JSON data
            data_json = json.loads(raw_data)

            # Validate required fields
            if 'last_query_domain' not in data_json:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(
                    json.dumps(
                        {'error': 'Missing start_char in JSON data'}
                    ).encode('utf-8')
                )
                return

            data = {
                'last_query_domain': data_json['last_query_domain'],
                'updated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

            # Save to file
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)

            # Send response
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

    def do_GET(self):
        try:
            # Read data from file
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = []

            # Send response
            if not data:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                return

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))


def arguments():
    parser = argparse.ArgumentParser(
        description='Findomain Server for Resume Query'
    )
    parser.add_argument('-p', '--port', default=8000, help='Port to listen on')
    return parser.parse_args()


def main():
    print('Findomain Server for Resume Query')

    args = arguments()
    port = args.port

    # 判断端口是否已被占用，若占用则随机端口再次运行服务器
    while True:
        try:
            with socketserver.TCPServer(('', port), RequestHandler) as httpd:
                print(
                    f'Listening on http://{httpd.server_address[0]}:{httpd.server_address[1]}'
                )
                print('Press Ctrl+C to stop')
                httpd.serve_forever()
        except OSError:
            print(f'Port {port} is already in use, trying another port...')
            port = 0


if __name__ == '__main__':
    main()
