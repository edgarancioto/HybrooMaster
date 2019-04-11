from FrontEnd import controller_frontend
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        controller_frontend.start_system_server(str(sys.argv[1]))
    controller_frontend.start_system_local()
