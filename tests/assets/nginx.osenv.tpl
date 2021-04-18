{{ nginx = {key.strip("NGINX_").lower(): val for key, val in env.items() if key.startswith("NGINX_")} }}
server {
  listen 80;
  server_name {{ =nginx["hostname"] }};

  root {{ =nginx["webroot"] }};
  index index.htm;

  access_log {{ =nginx["logs"] }}http.access.log combined;
  error_log  {{ =nginx["logs"] }}http.error.log;
}
