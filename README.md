# qSequencer

A companion application for [qBittorrent](https://www.qbittorrent.org) to handle sequential data checking and improving the performance on hard drives by reducing the likiness of seek thrashing and random seek latency.

> **Note:** You must have `Pre-allocate disk space for all files` enabled in qBittorrent under the Downloads section.
> This prevents data fragmentation and improves sequential file read time

## Installation/Setup

### Docker

The docker image is available and can be pulled from Docker Hub: [enayet123/qsequencer](https://hub.docker.com/r/enayet123/qsequencer) 

> **Note:** All environment variables associated with the Starr service you wish to manage must be provided.

Using docker compose is the recommended way to setup qSequencer e.g.
```
services:
  qsequencer:
    image: enayet123/qsequencer:latest
    container_name: qsequencer
    restart: unless-stopped
    environment:
      - URL=http://192.168.1.1:8090
      - USERNAME=
      - PASSWORD=
```

Using docker CLI as an alternative
```
docker run -d \
  --name=qsequencer \
  -e URL=http://192.168.1.1:8090 \
  -e USERNAME=user \
  -e PASSWORD=pass \
  --restart unless-stopped \
  enayet123/qsequencer:latest
```

### Python

> **Note:** The following steps assume you already have python installed.

Clone the repository to a location of your choice
```
git clone git@github.com:enayet123/qSequencer.git
cd qSequencer
```

Provide the required environment variables and run the application
```
URL=http://192.168.1.1:8090 USERNAME=user PASSWORD=pass
```

## Environment Variables

All variables are optional however providing none will result in the application quitting

| Variable                    | Description                                                                                          |
|-----------------------------|------------------------------------------------------------------------------------------------------|
| `URL`                       | The URL used to locate your qBittorrent instance                                                     |
| `USERNAME`                  | The username to access your qBittorrent WebUI (Tools -> Options -> WebUI -> Authentication)          |
| `PASSWORD`                  | The password to access your qBittorrent WebUI (Tools -> Options -> WebUI -> Authentication)          |

## Disclaimer 

This application is provided "as is" without any warranties or guarantees of any kind, either express or implied. The use of this application is at your own risk. The developers assume no liability for any damages, losses, or issues, including but not limited to data loss, system malfunctions, or financial impacts, that may arise from the use or misuse of this application.

By using this application, you agree to take full responsibility for any outcomes and understand that the developers are not liable for any consequences resulting from its use. Always test the application in a controlled environment before deploying it in production.
