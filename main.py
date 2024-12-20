import os
import sys
import time
from qbittorrentapi import Client

APP_NAME = "qSequencer"
UPDATE_INTERVAL = os.getenv("UPDATE_INTERVAL", 5)

class QSequencer:
    def __init__(self):
        self.url = os.getenv("URL")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")

        if not self.username or not self.password:
            raise ValueError(f"[{APP_NAME}] Environment variables URL, USERNAME and PASSWORD must be set")

        self.client = Client(host=self.url, username=self.username, password=self.password)
        self.connect_to_client()

    def connect_to_client(self):
        try:
            self.client.auth_log_in()
            print(f"[{APP_NAME}] Successfully connected to qBittorrent")
        except Exception as e:
            print(f"[{APP_NAME}] Failed to connect to qBittorrent: {e}")
            time.sleep(UPDATE_INTERVAL)

    def get_torrents(self):
        return self.client.torrents.info()
    
    def get_torrent(self, torrent_hash):
        torrent_list = [t for t in self.get_torrents() if t.hash == torrent_hash]
        return torrent_list[0]

    def resume_torrent(self, torrent_hash, name):
        try:
            self.client.torrents.resume(torrent_hash)
            print(f"[{APP_NAME}] Torrent '{name}' resumed")
        except Exception as e:
            print(f"[{APP_NAME}] Error resuming torrent '{name}': {e}")

    def pause_all_torrents(self):
        try:
            self.client.torrents.pause.all()
            print(f"[{APP_NAME}] All torrents have been paused")
        except Exception as e:
            print(f"[{APP_NAME}] Error pausing torrents: {e}")

    def pause_torrent(self, torrent_hash, name):
        try:
            self.client.torrents.pause(torrent_hash)
            print(f"[{APP_NAME}] Torrent '{name}' paused")
        except Exception as e:
            print(f"[{APP_NAME}] Error pausing torrent '{name}': {e}")

    # Credit to Thane Brimhall with modifications
    # https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb
    def format_bytes(self, size):
        power = 2**10
        n = 0
        power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels[n]+'B'}"

    def handle_torrents(self):
        torrents = self.get_torrents()

        # Snapshot of torrents that are not stopped
        active_torrents = [t for t in torrents if t.state not in ['pausedUP', 'pausedDL']]

        # Snapshot of torrents that are in a checking state
        checking_torrents = [t for t in active_torrents if t.state in ['checkingUP', 'checkingDL', 'checkingResumeData']]

        if not checking_torrents:
            print(f"[{APP_NAME}] No torrents in 'checking' state")
            time.sleep(UPDATE_INTERVAL)  # Wait before restarting loop
            return

        self.pause_all_torrents()

        print(f"[{APP_NAME}] Found {len(checking_torrents)} torrents in 'checking' state")

        # Recheck torrents sequentially
        for torrent in sorted(checking_torrents, key=lambda x: x.size):
            self.resume_torrent(torrent.hash, torrent.name)
            first_poll = True
            time.sleep(5) # Crucial to allow transition from paused to checking

            # Wait until the torrent finishes checking
            while True:
                try:
                    torrent_info = self.get_torrent(torrent.hash)

                    if not first_poll:
                        for _ in range(5):
                            sys.stdout.write("\033[F")  # Move the cursor up one line
                            sys.stdout.write("\033[2K")  # Clear the current line
                        sys.stdout.flush()
                    first_poll = False
                    
                    sys.stdout.write(f"[{APP_NAME}] Current task:\n")
                    sys.stdout.write(f"\tName: {torrent_info.name}\n")
                    sys.stdout.write(f"\tHash: {torrent_info.hash}\n")
                    sys.stdout.write(f"\tSize: {self.format_bytes(torrent_info.size)}\n")
                    sys.stdout.write(f"\tProgress: {torrent_info.progress * 100:.1f}%\n")
                    sys.stdout.flush()

                    if torrent_info.state not in ['checkingUP', 'checkingDL', 'checkingResumeData', 'checking']:
                        time.sleep(UPDATE_INTERVAL)
                        break

                    time.sleep(UPDATE_INTERVAL)
                except ConnectionRefusedError:
                    print(f"[{APP_NAME}] Connection to qBittorrent refused. Retrying...")
                    self.connect_to_client()

        print(f"[{APP_NAME}] Unpausing torrents that were not originally paused.")
        for torrent in torrents:
            if torrent.state not in ['pausedUP', 'pausedDL']:
                self.resume_torrent(torrent.hash, torrent.name)

if __name__ == "__main__":
    qb_manager = QSequencer()
    print(f"[{APP_NAME}] Application started successfully")
    while True:
        try:
            qb_manager.handle_torrents()
            time.sleep(UPDATE_INTERVAL)
        except ConnectionRefusedError:
            print(f"[{APP_NAME}] Connection refused. Attempting to reconnect...")
            time.sleep(UPDATE_INTERVAL)
        except Exception as e:
            print(f"[{APP_NAME}] An error occurred: {e}")
            time.sleep(UPDATE_INTERVAL)
