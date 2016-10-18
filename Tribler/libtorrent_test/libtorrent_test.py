import time
import sys
import libtorrent


class TestSeeding:
    def __init__(self):
        self.test_seeding()

    def test_seeding(self):
        """
        Test whether a torrent is correctly seeded
        """
        session = libtorrent.session()
        session.listen_on(6881, 6891)
        testtorrent = libtorrent.bdecode(open("fakeTorrent/testTorrent.torrent", 'rb').read())
        info = libtorrent.torrent_info(testtorrent)

        params = {'save_path': '.',
                  'storage_mode': libtorrent.storage_mode_t.storage_mode_sparse,
                  'ti': info}
        torrent_handle = session.add_torrent(params)
        print torrent_handle.status()

        while not torrent_handle.is_seed():
            s = torrent_handle.status()

            state_str = ['queued', 'checking', 'downloading metadata',
                         'downloading', 'finished', 'seeding', 'allocating', 'checking fastresume']
            print '\r%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' % \
                  (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
                   s.num_peers, state_str[s.state]),
            sys.stdout.flush()

            time.sleep(1)

        print torrent_handle.name(), 'complete'
