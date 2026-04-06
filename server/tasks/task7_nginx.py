TASK_ID = "task7_nginx"
DIFFICULTY = "very_hard"
FILE_TYPE = "nginx"
NUM_BUGS = 6

DESCRIPTION = (
    "An nginx reverse proxy configuration. It should define an upstream block named "
    "'app_server' pointing to localhost:3000, a server block listening on port 443 with "
    "SSL, proxy_pass to the upstream, worker_connections of at least 1024, and proper "
    "SSL certificate paths under /etc/ssl/certs/ and /etc/ssl/private/."
)

# Bug 1 (Syntax): Missing semicolon at end of server_name directive
# Bug 2 (Syntax): Unclosed brace in location block
# Bug 3 (Semantic): proxy_pass URL has wrong port (8080 but backend runs on 3000)
# Bug 4 (Semantic): ssl_certificate path points to non-standard location
# Bug 5 (Runtime): worker_connections set to 10 (unrealistically low)
# Bug 6 (Integration): upstream block defines "app_server" but proxy_pass references "http://backend"
BROKEN_CONFIG = """worker_processes auto;

events {
    worker_connections 10;
}

http {
    upstream app_server {
        server 127.0.0.1:3000;
    }

    server {
        listen 443 ssl;
        server_name example.com

        ssl_certificate /tmp/certs/server.crt;
        ssl_certificate_key /tmp/certs/server.key;

        location / {
            proxy_pass http://backend:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

        location /static/ {
            alias /var/www/static/;
            expires 30d;
        }

        location /health {
            access_log off;
            return 200 'OK';
        }
    }
}"""

ERROR_MESSAGE = (
    "nginx configuration error: unexpected end of file, expecting ';' or '}'. "
    "Additionally, the proxy_pass target may not match the upstream definition, "
    "SSL certificate paths may be non-standard, worker_connections may be too low, "
    "and there may be unclosed braces."
)

GROUND_TRUTH = """worker_processes auto;

events {
    worker_connections 1024;
}

http {
    upstream app_server {
        server 127.0.0.1:3000;
    }

    server {
        listen 443 ssl;
        server_name example.com;

        ssl_certificate /etc/ssl/certs/server.crt;
        ssl_certificate_key /etc/ssl/private/server.key;

        location / {
            proxy_pass http://app_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /static/ {
            alias /var/www/static/;
            expires 30d;
        }

        location /health {
            access_log off;
            return 200 'OK';
        }
    }
}"""
