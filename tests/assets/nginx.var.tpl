server {
  listen 80;
  server_name {{ =hostname }};

  root {{ =webroot }};
  index index.htm;

  access_log {{ =logs.path }}http.access.log combined;
  error_log  {{ =logs.path }}http.error.log;
}
