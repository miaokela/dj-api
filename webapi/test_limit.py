import threading
import requests

def make_request():
    url = "http://127.0.0.1:8000/api/v1/test/1"
    response = requests.get(url)
    print(f"Thread {threading.current_thread().name}: Status Code {response.status_code}")

def main():
    threads = []
    num_requests = 10

    for i in range(num_requests):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
    