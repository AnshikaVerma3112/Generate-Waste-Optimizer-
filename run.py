"""Start from any working directory: python /path/to/run.py --port 8000."""
import argparse
from backend.server import make_server

def main():
    parser = argparse.ArgumentParser(description='Waste Collection Route Optimizer')
    parser.add_argument('--port', type=int, default=8000, help='Local port (default: 8000)')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Port must be between 1 and 65535.')
    try:
        server = make_server(args.port)
    except OSError as error:
        parser.exit(1, f'Could not start the server: {error}\nTry: python run.py --port 8001\n')
    print(f'Open http://127.0.0.1:{args.port}\nKeep this terminal open. Press Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
