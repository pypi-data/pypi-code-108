"""
Tools for conveying dslibrary calls to other systems.

* to_rest - translate calls into REST calls, securing them with an access token
* to_volume - communicate with a Kubernetes sidecar using a shared volume
* sample_rest - example rest service which converts http calls back into dslibrary calls
* volume_watcher - the other side of 'to_volume' which translates volume-based requests back into dslibrary calls
"""
