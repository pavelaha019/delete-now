from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
from urllib.parse import urlparse
import time
import json
from datetime import datetime

class CacheEntry:
    def __init__(self, content, headers, timestamp):
        self.content = content
        self.headers = headers
        self.timestamp = timestamp

class ProxyHandler(BaseHTTPRequestHandler):
    # Class variable to store cached content
    cache = {}
    # Cache expiration time in seconds (5 minutes)
    CACHE_DURATION = 300
    
    def do_GET(self):
        try:
            # Parse the requested URL
            url = self.path
            if not url.startswith('http'):
                url = 'http://' + self.path.lstrip('/')
            
            # Check if the content is in cache and not expired
            cached_response = self.get_from_cache(url)
            if cached_response:
                print(f"Cache hit for {url}")
                self.send_cached_response(cached_response)
                return
            
            # If not in cache, fetch from origin server
            print(f"Cache miss for {url}")
            response = urllib.request.urlopen(url)
            
            # Read response content and headers
            content = response.read()
            headers = dict(response.getheaders())
            
            # Store in cache
            self.cache[url] = CacheEntry(
                content=content,
                headers=headers,
                timestamp=time.time()
            )
            
            # Send response to client
            self.send_response(response.status)
            for header, value in headers.items():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(content)
            
        except urllib.error.URLError as e:
            self.send_error(500, f"Error fetching URL: {str(e)}")
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def get_from_cache(self, url):
        """Check if URL is in cache and not expired"""
        if url in self.cache:
            entry = self.cache[url]
            if time.time() - entry.timestamp < self.CACHE_DURATION:
                return entry
            else:
                # Remove expired entry
                del self.cache[url]
        return None
    
    def send_cached_response(self, cache_entry):
        """Send cached response to client"""
        self.send_response(200)
        for header, value in cache_entry.headers.items():
            self.send_header(header, value)
        self.send_header('X-Cache', 'HIT')
        self.end_headers()
        self.wfile.write(cache_entry.headers)

def run_proxy_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f"Proxy server running on port {port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down proxy server...")
        httpd.shutdown()

if __name__ == '__main__':
    run_proxy_server()

# curl -v "http://localhost:8000/www.iamawesome.com"