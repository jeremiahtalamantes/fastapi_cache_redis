from fastapi import Depends, FastAPI
from fastapi_cache import caches, close_caches
from fastapi_cache.backends.redis import CACHE_KEY, RedisCacheBackend

# Initialize the FastAPI app object.
app = FastAPI()

#
#
# FASTAPI CACHE: SIMPLE CACHING SYSTEM
# by Compliiant.io -- Jeremiah Talamantes
#
#

# Define a dependency function that retrieves the configured cache backend.
def redis_cache():
    # This line fetches the RedisCacheBackend instance using a predefined CACHE_KEY.
    # It allows for easy retrieval and use of the cache backend across the application.
    return caches.get(CACHE_KEY)

# Define the root path of your API and its logic.
@app.get('/')
async def hello(cache: RedisCacheBackend = Depends(redis_cache)):
    # Attempt to retrieve a value for 'some_cached_key' from the cache.
    in_cache = await cache.get('some_cached_key')
    # If the key does not exist in the cache (None is returned),
    # then set a new key-value pair in the cache.
    if not in_cache:
        # Set 'some_cached_key' in the cache with a value of 'new_value'
        # and a time-to-live (TTL) of 5 seconds. After 5 seconds, the cache
        # entry will expire and be removed automatically.
        await cache.set('some_cached_key', 'new_value', 5)
        # Since the key was not initially found, we use a default value
        # to send as the response.
        in_cache = 'default'

    # Return the value retrieved from the cache, or the default value
    # if the cache did not contain the key.
    return {'response': in_cache}

# Event handler for when the application starts.
@app.on_event('startup')
async def on_startup() -> None:
    # Create an instance of RedisCacheBackend, pointing to the location
    # of the Redis server. The URI format is 'redis://host:port'.
    # Here, 'redis://redis' assumes a Redis server running on the default
    # port on a host named 'redis'.
    rc = RedisCacheBackend('redis://redis')
    # Assign the Redis cache backend to the caches registry using a
    # predefined key, allowing it to be retrieved and used globally
    # within the application.
    caches.set(CACHE_KEY, rc)

# Event handler for when the application shuts down.
@app.on_event('shutdown')
async def on_shutdown() -> None:
    # This line ensures that all cache connections are properly closed
    # when the application is shutting down, which is crucial for freeing up
    # resources and ensuring a graceful shutdown.
    await close_caches()
