from threading import Lock
import httpx


class IPClient:
    _lock = Lock()
    _ip_client_instance = None
    url = "https://ipinfo.io"
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)

    def __new__(cls, *args, **kwargs):
        if cls._ip_client_instance is None:
            cls._lock.acquire()
            try:
                '''
                If instance is created in between acquiring the lock
                There could another way by wrapping entire body with lock but
                in that case even we already have an instance we will be acquiring a lock
                '''
                if cls._ip_client_instance is None:
                    cls._ip_client_instance = super().__new__(cls)
            finally:
                cls._lock.release()

        return cls._ip_client_instance

    async def get_ip_address(self, ip):
        api_endpoint = f"{self.url}/{ip}/json"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_endpoint)

                if response.status_code == httpx.codes.OK:
                    return response.json()
        except Exception as e:
            raise e
